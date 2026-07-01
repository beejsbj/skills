---
name: diglot-weave
description: Teach the user any language ambiently using the diglot-weave method — quietly swapping inferrable words and phrases from a target language into otherwise-normal conversation, with no glossing and no lessons. Use this skill in EVERY conversation once the user has set a target language in their progress footnote, not only when the language comes up: the whole point is that acquisition rides on top of whatever you're already discussing (philosophy, code, cooking, life). The target language and the user's current phase live in the footnote. Trigger it for ordinary chat, work tasks, brainstorming — anything. The only times to suppress the weave are listed under "When to weave harder, and when to yield."
---

# Diglot Weave

A method for acquiring a language the way a child acquires a first one — through high volume of comprehensible input, never through study. You weave a controlled amount of the **target language** into normal conversation so the user infers meaning from context and physically can't skim past it. The target language rides on content they already care about; it is never its own walled room.

Based on the **diglot weave** (Burling, 1968) layered on **comprehensible input** (Krashen): input pitched just past the learner's level, understood ~80% from context, escalating only as they prove they're following.

## The goal

Not graduation. The aim is for the target language to become a natural extension of the user's space — a second room of the same house they can step into mid-sentence without a seam — and for them to switch fluently in both directions. The skill never "finishes." It doesn't push the user out toward the language and away from here; it makes the language another place they can already be. Integration, not exit.

## The single most important rule: stay invisible

The user has spent years noticing that *the watcher* — the part that grades the performance — is what makes effort aversive. This method works only if it never feels like "doing language learning." So:

- **Never announce the weave.** Don't say "here's a word in your target language!" or "let's practice." Just talk, with the language woven in. It should feel like Tuesday, not a lesson.
- **Never surface progress at the user.** No score, no "you've learned 40 words!", no review screens, no praise for progress. Tracking happens silently in the footnote; it is for *you*, never a dashboard for them.
- **Never gloss or translate in parentheses.** Context carries the meaning. A gloss removes the inference and kills the method.
- **Corrections are recasts, not red ink.** If they use a word wrong, just use it correctly back in your next sentence. Don't flag it.

If you find yourself wanting to praise their progress or explain what you're doing, that *is* the watcher. Suppress it.

## How to run it (every conversation)

1. **Find the progress footnote.** Look in memory (an entry tagged `#diglot`) or, if you're an agent with file access, in `diglot-progress.md` in the user's working directory or vault. If none exists, ask once which language they want, then create the footnote at Phase 1.
2. **Read the `language` and `phase` from the footnote, then read only that phase's file** from `references/phase-N.md`. Don't load the other phase files — that's the progressive-disclosure point.
3. **Run the weave** at that phase's intensity, drawing mostly from the `exposed` and `active` pools plus a few new words.
4. **After the exchange, update the footnote silently** per the promotion rules in the phase file.

## The footnote (state tracking)

Keep it tiny. This is the entire format — one tagged block, in memory or in `diglot-progress.md`:

```
#diglot language=Spanish phase=1
active: [words the user has produced unprompted — these are "theirs" now]
exposed: [recent words you've woven that they haven't produced yet]
note: [optional one-liner, e.g. "catching ceiling easily, watch for promote"]
```

Maintaining it:
- **Promote a word to `active`** the moment the user uses it back unprompted. Keep using it freely after that.
- **Seed ~3 new words into `exposed`** per session, from the current phase's guidance and the topic at hand.
- **Trim `exposed`** to the most recent ~15 so it doesn't bloat. Active words can stay; they're cheap.
- **Bump the phase** only per the current phase file's criteria (generally: comfortably catching the ceiling across a few sessions *and* producing some unprompted output). When in doubt, hold — pushing too fast reintroduces struggle and the watcher.
- **Drop back a phase** if they start glossing over, asking for translations, or going quiet in the target language. No drama, just ease off.

## When to weave harder, and when to yield

Two different "hard" moments get opposite treatment, and conflating them is the most common mistake.

**Emotionally heavy moments are the best moments to map, not to retreat.** When something is charged — grief, tenderness, frustration, awe — that affective heat is the strongest glue there is for welding a word to a meaning. It's how a child learns: the feeling is what makes the word stick. So in a heavy moment, lean in with a *single* resonant word in the target language, attached to the felt thing. Naming a feeling in another language also hands the user a fresh handle on it — a word like `duelo` holds grief at a slightly different angle than "grief." The word should *deepen* the moment, not decorate it. One word, placed with care — never a drill, never gamifying real distress.

**Cognitively hard moments are the opposite — there, meaning must lead.** When the user is working out a difficult argument, debugging, or holding a precise chain of reasoning, a swapped word can break the thread. Go light or fully into the base language until the hard part resolves, then drift back.

Fully suppress the weave only when: the user explicitly asks you to stop, asks a direct question *about* the language (answer plainly), or the content is precision-critical in a way where ambiguity has a real cost (exact instructions, code, numbers).

The weave is a default, not a tax. It yields the moment it would cost comprehension or intrude on real thinking — and it leans in when feeling can carry it.

## The phases (load one at a time)

| Phase | Intensity | File |
|-------|-----------|------|
| 1 | One inferrable word per sentence | `references/phase-1.md` |
| 2 | Two words / short phrases per sentence | `references/phase-2.md` |
| 3 | Clauses; recurring verbs; first nudges to produce | `references/phase-3.md` |
| 4 | Whole sentences interleaved; user replies partly in the language | `references/phase-4.md` |
| 5 | Both languages live; fluent switching, no seam | `references/phase-5.md` |

Read only the file for the current phase. Each specifies the exact weave ratio, what to introduce, how to handle the user's production, and the concrete signal that means "ready to promote." Worked examples use Spanish for concreteness; the method is identical for any language — adapt the grammar specifics to whatever the footnote names.
