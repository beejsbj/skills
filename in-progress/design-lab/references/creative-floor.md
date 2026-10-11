# Creative floor

Use this during exploration and on rendered compositions before handoff. The review checks whether the work follows an intentional direction, leads the eye, and gives meaningful feedback. It supports the user's taste judgment; it cannot guarantee that the user will like the result.

Ownership and token tracing belong to `systematizing.md`. Here, examine the actual experience. A coherent import graph does not make an indistinct or poorly composed interface good.

## Explore before committing

Specify variety deliberately rather than expecting repeated attempts to produce range. The orchestrator sets one shared brief and gives workers distinct exploration assignments, then reconciles overlap and gaps into a coherent comparison.

- **Established direction:** preserve accepted palette, type, doctrine, and liked details. Delegate scoped treatments within the unresolved space; an ordinary treatment in an accepted system does not need 3–5 new directions. A conflicting source export does not automatically supersede accepted intent.
- **Open direction:** develop 3–5 genuinely distinct candidates tied to the same brief. Vary the design point of view, not just recolours; specify the consequential choices, such as ground/accent values, named display/body type, density, geometry/elevation, and interaction character. Include a plausible departure from the reflexive choice.

Render open-direction candidates as comparable compositions using the same content, states, and host sizes. Give each a stable ID and name, a brief-specific rationale, concrete benefits and tradeoffs, and a preview or capture the user can compare. Written specs guide the work; they are not visual evidence. Preserve deep behavior through the existing seam when trying a new face, and identify units worth leaving alone. A visually attractive candidate that drops a difficult state has not won the comparison.

For an existing product, mount its real baseline beside treatments under the same content, states, and host constraints. Within an established direction, surface consequential unresolved taste or intent choices before dependent construction; otherwise proceed within the accepted brief.

For an open direction, present the comparison and wait for the user's selection or requested revisions before promoting a direction, building its full system, or adopting it. A recommendation is not a selection. The user may explicitly delegate selection for this pass; general permission to explore or do autonomous structural work does not. Independent work can continue while selection is pending. Freeze the selected direction in the tracker, keeping alternatives as short notes. Record accepted intent separately from the agent's proposal. Preserve distinctive details through systematization; a reuse decision should not flatten a meaningful creative difference. Reopen the direction for new evidence or user steering, not restless mid-build restyling.

## Review the rendered result

Inspect the real composition and later the final guide at representative sizes and states. Record concrete findings and fix them at their owners:

- **Unchosen house style.** Cream ground, serif display, terracotta/amber, and italic word accents reached for together without a brief-specific reason. The same applies to any habitual palette/type package. A calm organic direction can earn these choices; their presence alone is not a failure.
- **Generic defaults.** Decorative gradients, emoji labels, stock card recipes, placeholder illustration, or an unconsidered font stack replacing a deliberate decision. Familiar elements are legitimate when they serve the brief. Ask what the choice contributes rather than banning a color or typeface.
- **Flat hierarchy.** A first look cannot find the main purpose or action. Use scale, weight, tone, position, and density to establish a path; not every distinction needs all five. Check realistic long and empty content, not only the ideal hero.
- **Unclear feedback.** Interactive states are difficult to perceive, focus is lost, or transitions obscure cause and effect. Use motion only where it helps; immediate updates and Reduced Motion stillness are valid. Decorative movement on a noninteractive status does not make it a better control.
- **No point of view.** Nothing in color, type, layout, imagery, or interaction connects the result to this brief. Distinctiveness can be quiet and functional; it need not force spectacle into a dense tool.

Treat a failed review as a concrete design problem, not a score to assert away. Revise a proposal within the creative authority established in `SKILL.md`; if a protected accepted direction conflicts with the goal, show the conflict and proposed correction for a decision. If implementation drifted from a sound direction, correct the affected source. Keep existing behavior intact unless a change is in scope.

## Worked example: chosen hierarchy

Sprout is the invented plant-care system in `systematizing.md`. Warm paper and organic accents can express its natural, unhurried brief. The same treatment on a log viewer needs its own rationale; a domain label alone neither earns nor forbids a palette.

Suppose Sprout's garden view sets the kicker, heading, and summary at nearly equal size/weight, with an action that visually recedes. The hierarchy fails even when every value is a token. A better composition gives the task one clear headline and the primary action one clear visual role.

These excerpts show the ownership: shared recipes in tokens, action feedback in Button, and arrangement in the composition. Existing sources are extended rather than re-declared inside the guide.

```css
/* tokens.css — additional shared type, action, and motion roles */
:root {
  --text-sm: .875rem;
  --text-lg: 1.125rem;
  --text-hero: clamp(2rem, 5vw, 4rem);
  --weight-strong: 700;
  --leading-tight: 1.05;
  --tracking-label: .08em;
  --text-muted: #59574f;
  --action-bg: var(--ink);
  --action-fg: var(--paper);
  --action-hover-bg: #45433d;
  --focus-width: 2px;
  --focus-offset: 3px;
  --dur-feedback: 160ms;
  --ease-feedback: ease-out;
}

/* Inside the authoritative Button: relevant excerpt, not its whole API. */
.button {
  color: var(--action-fg);
  background: var(--action-bg);
  transition: background-color var(--dur-feedback) var(--ease-feedback);
}
.button:enabled:hover { background: var(--action-hover-bg); }
.button:focus-visible {
  outline: var(--focus-width) solid var(--ink);
  outline-offset: var(--focus-offset);
}
@media (prefers-reduced-motion: reduce) {
  .button { transition: none; }
}
```

```astro
---
// compositions/GardenHero.astro
import Button from '../primitives/Button.astro';
---
<section>
  <p class="kicker">Your garden</p>
  <h1>Water Monstera today</h1>
  <p class="summary">3 plants need attention this week</p>
  <Button>Open garden</Button>
</section>
<style>
  .kicker { font-size: var(--text-sm); letter-spacing: var(--tracking-label);
            text-transform: uppercase; color: var(--text-muted); }
  h1 { font-size: var(--text-hero); font-weight: var(--weight-strong);
       line-height: var(--leading-tight); text-wrap: balance; }
  .summary { font-size: var(--text-lg); color: var(--text-muted); }
</style>
```

The intended path is kicker → task → summary → action. Render it to check that this path actually reads, that the headline fits narrow hosts, and that focus/feedback remains visible. Tokenized CSS alone establishes none of those outcomes. The final guide imports GardenHero and Button rather than reproducing this markup.

## Attribution

The exploration and creative-floor approach was informed by [Trystan-SA/claude-design-system-prompt](https://github.com/Trystan-SA/claude-design-system-prompt), as recorded in this repository's June 28 rebuild commit `7417f97`. The current rules are adapted to Design Lab's workbench, ownership, and review workflow.
