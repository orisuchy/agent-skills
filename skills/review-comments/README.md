# review-comments

Walks you through the unresolved review comments on a pull request or merge request, one thread
at a time. For each thread it explains what the reviewer wants in plain language, judges whether
the point is valid after reading the code, suggests the smallest fix, and drafts a reply. It posts
the reply and resolves the thread only after you approve. Works on GitHub and GitLab (including
self-hosted); Bitbucket and Azure DevOps are described as REST steps.

## Use cases

- A teammate left a dozen comments on your PR and you want to triage them without losing track.
- You are new to a team and want help judging which review comments are right and how to reply politely.
- You want a short, consistent reply to each thread, and a record of which ones you answered or resolved.
- You want to resume a half-finished review pass: progress is cached per PR/MR.
- You are a reviewer's author on a self-hosted GitLab and want the same flow as on GitHub.

## Prerequisites

- **jq**: [jqlang.org](https://jqlang.org/). Used by the bundled scripts.
- **bash**: the bundled scripts are bash.
- **GitHub CLI `gh`**, authenticated, for GitHub: [cli.github.com](https://cli.github.com/manual/).
- **GitLab CLI `glab`**, authenticated, for GitLab: [GitLab docs](https://docs.gitlab.com/).
  Self-hosted: `glab auth login --hostname <host>`.
- **An AI coding agent that can read `SKILL.md` and run shell commands.** Tested on macOS with
  [Claude Code](https://code.claude.com/docs/en/overview), against GitLab. The GitHub adapter was
  checked against a mocked `gh` response, not a live PR.

No MCP servers or other skills are needed.

## Configuration

Settings are in the **Configuration** table at the top of [`SKILL.md`](SKILL.md):

- `REPLY_TONE`: default [`references/reply_tone.md`](references/reply_tone.md) (a junior developer
  replying to senior reviewers). Point it at your own file or describe a tone in the prompt.
- `CACHE_DIR`: default `/tmp/review-comments`. Override with the `REVIEW_CACHE_DIR` environment variable.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole
`review-comments/` folder, not just `SKILL.md`, because the skill runs the scripts in `scripts/`
and reads `references/reply_tone.md`.
