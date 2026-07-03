---
name: two-axis-review
description: Two-axis review of the diff since a fixed ref — Standards (repo coding standards plus the smell baseline) and Spec (does the diff implement the bound Linear issue). Use when reviewing an issue-bound branch, vetting a diff before In Review, or asked to review changes since a ref.
---

# Two-Axis Review

Review the diff between `HEAD` and a fixed point along two axes:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement what the originating issue asked for?

Both axes run as **parallel native subagents** so they don't pollute each other's context; this skill aggregates their findings side by side.

## Process

### 1. Pin the fixed point

Whatever the user named — a commit SHA, branch, tag, `HEAD~5`. If they named none, use the repo's default branch; if that is ambiguous, ask.

Capture once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base) and `git log <fixed-point>..HEAD --oneline`.

Confirm the ref resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff fails here — not inside two parallel subagents.

### 2. Identify the spec source

In this order:

1. The bound Linear issue — the issue key in the branch name, commit messages, or named by the user. Fetch it with `./cockpit.py issue BJS-X` (run from `/Users/burooj/Projects/cockpit`); the body plus unresolved comments are the spec.
2. A path the user passed.
3. Ask. If the user says there is no spec, the Spec subagent skips and the report says "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written — `CODING_STANDARDS.md`, `CONTRIBUTING.md`, `AGENTS.md`/`CLAUDE.md`.

On top of whatever the repo documents, the Standards axis always carries the smell baseline in [references/smell-baseline.md](references/smell-baseline.md) — documented repo standards override it, and every smell is a judgement call.

### 4. Spawn both subagents in parallel

One message, two native subagent (general-purpose) calls.

**Standards subagent prompt** — include:

- The diff command and commit list.
- The standards-source files from step 3, plus the absolute path to this skill's `references/smell-baseline.md` with the instruction to read it before reviewing.
- The brief: "Report — per file/hunk where relevant — (a) every place the diff violates a documented standard: cite the standard (file + rule); (b) any baseline smell you spot: name it and quote the hunk. Documented-standard breaches can be hard violations; baseline smells are always judgement calls, and a documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec subagent prompt** — include:

- The diff command and commit list.
- The spec contents: the fetched issue body and unresolved comments, or the passed file.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour the spec didn't ask for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If there is no spec, skip the Spec subagent and note it in the final report.

### 5. Aggregate

Present the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Do **not** merge or rerank findings across axes — that reranking is what the separation exists to prevent.

End with one line per axis: finding count and the worst issue within that axis. No single winner across axes.

### 6. Leave the receipt

If the spec came from a bound Linear issue, end with a short receipt on it (run from `/Users/burooj/Projects/cockpit`):

```bash
./cockpit.py comment BJS-X "Two-axis review @ <fixed-point-sha>: Standards — <verdict>. Spec — <verdict>."
```

## Why two axes

A change can pass one axis and fail the other:

- Follows every standard, implements the wrong thing → Standards pass, Spec fail.
- Does exactly what the issue asked, breaks the repo's conventions → Spec pass, Standards fail.

Separate reports stop one axis from masking the other.
