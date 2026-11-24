# agent-skills

Ten agent-agnostic skills for everyday engineering work: planning commits, understanding and sizing tickets, handling review comments, and running a feature with a team of agents.

## Skills

| Skill | What it does | Key prerequisite |
|---|---|---|
| [commit-plan](skills/commit-plan/) | Plans commits for uncommitted work across git repos as a markdown table; never commits. | `git`, bash |
| [feature-flow](skills/feature-flow/) | Plans a feature, then dispatches one fresh worker agent per ticket and tracks usage. | [Herdr](https://herdr.dev), Python 3, [Matt Pocock's skills](https://github.com/mattpocock/skills) |
| [make-repo-ai-ready](skills/make-repo-ai-ready/) | Makes a test-automation repo AI ready so agents write tests in the repo's style. | A test repo with `AGENTS.md`, Python 3 |
| [refresh-worktree-board](skills/refresh-worktree-board/) | Scans git worktrees and writes a self-contained HTML status board. | `git`, Python 3 |
| [review-comments](skills/review-comments/) | Walks through unresolved PR/MR review comments, drafts replies, posts after approval. | `gh` or `glab`, `jq` |
| [sprint-init](skills/sprint-init/) | Builds a prioritized `TASKS.md` from your current sprint and finds the next Code Freeze. | A tracker connection (Jira, GitHub, GitLab, Linear) |
| [story-point-estimator](skills/story-point-estimator/) | Sizes a ticket in story points against your team's reference tickets. | A tracker connection |
| [task-overview](skills/task-overview/) | Writes a personal overview of a finished coding session. | `git` (recommended) |
| [ticket-analyzer](skills/ticket-analyzer/) | Summarizes a ticket, its comments and linked docs in plain language. | A tracker connection |
| [ticket-planning-prep](skills/ticket-planning-prep/) | Prepares a ticket for planning: affected code, reuse, open questions, kickoff list. | A tracker connection |

Each folder has its own README with use cases, prerequisites and configuration.

## Install

Every skill is a folder with a `SKILL.md`, following the open [Agent Skills](https://agentskills.io) format. Copy (or symlink) the skill folders you want into your agent's skills directory:

```bash
git clone <this-repo-url> agent-skills
cp -r agent-skills/skills/commit-plan ~/.claude/skills/   # example
```

| Agent | Personal (all projects) | Project |
|---|---|---|
| [Claude Code](https://code.claude.com/docs/en/skills) | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` |
| [OpenAI Codex](https://learn.chatgpt.com/docs/build-skills) | `~/.agents/skills/<name>/` | `.agents/skills/<name>/` |
| [Gemini CLI](https://geminicli.com/docs/cli/skills/) | `~/.gemini/skills/<name>/` or `~/.agents/skills/<name>/` | `.gemini/skills/<name>/` or `.agents/skills/<name>/` |
| [Cursor](https://cursor.com/docs/context/skills) | `~/.cursor/skills/<name>/` or `~/.agents/skills/<name>/` | `.cursor/skills/<name>/` or `.agents/skills/<name>/` |
| [GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | `~/.copilot/skills/<name>/` or `~/.agents/skills/<name>/` | `.github/skills/<name>/` or `.agents/skills/<name>/` |

Notes:

- Supported locations depend on the surface (Copilot CLI, VS Code, cloud agent). Check the linked docs if a skill does not appear.
- Cursor and Copilot also read `.claude/skills/`, so a Claude Code install often works there too.
- The Gemini CLI docs state it was replaced by Antigravity CLI on June 18th, 2026; check the current docs for your version.
- **Any other agent:** if it reads `AGENTS.md` or can load a markdown file, point it at the skill's `SKILL.md` (for example "follow `skills/commit-plan/SKILL.md`"). Keep the skill's folder intact: `SKILL.md` refers to bundled `scripts/` and `references/`.
- **Installer CLI:** `npx skills add <owner>/<repo>` ([vercel-labs/skills](https://github.com/vercel-labs/skills), Node.js 22.20+) installs skills from a GitHub repo into your agent's skills directory; add `-a <agent>` to pick one and `-g` for a global install.

Some skills use Claude Code frontmatter or tools; each skill's README explains what to expect on other agents.

## Acknowledgments

- [Matt Pocock](https://github.com/mattpocock) for [his skills](https://github.com/mattpocock/skills) and the grill, spec, tickets, implement workflow that `feature-flow` builds on.
- The [Herdr](https://herdr.dev) project ([source](https://github.com/herdrdev/herdr)) for the agent-aware terminal that `feature-flow` drives.
- The authors of the [Agent Skills](https://agentskills.io) format, originally developed by Anthropic and released as an open standard.

## Contributing

Issues and pull requests are welcome.

## License

[MIT](LICENSE)
