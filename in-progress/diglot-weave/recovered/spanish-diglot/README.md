# spanish-diglot

Learn Spanish ambiently — the way a child learns a first language — by weaving it into normal conversation instead of sitting down to "study." No lessons, no flashcards, no progress screens. Just conversation that's quietly, increasingly, in Spanish.

Built on the **diglot weave** (Burling, 1968) and **comprehensible input** (Krashen): one inferrable word at a time, escalating only as you prove you're following, with meaning always leading.

## How it works

Each message you get is normal conversation about whatever you're already discussing — with a controlled amount of Spanish woven in that you can infer from context. No translations in parentheses (that would let you skim). You stay, you infer, the word becomes yours. Over time the ratio climbs through five phases until the conversation is mostly Spanish, and then the skill's job is to push you *out* into real Spanish-speaking communities.

Crucially: it never grades you, never announces what it's doing, never shows you a score. The tracking is a tiny silent footnote the assistant maintains for itself. The watcher stays off.

## Setup

### In a chat app (with memory)
Paste this into the system prompt / custom instructions / project instructions:

> Read the spanish-diglot skill at https://github.com/USERNAME/spanish-diglot and follow it in every conversation. Maintain my progress as a memory entry tagged `#spanish-diglot` in the exact footnote format the skill specifies. Update it silently after each exchange. Never show me the footnote or my progress unless I ask.

Most chat apps with a memory feature can read and write that footnote. The assistant reads the phase number from memory, loads only that phase's instructions, weaves at that level, and updates the footnote.

### In an agent (with file access)
Point the agent at this repo and tell it to maintain `spanish-progress.md` in your working directory or vault:

> Follow the spanish-diglot SKILL.md. Track my progress in `spanish-progress.md` using the skill's footnote format. Read only the current phase's reference file. Update the file silently after each session.

Slots cleanly into an OpenClaw-style setup — the progress file lives in your vault, agents read/write it like any other state.

## The footnote

The entire state. Tiny by design:

```
#spanish-diglot phase=1
active: hola, gracias, proceso, casa
exposed: agua, libro, pensar, ahora, mañana
note: catching ceiling easily
```

- `phase` — which of the 5 phases you're in (controls weave intensity)
- `active` — words you've produced unprompted; these are yours now
- `exposed` — recently woven words you haven't produced yet
- `note` — optional one-liner for the assistant's own calibration

You can bootstrap or reset just by editing this. Want to jump to phase 3? Change the number. Want to start over? Delete it.

## Structure

```
spanish-diglot/
├── SKILL.md            # orientation, the weave mechanic, footnote format, when to go silent
└── references/
    ├── phase-1.md      # one inferrable word per sentence
    ├── phase-2.md      # two words / short phrases
    ├── phase-3.md      # clauses; first nudges to produce
    ├── phase-4.md      # whole sentences interleaved
    └── phase-5.md      # mostly Spanish; launch into the wider web
```

Only the current phase file is ever loaded — progressive disclosure keeps context light.

## License

MIT. Do whatever you want with it.
