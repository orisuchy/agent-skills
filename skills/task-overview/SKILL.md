---
name: task-overview
description: Use this skill at the end of a coding session to generate a personal high-level overview of the work just completed. Produces a markdown file in the configured OUTPUT_DIR summarizing the feature/issue, plan, what was done, files changed and why, and code examples (before/after for fixes, full snippets for new features). Trigger when the user says things like "write up this task", "make me an overview of what we did", "/task-overview", or asks for a recap document of the session's coding work.
---

# Task Overview

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `OUTPUT_DIR` | `~/Documents/task-overviews/` | Folder where overview files are written. Created if missing. Change it by telling the agent in the prompt, or by editing this table in your copy of the skill. |

## Purpose

Generate a single self-contained markdown overview of a coding session that the user can re-read later to quickly recall the work and answer questions about it. Output is for personal use — not a PR description, not a Jira comment, not a stakeholder report.

## When to use

Invoke this skill when the user explicitly asks for an overview / writeup / recap of a coding session, typically right after the work is finished. Do NOT auto-trigger; this is a manual operation.

## Inputs

Use these in priority order:

1. **The current agent session conversation** — primary source. The plan, decisions, debugging path, "why" behind each change, and what was tried-and-discarded all live here. Mine the session aggressively before reaching for git.
2. **Git state** — only as a verification/gap-filling tool. Run `git diff`, `git log`, `git status` in the relevant repo(s) to confirm the final set of changed files, double-check snippets, or recover detail the conversation glossed over.
3. **Ask the user** — only if a critical fact is genuinely missing from both sources (e.g., the ticket ID isn't anywhere). Do not interrogate; one short clarifying question max.

## Workflow

### Step 1 — Detect repos in scope

The session may have touched one repo or several. To find them:

- Look at every file path the agent has read or edited during the session and group by repo root (look upward for `.git`).
- For each detected repo, run `git -C <repo> status --short` and `git -C <repo> diff --stat HEAD` to confirm there are actual changes.
- If a repo shows up in conversation but has no diff, note it in a "touched but not modified" line — don't include it in the file changes section.

### Step 2 — Extract the ticket ID and branch name

Detect a ticket ID (Jira-style: e.g., `PROJ-1234`, `ABC-567`) by checking, in order:

1. The branch name (`git -C <repo> rev-parse --abbrev-ref HEAD`)
2. Recent commit messages on the branch
3. Anything the user said in the session

If multiple repos are involved and they share a branch name, use that. If branches differ across repos, use the branch from the repo with the most changes.

### Step 3 — Decide the output filename

- If a ticket ID was found: `{TICKET_ID}-{branch_name}.md`
- Else: `{branch_name}-{YYYY-MM-DD}.md`
- Else (no branch — detached HEAD or non-repo session): `task-{YYYY-MM-DD-HHMM}.md`

Sanitize: replace `/` with `-`, strip characters that are awkward in filenames.

If the target file already exists, append `-v2`, `-v3`, etc. — never overwrite without telling the user.

### Step 4 — Generate the overview

Create `{OUTPUT_DIR}` if it does not exist, then write `{OUTPUT_DIR}/{filename}.md` using the structure in `references/output_template.md`.

Key rules for content:

- **Feature vs. bug fix vs. change** — classify the work, because it changes how to present code examples:
  - **New feature** → include the **full snippet** of the new function/class/component, not a diff.
  - **Bug fix or modification of existing code** → include a **before/after diff** (or paired snippets) of the key hunk(s). Skip the trivial reformatting; keep the load-bearing change.
  - **Refactor** → before/after of one representative file is usually enough; summarize the pattern for the rest.
- **Files changed and why** — list every modified file with a one-line "why this changed" rationale tied to the plan. If a file was changed for a reason that's only obvious from the conversation (e.g., "had to update this constant because the API returns it in a different format than expected"), capture that — git diff alone won't reveal it.
- **What was actually done vs. plan** — if the work diverged from the original plan (a different approach was chosen, scope was cut, an unexpected blocker came up), call that out. The whole value of this document is recording reasoning that isn't in the diff.
- **Multi-repo** — if more than one repo was touched, group "Files changed" by repo with a heading per repo. Snippets too.
- **Do NOT include** a "Q&A" or "talking points" section. The user does not want one.
- **Tone** — written for one reader (the user) re-reading later. Skip ceremony; be specific and concrete. Identifiers, file paths with line numbers, exact error messages where relevant.

### Step 5 — Confirm and report

After writing the file, tell the user:
- The full path written
- A 1-line summary of what's in it
- Any gaps where information was thin and the user might want to add detail manually

## Reference files

- `references/output_template.md` — the markdown skeleton to fill in. Read this before writing the output.

## Anti-patterns (do not do these)

- Don't pad the document with content reconstructable from `git log` — the value is the *reasoning*, not the file list.
- Don't include a Q&A / talking-points section.
- Don't summarize the *agent session itself* ("we discussed…", "I suggested…"); summarize **the work**.
- Don't paste massive diffs. For changes/fixes, the smallest hunk that conveys the change is right.
- Don't invent context the session doesn't support. If something is unclear, either grep/diff to verify or note it as "unverified" in the doc.
- Don't write the file silently — always report the path back so the user can open it.
