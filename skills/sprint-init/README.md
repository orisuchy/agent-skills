# sprint-init

Sets up your sprint board in one go. It fetches your open tasks in the current sprint, iteration, or cycle from your tracker, sorts them into Features, Technical, and Bugs, resolves bug sub-tasks to their parent's priority, looks up the next Code Freeze date in your calendar, and writes a prioritized `TASKS.md` plus a short sprint snapshot. Works with Jira, GitHub, GitLab, and Linear.

## Use cases

- It is the first day of a sprint and you want a clean, prioritized `TASKS.md`.
- You want to re-sync your board after tickets were added or moved mid-sprint.
- You need to know how many days remain until Code Freeze.
- You want bug sub-tasks shown under their parent, with the parent's priority.
- You want critical (Highest) bugs flagged at the top.

## Prerequisites

Use **one** tracker connection; the skill picks whichever the agent has:

- **Jira:** the Atlassian MCP server ([setup guide](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)).
- **GitHub:** [`gh`](https://cli.github.com/manual/gh_issue_list) (milestones) or [`gh project`](https://cli.github.com/manual/gh_project_item-list) (iterations), authenticated.
- **GitLab:** [`glab`](https://docs.gitlab.com), authenticated.
- **Linear:** the [Linear MCP server](https://linear.app/docs/mcp).
- Optional, for Code Freeze lookup: a calendar MCP server (Outlook via [Microsoft 365 MCP](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/) or a Google Calendar MCP). Without one, the Code Freeze step is skipped.

Tested on macOS with [Claude Code](https://code.claude.com/docs/en/overview), against Jira and Outlook. The GitHub, GitLab, Linear, and Google Calendar adapters follow each tool's official docs but were not run live.

## Configuration

Settings are in the **Configuration** table at the top of [`SKILL.md`](SKILL.md):

- `TASKS_FILE`: default `./TASKS.md`. The board file that is rewritten.
- `MEMORY_DIR`: default `./memory`. Where sprint snapshot and reference notes go.
- `WIKI_LOG`: default `none`. Set a path (e.g. `./wiki/_log.md`) to append a log entry.
- `CALENDAR`: default `none`. `outlook`, `google`, or `none`.
- `FREEZE_KEYWORD`: default `Code Freeze`. The calendar event subject to match.

The tracker, project key / repo / team, and extra filters are detected or asked each run.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole `sprint-init/` folder.
