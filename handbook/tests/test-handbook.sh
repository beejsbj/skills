#!/usr/bin/env bash
set -Eeuo pipefail

test_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(dirname "$test_dir")"
handbook="$skill_dir/scripts/handbook"
wrapper="$skill_dir/scripts/bjslab-cockpit"
hook="$skill_dir/scripts/terminal-context.sh"

expected=$(cockpit handbook bjslab)
test "$($handbook)" = "$expected"

banner=$($handbook --banner)
case "$banner" in
  "bjslab · handbook $expected · command: cockpit handbook bjslab") ;;
  *) printf 'unexpected banner: %s\n' "$banner" >&2; exit 1 ;;
esac

if "$handbook" unexpected >/dev/null 2>&1; then
  printf 'unexpected argument was accepted\n' >&2
  exit 1
fi

hook_output=$(
  PATH="$skill_dir/scripts:$PATH" \
  HANDBOOK_BANNER_SHOWN= \
  bash --noprofile --norc -ic ". '$hook'" 2>&1
)
grep -Fq "command: cockpit handbook bjslab" <<<"$hook_output"

$wrapper --help >/dev/null
printf 'handbook routes: ok\n'
