# Matt Pocock workflows on Cockpit's Linear tracker

Use this reference when `setup-matt-pocock-skills` configures a Burooj project for Linear. Copy the operational parts into that project's `docs/agents/issue-tracker.md`; the upstream skills read the project-local file, not this Cockpit reference.

## Tracker

Issues live in the BJS Linear workspace. Reads may use the connected Linear read tools. All writes use `cockpit.py` so activity is authored by the Cockpit app actor.

The tracker adapter is generic. Upstream skills decide what to create, which issue is on a frontier, when to claim it, and what counts as resolved. Cockpit only transports issue fields and relationships.

## Generic operations

```bash
# Full issue body, comments, parent/children, assignee, and both relation directions
./cockpit.py issue BJS-123 --json

# Create a root issue or native child
./cockpit.py create --title "..." --description-file /path/to/body.md --label <label>
./cockpit.py create --title "..." --parent BJS-123 --label <label>

# Update title/body/parent. The timestamp catches an already-stale shared map read.
./cockpit.py update BJS-123 --description-file /path/to/body.md --expected-updated-at <updatedAt>

# Assign/unassign. Assignment is a tracker primitive; a workflow may interpret it as a claim.
./cockpit.py assign BJS-123 <user-id-or-exact-name-or-email>
./cockpit.py assign BJS-123 --clear

# Native typed relation: SOURCE blocks TARGET. The add command prints the relation id.
./cockpit.py relation-add BJS-123 blocks BJS-456
./cockpit.py relation-remove <relation-id>

# Labels, comments, and closure
./cockpit.py label BJS-123 --add <label> --remove <label>
./cockpit.py comment BJS-123 --top-level "<resolution or workflow comment>"
./cockpit.py move BJS-123 Done
./cockpit.py move BJS-123 Canceled
```

`related`, `duplicate`, and `similar` are also valid relation types. Prefer Linear's native parent/child and blocker graph over body-text conventions.

## Wayfinding operations

The map is a labelled root issue; decision tickets are its native children. Read the map with `issue --json`; children are returned in Linear's native sub-issue order. Determine the frontier from open children, their inbound `blocks` relations, and assignee state; Cockpit does not provide a `frontier` command. Claiming is assignment. Resolution is an answer comment, a move to `Done`, and a map-body update. Create all child issues before wiring blocker edges.

`--expected-updated-at` is a best-effort stale-read check, not an atomic compare-and-swap: Linear's issue update API has no expected-version field. After updating a shared map, reread it immediately. If another writer landed concurrently, merge both decisions against the fresh body and retry instead of treating the last write as authoritative.

Use `wayfinder:map` on maps and `wayfinder:{research,prototype,grilling,task}` on decision tickets. These are opaque workflow-owned metadata to Cockpit.

## Triage role translation

Upstream role names map onto Cockpit without creating duplicate workflow labels:

| Upstream role | Cockpit representation |
|---|---|
| `bug` | `type:bug` label |
| `enhancement` | `type:feature` or `type:improvement` label |
| `needs-triage` | `Inbox` lane |
| `needs-info` | `Needs-info` lane |
| `ready-for-agent` | `Ready for agent` lane, only after Cockpit's goal-grade Done-when, executor, site, and blocker checks pass |
| `ready-for-human` | `Ready for Burooj` when Burooj is the actual next actor and a current decision brief exists; otherwise keep the issue in the lane matching its real next actor |
| `wontfix` | `Canceled` lane, with the upstream explanatory artifact/comment |

`to-spec` creates a planning/spec issue; it does not make implementation tickets executable by itself. Apply Cockpit's `Ready for agent` gate to the child tickets produced by `to-tickets`, not mechanically to an umbrella spec whose next step is decomposition.

## Closure evidence

Close an issue only when its own promised result exists. Implementation issues require accepted review/merge evidence. Research, planning, and decision issues require the answer or artifact they promised plus a resolution comment; they do not require a fictional PR.
