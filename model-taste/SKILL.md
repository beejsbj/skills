---
name: model-taste
description: Choose a model and reasoning effort when the user has not already selected them, using live availability first and the dated roster for capability, fit, and cost judgment.
---

# Model taste

Use this skill when a workflow needs model or effort selection and the user has not already made that choice. An explicit user choice wins. Inspect the live catalog and advertised tool or harness overrides first; availability is environment truth, while the roster is judgment, not an availability cache. On bjslab, resolve `cockpit handbook bjslab capabilities/t3-code.md` before choosing a route.

Choose model class and reasoning effort separately. Use the smallest sufficient class: small for bounded extraction and mechanical work, standard for ordinary implementation and review, and frontier when difficult judgment, ambiguity, or high-stakes quality earns it. Pick effort to match the uncertainty and stakes; do not infer capability from effort. Keep provider/model selection separate from the transport or harness (acpx, native CLI, Codex, OpenCode, Hermes, or another compatible surface).

Read the [model roster](references/roster.md) when the task needs a concrete provider/model fit, comparative cost judgment, or a dated cost/access fact. Its claims are dated snapshots, not newly verified prices.

## Completion

The selection is complete when the chosen model, effort, route, fit rationale, and any availability or cost uncertainty are explicit, with the user’s choice preserved when present.

<!-- Roster mechanically extracted from acpx/profiles.json at a61711341e40d9287c4c6e0c7dbaeb0415388a0e; source-dated facts are intentionally not recertified. -->
