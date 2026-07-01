# diglot-weave

Learn a language ambiently — the way a child learns a first one — by weaving it into normal conversation instead of sitting down to "study." No lessons, no flashcards, no progress screens. Just conversation that's quietly, increasingly, in your target language, until both languages are simply rooms you move between without a seam.

Built on the **diglot weave** (Burling, 1968) and **comprehensible input** (Krashen): one inferrable word at a time, escalating only as you prove you're following, with meaning always leading.

## How it works

Each message is normal conversation about whatever you're already discussing — with a controlled amount of your target language woven in that you infer from context. No translations in parentheses (that would let you skim). You stay, you infer, the word becomes yours. The ratio climbs through five phases until the two languages are both live and you switch fluidly between them.

It never grades you, never announces what it's doing, never shows you a score. Tracking is a tiny silent footnote the assistant keeps for itself. The watcher stays off.

Works for any language — set yours in the footnote.

## Setup

### In a chat app (with memory)
Paste into the system prompt / custom instructions / project instructions:

> Read the diglot-weave skill at https://github.com/USERNAME/skills/tree/main/diglot-weave and follow it in every conversation. My target language is **Spanish**. Maintain my progress as a memory entry tagged `#diglot` in the exact footnote format the skill specifies. Update it silently after each exchange. Never show me the footnote or my progress unless I ask.

Swap in whatever language you want. Most chat apps with memory can read and write the footnote.

### In an agent (with file access)
Point it at the skill and have it keep `diglot-progress.md` in your working directory or vault:

> Follow the diglot-weave SKILL.md. My target language is **Spanish**. Track my progress in `diglot-progress.md` using the skill's footnote format. Read only the current phase's reference file. Update the file silently after each session.

Slots cleanly into an OpenClaw-style setup — the progress file lives in your vault, agents read/write it like any other state.

## The footnote

The entire state. Tiny by design:

```
#diglot language=Spanish phase=1
active: hola, gracias, proceso, casa
exposed: agua, libro, pensar, ahora, mañana
note: catching ceiling easily
```

- `language` — your target language
- `phase` — which of the 5 phases (controls weave intensity)
- `active` — words you've produced unprompted; yours now
- `exposed` — recently woven words you haven't produced yet
- `note` — optional one-liner for the assistant's own calibration

Bootstrap, jump, or reset by editing this directly. Want phase 3? Change the number. Different language? Change `language` and clear the pools. Start over? Delete it.

## Structure

```
diglot-weave/
├── SKILL.md            # orientation, the weave mechanic, footnote format, when to yield vs. lean in
└── references/
    ├── phase-1.md      # one inferrable word per sentence
    ├── phase-2.md      # two words / short phrases
    ├── phase-3.md      # clauses; first nudges to produce
    ├── phase-4.md      # whole sentences interleaved
    └── phase-5.md      # both languages live; fluent switching
```

Only the current phase file is ever loaded — progressive disclosure keeps context light.
