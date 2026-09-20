---
name: jev
description: Use Jev for bounded semantic judgments, or build Jev into an application, pipeline, runbook, or agent workflow. Routes immediate Choice/Score/Noul calls through the jevon CLI and implementation work to the official TypeSafe SDK and patterns.
---

# Jev

Route by the work requested:

- **Use:** judge supplied evidence now, classify records, rank supplied candidates,
  or call Jev from an agent/runbook. Read [use.md](references/use.md) and invoke
  the upstream `jev` CLI from [jevon](https://github.com/douglance/jevon).
- **Build:** design or change a repeatable integration. Read
  [build.md](references/build.md), then the current official TypeSafe skill and
  relevant SDK/pattern documentation linked there. Put domain questions and
  decision policy with the workflow that owns them. This includes writing a
  scheduled shell pipeline; its implementation can call the CLI in the use guide.
- **Both:** use the CLI to test a proposed rubric on representative evidence,
  then implement the validated stage with the CLI or SDK that fits its caller.

A pipeline does not need to become an application to use an SDK. A scheduled
script can invoke a CLI. Undertext can mix both across stages. Choose based on
the caller, data flow, and deployment; there is no required shared runtime.

Keep exact lookup, parsing, arithmetic, clocks, permissions, and execution in
ordinary code. Jev supplies typed judgments about provided state; probabilities
are signals, not authority to act. Use a generative model for prose/code creation
and an audio model for raw sound interpretation.

On bjslab, `jev` is upstream jevon with a small credential launcher in this skill.
The earlier `Projects/jev` implementation is a preserved reference, not a
dependency for new work. Its `jev evaluate` contract is different; use
`jev-legacy evaluate` only when maintaining those existing examples.

Provider reference: [official TypeSafe skill](https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md).
CLI reference: [douglance/jevon](https://github.com/douglance/jevon).
