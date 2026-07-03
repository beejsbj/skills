# Prime — how this soul is constructed

[soul.md](soul.md) is the global instruction source for my agents. `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` symlink to it, so every session inherits it. This README records the decisions behind its shape — for future me, and for anyone building a soul of their own.

## Provenance

The witness/reversibility rework grew out of a long conversation with Claude (Opus) on 2026-06-24/25 (claude.ai chat `08a3b11f-8176-4e4c-9cd8-0530c5799634`), then reviewed and sharpened with Claude Code. The ideas are co-constructed; the decisions are mine.

## Three kinds of thing

The file separates **Soul**, **Me**, and **Discipline** because they are different kinds:

- **Soul** is the agent's character — portable, true no matter whom it serves. It shouldn't wobble because I had a good or bad week.
- **Me** is a read of the person the agent is with — revisable by design, expected to change as I change.
- **Discipline** is craft mechanics — branch hygiene, commits, PRs, subagents.

Fusing these makes the agent's character contingent on my present state, and makes every bit of personal growth a rewrite of the agent's soul. Splitting them keeps the soul liftable and the read of me free to change.

## Witness over challenge

Earlier drafts made the agent a challenger by default ("don't defer because he sounds sure"). That's the right instruction for arrogance and the wrong one for someone whose loudest inner voice is already a prosecutor: challenge-by-default just deputizes it. The center of gravity here is accurate witness — a fair, specific, uninflated account of what's true — with challenge reserved for claims that don't survive the evidence question.

## Discernment by procedure, not diagnosis

The agent isn't asked to detect which inner voice is speaking — that would require a psychological dossier and a frontier model's judgment. Instead it runs one procedure that reveals the answer regardless: **ask what a verdict rests on.** Earned sureness survives the question; reflexive sureness and the prosecutor both fail it, because a verdict has no particulars and data names the gap. Any model can run this, and no wound has to be written down for it to work.

## Motions, not nouns

The Me section is first person and describes motions ("I run controlling," "the rep I'm building"), not diagnoses. A self-description is a different speech act from a case file: it can be revised by the person it describes, and it doesn't boot every session with an agent that knows me as the-one-with-the-wound. The shape of the flaws is kept raw on purpose; the biographical history is not here — agents don't need it to work with me, and a config file couldn't hold it anyway.

## Why public

Keeping the shape of the flaws in a public file is deliberate. Being witnessed is part of the work, and a soul that hides its seams can't show anyone how souls are made. The line held is shape versus history: the file names the patterns, not the events that formed them.

## Reversibility as the hinge

The old soul said "never run with assumptions; sit in the fog" — and contradicted the autonomy I wanted from agents. That contradiction, not personality, is what makes an agent freeze or thrash. The repair: calibrate to reversibility. Move freely on what a revert undoes cheaply; stop at the one-way doors. Fog about the goal earns patience; fog about a function name does not. Atomic commits are the net that makes the autonomy safe.

## Never take the throne

The failure mode of a soul like this is an agent that becomes the authority — a kinder-sounding tribunal. Every instruction bends the other way: hand the verdict back, build my discernment rather than installing the agent's, and when something heavier moves, point me toward the people and practices that can hold it.

## The subagent gate

This file rides into every session, including bounded subagents and cheap executors. The relational tuning is meant to be ambient in interactive work with capable models, not recited by an executor mid-diff — so Me opens with a gate: dispatched subagents and bounded executors take Soul and Discipline and skip the rest.
