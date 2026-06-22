# Agent Briefs

Use an Agent Brief when an issue, PR, or work item is moving to `Ready for agent`, when Burooj asks for an AFK-agent-ready packet, or when the next worker should be able to start without reading the whole surrounding conversation.

In the tracker, prefer placing the current brief in the work item body when possible. If preserving the original body matters, post the brief as the latest authoritative comment and say that it supersedes earlier shaping notes.

## Principles

- Durable over brittle: describe behavior, stable surfaces, user-visible outcomes, and important interfaces. Avoid fragile line numbers or exact implementation steps unless they are required.
- Behavioral over procedural: specify what should become true, not exactly how the worker must code it.
- Searchable context is allowed: an agent can inspect repos, docs, tracker state, local files, or the web when the work item names the allowed sources and a stop condition.
- Complete acceptance criteria: use independently verifiable checks.
- Explicit boundaries: name what should not change and where to stop.
- Receipt required: the worker should report what changed, what was verified, and what remains.

## Template

```md
## Agent Brief

**Category**
- Bug | Enhancement | Research | Cleanup | Review | Decision | Chore

**Summary**
- ...

**Current Behavior / Context**
- ...

**Desired Outcome**
- ...

**Key Interfaces**
- Tracker:
- Repo/files:
- Commands/docs:
- Related issues:

**Acceptance Criteria**
- [ ] ...
- [ ] ...
- [ ] Verification is reported in the final comment or handoff.

**Out of Scope**
- ...

**Stop Conditions**
- Ask Burooj if ...
- Mark Blocked if ...
```

## Readiness Check

Before marking `Ready for agent`, confirm:

- A fresh worker can tell what to do from the work item alone.
- Any missing facts are searchable/discoverable without Burooj, or the issue has been moved to `Needs Burooj`.
- Acceptance criteria describe observable outcomes.
- The work item names the relevant repo, project, doc, service, or tracker area.
- The scope boundaries are clear enough to avoid opportunistic rewrites.
