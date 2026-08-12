#!/usr/bin/env bash
# Expose the promoted Matt Pocock skills from the pinned vendor submodule.
#
# This intentionally reads the upstream plugin manifest instead of scanning the
# whole checkout: `misc/` and `in-progress/` are upstream experiments, not part
# of the stable suite we subscribe to.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
vendor_root="$repo_root/vendor/mattpocock-skills"
manifest="$vendor_root/.claude-plugin/plugin.json"
mode="sync"
roots=()

usage() {
  cat <<'EOF'
Usage: scripts/sync-matt-pocock-skills.sh [--check] [--root <skill-directory>]...

Links the promoted upstream Matt Pocock skills into each selected agent skill
directory. Without --root, it updates the standard Claude and Codex locations
for the current user: ~/.claude/skills, ~/.agents/skills, and ~/.codex/skills.

Only symlinks managed by this repository are replaced or removed. Any other
file or symlink with a colliding skill name stops the command for inspection.
EOF
}

while (($#)); do
  case "$1" in
    --check)
      mode="check"
      ;;
    --root)
      shift
      if (($# == 0)); then
        echo "error: --root requires a directory" >&2
        exit 2
      fi
      roots+=("$1")
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ ! -f "$manifest" ]]; then
  echo "error: upstream vendor is missing at $vendor_root" >&2
  echo "hint: git submodule update --init --recursive" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required to read $manifest" >&2
  exit 1
fi

if ((${#roots[@]} == 0)); then
  roots=("$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.codex/skills")
fi

link_destination() {
  # Resolve the symlink text lexically, rather than with realpath: legacy
  # links may already be dangling because their local fork was just purged.
  python3 -c '
import os
import sys

target = sys.argv[1]
print(os.path.abspath(os.path.join(os.path.dirname(target), os.readlink(target))), end="")
' "$1"
}

is_replaceable_link() {
  local existing="$1"
  local name="$2"
  [[ "$existing" == "$repo_root/$name" || "$existing" == "$vendor_root/skills/"* ]]
}

promoted_skills() {
  python3 -c '
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    manifest = json.load(handle)
for skill in manifest.get("skills", []):
    print(skill.removeprefix("./"))
' "$manifest"
}

retired_local_skills=(grill-me-stateful to-issues two-axis-review writing-great-skills)
failed=0

for root in "${roots[@]}"; do
  if [[ "$mode" == "sync" ]]; then
    mkdir -p "$root"
  elif [[ ! -d "$root" ]]; then
    echo "missing skill root: $root" >&2
    failed=1
    continue
  fi

  while IFS= read -r relative; do
    source="$vendor_root/$relative"
    name="$(basename "$source")"
    target="$root/$name"

    if [[ ! -f "$source/SKILL.md" ]]; then
      echo "error: upstream manifest entry is not a skill: $relative" >&2
      exit 1
    fi

    if [[ -L "$target" ]]; then
      existing="$(link_destination "$target")"
      if [[ "$existing" == "$source" ]]; then
        echo "ok: $target -> $source"
        continue
      fi
      if ! is_replaceable_link "$existing" "$name"; then
        echo "collision: $target -> $existing (not managed by this repo)" >&2
        failed=1
        continue
      fi
      if [[ "$mode" == "check" ]]; then
        echo "stale link: $target -> $existing (expected $source)" >&2
        failed=1
      else
        ln -sfn "$source" "$target"
        echo "linked: $target -> $source"
      fi
    elif [[ -e "$target" ]]; then
      echo "collision: $target exists and is not a symlink" >&2
      failed=1
    elif [[ "$mode" == "check" ]]; then
      echo "missing link: $target -> $source" >&2
      failed=1
    else
      ln -s "$source" "$target"
      echo "linked: $target -> $source"
    fi
  done < <(promoted_skills)

  for name in "${retired_local_skills[@]}"; do
    target="$root/$name"
    if [[ ! -L "$target" ]]; then
      continue
    fi
    existing="$(link_destination "$target")"
    if [[ "$existing" != "$repo_root/$name" ]]; then
      echo "collision: retired $target -> $existing (not managed by this repo)" >&2
      failed=1
    elif [[ "$mode" == "check" ]]; then
      echo "stale retired link: $target -> $existing" >&2
      failed=1
    else
      rm "$target"
      echo "removed stale link: $target"
    fi
  done
done

exit "$failed"
