---
name: brain-to-brawn
description: Hand planned work to a cheaper executor — verify the brief is executor-grade, launch a small model on it with the Done-when as its goal, review the diff against the brief, receipt. Use when shaped work doesn't need frontier judgment to execute, or the user says brain-to-brawn, dispatch this, or hand it to a cheap model.
---

# Brain to Brawn

Frontier models write and review the plan; cheap models execute it. **The plan is the product** (distilled from [shadcn/improve](https://github.com/shadcn/improve)).

## 1. Verify the brief is executor-grade

The issue body (or plan file) must stand alone: Goal / Context / goal-grade Done-when / Constraints with the stop rule, and an `executor:*` class — see the `to-issues` skill for the shape. If the named class couldn't execute it cold, thicken the brief or split the slice; never compensate with a bigger executor.

## 2. Launch the brawn

Pick the smallest sufficient model from the `acpx` skill's `profiles.json`, then launch:

- acpx (claude/codex/gemini adapters): `bunx --bun acpx --approve-all --cwd <project-root> -s bjs-<n> claude --model sonnet "<brief>"`
- native CLI when there's no adapter: `opencode run --format json --model opencode-go/glm-5.2 "<brief>"`

The prompt tells the worker to adopt the issue's Done-when as its goal and to follow the `implement` skill (stop rule included). For Linear-bound work, bind the resulting session: `./cockpit.py bind BJS-X session:<provider>:<id>` and move to `In Progress`.

Identify the worker's native session id by a content marker — grep the provider's session store for a phrase from your prompt, and confirm the match is in the session's own *user/prompt* record (session metadata or first user message), not merely quoted in its transcript: scouts and workers grep each other's stores, so transcripts quote transcripts. Never trust newest-file mtime; parallel sessions make it lie. acpx quirks live in the `acpx` skill (named sessions need `sessions ensure` first; `-s` goes after the agent subcommand).

## 3. Review as the brain

Stop-rule comments come back to you, not to Burooj — answer them or adjust the brief; escalate only what genuinely needs his call. When the brawn reports done, review the diff against the brief (`two-axis-review` for repo diffs); the brawn's "done" is a claim, the review is the evidence.

## 4. Receipt

On the issue: model class used, verdict on both review axes, artifact link, residual risk. Recommend the next lane; never self-move to `Done`.
