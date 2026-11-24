#!/usr/bin/env bash
# Self-check: scan a temp repo with 2 worktrees, expect both in JSON and HTML.
set -euo pipefail
d=$(mktemp -d); trap 'rm -rf "$d"' EXIT
here=$(cd "$(dirname "$0")" && pwd)
git -C "$d" init -q repo && cd "$d/repo"
git -c user.email=a@b -c user.name=t commit -q --allow-empty -m init
git worktree add -q ../wt -b PROJ-1-demo
n=$(python3 "$here/worktree-scan.py" "$d" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(len(d["worktrees"]),d["worktrees"][1]["ticket"])')
[ "$n" = "2 PROJ-1" ] || { echo "FAIL: $n"; exit 1; }
python3 "$here/worktree-scan.py" --html "$d/b.html" "$d"
grep -q PROJ-1-demo "$d/b.html" || { echo "FAIL: html"; exit 1; }
echo "selfcheck: PASS"
