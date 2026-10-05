# Souls

Prime is the base orientation. Otto, Klaw, and Rose are distinct personas built on that ground.

## Edit and compose

- `prime/source/`: hand-authored orientation, reversibility, revisable personal context, and discipline.
- `otto.md`, `klaw.md`, `rose.md`: hand-authored persona text.
- `composition.json`: explicit ordered source lists and output paths.
- `prime/soul.md`, `generated/*.md`: generated complete instructions; never edit these directly.

From the repository root:

```sh
python3 scripts/compose-souls.py
python3 scripts/compose-souls.py --check
python3 -m unittest discover -s tests -p 'test_compose_souls.py'
```

Commit source changes and their generated outputs together. A stale-output check fails if a source edit has not been composed. Concatenation preserves the source text; there is no heading extraction, paraphrasing, or runtime include to interpret. Shared passages are written once. The manifest includes personal context for the persistent personas, with the same explicit skip for dispatched executors; its inclusion does not assign the personas identical roles.

## Consumers

| Consumer | Complete file |
| --- | --- |
| Codex / Claude global instructions | `prime/soul.md` |
| ChatGPT instruction text, when updated manually | `prime/soul.md` |
| Hermes default (Klaw) | `generated/klaw.md` |
| Hermes Otto | `generated/otto.md` |
| Hermes Rose | `generated/rose.md` |

On bjslab, the Codex and Claude global instruction symlinks point to this checkout's `prime/soul.md`. Hermes `~/.hermes/SOUL.md` and `~/.hermes/profiles/{otto,rose}/SOUL.md` point to the corresponding generated files. Preserve the previous files before changing consumer links; do not overwrite unrelated profiles (the Mac's University Bot is separate). On other machines, inspect the existing checkout and instruction links before deploying there. ChatGPT configuration is a separate manual consumer; composing a file does not update an account setting.

A runtime may cache instructions in an existing conversation. New prompt builds receive the current composed file; use a fresh session or the runtime's documented refresh to adopt changes in an existing one. A service restart alone does not prove a persisted prompt was refreshed.

## Review the behavior

Check complete loading without truncation in each profile. Then review representative situations: Otto coordinates a reply and delegates work without losing the purpose; Rose independently follows up on a salient habit or task; Klaw voices a conflict with the underlying commitment and verifies the work. Both Otto and Rose can update shared records. A repeated reminder, a speculative possibility promoted to a commitment, or an unverified completion claim is a failure even when the character voice sounds right.

Schedules, tool procedures, source-system authority, and the separate purposes of Act, Resurface, and Scan belong in their own guidance. Soul text does not create watchers or authorize unattended external actions by itself.

[Prime's construction and attribution](prime/README.md) records the reasoning and source of the Patrick adaptation.
