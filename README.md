# skills

My personal agent-skills repo. This is the live config that drives how Claude, Codex, Cursor, and opencode behave when I work — the global system instructions, model profiles, and a growing collection of slash-command skills.

It's a work in progress. I'll keep tweaking wording as I learn what actually works.

---

## What's in here

**`souls/prime.md`** — my global agent "soul and discipline" file (the soul). Symlinked as `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` so every session inherits it. Agents are steered away from editing `souls/` directly — it changes only when I deliberately change it.

**`agents/`** — the `agents` skill for choosing which model/provider to use, plus `profiles.json` with my current model roster across Claude, Codex, opencode, and Cursor.

**`cockpit/`** — the cockpit skill bundle: Linear-first project orchestration, dispatch logic, session discipline, and the `cockpit.py` script.

**`triage/`** — triage skill for sorting issues, PRs, and inbox items into clear next states (Needs Burooj, Ready for agent, Blocked, Parked, etc.).

**`grill-me/`** — rapid-fire interviewing skill. Grills me on a plan until we reach shared understanding.

**`grill-with-docs/`** — same as grill-me but reads existing `CONTEXT.md` and ADRs first, sharpens terminology, and updates docs inline as decisions crystallise.

**`grill-me-stateful/`** — stateful variant that tracks progress across turns.

**`improve-codebase-architecture/`** — finds deepening opportunities in a codebase: shallow-to-deep refactors, better seams, higher interface leverage.

**`design-lab/`** — full design-system composition skill. Takes raw material (repo, screenshots, words, moodboards) and builds out a complete token/primitive/component taxonomy plus a live style guide.

**`linear/`** — thin skill for Linear operations outside cockpit.

**`zoom-out/`** — asks me to zoom out when I'm about to grind before naming the right problem.

**`writing-great-skills/`** — Matt Pocock's reference skill for writing and editing predictable, low-sediment skills.

---

## Credits / inspiration

**Matt Pocock** ([mattpocock/skills](https://github.com/mattpocock/skills))
The `triage`, `grill-me`, `grill-with-docs`, `improve-codebase-architecture`, and `writing-great-skills` skills are adapted from Matt's engineering skills set. The triage skill and its `agent-brief` + `out-of-scope` reference files follow his structure closely. Really useful starting point — I've been evolving them for my own workflow but the bones are his.

**Anthropic** — the `anthropic-skills` bundle (not in this repo; installed separately as a Claude skill plugin) ships several useful primitives.

**Firecrawl** — the `firecrawl-*` skills (also installed separately as a plugin) come from Firecrawl's official Claude skill set.

**Everything else** — written from scratch or origin unclear. If you borrowed from something I should credit, let me know.

---

*Living draft. Burooj will keep tweaking.*
