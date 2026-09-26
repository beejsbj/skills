import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { parse, resolveProject, selection, createPlan, sendPlan, executePlan, run, verify } from './t3ctl.mjs';

const provider = { instanceId: 'codex', driver: 'codex', enabled: true, installed: true, status: 'ready',
  auth: { status: 'authenticated' }, models: [
    { slug: 'vendor/model/name', capabilities: { optionDescriptors: [
      { id: 'reasoningEffort', type: 'select', options: [{ id: 'low' }, { id: 'high' }] },
      { id: 'fast', type: 'boolean' } ] } },
    { slug: 'plain', capabilities: null } ] };
const model = { instanceId: 'codex', model: 'vendor/model/name', options: [{ id: 'reasoningEffort', value: 'low' }] };
const config = { environment: { environmentId: 'env-a', label: 'Fixture',
  capabilities: { requiredWorktreeBootstrap: true } }, providers: [provider] };
const project = { id: 'project-a', title: 'Cockpit', workspaceRoot: '/fixture/repo', defaultModelSelection: model };
const thread = { id: 'thread-a', projectId: project.id, title: 'Original', branch: 'main', worktreePath: null,
  modelSelection: model, runtimeMode: 'approval-required', interactionMode: 'plan', session: null,
  messages: [], archivedAt: null, deletedAt: null };
function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), 't3-skill-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const file = join(root, 'prompt.txt');
  writeFileSync(file, 'Do the intended task.\nKeep this newline.\n');
  return file;
}
function fakeClient(value = thread) {
  return { origin: 'http://fixture', calls: [],
    async request(method, path) {
      if (path === '/api/orchestration/snapshot') return { projects: [project], threads: [value] };
      return { thread: value };
    },
    async rpc(tag, payload) {
      if (tag === 'server.getConfig') return config;
      assert.equal(tag, 'vcs.refreshStatus');
      assert.equal(payload.cwd, project.workspaceRoot);
      return { refName: 'main', isRepo: true };
    },
    async dispatch(command) { this.calls.push(command); return { sequence: this.calls.length }; }
  };
}
const creation = { command: 'create', project: project.id, title: 'Fix build', 'runtime-mode': 'approval-required' };

test('project titles must resolve uniquely; full IDs disambiguate', () => {
  const projects = [project, { ...project, id: 'project-b' }];
  assert.throws(() => resolveProject(projects, 'Cockpit'), /2 exact title matches/);
  assert.equal(resolveProject(projects, 'project-a').id, 'project-a');
  assert.throws(() => resolveProject(projects, 'project-'), /0 exact title matches/);
});

test('model slugs retain slashes and effort must be advertised by this model', () => {
  assert.deepEqual(selection([provider], { model: 'vendor/model/name', effort: 'high', option: ['fast=true'] }, model),
    { instanceId: 'codex', model: 'vendor/model/name', options: [{ id: 'reasoningEffort', value: 'high' }, { id: 'fast', value: true }] });
  assert.throws(() => selection([provider], { effort: 'imaginary' }, model), /Invalid reasoningEffort/);
  assert.throws(() => selection([provider], { model: 'plain', effort: 'high' }, model), /does not advertise an effort/);
  assert.throws(() => selection([{ ...provider, installed: false }], {}, model), /unavailable/);
  assert.throws(() => selection([provider], { option: ['fast=maybe'] }, model), /Invalid fast/);
});

test('empty thread is created without a turn; branch records the actual checkout', async () => {
  const plan = await createPlan(fakeClient(), config, [project], creation);
  assert.equal(plan.commands.length, 1);
  assert.equal(plan.commands[0].type, 'thread.create');
  assert.equal(plan.commands[0].branch, 'main');
  assert.equal(plan.commands[0].worktreePath, null);
  await assert.rejects(createPlan(fakeClient(), config, [project], { ...creation, branch: 'other' }), /Checkout is on main/);
});

test('new worktree uses server bootstrap and the exact prompt, never a metadata-only branch', async t => {
  const file = fixture(t);
  const plan = await createPlan(fakeClient(), config, [project], { ...creation,
    'message-file': file, worktree: true, 'base-branch': 'main', branch: 'agent/fix', effort: 'high' });
  const command = plan.commands[0];
  assert.equal(command.type, 'thread.turn.start');
  assert.deepEqual(command.bootstrap.prepareWorktree, { projectCwd: project.workspaceRoot,
    baseBranch: 'main', branch: 'agent/fix', requireWorktree: true });
  assert.equal(command.bootstrap.runSetupScript, false);
  assert.equal(command.message.text, 'Do the intended task.\nKeep this newline.\n');
  assert.equal(command.bootstrap.createThread.projectId, project.id);
  assert.deepEqual(command.modelSelection, command.bootstrap.createThread.modelSelection);
  await assert.rejects(createPlan(fakeClient(), config, [project], { ...creation, worktree: true }), /first turn/);
  await assert.rejects(createPlan(fakeClient(), { ...config, environment: {} }, [project],
    { ...creation, 'message-file': file, worktree: true }), /does not advertise required worktree/);
});

test('send targets the existing thread, inherits settings, and rejects a mismatched project', async t => {
  const opts = { target: thread.id, 'message-file': fixture(t) };
  const plan = await sendPlan(fakeClient(), config, [project], opts);
  assert.equal(plan.commands.length, 1);
  assert.equal(plan.commands[0].threadId, thread.id);
  assert.equal(plan.commands[0].bootstrap, undefined);
  assert.equal(plan.commands[0].interactionMode, 'plan');
  assert.equal(plan.commands[0].runtimeMode, 'approval-required');
  assert.deepEqual(plan.commands[0].modelSelection, model);
  await assert.rejects(sendPlan(fakeClient(), config, [project, { ...project, id: 'other' }],
    { ...opts, project: 'other' }), /different project/);
});

test('an explicit mode change is dispatched before send; active turns require intentional steering', async t => {
  const opts = { target: thread.id, 'message-file': fixture(t), 'runtime-mode': 'full-access', 'interaction-mode': 'default' };
  const plan = await sendPlan(fakeClient(), config, [project], opts);
  assert.deepEqual(plan.commands.map(c => c.type), ['thread.runtime-mode.set', 'thread.interaction-mode.set', 'thread.turn.start']);
  const active = fakeClient({ ...thread, session: { status: 'running', activeTurnId: 'turn-1' } });
  await assert.rejects(sendPlan(active, config, [project], opts), /active turn/);
  await assert.rejects(sendPlan(active, config, [project], { ...opts, 'allow-active': true }), /before changing/);
  assert.equal((await sendPlan(active, config, [project], { target: thread.id,
    'message-file': opts['message-file'], 'allow-active': true })).threadId, thread.id);
});

test('send persists a chosen effort before starting the turn and checks the real branch', async t => {
  const opts = { target: thread.id, 'message-file': fixture(t), effort: 'high' };
  const plan = await sendPlan(fakeClient(), config, [project], opts);
  assert.deepEqual(plan.commands.map(c => c.type), ['thread.meta.update', 'thread.turn.start']);
  assert.equal(plan.commands[0].modelSelection.options[0].value, 'high');
  const client = fakeClient();
  client.rpc = async () => ({ isRepo: true, refName: 'unexpected' });
  await assert.rejects(sendPlan(client, config, [project], opts), /checkout is on unexpected/);
});

test('dry run and environment mismatch never dispatch a thread command', async t => {
  const client = fakeClient();
  const result = await run(client, { ...creation, 'message-file': fixture(t), 'dry-run': true });
  assert.equal(result.dryRun, true);
  assert.ok(result.prompt.sha256);
  assert.equal(result.prompt.text, undefined);
  assert.equal(client.calls.length, 0);
  await assert.rejects(run(client, { ...creation, 'expect-environment': 'another-server' }), /Environment ID/);
  assert.equal(client.calls.length, 0);
});

test('readback must match prompt, project, model and worktree before success', async t => {
  const plan = await createPlan(fakeClient(), config, [project], { ...creation, 'message-file': fixture(t), worktree: true });
  const observed = { ...thread, id: plan.threadId, branch: plan.expectedBranch, worktreePath: '/fixture/worktree',
    interactionMode: 'default', messages: [{ id: plan.message.messageId, role: 'user', text: plan.message.text }] };
  assert.equal(verify(plan, observed), null);
  assert.match(verify(plan, { ...observed, worktreePath: null }), /Worktree/);
  assert.match(verify(plan, { ...observed, projectId: 'wrong-project' }), /Project/);
  assert.match(verify(plan, { ...observed, messages: [{ ...observed.messages[0], text: 'wrong prompt' }] }), /Prompt/);
  const receipt = await executePlan(fakeClient(observed), plan, config);
  assert.equal(receipt.status, 'prompt-recorded');
  assert.equal(receipt.thread.worktreePath, '/fixture/worktree');
});

test('uncertain dispatch is not retried even if the prompt is already recorded', async t => {
  const plan = await sendPlan(fakeClient(), config, [project], { target: thread.id, 'message-file': fixture(t) });
  const client = fakeClient({ ...thread, messages: [{ id: plan.message.messageId, text: plan.message.text, role: 'user' }] });
  client.dispatch = async command => { client.calls.push(command); const error = new Error('lost reply'); error.uncertain = true; throw error; };
  let intent;
  await assert.rejects(executePlan(client, plan, config, { emitIntent: x => { intent = x; } }), error => {
    assert.equal(error.receipt.observed.promptRecorded, true);
    assert.equal(error.receipt.uncertain, true);
    return true;
  });
  assert.equal(client.calls.length, 1);
  assert.equal(intent.intent.threadId, thread.id);
});

test('accepted dispatch with a wrong prompt is a verification failure, not success', async t => {
  const plan = await sendPlan(fakeClient(), config, [project], { target: thread.id, 'message-file': fixture(t) });
  const client = fakeClient();
  await assert.rejects(executePlan(client, plan, config, { verifyTimeoutMs: 0 }), /Verification pending/);
  assert.equal(client.calls.length, 1);
});

test('unknown CLI flags fail instead of silently altering the task', () => {
  assert.throws(() => parse(['create', '--worktre']), /Unknown option/);
});
