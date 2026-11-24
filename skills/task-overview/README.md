# task-overview

Writes a personal, high-level overview of a coding session when you finish a piece of work. The
output is one markdown file covering the feature or issue, the plan, what was actually done, the
files changed and why, and code examples (before/after for fixes, full snippets for new features).
It is meant for you to re-read later, not as a PR description or stakeholder report. The skill runs
only when you ask for it.

## Use cases

- You finished a ticket and want a written record of the reasoning, which the diff alone does not
  show.
- You come back to a feature weeks later and need to recall why a file changed.
- You worked in several repos for one task and want one document that groups the changes by repo.
- You want the dead ends and deviations from the original plan written down, not just the final code.

## Prerequisites

- **git** (recommended): [git-scm.com/doc](https://git-scm.com/doc). The skill uses `git status`,
  `git diff`, `git log` and `git rev-parse` to find the changed files, the branch and the ticket ID.
  Without a repo, it still writes an overview from the session conversation.
- **An AI coding agent that can read `SKILL.md`, read and edit files, and run shell commands.**
  Tested on macOS with [Claude Code](https://code.claude.com/docs/en/overview). Other agents should
  work the same way. Asking a question is optional; without a question tool, the agent asks in plain
  text.

No MCP servers, accounts, or other skills are needed.

## Configuration

The setting (`OUTPUT_DIR`) and its default are in the **Configuration** table at the top of
[`SKILL.md`](SKILL.md). Change it by telling the agent in the prompt, or by editing that table in
your copy of the skill.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole
`task-overview/` folder, not just `SKILL.md`, because the skill reads `references/output_template.md`.
