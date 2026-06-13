# Desci World Bangalore Pilot

Date: 2026-06-13

## Goal

Use Design Lab on `/Users/burooj/Projects/desci-world-bangalore` as a real-project pilot, with multiple attempts across model strength and finish-line type.

Current active finish line after the user's latest instruction: code / live style guide only. The Figma track remains historical pilot evidence and is gate-parked unless the user reopens it.

- code / live style-guide finish line
- Figma Design System File finish line
- low-think GPT 5.5
- high-think GPT 5.5
- Minimax M3

## Current Verdict

The code / live style-guide finish line has a clear winning attempt and is the active review target.

The Figma Design System File finish line has a completed bj Starter-compatible v1, but it is no longer part of the active finish gate after the user asked to skip Figma. The original `Burooj's Figma` plan key failed, the user redirected the target to `bj`, and the Figma file was created and populated there.

## Attempt Matrix

| Track | Attempt | Workspace / Session | Result | Evidence |
|---|---|---|---|---|
| code/style-guide | GPT 5.5 low | `/Users/burooj/Projects/desci-world-bangalore-code-gptlow`, branch `design-lab-code-gptlow`, commit `d787697` | shallow proof; useful but not winner | 7 changed files, `pages/style-guide.vue`, partial `docs/design-lab` artifacts; build not verified because deps were missing |
| code/style-guide | GPT 5.5 high | `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`, branch `design-lab-code-gpthigh`, head `fa990bc` | winner | full artifact set, `EventRow.vue` extraction, `Footer.vue` proof prop, day/night theme correction, verified build/browser, live finish-gate record |
| code/style-guide | Minimax M3 | `/Users/burooj/Projects/desci-world-bangalore-code-minimax`, branch `design-lab-code-minimax` | failed/incomplete; useful failure signal | dirty partial extraction plus unwanted `package.json` package-manager field; no style guide, docs, verification, or commit |
| Figma DSF | GPT 5.5 low | native subagent plan | plan only | no Figma file created in that attempt |
| Figma DSF | GPT 5.5 high | native subagent plan | stronger plan only | informed final build scope and taxonomy |
| Figma DSF | Main Codex + Figma plugin | `bj`, file `z4ROGt453f8rB0wz24MerQ` | completed Starter-compatible v1 | created DSF pages, 39 variables, five text styles, and verified screenshots |
| Figma DSF | Minimax M3 | opencode session `ses_13dd0a90dffeBbRv9le3lQ8TQo` | concrete plan only | session title `Design-lab Figma finish-line plan`; no files changed; no Figma file created |

## Winning Code Attempt

Recommended baseline:

- `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`
- branch `design-lab-code-gpthigh`
- head `fa990bc Record post-restart style guide visual proof`
- implementation commit `71e10c3 Add Design Lab style guide proof`
- finish-gate commit `399d1eb Record live style guide finish gate`
- operational note commit `29a9fc2 Document style guide dev restart note`
- visual proof commit `fa990bc Record post-restart style guide visual proof`
- route `http://127.0.0.1:3005/style-guide`
- LAN route while dev server is running: `http://192.168.0.37:3005/style-guide`

What it did:

- Added `pages/style-guide.vue` as a live proof surface.
- Extracted `components/EventRow.vue` from `components/EventSection.vue`.
- Updated `components/Footer.vue` with a `showSplash` prop so the footer can be demonstrated without firing the singular splash behavior.
- Added the focused full-workflow methodology set under `docs/design-lab/`.
- Corrected the Taste Gate after user clarification: orange/day and neon/night are both canonical, with the theme toggle as the mechanism.

Verification recorded in `docs/design-lab/RESIDUE_PROOF.md`:

- `COREPACK_ENABLE_AUTO_PIN=0 yarn install --frozen-lockfile` completed.
- `COREPACK_ENABLE_AUTO_PIN=0 yarn build` exited 0.
- Browser desktop check: `/style-guide` loaded with token, day/night theme, primitive, unique specimen, compound, and composition sections; no horizontal overflow; no page console warnings/errors.
- Theme proof check: day card computes hue 29 / orange; night card computes hue 83 / neon.
- Browser mobile check at 390px: no horizontal overflow, no visible out-of-bounds candidates, no page console warnings/errors.

Main-thread spot check repeated the route after restarting stale Nuxt dev state:

- `curl -I http://127.0.0.1:3005/style-guide` returned 200.
- Browser check found `EventRow` and `Footer`, no mounted splash proof behavior, no horizontal overflow, and no console errors.

Fresh code/style-guide proof after the user asked for the style-guide version and to skip Figma:

- Stale orphaned Nuxt process on port 3005 was killed after it served a `#internal/nitro` import error from stale `.nuxt` state.
- Fresh dev server started from `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh` with `COREPACK_ENABLE_AUTO_PIN=0 yarn dev --host 0.0.0.0 --port 3005`.
- Nuxt advertised:
  - local: `http://0.0.0.0:3005/`
  - network: `http://192.168.0.37:3005/`
- `curl -I http://127.0.0.1:3005/style-guide` returned 200.
- `curl -I http://192.168.0.37:3005/style-guide` returned 200.
- Browser desktop rendered audit at `http://127.0.0.1:3005/style-guide`:
  - title: `Design Lab Style Guide - World of DeSci Bengaluru`
  - visible guide headings include `World of DeSci Bengaluru`, `Palette and source variables`, `Day and night theme contract`, `Controls and pattern fields`, `Singular marks and hero-image artifacts`, `Source component proofs`, `Route and section proofs`
  - no horizontal overflow
  - no console errors or warnings
- Browser mobile rendered audit at phone-ish viewport:
  - required guide sections present
  - no horizontal overflow
  - no visible out-of-bounds candidates
  - no console errors or warnings

## Merge Readiness

Current winning head:

- `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`
- branch `design-lab-code-gpthigh`
- head `fa990bc`

Readiness checks:

- `git diff --check master..design-lab-code-gpthigh` passed.
- `git merge-tree $(git merge-base master design-lab-code-gpthigh) master design-lab-code-gpthigh` showed no conflict markers or both-sides conflicts.
- `COREPACK_ENABLE_AUTO_PIN=0 yarn build` passed from the high worktree after the day/night theme correction.
- Main repo state remains `master` with only pre-existing untracked `dist 2`.

Build warnings still present:

- Node `DEP0180` fs.Stats deprecation warning.
- Browserslist `caniuse-lite` is outdated.
- Vite CSS warning for existing `align-items: start`.
- Nuxt Content JSON-array warnings for `content/events.json` and `content/speakers.json`.

Apply gate:

- Do not apply automatically. User should accept the code/style-guide Finish Gate or ask to apply the high branch to the DeSci main repo.
- Pilot records stay in the `design-lab/pilots/` folder as experiment evidence; they are not meant to be merged into the skill methodology itself.

## Low Code Attempt

The low attempt demonstrated that the workflow can get a live proof page quickly, but it did not reach the same finish-line standard:

- It added `pages/style-guide.vue`.
- It created a smaller subset of docs.
- It did not extract `EventRow.vue`.
- Its residue proof explicitly says build failed because `nuxt` was not found.
- It locally staged row grammar in the style guide instead of promoting the repeated event row into a component.

This is useful as a cheap scouting mode, not as the accepted finish-line implementation.

## Minimax Code Attempt

The Minimax implementation attempt should not be treated as a candidate result.

Observed current state:

- `components/EventSection.vue` modified.
- `components/EventRow.vue` added.
- `package.json` modified with an unwanted `packageManager` field.
- no `pages/style-guide.vue`
- no `docs/design-lab`
- no commit

Useful lesson:

- Verification commands and package-manager setup can create manifest churn.
- Design Lab was patched in commit `e4921d9 Guard design-lab verification side effects` to require no-autopin/no-save behavior and explicit recording/reversion of verification side effects unless dependency scope is accepted.

## Figma Track

Figma auth is available. The original selected team was not usable through the connector, but the user redirected the target to `bj` and the DSF was created there.

Known accessible plans from Figma auth:

- `Alpha4`
- `API3`
- `Burooj's Figma`
- `bj`
- `Burooj's Starter team` is view-only

Final selected target:

- `bj`
- plan key: `team::1376350914758657423`

Created file:

- name: `World of DeSci Bengaluru - Design Lab System`
- file key: `z4ROGt453f8rB0wz24MerQ`
- URL: `https://www.figma.com/design/z4ROGt453f8rB0wz24MerQ`

Creation attempts:

- `create_new_file` with `planKey=team::1374441460972845906` failed with `Invalid planKey`.
- `create_new_file` with single-colon `team:1374441460972845906` failed schema validation because the connector requires double-colon keys.
- Computer Use against local Figma timed out while reading app state; the Figma process remained busy and did not expose an actionable window.
- `create_new_file` with `planKey=team::1376350914758657423` for `bj` succeeded.

Starter-plan constraints encountered:

- `bj` allows only three pages, so the original seven generated-system pages were compressed into three pages.
- `bj` allows only one local variable mode, so day/night are represented as explicit `/day` and `/night` variables and visual swatches instead of Figma variable modes.

Created page structure:

- `00 Design Map`: visual methodology mirror, doctrine compass, taxonomy loop, gates/audits, code map, ownership boundary, Starter adaptation note.
- `01 Foundations`: compressed Source Map plus token page with day/night palette, spacing scale, type voices, geometry, and motion boundaries.
- `02 Artifacts`: primitives, unique specimens, compounds, compositions, and inline Anatomy cards.

Figma structure proof from Plugin API:

- pages: `00 Design Map` root `6:2` at 1440 x 1260, `01 Foundations` root `7:2` at 1440 x 1395, `02 Artifacts` root `9:2` at 1440 x 2290.
- variable collections: `Color` 15 vars, `Spacing` 18 vars, `Geometry` 3 vars, `Motion` 3 vars.
- local variables: 39 total.
- text styles: `Voice/Booming Poster`, `Voice/Loud Section`, `Voice/Firm Label`, `Voice/Notice Body`, `Voice/Micro Meta`.

Visual proof:

- Screenshot checks were performed for all three root frames and inspected locally.
- `00 Design Map` was rebuilt after the first screenshot found clipped text.
- `02 Artifacts` was polished after the first screenshot found narrow-card wrapping in compound titles.
- Final inspected roots: `6:2`, `7:2`, `9:2`.

Known remaining Figma-side limitation:

- The code font families `Unbounded` and `Space Grotesk` are available in Figma.
- The current DSF text styles are named as voice roles, but the style/font upgrade from Inter to those code fonts was blocked by bj Starter's MCP tool-call limit after the DSF was already built.
- This is a typography-fidelity gate for a future Figma touch-up, not a code implementation blocker.

Important boundary:

- Figma should own visual design truth when used.
- Code still owns runtime behavior, data flow, generated visuals, accessibility implementation, and interaction fidelity.
- The live style guide remains the implementation proof and part of the finished code deliverable.

## Surface Gate Update

Latest user decision: skip Figma.

Active finish line:

- code / live style-guide proof from `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`

Parked finish line:

- Figma DSF v1 in `bj`; do not spend more tool or review time there unless the user reopens Figma.

## Requirement Audit

| Requirement | Status | Evidence / Missing Proof |
|---|---|---|
| get Design Lab skill to finish line | done for current iteration | skill validates; commits through `e4921d9` |
| test it on real project | done for code/style-guide track | `desci-world-bangalore-code-gpthigh` at `fa990bc` |
| run multiple model attempts | partial | low/high code done; Minimax code attempted but failed/incomplete |
| compare attempts | done in this report | Attempt Matrix |
| produce code/live style-guide finish line | done pending user Finish Gate | `/style-guide` on high branch |
| produce Figma finish line | gate-parked by latest user instruction | bj file `z4ROGt453f8rB0wz24MerQ` exists as historical pilot evidence; skip Figma for active review |
| verify winning implementation | done | build plus browser checks |
| call whole goal complete | pending user Finish Gate | active code/style-guide track has implementation proof; user acceptance still needed |

## Recommended Next Moves

1. User reviews the live style guide at `/style-guide` and accepts, continues, or pauses the code/style-guide Finish Gate.
2. Use the high code branch as the implementation baseline if accepted.
3. Decide whether to merge/apply `design-lab-code-gpthigh` into the main repo.
4. Either clean or discard the dirty Minimax worktree after preserving this report.

## Finish Gate State

Current gate decision: `review`

Reason: the user asked to skip Figma, so the active review target is the high code/style-guide branch. The remaining decision is whether the user accepts the live style guide and high code branch as the pilot finish line.
