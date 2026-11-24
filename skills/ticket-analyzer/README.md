# ticket-analyzer

Turns a ticket into a plain-language summary for a developer who is new to the project. It fetches
the ticket, its comments, linked tickets, linked docs (such as Confluence pages), and optionally
attachments, then explains what the ticket wants, why it matters, the rough scope, key decisions
from the comments, and dependencies. It is for *understanding* a ticket, not planning the
implementation. Works with Jira (+ Confluence), GitHub Issues, GitLab Issues, and Linear.

## Use cases

- You were assigned a ticket with a long comment thread and want the decisions pulled out.
- You are new to a codebase and want jargon explained inline.
- You want a quick 2-4 sentence preview before reading the full summary.
- You want the summary saved as Markdown, text, Word, or PDF, or translated into another language.
- You want to see how a ticket fits into its parent or epic and what blocks it.

## Prerequisites

Use **one** tracker connection; the skill picks whichever the agent has:

- **Jira + Confluence:** the Atlassian MCP server
  ([setup guide](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)),
  or the [Atlassian CLI `acli`](https://developer.atlassian.com/cloud/acli/guides/introduction/)
  for Jira only (it has no Confluence commands).
- **GitHub Issues:** [`gh`](https://cli.github.com/manual/gh_issue_view), authenticated.
- **GitLab Issues:** [`glab`](https://docs.gitlab.com), authenticated.
- **Linear:** the [Linear MCP server](https://linear.app/docs/mcp).
- Optional, for `.docx`/`.pdf` output: a docx or pdf skill or tool. Without one, the skill offers Markdown.

Tested on macOS with [Claude Code](https://code.claude.com/docs/en/overview), against Jira via the
Atlassian MCP server. The other adapters follow each tool's official docs but were not run live.
If no tracker tool is available, the skill asks you to paste the ticket text.

## Configuration

Settings are in the **Configuration** table at the top of [`SKILL.md`](SKILL.md):

- `OUTPUT_DIR`: default `./notes`. Where saved summaries go, as `<TICKET-ID>-Summary.<ext>`.
  Edit the table, or tell the agent a different folder when it asks.

Output mode, language, and file format are asked each run.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole
`ticket-analyzer/` folder.
