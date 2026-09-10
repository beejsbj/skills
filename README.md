# skills

My personal agent-skills repo. This is the live config that drives how Claude, Codex, Cursor, and opencode behave when I work — the global system instructions, model profiles, and a growing collection of slash-command skills.

It's a work in progress. I'll keep tweaking wording as I learn what actually works.

---

## Access points

This repository is the canonical source for Burooj-owned and deliberately adopted skills. Agent-specific skill directories are access points, not independent sources of truth.

- **Claude Code, Codex, and T3 Code:** repo-owned skill folders are linked into `~/.claude/skills/`, `~/.agents/skills/`, and `~/.codex/skills/` as described in `AGENTS.md`. T3 Code reads those native provider roots directly; it has no separate skill copy to maintain. Run [`scripts/sync-matt-pocock-skills.sh`](scripts/sync-matt-pocock-skills.sh) after cloning or updating the upstream vendor pin.
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

**`acpx/`** — adapted official skill for [openclaw/acpx](https://github.com/openclaw/acpx), the headless ACP client for reaching other models/providers. Model selection and the dated roster live in **`model-taste/`**.

**`model-taste/`** — reusable model/provider judgment and dated roster, separate from dispatch mechanics and transport.

**`consult/`** — independent model judgment: frame a neutral evidence packet, select a live frontier route and effort, and reconcile the consultant's verdict without surrendering the root decision.

**`finish-pr/`** — carries an existing pull request through independent review, active babysitting, authorized merge, and exact cleanup.

**`search-party/`** — parallel candidate discovery across source ecosystems, including dedicated computer-use scouts for rendered human-facing results and evidence-graded synthesis.

**`cockpit/`** — a catalog symlink to the sibling Cockpit repository, whose root `SKILL.md` is the cross-project router. The PATH entrypoint is that repository's `bin/cockpit`; Linear is one actuator under `cockpit linear`.

**`vendor/mattpocock-skills/`** — unchanged, pinned upstream suite from [mattpocock/skills](https://github.com/mattpocock/skills). The vendor exposes exactly its 25 promoted engineering and productivity skills through the manifest-driven linker; experimental and miscellaneous upstream skills stay unlinked by default.

**`pear/`** — local-first/P2P guidance for Pear/Holepunch: when to use peer replication, multi-device sync, Hypercore-style append-only stores, and pear:// app distribution instead of defaulting to servers, blockchain, or vague decentralization.

**`design-lab/`** — full design-system composition skill. Takes raw material (repo, screenshots, words, moodboards) and builds out a complete token/primitive/component taxonomy plus a live style guide.

**`linear/`** — Burooj's Linear board discipline and write path: lanes, labels, issue bodies, comments, dependencies, receipts, and cockpit app-actor commands.

**`zoom-out/`** — asks me to zoom out when I'm about to grind before naming the right problem.

**`tldw/`** — imported from the live OpenClaw host for extracting and summarizing YouTube transcripts with `yt-dlp`.

**`unslop/`** — semantic prose review for skills and agent instructions, operational handbooks and runbooks, and human-facing technical prose. It removes language that hides meaning while preserving informative metaphors, stable terminology, and the author's register.

**`gsap-skills/`** — imported GSAP AI skills bundle: core GSAP, timelines, ScrollTrigger, plugins, framework usage, examples, and plugin metadata.

**`in-progress/diglot-weave/`** — recovered packet for a future `diglot-weave` skill, including source transcripts, raw zip artifacts, recovered skill drafts, and prior-art notes.

---

## Credits / inspiration

**Matt Pocock** ([mattpocock/skills](https://github.com/mattpocock/skills))
The upstream suite is preserved unchanged in `vendor/mattpocock-skills/`, pinned as a git submodule. It replaces the earlier local forks of his workflow skills; updates are reviewed by advancing the pin rather than adapting copies.

**shadcn** ([shadcn/improve](https://github.com/shadcn/improve))
The "smart model writes a self-contained plan a cheaper model executes cold; the plan is the product" idea is adapted from `shadcn/improve` and lives in Cockpit's `Ready for agent` readiness bar (not kept as a separate skill).

**GreenSock / GSAP** ([greensock/gsap-skills](https://github.com/greensock/gsap-skills))
The `gsap-skills/` folder is an imported copy of GreenSock's official MIT-licensed GSAP AI skills bundle.

**Diglot-weave packet** (`in-progress/diglot-weave/`)
The diglot-weave material is recovered from Burooj's June 2026 Claude sessions and preserved with local source transcripts and zip artifacts. Its method lineage points to Robbins Burling's 1968 "diglot weave" and Krashen-style comprehensible input; the packet's research notes also cite adjacent public prior art such as [`m98/fluent`](https://github.com/m98/fluent), [`zhangrui-vibe/claude-code-english-coach`](https://github.com/zhangrui-vibe/claude-code-english-coach), [`geusan/claude-skills-english-tutor`](https://github.com/geusan/claude-skills-english-tutor), [`azborovskyi/claude-english-tutor`](https://github.com/azborovskyi/claude-english-tutor), [`rizukirr/no-vibe`](https://github.com/rizukirr/no-vibe), and [`CreatmanCEO/lingua-companion`](https://github.com/CreatmanCEO/lingua-companion).

**Anthropic** — the `anthropic-skills` bundle (not in this repo; installed separately as a Claude skill plugin) ships several useful primitives.

**Firecrawl** — the `firecrawl-*` skills (also installed separately as a plugin) come from Firecrawl's official Claude skill set.

**Everything else** — written from scratch or origin unclear. If you borrowed from something I should credit, let me know.

---

*Living draft. Burooj will keep tweaking.*
