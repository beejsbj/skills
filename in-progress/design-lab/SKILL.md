---
name: design-lab
description: Use when turning raw design material — repos, existing UI, Claude Design HTML, screenshots, moodboards, words, metaphors, notes, or partial components — into a cohesive ground-up design system (tokens, primitives, unique specimens, compounds, compositions) realized as a style-guide surface plus importable components. For composing or extending a whole system, not one-off component styling or quick visual tweaks.
---

# Design Lab

Compose a cohesive design system from raw material, systematize it autonomously, and stop only for taste.

Entry points: any mix of repos, existing UI, Claude Design HTML, screenshots, moodboards, words, metaphors, notes, or partial components. Material is a seed, not a boundary — generate or extend a direction, don't merely catalog what already exists.

## Two axes

Every run moves on two axes. Only one is the user's to review.

- **Creative axis — the user's.** Generating or extending ideas from the raw material: taste, intent, creativity, UX. The user reviews this **once, at the end.**
- **System axis — the skill's, fully autonomous.** Making everything cohere. The user **never** reviews this; the skill guarantees it and asserts it done.

Never ask the user a systematizing question. No "should this be a token?" gate. Resolve it yourself.

## The cohesion invariant

This is the entire product of the System axis:

> Every design decision resolves to an existing lower-level idea, is promoted into one, or is pruned.

Concretely: no orphan primitive sitting inline in a composition; no raw hex/px/duration that should be a token; no component re-declared instead of imported. The skill enforces this by self-audit — see `references/systematizing.md`.

## The creative floor

The Creative axis has a floor the skill guarantees autonomously — symmetric to the cohesion invariant, and just as un-negotiated with the user:

> Every surface reads as a *chosen* direction, not a default — distinctive, with hierarchy that leads the eye and interactions that feel alive.

This is the guard against the model's own defaults: the editorial-warm house style (cream `#f4f1ea`-family ground + serif display + terracotta/amber + italic word-accents) reached for *as a silent default*, generic SaaS tropes, flat hierarchy, dead interactions. Cohesion asks *is it systematized*; the floor asks *is it any good*. A system can pass cohesion perfectly — fully tokenized, fully imported — and still be slop. The skill detects and fixes floor violations by self-audit before the taste handoff; it never ships the default and calls it a bet. Detection rules, the exploration protocol, and fixes live in `references/creative-floor.md`.

## The loop

```text
material -> explore -> freeze -> compose -> systematize -> self-audit (cohesion + floor) -> taste handoff
```

1. **Intake.** Classify the material. Absorb any direction it already carries (brand, doctrine, Claude Design HTML, existing tokens).
2. **Explore.** Diverge before committing — don't grab the first idea. If the material already pins a direction, explore a few *treatments* within it; if it doesn't, generate 3–4 genuinely distinct directions, each specified concretely (ground/accent, display + body type, density, mood), not sampled, not four shades of one palette, at least one off-distribution. (See `references/creative-floor.md`.)
3. **Freeze.** Commit to **one** direction and write it as a visible direction block — the anchor everything downstream resolves to. Record the 1–2 alternates for the report. Do not re-decide the vibe mid-build.
4. **Compose.** Realize the frozen direction concretely in the style-guide surface, including at least one **hero composition** — not just a token/primitive gallery. This is the creative bet.
5. **Systematize.** One piece at a time: classify into the taxonomy → extract a real importable component into the source-of-truth location → the style-guide specimen **imports** it (never re-declares it) → add anatomy + a variant grid.
6. **Self-audit — both axes.** Run *both* invariants across the built system and fix every hit; never ask.
   - **Cohesion** (system) — every decision resolves down, promotes, or is pruned. `references/systematizing.md`.
   - **Creative floor** (taste) — chosen direction not default, hierarchy leads, interactions alive. `references/creative-floor.md`.
7. **Taste handoff.** Stage to ready-for-review and report only on the Creative axis. Stop.

## Taxonomy

The scaffold you compose into (source of truth, low → high):

`tokens` → `primitives` → `unique specimens` → `compounds` → `compositions`

Boundary rules ("which layer is this?") live in `references/systematizing.md`. During that classification, also decide whether the artifact should **snap** to an existing component, be **promoted as a variant**, or be **promoted as new**; the reuse decision is about sameness and difference, not taxonomy layer. The decision rule and Sprout examples live in `references/systematizing.md` under **Reuse decision**.

## Framework policy

Killing copy-paste drift means everything is **imported, never duplicated**. Standalone HTML where primitives are pasted is the failure mode.

- **Source-of-truth components match the consuming app.** A Vue app gets Vue primitives the app can import; React gets React. Greenfield with no app → Astro components are the source of truth.
- **Style-guide surface defaults to Astro static** (zero-JS build, portable, importable; mounts framework components as islands for interactive specimens) — unless the repo already has a stronger guide convention.
- Astro can import Vue/React; a Vue/React app cannot import Astro. Never make an existing app depend on Astro components.

## Autonomy rules

- **One human gate: the final taste review.** Zero interactive gates before it.
- Make creative calls and **state** them; never stop mid-flight to systematize.
- Commit to **one** direction. The user re-runs for other vibes or tweaks at review.
- Do **not** dump methodology `.md` files (scope/coverage/closure logs) into the repo. Deliverables are components + style guide + the review report.
- Style-guide surfaces **demonstrate** components; they never become the source of truth.

## The ready-for-review report

Short, framed only around taste/intent/creativity/UX:

- **Direction realized** — and 1-2 alternates considered, why this one.
- **Hero moment** — what to look at first.
- **Creative calls** — where I extended or invented beyond the raw material.
- **Needs your eye** — taste/UX judgments, not systematizing.
- **System axis** — one line: cohesion self-audit passed (N recipes promoted, M pruned, 0 orphans).

## Subagents (optional)

Two safe places to delegate — both keep a single hand on the build:

- **Recon (front).** For large generative runs, parallelize **read-only** archaeology (visual, repo) and rejoin before composing.
- **Floor review (back).** The creative-floor audit benefits from a *fresh-eyes* reviewer subagent — the builder is anchored to its own bet and under-sees its defaults. Have it report findings against `references/creative-floor.md`; you fix. Cohesion stays a self-audit.

Optional — not required ceremony. Never fan out **construction** to parallel workers: cohesion lives in the imported tokens + primitives, and one hand on the build is what keeps the visual point of view single.

## Quality bar

A formalized primitive: a real importable component, a token for every value, states + variants named, and the style-guide specimen importing it rather than copying it. Worked examples — one per taxonomy layer (token promotion, primitive, unique specimen, compound, composition) plus cross-layer drift — are in `references/systematizing.md`, built on an invented system rather than any real repo.

That is the **system** half of the bar. The **taste** half — a distinctive committed direction, hierarchy that leads, interactions that feel alive, no default-house-style drift — is the creative floor in `references/creative-floor.md`. Both halves are guaranteed before handoff; passing one is not passing the other.
