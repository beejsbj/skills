# Out Of Scope And Prior Decisions

Use this reference when an enhancement or repeated idea may be rejected, parked, or treated as already decided.

Store out-of-scope records in the project's canonical place: tracker project doc, project description, repo decision file, or equivalent. Do not create a new local side channel unless the project has explicitly chosen it.

## When To Use

Use out-of-scope records for:

- rejected enhancements
- repeated requests that should not be re-litigated every triage pass
- product/workflow boundaries that explain why a class of work is not being done
- "not this project" decisions that future agents are likely to rediscover

Do not use out-of-scope records for:

- bugs
- duplicates that should point to an active canonical issue
- work that is already implemented
- temporary deferrals that belong in `Parked`
- ideas that simply need clarification

## Triage Flow

1. Search the issue, PR, project, and relevant docs for similar prior decisions.
2. If a matching out-of-scope record exists, summarize the match and ask whether to confirm, reconsider, or split the new request.
3. If confirmed, close/cancel/park the issue with a comment linking the record.
4. If reconsidered, update the record with the new decision and continue triage.
5. If no record exists and the decision is durable, create one in the project's canonical decision surface before closing the loop.

## Record Shape

```md
## <Decision or Capability Name>

**Decision**
- Out of scope | Not this project | Rejected for now | Reconsidered on <date>

**Reason**
- ...

**Prior Requests**
- ...

**Reconsider When**
- ...

**Last Reviewed**
- YYYY-MM-DD
```

Keep the record short. Its job is to preserve the reason and redirect future triage, not to become a full design document.
