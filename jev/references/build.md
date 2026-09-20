# Build with Jev

Read the current [official TypeSafe skill](https://raw.githubusercontent.com/typesafe-ai/skills/main/skills/typesafe-ai/SKILL.md)
before designing an integration. Follow its links to the relevant SDK, primitive,
and cookbook. This file describes local integration choices; provider docs own
the API contract.

## Choose the call boundary

Use [the CLI](use.md) for shell pipelines, agent tools, and runbook steps. Read its
JSON response and check success before applying policy. Existing Python or
JavaScript code can use the official SDK directly for structured state, reusable
clients, and composition. Both are valid in workflows such as Undertext; neither
needs the old `jev-foundation` package. Introduce shared helpers only when actual
callers need the same behavior.

The workflow owns its evidence, questions, candidate IDs, thresholds, error
handling, and actions. Keep deterministic work in code. Test semantic judgments
against representative labeled examples before replacing an existing LLM stage.
Measure the errors that matter to that workflow, alongside latency and cost.

Use Choice for one option from a supplied set, independent Noul questions for
multiple applicable tags, and Score for position along ordered criteria. Include
an explicit no-match option where needed. Preserve distributions and unresolved
outcomes; a missing/failed answer is not a negative answer. Confidence needs
calibration on the workflow's data, not a universal cutoff.

Independent questions in one call share state but cannot inspect each other's
answers. When an answer determines evidence or candidates, construct the next
stage in code. Fan out across semantic chunks when appropriate, retain source
IDs, and merge with explicit policy. Splitting changes the context available to
each judgment; evaluate that loss as well as throughput.

## JavaScript example

Install `@typesafe-ai/sdk` in the consuming project. This example uses an existing
environment key; it does not read a host credential store. For local execution
with the bjslab credential launcher, see `use.md` instead. SDK/API details were
checked with JavaScript SDK 0.6.0 on 2026-09-20; check current docs when upgrading.

Save as an `.mjs` file and run with Node:

```js
import { TypeSafeClient, choice, noul } from '@typesafe-ai/sdk';

const directKey = process.env.TYPESAFE_API_KEY?.trim();
const routerKey = process.env.OPENROUTER_API_KEY?.trim();
if (!directKey && !routerKey) throw new Error('A Jev provider key is required');

const client = new TypeSafeClient(directKey
  ? { apiKey: directKey, baseURL: 'https://api.typesafe.ai', defaultModel: 'jev-1.13.0' }
  : { apiKey: routerKey, baseURL: 'https://openrouter.ai/api', defaultModel: 'typesafe/jev-1.13' });

const result = await client.systemOne({
  state: { request: 'I was charged twice for my subscription.' },
  questions: {
    topic: choice('Which topic best matches the request?', {
      billing: 'Charges, invoices, refunds, or duplicate payment',
      account: 'Login, profile, or access',
      other: 'No supplied topic fits',
    }),
    duplicate_charge: noul('Does the person report being charged twice?'),
  },
});

console.log(JSON.stringify(result));
```

This chooses a configured provider; it does not retry across providers. Add
failover only if the workflow needs it, with bounded retries and explicit error
policy. Keep credentials server-side and out of command arguments or logs.
OpenRouter's SDK compatibility base is `/api`, because the SDK appends
`/v1/systemone`; the regular chat-completions interface is not this API.

## Patterns to reach for

- Undertext/content: chunk judgments, glint/thread candidates, relations, ranking,
  and source selection; generative synthesis remains a separate stage.
- Handbook/Cockpit/job search: supply current candidates and evidence, judge fit
  or relevance, then let the workflow execute its authorized next step.
- Grimmory: judge metadata and genre candidates; use exact code for file identity,
  copying, torrent state, and elapsed seeding time.

These are integration directions, not verified migrations. Start with one bounded
stage and compare its outcomes to the existing workflow.

References: [JavaScript SDK](https://docs.typesafe.ai/sdk/javascript),
[Python SDK](https://docs.typesafe.ai/sdk/python),
[fan-out](https://docs.typesafe.ai/patterns/fan-out),
[parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions),
[intent routing](https://docs.typesafe.ai/patterns/intent-routing),
[OpenRouter SDK compatibility](https://openrouter.ai/docs/guides/community/typesafe-sdk).
