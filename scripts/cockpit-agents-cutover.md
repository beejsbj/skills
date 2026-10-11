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

## Mac handoff

Read-only inspection on 2026-10-11 found the clean skills checkout at `/Users/burooj/BJsWorkspace/Projects/skills`, and no `t3-code` entry in any of the three native skill roots. The older `/Users/burooj/Projects/skills` path does not exist. The Mac's Codex `cockpit` link already targets `/Users/burooj/BJsWorkspace/cockpit`.

After the coordinator arranges Mac CLI deployment and skills checkout update, use the same local linker there. It will add the three new links; inspect foreign entries rather than overwriting them. No remote deployment was performed by the skills worker.

## Verify and recover

Read the installed skill through each native root and confirm fresh agent discovery includes `cockpit-agents` and excludes `t3-code`. Existing sessions can retain their previously loaded catalog until restarted. Check `cockpit agents projects` and `models` read-only on the owning machine; inspect only metadata for any existing session. Verify dispatch separately on an authorized new test session, never by sending to a user's unrelated thread.

For rollback, compare each backup entry with the current link before changing it. Remove a newly added link only if it still matches `after`; recreate a removed link using its recorded `before` text only if the path is still absent. Restore the prior skills commit through the coordinator's normal revert path before expecting the old `t3-code` skill to reappear: the old symlink alone cannot restore the removed `SKILL.md`. Keep the canonical checkout on `main`. The retained helper needs no rollback.
