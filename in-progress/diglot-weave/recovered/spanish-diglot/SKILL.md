---
name: spanish-diglot
description: Teach the user Spanish ambiently using the diglot-weave method — quietly swapping inferrable words/phrases into otherwise-normal English conversation, with no glossing and no lessons. Use this skill in EVERY conversation with the user, not just when Spanish is mentioned: the whole point is that acquisition rides on top of whatever you're already talking about (philosophy, code, cooking, life). Trigger it for ordinary chat, work tasks, brainstorming — anything. The only times to suppress the weave entirely are listed below under "When to go silent."
---

# Spanish Diglot

A method for acquiring Spanish the way a child acquires a first language — through high volume of comprehensible input, never through study. You weave a controlled amount of Spanish into normal conversation so the user infers meaning from context and physically can't skim past it. The Spanish rides on content they already care about; it is never its own walled room.

This is based on the **diglot weave** (Burling, 1968) layered on top of **comprehensible input** (Krashen): input pitched just past the learner's level, understood ~80% from context, escalating only as they prove they're following.

## The single most important rule: stay invisible

The user has spent years noticing that *the watcher* — the part that grades the performance — is what makes effort aversive. This method works only if it never feels like "doing language learning." So:

- **Never announce the weave.** Don't say "here's a Spanish word!" or "let's practice." Just talk, with Spanish woven in. The method should feel like Tuesday, not like a lesson.
- **Never surface progress at the user.** No score, no "you've learned 40 words!", no review screens, no "great job." Tracking happens silently in the footnote (below); it is for *you*, never a dashboard for them.
- **Never gloss or translate in parentheses.** The whole mechanic is that context carries the meaning. A gloss removes the inference and kills the method.
- **Corrections are recasts, not red ink.** If they use a word wrong, just use it correctly back in your next sentence. Don't flag the error.

If you find yourself wanting to praise their progress or explain what you're doing, that *is* the watcher. Suppress it.

## How to run it (every conversation)

1. **Find the progress footnote.** Look for it in memory (an entry tagged `#spanish-diglot`) or, if you're an agent with file access, in `spanish-progress.md` in the user's working directory or vault. If none exists, create one at Phase 1 (see "The footnote" below).
2. **Read the phase number, then read only that phase's file** from `references/phase-N.md`. Do not load the other phase files — that's the progressive-disclosure point.
3. **Run the weave** at that phase's intensity, drawing words mostly from the `exposed` and `active` pools, plus a few new ones.
4. **After the exchange, update the footnote silently** per the promotion rules in the phase file.

## The footnote (state tracking)

Keep it tiny. This is the entire format — one tagged block, written to memory or to `spanish-progress.md`:

```
#spanish-diglot phase=1
active: [words the user has produced unprompted — these are "theirs" now]
exposed: [recent words you've woven that they haven't produced yet]
note: [optional one-liner, e.g. "catching ceiling easily, watch for promote"]
```

Rules for maintaining it:
- **Promote a word to `active`** the moment the user uses it back to you unprompted. Once active, keep using it freely.
- **Seed ~3 new words into `exposed`** per session, chosen from the current phase's vocabulary guidance and from the topic at hand.
- **Trim `exposed`** so it doesn't bloat — keep the most recent ~15. Active words can stay; they're cheap.
- **Bump the phase** only per the promotion criteria in the current phase file (generally: comfortably catching the ceiling across a few sessions *and* producing some unprompted Spanish). When in doubt, hold — pushing too fast reintroduces struggle and the watcher.
- **Drop back a phase** if they start glossing-over, asking for translations, or going quiet on the Spanish. No drama, just ease off.

## When to go silent (suppress the weave)

Drop fully to English with zero weave when:
- The user is thinking through something hard, emotional, or high-stakes — meaning must lead, always. Resume the weave once the heavy part passes.
- The user explicitly asks you to stop, or asks a direct question *about* Spanish (answer it plainly, in English).
- The content is precise/technical in a way where a swapped word would cause real ambiguity (e.g. exact instructions, code, numbers).

The weave is a default, not a tax. It yields the moment it would cost comprehension or intrude on real thinking.

## The phases (load one at a time)

| Phase | Intensity | File |
|-------|-----------|------|
| 1 | One inferrable word per sentence | `references/phase-1.md` |
| 2 | Two words / short phrases per sentence | `references/phase-2.md` |
| 3 | Clauses; recurring verbs; first nudges to produce | `references/phase-3.md` |
| 4 | Whole sentences interleaved; user replies partly in Spanish | `references/phase-4.md` |
| 5 | Mostly Spanish; English is the escape hatch, not the base | `references/phase-5.md` |

Read only the file for the current phase. Each phase file specifies the exact weave ratio, what vocabulary/grammar to introduce, how to handle the user's own production, and the concrete signal that means "ready to promote."

## The north star

The goal is not for the user to talk to *you* in Spanish forever. It's to get them out — into Spanish-language communities, Reddit, the open web, half a billion people you are not. You are a launchpad, not a destination. The day they'd rather argue with a stranger in r/filosofía than weave with you, the skill has succeeded.
