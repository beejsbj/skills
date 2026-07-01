# Diglot-Weave Skill Search Report

Date: 2026-06-25

## Bottom Line

You already designed and had Claude build a formal `diglot-weave` skill on 2026-06-05. The artifact itself was created inside Claude's sandbox and I did not find the resulting `skills-repo.zip` or `diglot-weave/` folder on this Mac, but the full transcript contains enough structure to reconstruct it.

Public prior art exists for language coaching inside coding assistants, mostly as English correction, tutor mode, or deferred prompt review. I did not find a strong public Claude Code/Codex/OpenCode skill that does your specific thing: ambient diglot-weave inside normal coding or agent conversations with hidden state, phased progressive disclosure, and fluent code-switching as the end state.

## Local Evidence

Primary thread:

- Chat-scrobbler session: `claude:ef0ea9af-4660-4f7c-8874-15b3abb10942`
- Title: `Passive Spanish learning through mirror neurons`
- Date: 2026-06-05
- Extracted transcript: `outputs/diglot-thread-2026-06-05.md`

Key facts from that thread:

- The idea started as Spanish learning through ordinary LLM interaction rather than a separate study activity.
- You named the mechanism as frictionful contextual substitution: a target-language word carries the meaning-load inside an English sentence.
- Claude connected this to Robbins Burling's 1968 "diglot weave" lineage.
- You asked to create a skill and then put it on GitHub.
- The first draft was `spanish-diglot`.
- It used:
  - `SKILL.md`
  - `references/phase-1.md` through `references/phase-5.md`
  - a compact memory marker like `#spanish-skill-phase=1`
  - hidden progress state for `exposed`, `active`, and `mastered` vocabulary
- You corrected the design:
  - heavy emotional moments can be good mapping opportunities
  - remove the "Northstar" / graduation framing
  - generalize beyond Spanish
  - target fluent switching, not a separate learned subject
- The skill was renamed to `diglot-weave`.
- The generalized state marker became:

```text
#diglot language=Spanish phase=1
```

- The intended folder shape was:

```text
skills/
  README.md
  LICENSE
  diglot-weave/
    README.md
    SKILL.md
    references/
      phase-1.md
      phase-2.md
      phase-3.md
      phase-4.md
      phase-5.md
```

Secondary thread:

- Chat-scrobbler session: `claude:d2493afb-6e64-449a-84c7-2b26dcb56d8e`
- Title: `Pedagogy discussion summary`
- Date: 2026-06-09
- Extracted transcript: `outputs/diglot-thread-2026-06-09.md`

Key facts from that thread:

- Claude explicitly remembered the diglot-weave work as "pedagogy in practice, not theory."
- It described the skill as ambient weaving rather than explicit instruction.
- It compared your design to Matt Pocock's `/teach` skill and concluded yours was structurally similar in being phased, stateful, and progressive-disclosure based, but philosophically different.
- The gap you noticed was that existing tutor systems are delivery infrastructure/content pipelines, while your design is more like dialogos: learning through lived interaction, friction, forgetting, drift, and return.

## Public Prior Art

Strongest adjacent matches:

- `m98/fluent`: broad AI language-learning kit for Claude Code and others, with hooks, local progress tracking, and `AGENTS.md` support.
- `zhangrui-vibe/claude-code-english-coach`: closest coding-assistant match; uses Claude Code hooks to correct or upgrade English prompts while coding and log vocabulary.
- `geusan/claude-skills-english-tutor`: prompt-level English tutor with grammar checks and bilingual support.
- `azborovskyi/claude-english-tutor`: deferred review from Claude history rather than real-time coaching.
- `rizukirr/no-vibe`: useful packaging precedent for cross-platform tutoring across Claude Code, OpenCode, and Codex, but not language learning.
- `CreatmanCEO/lingua-companion`: closer to true code-switching language coaching, but standalone rather than an embedded coding-assistant skill.

Public gap:

- Existing tools mostly do English correction, translation overlay, separate language-learning sessions, or deferred drills.
- I did not find a polished public skill that does ambient diglot-weave inside ordinary coding interactions.

## Distinctive Shape Of Your Version

- Language is not a separate lesson mode.
- The assistant still does the user's real task first.
- The target language is woven into real work and real thought.
- State is silent and tiny, never a visible progress meter.
- The skill uses progressive disclosure, loading only the current phase.
- Emotional salience is a feature, with guardrails for actual crisis or precision-critical work.
- The end state is not "graduating" into another community; it is fluent switching inside the same lived space.

## Recommendation

Reconstruct `diglot-weave` as a real local skill/repo from the transcript, then compare it against `fluent` and `claude-code-english-coach` only for packaging and hook ideas. The core concept appears meaningfully distinct enough to deserve its own formal skill.
