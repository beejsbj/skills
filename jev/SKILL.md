---
name: jev
description: Build or invoke TypeSafe Jev typed judgments through the shared library and CLI. Use for Choice, Score, Noul, dynamic candidate selection, or adapting semantic workflow decisions; generative prose and raw audio interpretation belong to other tools.
---

# Jev

The shared runtime is `/mnt/server-ssd/BJsWorkspace/Projects/jev` on bjslab.
`jev evaluate` is the JSON CLI; applications import `jev-foundation` from that
checkout. Both use one evaluator. This skill contains guidance, not a second runtime.

## Evaluate a supplied record

Read the runtime [README](../../jev/README.md) for its request and result
contract, or use the absolute source path above when a harness resolves symlinks
differently. Put state and independent Choice/Score/Noul questions in one JSON
request with `schema_version: 1` and a meaningful `rubric_version`.

```sh
jev evaluate --input /path/to/request.json --timeout-ms 10000
```

Live calls automatically try configured TypeSafe, then OpenRouter, using each
provider’s own key. On bjslab the installed `jev` launcher supplies the existing
OpenCodex OpenRouter key to the child environment when needed; fixture replay and
help do not read credentials. The portable Node CLI and library use
`TYPESAFE_API_KEY` / `OPENROUTER_API_KEY`. Obtain any missing access through the
authorized credential route; keep key values out of commands, receipts, and conversation.
Use `--provider typesafe|openrouter` only to restrict providers. Omit request
`model` for fallback; an explicit model restricts evaluation to its matching
provider. Auto falls back on provider access/unavailability within one deadline,
not invalid input, bad answers, capacity rejection, or cancellation. Handle
`ok: false` before reading answers; failure is not an unresolved judgment.
Receipts show provider attempts/errors, actual provider/model, rubric, evidence
hashes, latency, and available usage/cost without storing raw state.

For a reproducible public demonstration with all three primitives:

```sh
jev evaluate \
  --input /mnt/server-ssd/BJsWorkspace/Projects/jev/examples/synthetic.request.json \
  --fixture /mnt/server-ssd/BJsWorkspace/Projects/jev/examples/synthetic.fixture.json
```

The fixture is **hand-authored synthetic contract data, not live inference**. Report
its `source` and `fixture_kind`. It matches only the supplied example's state,
questions, and model; it cannot judge a different record. To test that record live,
omit `--fixture`. For OpenRouter offline replay use
`examples/synthetic.openrouter.fixture.json` in the same runtime checkout. Auto
replay selects the fixture’s recorded provider independently of configured keys;
an explicit provider override must match it.
If `jev` is unavailable, invoke
`node /mnt/server-ssd/BJsWorkspace/Projects/jev/dist/cli.js` with the same arguments;
build/setup steps live in the runtime README.

## Build or adapt a workflow

Read the current [official TypeSafe skill](https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md)
before designing an integration; follow its live documentation links for the
relevant primitives and cookbook. It is the canonical provider reference.
The runtime's `docs/provider-contract.md` records its pinned SDK/model and limits;
changing versions requires refreshing validation and fixtures together. Consult
that contract for OpenRouter’s supported model identities, rounded answers, and
criteria restrictions before adapting a direct TypeSafe request.

Use `examples/synthetic.mjs` in the runtime for executable dynamic candidates and
an explicit unresolved outcome. Code owns exact IDs, evidence retrieval, arithmetic,
actions, and clocks. Jev supplies typed judgments. An application can use those
judgments to decide whether a generative agent is needed.

Independent questions see the same state and cannot see one another's answers.
When one answer determines new evidence or candidates, build a subsequent request
in code. Callers own semantic chunking; the evaluator sends complete evidence and
returns explicit capacity failures. Keep Choice and Score distributions, Score's
fractional meaning, and Noul's probability of yes; Noul has no separate confidence.

Official sources: [TypeSafe agent skill](https://docs.typesafe.ai/agent-skill),
[API](https://docs.typesafe.ai/api), [patterns](https://docs.typesafe.ai/patterns),
[OpenRouter SDK compatibility](https://openrouter.ai/docs/guides/community/typesafe-sdk).
Community design reading: [Drew Breunig's Jev skill](https://github.com/dbreunig/building-with-jev-skill).
No community code or text is vendored here.
