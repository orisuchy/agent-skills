---
name: refresh-worktree-board
description: Refresh a board of the current state of every git worktree on this machine (dirty, unpushed, merged, safe to remove). Use when the user says "refresh my worktree board", "update worktree board", or asks to sync/rescan their worktrees.
---

# Refresh the Worktree Board

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `ROOTS` | `$WORKTREE_ROOTS`, else `.` | Folders to scan for git repos (pass as args to the scanner) |
| `BOARD_FILE` | `./worktree-board.html` | Where the self-contained HTML board is written |
| `ARTIFACT_URL` | `none` | Only for the optional Claude Artifact mode below |

Ask the user for `ROOTS` once if neither is set and the current directory is not a code folder.

## Default mode (any agent)

1. Run `python3 scripts/worktree-scan.py --html <BOARD_FILE> <ROOTS...>` (path relative to this skill's folder). Without `--html` it prints JSON.
2. Reply with one line: how many worktrees, how many need attention (dirty or unpushed) / are safe to remove (merged, upstream gone, prunable), and the board path.

## Optional: Claude Artifact mode

Only if the agent supports Claude Artifacts and `ARTIFACT_URL` is set (it must be a board artifact with `worktrees` and `meta` collections).

1. Run the scanner without `--html` into a scratch file.
2. Split it into one JSON file per worktree (`<id>.json`, the whole worktree object) plus `meta.json` = `{scannedAt, roots}`.
3. `ArtifactData` `list` the `worktrees` collection (limit 1000) to get existing ids and versions.
4. One `ArtifactData` `batch` (max 50 writes; split if more):
   - `set` each scanned worktree in `worktrees` (doc_id = its `id`, `if_version` when it already exists),
   - `delete` every existing `worktrees` doc whose id is not in the scan (with its `if_version`),
   - `set` `meta/scan` from `meta.json` (`get` it first for `if_version`).
5. Never touch the `notes` collection: that holds the user's own notes.
6. Reply as in default mode, plus the artifact link.
