# When to call Jev

Jev is a typed-judgment model. You hand it evidence you already hold plus a
closed question, and it returns one of the answers you listed, with a
probability over all of them. One call is roughly 300 ms and about a thousand
tokens. It does not write prose or code, does not look anything up, and does
not act. Everything around it is yours: the candidates, the evidence, the
threshold, and what happens next.

## The index-card test

Before the evidence arrives, could you write the complete answer set and the
rubric on an index card?

- Yes, and the answer depends on meaning rather than exact fact: **Jev**.
- The answer is exact (lookup, arithmetic, dates, parsing, file identity,
  permissions, clock): **code**.
- You need new words, code, a reason, or the answer set itself: **a
  generative model**.

## Call Jev when all four hold

1. **The question is closed.** One option from a set you can enumerate now
   (`choice`), a level on a rubric you can write down (`score`), or yes/no on a
   proposition (`noul`). Always include an explicit `none`, `keep`, or `other`.
2. **The evidence is in hand.** Text or JSON state you already have, small
   enough for one payload. Jev does not fetch, browse, or remember.
3. **A wrong answer is cheap or gated.** The result feeds a rank, a label, a
   preview, or a choice that code or a person validates before anything
   irreversible happens. Probabilities are signals, not authorization.
4. **It recurs, or a full model turn would be waste.** The same question over
   many records, inside a loop, ahead of a deadline, or a bounded decision that
   does not deserve a conversation. A single judgment you can make yourself in
   the time it takes to write the rubric is not worth a call.

## Do not call Jev when

- You want prose, code, a summary, or an explanation.
- The candidate set is unknown. Generate candidates first (code or a
  generative model), then let Jev pick.
- The decision is consequential and nobody will review it. Put a preview and an
  acceptance step between Jev and the action.
- The evidence is private and not authorized for the configured provider.
  Calls go to OpenRouter or TypeSafe; send only what may leave the machine.
- You are tempted to add it to a pipeline stage that already works. Replace a
  stage only after comparing Jev to the current approach on labeled examples
  from that workflow.

## How to call it well

- Put state in JSON, questions in a file, and pipe: `jev ask - --questions-file
  q.json --format json --full-output`. Check `.ok`. A failed or timed-out call
  is *unresolved*, never *no*.
- Keep the full distribution. Set thresholds in the caller from a few labeled
  examples of that workflow, not from a universal confidence cutoff.
- Ask independent questions about the same state in one call. When one answer
  determines the next candidates, build the next stage in code.
- For many records use `jev classify` with stable IDs and map rows back in
  order. Check per-row errors even when the envelope succeeds.
- Test a proposed rubric with `jev eval` against known labels before wiring it
  in.

## Where it is already wired

- `cockpit linear triage` — project, lane, and relation suggestions for one
  issue, with a digest-bound preview before any write.
- `cockpit handbook rank` — rerank a supplied handbook/skill shortlist,
  surfacing conflicts without settling authority.
- Tasting Kitchen `taste observe` — axis observations on an immutable Dish,
  stored beside human tastings, disagreements kept.
- `job-search-jev` shortlist and packet — offered-action selection, listing fit,
  requirement-to-evidence and claim checks, review-only.

Prefer extending one of these over inventing a parallel call site.
