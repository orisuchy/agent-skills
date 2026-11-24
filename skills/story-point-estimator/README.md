# story-point-estimator

Sizes a ticket in story points. It fetches the ticket (and its parent, blockers, and linked docs),
scores it on five dimensions (amount of work, familiarity, risk and uncertainty, testing, process
overhead and dependencies), compares it to your team's reference tickets, and picks a value from a
point scale (Fibonacci by default). Points measure size, never hours; the skill refuses to convert
them. Works with Jira (+ Confluence), GitHub Issues, GitLab Issues, and Linear.

## Use cases

- Prepare for planning poker or backlog refinement with a first-pass estimate and reasoning.
- Settle "is this a 5 or an 8?" by comparing against tickets your team already sized.
- Spot tickets that are too big (top of the scale) and get a recommendation to split them.
- Keep a small baseline table of reference tickets and add a newly sized ticket to it.

## Prerequisites

Use **one** tracker connection; the skill picks whichever the agent has:

- **Jira + Confluence:** the Atlassian MCP server
  ([setup guide](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)),
  or the [Atlassian CLI `acli`](https://developer.atlassian.com/cloud/acli/guides/introduction/)
  for Jira only (it has no Confluence commands).
- **GitHub Issues:** [`gh`](https://cli.github.com/manual/gh_issue_view), authenticated.
- **GitLab Issues:** [`glab`](https://docs.gitlab.com), authenticated.
- **Linear:** the [Linear MCP server](https://linear.app/docs/mcp).
- [Python 3](https://www.python.org/downloads/) for `scripts/manage_baseline.py` (standard library only).

Tested on macOS with [Claude Code](https://code.claude.com/docs/en/overview), against Jira via the
Atlassian MCP server. The other adapters follow each tool's official docs but were not run live.
If no tracker tool is available, the skill asks you to paste the ticket text.

## Configuration

- `POINT_SCALE`: default `1,2,3,5,8,13,21`. Edit the table at the top of [`SKILL.md`](SKILL.md) and
  export the same list as the `POINT_SCALE` environment variable so the baseline script accepts it.
- **Baseline table:** [`baseline-table.json`](baseline-table.json) ships with three **fictional**
  example tickets (`PROJ-101`..`PROJ-103`). Build your own from tickets your team has already sized,
  run from the skill folder:

  ```bash
  python3 scripts/manage_baseline.py list
  python3 scripts/manage_baseline.py add --key PROJ-123 --points 5 --summary "..." --notes "..."
  python3 scripts/manage_baseline.py edit --key PROJ-123 --points 8
  python3 scripts/manage_baseline.py remove --key PROJ-101
  ```

  Remove the examples once you have real anchors. Write `--notes` against the five dimensions.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole
`story-point-estimator/` folder, including `scripts/` and `baseline-table.json`.
