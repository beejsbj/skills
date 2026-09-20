# Use Jev through jevon

On bjslab, `jev` runs upstream [jevon](https://github.com/douglance/jevon) 0.8.0.
`jevon` is an alias for the same command. No MCP registration is needed for an
agent that can run shell commands, including this harness and Hermes.

```sh
jev --version
jev ask --help
jev classify --help
```

## One judgment or a pipeline stage

```sh
jev ask 'I was charged twice for my subscription.' \
  --noul 'Which topic best matches this request?' \
  --choice billing --choice account --choice other \
  --format json --full-output
```

`--noul` supplies the question text even when paired with `--choice` or `--score`.
Used alone, it returns the probability of yes. The shorthand answer is named
`answer`. Use `--questions-file` for multiple named questions and richer criteria.

For a pipeline, pass evidence on stdin (or use `--state-file`), request the full
JSON envelope, and check success before extracting an answer:

```sh
set -euo pipefail
printf '%s\n' 'I was charged twice for my subscription.' |
  jev ask - --noul 'Which topic best matches this request?' \
    --choice billing --choice account --choice other \
    --format json --full-output |
  jq -er 'if .ok then .data.answers.answer.choice else error(.error | tostring) end'
```

`ask` returns `{ok, data: {model, answers, usage}, meta}` with `--full-output`.
Without it, successful output is the data alone. Handle nonzero exit status and
`ok: false`; never translate a failed call into a negative judgment. Use `timeout`
around the command if the workflow needs an overall wall-clock limit.

## Many records or many questions

```sh
jev classify --stdin \
  --noul 'Which topic best matches this request?' \
  --choice billing --choice account --choice other \
  --concurrency 4 --format json --full-output < records.txt > results.json
```

Each input line is one complete record. Use `--items-file` with a JSON array of
strings for multiline records. Keep stable source IDs in the input and map rows
back to the original order. Batch output includes the original text; store it
according to the workflow's data policy. Check `.data.failed` and per-row `error`
even when the top-level envelope is successful. Batch exit codes are 0 for all
answered, 1 for none answered, and 2 for partial failure.

`--questions-file questions.json` accepts an object such as:

```json
{
  "topic": {
    "type": "choice",
    "instructions": "Which topic best matches this request?",
    "criteria": {
      "billing": "Charges, invoices, refunds, or duplicate payment",
      "account": "Login, profile, or access",
      "other": "No supplied topic fits"
    }
  },
  "duplicate_charge": {
    "type": "noul",
    "instructions": "Does the person report being charged twice?"
  }
}
```

Use one request for independent questions about the same state. Use another stage
when an answer determines new evidence or candidates. Noul has no separate
confidence; Choice/Score confidence describes concentration, not correctness.
Keep probabilities when making consequential decisions. Jevon's default
`--min-confidence` is a reporting threshold, not a validated policy for your data.
Use `jev eval --help` when comparing rubrics against known labels.

## Credentials and installation

The [local launcher](../scripts/jev.py) passes through upstream arguments, output,
exit status, and signals. It adds only host credential configuration:

1. An existing `TYPESAFE_API_KEY` uses the caller's TypeSafe SDK configuration.
2. Otherwise, use `OPENROUTER_API_KEY` or the existing protected OpenCodex key at
   `~/.opencodex/config.json`, setting the compatibility base to
   `https://openrouter.ai/api` and model to `typesafe/jev-1.13`.

It refuses to borrow an OpenRouter key for an unrelated explicit endpoint or a
direct TypeSafe model. Help/schema inspection does not read the credential store.
`jev doctor` reports resolved configuration and a masked key; do not copy that key
fragment into receipts. Provider debug logging is disabled. Keys are passed only
in the child environment, not command arguments or a new credential file.

This is automatic credential selection, not cross-provider retry. SDK retries
remain upstream's behavior. The old foundation's custom receipts, replay contract,
and provider fallback are not part of jevon.

The pinned upstream executable is `~/.local/share/jevon/0.8.0/bin/jev`.
To reproduce the installation with a compatible Rust toolchain (Rust >= 1.98):

```sh
cargo install jevon --version 0.8.0 --locked --bin jev \
  --root "$HOME/.local/share/jevon/0.8.0"
```

On bjslab the isolated toolchain is under `~/.local/share/jevon/toolchain/`; its
installation did not modify shell profiles. The installed `~/.local/bin/jev` and
`jevon` links target this skill's executable launcher. Skill links already expose
the same router to Codex, Claude, Hermes, and `.agents` consumers.

Jevon also offers `jev --mcp`; register it only when a caller needs MCP. Its stdin
then carries the protocol, so pass state directly or by file. Upstream skill
generation is optional; this shared router is the normal entry point here.

For earlier foundation fixtures only, `jev-legacy evaluate ...` remains available.
That command has a different request/result contract. For new integration work,
follow [build.md](build.md).
