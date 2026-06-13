# Desci World Bangalore Figma Build Packet

Date: 2026-06-13

## Purpose

This packet prepares and records the Figma Design System File (DSF) creation step for the Design Lab pilot on `/Users/burooj/Projects/desci-world-bangalore`.

It is not the DSF itself. It captures the intended full DSF plan, the actual bj Starter-compatible adaptation, and the verification proof for the file that was created.

Recommended file name:

- `World of DeSci Bengaluru - Design Lab System`

## Creation Gate And Result

Figma auth returned multiple plans. The user first selected `Burooj's Figma`; that plan key failed. The user then instructed not to use `Burooj's Figma` and to use `bj`.

Writable-looking choices:

- `Alpha4`
- `API3`
- `Burooj's Figma`
- `bj`

View-only:

- `Burooj's Starter team`

Failed target:

- `Burooj's Figma`
- returned key: `team::1374441460972845906`

Creation attempts:

- `create_new_file` with `team::1374441460972845906` failed as `Invalid planKey`.
- `create_new_file` with `team:1374441460972845906` failed schema validation because the tool requires `team::...`.
- Local Figma app Computer Use fallback timed out while reading app state.
- `create_new_file` with `team::1376350914758657423` for `bj` succeeded.

Final target:

- team: `bj`
- plan key: `team::1376350914758657423`
- file key: `z4ROGt453f8rB0wz24MerQ`
- file URL: `https://www.figma.com/design/z4ROGt453f8rB0wz24MerQ`

Starter-plan adaptations:

- `bj` allows only three pages, so the generated system was compressed into three pages.
- `bj` allows only one local variable mode, so day/night theme modes are represented as explicit `/day` and `/night` variables and swatches.
- The original seven-page plan remains below as the full-shape target for a non-Starter file.

Final created pages:

1. `00 Design Map`
2. `01 Foundations`
3. `02 Artifacts`

Root frames:

| Page | Root Frame | Size | Role |
|---|---|---:|---|
| `00 Design Map` | `6:2` | 1440 x 1260 | methodology mirror, doctrine, gates/audits, code map, ownership boundary |
| `01 Foundations` | `7:2` | 1440 x 1395 | compressed Source Map plus tokens |
| `02 Artifacts` | `9:2` | 1440 x 2290 | primitives, unique specimens, compounds, compositions, inline Anatomy |

Created Figma foundations:

| Kind | Count / Names |
|---|---|
| variable collections | `Color` 15 vars, `Spacing` 18 vars, `Geometry` 3 vars, `Motion` 3 vars |
| local variables | 39 |
| text styles | `Voice/Booming Poster`, `Voice/Loud Section`, `Voice/Firm Label`, `Voice/Notice Body`, `Voice/Micro Meta` |

Visual verification:

- Screenshots were taken and inspected for all root frames.
- `00 Design Map` was rebuilt after first-pass clipping.
- `02 Artifacts` was polished after first-pass narrow-card wrapping.
- Final inspected root frame IDs: `6:2`, `7:2`, `9:2`.

Known remaining Figma-side limitation:

- `Unbounded` and `Space Grotesk` are available in the Figma font list.
- The DSF text styles were created as voice-role styles, but the final font-family upgrade from Inter to the code fonts failed because bj reached its Starter MCP tool-call limit.
- Treat this as a future typography-fidelity touch-up. Code remains the runtime typography source of truth.

## Source Inputs

Winning code/style-guide branch:

- worktree: `/Users/burooj/Projects/desci-world-bangalore-code-gpthigh`
- branch: `design-lab-code-gpthigh`
- head: `9fd5054 Represent day-night theme contract`
- implementation commit: `71e10c3 Add Design Lab style guide proof`
- proof route: `http://127.0.0.1:3005/style-guide`
- LAN proof route while dev server is running: `http://192.168.0.37:3005/style-guide`

Key source files:

- `docs/design-lab/DESIGN_MAP.md`
- `docs/design-lab/TAXONOMY_SCHEMA.md`
- `docs/design-lab/RAW_RECIPE_INVENTORY.md`
- `docs/design-lab/ANATOMY.md`
- `docs/design-lab/STYLE_GUIDE_PLAN.md`
- `assets/styles/colors.css`
- `assets/styles/settings.css`
- `assets/styles/typography.css`
- `assets/styles/components.css`
- `assets/styles/utilities.css`
- `components/EventRow.vue`
- `components/SpeakerCard.vue`
- `components/Header.vue`
- `components/Footer.vue`
- `components/RegisterNow.vue`
- `components/ToggleLight.vue`
- `components/RightArrow.vue`
- `components/LotusPath.vue`
- `components/ChakraDecoration.vue`
- `components/StarDecoration.vue`
- `public/images/*`

## Required Figma Skills And Tool Order

Before any tool calls:

1. Load `figma:figma-create-new-file`.
2. Use `whoami` only if the user did not provide a plan key.
3. Call `create_new_file` only after the user chooses the plan.
4. Load `figma:figma-use`.
5. Load `figma:figma-generate-library`.
6. Read `figma-use/references/plugin-api-standalone.index.md`.
7. Read `figma-use/references/working-with-design-systems/wwds.md`.
8. For variable creation, read variable-specific refs before scripting.
9. For component creation, read component-specific refs before scripting.

Use `use_figma` incrementally. Do not build the whole DSF in one script.

## Intended Full Figma File Page Structure

Use this exact page order in a file that supports the full page count:

1. `00 Design Map`
2. `01 Source Map`
3. `02 Tokens`
4. `03 Primitives`
5. `04 Unique Specimens`
6. `05 Compounds`
7. `06 Compositions`

Anatomy lives inline beside the artifact it explains. Do not create a separate Anatomy page.

In the bj Starter-compatible result, the same structure is compressed as:

- `00 Design Map`: `00 Design Map`.
- `01 Foundations`: `01 Source Map` plus `02 Tokens`.
- `02 Artifacts`: `03 Primitives`, `04 Unique Specimens`, `05 Compounds`, and `06 Compositions`.

## DSF Ownership Boundary

Figma owns:

- visual design truth for accepted tokens
- visual component anatomy
- component-set representations of primitives and compounds
- static composition proofs
- source-map/reference material

Code owns:

- runtime behavior
- data flow
- Fitty sizing
- GSAP splash behavior
- theme mutation
- hover/focus implementation fidelity
- accessibility implementation
- final production components

The live style guide remains implementation proof, not the Figma visual source of truth.

## Phase 0: Discovery And Scope Lock

Before creating nodes:

- inspect the new blank file
- create or reconstruct a state ledger
- lock v1 scope to the focused pilot scope
- treat orange/day and neon/night as one canonical theme system
- keep individual lotus/city assets on `01 Source Map` until classified as unique specimens or composition material

State ledger:

- suggested path: `/tmp/design-lab-dsf-desci-world-bangalore-2026-06-13.json`
- run id: `design-lab-desci-world-bangalore-2026-06-13`

Ledger must track:

- file key and URL
- pages
- sections
- variable collections
- variables
- text styles
- effect styles
- components
- validation screenshots
- pending behavior probes

User checkpoint:

- confirm DSF scope before Phase 1.

## Phase 1: Foundations

Create variables before components.

### Variable Collections

Recommended collections:

| Collection | Modes | Purpose |
|---|---|---|
| `Primitives` | `Value` | hard values and reference colors |
| `Color` | `Light`, `Dark` | mode-aware semantic colors mirroring `--hue` behavior |
| `Spacing` | `Mobile 320`, `Desktop 1600` | Figma numeric snapshots for CSS `clamp()` space tokens |
| `Typography` | `Mobile 320`, `Desktop 1600` | Figma numeric snapshots for CSS `clamp()` type tokens |
| `Geometry` | `Value` | line width, radius, clip/radius notes |
| `Motion` | `Value` | placeholders only; actual behavior remains code-owned |

### Color Variables

Figma cannot represent CSS `hsl(calc(var(--hue) + ...))` dynamically. Create `Color` modes from the accepted mode snapshots:

| Token | Light | Dark | Code Syntax |
|---|---|---|---|
| `color/black` | `#030303` | `#030303` | `var(--black)` |
| `color/white` | `#FCFAF7` | `#FAFCF7` | `var(--white)` |
| `color/paper` | `#FCFAF7` | `#FAFCF7` | `var(--paper)` |
| `color/ink` | `#030303` | `#030303` | `var(--ink)` |
| `color/accent` | `#FB9637` | `#B0FB37` | `var(--color)` |
| `color/accent-light` | `#FCB069` | `#C4FC69` | `var(--color-light)` |
| `color/accent-darkest` | `#E16F05` | `#8CE105` | `var(--color-darkest)` |
| `color/highlight` | `#3D40F5` | `#DF3DF5` | `var(--highlight)` |
| `color/highlight-darker` | `#0A0DC2` | `#AC0AC2` | `var(--highlight-darker)` |
| `color/tertiary` | `#5A8712` | `#128733` | `var(--tertiary-color)` |
| `color/success` | `#5AF25F` | `#5AF25F` | `var(--success)` |
| `color/warning` | `#F2C95A` | `#F2C95A` | `var(--warning)` |
| `color/error` | `#F25A5A` | `#F25A5A` | `var(--error)` |

Semantic aliases:

- `surface/page` -> `color/paper`
- `surface/inverse` -> `color/ink`
- `text/default` -> `color/ink`
- `text/inverse` -> `color/paper`
- `action/bg` -> `color/ink`
- `action/text` -> `color/paper`
- `action/accent` -> `color/accent`
- `border/default` -> `color/ink`
- `border/on-dark` -> `color/paper`

### Spacing Variables

CSS source uses clamp. Figma should expose two numeric modes:

| Token | Mobile 320 | Desktop 1600 | Code Syntax |
|---|---:|---:|---|
| `space/3xs` | 4 | 5 | `var(--space-3xs)` |
| `space/2xs` | 8 | 9 | `var(--space-2xs)` |
| `space/xs` | 12 | 14 | `var(--space-xs)` |
| `space/s` | 16 | 18 | `var(--space-s)` |
| `space/m` | 24 | 27 | `var(--space-m)` |
| `space/l` | 32 | 36 | `var(--space-l)` |
| `space/xl` | 48 | 54 | `var(--space-xl)` |
| `space/2xl` | 64 | 72 | `var(--space-2xl)` |
| `space/3xl` | 96 | 108 | `var(--space-3xl)` |

### Typography Styles

Create text styles named after voice utilities:

| Style | Family | Size Token | Weight | Line Height | Code Syntax |
|---|---|---|---|---|---|
| `voice/booming` | Unbounded | `--step-4` | 700 | default | `.booming-voice` |
| `voice/loud` | Unbounded | `--step-4` | 700 | heading | `.loud-voice` |
| `voice/attention` | Space Grotesk | `--step-3` | 400 | heading | `.attention-voice` |
| `voice/firm` | Unbounded | `--step-2` | 700 | heading | `.firm-voice` |
| `voice/notice` | Space Grotesk | `--step-2` | 400 | body | `.notice-voice` |
| `voice/calm` | Space Grotesk | `--step-0` | 400 | body | `.calm-voice` |
| `voice/solid` | Unbounded | `--step--1` | 700 | body | `.solid-voice` |
| `voice/micro` | Space Grotesk | `--step--2` | 400 | body | `.micro-voice` |

If Unbounded or Space Grotesk is unavailable in Figma, stop and record a font availability gate rather than silently replacing the style.

### Geometry And Effects

Create:

- `stroke/line-width` = 2, code syntax `var(--line-width)`
- `radius/corners` = 16, code syntax `var(--corners)`
- `border/ghost` as a documented style, code syntax `var(--border-ghost)`
- `effect/shadow/poster` from `--shadow`, code syntax `var(--shadow)`

Do not attempt to encode `--clip-path` as a generic reusable Figma token in v1. Document it on `02 Tokens` as a code-owned geometry recipe.

Exit proof:

- variable summary
- text style summary
- screenshot of `02 Tokens`

User checkpoint:

- approve foundations before building components.

## Phase 2: File Structure And Documentation Frames

Create page skeleton:

- `00 Design Map`: Doctrine Compass, taxonomy loop, ownership boundary
- `01 Source Map`: repo source cards, style-guide proof screenshot slot, day/night assets, source-map material
- `02 Tokens`: color swatches, spacing bars, type voice rows, geometry/effect notes
- `03 Primitives`: button, text link, theme toggle, right arrow, pattern fields
- `04 Unique Specimens`: lotus path, splash behavior boundary, chakra, star, hero/city assets
- `05 Compounds`: EventRow, SpeakerCard, Header, Footer, RegisterNow
- `06 Compositions`: home page structure, hero region, event region, speaker/register/footer regions

Each page should have a compact top strip:

- layer name
- source-of-truth statement
- accepted / theme-source / code-probe badges

## Phase 3: Primitives

Build one primitive at a time.

### Button

Represent:

- Default
- Hover/focus static snapshot

Properties:

- `Label` text property
- `State` variant: `Default`, `Hover`

Bindings:

- background -> `action/bg`
- text -> `action/text`
- spacing/radius -> spacing and radius variables

Boundary:

- arrow sweep animation is a code probe, not fully represented by Figma.

### Text Link

Represent:

- Default
- Hover/focus underline snapshot

Properties:

- `Label`
- `State`

Boundary:

- pseudo-element underline behavior remains code-owned.

### ToggleLight

Represent:

- `Theme=Light`
- `Theme=Dark`
- `State=Default`
- `State=Active` optional static pose

Boundary:

- theme mutation and tremble animation are code-owned.

### RightArrow

Represent:

- default chevron
- hover shifted snapshot

Boundary:

- SVG source is code-owned in `RightArrow.vue`.

### Pattern Fields

Represent as local pattern cards:

- `.points`
- `.points-white`
- `.checkers`
- `.diagnol` (preserve repo spelling)

Boundary:

- data URI pattern definitions remain code-owned in `settings.css`.

## Phase 4: Unique Specimens

Do not create component sets with standard variant axes. Use singular cards with inline Anatomy.

Cards:

- `LotusPath`
- `SpashAnimation` behavior boundary
- `ChakraDecoration`
- `StarDecoration`
- `Hero image artifacts`
- `Night-mode lotus-city source material`

Each card includes:

- source file/path
- why singular
- allowed local variations
- forbidden promotion
- code probe requirement if behavior-heavy

For asset-heavy cards, use placed image thumbnails where possible. If image import is not available, create reserved frames with source path labels and mark them as asset slots.

## Phase 5: Compounds

Build compounds in dependency order:

1. `EventRow`
2. `SpeakerCard`
3. `Header`
4. `RegisterNow`
5. `Footer`

### EventRow

Source:

- `components/EventRow.vue`

Parts:

- day
- start time
- name
- location
- RightArrow child

Properties:

- text properties for day, time, name, location
- optional `Has Link` boolean

Bindings:

- gap -> `space/l`
- divider -> `border/ghost`
- arrow uses RightArrow primitive

### SpeakerCard

Source:

- `components/SpeakerCard.vue`

Parts:

- circular image
- speaker name
- company
- role

Properties:

- `Name`
- `Company`
- `Role`
- image slot placeholder

Boundary:

- content source remains Nuxt Content JSON.

### Header

Source:

- `components/Header.vue`

Parts:

- nav links
- ToggleLight child

Boundary:

- in-page anchor behavior and theme mutation are code-owned.

### RegisterNow

Source:

- `components/RegisterNow.vue`

Parts:

- heading
- CTA list

Boundary:

- external Airtable links are content/config, not visual variants.

### Footer

Source:

- `components/Footer.vue`

Parts:

- nav groups
- social links
- ToggleLight child
- optional splash unique child

Represent:

- `showSplash=false` proof variant
- annotation for `showSplash=true` runtime behavior

Boundary:

- SpashAnimation remains unique behavior specimen.

## Phase 6: Compositions

Static composition frames:

- `Home Page Flow`
- `Hero Poster Region`
- `Event Section`
- `Speaker Section`
- `Register Section`
- `Footer Region`

Do not recreate the whole site as a marketing redesign. These frames prove the grammar and reveal gaps.

Expected composition feedback loop:

- repeated event row already promoted to `EventRow`
- singular hero image treatment remains unique/composition-local
- no new reusable primitives should be introduced without Promotion Gate

## Behavior Fidelity Boundaries

| Artifact | Figma Proof | Code Probe |
|---|---|---|
| ToggleLight | static light/dark/active poses | data-theme mutation and tremble |
| SpashAnimation | static lotus path card and sequence notes | GSAP path draw, page reveal, global overflow/opacity mutation |
| HeroLanding | static hero frame | Fitty-driven poster scaling |
| Button | static default/hover state | arrow sweep pseudo background |
| Pattern fields | static pattern samples | data URI source exactness |

## Finish Proof For Figma Track

Figma track is complete for the bj Starter-compatible v1 when the Finish Gate names:

- DSF URL
- file key
- created page names
- variable collection counts
- artifact groups and Anatomy coverage
- Source Map coverage
- behavior boundaries
- implementation pass status
- unresolved gates

Current v1 proof:

- DSF URL: `https://www.figma.com/design/z4ROGt453f8rB0wz24MerQ`
- file key: `z4ROGt453f8rB0wz24MerQ`
- pages: `00 Design Map`, `01 Foundations`, `02 Artifacts`
- root frames: `6:2`, `7:2`, `9:2`
- `01 Foundations` has Source Map evidence plus color, spacing, type, geometry/effect, and motion-boundary docs
- `02 Artifacts` covers button, text link, toggle, arrow, pattern fields, lotus/splash/chakra/star/hero media, EventRow, SpeakerCard, Header, RegisterNow, Footer, and home-page composition
- `00 Design Map` mirrors the Design Lab doctrine, ownership boundary, gates/audits, code map, and Starter adaptation
- orange/day and neon/night are both represented as canonical theme modes
- individual lotus-city assets are not accidentally promoted into reusable primitive families
- behavior boundaries are called out inline for ToggleLight, SpashAnimation, HeroLanding/Fitty, button hover sweep, and pattern data URIs
- typography font-family fidelity is gate-parked behind bj MCP tool-call availability

## First Tool Calls After User Chooses Team

1. `create_new_file`:
   - `editorType`: `design`
   - `fileName`: `World of DeSci Bengaluru - Design Lab System`
   - `planKey`: chosen team key

2. `use_figma` read-only inspection:
   - return file key, current pages, editor type, fonts available for Unbounded and Space Grotesk

3. `use_figma` setup call:
   - create page skeleton only
   - return all page IDs
   - write state ledger

Stop after page skeleton and ask for checkpoint approval before variable creation.

This section is retained as the reusable procedure. For this pilot, those calls have already happened against `bj`, with the Starter-compatible result recorded above.
