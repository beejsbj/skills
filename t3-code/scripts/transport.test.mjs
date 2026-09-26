import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile, rm } from "node:fs/promises";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { withClient } from "./transport.mjs";

process.env.T3_AUTH_TOKEN = "token-synthetic";

async function server(handler) {
  const s = http.createServer(handler);
  await new Promise((resolve) => s.listen(0, "127.0.0.1", resolve));
  return { s, origin: `http://127.0.0.1:${s.address().port}` };
}

function wsFake(mode, record) {
  return class FakeWebSocket {
    static instances = [];
    constructor(url) {
      this.url = String(url); this.listeners = {}; this.closed = false;
      FakeWebSocket.instances.push(this); record.url = this.url;
      queueMicrotask(() => this.emit("open", {}));
    }
    addEventListener(type, fn) { (this.listeners[type] ??= []).push(fn); }
    emit(type, value) { for (const fn of this.listeners[type] ?? []) fn(value); }
    send(raw) {
      record.frame = JSON.parse(raw);
      if (mode === "success") {
        this.emit("message", { data: JSON.stringify({ requestId: "wrong", _tag: "Exit", exit: { _tag: "Success", value: "wrong" } }) });
        queueMicrotask(() => this.emit("message", { data: JSON.stringify({ requestId: record.frame.id, _tag: "Exit", exit: { _tag: "Success", value: { ok: true } } }) }));
      } else if (mode === 'batch') {
        queueMicrotask(() => this.emit('message', { data: JSON.stringify([
          { _tag: 'Exit', requestId: 'other', exit: { _tag: 'Success', value: 'wrong' } },
          { _tag: 'Exit', requestId: record.frame.id, exit: { _tag: 'Success', value: 'batched' } }
        ]) }));
      } else if (mode === 'defect') {
        queueMicrotask(() => this.emit('message', { data: JSON.stringify({ _tag: 'Defect', defect: { message: 'server defect' } }) }));
      } else if (mode === "failure") {
        queueMicrotask(() => this.emit("message", { data: JSON.stringify({ requestId: record.frame.id, _tag: "Exit", exit: { _tag: "Failure", cause: [{ _tag: "Fail", error: { message: "server rejected" } }] } }) }));
      } else if (mode === "close") queueMicrotask(() => this.emit("close", {}));
    }
    close() { this.closed = true; record.closed = true; }
  };
}

function ticketHandler(token, seen) {
  return (req, res) => {
    seen.push({ path: req.url, auth: req.headers.authorization });
    res.setHeader("content-type", "application/json");
    res.end(JSON.stringify({ ticket: token }));
  };
}

test("requests ticket with exact bearer auth and filters unrelated RPC frames", async () => {
  const seen = [], record = {};
  const fake = await server(ticketHandler("ticket-synthetic", seen));
  try {
    const result = await withClient({ origin: fake.origin, timeoutMs: 1000, _deps: { WebSocket: wsFake("success", record) } }, (client) => client.rpc("method.example", { n: 1 }));
    assert.deepEqual(result, { ok: true });
    assert.deepEqual(seen[0], { path: "/api/auth/websocket-ticket", auth: "Bearer token-synthetic" });
    assert.equal(record.frame._tag, "Request");
    assert.equal(record.frame.tag, "method.example");
    assert.deepEqual(record.frame.payload, { n: 1 });
    assert.match(record.url, /wsTicket=ticket-synthetic/);
    assert.match(record.url, /orchestrationProtocol=1/);
  } finally { await new Promise((resolve) => fake.s.close(resolve)); }
});

test("explicit remote origin requires caller token and never runs local auth", async () => {
  const old = process.env.T3_AUTH_TOKEN; delete process.env.T3_AUTH_TOKEN;
  try { await assert.rejects(withClient({ origin: "http://127.0.0.1:9", _deps: { execFileSync() { throw new Error("must not run"); } } }, () => {}), /required/); }
  finally { if (old === undefined) delete process.env.T3_AUTH_TOKEN; else process.env.T3_AUTH_TOKEN = old; }
});

async function localSetup() {
  const baseDir = await mkdtemp(path.join(os.tmpdir(), "t3-transport-"));
  await mkdir(path.join(baseDir, "userdata"), { recursive: true });
  await writeFile(path.join(baseDir, "userdata", "server-runtime.json"), JSON.stringify({ origin: "http://127.0.0.1:1" }));
  return baseDir;
}

test("local auth is revoked after both callback success and failure", async t => {
  const baseDir = await localSetup(), calls = [], record = {};
  t.after(() => rm(baseDir, { recursive: true, force: true }));
  const fake = await server(ticketHandler("ticket-local", []));
  const old = process.env.T3_AUTH_TOKEN; delete process.env.T3_AUTH_TOKEN;
  try {
    await writeFile(path.join(baseDir, "userdata", "server-runtime.json"), JSON.stringify({ origin: fake.origin }));
    const io = { WebSocket: wsFake("success", record), execFileSync(file, args) { calls.push([file, args]); return JSON.stringify({ token: "local-token", sessionId: "session-1" }); } };
    await withClient({ baseDir, t3Bin: "/synthetic/t3", _deps: io }, () => "ok");
    await assert.rejects(withClient({ baseDir, t3Bin: "/synthetic/t3", _deps: { ...io, WebSocket: wsFake("success", {}) } }, async () => { throw new Error("callback failed"); }), /callback failed/);
    assert.equal(calls.filter(([, args]) => args.includes("issue")).length, 2);
    assert.equal(calls.filter(([, args]) => args.includes("revoke")).length, 2);
    for (const [, args] of calls) assert(!args.join(" ").includes("local-token"));
  } finally {
    if (old === undefined) delete process.env.T3_AUTH_TOKEN; else process.env.T3_AUTH_TOKEN = old;
    await new Promise((resolve) => fake.s.close(resolve));
  }
});

test("caller token is never revoked and dispatch performs one RPC", async () => {
  const record = {}, calls = [], fake = await server(ticketHandler("ticket-caller", []));
  const old = process.env.T3_AUTH_TOKEN; process.env.T3_AUTH_TOKEN = "caller-token";
  try {
    const result = await withClient({ origin: fake.origin, _deps: { WebSocket: wsFake("success", record), execFileSync(...args) { calls.push(args); } } }, (client) => client.dispatch({ kind: "Ping" }));
    assert.deepEqual(result, { ok: true }); assert.equal(record.frame.tag, "orchestration.dispatchCommand");
    assert.equal(calls.length, 0); assert.match(record.frame.payload.commandId, /^[0-9a-f-]{36}$/);
  } finally { if (old === undefined) delete process.env.T3_AUTH_TOKEN; else process.env.T3_AUTH_TOKEN = old; await new Promise((resolve) => fake.s.close(resolve)); }
});

for (const [name, mode, pattern, uncertain] of [["timeout", "none", /timed out/, true], ["failure", "failure", /server rejected/, false], ["close", "close", /closed/, true], ['defect', 'defect', /server defect/, true]]) {
  test(`RPC ${name} is bounded and does not retry`, async () => {
    const record = {}, fake = await server(ticketHandler("ticket-secret", []));
    try {
      await assert.rejects(withClient({ origin: fake.origin, timeoutMs: 20, _deps: { WebSocket: wsFake(mode, record) } }, (client) => client.rpc("one")), (error) => {
        assert.match(error.message, pattern); assert.equal(Boolean(error.uncertain), uncertain); assert.equal(record.closed, true); return true;
      });
    } finally { await new Promise((resolve) => fake.s.close(resolve)); }
  });
}

test("transport errors redact token and ticket", async () => {
  const fake = await server(ticketHandler("ticket-secret", []));
  const old = process.env.T3_AUTH_TOKEN; process.env.T3_AUTH_TOKEN = "token-secret";
  try {
    await assert.rejects(withClient({ origin: fake.origin, timeoutMs: 20, _deps: { WebSocket: wsFake("close", {}) } }, (client) => client.rpc("one")), (error) => {
      assert.doesNotMatch(error.message, /token-secret|ticket-secret/); return true;
    });
  } finally { if (old === undefined) delete process.env.T3_AUTH_TOKEN; else process.env.T3_AUTH_TOKEN = old; await new Promise((resolve) => fake.s.close(resolve)); }
});

test('batched replies preserve the command ID printed before dispatch', async () => {
  const record = {}, fake = await server(ticketHandler('ticket-batch', []));
  try {
    const result = await withClient({ origin: fake.origin, _deps: { WebSocket: wsFake('batch', record) } },
      c => c.dispatch({ type: 'thread.create', commandId: 'known-command-id' }));
    assert.equal(result, 'batched');
    assert.equal(record.frame.payload.commandId, 'known-command-id');
  } finally { await new Promise(resolve => fake.s.close(resolve)); }
});

test('revocation failure is surfaced without losing the successful operation receipt', async t => {
  const baseDir = await localSetup();
  t.after(() => rm(baseDir, { recursive: true, force: true }));
  const old = process.env.T3_AUTH_TOKEN; delete process.env.T3_AUTH_TOKEN;
  const io = { execFileSync(file, args) {
    if (args.includes('issue')) return JSON.stringify({ token: 'private-token', sessionId: 's-1' });
    throw new Error('private-token');
  } };
  try {
    await assert.rejects(withClient({ baseDir, t3Bin: '/synthetic/t3', _deps: io }, () => ({ ok: true, threadId: 'created-1' })), e => {
      assert.match(e.message, /could not be revoked/);
      assert.equal(e.receipt.operationResult.threadId, 'created-1');
      assert.doesNotMatch(e.message, /private-token/);
      return true;
    });
    await assert.rejects(withClient({ baseDir, t3Bin: '/synthetic/t3', _deps: io }, () => { throw new Error('dispatch failed private-token'); }), e => {
      assert.match(e.message, /dispatch failed/);
      assert.match(e.message, /could not be revoked/);
      assert.doesNotMatch(e.message, /private-token/);
      return true;
    });
  } finally { process.env.T3_AUTH_TOKEN = old; }
});

test('HTTP timeout covers a stalled response body', async () => {
  const fake = await server((req, res) => {
    res.writeHead(200, { 'content-type': 'application/json' });
    res.write('{');
  });
  try {
    await assert.rejects(withClient({ origin: fake.origin, timeoutMs: 40 }, c => c.request('GET', '/slow')), /timed out/);
  } finally { fake.s.closeAllConnections(); await new Promise(resolve => fake.s.close(resolve)); }
});
