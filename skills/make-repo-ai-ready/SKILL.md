---
name: make-repo-ai-ready
description: Makes a test-automation repo AI ready, so an agent given a test plan writes tests in the repo's style. Scans the repo to decide how to steer agents in it, reconciles the team's reviewer rules with the repo docs, adds the docs agents need (writing-tests guide, product glossary, generated fixture/marker/CI-job/env catalogs with drift tests, CI-lane and parallel-safety guide, test-management reading, helper diagnosis), writes the repo-tracked write-tests-from-plan skill, and checks it all with a pilot test from a real test case. Use when asked to "make <repo> AI ready", "AI readiness for <repo>", "add tests-from-plan to <repo>", "create the write-tests-from-plan skill for <repo>", or "bring the test-writing skill to another automation repo".
---

# Make a repo AI ready

Goal: an agent handed a test plan writes tests in this repo's style, in the right CI job, and reports what it
could not prove. Every rule lives in the repo's `AGENTS.md` and `docs/*.md`; skills hold steps and links only.
Examples below use pytest; for another runner, keep the steps and swap the mechanics.

## Configuration
| Setting | Default | Meaning |
|---|---|---|
| `REFERENCE_REPO` | empty | Path of an already AI-ready test repo to read for shapes. Read its files, never copy them: they hold its facts. May be empty; then use only this skill's references. |
| `TEST_MGMT` | `none` | Test-management tool the plans live in: `testmo`, `testrail`, `xray`, `none`. `none` skips C9 and the case-link steps. |
| `CI` | detected | `github-actions` or `gitlab-ci` (from `.github/workflows/` or `.gitlab-ci.yml`); ask if neither. |
| `REVIEWER_RULE_FILES` | none | Files holding the team's code-review rules, to reconcile in phase 2. |
| `OUTPUT_DIR` | `.scratch/ai-ready` | Where the repo map and pilot report go. |
| `AGENT_SKILLS_DIR` | `.claude/skills` | Where the repo skill goes (`.agents/skills` for agents that read that). |

If `REFERENCE_REPO` is a git repo whose files are not on its default branch yet, find a ref with
`git -C <REFERENCE_REPO> log --all --oneline -1 -- docs/ci-jobs.md` and read with `git show <ref>:<path>`.
Lessons and pitfalls: [REFERENCE.md](REFERENCE.md).

## 0. Preconditions (stop if any fails)
- Target is a test repo. Refuse shared helper libraries (their docs are their own `AGENTS.md`/`API.md`), CI
  control repos and reporting repos.
- It has `AGENTS.md`, a `CLAUDE.md` (or equivalent) pointing to it, an agent-workflow doc, an offline gate command
  and a PR/MR template. Missing any: stop and tell the user to add that base layer first (or do it as a separate task).
- Ask once: base branch, tracker key convention for branches (e.g. `PROJ-123-<slug>`), `REVIEWER_RULE_FILES`,
  `TEST_MGMT`, beta/staging runs allowed yes/no.
- Long effort: run phases 3–6 through the `feature-flow` skill if installed (one ticket per component), else serially here.

## 1. Scan (read-only)
Follow [references/scan.md](references/scan.md). Output `<OUTPUT_DIR>/repo-map.md`: per component
(C1–C10) **applies / exists / skip / blocked-by-base**, with `file:line` evidence and the shape it takes in this
repo. Verify the map with a separate read-only agent (a cheaper model is fine; Claude Code: a subagent on Haiku);
spot-check its most severe finding yourself.

## 2. Decide with the user
- Show the repo map. Ask per component (up to 4 per question): build, skip, or defer. Recommend with this repo's data.
- Reconcile reviewer rules: only rules missing from the docs or conflicting with them. Ask per rule with evidence
  ("type hints: 0 of 79 tests"). Never adopt or drop one silently; not-adopted rules go in the PR "Change" section.
- Check REFERENCE "Must exist in the docs" against the repo; propose each missing item the same way.

## 3. Docs and catalogs
- Each adopted rule goes in the doc that owns the topic, never in a skill.
- Hand-written: writing-tests guide (C2), glossary (C3), helper and test-management sections
  ([references/test-management-and-helpers.md](references/test-management-and-helpers.md)), CI guide ([references/ci-jobs.md](references/ci-jobs.md)).
- Generated, with drift tests: [references/catalogs.md](references/catalogs.md).
- A rule an offline test can check gets a check in the structural gate. Existing violations go in a
  `unit_tests/_<rule>_legacy.txt` list the check reads; the list may only shrink (stale entries fail).
- AGENTS.md: one pointer line per new doc, one "keep the docs in sync" line per generator.
- Run the gate; paste counts before → after. Have a separate read-only agent check each hand-written guide against
  its source (CI YAML, conftest, helper docs); fix every false claim it finds.

## 4. Repo skill
- Copy [templates/write-tests-from-plan.SKILL.md](templates/write-tests-from-plan.SKILL.md) as `SKILL.md`, and
  [templates/ticket-template.md](templates/ticket-template.md), into `<AGENT_SKILLS_DIR>/write-tests-from-plan/`.
  Replace every `{{…}}` with this repo's doc links and anchors. Delete a line whose target does not exist; never invent a doc for it.
- Every link resolves. No `.scratch/` links, no local absolute paths, no personal-skill dependency without a fallback.
- One pointer line under AGENTS.md's agent-skills section, one layout line in the README.

## 5. Guards
- Add [templates/test_skill_overlap.py](templates/test_skill_overlap.py) to the repo's agent-files test (or as a new
  structural test in the gate; set `SKILLS_DIR` in it if not `.claude/skills`). Fix an overlap by deleting the skill line, not the doc line.
- Each generator from phase 3 has its drift test in the offline gate. Run the gate.

## 6. Pilot
- With the user, pick one real test case whose helpers are known to work. Second pilot: a different area.
- Run `/write-tests-from-plan` on it in a fresh agent, in a worktree on a throwaway branch (never pushed),
  symlinking `.venv` (and `.env` if needed). The agent asks the user; you do not answer for them.
- Beta/staging run only with the user's yes, once per test.
- The pilot report must name the CI job, the parallel-safety verdict and the neighbour findings (exercises C6).
- Write `<OUTPUT_DIR>/pilot.md`: result, files, gate counts, rules followed, questions asked, cost, numbered
  "Remaining gaps". Fix each gap in the skill (step) or the docs (rule); rerun the gate.
- Bugs outside the repo (helpers, product): report separately; ask before opening any tracker ticket.

## 7. PR/MR
- One PR/MR to the base branch from the repo's template: components built and skipped, adopted / not-adopted rules,
  checks added, gate output, pilot results. "Not verified": cases piloted, by whom, what only CI or a beta run proves.
- Do not push or open it before the user says so. Remove pilot worktrees when done.
