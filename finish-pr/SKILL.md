---
name: finish-pr
description: Carry an existing pull request through independent review, active babysitting of new comments and checks, authorized merge, and exact cleanup. Use when the user asks to finish, land, merge, or babysit a PR; exclude PR creation and read-only code review.
---

# Finish a PR

Own an existing pull request until the user's requested finish line is true. Start from its current state and skip completed stages.

## Set the finish line

Resolve the exact existing pull request and feature branch, then read the active request and session authorization before mutating anything:

- **Babysit** ends at the review-loop stability criterion below.
- **Finish, land, merge,** or an unqualified explicit `$finish-pr` runs that PR's full lifecycle through ordinary merge and safe removal of its feature branch and owned worktree.

Earlier authorization in the active session remains valid until the user supersedes it; a nearer bound wins. Force operations, bypassing protections, and cleanup beyond the resolved PR's exact merged branch or owned worktree require separate authorization.

## Reconcile current state

Read the repository instructions and inspect the PR, branch, base, upstream, worktree, remotes, and host authentication. Separate owned changes from unrelated dirty-tree work. If no matching PR exists, stop with that prerequisite instead of creating one.

This stage is complete when the PR URL, current head, intended base, PR state, owned changes, and requested finish line are all known from live evidence. Before review, ensure the intended changes are committed and pushed and the PR's displayed head matches the branch.

## Run the review loop

For a full finish, invoke `$consult` against the stable diff as an independent PR reviewer. Give it the resolved PR as the authorized delivery surface and require its verified findings and verdict to be submitted there as a review. Record the consulted head SHA and review URL. The consultation is complete only when its review is visible on the PR. Consult the new head again only when later changes materially alter the reviewed logic or behavior, or invalidate an earlier finding.

Establish a review horizon at the current head SHA, then repeatedly refresh all review surfaces the host exposes: required checks, review decisions, inline threads, general comments, and bot findings. Consider only events that still apply to the latest code.

- Fix a real finding, verify the fix, commit it coherently, push it, and reply or resolve where appropriate.
- Answer a false, stale, or already-fixed finding with the concrete reason when the workflow permits responses.
- Surface a finding that requires product judgment or authority instead of guessing.
- After every push, move the horizon to the new head and restart check and review observation for that SHA.

Use the environment's recurring wait or monitoring mechanism while checks or reviewers are active. The latest reviewed head is ready to land only when the consultation review covers it under the reconsultation rule, every known automated review job and required check has reached a terminal state, all required checks and approvals pass, no blocking review remains unresolved, every other actionable item observed in scope has a disposition, and one final refresh after those terminal results shows no newer actionable event. When the user sets a watch boundary for human review, that boundary is part of this criterion.

## Land and clean up

When the finish line includes landing, verify that the reviewed head is still current, satisfies the ready-to-land criterion, and meets the repository's merge policy, then use its normal merge method. After the host records the PR as merged, remove only the exact merged feature branch and owned worktree that are safe to remove. Preserve unmatched branches, dirty worktrees, and recovery refs.

## Complete or block

The full workflow is complete when the host reports the PR merged, the intended mainline contains the result, exact authorized cleanup is verified, and no required monitoring process remains running.

Stop with a precise blocker when access fails, a check or reviewer reports a terminal condition that needs an external owner, an agreed monitoring limit is reached, the branch cannot be reconciled safely, or a review finding requires a user decision. An unchanged pending state remains active work. Report the PR URL, latest head, checks, review disposition, merge state, cleanup performed, and any residual risk.
