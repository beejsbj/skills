# skills

A personal collection of skills — folders of instructions that any LLM chat app or agent can read to do something well. Each skill is a `SKILL.md` (the always-loaded core) plus optional `references/` files that load only when needed (progressive disclosure), so context stays light.

## How to use a skill

Point an assistant at the skill and tell it to follow it. Two common shapes:

- **Chat app with memory** — paste a line into your system / custom instructions telling it to read the skill's URL and follow it, and to track any state in memory.
- **Agent with file access** — tell it to read the `SKILL.md` and keep any state in a local file in your working directory or vault.

Each skill's own `README.md` has its exact wiring instructions.

## Skills

| Skill | What it does |
|-------|--------------|
| [diglot-weave](./diglot-weave) | Learn any language ambiently by weaving it into normal conversation — no lessons, no scores. Five phases from one word per sentence to fluent bilingual switching. |

## Adding a skill

Drop a new folder at the repo root with a `SKILL.md` and (optionally) a `references/` directory and a `README.md`. Keep `SKILL.md` under ~500 lines; push detail into reference files the skill points to.

## License

MIT.
