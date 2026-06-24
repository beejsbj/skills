# Cockpit Redesign — Design Spec

Date: 2026-06-24
Status: Approved (Burooj), ready for implementation
Author: Burooj + cockpit (Opus) brainstorming session

This spec is the single source of truth for the cockpit redesign. Implementation
agents MUST follow the exact names, lanes, labels, and verbs defined here so the
skill docs, the CLI, and the board all agree.

---

## 0. Governing principle: wu-wei / ergonomic discipline

Cockpit's rules are **river banks, not cages**. They shape where attention flows so
the right move is the *easy* move — they do not constrain the agent against the grain.

Corollary, applied throughout: **under-discipline beats over-discipline.** Over-constrained
agents fail *because they are trying to comply*. When in doubt, slim. The `linear` skill
especially stays minimal. Trust the agent; give it banks, not a script.

This principle resolves design ties: prefer the natural shape of the work over an
artificially minimal one (this is why `Grilling` is its own lane), and prefer fewer,
clearer rules over exhaustive ones.

---

## 1. Interaction model (the spine)

```
You  ⇄  Cockpit (manager-coworker)  ⇄  Workers
```

- **You** talk to **cockpit**, not to worker sessions. Live (a cockpit session) or
  async (Linear comments from phone/web).
- **Cockpit** is the manager-coworker in the Linear space: it triages with you,
  dispatches and binds workers, handles your comments, keeps the board honest.
- **Workers** are dispatched provider sessions (Codex/Claude/opencode/Cursor) or
  native subagents. They do the actual project work in the project's own repo.

Cockpit rarely makes you talk to a worker directly. You delegate to cockpit; cockpit
delegates to workers.

---

## 2. Linear surface: app-actor graph only

Cockpit knows **one** Linear surface: the **app-actor GraphQL API** (`https://api.linear.app/graphql`),
authored as the Cockpit app actor, for **both reads and writes**.

- **Remove** the kyaukyuai `linear` CLI read/fallback path entirely. It is the second
  surface that confuses cockpit. All board reads go through the app-actor GraphQL path
  that already exists (`load_linear_issues_graphql`, `load_linear_issue_graphql`).
- Keep the app-actor auth machinery (`COCKPIT_LINEAR_APP_ACCESS_TOKEN`, client-credentials,
  Keychain). Keep `linear-doctor` but it now only checks the GraphQL app-actor surface
  (no `linear` binary version/capabilities checks).
- The `./node_modules/.bin/linear` dependency and all `run_linear` / `run_linear_json`
  call sites are removed. If a needed read is not yet implemented in GraphQL, implement
  it in GraphQL — do not reintroduce the CLI.

---

## 3. Status lanes (10 → 9 + Canceled)

The canonical Linear workflow states. Exact names matter (used as strings in the CLI).

| Lane | Meaning | Who acts next |
|---|---|---|
| `Inbox` | Intake. Everything new or uncl­arified. Absorbs old Needs-triage / Backlog / Todo. | Cockpit + you (triage) |
| `Needs-info` | Context gathering. Bounded, does **not** linger. Fed by the repo (an agent digs) **and/or** by you (supply a fact). Usually comes *after* grilling. | Agent or you |
| `Grilling` | Deep shaping — clarify intent, problem-solve, sketch the approach (pseudocode-vibe). Interactive with you, **can linger across sessions**. Optional; not every issue needs it. Session-ownable. | You + a grilling session |
| `Ready for Burooj` | You are the next actor: a **decision / approval / judgment / physical action**. (Renamed from "Needs Burooj".) | You |
| `Ready for agent` | Cold-dispatchable. A worker can start from the issue body. | Cockpit dispatches |
| `Blocked` | Waiting on a **real external dependency** (another issue, an outside party). NOT "needs investigation" — that is `Needs-info`. | Blocker resolves |
| `In Progress` | A worker session is executing it. Exactly one `session:*` label. | Worker |
| `In Review` | PR / checks / review phase. | You / reviewer |
| `Done` | Complete. No `session:*` label. Final receipt left. | — |
| `Canceled` | Dead idea (Linear-native). Replaces the old "Parked" graveyard. | — |

**Killed:** `Needs triage`, `Backlog`, `Todo`, `Parked`.

### Shaping region (the pipeline)

```
Inbox → [Grilling?] → [Needs-info?] → Ready for agent / Ready for Burooj
                                    ↘ Blocked (real external block)
```

- Meaty issue: grill out the approach, then gather the context that approach needs, then ready.
- Simple issue: skip grilling; maybe skip needs-info; go straight to Ready.
- `Grilling` and `Needs-info` are **distinct lanes** because they split by *who acts*
  (you interactively vs an agent/quick-fact) and by *depth* (approach vs context).
- The thin edge `Needs-info (from you)` vs `Ready for Burooj` is **deliberate**:
  Needs-info = *supply a fact/context*; Ready for Burooj = *make a decision / approve / act*.

---

## 4. Labels

Keep labels lightweight. Labels never encode workflow position (that is status).

- `type:*` — KEPT. Domain/work kind: `type:bug`, `type:cleanup`, `type:research`,
  `type:chore`, `type:seed`, and **new `type:grilling`** (a flavor of work that will
  pass through the Grilling lane / Ready-for-Burooj).
- `session:<provider>:<id>` — KEPT. Active session binding only, on active lanes only.
- `workflow:issue-pr` — KEPT (optional training rail), unchanged.
- `formation:*` — **REMOVED.** Delete the labels and all code/doc that reads or writes them.
- `mode:*`, `agent:*` — remove unless trivially in use; do not add new dependence on them.

---

## 5. Killed vocabulary

- **"formation"** — the word, the `formation:*` labels, and the seed/clarify/scout/research/execute
  taxonomy as a *named concept*. Triage just routes to the lanes above.
- **research vs execute distinction** — gone. A research issue's answer *is* its execution.
  At dispatch, cockpit reads the issue and writes the appropriate brief; no persistent tag.
- **the `scout` verb / scout as machinery** — gone. "Scouting" is simply an issue in
  `Needs-info` whose worker (often a native subagent) investigates. No special command.
- **Parked** — gone (Canceled for dead, Inbox for alive).

---

## 6. Comments

Comments are cockpit's vital async channel. Three roles:

1. **Your async channel to cockpit.** From phone/web you drop notes: clarity, "split this,"
   "move it," "this is done," instructions. Cockpit's `inbox` surfaces **your unresolved
   comments** as its work queue, and cockpit handles each (often by spawning a per-issue
   native subagent to act on it).
2. **Cockpit Thread (one per issue).** A single top-level comment; all receipts / audit /
   log trails are **replies under it**. Keep the existing Cockpit Thread mechanism
   (`comment`, `bind`, `release`, `done` create/reuse it).
3. **Questions thread (one per issue).** Questions *for you* live as a dedicated comment
   thread you can reply to **per-question** — NOT as checkboxes in the issue body. This
   replaces body-checkbox questions. Cockpit creates/reuses a `Questions` top-level
   comment and adds each question as a reply.

Resolution: reply before resolving; resolve only when the reply says what closed it.

---

## 7. Skill split (the de-bloat)

Two skills, clear seam.

### `linear` (new skill — lean, board discipline)

Location: `/Users/burooj/Projects/skills/linear/SKILL.md` (+ a thin reference only if needed).

Contents — the minimum a worker needs to touch the board correctly:
- The ontology (team/project/issue/session/PR/comment/dependency).
- Issue-body shape (Goal / Context / Done-when / Constraints — questions go to the
  Questions comment thread, NOT the body).
- The 9 lanes + Canceled and their meaning (§3).
- Label taxonomy (§4).
- The comment model (§6).
- The app-actor graph surface as the only write path; cockpit commands for writes.

This is the skill **handed to dispatched sessions**. It must NOT contain orchestration
doctrine (dispatch, binding strategy, triage, the manager model). Keep it short.

### `cockpit` (rewritten — orchestration, slim)

Location: `/Users/burooj/Projects/skills/cockpit/SKILL.md` (+ slimmed references).

Contents — the manager brain:
- The interaction model (§1) and the wu-wei principle (§0).
- Triage-with-Burooj over the lanes; the shaping pipeline (§3).
- Dispatch / bind / release / done; comment-handling; stop gates.
- `depends on linear` — references the `linear` skill rather than restating board rules.

Fold the current 5 references down hard. Preserve verbatim only: the **app-actor write
auth** rules and the **stop gates**. Everything else slims or merges. Remove all
formation/scout/dispatch-prompt-contract machinery and the formation-examples file.

---

## 8. Verb surface (`cockpit.py`, agent-facing)

`cockpit.py` is **river banks for agents**, not a human tool. Ergonomics target agents.

### Keep (update to new lanes/surface)
- `status`, `board` — use the 9 lanes.
- `issue BJS-X` — show one issue + binding (GraphQL read).
- `inbox` — now ALSO surfaces **your unresolved comments** as work items, alongside
  issues needing a triage decision. (Fold the old `inbox-review` / `comments-review`
  intent in here; drop those as separate verbs.)
- `bind BJS-X <provider> <id>` — low-level: attach an already-running session. Unchanged
  semantics; `dispatch` calls it internally.
- `release BJS-X`, `done BJS-X` — unchanged.
- `comment` / `comment-resolve` / `comment-unresolve` — keep; support the Questions thread.
- `audit` — session-label drift, on the 9 lanes.
- `sessions` — local session discovery (unchanged).
- `linear-doctor` — app-actor-only checks now.

### Add
- `dispatch BJS-X` — the heavy verb. Execution only. Steps:
  1. Resolve the project's dir/repo from the issue's project (every project is coupled
     to a directory and/or a GitHub repo — deterministic, **no asking**).
  2. Ensure the working dir exists: if missing and the project has a repo → **clone**;
     if a brand-new project → **create the dir**.
  3. Ensure it is a saved Codex project via `codex app <dir>` when the target provider
     is Codex. (There is no "pinning"; the dir must be saved to Codex to create a thread.)
  4. Launch a session in that dir (via the `agents` skill / provider CLI / Codex thread
     tools) with the issue brief derived from the issue body + unresolved comments.
  5. `bind` it and move the issue to `In Progress`.
  - Dispatch does not stop for folder-create / clone / `codex app`. It DOES still respect
    the global stop gates (money / accounts / security / deletion / email-send).

### Remove
- `issue-doctor` (formation classifier), `dispatch-prompt` (formation prompts),
  `inbox-review`, `comments-review` (folded into `inbox`).

### Needs-info / scouting
No verb. A `Needs-info` issue is handled by cockpit spawning a **native subagent**
(harness Task/subagent, per the `agents` skill rule: result-only work in the current
harness) pointed at the project dir, read-only, writing its findings back as an issue
comment. Or by you supplying the fact in a comment.

---

## 9. Board migration (GATED — not auto-run by implementation agents)

Changing live Linear workflow states and bulk-relabeling 106 issues is a stop-gate
(broad workflow change + canonical source-of-truth). Implementation agents MUST NOT
mutate the live board. Instead, produce the migration as a **reviewable plan/script**
that Burooj runs or approves separately.

Migration mapping:
- `Needs triage` → `Inbox`; `Backlog` → `Inbox`; `Todo` → `Inbox`.
- `Parked` → `Inbox` (if alive) or `Canceled` (if dead) — needs human judgment per issue,
  so list them; do not bulk-decide.
- `Needs Burooj` → `Ready for Burooj` (rename).
- Create new states: `Needs-info`, `Grilling`.
- Strip all `formation:*` labels; delete the `formation:*` label definitions.
- Add `type:grilling` label definition.

---

## 10. Implementation tasks (for subagents)

Three parallel, file-disjoint tasks. Each agent reads THIS spec first. Local files only;
no live Linear mutation; no commits without Burooj approval.

- **Task A — `linear` skill (new).** Create `/Users/burooj/Projects/skills/linear/SKILL.md`
  per §7. Lean, worker-facing. Frontmatter `name: linear` + a precise `description`.
- **Task B — `cockpit` skill rewrite.** Rewrite `/Users/burooj/Projects/skills/cockpit/SKILL.md`
  and slim `references/` per §0,§1,§3–§8. Kill formation/scout/dispatch-prompt machinery;
  delete `formation-examples.md`; preserve app-actor auth + stop gates verbatim. Point to
  the `linear` skill.
- **Task C — `cockpit.py` refactor.** In `/Users/burooj/Projects/skills/cockpit/scripts/cockpit.py`:
  app-actor-only (remove the linear-CLI path, §2); new 9 lanes (§3); remove `formation:*`
  logic (§4,§5); `inbox` surfaces Burooj comments (§6,§8); Questions-thread comment support
  (§6); add `dispatch` verb (§8) — implement the resolve/clone/`codex app`/launch/bind/move
  chain, shelling out where needed; remove `issue-doctor`/`dispatch-prompt`/`inbox-review`/
  `comments-review`. MUST end with `python3 -m py_compile scripts/cockpit.py` passing and
  `git diff --check` clean. Where a behavior is ambiguous, leave a clearly-marked TODO and
  a note in the final report rather than guessing.

After A/B/C land, cockpit (Opus) reviews the combined diff, then the GATED board migration
(§9) is presented to Burooj.
