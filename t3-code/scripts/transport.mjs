import { execFileSync } from "node:child_process";
import { randomUUID } from "node:crypto";
import { readFileSync, existsSync, accessSync, constants } from "node:fs";
import os from "node:os";
import path from "node:path";

const DEFAULT_TIMEOUT = 30_000;
const WS_PROTOCOL = 1;

const deps = {
  fetch: (...args) => fetch(...args),
  WebSocket: globalThis.WebSocket,
  readFileSync,
  existsSync,
  accessSync,
  execFileSync,
};

function clean(value, secrets = []) {
  let text = value instanceof Error ? value.message : String(value ?? "Unknown error");
  for (const secret of secrets) if (secret) text = text.split(String(secret)).join("[redacted]");
  text = text.replace(/([?&](?:wsTicket|ticket)=)[^&\s]+/gi, "$1[redacted]");
  try {
    const url = new URL(text);
    if (url.search) text = text.replace(url.search, "?[redacted]");
  } catch {}
  return text;
}

function fail(message, secrets, uncertain = false) {
  const error = new Error(clean(message, secrets));
  if (uncertain) error.uncertain = true;
  return error;
}

function validOrigin(value) {
  let url;
  try { url = new URL(value); } catch { throw new Error("origin must be a valid http(s) URL"); }
  if (!["http:", "https:"].includes(url.protocol) || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new Error("origin must be an http(s) origin without userinfo, path, query, or fragment");
  }
  url.pathname = url.pathname.replace(/\/$/, "");
  return url;
}

function jsonFile(file, io) {
  return JSON.parse(io.readFileSync(file, "utf8"));
}

function runtimeOrigin(baseDir, io) {
  const runtime = jsonFile(path.join(baseDir, "userdata", "server-runtime.json"), io);
  if (!runtime.origin) throw new Error("server runtime has no origin");
  return runtime.origin;
}

function isExecutable(file, io) {
  try { io.accessSync(file, constants.X_OK); return true; } catch { return false; }
}

function findExecutable(baseDir, requested, io) {
  if (requested) return requested;
  const stateFile = path.join(baseDir, "runtime", "service-state.json");
  try {
    const state = jsonFile(stateFile, io);
    const version = state.activeVersion ?? state.active?.version;
    if (typeof version === "string" && version && !version.includes("/") && !version.includes("\\") && version !== "." && version !== "..") {
      const managed = path.join(baseDir, "runtime", "versions", version, "t3");
      if (isExecutable(managed, io)) return managed;
      const legacy = path.join(baseDir, "runtime", "versions", version, "node_modules", "t3", "dist", "bin.mjs");
      if (io.existsSync(legacy)) return { file: process.execPath, prefix: [legacy] };
    }
  } catch {}
  try {
    const found = io.execFileSync("which", ["t3"], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
    if (found) return found;
  } catch {}
  throw new Error("could not find the t3 executable");
}

function runAuth(baseDir, executable, io, secrets) {
  const command = typeof executable === "string" ? [executable] : [executable.file, ...(executable.prefix ?? [])];
  const args = [...command.slice(1), "auth", "session", "issue", "--base-dir", baseDir, "--ttl", "10m", "--label", "t3-code-skill", "--json"];
  let output;
  try {
    output = io.execFileSync(command[0], args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], timeout: 30000 });
  } catch (error) { throw fail("local auth session could not be issued", secrets); }
  let parsed;
  try { parsed = JSON.parse(output); } catch { throw fail("local auth session returned invalid JSON", secrets); }
  const token = parsed.token ?? parsed.authToken ?? parsed.accessToken;
  const sessionId = parsed.sessionId ?? parsed.session?.id ?? parsed.id;
  if (typeof token !== "string" || !token || typeof sessionId !== "string" || !sessionId) throw fail("local auth session response was incomplete", secrets);
  secrets.push(token);
  return { token, sessionId, executable };
}

function revokeAuth(auth, baseDir, io, secrets) {
  const executable = auth.executable;
  const command = typeof executable === "string" ? [executable] : [executable.file, ...(executable.prefix ?? [])];
  const args = [...command.slice(1), "auth", "session", "revoke", "--base-dir", baseDir, auth.sessionId];
  try { io.execFileSync(command[0], args, { encoding: "utf8", stdio: ["ignore", "pipe", "pipe"], timeout: 30000 }); }
  catch (error) { throw fail("local auth session could not be revoked", secrets); }
}

function serverMessage(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) {
    for (const item of value) { const nested = serverMessage(item); if (nested !== "RPC request failed") return nested; }
    return "RPC request failed";
  }
  if (!value || typeof value !== "object") return "RPC request failed";
  for (const key of ["message", "detail", "reason", "error"]) {
    if (typeof value[key] === "string") return value[key];
  }
  for (const key of ["cause", "error", "defect", "reasons", "left", "right"]) {
    if (value[key]) { const nested = serverMessage(value[key]); if (nested !== "RPC request failed") return nested; }
  }
  return "RPC request failed";
}

async function makeClient({ origin, token, timeoutMs, io, secrets }) {
  const base = validOrigin(origin);
  const request = async (method, requestPath, body) => {
    const url = new URL(requestPath, `${base.href}/`);
    if (url.origin !== base.origin) throw fail("request path must stay on the configured origin", secrets);
    const headers = { authorization: `Bearer ${token}`, accept: "application/json" };
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    const init = { method, headers, redirect: "error", signal: controller.signal };
    if (body !== undefined) { headers["content-type"] = "application/json"; init.body = JSON.stringify(body); }
    try {
      const response = await io.fetch(url, init);
      let value;
      try { value = await response.json(); }
      catch (error) { throw fail(controller.signal.aborted ? 'HTTP request timed out' : `HTTP ${response.status} returned invalid JSON`, secrets); }
      if (!response.ok) throw fail(`HTTP ${response.status}: ${serverMessage(value)}`, secrets);
      return value;
    } catch (error) { throw fail(controller.signal.aborted ? "HTTP request timed out" : error, secrets); }
    finally { clearTimeout(timer); }
  };
  const rpc = async (tag, payload = {}) => {
    const ticketResponse = await request("POST", "/api/auth/websocket-ticket");
    const ticket = ticketResponse?.ticket;
    if (typeof ticket !== "string" || !ticket) throw fail("websocket ticket response was incomplete", secrets);
    secrets.push(ticket);
    const wsUrl = new URL("/ws", base);
    wsUrl.protocol = base.protocol === "https:" ? "wss:" : "ws:";
    wsUrl.searchParams.set("wsTicket", ticket);
    wsUrl.searchParams.set("orchestrationProtocol", String(WS_PROTOCOL));
    const id = randomUUID();
    const WebSocketImpl = io.WebSocket;
    if (typeof WebSocketImpl !== "function") throw fail("WebSocket is unavailable", secrets);
    return new Promise((resolve, reject) => {
      let sent = false, settled = false;
      const ws = new WebSocketImpl(wsUrl);
      const timer = setTimeout(() => finish(fail("RPC request timed out", secrets, sent)), timeoutMs);
      const finish = (error, value) => {
        if (settled) return;
        settled = true; clearTimeout(timer);
        try { ws.close(); } catch {}
        error ? reject(error) : resolve(value);
      };
      const message = (event) => {
        let frame;
        try { frame = JSON.parse(typeof event.data === "string" ? event.data : String(event.data)); } catch { return; }
        for (const item of Array.isArray(frame) ? frame : [frame]) {
          if (item?._tag === 'Defect') { finish(fail(serverMessage(item.defect), secrets, sent)); break; }
          if (item?.requestId !== id || item._tag !== 'Exit') continue;
          if (item.exit?._tag === 'Success') finish(null, item.exit.value);
          else finish(fail(serverMessage(item.exit?.cause), secrets));
          break;
        }
      };
      const opened = () => {
        try {
          sent = true;
          ws.send(JSON.stringify({ _tag: "Request", id, tag, payload, headers: [] }));
        } catch (error) { finish(fail(error, secrets, sent)); }
      };
      const errored = (event) => finish(fail(event?.error ?? event ?? "WebSocket error", secrets, sent));
      const closed = () => finish(fail("WebSocket closed before the RPC response", secrets, sent));
      if (ws.addEventListener) { ws.addEventListener("open", opened); ws.addEventListener("message", message); ws.addEventListener("error", errored); ws.addEventListener("close", closed); }
      else { ws.onopen = opened; ws.onmessage = message; ws.onerror = errored; ws.onclose = closed; }
    });
  };
  const dispatch = (command) => rpc("orchestration.dispatchCommand", { ...command, commandId: command.commandId ?? randomUUID() });
  return { origin: base.href, request, rpc, dispatch };
}

export async function withClient(options = {}, callback) {
  const baseDir = options.baseDir ?? process.env.T3CODE_HOME ?? path.join(os.homedir(), ".t3");
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT;
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) throw new Error("timeoutMs must be positive");
  const externalOrigin = options.origin !== undefined;
  let token = process.env.T3_AUTH_TOKEN;
  if (externalOrigin && !token) throw new Error("T3_AUTH_TOKEN is required with an explicit origin");
  const io = { ...deps, ...(options._deps ?? {}) };
  let auth;
  const secrets = token ? [token] : [];
  let primary, result;
  try {
    const origin = externalOrigin ? options.origin : runtimeOrigin(baseDir, io);
    validOrigin(origin);
    if (!token) {
      const executable = findExecutable(baseDir, options.t3Bin, io);
      auth = runAuth(baseDir, executable, io, secrets);
      token = auth.token;
    }
    const client = await makeClient({ origin, token, timeoutMs, io, secrets });
    result = await callback(client);
  } catch (error) {
    primary = error instanceof Error ? error : new Error(String(error));
    primary.message = clean(primary, secrets);
  } finally {
    if (auth) {
      try { revokeAuth(auth, baseDir, io, secrets); }
      catch (revokeError) {
        if (primary) { primary.revokeError = revokeError; primary.message += `; ${revokeError.message}`; }
        else { primary = revokeError; primary.receipt = { operationResult: result,
          instruction: 'The operation completed, but auth cleanup failed. Do not repeat the operation; the temporary session expires in 10 minutes.' }; }
      }
    }
  }
  if (primary) throw primary;
  return result;
}
