#!/usr/bin/env bash
# Update the status of a single thread in the cache file.
#
# Usage: update_status.sh <cache-file> <thread-index> <status>
#   status: pending | addressed | skipped | replied | resolved
#
# Writes the updated JSON in place.

set -euo pipefail

CACHE_FILE="${1:?cache file path required}"
INDEX="${2:?thread index required}"
STATUS="${3:?status required}"

if [[ ! -f "$CACHE_FILE" ]]; then
    echo "ERROR: cache file not found: $CACHE_FILE" >&2
    exit 1
fi

TMP="$(mktemp)"
jq --argjson idx "$INDEX" --arg status "$STATUS" '
    .threads = [
        .threads[] | if .index == $idx then .status = $status else . end
    ]
' "$CACHE_FILE" > "$TMP"
mv "$TMP" "$CACHE_FILE"
