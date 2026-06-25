#!/usr/bin/env python3
"""
One-off Linear board migration for the cockpit redesign (2026-06-24).

Maps the live BJS board onto the redesign's 9-lane model. Idempotent-ish:
renames are safe to re-run; issue moves and state creation guard on current state.

Does NOT touch Parked issues — those need Burooj's per-issue alive/dead call
(see docs/specs/2026-06-24-cockpit-redesign.md §9). Run separately after that call.

Writes are authored by the Cockpit app actor (reuses cockpit.py's GraphQL plumbing).
"""
import sys

sys.path.insert(0, "/Users/burooj/Projects/skills/cockpit/scripts")
import cockpit  # noqa: E402

gql = cockpit.run_linear_graphql

RENAME = """mutation($id:String!,$name:String!){
  workflowStateUpdate(id:$id, input:{name:$name}){ success workflowState{ id name } }
}"""
CREATE = """mutation($input:WorkflowStateCreateInput!){
  workflowStateCreate(input:$input){ success workflowState{ id name type } }
}"""
ARCHIVE = """mutation($id:String!){ workflowStateArchive(id:$id){ success } }"""
ISSUE_UPDATE = """mutation($id:String!,$input:IssueUpdateInput!){
  issueUpdate(id:$id, input:$input){ success }
}"""
LABEL_CREATE = """mutation($input:IssueLabelCreateInput!){
  issueLabelCreate(input:$input){ success issueLabel{ id name } }
}"""


def step(label, fn):
    try:
        result = fn()
        print(f"  OK   {label}: {result}")
    except Exception as exc:  # noqa: BLE001 - report and continue
        print(f"  FAIL {label}: {exc}")


def main():
    meta = cockpit.linear_team_metadata()
    team_id = meta["id"]
    states = {s["name"]: s for s in meta["states"]["nodes"]}
    state_id = {n: s["id"] for n, s in states.items()}

    inbox_id = state_id.get("Needs triage")  # becomes "Inbox"
    backlog_id = state_id.get("Backlog")
    todo_id = state_id.get("Todo")

    print("== A/B. Rename states ==")
    if "Needs Burooj" in state_id:
        step("Needs Burooj -> Ready for Burooj",
             lambda: gql(RENAME, {"id": state_id["Needs Burooj"], "name": "Ready for Burooj"}))
    if inbox_id:
        step("Needs triage -> Inbox",
             lambda: gql(RENAME, {"id": inbox_id, "name": "Inbox"}))

    print("== E. Create shaping lanes ==")
    for name in ("Needs-info", "Grilling"):
        if name in state_id:
            print(f"  SKIP {name}: already exists")
            continue
        step(f"create {name}",
             lambda name=name: gql(CREATE, {"input": {
                 "teamId": team_id, "name": name, "type": "unstarted", "color": "#9b8afb"}}))

    print("== F. Create type:grilling label ==")
    if cockpit.issue_label_id("type:grilling"):
        print("  SKIP type:grilling: already exists")
    else:
        step("create type:grilling",
             lambda: gql(LABEL_CREATE, {"input": {
                 "teamId": team_id, "name": "type:grilling", "color": "#9b8afb",
                 "description": "Issue needs a grilling session to sharpen intent/approach."}}))

    print("== C. Move Backlog + Todo issues -> Inbox ==")
    if not inbox_id:
        print("  ABORT moves: Inbox (ex Needs triage) state id missing")
    else:
        issues = cockpit.load_linear_issues_graphql()
        moving = [i for i in issues
                  if ((i.get("state") or {}).get("name")) in ("Backlog", "Todo")]
        print(f"  moving {len(moving)} issues into Inbox")
        for i in moving:
            ident = cockpit.issue_identifier(i)
            step(f"move {ident}",
                 lambda i=i: gql(ISSUE_UPDATE, {"id": i["id"], "input": {"stateId": inbox_id}}))

    print("== D. Archive emptied Backlog + Todo states ==")
    for name, sid in (("Backlog", backlog_id), ("Todo", todo_id)):
        if sid:
            step(f"archive {name}", lambda sid=sid: gql(ARCHIVE, {"id": sid}))

    print("== G. Parked -> Inbox (Burooj's call 2026-06-24: all alive, re-triage in Inbox) ==")
    if not inbox_id:
        print("  ABORT: Inbox (ex Needs triage) state id missing")
    else:
        issues = cockpit.load_linear_issues_graphql()
        parked = [i for i in issues if ((i.get("state") or {}).get("name")) == "Parked"]
        print(f"  moving {len(parked)} Parked issues into Inbox")
        for i in parked:
            ident = cockpit.issue_identifier(i)
            step(f"move {ident}",
                 lambda i=i: gql(ISSUE_UPDATE, {"id": i["id"], "input": {"stateId": inbox_id}}))
        # Parked state can be archived once empty (admin-only).
        if "Parked" in state_id:
            step("archive Parked", lambda: gql(ARCHIVE, {"id": state_id["Parked"]}))

    print("\nDONE (issue moves). Structural changes (rename/create/archive states, "
          "create labels) require team-admin rights the Cockpit app actor lacks (403) "
          "— do those in the Linear UI.")


if __name__ == "__main__":
    main()
