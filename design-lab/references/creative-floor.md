# Creative Floor (Taste Axis Reference)

The Creative axis is the user's to review — but only **once, at the end**, and only at taste altitude. Before that handoff the skill guarantees a floor: the work must read as a *chosen* direction, not the model's default. This file holds the two things that keep it there — how to **explore** before committing, and the **floor self-audit** that runs before handoff. Like `systematizing.md`, none of this becomes a user question: explore, decide, fix, assert it done.

Cohesion (`systematizing.md`) asks *is it systematized*. The floor asks *is it any good*. They are orthogonal — a system can pass cohesion perfectly, every value tokenized and every primitive imported, and still be slop: the default cream-and-terracotta look, flat hierarchy, dead buttons. The floor is what catches that. Don't re-audit token tracing here; that's cohesion's job.

## Exploring directions

**Variety is written, not rolled.** These models have no temperature knob — you cannot sample your way to range. If you don't *specify* distinct directions, you get one safe default dressed three ways. So spec them.

Before composing, diverge:

- **If the material pins a direction** (brand, existing tokens, Claude Design HTML, a doctrine) — stay inside it. Explore a few *treatments* within the given palette/type, not away from it. Don't invent a rival brand.
- **If it doesn't** — generate **3–4 genuinely distinct directions**. Each is a concrete spec, not an adjective:
  - **ground + accent** — background and one or two accent colors, as real values (lean `oklch()` for harmony)
  - **type** — named display + body faces, with intent (not "a sans")
  - **density** — tight / normal / loose, on a 4 or 8px base
  - **geometry + elevation** — radius and shadow as one committed system (sharp / soft / pill)
  - **motion + component style** — quiet / expressive / playful; filled / ghost / outlined / elevated

  Rules: the directions **must not share a palette family** — four takes on warm-cream is *one* direction, not four. Make **at least one off-distribution** (a bet you wouldn't reach for by reflex). Tie each to the brief in one line of rationale.

Then **freeze one** as the visible direction block and record the alternates for the report. The user re-runs for a different bet; you do not stop to ask which.

## The floor self-audit

Run before the taste handoff. Every hit is fixed, not reported as a question — symmetric to the cohesion residue scan.

Floor residue (each must be 0 or deliberately justified by the brief):

- **House-style default.** The editorial-warm look — cream `#f4f1ea`-family ground + serif display (Georgia / Playfair / Fraunces) + terracotta/amber accent + italic word-accents — reached for *without the brief calling for it*. Any one can be a choice; all of them together on a dashboard, dev-tool, fintech, or enterprise surface is the default-template look, today's purple gradient. If the frozen direction itself drifted here with no reason, **re-pick**; if a surface drifted here off the frozen direction, **pull it back** to the direction.
- **Generic tropes as defaults.** Trendy multi-stop / neon gradients on large surfaces; emoji as decoration (🚀 ✅ prepending labels the brand doesn't use); rounded-corner + `border-left: 4px` as the *default* card; placeholder-grade hand-drawn SVG of people or scenes presented as final; Inter / Roboto / bare system stack as an *unconsidered* default. (Cohesion owns whether values are tokenized; the floor owns whether the *choice* was made.)
- **Flat hierarchy.** Primary / secondary / tertiary not separated by size + weight + color + position + density; the hero composition doesn't lead the eye; the 5-second test fails (a first look can't find the one thing that matters).
- **Dead interaction.** Interactive primitives with no hover / active / focus feedback, or state changes with no transition. The state *matrix* is cohesion's anatomy; the floor asks whether those states actually **read as feedback** in the realized UI.
- **Safe everywhere.** No axis — color, type, layout, or motion — where the direction commits boldly. The result is generically pleasant and forgettable. One strong choice beats many safe ones; if nothing is chosen with conviction, the bet wasn't placed.

## Worked examples

Same invented system as `systematizing.md` — **Sprout**, a calm plant-care app — so the references interlock. Foundation tokens as defined there (`--paper:#f4f1ea; --ink:#2b2a26; --sage:#7c9885; --clay:#c9785b; …`).

### 1. Default vs. chosen — the same palette, judged by the brief

Sprout's warm-organic palette (cream paper, sage, clay) is **not** house-style residue — a calm plant-care app earns warm-organic; it traces to the brief (natural, unhurried, tactile). The floor passes it.

The *same* palette on a different brief fails:

❌ Floor residue — a developer-tooling dashboard handed Sprout's cream/serif/clay because it's the reflex:

```css
/* LogStream.astro — a CLI log viewer */
.viewport { background:#f4f1ea; font-family:Georgia, serif; }
.tail-btn { background:#c9785b; }
```
- cream ground + serif display + terracotta on a dense, technical, monospace-native surface is the default look wearing the wrong brief — it reads as "AI made a dashboard," not as a chosen tool. **Re-pick:** a cool, near-black ground, a real mono/grotesk, one functional accent for the live state.

The lesson the floor encodes: warm-editorial is a **legitimate choice** and a **lazy default** — the only difference is whether the brief asked for it.

### 2. Flat vs. leading hierarchy in the hero

❌ Flat — the hero composition treats every element at one altitude:

```astro
<section class="hero">
  <p class="kicker">Your garden</p>
  <h1>Water Monstera today</h1>
  <p class="sub">3 plants need attention this week</p>
  <button>Open garden</button>
</section>
<style>
  .kicker,.sub { font-size:18px; color:var(--ink); }
  h1 { font-size:22px; font-weight:500; }
  button { background:var(--sage-1); color:var(--ink); }
</style>
```
- 18 / 22 / 18px at near-equal weight and one flat tone — nothing leads; the eye has to hunt. The CTA recedes into a tint. 5-second test fails.

✅ Leading — size + weight + tone + a committed primary action create a path:

```astro
<style>
  .kicker { font-size:var(--text-sm); letter-spacing:.08em; text-transform:uppercase; color:var(--sage); }
  h1      { font-size:var(--text-5xl); font-weight:700; line-height:1.05; text-wrap:balance; }
  .sub    { font-size:var(--text-lg); color:color-mix(in oklch, var(--ink), transparent 35%); }
  .cta    { background:var(--clay); color:var(--paper); padding:var(--space-md) var(--space-xl);
            transition:transform var(--dur-calm) var(--ease-gentle); }
  .cta:hover { transform:translateY(-1px); }
  .cta:focus-visible { outline:2px solid var(--clay); outline-offset:2px; }
</style>
```
- one large bold headline carries the eye; the kicker recedes by size and the muted accent; the sub is de-emphasized by tone; the CTA is the single saturated, lifted, focus-ringed element. Hierarchy *leads*, and the interaction is alive — values still all trace to tokens, so cohesion holds too.

**Test the floor with one question per surface:** could a stranger, in five seconds, name the one thing this is for — and does it look like *a* decision rather than *the* decision every model makes? If no, the floor isn't met yet.
