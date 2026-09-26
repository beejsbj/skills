#!/usr/bin/env node
// T3 Code commands for agents. Node 22+; no package installation required.
import { readFileSync, realpathSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { randomUUID, createHash } from 'node:crypto';
import { parseArgs, isDeepStrictEqual } from 'node:util';
import { pathToFileURL } from 'node:url';
import { withClient } from './transport.mjs';

const MODES = ['approval-required', 'auto-accept-edits', 'auto', 'full-access'];
const HELP = `T3 Code thread control (Node 22+)

  node t3ctl.mjs projects
  node t3ctl.mjs threads [--project ID]
  node t3ctl.mjs models [--instance ID] [--model SLUG]
  node t3ctl.mjs show THREAD_ID [--messages]
  node t3ctl.mjs create --project ID --title TITLE --runtime-mode MODE
      [--instance ID --model SLUG] [--effort VALUE] [--option KEY=VALUE ...]
      [--message-file FILE] [--interaction-mode default|plan]
      [--worktree --base-branch REF --branch NEW_BRANCH [--run-setup]]
      [--worktree-path EXISTING_PATH] [--branch EXPECTED_CURRENT_BRANCH]
      [--dry-run]
  node t3ctl.mjs send THREAD_ID --message-file FILE [--project EXPECTED_ID]
      [--instance ID --model SLUG] [--effort VALUE] [--option KEY=VALUE ...]
      [--runtime-mode MODE] [--interaction-mode default|plan]
      [--allow-active] [--dry-run]

Common: --base-dir PATH (default ~/.t3), --t3-bin PATH, --timeout-ms N,
        --origin URL (requires T3_AUTH_TOKEN), --expect-environment ID
Modes: ${MODES.join(', ')}

New threads require an explicit access mode. Sending preserves existing modes
unless overridden. No message creates an empty real thread. A message starts
an agent turn. --worktree creates a fresh worktree through T3 and needs a message.
Without --worktree, the current checkout is used; --branch validates its current
branch and never switches it. --worktree-path attaches a verified local worktree.
Project selectors accept full IDs or unique exact titles. Model slugs are literal.
--dry-run reads server state and prints a plan with prompt hashes; it dispatches
no thread commands. Commands are never retried automatically.
`;

const stringOptions = ['project', 'title', 'instance', 'model', 'effort', 'message-file',
  'runtime-mode', 'interaction-mode', 'base-branch', 'branch', 'worktree-path',
  'base-dir', 't3-bin', 'origin', 'expect-environment', 'timeout-ms'];
const booleanOptions = ['help', 'messages', 'worktree', 'run-setup', 'allow-active', 'dry-run'];
export function parse(argv) {
  const { values, positionals } = parseArgs({ args: argv, allowPositionals: true, strict: true,
    options: { ...Object.fromEntries(stringOptions.map(k => [k, { type: 'string' }])),
      ...Object.fromEntries(booleanOptions.map(k => [k, { type: 'boolean' }])),
      option: { type: 'string', multiple: true } } });
  return { ...values, command: positionals[0], target: positionals[1], extra: positionals.slice(2) };
}

function requireThat(condition, message) { if (!condition) throw new Error(message); }
const digest = text => createHash('sha256').update(text).digest('hex');
const fresh = () => ({ commandId: randomUUID(), createdAt: new Date().toISOString() });
const nonempty = value => typeof value === 'string' && value.trim().length > 0;
const identity = environment => Object.fromEntries(['environmentId', 'label', 'serverVersion', 'platform']
  .filter(k => environment[k] !== undefined).map(k => [k, environment[k]]));

export function resolveProject(projects, selector) {
  const active = projects.filter(p => !p.deletedAt);
  const id = active.find(p => p.id === selector);
  if (id) return id;
  const matches = active.filter(p => p.title === selector);
  requireThat(matches.length === 1, `Project ${JSON.stringify(selector)} has ${matches.length} exact title matches; use a full ID from projects.`);
  return matches[0];
}

function chosenProvider(providers, instanceId) {
  const provider = providers.find(p => p.instanceId === instanceId);
  requireThat(provider, `Provider instance ${instanceId} is not configured on this environment.`);
  requireThat(provider.enabled && provider.installed && provider.availability !== 'unavailable'
    && !['error', 'disabled'].includes(provider.status) && provider.auth?.status !== 'unauthenticated',
  `Provider instance ${instanceId} is unavailable: ${provider.status}. Inspect models on this environment.`);
  return provider;
}

export function selection(providers, opts, fallback) {
  const instanceId = opts.instance ?? fallback?.instanceId;
  const model = opts.model ?? fallback?.model;
  requireThat(nonempty(instanceId) && nonempty(model), 'Select --instance and --model from models; this project has no default selection.');
  requireThat(!opts.instance || opts.model || opts.instance === fallback?.instanceId,
    'Changing provider instance requires --model.');
  const provider = chosenProvider(providers, instanceId);
  const entry = provider.models.find(m => m.slug === model);
  requireThat(entry, `Model ${model} is absent from instance ${instanceId}'s live catalog.`);
  const descriptors = entry.capabilities?.optionDescriptors ?? [];
  const same = instanceId === fallback?.instanceId && model === fallback?.model;
  const options = new Map((same ? fallback.options ?? [] : []).map(o => [o.id, o.value]));
  const requested = new Map();
  for (const option of opts.option ?? []) {
    const split = option.indexOf('=');
    requireThat(split > 0 && split < option.length - 1, '--option requires KEY=VALUE.');
    const id = option.slice(0, split), value = option.slice(split + 1);
    requireThat(!requested.has(id), `Option ${id} was provided twice.`);
    requested.set(id, value === 'true' ? true : value === 'false' ? false : value);
  }
  if (opts.effort) {
    const effort = descriptors.find(d => d.id === 'reasoningEffort') ?? descriptors.find(d => d.id === 'effort');
    requireThat(effort, `Model ${model} does not advertise an effort option. Inspect models and use its advertised --option if appropriate.`);
    requireThat(!requested.has(effort.id), 'Effort was provided both as --effort and --option.');
    requested.set(effort.id, opts.effort);
  }
  for (const [id, value] of requested) {
    const desc = descriptors.find(d => d.id === id);
    requireThat(desc, `Model ${model} does not advertise option ${id}.`);
    const valid = desc.type === 'boolean' ? typeof value === 'boolean' : desc.options?.some(o => o.id === value);
    requireThat(valid, `Invalid ${id} value ${JSON.stringify(value)}. Check this model's live option descriptors.`);
    options.set(id, value);
  }
  return { instanceId, model, ...(options.size ? { options: [...options].map(([id, value]) => ({ id, value })) } : {}) };
}

export function summary(thread) {
  return Object.fromEntries(['id', 'title', 'projectId', 'branch', 'worktreePath', 'modelSelection',
    'runtimeMode', 'interactionMode', 'archivedAt', 'deletedAt', 'latestTurn'].map(k => [k, thread[k]]).concat([
    ['session', thread.session ? { status: thread.session.status, activeTurnId: thread.session.activeTurnId,
      lastError: thread.session.lastError } : null] ]));
}

function readMessage(opts) {
  if (!opts['message-file']) return null;
  const text = readFileSync(opts['message-file'], 'utf8');
  requireThat(nonempty(text), 'The prompt file is empty.');
  return { messageId: randomUUID(), role: 'user', text, attachments: [] };
}

function checkModes(opts) {
  if (opts['runtime-mode']) requireThat(MODES.includes(opts['runtime-mode']), `Invalid runtime mode. Choose ${MODES.join(', ')}.`);
  if (opts['interaction-mode']) requireThat(['default', 'plan'].includes(opts['interaction-mode']), 'Interaction mode must be default or plan.');
}

function verifyLocalWorktree(projectRoot, worktreePath) {
  const common = cwd => realpathSync(execFileSync('git', ['-C', cwd, 'rev-parse', '--path-format=absolute', '--git-common-dir'],
    { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim());
  requireThat(common(projectRoot) === common(worktreePath), 'The existing worktree belongs to another repository.');
}

export async function createPlan(client, config, projects, opts) {
  requireThat(opts.project && nonempty(opts.title), 'create requires --project and --title.');
  requireThat(opts['runtime-mode'], 'create requires an explicit --runtime-mode.');
  requireThat(!(opts.worktree && opts['worktree-path']), 'Choose a new worktree or an existing worktree, not both.');
  requireThat(opts.worktree || (!opts['base-branch'] && !opts['run-setup']), '--base-branch and --run-setup require --worktree.');
  const project = resolveProject(projects, opts.project);
  const modelSelection = selection(config.providers, opts, project.defaultModelSelection);
  const message = readMessage(opts);
  requireThat(!opts.worktree || message, 'A new T3 worktree is prepared with the first turn. Provide --message-file, or attach an existing worktree.');
  let cwd = project.workspaceRoot;
  if (opts['worktree-path']) {
    requireThat(!opts.origin, 'Run the helper on the owning machine to validate an existing worktree.');
    cwd = realpathSync(opts['worktree-path']);
    verifyLocalWorktree(project.workspaceRoot, cwd);
  }
  const git = await client.rpc('vcs.refreshStatus', { cwd });
  if (!opts.worktree && opts.branch) requireThat(git.refName === opts.branch,
    `Checkout is on ${git.refName ?? '(no branch)'}, not ${opts.branch}. Choose a new worktree or an existing checkout on that branch.`);
  const threadId = randomUUID();
  const metadata = { projectId: project.id, title: opts.title, modelSelection,
    runtimeMode: opts['runtime-mode'], interactionMode: opts['interaction-mode'] ?? 'default',
    branch: git.refName ?? null, worktreePath: opts['worktree-path'] ? cwd : null,
    createdAt: new Date().toISOString() };
  let expectedBranch = metadata.branch;
  let command;
  if (message) {
    command = { type: 'thread.turn.start', ...fresh(), threadId, message, modelSelection,
      runtimeMode: metadata.runtimeMode, interactionMode: metadata.interactionMode,
      bootstrap: { createThread: metadata } };
    if (opts.worktree) {
      requireThat(config.environment.capabilities?.requiredWorktreeBootstrap === true,
        'This server does not advertise required worktree bootstrap. Check its version before starting an isolated thread.');
      const baseBranch = opts['base-branch'] ?? git.refName;
      requireThat(git.isRepo && nonempty(baseBranch), 'A worktree needs a Git repository and --base-branch (or a current branch).');
      expectedBranch = opts.branch ?? `agent/t3-${threadId.slice(0, 8)}`;
      command.bootstrap.prepareWorktree = { projectCwd: project.workspaceRoot, baseBranch,
        branch: expectedBranch, requireWorktree: true };
      command.bootstrap.runSetupScript = Boolean(opts['run-setup']);
    }
  } else command = { type: 'thread.create', commandId: randomUUID(), threadId, ...metadata };
  return { threadId, project, message, commands: [command], modelSelection,
    runtimeMode: metadata.runtimeMode, interactionMode: metadata.interactionMode,
    expectedBranch, checkoutBranch: git.refName ?? null,
    worktree: opts.worktree ? 'new' : opts['worktree-path'] ? 'existing' : 'checkout',
    worktreePath: metadata.worktreePath };
}

export async function sendPlan(client, config, projects, opts) {
  requireThat(nonempty(opts.target), 'send requires a thread ID.');
  const { thread } = await client.request('GET', `/api/orchestration/threads/${encodeURIComponent(opts.target)}`);
  requireThat(thread?.id === opts.target && !thread.deletedAt, 'The requested thread does not exist on this server.');
  requireThat(!thread.archivedAt, 'Thread is archived; unarchive it deliberately before sending.');
  if (opts.project) requireThat(thread.projectId === resolveProject(projects, opts.project).id,
    'Thread belongs to a different project than --project. No message sent.');
  requireThat(opts['allow-active'] || !(thread.session?.activeTurnId || ['running', 'starting'].includes(thread.session?.status)),
    'Thread has an active turn. Inspect it; --allow-active explicitly permits provider-specific steering/queueing.');
  const message = readMessage(opts);
  requireThat(message, 'send requires --message-file.');
  const modelSelection = selection(config.providers, opts, thread.modelSelection);
  const provider = chosenProvider(config.providers, modelSelection.instanceId);
  if (thread.session && provider.requiresNewThreadForModelChange) requireThat(
    modelSelection.model === thread.modelSelection.model && modelSelection.instanceId === thread.modelSelection.instanceId,
    'This provider requires a new thread to change models.');
  const runtimeMode = opts['runtime-mode'] ?? thread.runtimeMode;
  const interactionMode = opts['interaction-mode'] ?? thread.interactionMode;
  const project = projects.find(p => p.id === thread.projectId && !p.deletedAt);
  requireThat(project, 'The thread project is missing or deleted.');
  const checkout = await client.rpc('vcs.refreshStatus', { cwd: thread.worktreePath ?? project.workspaceRoot });
  requireThat(!thread.branch || checkout.refName === thread.branch,
    `Thread expects branch ${thread.branch}, but its checkout is on ${checkout.refName ?? '(no branch)'}. Resolve the checkout before sending.`);
  const modelChanged = !isDeepStrictEqual(modelSelection, thread.modelSelection);
  if (thread.session?.activeTurnId || ['running', 'starting'].includes(thread.session?.status)) requireThat(
    !modelChanged && runtimeMode === thread.runtimeMode && interactionMode === thread.interactionMode,
    'Wait for the active turn to finish before changing its model or modes.');
  const commands = [];
  if (modelChanged) commands.push({ type: 'thread.meta.update', commandId: randomUUID(), threadId: thread.id, modelSelection });
  if (runtimeMode !== thread.runtimeMode) commands.push({ type: 'thread.runtime-mode.set', ...fresh(), threadId: thread.id, runtimeMode });
  if (interactionMode !== thread.interactionMode) commands.push({ type: 'thread.interaction-mode.set', ...fresh(), threadId: thread.id, interactionMode });
  commands.push({ type: 'thread.turn.start', ...fresh(), threadId: thread.id, message,
    modelSelection, runtimeMode, interactionMode });
  return { threadId: thread.id, project,
    message, commands, modelSelection, runtimeMode, interactionMode,
    expectedBranch: thread.branch, checkoutBranch: checkout.refName,
    worktree: thread.worktreePath ? 'existing' : 'checkout', worktreePath: thread.worktreePath };
}

export function planSummary(plan, environment, origin) {
  return { environment: identity(environment), origin, threadId: plan.threadId, projectId: plan.project?.id,
    workspaceRoot: plan.project?.workspaceRoot, modelSelection: plan.modelSelection,
    runtimeMode: plan.runtimeMode, interactionMode: plan.interactionMode,
    branch: plan.expectedBranch, checkoutBranch: plan.checkoutBranch ?? plan.expectedBranch,
    worktree: plan.worktree, worktreePath: plan.worktreePath,
    commands: plan.commands.map(c => ({ type: c.type, commandId: c.commandId })),
    prompt: plan.message ? { messageId: plan.message.messageId, sha256: digest(plan.message.text), bytes: Buffer.byteLength(plan.message.text) } : null };
}

export function verify(plan, thread) {
  if (!thread || thread.id !== plan.threadId || thread.deletedAt) return 'Thread is absent.';
  if (thread.projectId !== plan.project?.id) return 'Project does not match.';
  if (thread.branch !== plan.expectedBranch) return 'Branch does not match.';
  if (plan.worktree === 'new' && !thread.worktreePath) return 'Worktree has not been assigned.';
  if (plan.worktree !== 'new' && (thread.worktreePath ?? null) !== (plan.worktreePath ?? null)) return 'Worktree path does not match.';
  if (thread.runtimeMode !== plan.runtimeMode || thread.interactionMode !== plan.interactionMode) return 'Thread modes do not match.';
  if (thread.modelSelection?.instanceId !== plan.modelSelection.instanceId || thread.modelSelection?.model !== plan.modelSelection.model) return 'Model selection does not match yet.';
  for (const option of plan.modelSelection.options ?? []) {
    if (!(thread.modelSelection.options ?? []).some(o => o.id === option.id && isDeepStrictEqual(o.value, option.value))) return `Model option ${option.id} does not match yet.`;
  }
  if (plan.message && !(thread.messages ?? []).some(m => m.id === plan.message.messageId && m.role === 'user' && m.text === plan.message.text)) return 'Prompt has not been recorded exactly.';
  return null;
}

export async function executePlan(client, plan, config, { emitIntent = () => {}, verifyTimeoutMs = 5000 } = {}) {
  const intent = planSummary(plan, config.environment, client.origin);
  emitIntent({ intent }); // IDs survive a killed client or a lost server response.
  let phase = 'dispatch';
  try {
    for (const command of plan.commands) await client.dispatch(command);
    phase = 'verify';
    const deadline = Date.now() + verifyTimeoutMs;
    let problem;
    do {
      const { thread } = await client.request('GET', `/api/orchestration/threads/${encodeURIComponent(plan.threadId)}`);
      problem = verify(plan, thread);
      if (!problem) return { ok: true, ...intent, status: plan.message ? 'prompt-recorded' : 'thread-created',
        thread: summary(thread), note: plan.message ? 'Command accepted and prompt verified; agent completion is not implied.' : undefined };
      if (Date.now() < deadline) await new Promise(r => setTimeout(r, 200));
    } while (Date.now() < deadline);
    throw new Error(`Verification pending: ${problem}`);
  } catch (error) {
    error.receipt = { ok: false, ...intent, phase, uncertain: Boolean(error.uncertain) || phase === 'verify',
      instruction: 'Inspect this exact thread and message ID before any retry. Creation or delivery may be partial.' };
    try {
      const { thread } = await client.request('GET', `/api/orchestration/threads/${encodeURIComponent(plan.threadId)}`);
      error.receipt.observed = { thread: summary(thread), promptRecorded: Boolean(plan.message &&
        thread.messages?.some(m => m.id === plan.message.messageId && m.text === plan.message.text)) };
    } catch { error.receipt.observed = 'Readback unavailable.'; }
    throw error;
  }
}

export async function run(client, opts, output = () => {}) {
  checkModes(opts);
  const config = await client.rpc('server.getConfig', {});
  if (opts['expect-environment']) requireThat(config.environment.environmentId === opts['expect-environment'],
    'Environment ID does not match --expect-environment. No thread command sent.');
  const envelope = { environment: identity(config.environment), origin: client.origin };
  if (opts.command === 'models') return { ...envelope, providers: config.providers
    .filter(p => !opts.instance || p.instanceId === opts.instance)
    .map(p => ({ instanceId: p.instanceId, driver: p.driver, enabled: p.enabled, installed: p.installed,
      status: p.status, availability: p.availability, requiresNewThreadForModelChange: p.requiresNewThreadForModelChange,
      models: p.models.filter(m => !opts.model || m.slug === opts.model).map(m => ({ slug: m.slug,
        name: m.name, isDefault: m.isDefault, options: m.capabilities?.optionDescriptors ?? [] })) })) };
  if (opts.command === 'show') {
    requireThat(opts.target, 'show requires a thread ID.');
    const { thread } = await client.request('GET', `/api/orchestration/threads/${encodeURIComponent(opts.target)}`);
    return { ...envelope, thread: summary(thread), messages: (thread.messages ?? []).map(m => ({ id: m.id,
      role: m.role, ...(opts.messages ? { text: m.text } : { sha256: digest(m.text ?? '') }) })) };
  }
  const snapshot = await client.request('GET', '/api/orchestration/snapshot');
  if (opts.command === 'projects') return { ...envelope, projects: snapshot.projects.filter(p => !p.deletedAt)
    .map(p => ({ id: p.id, title: p.title, workspaceRoot: p.workspaceRoot,
      defaultModelSelection: p.defaultModelSelection, defaultThreadEnvMode: p.defaultThreadEnvMode })) };
  if (opts.command === 'threads') {
    const project = opts.project ? resolveProject(snapshot.projects, opts.project) : null;
    return { ...envelope, threads: snapshot.threads.filter(t => !t.deletedAt && (!project || t.projectId === project.id)).map(summary) };
  }
  const plan = opts.command === 'create' ? await createPlan(client, config, snapshot.projects, opts)
    : await sendPlan(client, config, snapshot.projects, opts);
  if (opts['dry-run']) return { dryRun: true, ...planSummary(plan, config.environment, client.origin) };
  return executePlan(client, plan, config, { emitIntent: output });
}

async function main() {
  let opts;
  try {
    opts = parse(process.argv.slice(2));
    if (opts.help || !opts.command) { console.log(HELP); return; }
    requireThat(['projects', 'threads', 'models', 'show', 'create', 'send'].includes(opts.command), 'Unknown command; use --help.');
    requireThat(!opts.extra.length && (!(opts.target) || ['show', 'send'].includes(opts.command)), 'Unexpected positional argument; use --help.');
    if (!['create', 'send'].includes(opts.command)) requireThat(!opts['message-file'], '--message-file applies only to create/send.');
    if (opts.command === 'send') requireThat(!opts.worktree && !opts['worktree-path'] && !opts.branch && !opts['base-branch'], 'An existing thread keeps its checkout. Create a new thread to change branch/worktree.');
    const timeoutMs = opts['timeout-ms'] ? Number(opts['timeout-ms']) : 60000;
    requireThat(Number.isInteger(timeoutMs) && timeoutMs > 0 && timeoutMs <= 600000, '--timeout-ms must be between 1 and 600000.');
    const result = await withClient({ baseDir: opts['base-dir'], t3Bin: opts['t3-bin'], origin: opts.origin, timeoutMs },
      client => run(client, opts, value => process.stderr.write(`${JSON.stringify(value)}\n`)));
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(JSON.stringify({ ok: false, ...error.receipt, error: error.message }, null, 2));
    process.exitCode = 1;
  }
}
if (process.argv[1] && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href) await main();
