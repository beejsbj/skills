# Skills Repo Instructions

This repo is the source of truth for personal agent skills and shared agent-home setup. Global Claude instructions are handled separately by `system-instructions.md`.

## Skill Symlinks

This repo keeps personal skills in one place. Codex and Claude make those same repo-owned skills available by symlinking from their skill directories:

- `/Users/burooj/.codex/skills/<skill-name>` -> `/Users/burooj/Projects/skills/<skill-name>`
- `/Users/burooj/.claude/skills/<skill-name>` -> `/Users/burooj/Projects/skills/<skill-name>`

When adding, renaming, or removing a skill, update the repo-owned folder first, then refresh both agent-home symlinks. Do not edit the symlink target as if it were a generated copy; the target in this repo is the source of truth.

## Global Instructions

`system-instructions.md` is not the README for this repo. It is the repo-owned global instruction target used by:

- `/Users/burooj/.codex/AGENTS.md`
- `/Users/burooj/.claude/CLAUDE.md`

Use that file when changing global agent behavior across Codex and Claude from one place.

## Repository Work

Know the branch. Leave handholds. Respect the dirty tree.

Work in small, coherent slices. Prefer atomic commits at natural checkpoints: recoverable savepoints with a clear story of what changed, why it changed, and how far it was verified.

Before committing, explain what you have done and wait for approval unless an autonomous commit flow was explicitly requested.

Keep PRs singular, focused, and reviewable.
