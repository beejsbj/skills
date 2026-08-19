---
name: unslop
description: Semantic prose review that preserves load-bearing language, metaphor, voice, and document function. Use for skills and agent instructions, operational handbooks and runbooks, human-facing technical prose, or explicit requests to unslop or tighten writing.
---

# Unslop

Improve the meaning carried by the prose while preserving the author's voice and the document's native register.

**Semantic slop** is language that obscures, weakens, inflates, or substitutes for the intended meaning. A stylistic preference is not a defect by itself.

## Process

1. Identify the document's job and consumers. Determine whether it must guide an agent, operate a system, explain something to a person, or serve more than one of these roles.
2. Mark only passages with a specific semantic or pragmatic defect. Name the defect before changing the passage.
3. Apply the information test to terminology, metaphors, and unusual phrasing: if replacing the language with a plainer word loses useful distinctions or predictions, it is **load-bearing language**. Preserve it, define it when necessary, and use it consistently.
4. Rewrite the smallest span that fixes each marked defect. Preserve facts, uncertainty, tone, structure, code, commands, paths, links, and intentionally stable terminology.
5. Audit the result against the completion criteria. If the original already passes, leave it alone.

## What earns a change

Change prose when one of these failures is present:

- **Empty abstraction:** the sentence gestures at importance, quality, concern, progress, or mechanism without saying what happened or how it works.
- **Unsupported force:** confidence, praise, criticism, urgency, or promotional language outruns the evidence.
- **Vague authority:** a claim hides behind unnamed experts, reports, users, or consensus when the source matters.
- **Generic substitution:** reusable framing takes the place of a fact, instruction, decision, or explanation specific to this document.
- **Reader tax:** throat-clearing, repeated conclusions, stacked hedges, redundant transitions, or syntactic density makes the reader retain more than the idea requires.
- **Terminology drift:** several names refer to one concept, or one name silently refers to several concepts.
- **Formula over thought:** a stock contrast, tidy grouping, or canned conclusion distorts the natural shape of the material.
- **Unearned ceremony:** praise, reassurance, or ritual politeness distracts from the response or claims a relationship the evidence does not support.

Prefer concrete actors and mechanisms when they matter. Preserve passive voice when the actor is unknown or irrelevant. Replace qualitative magnitude with measurements when the text makes an empirical claim and measurements are available.

## Load-bearing language

Metaphors and technical terms are compressed models. Judge them by what they let the reader or agent infer, not by whether they appear on a fashionable-word list.

- `add` says that something is introduced. `wedge` can name a narrow entry that opens a larger space. They are not interchangeable when that shape matters.
- `ratchet` can encode one-way movement. Replacing it with `change` discards the monotonic constraint.
- `substrate` can name a shared supporting layer. Replace it with `base` only when no dependency or medium distinction is lost.

Keep a metaphor when it compresses a stable cluster of implications. Define it once if its intended predictions are not obvious. Replace it when it is ornamental, ambiguous, or pretending to explain a mechanism it merely decorates.

## Match the document

### Agent instructions

Behavioral reliability outranks smoothness. Preserve leading words, context pointers, completion criteria, authority boundaries, and deliberate repetition of a compact anchor. Remove a generic sentence only when it changes no likely agent behavior.

### Operational handbooks and runbooks

Preserve stable names, commands, paths, ownership boundaries, preconditions, postconditions, and warnings. A vivid metaphor may remain when it helps operators remember system topology or control relationships.

### Human-facing prose

Preserve the author's register and rhythm. Improve clarity without normalizing punctuation, sentence length, capitalization, dialect, first person, or emotional temperature into a house style.

Apply explicit user or project style requirements as local requirements, not as universal diagnoses of good writing.

## Completion criteria

The revision is complete only when:

- every change answers a named semantic or pragmatic defect;
- no change rests only on a word blacklist, punctuation preference, or claim that a pattern "sounds AI";
- every load-bearing term and metaphor retains the distinction it carried;
- all facts, qualifications, commands, paths, links, and authority boundaries still mean what they meant;
- every marked defect is gone, and the revision introduces no new defect from this skill's categories.

When asked for an audit rather than a rewrite, report only high-signal findings. For each finding, quote the passage, name the defect, explain the lost meaning or reader cost, and propose the smallest correction. A clean audit may conclude that no change is warranted.

Adapted from Lauren Tan's pstack [`unslop`](https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md). This version replaces universal style bans with semantic tests and explicitly protects informative metaphor.
