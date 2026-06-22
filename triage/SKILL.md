---
name: triage
description: Triage issues, PRs, work items, and inbox requests into clear workflow outcomes and agent-ready briefs. Use when inspecting issue comments or pull requests, deciding Needs Burooj vs Blocked vs Ready for agent, drafting briefs, clarifying inbox items, or recording out-of-scope and prior-decision notes.
---

# Triage

Triage turns raw issues, PRs, comments, and half-shaped requests into a durable next state: ask Burooj, block on something external, park or reject it, or prepare an agent-ready brief.

## Invocation Boundary

Use this skill deliberately when the user asks to triage, clarify, inbox-sort, brief, prepare, reject, or move a work item toward an actor. Do not silently impose this workflow on every tracker interaction; one-off conversations and exploratory sessions are allowed.

## Reference Files

- Read [references/agent-brief.md](references/agent-brief.md) before drafting or approving an issue, PR, or work item for `Ready for agent`.
- Read [references/out-of-scope.md](references/out-of-scope.md) before rejecting an enhancement, closing a repeated request, or checking whether a similar idea was already ruled out.

## Triage Outcomes

Use statuses for workflow position. Use labels for metadata such as `type:*`, `mode:*`, `agent:*`, `workflow:*`, domain, repo, or source.

- `Needs triage`: intake is not yet classified, the next actor is unknown, or the issue needs basic shaping before anyone should work it.
- `Needs Burooj`: Burooj is the next actor because the issue needs judgment, taste, priority, approval, private context, account access, physical action, or a non-searchable answer.
- `Blocked`: an external dependency, issue dependency, unavailable service, missing artifact, or access problem blocks progress. Name the blocker in the issue.
- `Ready for agent`: a fresh agent can proceed from the issue content plus allowed inspection/search. Missing information is searchable or discoverable and has a stop condition.
- `In Progress`: a specific worker/session is actively carrying it.
- `Parked`: valid idea, intentionally inactive.
- `Canceled`: not doing it, duplicate, obsolete, or out of scope.
- `Done`: completed with enough receipt for future readers.

Do not preserve `needs-info` as a fuzzy bucket. Map it to the actor who can resolve it:

- Choose `Needs Burooj` when the missing information requires Burooj's preference, decision, approval, private files, account access, or embodied context.
- Choose `Blocked` when the missing information depends on someone/something outside Burooj and the agent cannot safely obtain it.
- Choose `Ready for agent` when the missing information can be found by repository inspection, tracker search, docs, web research, or safe local commands, and the work item states where to look and when to stop.

## Triage Workflow

1. Identify the triage surface: one issue or PR, a project queue, `Needs triage`, new comments since last pass, or Burooj's pasted inbox.
2. Gather context: issue body, comments, status, labels, project, dependencies, related issues, relevant docs/repos, and any prior out-of-scope notes.
3. Decide the type: bug, enhancement, research, cleanup, review, seed, decision, chore, or support. Prefer the workspace's existing label language when available.
4. Check whether the request already exists, is already implemented, is a duplicate, or was previously rejected.
5. Recommend the next state before mutating the tracker unless the user explicitly asked for an autonomous triage pass.
6. Apply the status/label/comment changes only after approval or inside the approved autonomous scope.
7. Leave a durable trail: what was established, what is still unknown, who is next, and what would make the issue done.

## Comment Shapes

### Triage Notes

```md
## Triage Notes

**Established**
- ...

**Still Needed**
- [ ] ...

**Recommendation**
- Status:
- Labels:
- Next:
```

### Needs Burooj

```md
## Needs Burooj

**Established**
- ...

**Questions**
- [ ] ...

**Why this needs you**
- ...
```

Ask specific questions that can be answered directly. Avoid turning the issue into an interview unless the shape of the work genuinely needs it.

### Ready For Agent

Use [references/agent-brief.md](references/agent-brief.md). A `Ready for agent` issue, PR, or work item should have either an Agent Brief in the body or a latest authoritative comment saying the brief is current.

## Out Of Scope

Use [references/out-of-scope.md](references/out-of-scope.md). Prefer the project's canonical tracker doc, project doc, or repo decision file for out-of-scope and prior-decision records.
