---
name: model-taste
description: Choose an unspecified model or reasoning effort, using live availability first and the dated roster for capability, fit, and cost judgment.
---

# Model taste

Use this skill when a workflow needs a model or effort the user has not specified. Preserve any explicit choice while selecting the remaining dimension. Inspect the live catalog and advertised tool or harness overrides first; availability is environment truth, while the roster is judgment, not an availability cache. Use `cockpit agents options --json` for live route availability and [cockpit-agents](../cockpit-agents/SKILL.md) for session dispatch.

Choose model class and reasoning effort separately. Use the smallest sufficient class: small for bounded extraction and mechanical work, standard for ordinary implementation and review, and frontier when difficult judgment, ambiguity, or high-stakes quality earns it. Pick effort to match the uncertainty and stakes; do not infer capability from effort. Keep provider/model selection separate from the transport or harness (acpx, native CLI, Codex, OpenCode, Hermes, or another compatible surface).

Read the [model roster](references/roster.md) when the task needs a concrete provider/model fit, comparative cost judgment, or a dated cost/access fact. Its claims are dated snapshots, not newly verified prices. Check the record’s date and source before a material spending decision.

## Completion

The selection is complete when the chosen model, effort, route, fit rationale, and any availability or cost uncertainty are explicit, with the user’s choice preserved when present.

<!-- Roster facts are source-dated snapshots and are intentionally not recertified on every use. -->
