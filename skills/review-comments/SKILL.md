---
name: review-comments
description: Walk through unresolved pull/merge request review comments one by one on GitHub, GitLab, or other forges. Explain each reviewer's point in plain language, judge whether it is valid, suggest a fix, draft a reply in a configurable tone, and post the reply (and optionally resolve the thread) once approved. Use when the user asks to handle PR/MR review comments, address review feedback, reply to reviewers, or resolve review threads.
---

# review-comments

Walks through unresolved review threads on a pull request (GitHub) or merge request (GitLab and
others) interactively, one at a time. For each thread: explains the comment, judges validity,
suggests a fix, drafts a reply, and, on the user's approval, posts the reply and optionally
resolves the thread.

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `REPLY_TONE` | `references/reply_tone.md` (junior dev replying to senior reviewers) | Guide for drafting replies. Point to your own file, or describe a tone in the prompt. |
| `CACHE_DIR` | `/tmp/review-comments` | Where thread progress is cached (scripts read env `REVIEW_CACHE_DIR`). |

## When to use

Trigger when the user asks to "address / handle / answer review comments", "go through the review
on my PR/MR", "reply to reviewers", or "resolve review threads".

## Platform adapters

Detect the platform from `git remote -v` (or ask). `<id>` = the thread id in the cache.

| Operation | GitHub | GitLab (incl. self-hosted) | Bitbucket / Azure DevOps |
|---|---|---|---|
| Find the PR/MR | `gh pr view [arg] --json number,url` | `glab mr view [arg] -F json` | Azure: `az repos pr list --source-branch <b>`; Bitbucket: REST `pullrequests` |
| List unresolved threads | `scripts/fetch_threads_github.sh [arg]` (GraphQL `reviewThreads`, filters `isResolved`) | `scripts/fetch_threads_gitlab.sh [arg]` (`glab mr note list --state unresolved`) | Not scripted: REST (Azure `pullRequests/{id}/threads`, Bitbucket `pullrequests/{id}/comments`); build the same cache shape by hand |
| Post reply | `gh api graphql` mutation `addPullRequestReviewThreadReply(input:{pullRequestReviewThreadId:"<id>", body:"..."})` | `glab mr note create <iid> --reply <id-prefix> -m "..."` | REST: Azure `POST .../threads/{threadId}/comments`; Bitbucket `POST .../comments` with `parent.id` |
| Resolve thread | `gh api graphql` mutation `resolveReviewThread(input:{threadId:"<id>"})` | `glab mr note resolve <id> <iid>` | REST: Azure `PATCH .../threads/{threadId}` with `status`; Bitbucket `POST .../comments/{id}/resolve` |

Self-hosted GitLab: `glab` uses the host of the git remote; authenticate with
`glab auth login --hostname <host>` (or set `GITLAB_HOST`).

## Workflow

### Step 1 — Identify the PR/MR

If the user passed a number, branch name, or URL, use it. Otherwise auto-detect from the current
branch. If none is found, ask the user. Pick the adapter column from the git remote.

### Step 2 — Fetch unresolved threads into temp memory

Run the adapter's fetch script (`scripts/fetch_threads_github.sh` or `scripts/fetch_threads_gitlab.sh`).
It prints the cache file path on stdout. The cache (`<CACHE_DIR>/<platform>-<pr|mr>-<number>.json`) contains every unresolved thread with
a `status` field (`pending` initially) so progress survives across iterations.

```bash
CACHE=$(bash scripts/fetch_threads_github.sh "$PR_ARG")   # or fetch_threads_gitlab.sh
```

If the cache exists already from a prior run on the same MR, ask the user whether to refresh it
or resume from where they left off. Refresh = re-run the script (overwrites). Resume = read
the existing cache and skip threads whose `status` is not `pending`.

If the threads array is empty, tell the user there are no unresolved threads and stop.

### Step 3 — Summarize the queue

Before diving in, briefly tell the user: how many threads, grouped by file (for diff threads)
plus a count of general (non-diff) threads. Keep it to ~3 lines. Example:

> 7 unresolved threads: 4 in `src/auth/login.go`, 2 in `src/db/migrate.sql`, 1 general thread.

### Step 4 — Loop over threads (one at a time)

For each `pending` thread, in `index` order:

#### 4a. Show the thread

Display, in this exact shape:

```
Thread N/M  ·  <file_path>:<line>  (or "general")
─────────────────────────────────────
<author>: <body>
[follow-up notes if any]
```

Strip system notes (where `system: true`). For diff threads, also `Read` the cited
file at the cited line so you can speak to the actual code, not just the comment text.

#### 4b. Explain in plain words

One short paragraph. What is the reviewer asking for, in non-jargon terms? If they're pointing
at a specific issue (bug, style, naming, perf, missing test, etc.), name it.

#### 4c. Judge validity

State a verdict in one line, with a short reason:
- **Valid** — the reviewer is right; the code should change.
- **Partially valid** — the concern is real but the suggested fix isn't quite right.
- **Not applicable / wrong** — the reviewer misread the code, or the concern doesn't apply.
  Cite the line/symbol that proves it.

Be honest. Senior reviewers are usually right but not always; read the code before deciding.

#### 4d. Suggest a fix

If valid or partially valid: propose the smallest change that addresses the concern. Show the
diff inline (a few lines of before/after) — don't apply it yet. Wait for the user's go-ahead,
then use `Edit` to apply.

If not applicable: skip to 4e (the reply will explain why).

#### 4e. Draft a reply

Draft a reply following the configured `REPLY_TONE` (default `references/reply_tone.md`). Read it
before drafting if you haven't this session. Show the draft to the user prefixed with `Draft reply:` so it's clear
this is the proposed message.

#### 4f. Approve and post

Ask the user: post as-is, edit, or skip?
- If "post": run the adapter's **Post reply** operation.
- If the user wants edits, take their changes and re-show before posting.
- If "skip" — leave the thread alone.

After a successful post, ask whether to resolve the thread; if yes, run the adapter's
**Resolve thread** operation.

Update the cache status with `scripts/update_status.sh`:
- `replied` after a reply is posted
- `resolved` after the thread is resolved
- `addressed` if the user fixed code but chose not to reply (rare)
- `skipped` if the user moved on without action

```bash
bash scripts/update_status.sh "$CACHE" <index> replied
```

### Step 5 — Wrap up

When all threads are done (no `pending` left), summarize: N replied, N resolved, N skipped.
Mention any uncommitted code changes from fixes the user accepted — remind them to commit/push
so the reviewer can see the changes alongside the replies.

## Important notes

- **Never post without explicit approval.** "Post the reply?" must be answered yes before
  running any post operation.
- **Never resolve without explicit approval.** Resolving silences the reviewer's notification;
  let them confirm the fix is acceptable when in doubt.
- **One thread at a time.** Don't batch. The user wants to think through each one.
- **Reply tone** comes from `REPLY_TONE`. The default is brief, technical, polite, not
  sycophantic; "Done!" is fine for trivial obvious fixes.
- **For diff threads, read the actual file** before judging. The reviewer's quoted snippet
  may be stale if the user pushed after the comment was written.
- **If the fetch returns empty but the PR/MR clearly has comments**, they may all be resolved.
  Mention it; don't act on resolved threads unless the user asks.
- **Prerequisites:** `jq`, plus `gh` (GitHub) or `glab` (GitLab), authenticated.
