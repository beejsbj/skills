# skills

My personal agent-skills repo. This is the live config that drives how Claude, Codex, Cursor, and opencode behave when I work — the global system instructions, model profiles, and a growing collection of slash-command skills.

It's a work in progress. I'll keep tweaking wording as I learn what actually works.

---

## Access points

This repository is the canonical source for Burooj-owned and deliberately adopted skills. Agent-specific skill directories are access points, not independent sources of truth.

- **Claude Code and Codex on macOS:** repo-owned skill folders are linked into `~/.claude/skills/` and `~/.codex/skills/` as described in `AGENTS.md`.
- **Hermes profiles:** clone this repository on the machine, then add the checkout as an external skill directory in that profile's `config.yaml`:

  ```yaml
  skills:
    external_dirs:
      - /absolute/path/to/skills
  ```

  Hermes then exposes the repo-owned skills through its skill index and `/skill-name` commands. Local Hermes skills still take precedence when a name collides.

Bundled skills maintained by an agent framework remain upstream-owned. Add a skill here when Burooj authored it, adapted it, or deliberately wants this repository to preserve the chosen version.

---

## What's in here

**`souls/prime/`** — my global agent "soul and discipline" file (`soul.md`), plus a README explaining the decisions behind its construction. `soul.md` is symlinked as `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` so every session inherits it. Agents are steered away from editing `souls/` directly — it changes only when I deliberately change it.

**`acpx/`** — adapted official skill for [openclaw/acpx](https://github.com/openclaw/acpx), the headless ACP client for reaching other models/providers, plus `profiles.json` — my model roster and taste (premium tokens for judgment, cheap classes for execution).

**`cockpit/`** — the cockpit skill bundle: Linear-first project orchestration, dispatch logic, session discipline, and the `cockpit.py` script.

**`triage/`** — triage skill for sorting issues, PRs, and inbox items into clear next states (Needs Burooj, Ready for agent, Blocked, Parked, etc.).

**`to-issues/`** — breaks a plan, spec, or grilling outcome into independently-grabbable tracer-bullet Linear issues with goal-grade Done-whens, each targeted at an executor class (the "smart model writes a plan a cheaper model runs cold" idea, adapted from shadcn/improve).

**`implement/`** — worker discipline for implementing a Linear issue end to end: goal adoption, tdd, review, artifact gate, receipt.

**`two-axis-review/`** — Standards + Spec review of a diff against its originating issue, run as parallel subagents (renamed from Matt's `code-review` to avoid Claude Code's built-in command).

**`tdd/`** — the red-green loop, testing at pre-agreed seams, vertical slices.

**`diagnosing-bugs/`** — deep diagnosis loop for hard bugs and performance regressions: reproduce → minimise → hypothesise → instrument → fix → regression-test.

**`prototype/`** — throwaway prototypes to answer a design question before committing to real code.

**`pear/`** — local-first/P2P guidance for Pear/Holepunch: when to use peer replication, multi-device sync, Hypercore-style append-only stores, and pear:// app distribution instead of defaulting to servers, blockchain, or vague decentralization.

**`grill-me/`** — rapid-fire interviewing skill. Grills me on a plan until we reach shared understanding.

**`grill-with-docs/`** — same as grill-me but reads existing `CONTEXT.md` and ADRs first, sharpens terminology, and updates docs inline as decisions crystallise.

**`grill-me-stateful/`** — stateful variant that tracks progress across turns.

**`improve-codebase-architecture/`** — finds deepening opportunities in a codebase: shallow-to-deep refactors, better seams, higher interface leverage.

**`design-lab/`** — full design-system composition skill. Takes raw material (repo, screenshots, words, moodboards) and builds out a complete token/primitive/component taxonomy plus a live style guide.

**`linear/`** — Burooj's Linear board discipline and write path: lanes, labels, issue bodies, comments, dependencies, receipts, and cockpit app-actor commands.

**`zoom-out/`** — asks me to zoom out when I'm about to grind before naming the right problem.

**`writing-great-skills/`** — Matt Pocock's reference skill for writing and editing predictable, low-sediment skills.

**`tldw/`** — imported from the live OpenClaw host for extracting and summarizing YouTube transcripts with `yt-dlp`.

**`gsap-skills/`** — imported GSAP AI skills bundle: core GSAP, timelines, ScrollTrigger, plugins, framework usage, examples, and plugin metadata.

**`in-progress/diglot-weave/`** — recovered packet for a future `diglot-weave` skill, including source transcripts, raw zip artifacts, recovered skill drafts, and prior-art notes.

---

## Credits / inspiration

**Matt Pocock** ([mattpocock/skills](https://github.com/mattpocock/skills))
The `triage`, `grill-me`, `grill-with-docs`, `improve-codebase-architecture`, `writing-great-skills`, `to-issues`, `two-axis-review` (his `code-review`), `implement`, `tdd`, `diagnosing-bugs`, and `prototype` skills are adapted from Matt's engineering skills set. The triage skill and its `agent-brief` + `out-of-scope` reference files follow his structure closely. Really useful starting point — I've been evolving them for my own workflow but the bones are his.

**shadcn** ([shadcn/improve](https://github.com/shadcn/improve))
The "smart model writes a self-contained plan a cheaper model executes cold; the plan is the product" idea is adapted from `shadcn/improve` and woven into `to-issues` and the `Ready for agent` readiness bar (not kept as a separate skill).

**GreenSock / GSAP** ([greensock/gsap-skills](https://github.com/greensock/gsap-skills))
The `gsap-skills/` folder is an imported copy of GreenSock's official MIT-licensed GSAP AI skills bundle.

**Diglot-weave packet** (`in-progress/diglot-weave/`)
The diglot-weave material is recovered from Burooj's June 2026 Claude sessions and preserved with local source transcripts and zip artifacts. Its method lineage points to Robbins Burling's 1968 "diglot weave" and Krashen-style comprehensible input; the packet's research notes also cite adjacent public prior art such as [`m98/fluent`](https://github.com/m98/fluent), [`zhangrui-vibe/claude-code-english-coach`](https://github.com/zhangrui-vibe/claude-code-english-coach), [`geusan/claude-skills-english-tutor`](https://github.com/geusan/claude-skills-english-tutor), [`azborovskyi/claude-english-tutor`](https://github.com/azborovskyi/claude-english-tutor), [`rizukirr/no-vibe`](https://github.com/rizukirr/no-vibe), and [`CreatmanCEO/lingua-companion`](https://github.com/CreatmanCEO/lingua-companion).

**Anthropic** — the `anthropic-skills` bundle (not in this repo; installed separately as a Claude skill plugin) ships several useful primitives.

**Firecrawl** — the `firecrawl-*` skills (also installed separately as a plugin) come from Firecrawl's official Claude skill set.

**Everything else** — written from scratch or origin unclear. If you borrowed from something I should credit, let me know.

---

*Living draft. Burooj will keep tweaking.*
