# Execution Sites

Linear records the minimum capability requirement with one `site:*` label. Cockpit chooses the concrete launch target at dispatch time. Do not put vendor names or transient infrastructure state into Linear labels.

## Target selection

| Requirement | Prefer | Use when | Avoid when |
|---|---|---|---|
| `site:cloud` | Native Codex or Claude cloud | One provider can complete portable repo-only work and its native cloud has the best launch/review path. | The worker must invoke another provider or needs durable machine state beyond the native sandbox. |
| `site:cloud` | Fly.io Sprites | Work needs a provider-neutral persistent Linux environment, multiple provider CLIs, isolation from bjslab's live services, or a disposable per-issue machine. | The issue needs home-network data/services, Mac hardware/GUI, or a simple native-cloud run is sufficient. |
| `site:bjslab` | Headless bjslab worker | Work requires services, data, network access, or durable operations that physically live on bjslab. | Repo plus tokens is enough; use cloud instead and keep load away from live services. |
| `site:macbook` | Local/native Mac worker | Work requires GUI, Computer Use, physical hardware, keychain/account state, launchd, or live HITL. | The Mac is merely where the board or CLI happens to be open. |
| `site:multi` | Explicit two-device plan | The work itself must coordinate or verify behavior across devices. | A single environment can reach both dependencies. |

Native agent clouds are single-provider. A Codex cloud task cannot drive Claude and a Claude cloud session cannot drive Codex. Sprites are provider-neutral: install the needed CLIs inside the Sprite and launch the chosen provider there.

## Sprites contract

Sprites are persistent, hardware-isolated Linux environments that sleep when idle. They are a cloud execution target, not another board lane and not a replacement for bjslab-hosted services.

Current control surfaces:

- MacBook CLI: `/Users/burooj/.local/bin/sprite`
- bjslab CLI: `/home/admin/.local/bin/sprite`
- Authentication is per machine/config under `~/.sprites/sprites.json`; never copy or print its tokens casually.
- The CLI may not be on non-interactive SSH `PATH`; use the absolute bjslab path.

Before a Sprite dispatch:

1. Run `sprite list` (or the absolute bjslab path) to prove authentication and organization access. Login, token setup, billing, and spend changes are approval-gated account actions.
2. Name the environment after the issue, for example `bjs-123-short-slug`, and record the name in the Cockpit Thread.
3. Create or reuse the Sprite, clone the exact repo/ref, install only the required provider/tooling, and launch from inside the Sprite.
4. Bind the provider session to the issue and move it to `In Progress` only after execution actually starts.
5. Receipt the Sprite name, repo/ref, provider session, checks, cost observation, and whether any durable state must be retained.
6. Let idle pause stop compute billing. Checkpointing or destroying provider-side state is a deliberate lifecycle decision; deletion still requires Burooj's approval.

Sprites do not expose SSH directly by default. Prefer `sprite exec` or `sprite console`; use `sprite proxy` plus an installed SSH server only when an actual SSH client workflow is necessary.

## Site label versus control surface

The launcher and the worker can live in different places:

```text
Mac or bjslab cockpit -> sprite CLI/API -> Sprite worker -> provider session
```

That remains `site:cloud`. Use `site:bjslab` only when the issue requires bjslab's own services, data, network, or durable host state.
