# Desci World Bangalore Pilot

Date: 2026-06-13

## Goal

Use Design Lab on `/Users/burooj/Projects/desci-world-bangalore` as a real-project pilot, with multiple attempts across model strength and finish-line type:

- code / live style-guide finish line
- Figma Design System File finish line
- low-think GPT 5.5
- high-think GPT 5.5
- Minimax M3

## Current Verdict

The code / live style-guide finish line has a clear winning attempt.

The Figma Design System File finish line is not complete because file creation is still gated on the user choosing a Figma team/project. Planning attempts produced useful structure, but no editable Figma file exists yet.

## Attempt Matrix

| Track | Attempt | Workspace / Session | Result | Evidence |
|---|---|---|---|---|
| code/style-guide | GPT 5.5 low | `/Users/burooj/Projects/desci-world-bangalore-code-gptlow`, branch `design-lab-code-gptlow`, commit `d787697` | shallow proof; useful but not winner | 7 changed files, `pages/style-guide.vue`, partial `docs/design-lab` artifacts; build not verified because deps were missing |
| code/style-guide | GPT 5.5 high | `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`, branch `design-lab-code-gpthigh`, head `f82c0ec` | winner | 18 changed files, full artifact set, `EventRow.vue` extraction, `Footer.vue` proof prop, verified build/browser |
| code/style-guide | Minimax M3 | `/Users/burooj/Projects/desci-world-bangalore-code-minimax`, branch `design-lab-code-minimax` | failed/incomplete; useful failure signal | dirty partial extraction plus unwanted `package.json` package-manager field; no style guide, docs, verification, or commit |
| Figma DSF | GPT 5.5 low | native subagent plan | plan only | no Figma file created; blocked by Surface Gate team choice |
| Figma DSF | GPT 5.5 high | native subagent plan | stronger plan only | no Figma file created; blocked by Surface Gate team choice |
| Figma DSF | Minimax M3 | opencode session `ses_13dd0a90dffeBbRv9le3lQ8TQo` | concrete plan only | session title `Design-lab Figma finish-line plan`; no files changed; no Figma file created |

## Winning Code Attempt

Recommended baseline:

- `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`
- branch `design-lab-code-gpthigh`
- head `f82c0ec Record Design Lab verification side effects`
- implementation commit `71e10c3 Add Design Lab style guide proof`
- route `http://127.0.0.1:3005/style-guide`

What it did:

- Added `pages/style-guide.vue` as a live proof surface.
- Extracted `components/EventRow.vue` from `components/EventSection.vue`.
- Updated `components/Footer.vue` with a `showSplash` prop so the footer can be demonstrated without firing the singular splash behavior.
- Added the focused full-workflow methodology set under `docs/design-lab/`.
- Kept neon lotus-city material deferred behind a Taste Gate.

Verification recorded in `docs/design-lab/RESIDUE_PROOF.md`:

- `COREPACK_ENABLE_AUTO_PIN=0 yarn install --frozen-lockfile` completed.
- `COREPACK_ENABLE_AUTO_PIN=0 yarn build` exited 0.
- Browser desktop check: `/style-guide` loaded with token, primitive, unique specimen, compound, and composition sections; no horizontal overflow; no page console warnings/errors.
- Browser mobile check at 390px: no horizontal overflow, no visible out-of-bounds candidates, no page console warnings/errors.

Main-thread spot check repeated the route after restarting stale Nuxt dev state:

- `curl -I http://127.0.0.1:3005/style-guide` returned 200.
- Browser check found `EventRow` and `Footer`, no mounted splash proof behavior, no horizontal overflow, and no console errors.

## Merge Readiness

Current winning head:

- `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`
- branch `design-lab-code-gpthigh`
- head `f82c0ec`

Readiness checks:

- `git diff --check master..design-lab-code-gpthigh` passed.
- `git merge-tree $(git merge-base master design-lab-code-gpthigh) master design-lab-code-gpthigh` showed no conflict markers or both-sides conflicts.
- `COREPACK_ENABLE_AUTO_PIN=0 yarn build` passed from the high worktree after the verification-side-effect doc update.
- Main repo state remains `master` with only pre-existing untracked `dist 2`.

Build warnings still present:

- Node `DEP0180` fs.Stats deprecation warning.
- Browserslist `caniuse-lite` is outdated.
- Vite CSS warning for existing `align-items: start`.
- Nuxt Content JSON-array warnings for `content/events.json` and `content/speakers.json`.

Merge gate:

- Do not merge automatically. User should accept the code/style-guide Finish Gate or ask to apply the high branch to main.

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

Figma is available, but actual creation is gated.

Known accessible plans from Figma auth:

- `Alpha4`
- `API3`
- `Burooj's Figma`
- `bj`
- `Burooj's Starter team` is view-only

Because more than one writable plan exists, Figma file creation must wait for the user to choose the team/project. Until then, the Figma attempts are planning evidence only.

Prepared creation packet:

- `design-lab/pilots/desci-world-bangalore-figma-build-packet-2026-06-13.md`

Recommended first file structure once the gate is opened:

- `00 Design Map`
- `01 Source Map`
- `02 Tokens`
- `03 Primitives`
- `04 Unique Specimens`
- `05 Compounds`
- `06 Compositions`

Important boundary:

- Figma should own visual design truth when used.
- Code still owns runtime behavior, data flow, generated visuals, accessibility implementation, and interaction fidelity.
- The live style guide remains the implementation proof and part of the finished code deliverable.

## Requirement Audit

| Requirement | Status | Evidence / Missing Proof |
|---|---|---|
| get Design Lab skill to finish line | done for current iteration | skill validates; commits through `e4921d9` |
| test it on real project | done for code/style-guide track | `desci-world-bangalore-code-gpthigh` at `f82c0ec` |
| run multiple model attempts | partial | low/high code done; Minimax code attempted but failed/incomplete |
| compare attempts | done in this report | Attempt Matrix |
| produce code/live style-guide finish line | done pending user Finish Gate | `/style-guide` on high branch |
| produce Figma finish line | not done | blocked by Figma team/project choice |
| verify winning implementation | done | build plus browser checks |
| call whole goal complete | not yet | Figma finish line still gated; user acceptance pending |

## Recommended Next Moves

1. User chooses a Figma team/project.
2. Create the Figma Design System File using `desci-world-bangalore-figma-build-packet-2026-06-13.md`.
3. Use the high code branch as the implementation baseline.
4. Decide whether to merge/apply `design-lab-code-gpthigh` into the main repo.
5. Either clean or discard the dirty Minimax worktree after preserving this report.

## Finish Gate State

Current gate decision: `continue`

Reason: code/style-guide proof is strong enough to accept, but full original pilot goal included a Figma finish-line attempt, and no Figma file exists yet.
