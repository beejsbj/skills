---
name: implement
description: "Worker discipline for implementing a Linear issue end to end: read the issue, verify the workspace, build with tdd, review, push the artifact, leave a receipt."
disable-model-invocation: true
---

# Implement

The discipline a worker session follows to carry a Linear issue from `Ready for agent` to a receipt in `In Review`. Applies to any issue-bound implementation session, from any harness.

## 1. Read the issue

From `/Users/burooj/Projects/cockpit`:

```bash
./cockpit.py issue BJS-X
```

The issue body's `## Goal` / `## Context` / `## Done when` / `## Constraints` is the spec (see the `linear` skill for the shape). Unresolved comments count as spec too — read them before starting; they can narrow, override, or add to the body.

Done when you can state the goal, the constraints, and the done-when conditions without re-reading the issue.

## 2. Verify the workspace

Implementation happens on a branch in a worktree, never the repo's root checkout when parallel work on the same repo is possible — a root checkout collides with any other issue being worked at the same time. Confirm `pwd` is a worktree path, not `/Users/burooj/Projects/<repo>`, before writing code.

Done when the working directory is a worktree on the issue's branch.

## 3. Set the goal

Both Claude Code and Codex have a native completion-contract feature (`/goal`). The issue's `Done when` list is written to be used verbatim as that condition — set it as the session goal rather than re-deriving one.

Done when the session goal matches the issue's `Done when` list.

## 4. Build

Use the `tdd` skill at seams pre-agreed with the user. Typecheck and run the relevant tests regularly through the build, not only at the end; run the full suite once when the build is otherwise complete.

Done when the full suite passes and nothing pre-agreed as in-scope is left unimplemented.

## 5. Review

Run a two-axis review (Standards + Spec) before handing off — see the `two-axis-review` skill if present in this skills repo, or run the equivalent review manually: does the diff follow the repo's documented standards, and does it faithfully implement the issue's Goal/Done-when? Fix what the review finds or record why not.

Done when the review has run and its findings are resolved or explicitly deferred with reason.

## 6. Push the artifact

Push the branch and open the review artifact the issue names — normally a draft or ready PR. Local commits are not completion evidence; nothing after this step is true until the artifact exists remotely.

Done when the branch is pushed and the PR (or named artifact) URL exists.

## 7. Leave the receipt

```bash
./cockpit.py comment BJS-X "..."
```

Post under the issue's Cockpit Thread (cockpit reuses it automatically). Include: branch, commit, pushed yes/no, PR/review artifact URL, checks run, residual risks, and a recommended next state.

Recommend `In Review`. Never move the issue to `Done` yourself — `Done` requires acceptance or merge, which is Burooj's or a reviewer's call.

Done when the receipt is posted and the issue is still in a state you recommended, not one you set.
