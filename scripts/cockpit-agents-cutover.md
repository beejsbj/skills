# Cockpit agents skill cutover

Deploy the BJS-527 Cockpit CLI and confirm its readiness with the coordinator before applying this skills change. Review and merge the skills PR separately; run the linker from the canonical skills checkout after it advances to the accepted commit. A task worktree must not become a durable skill target.

`cockpit/` remains a symlink into the sibling Cockpit repository. The new `cockpit-agents/` owns session guidance within this repo and uses only the public `cockpit agents` interface. Consult, model-taste, and acpx link to it. Their existing installation links need no replacement when they already target this canonical repo.

## Apply on bjslab

Run from `/mnt/server-ssd/BJsWorkspace/Projects/skills` after CLI deployment:

```sh
python3 scripts/sync-cockpit-agents.py --check
python3 scripts/sync-cockpit-agents.py --apply \
  --backup /absolute/session/path/skills-links-before.json
python3 scripts/sync-cockpit-agents.py --check
```

The first check exits 1 if links need updating, or 2 if CLI commands are missing or a name collides. Apply checks the CLI and all selected roots before changing links. It records old and intended link targets in a new backup file, adds `cockpit-agents`, and removes only `t3-code` symlinks pointing to this repo. Existing foreign links and ordinary directories cause refusal. No helper, session, credential, or transcript data is touched. A late filesystem failure may leave a partial cutover; inspect the backup and current links before retrying.

Default roots are `~/.codex/skills`, `~/.agents/skills`, and `~/.claude/skills`; `--root PATH` can select explicit roots. The new targets must resolve to this canonical checkout's `cockpit-agents/`. Hermes profiles using this repo through `skills.external_dirs` discover the new folder after their normal skill-index refresh; inspect any profile-local name collision separately.

The compatibility scripts under `t3-code/scripts/` remain byte-for-byte unchanged so already-running coordinators and older Cockpit installations can finish using them. Removing the discovered skill does not delete that helper. Cockpit's deployed transport owns future calls; retire the compatibility files only after all callers have migrated. Their protocol reference is retained for legacy debugging, not as a session route.

## Hermes profile links

Read-only inspection on 2026-10-11 found:

| Profile | Skill source | Required cutover |
| --- | --- | --- |
| Otto | `skills.external_dirs` includes the canonical skills repo; no local `t3-code` copy or link | Advance the canonical repo, then refresh discovery. The old trigger disappears with `t3-code/SKILL.md`; `cockpit-agents` appears from the same external source. |
| Rose | Profile-local skills only; no `t3-code` entry and no external skill roots | Add `cockpit-agents` to `/home/admin/.hermes/profiles/rose/skills`. |
| Klaw/default | Root-local skills only; no `t3-code` entry and no external skill roots | Add `cockpit-agents` to `/home/admin/.hermes/skills`. |

Neither skill name is disabled globally or per platform in these profiles. After CLI readiness and canonical repo integration, run this **in addition to** the native-root invocation above:

```sh
python3 scripts/sync-cockpit-agents.py --apply \
  --root /home/admin/.hermes/skills \
  --root /home/admin/.hermes/profiles/rose/skills \
  --backup /absolute/session/path/hermes-skills-links-before.json
python3 scripts/sync-cockpit-agents.py --check \
  --root /home/admin/.hermes/skills \
  --root /home/admin/.hermes/profiles/rose/skills
```

Explicit `--root` arguments replace the three default roots, so retain both deployment invocations. Otto needs no extra local link. Verify fresh discovery per profile after cutover: existing sessions may retain a previously loaded trigger. Do not change `agent.environment_hint`, souls, or profile configuration as part of this link deployment.

## Mac handoff

Read-only inspection on 2026-10-11 found the clean skills checkout at `/Users/burooj/BJsWorkspace/Projects/skills`, and no `t3-code` entry in any of the three native skill roots. The older `/Users/burooj/Projects/skills` path does not exist. The Mac's Codex `cockpit` link already targets `/Users/burooj/BJsWorkspace/cockpit`.

After the coordinator arranges Mac CLI deployment and skills checkout update, use the same local linker there. It will add the three new links; inspect foreign entries rather than overwriting them. No remote deployment was performed by the skills worker.

## Verify and recover

Read the installed skill through each native root and confirm fresh agent discovery includes `cockpit-agents` and excludes `t3-code`. Existing sessions can retain their previously loaded catalog until restarted. Check `cockpit agents projects` and `models` read-only on the owning machine; inspect only metadata for any existing session. Verify dispatch separately on an authorized new test session, never by sending to a user's unrelated thread.

For rollback, compare each backup entry with the current link before changing it. Remove a newly added link only if it still matches `after`; recreate a removed link using its recorded `before` text only if the path is still absent. Restore the prior skills commit through the coordinator's normal revert path before expecting the old `t3-code` skill to reappear: the old symlink alone cannot restore the removed `SKILL.md`. Keep the canonical checkout on `main`. The retained helper needs no rollback.
