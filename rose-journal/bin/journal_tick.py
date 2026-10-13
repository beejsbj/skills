"""Rose cron entry point (copied into the Rose profile's scripts/ directory).

Hermes only runs scripts that live under HERMES_HOME/scripts, so this stub
imports the engine from the canonical skills checkout.
"""
import sys

sys.path.insert(0, "/mnt/server-ssd/BJsWorkspace/Projects/skills/rose-journal")

from rose_journal.tick import main  # noqa: E402

raise SystemExit(main())
