# Skills Repo Instructions

This repo is the source of truth for personal agent skills and shared agent-home setup. Global Codex instructions live in `souls/prime.md`.

## Skill Symlinks

This repo keeps personal skills in one place. Codex and Claude make those same repo-owned skills available by symlinking from their skill directories:

- `/Users/burooj/.codex/skills/<skill-name>` -> `/Users/burooj/Projects/skills/<skill-name>`
- `/Users/burooj/.claude/skills/<skill-name>` -> `/Users/burooj/Projects/skills/<skill-name>`

When adding, renaming, or removing a skill, update the repo-owned folder first, then refresh both agent-home symlinks. Do not edit the symlink target as if it were a generated copy; the target in this repo is the source of truth.

## Global Instructions & souls/

`souls/prime.md` is the repo-owned global instruction target (Burooj's "soul"), used by:

- `/Users/burooj/.codex/AGENTS.md` -> `souls/prime.md`
- `/Users/burooj/.claude/CLAUDE.md` -> `souls/prime.md`

It sets global agent behavior across Codex and Claude from one place.

**Treat `souls/` as protected. Do not edit files in `souls/` directly or as a side effect** — agents drift into rewriting the soul too readily. Change it only when Burooj explicitly asks to adjust global behavior, in a small deliberate edit, never bundled into unrelated work.

## Attribution

When a skill is brought in or adapted from an external source — another repo, a blog post, a person's workflow — cite the original in the skill file itself (a comment, a README, or a credits line) and/or in the repo's credits list. Attribution makes borrowing guilt-free: it's explicit, it's transparent, and it doesn't pretend the work is original. If the source is unclear, say so rather than omitting it or inventing one.
