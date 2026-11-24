#!/usr/bin/env bash
# GitLab adapter: writes unresolved MR threads to a cache file, prints its path.
# Self-hosted: set GITLAB_HOST (glab reads it).
set -euo pipefail

MR_ARG="${1:-}"

if ! command -v glab >/dev/null 2>&1; then
    echo "ERROR: glab not found in PATH" >&2
    exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
    echo "ERROR: jq not found in PATH" >&2
    exit 1
fi

# Resolve MR metadata (iid, web_url) so we can name the cache file deterministically.
if [[ -n "$MR_ARG" ]]; then
    MR_JSON="$(glab mr view "$MR_ARG" -F json 2>/dev/null)"
else
    MR_JSON="$(glab mr view -F json 2>/dev/null)"
fi

if [[ -z "$MR_JSON" ]]; then
    echo "ERROR: could not resolve MR (pass an iid/branch/url, or run from a branch with an open MR)" >&2
    exit 2
fi

MR_IID="$(echo "$MR_JSON" | jq -r '.iid')"
MR_URL="$(echo "$MR_JSON" | jq -r '.web_url')"

if [[ "$MR_IID" == "null" || -z "$MR_IID" ]]; then
    echo "ERROR: could not extract MR iid from glab response" >&2
    exit 3
fi

CACHE_DIR="${REVIEW_CACHE_DIR:-/tmp/review-comments}"
mkdir -p "$CACHE_DIR"
CACHE_FILE="$CACHE_DIR/gitlab-mr-${MR_IID}.json"

# Pull unresolved threads. Supplying the iid avoids ambiguity if the cwd has multiple MRs.
THREADS_RAW="$(glab mr note list "$MR_IID" --state unresolved -F json 2>/dev/null)"

if [[ -z "$THREADS_RAW" ]]; then
    THREADS_RAW="[]"
fi

NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Reshape: keep only fields the workflow needs, add a stable index + status.
echo "$THREADS_RAW" | jq \
    --arg mr_url "$MR_URL" \
    --argjson mr_iid "$MR_IID" \
    --arg fetched_at "$NOW" \
    '{
        mr_iid: $mr_iid,
        mr_url: $mr_url,
        fetched_at: $fetched_at,
        threads: [
            . as $all | range(0; length) as $i |
            $all[$i] | {
                index: ($i + 1),
                discussion_id: .id,
                status: "pending",
                type: (
                    if (.notes[0].position // null) != null then "diff"
                    elif (.notes[0].type // "") == "DiffNote" then "diff"
                    else "general"
                    end
                ),
                file_path: (.notes[0].position.new_path // .notes[0].position.old_path // null),
                new_line: (.notes[0].position.new_line // null),
                old_line: (.notes[0].position.old_line // null),
                notes: [
                    .notes[] | {
                        author: (.author.username // .author.name // "unknown"),
                        body: .body,
                        created_at: .created_at,
                        system: (.system // false)
                    }
                ]
            }
        ]
    }' > "$CACHE_FILE"

echo "$CACHE_FILE"
