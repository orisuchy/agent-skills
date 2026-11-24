---
name: commit-plan
description: Scans a folder of git repos (or a single repo) for uncommitted changes, separates work relevant to a given ticket or feature from unrelated noise (personal local config, leftover edits, IDE housekeeping) by asking short clarifying questions, and outputs a commit plan as a markdown table — logically grouped commits, one short message per group, one-line explanation per file. Never creates any actual commits. Use when the user asks to plan commits, split a diff into commits, organize uncommitted changes before committing, or "create a commit plan" — especially when several repos have changes at once.
---

# commit-plan

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `ROOT_DIR` | `.` (current directory) | Folder to scan. Can hold several git repos, or be a single repo. |
| `SCAN_DEPTH` | `5` | How many folder levels below `ROOT_DIR` to look for `.git` directories. |
| `LOCAL_FILE_PATTERNS` | `*-local.*`, `*.local.*` | Filename patterns for personal dev-environment config that should never be part of a feature commit. |
| `COMMIT_STYLE` | `<TICKET-KEY> <imperative summary>` (e.g. `PROJ-123 Add retry to sync job`) | Message format. If the work has no ticket key, use `type: summary` (e.g. `fix: handle empty payload`). |

Change a value by telling the agent in the prompt (e.g. "scan `~/work/clients`, depth 2") or by
editing this table in your copy of `SKILL.md`.

Turns the uncommitted state of one or more git repos into a reviewable commit plan (a table),
without running `git add` or `git commit`. The user commits themselves after reviewing the plan.

## Inputs

Ask only if missing:
- **Ticket/feature description** (e.g. a ticket key plus a short title). This is the filter for
  "relevant vs noise", and you need it before judging any file.

## Workflow

### Step 1 — Discover changed repos

Run the bundled script from this skill's `scripts/` folder, with the configured values:

```bash
bash <skill-dir>/scripts/scan-changes.sh "$ROOT_DIR" "$SCAN_DEPTH"
```

It finds every `.git` directory up to `SCAN_DEPTH` and prints `git status --porcelain` for each
repo that has changes. Repos with nothing changed are silently skipped. If `ROOT_DIR` does not
exist, the script exits with an error; report it and ask for the right folder.

### Step 2 — Triage every changed file

For each file, decide: **relevant**, **noise (auto-skip)**, or **ambiguous (ask)**.

Auto-skip without asking, but still name them in your final summary as excluded:
- `.DS_Store` and other OS junk
- Generic `.gitignore` additions unrelated to the ticket (IDE files, scratch notes, editor prefs)
- Files matching `LOCAL_FILE_PATTERNS` — personal dev-environment tweaks, not part of a feature

Treat as **ambiguous** and batch these into one multiple-choice question covering all of them
(ask the user a multiple-choice question; Claude Code: `AskUserQuestion`; otherwise plain text).
Do not ask one at a time:
- Dependency or version bumps in a manifest (`pom.xml`, `package.json`, `go.mod`, ...) for a
  shared library. Before asking, check whether the bump is relevant:
  `git -C <repo> log --oneline -5`. If another repo already has a recent commit mentioning the
  same ticket key, the bump is relevant and needs no question. If not, ask.
- Changes in a repo or area that looks unrelated to the ticket's subject (e.g. a permissions enum
  change when the ticket is about billing).
- Anything else you can't confidently classify from the diff alone.

Never guess silently on an ambiguous file. A wrong include or exclude corrupts the whole plan.

### Step 3 — Read full diffs for everything marked relevant

Filenames aren't enough. For every file staying in scope:

```bash
git -C <repo> diff -- <file>
```

Understand *what* changed, not just *that* it changed. Watch for incidental noise bundled inside
an otherwise-relevant file's diff (e.g. wildcard imports expanded to explicit ones by an IDE save).
Keep the file in the commit, but call the incidental part out in its explanation rather than
describing it as part of the feature.

### Step 4 — Group into commits

Group by **why**, not by directory or file type. Typical shape for a code change:
1. Shared dependency or library version bump (if any), as its own commit, first
2. Bug fix(es), separate from new feature work
3. Feature implementation with its tests together (tests belong with the code they test, not in
   a separate "add tests" commit)

Each group gets one short message in the configured `COMMIT_STYLE`.

### Step 5 — Output the plan as a table

Columns: `#` | `commit message` | `files` | `what changed`. One row per file. Leave `#` and
`commit message` blank on continuation rows of a multi-file commit so it reads as one group.

After the table, list what was excluded and why (one line each). Mention any related work already
committed in another repo (from the Step 2 `git log` check).

## Important notes

- **Never run `git add` or `git commit`.** This skill only plans. If the user wants it committed,
  that is a separate, explicit request.
- **Keep clarifying questions short and few.** One batched question covers all ambiguous files.
- **One plan per invocation.** If the user adjusts scope after seeing the table (e.g. "also exclude
  file X"), re-render the table. Don't re-run the whole scan.
