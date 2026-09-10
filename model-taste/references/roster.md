# Model roster

This is the source-dated model judgment roster. Provider identifies the model family; harness/transport is selected separately. The records below preserve the original fields and cost metadata.

## Defaults and policy

- Default policy: explicit user model/effort choices win; inspect live availability and advertised overrides before consulting this roster.
- Default routing judgment: choose the smallest sufficient executor class and select effort independently.
- Availability is environment truth; this roster is not an availability cache.
- Cost claims are dated snapshots and must not be treated as newly verified prices.

## Records


### chatgpt — gpt-6-astra

- **provider:** `chatgpt`
- **model:** `gpt-6-astra`
- **executor_class:** `frontier`
- **good_for:** Highest-capability independent judgment: architecture, visual taste, ambiguous decisions, difficult diagnosis, and acceptance review.
- **avoid_for:** Mechanical execution, bulk work, or broad unattended autonomy without explicit bounds and a stopping condition.
- **default_effort:** `low`
- **cost:**

```json
{
  "relative": "unknown",
  "access": "Route-dependent; currently exposed through the bjslab T3/Codex OpenCodex catalog",
  "note": "Treat class and effort separately: low effort is the default for a bounded consultation, not a claim that Astra is a small model. Live harness availability outranks this roster.",
  "checked": "2026-09-09",
  "source": "cockpit handbook bjslab capabilities/t3-code.md"
}
```


### chatgpt — gpt-5.6-sol

- **provider:** `chatgpt`
- **model:** `gpt-5.6-sol`
- **executor_class:** `frontier`
- **good_for:** Frontier workhorse: hard implementation, architecture, difficult debugging, review, and long tool-heavy execution where both judgment and follow-through matter.
- **avoid_for:** Thin or ambiguous briefs, weak stop conditions, and cheap bulk work. Sol can be overeager: give it explicit success criteria, boundaries, validation, and a stopping condition before granting broad autonomy.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "premium",
  "access": "Codex/ChatGPT plan limits or OpenAI API",
  "api_usd_per_million_tokens": {
    "input": 5,
    "cached_input": 0.5,
    "cache_write": 6.25,
    "output": 30
  },
  "long_context_api_usd_per_million_tokens": {
    "input": 10,
    "cached_input": 1,
    "cache_write": 12.5,
    "output": 45
  },
  "note": "Standard API pricing; long-context eligibility/thresholds are model-specific. Codex subscription usage is plan-metered rather than billed at these API rates.",
  "checked": "2026-07-20",
  "source": "https://developers.openai.com/api/docs/pricing"
}
```


### chatgpt — gpt-5.6-terra

- **provider:** `chatgpt`
- **model:** `gpt-5.6-terra`
- **executor_class:** `standard`
- **good_for:** Balanced everyday workhorse: implementation, debugging, review, synthesis, and agentic work that needs strong intelligence without Sol's full cost.
- **avoid_for:** The hardest quality-first judgment where Sol earns its cost, or high-volume mechanical work where Luna is sufficient.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "mid",
  "access": "Codex/ChatGPT plan limits or OpenAI API",
  "api_usd_per_million_tokens": {
    "input": 2.5,
    "cached_input": 0.25,
    "cache_write": 3.125,
    "output": 15
  },
  "long_context_api_usd_per_million_tokens": {
    "input": 5,
    "cached_input": 0.5,
    "cache_write": 6.25,
    "output": 22.5
  },
  "note": "Standard API pricing; long-context eligibility/thresholds are model-specific. Codex subscription usage is plan-metered rather than billed at these API rates.",
  "checked": "2026-07-20",
  "source": "https://developers.openai.com/api/docs/pricing"
}
```


### chatgpt — gpt-5.6-luna

- **provider:** `chatgpt`
- **model:** `gpt-5.6-luna`
- **executor_class:** `small`
- **good_for:** Fast, affordable high-volume work: extraction, classification, bounded edits, routine scouting, and well-specified mechanical execution.
- **avoid_for:** Architecture, subtle debugging, ambiguous product judgment, or work whose context and dependencies exceed a tightly bounded brief.
- **default_effort:** `low`
- **cost:**

```json
{
  "relative": "low",
  "access": "Codex/ChatGPT plan limits or OpenAI API",
  "api_usd_per_million_tokens": {
    "input": 1,
    "cached_input": 0.1,
    "cache_write": 1.25,
    "output": 6
  },
  "long_context_api_usd_per_million_tokens": {
    "input": 2,
    "cached_input": 0.2,
    "cache_write": 2.5,
    "output": 9
  },
  "note": "Standard API pricing; long-context eligibility/thresholds are model-specific. Codex subscription usage is plan-metered rather than billed at these API rates.",
  "checked": "2026-07-20",
  "source": "https://developers.openai.com/api/docs/pricing"
}
```


### chatgpt — gpt-5.5

- **provider:** `chatgpt`
- **model:** `gpt-5.5`
- **executor_class:** `standard`
- **good_for:** Proven incumbent and compatibility fallback: familiar stewardship, implementation, debugging, synthesis, and tool-heavy coordination when its established behavior matters more than adopting 5.6.
- **avoid_for:** Treating it as the cheap fallback: its standard short-context API price matches Sol. Prefer Terra or Luna when cost is the reason, and Sol when frontier capability is the reason.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "premium",
  "access": "Codex/ChatGPT plan limits or OpenAI API",
  "api_usd_per_million_tokens": {
    "input": 5,
    "cached_input": 0.5,
    "output": 30
  },
  "long_context_api_usd_per_million_tokens": {
    "input": 10,
    "cached_input": 1,
    "output": 45
  },
  "note": "Standard API pricing; long-context eligibility/thresholds are model-specific. Keep for behavioral familiarity and compatibility, not a price advantage over Sol.",
  "checked": "2026-07-20",
  "source": "https://developers.openai.com/api/docs/pricing"
}
```


### claude — fable

- **provider:** `claude`
- **model:** `fable`
- **executor_class:** `frontier`
- **good_for:** Most ambitious long-running coding and knowledge work: large migrations, complex implementations, high-fidelity design work, deep research, and multi-day autonomous sessions that benefit from proactive planning, delegation, and self-verification.
- **avoid_for:** Routine work, cost-sensitive throughput, sensitive workloads that cannot accept 30-day retention, or ordinary security/debugging tasks likely to trip its stricter cyber classifier and route to Opus 4.8.
- **default_effort:** `high`
- **cost:**

```json
{
  "relative": "very-premium",
  "access": "Claude usage credits or Anthropic API",
  "api_usd_per_million_tokens": {
    "input": 10,
    "cached_input": 1,
    "output": 50
  },
  "note": "API model id: claude-fable-5. Fable requires 30-day data retention for safety monitoring; US-only inference is 1.1x. Anthropic positions it above Opus for ambitious, long-running asynchronous work.",
  "checked": "2026-07-20",
  "source": "https://www.anthropic.com/claude/fable"
}
```


### claude — opus

- **provider:** `claude`
- **model:** `opus`
- **executor_class:** `frontier`
- **good_for:** Deep architecture, hard review, ambiguous reasoning, high-stakes judgment.
- **avoid_for:** Routine extraction, simple edits, or low-risk cleanup.
- **default_effort:** `high`
- **cost:**

```json
{
  "relative": "premium",
  "access": "Claude plan quota or Anthropic API",
  "note": "The unversioned Claude CLI alias can move between model versions; consult live Anthropic pricing before estimating token cost.",
  "checked": "2026-07-20",
  "source": "https://docs.anthropic.com/en/docs/about-claude/pricing"
}
```


### claude — sonnet

- **provider:** `claude`
- **model:** `sonnet`
- **executor_class:** `standard`
- **good_for:** General implementation, review, debugging, and balanced code work.
- **avoid_for:** Tiny extraction tasks or problems needing the deepest available reasoning.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "mid",
  "access": "Claude plan quota or Anthropic API",
  "note": "The unversioned Claude CLI alias can move between model versions; consult live Anthropic pricing before estimating token cost.",
  "checked": "2026-07-20",
  "source": "https://docs.anthropic.com/en/docs/about-claude/pricing"
}
```


### claude — haiku

- **provider:** `claude`
- **model:** `haiku`
- **executor_class:** `small`
- **good_for:** Fast summaries, classification, extraction, low-risk scouting.
- **avoid_for:** Architecture, complex implementation, or nuanced product judgment.
- **default_effort:** `low`
- **cost:**

```json
{
  "relative": "low",
  "access": "Claude plan quota or Anthropic API",
  "note": "The unversioned Claude CLI alias can move between model versions; consult live Anthropic pricing before estimating token cost.",
  "checked": "2026-07-20",
  "source": "https://docs.anthropic.com/en/docs/about-claude/pricing"
}
```


### opencode — opencode-go/deepseek-v4-flash

- **provider:** `opencode`
- **model:** `opencode-go/deepseek-v4-flash`
- **executor_class:** `small`
- **good_for:** Cheap/fast lane. Use this for throwaway work — extraction, summarization, classification, and ephemeral `run` passes. Use it when you want maximum throughput per dollar and don't need depth.
- **avoid_for:** Complex implementation, hard reasoning, or anything you will build on.
- **default_effort:** `low`
- **cost:**

```json
{
  "relative": "very-low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.14,
    "cached_input": 0.0028,
    "output": 0.28
  },
  "estimated_requests_per_5_hours": 31650,
  "note": "$5 introductory first month, then $10/month; one of Go's highest-throughput lanes by its published request estimate.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/glm-5.2

- **provider:** `opencode`
- **model:** `opencode-go/glm-5.2`
- **executor_class:** `standard`
- **good_for:** General balanced coder. Use this for everyday implementation and review through opencode. Use it when you want a dependable all-rounder and need neither a specialist nor a flagship.
- **avoid_for:** The hardest reasoning or peak code work; reach for deepseek-v4-pro.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 1.4,
    "cached_input": 0.26,
    "output": 4.4
  },
  "estimated_requests_per_5_hours": 880,
  "note": "$5 introductory first month, then $10/month; included allowance is $60 of monthly model usage.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/kimi-k2.7-code

- **provider:** `opencode`
- **model:** `opencode-go/kimi-k2.7-code`
- **executor_class:** `standard`
- **good_for:** Code specialist. Use this for writing, editing, and refactoring. Use it when the task is mostly code and you want Kimi's code-tuned fork (faster, fewer reasoning tokens).
- **avoid_for:** General agentic or long tool-use chains; use kimi-k2.6 for that.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.95,
    "cached_input": 0.19,
    "output": 4
  },
  "estimated_requests_per_5_hours": 1350,
  "note": "$5 introductory first month, then $10/month; included allowance is $60 of monthly model usage.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/kimi-k2.6

- **provider:** `opencode`
- **model:** `opencode-go/kimi-k2.6`
- **executor_class:** `standard`
- **good_for:** General agentic workhorse. Use this for long, tool-heavy chains — it sustains thousands of tool calls cheaply. Use it for broad agentic work that isn't purely code.
- **avoid_for:** Pure code grinding (prefer kimi-k2.7-code) or quick throwaway tasks.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.95,
    "cached_input": 0.16,
    "output": 4
  },
  "estimated_requests_per_5_hours": 1150,
  "note": "$5 introductory first month, then $10/month; included allowance is $60 of monthly model usage.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/minimax-m3

- **provider:** `opencode`
- **model:** `opencode-go/minimax-m3`
- **executor_class:** `standard`
- **good_for:** Max-context, multimodal. Use this for huge codebases, long documents, or images — up to ~1M tokens and fast for its tier. Use it when context size is the constraint.
- **avoid_for:** Small, latency-sensitive tasks; minimax-m2.7 is faster when context is modest.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.3,
    "cached_input": 0.06,
    "output": 1.2
  },
  "estimated_requests_per_5_hours": 3200,
  "note": "$5 introductory first month, then $10/month; included allowance is $60 of monthly model usage.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/minimax-m2.7

- **provider:** `opencode`
- **model:** `opencode-go/minimax-m2.7`
- **executor_class:** `small`
- **good_for:** Fast agentic. Use this when you want speed on agentic work at a modest (~200K) context — much quicker and cheaper than m3. Use it when m3's huge window is overkill.
- **avoid_for:** Very large context or multimodal input; use minimax-m3.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "very-low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.3,
    "cached_input": 0.06,
    "cache_write": 0.375,
    "output": 1.2
  },
  "estimated_requests_per_5_hours": 3400,
  "note": "$5 introductory first month, then $10/month; included allowance is $60 of monthly model usage.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/deepseek-v4-pro

- **provider:** `opencode`
- **model:** `opencode-go/deepseek-v4-pro`
- **executor_class:** `frontier`
- **good_for:** Peak coding/reasoning. Use this for the hardest bugs, algorithmic work, and high-stakes code — it leads the open coding benchmarks. Use it when depth matters most.
- **avoid_for:** Cheap or throwaway work; deepseek-v4-flash is far cheaper.
- **default_effort:** `high`
- **cost:**

```json
{
  "relative": "low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.435,
    "cached_input": 0.003625,
    "output": 0.87
  },
  "estimated_requests_per_5_hours": 3450,
  "note": "$5 introductory first month, then $10/month. Go currently assigns this model $15 of monthly included usage; the frontier role is about capability, not a premium per-token bill on this access path.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/grok-4.5

- **provider:** `opencode`
- **model:** `opencode-go/grok-4.5`
- **executor_class:** `frontier`
- **good_for:** Premium OpenCode Go lane for difficult coding and reasoning when you want a second frontier perspective outside the ChatGPT and Claude families.
- **avoid_for:** Routine or high-volume work: it has by far the smallest request allowance in Go's current headline roster.
- **default_effort:** `high`
- **cost:**

```json
{
  "relative": "premium",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 2,
    "cached_input": 0.3,
    "output": 6
  },
  "estimated_requests_per_5_hours": 120,
  "note": "$5 introductory first month, then $10/month. Go currently assigns this model $15 of monthly included usage rather than the usual $60.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/glm-5.1

- **provider:** `opencode`
- **model:** `opencode-go/glm-5.1`
- **executor_class:** `standard`
- **good_for:** Compatibility fallback for general coding and review when GLM-5.2 behavior or availability is undesirable.
- **avoid_for:** Default new work when GLM-5.2 is available at the same published Go rate and allowance.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 1.4,
    "cached_input": 0.26,
    "output": 4.4
  },
  "estimated_requests_per_5_hours": 880,
  "note": "$5 introductory first month, then $10/month; current published pricing and request estimates match GLM-5.2.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### nous — moonshotai/kimi-k3

- **provider:** `nous`
- **model:** `moonshotai/kimi-k3`
- **executor_class:** `frontier`
- **good_for:** Premium long-horizon agent and coding work where a new Kimi-family frontier perspective is worth a deliberately bounded scout or implementation pass.
- **avoid_for:** Cheap iteration or loosely bounded execution. Hermes one-shot calls load substantial agent context, and K3 can take several minutes before returning final text.
- **default_effort:** `high`
- **cost:**

```json
{
  "relative": "premium",
  "access": "Hermes through the Nous OAuth catalog",
  "note": "Invoke with provider nous and model moonshotai/kimi-k3, then confirm both fields in the Hermes --usage-file receipt. No stable per-token price is recorded for this routed access.",
  "checked": "2026-08-19",
  "source": "Live Nous model catalog and verified Hermes usage receipt"
}
```


### opencode — opencode-go/mimo-v2.5

- **provider:** `opencode`
- **model:** `opencode-go/mimo-v2.5`
- **executor_class:** `small`
- **good_for:** Extremely cheap high-volume extraction, classification, routine edits, and disposable scouting through OpenCode Go.
- **avoid_for:** Hard architecture, subtle debugging, or work where one weak pass can contaminate downstream decisions.
- **default_effort:** `low`
- **cost:**

```json
{
  "relative": "very-low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.14,
    "cached_input": 0.0028,
    "output": 0.28
  },
  "estimated_requests_per_5_hours": 30100,
  "note": "$5 introductory first month, then $10/month; one of Go's highest-throughput lanes by its published request estimate.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/mimo-v2.5-pro

- **provider:** `opencode`
- **model:** `opencode-go/mimo-v2.5-pro`
- **executor_class:** `standard`
- **good_for:** Affordable bounded implementation, review, and agentic execution when MiMo V2.5 is too light but a premium frontier lane is unnecessary.
- **avoid_for:** The hardest judgment or broad autonomous work without first validating its behavior on a representative slice.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "very-low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.435,
    "cached_input": 0.003625,
    "output": 0.87
  },
  "estimated_requests_per_5_hours": 3250,
  "note": "$5 introductory first month, then $10/month. Go currently assigns this model $15 of monthly included usage rather than the usual $60.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/qwen3.7-max

- **provider:** `opencode`
- **model:** `opencode-go/qwen3.7-max`
- **executor_class:** `frontier`
- **good_for:** Higher-capability Qwen lane for difficult implementation, review, and an independent frontier scout on ambiguous technical decisions.
- **avoid_for:** Mechanical work or cost-led routing; Qwen3.7 Plus has a far larger Go request allowance.
- **default_effort:** `high`
- **cost:**

```json
{
  "relative": "mid",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 2.5,
    "cached_input": 0.5,
    "cache_write": 3.125,
    "output": 7.5
  },
  "estimated_requests_per_5_hours": 950,
  "note": "$5 introductory first month, then $10/month; included request allowance reflects its higher per-token rate.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/qwen3.7-plus

- **provider:** `opencode`
- **model:** `opencode-go/qwen3.7-plus`
- **executor_class:** `standard`
- **good_for:** High-throughput general coding and agent work with a generous Go allowance; a practical Qwen-family default below Max.
- **avoid_for:** The hardest frontier judgment, or contexts above 256K tokens when its published rates triple.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "very-low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.4,
    "cached_input": 0.04,
    "cache_write": 0.5,
    "output": 1.6
  },
  "long_context_api_usd_per_million_tokens": {
    "input": 1.2,
    "cached_input": 0.12,
    "cache_write": 1.5,
    "output": 4.8
  },
  "estimated_requests_per_5_hours": 4300,
  "note": "$5 introductory first month, then $10/month; long-context pricing applies above 256K tokens.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### opencode — opencode-go/qwen3.6-plus

- **provider:** `opencode`
- **model:** `opencode-go/qwen3.6-plus`
- **executor_class:** `standard`
- **good_for:** Compatibility fallback for general Qwen-family coding and agent work when 3.7 behavior or availability is undesirable.
- **avoid_for:** Default new work when Qwen3.7 Plus is available: 3.7 currently has both lower published rates and a larger request allowance.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "low",
  "access": "OpenCode Go subscription",
  "subscription_usd_per_month": 10,
  "api_usd_per_million_tokens": {
    "input": 0.5,
    "cached_input": 0.05,
    "cache_write": 0.625,
    "output": 3
  },
  "long_context_api_usd_per_million_tokens": {
    "input": 2,
    "cached_input": 0.2,
    "cache_write": 2.5,
    "output": 6
  },
  "estimated_requests_per_5_hours": 3300,
  "note": "$5 introductory first month, then $10/month; long-context pricing applies above 256K tokens.",
  "checked": "2026-07-20",
  "source": "https://dev.opencode.ai/docs/go/"
}
```


### cursor — composer-2.5-fast

- **provider:** `cursor`
- **model:** `composer-2.5-fast`
- **executor_class:** `standard`
- **good_for:** Fast coding lane (Cursor's default). Use this for quick edits, boilerplate, and tight agent loops where speed beats cost.
- **avoid_for:** Unattended/background work where standard Composer has the same intelligence for one-sixth the token price, or high-stakes review that needs a different frontier model.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "mid",
  "access": "Cursor included usage pool, then on-demand",
  "api_usd_per_million_tokens": {
    "input": 3,
    "output": 15
  },
  "note": "Fast changes throughput, not intelligence; Cursor may expose it as a variant rather than a distinct picker entry.",
  "checked": "2026-07-20",
  "source": "https://cursor.com/composer"
}
```


### cursor — composer-2.5

- **provider:** `cursor`
- **model:** `composer-2.5`
- **executor_class:** `standard`
- **good_for:** Cost-efficient hands-on and background coding with the same underlying intelligence as Composer 2.5 Fast; good for sustained multi-file work and long agent loops.
- **avoid_for:** Interactive work where higher throughput is worth 6x token price, or ambiguous architecture and hard review where a stronger judgment model is warranted.
- **default_effort:** `medium`
- **cost:**

```json
{
  "relative": "low",
  "access": "Cursor included usage pool, then on-demand",
  "api_usd_per_million_tokens": {
    "input": 0.5,
    "output": 2.5
  },
  "note": "Standard and Fast use the same model intelligence; this is the cheaper throughput tier.",
  "checked": "2026-07-20",
  "source": "https://cursor.com/composer"
}
```

