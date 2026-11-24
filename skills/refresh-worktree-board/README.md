# refresh-worktree-board

Scans your machine for git repos that have extra worktrees and writes a single self-contained HTML board: branch, ticket key, dirty files, unpushed/behind counts, last commit, and a status (needs attention / safe to remove). Optionally it syncs the same data into a Claude Artifact.

## Use cases

- You have many worktrees across repos and want to know which still hold unpushed work.
- You want a list of worktrees safe to remove (branch merged, upstream deleted, or directory gone).
- You want to spot dirty worktrees you forgot about.
- You want a shareable, no-server HTML snapshot of all your in-flight branches.

## Prerequisites

- `git` and Python 3 (stdlib only).
- Optional: an agent with [Claude Artifacts](https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them) for the artifact mode.

Tested on macOS with [Claude Code](https://code.claude.com/docs/en/overview). The scanner never runs `git fetch`, so ahead/behind is as of your last fetch.

## Configuration

Settings are in the **Configuration** table at the top of [`SKILL.md`](SKILL.md):

- `ROOTS`: default `$WORKTREE_ROOTS` (path-separated), else the current directory. Folders to scan.
- `BOARD_FILE`: default `./worktree-board.html`. Output board.
- `ARTIFACT_URL`: default `none`. Set to your own board artifact to enable artifact mode.

Check the scanner works: `scripts/selfcheck.sh`.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole `refresh-worktree-board/` folder (the `scripts/` are required).
