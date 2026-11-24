# ticket-planning-prep

Prepares a ticket for implementation planning. It fetches the ticket, comments, linked tickets, and
linked docs (such as Confluence pages), explores your codebase for affected files and reusable
code, surfaces technical questions, outlines implementation approaches, and writes a planning-ready
summary with a concrete kickoff list. It can also create a work branch. Works with Jira
(+ Confluence), GitHub Issues, GitLab Issues, and Linear.

## Use cases

- You were assigned a ticket and want to know which files it touches before you plan.
- You want a DRY check: existing helpers or utilities you can reuse instead of writing new ones.
- You want open technical questions and risks listed before you start coding.
- You want the analysis saved as Markdown so a fresh session can start coding from it.
- You want a work branch named after the ticket, created from your default branch.

## Prerequisites

Use **one** tracker connection; the skill picks whichever the agent has:

- **Jira + Confluence:** the Atlassian MCP server
  ([setup guide](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)),
  or the [Atlassian CLI `acli`](https://developer.atlassian.com/cloud/acli/guides/introduction/)
  for Jira only (it has no Confluence commands).
- **GitHub Issues:** [`gh`](https://cli.github.com/manual/gh_issue_view), authenticated.
- **GitLab Issues:** [`glab`](https://docs.gitlab.com), authenticated.
- **Linear:** the [Linear MCP server](https://linear.app/docs/mcp).
- A git repository for code discovery and the branch step.

Tested on macOS with [Claude Code](https://code.claude.com/docs/en/overview), against Jira via the
Atlassian MCP server. The other adapters follow each tool's official docs but were not run live.
If no tracker tool is available, the skill asks you to paste the ticket text.

## Configuration

Settings are in the **Configuration** table at the top of [`SKILL.md`](SKILL.md):

- `OUTPUT_DIR`: default `./notes`. Where saved analyses go, as `<TICKET-ID>-analysis.md`.
- `BASE_BRANCH`: default is the repo's default branch. The branch the new work branch starts from.

Edit the table, or tell the agent different values when it asks.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole
`ticket-planning-prep/` folder.
