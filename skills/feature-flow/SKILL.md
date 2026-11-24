---
name: feature-flow
description: Orchestrate feature development across Herdr panes with named worker agents. Runs Matt Pocock's planning flow (grill → spec → tickets in this session), then dispatches one fresh agent per ticket running the implement skill, with a per-ticket model line. Workers can be any agent kind Herdr can start (Claude Code by default). Also dispatches diagnosis, research, prototype and review-comment agents. Use when the user says "feature-flow", wants to build a feature with multiple agents, or asks to dispatch tickets to workers. Requires HERDR_ENV=1.
disable-model-invocation: true
---

# feature-flow

You are the **orchestrator** (planner model). You plan with the user, then dispatch workers through the `herdr` CLI. You do not write feature code yourself. Any agent that runs shell commands can orchestrate.

Precondition: `test "${HERDR_ENV:-}" = 1`. If it fails, say you are not inside Herdr and stop. Follow the `herdr` skill for CLI syntax and safety rules; run `herdr agent --help` if unsure of a flag.

## Configuration

| Setting | Default |
|---|---|
| `SKILL_DIR` | absolute path of the folder holding this `SKILL.md` |
| `FF` | `python3 $SKILL_DIR/scripts/ff.py` (shell variables do not persist: set both in each command that uses them) |
| `AGENT_KIND`: worker agent kind (any `herdr agent start --kind` value) | `claude` |
| `IMPLEMENTER` model: judgment tickets, on-demand agents | `implementer` |
| `MECHANICAL` model: explicit, test-checkable tickets | `mechanical` |

The planner tier is you (on Claude Code, start the session on `opus`). A model value is a tier (`planner`, `implementer`, `mechanical`) or a literal model id. `ff.py` maps tiers per kind via `TIERS` (only `claude` has defaults: opus/sonnet/haiku; other kinds use their own default model). Literal ids pass through as `--model`, only for kinds whose CLI has that flag (see "Supported agents").

## Supported agents

Pass `--kind <AGENT_KIND>` (or a per-ticket kind the user picked) to every `$FF start`; without it the worker is `claude`. This table is the one place that says how to prompt a skill. Prompts below name the skill and show the Claude Code form (`/implement <path>`); for another kind use its row.

| Kind | Prompt a skill | Model flag | `/cost` + usage.py |
|---|---|---|---|
| `claude` | `/implement <path>` | `--model` | yes |
| `codex`, `gemini`, `copilot` | `Use the implement skill on <path>.` | `--model` | no: `n/a` |
| any other Herdr kind | `Use the implement skill on <path>.` | not passed (unverified) | no: `n/a` |

The worker agent must load Agent Skills and have the required skills installed for it.

## Phase 0 — Bootstrap (only if needed)

The flow needs `/setup-matt-pocock-skills` to have run (tracker = local markdown, tickets at `.scratch/<feature>/issues/NN-slug.md`). Check the current folder:

| State | Action |
|---|---|
| `docs/agents/issue-tracker.md` exists | Skip to Phase 1. |
| Git repo, setup missing | Offer to run the setup (below). |
| No `.git` (new project) | Ask the user which they want, then run the setup: **(a) `git init` locally, no remote** (recommended: `/implement` commits and worktrees need git; nothing is pushed anywhere), or **(b) no git at all** (see "No-git mode"). Never add a remote. |

To run the setup, ask first: "Run the setup here with local markdown, default triage labels, and CLAUDE.md?" Only on a yes:
1. Start the agent with `$FF start _setup setup setup - <IMPLEMENTER> --kind <AGENT_KIND>` and prompt it with `/setup-matt-pocock-skills` (Claude Code: it cannot be model-invoked, so send it as the prompt; other kinds: see "Supported agents").
2. Answer its questions with exactly what the user approved: tracker = Local markdown, default triage labels, CLAUDE.md. Answer menus with `herdr agent send-keys setup <keys>`; zoom the pane (`herdr pane zoom <pane> --on`, `--off` after) to read them, since small panes hide the options. Clear any unsent text in the input box first (`herdr agent send-keys setup ctrl+u`).
3. Verify on disk that `docs/agents/issue-tracker.md` says "Local Markdown", then `$FF close _setup setup`.
4. If the user declines the setup, stop.

For a brand-new project too big to plan in one session, tell the user to run `/wayfinder` first and hand off at `/to-spec`.

### No-git mode

When the user chose no git, there is nothing to commit and nothing to isolate:
- Run **serially only**: no parallel mode, no worktrees (`herdr worktree` needs git).
- Tell every `impl` agent: "There is no git repo. Do not commit or run git commands. Implement, run the tests, and report the changed files." The ticket's done-check becomes the test output plus the listed changed files, not a commit.
- In Dispatch step 4, check "no changed files or failing tests" instead of "no commit".
- There is no undo. Before each ticket, suggest the user copy the folder or run `git init` later; do not run it for them.
- `/review-comments` is unavailable (needs a PR/MR).

## Phase 1 — Plan (this session, interactive)

Keep these in one unbroken context; do not compact or clear it until tickets are written.
1. `/grill-with-docs` with the user to sharpen the idea (in a new project it builds `CONTEXT.md` from scratch). If a question needs runnable code, use the prototype detour below.
2. If the effort is multi-session: `/to-spec`, then `/to-tickets`. Otherwise skip to Phase 2 with a single ticket.
3. After `/to-tickets`, add a model line to every ticket file, under `**Status:**`:

   ```
   **Model:** <IMPLEMENTER or MECHANICAL value: a tier, e.g. mechanical, or a model id>
   ```

   - Mechanical: explicit, test-checkable criteria (add a field, wire an endpoint, follow an existing pattern, rename or move).
   - Implementer (default, and when in doubt): anything needing judgment about the codebase (shared helpers, fixture design, flaky behaviour, unclear seams).
   - Show the user the model per ticket and let them override.

## Agent bookkeeping

Every agent you start or close goes through `$FF`, never raw `herdr agent start` or `pane close`; an agent started any other way is missing from the usage summary. It does the layout, ledger, session ids and (Claude Code only) `/cost` capture in code.

| When | Command |
|---|---|
| Start of Phase 1 | `$FF orch <feature>` (adds your own ledger row) |
| Start any agent | `$FF start <feature> <name> <role> <ticket> <model> [--kind <kind>] [--cwd <worktree>]` → prints the pane id |
| Agent finished | `$FF close <feature> <name>` (captures session id and, for `claude`, `/cost`; then closes its pane or tab) |

- `role`: `impl`, `diag`, `research`, `proto`, `review`, or `setup`. `ticket`: `NN-slug`, or `-`. `model`: a tier or a model id. `kind`: default `claude`.
- If `start` exits non-zero (for example `agent_not_ready` at a trust dialog), the row and pane are still recorded. Inspect with `herdr agent get <name>` and `herdr agent read <name>`, notify the user, and `close` it later as usual.
- Reruns and escalations are new agents with new names (`impl-03b`).
- `close` refuses names it did not start, so it cannot close the user's panes.
- Files in `.scratch/<feature>/`: `usage.tsv` (ledger), `cost.tsv`, `panes.tsv` (panes `ff.py` opened). Do not edit them by hand.
- Your own cost (Claude Code only; other kinds write `n/a`): at Finish, run `/cost` yourself and append `orchestrator<TAB><figure>` to `cost.tsv`, or `n/a`. Never estimate.

## Layout

`$FF start` keeps you in the left half, never split: the first worker splits right of you, later ones split down from the last worker, and from the 4th on each worker gets its own tab. All with `--no-focus`.
- Start `review` last so it lands in the bottom slot (or its own tab); the user answers in it.
- `$FF close` each agent as soon as it finishes.
- If the user asks for a different arrangement, split panes by hand and start agents with raw `herdr agent start`, but then write the ledger row yourself (`name<TAB>role<TAB>ticket<TAB>model<TAB>session_id<TAB>kind` into `usage.tsv`, session id from `herdr agent get <name>` → `.result.agent.agent_session.value`, read before the pane closes).

## Phase 2 — Dispatch (the frontier loop)

Work the **frontier**: tickets whose blockers are all done and whose `Status` is `ready-for-agent`.

For each frontier ticket `NN-slug`:

1. If more than one ticket runs in parallel, give each its own worktree (`/implement` commits to the current branch): `herdr worktree create --branch <feature>-NN --path <dir> --no-focus`, then `--cwd <dir>` on `$FF start`. Serial tickets may share the checkout.
2. Start the agent, model from the ticket: `$FF start <feature> impl-NN impl NN-slug <model> --kind <AGENT_KIND>`. It opens the pane per "Layout".
3. Prompt it with the implement skill on the ticket, one ticket per fresh agent, never reuse an agent across tickets (form per kind: "Supported agents"; Claude Code shown):
   `herdr agent prompt impl-NN "/implement .scratch/<feature>/issues/NN-slug.md" --wait --timeout 600000`
   The 10-minute timeout is the stuck-check interval, not a failure.
4. Handle the settled state:
   - `idle`/`done`: **idle is not proof of done.** Read the result (`herdr agent read impl-NN --source recent-unwrapped --lines 150`) and check the ticket's commit and test output. If the last message ends in a question, or there is no commit, treat it as a question (see "Questions"). Otherwise mark the ticket `Status: done`, run `$FF close <feature> impl-NN`, and move on.
   - `blocked`: inspect with `herdr agent get`/`herdr agent read`. Do not answer approval or permission dialogs yourself. Notify the user and ask.
   - `agent_prompt_stalled`: the prompt was likely not picked up. Inspect before resending anything.
   - `timeout` (10 minutes): run the stuck check.
5. **Escalation:** if a mechanical-model ticket fails, or the tests are thin or only assert the happy path, rerun that ticket once on the implementer model in a fresh agent (non-`claude` kinds have no tier defaults: escalate with a literal model id or another kind, or the rerun uses the same model). If that also fails, dispatch `diag`.

### Questions

An agent that asks a plain-text question settles as `idle`. If its last message is a question:
- Answer it yourself only if the spec or ticket answers it outright (send with `herdr agent prompt`, flags as in step 3).
- Anything about intent, scope, or a trade-off goes to the user. Notify them, relay the question verbatim, and send their answer.
- Never guess an answer to unblock an agent.

### Stuck check

On a 10-minute timeout, save a snapshot (`herdr agent read impl-NN --source recent-unwrapped --lines 40`) and compare it to the previous one for this agent.
- Output changed: it is working. Wait again with `herdr agent wait impl-NN --timeout 600000`.
- Output unchanged since the last check: it is stuck. Send `herdr agent send-keys impl-NN esc`, read what it was doing, then either steer it with a short prompt or, if it is looping or confused, `$FF close` it and rerun the ticket in a fresh agent (escalate model per step 5). If the same ticket sticks twice, stop and tell the user.

### Notify

Whenever an agent is `blocked`, asks a question you cannot answer from the spec, or sticks twice, notify the user (Claude Code: `PushNotification`; otherwise a plain message) naming the agent and ticket, then wait for their reply. Do not wait silently.

### Parallel mode (opt-in)

Default is serial with `--wait`. Only when the user asks to run several tickets at once:
1. Give each its own worktree and pane.
2. Prompt each without `--wait`, then confirm it started with `herdr agent wait impl-NN --until working --timeout 10000`. A prompt that never took shows up as a timeout here; inspect before resending.
3. Run one background watch loop over `herdr agent list` (Claude Code: `Monitor`; otherwise a polling shell loop). Report an agent only after it has been seen `working` and then reaches `idle`, `done`, or `blocked`; right after a prompt the old `idle`/`done` is stale and would fire early.
4. In the same loop, flag any `working` agent whose pane output is unchanged for 10 minutes, and apply the rules above to whichever agent surfaces.

Read blocked/failed state from `herdr agent get`, not from the pane layout. IDs come from JSON responses only.

## Other agents (on demand)

Start each with `$FF start <feature> <name> <role> - <IMPLEMENTER> --kind <AGENT_KIND>`, prompt with `--wait`, `$FF close` when done.

| Agent | When | Prompt |
|---|---|---|
| `diag` | A ticket's tests or a bug resist a first fix | `/diagnosing-bugs <symptom + ticket path>` |
| `research` | A question needs primary-source reading | `/research <question>` |
| `proto` | Grilling hit a question that needs runnable code | Write a `/handoff` file first, then `/prototype` in a fresh agent referencing it; hand the answer back with `/handoff` |
| `review` | The PR/MR has reviewer comments | `/review-comments <PR/MR number or url>`. It is interactive and posts nothing without approval: leave its pane open, tell the user to answer there, and do not answer its prompts. For a valid comment needing more than a one-liner, write a new ticket and dispatch `impl-NN`, then let `review` reply. |

## Finish

When every ticket is done: run the full test suite once, summarize per ticket (model used, escalations, commit), and list uncommitted or unmerged work. Do not push or open a PR/MR unless the user asks.

Then ask: "Want a usage summary for this session's agents?" Only on a yes, run `python3 $SKILL_DIR/scripts/usage.py .scratch/<feature>/usage.tsv .scratch/<feature>/cost.tsv` and show its table, plus: agent count per role, escalations (reruns of a ticket), and the heaviest agent by output tokens. The cost column comes from each agent's `/cost` output; show `n/a` where missing and never compute a price yourself. Limits: it reads each agent's own Claude Code transcript (no internal sub-agents), so non-`claude` rows show `n/a` and are left out of the totals, and the orchestrator row covers only the session so far.

## Rules

- Only close panes and agents you created. Never close the user's panes.
- Use `--no-focus`; do not steal the user's focus.
- Never run `herdr server stop` or kill the main Herdr process.
- Do not answer trust, approval, or permission dialogs for the user.
- Do not run Phase 2 before the user approves the ticket breakdown and model lines.
