# commit-plan

Plans commits for uncommitted work across one or more git repos. It scans the folder for changed
repos, separates the changes that belong to a ticket or feature from unrelated noise, and outputs a
commit plan as a markdown table: logically grouped commits, one short message per group, and a
one-line explanation per file. It never runs `git add` or `git commit`; you review the plan and
commit yourself.

## Use cases

- You changed several repos for one ticket and want the work split into clean, reviewable commits.
- Your working tree has leftover edits, IDE housekeeping, or personal local config mixed in with a
  feature, and you want those kept out of the commits.
- You want a dependency bump committed separately from the bug fix and the feature that use it.
- You want a quick, readable summary of what changed in each file before you commit.

## Prerequisites

- **git**: [git-scm.com/doc](https://git-scm.com/doc). The bundled script runs `git status`, and the
  skill uses `git diff` and `git log`.
- **bash**: the bundled `scripts/scan-changes.sh` is a bash script. Any recent bash or zsh works.
- **An AI coding agent that can read `SKILL.md` and run shell commands.** Tested on
  [Claude Code](https://code.claude.com/docs/en/overview). Other agents work too, as long as they can
  run the script. A multiple-choice question tool is optional. Without one, the agent asks in plain
  text.

No MCP servers, accounts, or other skills are needed.

## Configuration

Settings live in the table at the top of `SKILL.md`, under **Configuration**:

| Setting | Default | How to change it |
|---|---|---|
| `ROOT_DIR` | `.` (current directory) | Tell the agent which folder to scan, or edit the default in `SKILL.md`. |
| `SCAN_DEPTH` | `5` | Same as above. Lower it if the scan is slow in a large folder tree. |
| `LOCAL_FILE_PATTERNS` | `*-local.*`, `*.local.*` | Add the filename patterns your personal config uses. |
| `COMMIT_STYLE` | `<TICKET-KEY> <imperative summary>` | Replace with your team's commit message format. |

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole
`commit-plan/` folder, not just `SKILL.md`, because the skill runs `scripts/scan-changes.sh`.
