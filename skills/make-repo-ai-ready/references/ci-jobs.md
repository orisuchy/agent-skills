# CI-jobs guide (C6)

An agent writing a test must know which job runs it, whether it is safe there, and when to propose a new job.
Reference shape: `docs/ci-jobs.md` (hand-written sections 1–6, generated table at the end).

Terms differ by CI system; use the repo's own words in its guide:

| Concept | GitLab CI | GitHub Actions |
|---|---|---|
| Pipeline file(s) | `.gitlab-ci.yml` + `include:` files | `.github/workflows/*.yml` + reusable workflows (`workflow_call`) |
| Serialize whole jobs across runs | `resource_group` | `concurrency: group:` |
| Job timeout | `timeout` | `timeout-minutes` |
| Job retry | `retry` | none built in (re-run failed jobs, or a retry action); say so if the repo has none |
| Pipeline inputs | `variables`, `workflow:rules`, pipeline triggers | `workflow_dispatch` `inputs:` |
| Job ordering | `stages`, `needs` | `needs` |

## Sections the repo's guide needs
1. **How a test reaches CI**: pipeline inputs (env, component, suite, run type, test-case id), how env picks jobs,
   how `pytest -m` selects, which inputs bypass lanes.
2. **Choosing the lane**: product area → lane marker (via the markers catalog), the catch-all lane and who excludes
   it, the "also on prod" marker, what the lane fixes (stage, concurrency group, `-n`, reruns, timeout, retry).
   No fitting lane → stop and ask.
3. **Parallel and shared-state safety**: what `-n N` means on one tenant; this repo's locks (how they are keyed,
   first match only?, per working directory = per job only); `xdist_group` works only with `--dist loadgroup`;
   the concurrency group serializes whole jobs across runs, never tests inside one job. One real example from this
   repo. A verdict format: `safe` or `unsafe: <what it changes>, <what protects it, or nothing>`.
4. **Runtime**: job timeout (unknown default stated as unknown; GitHub's default is 360 minutes, GitLab's is
   project-set), reruns cost `(1 + reruns) x runtime + reruns x delay`, job retry restarts all reruns, estimate from sleeps and polls.
5. **When to propose a new job**: (a) shared state nothing protects, (b) runtime near the timeout, (c) a new
   component with no lane. Proposal template (name following the table's pattern, stage, concurrency group,
   selector, parallel, reruns/retry, why no job fits). Proposal only: CI edits are stop-and-ask.
6. **Audit neighbours**: report (never fix) tests of the same lane that change shared state unprotected, lack a
   positive control, or carry a marker no job selects.

## Wire it in
- agent-workflow "Reporting": a test-authoring report names the job(s), the parallel-safety verdict, any new-job
  proposal and the neighbour findings.
- AGENTS.md "Writing a test": one pointer line. Sync rule: a CI selector/job/stage/concurrency change →
  regenerate the table and recheck the guide text.
- State job-name consumers (other repos or dashboards that read job names) and that job names never change.

## Pitfalls
- Write facts about this repo's YAML, not the reference's. Then have a second agent check every claim against the YAML;
  in the reference build it found two false ones (a run type that selects nothing; a bypass that still runs a healthcheck).
- Cite jobs by name, never by YAML line number.
- Check every lane for `-n` without `loadgroup` next to `xdist_group` markers: a real gap found in practice (prod lanes).
