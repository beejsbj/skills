# Two-Axis Review

Review the diff since a fixed point along two independent axes — Standards (the repo's documented coding standards plus a Fowler smell baseline) and Spec (does the diff implement what the originating Linear issue asked) — run as parallel subagents and reported side by side, never reranked against each other.

Renamed from the upstream `code-review`: Claude Code ships a built-in `/code-review` command, and keeping the name would collide with it.

Adapted from Matt Pocock's code-review skill in [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/code-review), retargeted at Burooj's board: the spec axis reads the bound Linear issue and the review leaves a cockpit receipt on it.

The Codex/Claude skill entrypoint is [SKILL.md](SKILL.md).
