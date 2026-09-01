---
name: linear
description: "Use when you need to understand or update Burooj's Linear board as configured: board ontology, lanes, labels, issue bodies, comments, dependencies, receipts, and the cockpit app-actor write path."
---

# Linear Board Discipline

Linear is canonical. Do not track workflow state anywhere else.

This skill defines Burooj's Linear board discipline and write path. It is shared context for any session that needs to read or update Linear state without inventing a parallel workflow.

Use this skill to:

- understand issue lanes, labels, comments, dependencies, and receipt expectations;
- make or request durable board updates through cockpit commands;
- avoid inventing parallel workflow state in chat, local files, or provider session titles.

This is not an orchestration skill. Do not use it to choose workers, launch sessions, or manage cockpit flow; use the `cockpit` skill for that.

---

## Ontology

- **Team:** `Bjs-projects` / key `BJS`.
- **Project:** a durable repo, area, or outcome lane. Read the live project list; do not trust this file for current project names.
- **Issue:** a packet of attention with enough context for a fresh worker to start cold.
- **Session:** one active attempt by Codex, Claude, opencode, Cursor, or another provider.
- **PR:** review artifact when an issue produces code.
- **Comment:** durable trail — receipts, questions, decisions. Never leave important state trapped in chat.
- **Dependency:** a Linear issue relation. Do not mark `Blocked` without a blocker issue or explicit comment.

---

## Issue Body Shape

```markdown
## Goal

One concrete outcome.

## Context

Source, repo/path, links, prior decisions — anything needed to avoid re-asking.

## Done when

- Observable completion condition.
- PR, checks, receipt, or review expectation where relevant.

Write Done-when **goal-grade**: one measurable end state, a stated check that proves it (a command, artifact, or count), and the constraints that must hold on the way — so a worker can adopt it verbatim as its native `/goal` condition (Claude Code and Codex both evaluate one after every turn).

## Constraints

- Boundaries, non-goals, approval gates, taste/security/account/money limits.
```

**Questions go to the Questions comment thread, not the body.** If you have a question for Burooj, post it as a reply under the issue's `Questions` top-level comment (create one if absent). Do not add question checkboxes to the issue body.

Omit any section that does not apply; do not write `N/A`.

Title discipline: plain verb + object + outcome. Prefer repo/path names when they disambiguate. Avoid vague umbrella titles.

---

## Status Lanes

| Lane | One-line meaning |
|---|---|
| `Inbox` | Intake; everything new or unclarified. |
| `Needs-info` | Context-gathering; an agent digs or you supply a fact. Bounded — does not linger. |
| `Grilling` | Deep shaping — clarify intent, sketch approach. Interactive with Burooj; can span sessions. |
| `Ready for Burooj` | Burooj is the next actor: a decision, approval, judgment, or physical action. Requires a current `For Burooj` brief (see Comment Model). |
| `Ready for agent` | Cold-dispatchable: a smart model has distilled the issue into a self-contained `/goal` a cheaper executor can run without judgment. |
| `Blocked` | Real external dependency (another issue or outside party). NOT "needs investigation." |
| `In Progress` | A worker session is executing it. Exactly one `session:*` label must be present. |
| `In Review` | PR / checks / review phase. |
| `Done` | Accepted closure with evidence appropriate to the issue kind. Implementation requires merged/accepted review evidence; planning, research, and decisions require their promised answer/artifact plus a resolution comment. No `session:*` label. |
| `Canceled` | Dead idea (Linear-native). |

Lane invariants:
- `In Progress` → exactly one `session:*` label.
- `Done` / `Canceled` / `Inbox` → no `session:*` label.
- `Blocked` → must have a Linear dependency relation or an explicit blocker comment.
- `Ready for agent` → must have Goal, Context, Done-when, Constraints, an `executor:*` class, and no hidden blocker. The readiness bar is the whole point of this lane: preparing an issue for it *is* a smart model writing a plan a less-smart model can execute cold. The Done-when must be goal-grade (see Issue Body Shape) — adoptable verbatim as the executor's `/goal` — and the `executor:*` class names the smallest model that plan is written for. If only a frontier model could run it, it isn't ready; sharpen the plan, don't reach for a bigger executor.
- `Ready for Burooj` → must have a current `For Burooj` brief (top-level comment thread, see Comment Model) naming the decision, the minimum facts, options with a recommendation, and a receipt-trail pointer. This is the same readiness bar as `Ready for agent`, aimed at Burooj instead of a worker: preparing the issue for this lane *is* writing the brief.

---

## Label Taxonomy

Labels encode metadata, never workflow position.

| Prefix | Purpose | Notes |
|---|---|---|
| `type:*` | Work kind | `bug`, `feature`, `improvement`, `cleanup`, `research`, `chore`, `seed`, `grilling`, `context`, `one-off`, `polish` |
| `executor:*` | Smallest model class the brief is written for | `frontier` (Sol/opus/fable judgment or hard execution), `standard` (Terra/gpt-5.5/sonnet/glm/minimax implementation), `small` (Luna/haiku/flash bulk work) |
| `site:*` | Minimum execution site the work requires | `cloud`, `bjslab`, `macbook`, `multi` — see below |
| `session:<provider>:<id>` | Active session binding | Live issues only; remove on `Done`/`Canceled` |
| `<skill-namespace>:*` | Opaque metadata owned by an installed workflow | Cockpit transports but does not interpret it; for example `wayfinder:map` and `wayfinder:{research,prototype,grilling,task}` |

`site:*` encodes *where the work can physically run*, as a capability ladder — label the **minimum** site required, not every site that would work. One `site:*` label per issue; absent means site-untriaged. Anything `site:cloud` is by definition phone-driveable, so there is no separate `site:phone` label.

Labeling criteria — walk the ladder top-down and stop at the first "yes":

1. **`site:multi`** — does the work *itself* coordinate across devices (e.g. a sync protocol tested between bjslab and the MacBook, a launchd job on one talking to a service on the other)? Rare; needing "the repo plus a server" is not multi — that's wherever both can be reached from.
2. **`site:macbook`** — does it need the head or the Mac's body: GUI apps, screenshots/computer-use, HITL alongside Burooj, physical hardware (mic, display, USB), macOS keychain secrets, launchd, or accounts that only live on the Mac?
3. **`site:bjslab`** — does it need Burooj's infra without a head: services or data hosted on bjslab, the home network, long-running daemons, or heavy/local compute that shouldn't ride the laptop?
4. **`site:cloud`** — none of the above: repo + tokens is enough. Code changes, research, writing, and anything a fresh sandbox clone can do land here. Native agent clouds (Claude Code web, Codex cloud) are valid single-provider targets. A provider-neutral sandbox such as Fly.io Sprites is the cloud target when the work needs multiple provider CLIs, durable Linux state, or isolation from bjslab's live services. The label still records the requirement, not the chosen vendor; cockpit chooses the concrete target at dispatch time.

Site labels are **claims about requirements, not history**. The board was built on the MacBook, so "it has always been done on the Mac" is not evidence for `site:macbook` — most repo work is movable. When in doubt between two rungs, take the more portable one (lower rung) and let execution prove otherwise.

`formation:*`, `mode:*`, `agent:*`, and `workflow:*` labels are **removed** (mode/agent encoded dispatch-era routing that lanes now carry; `workflow:issue-pr` was an opaque, unused training rail) — do not read, write, or reference them. Use `type:*` instead of Linear's default `Feature`/`Improvement`/`Bug` labels.

Here `workflow:*` means that retired literal prefix, not every workflow-owned namespace. A promoted skill may own a narrow namespace such as `wayfinder:*`; treat it as opaque metadata and do not turn it into Cockpit lane logic.

## Generic tracker operations

Cockpit exposes the Linear issue graph without encoding any upstream workflow: full JSON reads (including comments, parent/children, assignee, and both relation directions), root/child creation, title/body/parent edits, assignment, typed relation add/remove, labels, comments, and state moves. `SOURCE blocks TARGET` is the native blocker direction.

### Settled history and archiving

Use `cockpit linear board --settled` when the full record of completed and abandoned work matters; it lists `Done` and `Canceled` issues together and automatically includes archived issues. The narrower `cockpit linear board --state Done` and `cockpit linear board --state Canceled` views also include archives. The unfiltered `cockpit linear board` remains the current, unarchived board.

Archive only settled work through the Cockpit app actor:

```bash
cockpit linear archive BJS-123
cockpit linear unarchive BJS-123
cockpit linear archive-settled       # preview Done + Canceled count
cockpit linear archive-settled --yes # perform the reversible bulk archive
```

Upstream skills compose these primitives. A frontier, claim, map, ticket, or resolution algorithm belongs to the workflow skill, never to Linear or `cockpit.py`. See [the Cockpit tracker reference](../cockpit/references/matt-linear-tracker.md) for the project-local contract written by `setup-matt-pocock-skills`.

---

## Comment Model

**Cockpit Thread** (one per issue): a single top-level comment. All receipts, binding events, and audit trail live as replies under it. `bind`, `release`, `move`, and `comment` commands create or reuse this thread automatically.

**Questions thread** (one per issue): a top-level comment titled `Questions`. Each question is a reply under it. Burooj replies per-question. Do not put questions in the issue body.

**For Burooj thread** (one per issue): a top-level comment titled `For Burooj`. Posted when an issue moves to `Ready for Burooj` (or to `In Review` with Burooj as reviewer). Shape: the exact decision/question being asked, the minimum facts needed to decide, options with a recommendation, and a one-line pointer to the receipt trail (Cockpit Thread). Burooj reads only this comment and replies there — it is the entry point, not a duplicate of the Cockpit Thread. Mirrors the `Ready for agent` readiness bar: preparing an issue for `Ready for Burooj` *is* writing this brief.

**Grilling thread** (one per issue): a top-level comment titled `Grilling`. Interactive shaping dialogue with Burooj — multi-turn, can span sessions. The thread is the working-out, not the record: when grilling converges, conclusions graduate into the issue body and the thread resolves.

**Research routing rule:** research/brainstorm output routes to whoever acts next, never sits mid-air. If it ends in a Burooj decision (e.g. "pick tldraw vs excalidraw"), the result *is* the For Burooj brief — options, pros/cons, recommendation — posted to that thread. If it feeds an agent's next step, distill it into the body's Context section. Long-form artifacts get a linked Linear document; the brief/Context holds only the pointer and the settled takeaway. The body records only what is settled — in-progress findings never land there; when a decision lands, Context gets one line recording it.

Use cockpit commands for all writes so authorship stays on the Cockpit app actor (not Burooj's personal account):

```bash
./cockpit.py bind BJS-123 codex <session-id>
./cockpit.py release BJS-123
./cockpit.py comment BJS-123 "Receipt or update."
./cockpit.py comment BJS-123 --reply-to <comment-id> "Reply body."
./cockpit.py comment BJS-123 --brief "Decision brief text (goes to the For Burooj thread)."
./cockpit.py comment-resolve <comment-id>
./cockpit.py comment-unresolve <comment-id>
./cockpit.py move BJS-123 "In Review"
```

Resolution semantics: resolving a thread asserts the issue body no longer needs it — content graduated into the body, or the thread became moot. Unresolved threads are live context: `prepare` builds launch briefs from the body plus unresolved comments, so a cold worker sees exactly which threads still matter. The Cockpit Thread is auto-resolved by cockpit and is therefore never load-bearing for a cold start; Questions, For Burooj, and Grilling resolve only when a reply says what closed them — for Grilling, that means its conclusions have graduated into the body. Do not use raw Linear API/CLI writes for cockpit comments.

---

## Write Path

The app-actor GraphQL API (`https://api.linear.app/graphql`) is the **only** write path. All status moves, label changes, and comment writes go through cockpit commands, which author activity as the Cockpit app actor — not as Burooj.

Auth (in priority order):
1. `COCKPIT_LINEAR_APP_ACCESS_TOKEN` — OAuth access token with `actor=app`.
2. `COCKPIT_LINEAR_APP_CLIENT_ID` + `COCKPIT_LINEAR_APP_CLIENT_SECRET` — client-credentials app token.
3. Mac-local: `.linear.toml` with `app_actor.keychain_service` pointing to the client secret in macOS Keychain.
4. Emergency only: `COCKPIT_ALLOW_PERSONAL_LINEAR_WRITES=1`.

Run `./cockpit.py linear-doctor` to verify. It should report `write actor: app OK`.

Before any board touch, verify the action satisfies the lane invariants above and leaves a durable receipt in the Cockpit Thread when state changes.
