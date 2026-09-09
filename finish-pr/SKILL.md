---
name: finish-pr
description: Carry a pull request from the branch's current state through creation, active review, new comments and checks, authorized merge, and exact cleanup. Use when the user asks to create, finish, land, merge, or babysit a PR; exclude requests for read-only code review.
---

# Finish a PR

Own the pull request until the user's requested finish line is true. Start from current state and skip completed stages.

## Set the finish line

Read the current request before mutating anything:

- **Create or open** ends with a pushed branch and an accurate open PR.
- **Babysit** ends at the review-loop stability criterion below.
- **Finish, land, merge,** or an unqualified explicit `$finish-pr` runs the full lifecycle through ordinary merge and exact post-merge cleanup.

A nearer bound from the user wins. Force operations, bypassing protections, and cleanup beyond the exact merged branch or owned worktree require separate authorization.

## Reconcile current state

Read the repository instructions and inspect the branch, base, upstream, worktree, remotes, existing PRs, and host authentication. Separate owned changes from unrelated dirty-tree work. Reuse an existing PR for the branch instead of opening a duplicate.

This stage is complete when the current head, intended base, existing PR state, owned changes, and requested finish line are all known from live evidence.

## Prepare and open

Bring only the owned change to a reviewable state. Verify it in proportion to its risk, create coherent commits, push the branch, then create or update the PR using the repository's title, body, evidence, and hosting conventions. Do not manufacture an empty PR or silently fold unrelated changes into it.

This stage is complete when the PR URL, base, and displayed head SHA match the pushed branch and its checks have been triggered.

## Run the review loop

For a full finish, invoke `$consult` against the stable diff before declaring the PR ready. Treat its output as candidate findings: verify each one against the source and tests.

Establish a review horizon at the current head SHA, then repeatedly refresh all review surfaces the host exposes: required checks, review decisions, inline threads, general comments, and bot findings. Consider only events that still apply to the latest code.

- Fix a real finding, verify the fix, commit it coherently, push it, and reply or resolve where appropriate.
- Answer a false, stale, or already-fixed finding with the concrete reason when the workflow permits responses.
- Surface a finding that requires product judgment or authority instead of guessing.
- After every push, move the horizon to the new head and restart check and review observation for that SHA.

Use the environment's recurring wait or monitoring mechanism while checks or reviewers are active. The loop is complete only when every known automated review job and required check for the latest head has reached a terminal state, the required checks are green, every actionable item observed in scope has a disposition, and one final refresh after those terminal results shows no newer actionable event. When the user sets a watch boundary for human review, that boundary is part of this criterion.

## Land and clean up

When the finish line includes landing, verify that the reviewed head is still current and mergeable, then use the repository's normal merge method. After the host records the PR as merged, remove only the exact merged feature branch and owned worktree that are safe to remove. Preserve unmatched branches, dirty worktrees, and recovery refs.

The full workflow is complete when the host reports the PR merged, the intended mainline contains the result, exact authorized cleanup is verified, and no required monitoring process remains running.

Stop with a precise blocker when access fails, a check or reviewer reports a terminal condition that needs an external owner, an agreed monitoring limit is reached, the branch cannot be reconciled safely, or a review finding requires a user decision. An unchanged pending state remains active work. Report the PR URL, latest head, checks, review disposition, merge state, cleanup performed, and any residual risk.
