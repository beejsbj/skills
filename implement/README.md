# Implement

Worker discipline for carrying a Linear issue from `Ready for agent` to a receipt in `In Review`: read the issue, verify the workspace, build with tdd, review, push the artifact, leave a receipt.

Adapted from Matt Pocock's engineering implement workflow in [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/implement), expanded to fit cockpit's artifact-gated lifecycle and Linear as the source of truth.

The Codex/Claude skill entrypoint is [SKILL.md](SKILL.md).
