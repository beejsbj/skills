---
name: brain-to-brawn
description: Write a self-contained runbook the smallest sufficient model can execute unattended, then launch, review, and receipt it. Use when shaped work doesn't need frontier judgment to execute, or the user says brain-to-brawn, dispatch this, or hand it to a cheap model.
---

# Brain to Brawn

**The intelligence goes into the runbook, not into who runs it.** A frontier model writes a brief so complete and unambiguous that a standard or small-class model can execute it correctly with no back-and-forth — then a frontier model reviews the result. The cost saving comes from *not needing judgment at execution time*, because judgment was already spent writing the plan.

This is not "delegate to a subagent." A native subagent (Task tool) stays inside the current harness and model family — same brain, borrowed hands, for parallelizing or protecting context. Brain-to-brawn crosses *model class and provider on purpose*, to spend frontier tokens only where judgment is genuinely needed and route everything else to whatever is cheapest that can still do the job. If the work just needs another pair of hands in this session, use a subagent — this skill is for when the point is the cost/capability split itself.

## 1. Write or verify the runbook

The deliverable is the runbook, not the code — "the plan is the product" (distilled from [shadcn/improve](https://github.com/shadcn/improve)). It must stand alone: Goal / Context / goal-grade Done-when / Constraints with the stop rule, plus an `executor:*` class naming the smallest model that can run it cold (see the `to-issues` skill for the shape).

The test is concrete: could the named class execute this with *zero* clarifying questions? If not, the runbook is thin or the slice too big — thicken or split it. Never compensate by handing a thin brief to a bigger model; that defeats the whole point.

## 2. Launch the brawn

Pick the smallest sufficient model from the `acpx` skill's `profiles.json`, then launch:

- acpx (claude/codex/gemini adapters): `bunx --bun acpx --approve-all --cwd <project-root> -s bjs-<n> claude --model sonnet "<runbook>"`
- codex (proven recipe — write the runbook to a file first): `codex exec -C <project-root> -m gpt-5.5 -s workspace-write "$(cat runbook.md)" < /dev/null` — the `< /dev/null` matters; without it codex exec can hang silently at startup. Its stdout header prints the session id: bind that, no guessing.
- native CLI when there's no adapter: `opencode run --format json --model opencode-go/glm-5.2 "<runbook>"`

The prompt tells the worker to adopt the Done-when as its goal and to follow the `implement` skill (stop rule included). For Linear-bound work, bind the resulting session: `./cockpit.py bind BJS-X session:<provider>:<id>` and move to `In Progress`.

Identify the worker's native session id by a content marker — grep the provider's session store for a phrase from your prompt, and confirm the match is in the session's own *user/prompt* record (session metadata or first user message), not merely quoted in its transcript: scouts and workers grep each other's stores, so transcripts quote transcripts. Never trust newest-file mtime; parallel sessions make it lie. acpx quirks live in the `acpx` skill (named sessions need `sessions ensure` first; `-s` goes after the agent subcommand).

## 3. Review as the brain

Stop-rule comments come back to you, not to Burooj — answer them or thicken the runbook; escalate only what genuinely needs his call. A stop-rule report is a signal the runbook underspecified something, not just a blocker to clear — fix the gap so the next slice doesn't hit it.

When the brawn reports done, review the diff against the runbook (`two-axis-review` for repo diffs); the brawn's "done" is a claim, the review is the evidence.

## 4. Receipt

On the issue: model class used, verdict on both review axes, artifact link, residual risk. Recommend the next lane; never self-move to `Done`.
