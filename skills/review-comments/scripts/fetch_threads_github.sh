#!/usr/bin/env bash
# GitHub adapter: writes unresolved PR review threads to a cache file (same schema as the
# GitLab adapter), prints its path. Usage: fetch_threads_github.sh [pr-number|url|branch]
set -euo pipefail

PR_ARG="${1:-}"
for c in gh jq; do
    command -v "$c" >/dev/null 2>&1 || { echo "ERROR: $c not found in PATH" >&2; exit 1; }
done

PR_JSON="$(gh pr view ${PR_ARG:+"$PR_ARG"} --json number,url 2>/dev/null || true)"
if [[ -z "$PR_JSON" ]]; then
    echo "ERROR: could not resolve PR (pass a number/branch/url, or run from a branch with an open PR)" >&2
    exit 2
fi
PR_NUM="$(jq -r .number <<<"$PR_JSON")"
PR_URL="$(jq -r .url <<<"$PR_JSON")"
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
OWNER="${REPO%%/*}"; NAME="${REPO##*/}"

CACHE_DIR="${REVIEW_CACHE_DIR:-/tmp/review-comments}"
mkdir -p "$CACHE_DIR"
CACHE_FILE="$CACHE_DIR/github-pr-${PR_NUM}.json"

# First 100 threads, first 50 comments each (ponytail: no pagination; add --paginate cursor if a PR exceeds this)
QUERY='query($owner:String!,$name:String!,$num:Int!){repository(owner:$owner,name:$name){pullRequest(number:$num){reviewThreads(first:100){nodes{id isResolved path line originalLine comments(first:50){nodes{author{login} body createdAt}}}}}}}'

gh api graphql -f query="$QUERY" -F owner="$OWNER" -F name="$NAME" -F num="$PR_NUM" |
jq --arg url "$PR_URL" --argjson num "$PR_NUM" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
    [.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved | not)] as $t |
    { mr_iid: $num, mr_url: $url, fetched_at: $now,
      threads: [ range(0; $t|length) as $i | $t[$i] | {
        index: ($i + 1),
        discussion_id: .id,
        status: "pending",
        type: (if .path then "diff" else "general" end),
        file_path: .path,
        new_line: .line,
        old_line: .originalLine,
        notes: [ .comments.nodes[] | {
            author: (.author.login // "unknown"), body: .body,
            created_at: .createdAt, system: false } ] } ] }' > "$CACHE_FILE"

echo "$CACHE_FILE"
