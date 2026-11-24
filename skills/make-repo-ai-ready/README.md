# make-repo-ai-ready

Makes a test-automation repo AI ready, so an agent that is handed a test plan writes tests in the repo's own style, in the right CI job, and reports what it could not prove. The skill scans the repo, agrees with you which pieces to build, writes the docs agents need (writing-tests guide, glossary, generated fixture/marker/CI-job/env catalogs with drift tests, CI-lane and parallel-safety guide, helper diagnosis, optional test-management reading), adds a repo-tracked `write-tests-from-plan` skill, and checks it all with a pilot test. The templates and examples assume a Python/pytest repo; the steps carry over to other runners.

## Use cases

- A team's test repo has tests but no agent guidance, and agents keep writing tests in a different style.
- You want agents to know which CI job (and which parallel lane) a new test belongs in.
- You want fixture, marker, CI-job and env-var docs that cannot silently go stale (generated, with a test that fails on drift).
- You want your team's code-review rules reconciled with the repo docs, rule by rule, with evidence.
- You want to bring the same test-writing skill to a second automation repo, using the first as a reference.

## Prerequisites

- A test repo that already has `AGENTS.md`, a `CLAUDE.md` (or equivalent) pointing to it, an agent-workflow doc, an offline gate command (a fast check that runs without live services) and a PR/MR template. The skill stops and tells you if any is missing.
- Python with pytest for the bundled `templates/test_skill_overlap.py` (standard library `unittest` only).
- Optional: the [`feature-flow`](../feature-flow/) skill for long builds; without it the phases run serially.
- Optional: a test-management tool (Testmo, TestRail, Xray) with an MCP server or API token, if plans live there.
- Optional: a second, already AI-ready repo to use as `REFERENCE_REPO`.

Tested on macOS with [Claude Code](https://code.claude.com/docs/en/overview). The GitHub Actions guidance follows the [GitHub Actions docs](https://docs.github.com/en/actions) and the GitLab CI guidance the GitLab CI/CD docs (docs.gitlab.com); neither was run against a live pipeline here. Some steps name Claude Code features (subagents, `/implement`, `/review`); each has a fallback in the skill text.

## Configuration

Settings are in the **Configuration** table at the top of [`SKILL.md`](SKILL.md):

- `REFERENCE_REPO`: default empty. Path of a finished AI-ready repo to read for shapes.
- `TEST_MGMT`: default `none`. `testmo`, `testrail`, `xray` or `none`.
- `CI`: default detected. `github-actions` or `gitlab-ci`.
- `REVIEWER_RULE_FILES`: default none. Review-rule files to reconcile.
- `OUTPUT_DIR`: default `.scratch/ai-ready`. Repo map and pilot report.
- `AGENT_SKILLS_DIR`: default `.claude/skills`. Where the repo skill is written.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole `make-repo-ai-ready/` folder, including `references/` and `templates/`.
