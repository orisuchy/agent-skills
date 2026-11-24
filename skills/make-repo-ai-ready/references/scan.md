# Scan: understand the repo and decide how to steer agents

Read-only. Never read or print `.env*` or credential values. Fill one row per component; the shape column is
what makes this repo different from `REFERENCE_REPO` (or from the generic shape described here).

## What to read
1. `AGENTS.md`, `CLAUDE.md`, `README.md`, every `docs/*.md`, `CONTEXT.md`, the PR/MR template, `<AGENT_SKILLS_DIR>`.
2. 3–5 recent tests (`git log --diff-filter=A --name-only -- <tests dir>`), plus one old one, to see the style
   the team wants now versus legacy.
3. Test plumbing: root `conftest.py` (`pytest_plugins` list or plain fixtures?), `pytest.ini`/`pyproject.toml`
   (markers, `addopts`: flag `-l`), lock plugins (`FileLock`, `xdist_group`).
4. CI: `.gitlab-ci.yml` and every `include:` file, or every `.github/workflows/*.yml` (and reusable workflows /
   composite actions they call). Stages or jobs, `pytest -m` selectors, `-n`/`--dist`, concurrency control
   (GitLab `resource_group`, GitHub `concurrency`), `timeout`, `--reruns`, job retry, job dependencies
   (`needs`). Consumers of job names: grep sibling CI/reporting repos for this repo's name.
5. Helpers: where tests get their API. Installed packages from a shared helper library (find the folder with
   `python -c "import importlib.util,pathlib;print(pathlib.Path(importlib.util.find_spec('<pkg>').submodule_search_locations[0]))"`
   and check for `<pkg>/AGENTS.md`, `<pkg>/API.md`), in-repo helper packages, or page objects (UI repos).
6. Env vars: one declaring module (e.g. `config/run_settings.py`) or scattered `os.environ`/`os.getenv`.
7. Reporting: Allure usage (`allure.step`, `allure.link`), test-management markers (e.g. `testmo_<id>`), the
   test-management project(s).

## Components
| # | Component | Applies when | Shape varies by |
|---|---|---|---|
| C1 | Base agent files | always | missing → blocked-by-base |
| C2 | Writing-tests guide (shape, reference tests, markers, ids, where to find things, checking a test) | always | test style, base class, polling helper |
| C3 | Product glossary `CONTEXT.md` (plan term → fixture/helper → example test) | tests use product terms | product area |
| C4 | Fixtures catalog + docstrings + drift test | fixtures registered in one place | no registry → blocked-by-base |
| C5 | Markers catalog (marker → jobs, lock, parallelism) + drift test | selection by marker in CI | include files, selectors |
| C6 | CI-jobs guide + generated jobs table | always | lanes, `-n`, concurrency control |
| C7 | Env-var docs + drift test | one declaring module | scattered reads → blocked-by-base |
| C8 | Helper docs pointer + helper diagnosis | tests call helpers | packages / in-repo / page objects |
| C9 | Test-management reading + PR/MR "test cases" section | `TEST_MGMT` is not `none` and tests carry case ids | project ids |
| C10 | Repo skill `write-tests-from-plan` + overlap check | always | doc anchors |

## Output row
`| C# | applies/exists/skip/blocked-by-base | evidence (file:line) | shape in this repo | gap |`

Mark "exists" only when the doc covers what the reference build covers for that component, not when a file
with that name exists. A UI repo still gets C2, C3, C6, C9, C10; C8 becomes "page objects
and their docs", and the C8 diagnosis rules apply to page-object methods that swallow failures.
