# feature-flow

Build a feature with a team of agents inside [Herdr](https://herdr.dev). You plan with one orchestrator agent in your own pane (grill the idea, write a spec, cut it into tickets), then it dispatches one fresh worker agent per ticket into panes beside you, each running the implement skill. Workers can be Claude Code (the default), Codex, Gemini CLI, Copilot CLI or any other agent Herdr can start, mixed in one run. It watches them, answers what the spec already answers, brings you everything else, escalates failing tickets to a stronger model (tier defaults exist for Claude Code; other agents need a model id), and keeps a per-agent usage ledger. You stay in one pane and make the decisions.

## Use cases

- A feature big enough for a spec and 3-10 tickets, and you want each ticket built by a fresh agent with a clean context.
- Cheap models for mechanical tickets and a stronger one for judgment calls, chosen per ticket and shown to you before anything runs (Claude Code by tier; other agents by model id).
- Several independent tickets built at once, each in its own git worktree (opt-in).
- A worker is stuck or keeps failing: the orchestrator notices, steers or restarts it, and sends a diagnosis agent.
- Your PR/MR got review comments: a review agent walks you through them while fix tickets go to new workers.
- One ticket on a different agent (e.g. Codex) while the rest stay on Claude Code.
- After the run, a token-usage and `/cost` table per agent (Claude Code workers only; others show `n/a`).

## When not to use it

- A change you can make in one sitting with one agent. The planning and dispatch overhead is not worth it.
- You are not inside Herdr. The skill stops at once without `HERDR_ENV=1`.
- The idea is still foggy. Run `/wayfinder` first and come back at `/to-spec`.

## How it works

### Phase flow

```mermaid
flowchart LR
  B[Phase 0: Bootstrap<br/>tracker setup if missing] --> P[Phase 1: Plan<br/>grill → spec → tickets<br/>+ model per ticket]
  P -->|you approve| D[Phase 2: Dispatch<br/>frontier loop]
  D -->|ticket done| D
  D -->|stuck / failed| X[escalate model<br/>or diag agent]
  X --> D
  D -->|all done| F[Finish<br/>full test run, summary,<br/>usage table]
```

The **frontier** is every ticket whose blockers are done. For each one the orchestrator starts a fresh worker, prompts the implement skill on the ticket (`/implement <ticket>` on Claude Code), waits, and then checks for a commit and test output, because an idle agent is not proof of done. A worker that asks a question settles as idle; the orchestrator answers only what the spec answers outright and relays the rest to you verbatim.

### Pane layout

```
┌──────────────────────┬──────────────────────┐
│                      │ impl-01              │
│   orchestrator       ├──────────────────────┤
│   (you talk here)    │ impl-02 / diag /     │
│                      │ research / proto     │
│                      ├──────────────────────┤
│                      │ review               │
└──────────────────────┴──────────────────────┘
```

Workers split down the right column without taking focus. From the 4th worker on, each gets its own tab. Each pane is closed as soon as its agent finishes. The bundled `scripts/ff.py` does all pane, ledger and cost bookkeeping, and it only ever closes panes it opened.

### Agent roles

| Role | Model tier | Started when | Runs |
|---|---|---|---|
| orchestrator | planner | you invoke the skill | grilling, spec, tickets, dispatch |
| `impl-NN` | per ticket: mechanical or implementer | a ticket reaches the frontier | `/implement <ticket>` |
| `diag` | implementer | a ticket or bug resists a first fix | `/diagnosing-bugs` |
| `research` | implementer | a question needs primary-source reading | `/research` |
| `proto` | implementer | grilling needs runnable code to decide | `/prototype` via a `/handoff` file |
| `review` | implementer | the PR/MR has reviewer comments | `/review-comments` (you answer in its pane) |
| `setup` | implementer | the repo has no tracker setup | `/setup-matt-pocock-skills` |

### Example session

```
you   › /feature-flow add CSV export to the reports page
orch  › (grills you about formats, size limits, permissions; writes the spec)
orch  › 4 tickets: 01-export-endpoint (implementer), 02-csv-writer (mechanical),
        03-ui-button (mechanical), 04-permissions (implementer). Approve?
you   › yes, make 04 opus, and run 02 on codex
        ── pane "impl-01" opens on the right, runs /implement, commits, closes
        ── "impl-02" starts as codex, prompted "Use the implement skill on …"; commits, closes
        ── "impl-03" fails on haiku → rerun as impl-03b on the implementer tier (sonnet)
        ── impl-04 asks "should admins bypass the row limit?" → orch relays it to you
you   › no
orch  › all 4 done, full suite green. Want a usage summary?
you   › yes
orch  › (table per agent; impl-02 shows n/a: token and /cost capture are Claude Code only)
```

## Prerequisites

- [Herdr](https://herdr.dev) ([source](https://github.com/herdrdev/herdr)), with its `herdr` skill installed for the orchestrator. Commands were checked against herdr 0.9.5.
- An agent that loads Agent Skills, for the orchestrator (it only needs to run shell commands) and the workers. Default and fully tested: [Claude Code](https://code.claude.com/docs/en/overview) in both roles. Other kinds: see the table below.
- Python 3 (standard library only) for `scripts/ff.py`, `scripts/usage.py` and the self-check `scripts/test_ff.py`.
- [Matt Pocock's skills](https://github.com/mattpocock/skills):
  - Required: `setup-matt-pocock-skills`, `grill-with-docs`, `to-spec`, `to-tickets`, `implement`.
  - On demand: `wayfinder`, `diagnosing-bugs`, `research`, `prototype`, `handoff`.
- Optional: the sibling [`review-comments`](../review-comments/) skill for the `review` agent.
- git, for commits and parallel worktrees. Without git the skill runs serially and does not commit.

### Supported agents

`ff.py start --kind <kind>` accepts any kind `herdr agent start --help` lists (claude, codex, gemini, cursor, copilot, opencode, amp, ...). What differs per kind:

| Kind | How a skill is invoked | Model flag | `/cost` + token usage |
|---|---|---|---|
| `claude` (default) | `/implement <ticket>` | `--model`; tiers default to opus/sonnet/haiku | yes (Claude Code only) |
| `codex`, `gemini`, `copilot` | `Use the implement skill on <ticket>.` | `--model`, only for a literal model id; tiers use the agent's default | `n/a` |
| other Herdr kinds | `Use the implement skill on <ticket>.` | not passed (flag unverified): the agent's default model | `n/a` |

The `--model` flag was checked in `gemini --help` and `copilot --help`, and in the [Codex CLI docs](https://developers.openai.com/codex/cli/reference). Claude-only features: `/cost` capture, `usage.py` token counts, the `/setup-matt-pocock-skills` slash trigger, and the tier defaults. The worker must have Matt Pocock's skills installed for its own agent. Only `claude` workers were run end to end.

## Configuration

The **Configuration** table at the top of [`SKILL.md`](SKILL.md):

- `SKILL_DIR`: default the folder holding `SKILL.md`, resolved by the agent. Set it explicitly there if your agent cannot resolve it.
- `FF`: default `python3 $SKILL_DIR/scripts/ff.py`.
- `AGENT_KIND`: default `claude`. The worker kind passed as `--kind` to `ff.py start`; the user can pick another kind per ticket.
- Model tiers. Each ticket's `**Model:**` line holds a tier (`planner`, `implementer`, `mechanical`) or a literal model id; on-demand agents and escalations use `IMPLEMENTER` (default `implementer`).

  | Tier | Setting | Used for | `claude` default (other kinds: their own) | Pick instead |
  |---|---|---|---|---|
  | planner | none: the model you start the session on | the orchestrator: grilling, spec, tickets, dispatch decisions | `opus` | your strongest reasoning model |
  | implementer | `IMPLEMENTER` | tickets needing judgment, all on-demand agents, escalations | `sonnet` | a strong coding model |
  | mechanical | `MECHANICAL` | tickets with explicit, test-checkable criteria | `haiku` | your fastest cheap model |

  Tiers resolve per kind via `TIERS` in `scripts/ff.py` (edit it when new versions ship, or to give another kind defaults). Only `claude` has defaults; for other kinds a tier means "the agent's own default model". The old aliases `opus`/`sonnet`/`haiku` still work for `claude`. Any other value is a literal model id, passed as `--model` for kinds in `MODEL_FLAG`.

Environment: `HERDR_BIN` points `ff.py` at a different `herdr` binary (the self-check uses it). Run state lives in `.scratch/<feature>/` of the project: `usage.tsv` (with a `kind` column), `cost.tsv`, `panes.tsv`.

The frontmatter sets `disable-model-invocation: true`, a Claude Code field that stops the agent from starting the skill on its own; you start it with `/feature-flow`. Other agents ignore the field.

## Install

See the root [README](../../README.md#install) for install steps for each agent. Copy the whole `feature-flow/` folder, including `scripts/`. Then check the scripts from wherever you installed it:

```sh
SKILL_DIR=~/.claude/skills/feature-flow   # your install path
python3 "$SKILL_DIR/scripts/test_ff.py"   # prints: ok (uses a fake herdr, opens no panes)
```

Start Claude Code inside a Herdr pane and type `/feature-flow <what you want to build>`. Another orchestrator agent: ask it to use the feature-flow skill.

## Acknowledgments

- [Matt Pocock](https://github.com/mattpocock) for the [skills](https://github.com/mattpocock/skills) this flow is built on: the grill → spec → tickets → implement loop, the local-markdown tracker, and the diagnosis, research, prototype and handoff skills.
- The [Herdr](https://github.com/herdrdev/herdr) project for the agent-aware terminal and CLI that make named worker panes possible.
