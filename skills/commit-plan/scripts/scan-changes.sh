#!/usr/bin/env bash
# Find every git repo under a root dir that has uncommitted changes.
# Usage: scan-changes.sh [root-dir] [max-depth]
set -euo pipefail

ROOT="${1:-.}"
DEPTH="${2:-5}"

while IFS= read -r gitdir; do
    repo="${gitdir%/.git}"
    changes="$(git -C "$repo" status --porcelain 2>/dev/null || true)"
    if [ -n "$changes" ]; then
        echo "=== $repo ==="
        echo "$changes"
        echo
    fi
done < <(find "$ROOT" -maxdepth "$DEPTH" -type d -name ".git" 2>/dev/null)
