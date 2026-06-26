---
name: web-animation-recipes
description: Build, adapt, or review focused web animation demos and interaction recipes in HTML/CSS/JS or frontend apps. Use when the task mentions web animation, motion design, WAAPI, CSS transitions/keyframes, SVG animation, page transitions, microinteractions, recipe-book animation examples, reduced motion, or verifying that animation behavior actually renders and survives interaction stress.
---

# Web Animation Recipes

Use this skill when the work is about making motion itself legible and robust, not just decorating an interface.

## Workflow

1. Identify the motion job:
   - **State transition:** route, tab, drawer, modal, card expand/collapse.
   - **Microinteraction:** button press, selection, drag/drop, toggle, progress.
   - **SVG-native motion:** stroke drawing, path motion, masks, filters, symbol reuse.
   - **Scene/recipe demo:** a small standalone proof of one animation principle.
2. Choose the smallest primitive that can carry it:
   - CSS transitions for simple state changes.
   - CSS keyframes for repeatable ambient or staged loops.
   - WAAPI for cancelable, inspectable, JS-coordinated transitions.
   - SVG attributes, paths, masks, filters, and `viewBox` composition when the effect is genuinely SVG-specific.
   - A JS animation library only when sequencing, layout projection, gestures, or physics justify the dependency.
3. Build a deterministic state harness:
   - URL params, buttons, or visible controls should let the state be reloaded and tested.
   - Rapid repeated interactions should cancel or settle cleanly.
   - Use stable dimensions so animation states do not resize the layout unexpectedly.
4. Respect motion accessibility:
   - Provide `prefers-reduced-motion` behavior.
   - Prefer a reduced version of the state change over hiding the state change entirely.
   - Avoid motion that blocks reading, focus, or repeated operation.
5. Verify with a real render:
   - Start a local server when file loading or modules need it.
   - Use browser/Playwright/in-app browser screenshots when available.
   - Check console errors and interaction stress, especially rapid clicks and interrupted WAAPI animations.
   - Confirm the animated element is visible, framed, and nonblank at desktop and a narrow viewport when layout is part of the task.

## Implementation Rules

- Animate `transform` and `opacity` first. Animate layout-affecting properties only when the animation is specifically about layout and the performance cost is acceptable.
- Keep easing intentional: entries usually ease out, exits are shorter, and overshoot belongs to objects with a reason to rebound.
- Separate semantic state from animation state. The UI should still have a correct selected/open/current state if animation is disabled or interrupted.
- For WAAPI, handle canceled animations. `animation.finished` can reject with `AbortError`; catch or ignore expected cancellation.
- For SVG, use the SVG feature as the point of the demo. If a `div` could do the same thing more simply, do not wrap generic DOM motion in an SVG shell.
- Do not rely on text explaining what the user should see. The movement should make the state change understandable on its own.

## Demo Deliverables

For standalone demos, create:

- `index.html`
- `styles.css`
- `script.js` when behavior is needed
- `README.md` explaining what motion recipe was tried, what animation-specific technique mattered, what was verified, and what limitations remain

Keep demos self-contained unless the user asked for a framework. If using outside prior art, cite the source in the README or comments.

## Review Checklist

Before finishing, answer these in the final receipt:

- What is the primary motion recipe?
- Which browser-rendered checks were run?
- What happens under rapid repeated interaction?
- What does reduced motion do?
- Which files changed?
