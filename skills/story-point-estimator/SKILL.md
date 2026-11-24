---
name: story-point-estimator
description: Use when asked to estimate story points for a ticket (Jira, GitHub Issues, GitLab Issues, Linear), size a ticket, gauge how big a piece of work is, or prep for planning poker/backlog grooming/refinement. Triggers on a ticket ID, key, or URL plus a request like "estimate", "how many points", "size this", or "is this a 5 or an 8".
---

# Story Point Estimator

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `POINT_SCALE` | `1,2,3,5,8,13,21` (Fibonacci) | Allowed point values. To change it, edit this row and set the same list in the `POINT_SCALE` environment variable so `scripts/manage_baseline.py` accepts it. |

## Overview

Story points measure the **size** of work, not time. This skill fetches a ticket (Jira, GitHub Issues, GitLab Issues, or Linear) and sizes it on five dimensions (amount of work, familiarity, risk and uncertainty, testing, process overhead and dependencies), anchored to reference stories, on the `POINT_SCALE` above.

**Core rule: never convert points to hours/days, and never estimate from a blank page.** Both defeat the purpose — see "What NOT to do" below.

## Workflow

### 1. Fetch the ticket

- Extract the ticket key from whatever the user gave you (ID, key, or URL).
- Detect the tracker from the URL, the ID format, or `git remote -v`; ask the user if unclear. Use whichever tool in **Platform adapters** the agent has; if none, ask the user to paste the ticket text.
- Fetch the ticket with its description, acceptance criteria, comments, and links.
- If the ticket references a parent/epic, blocking tickets, or linked docs, fetch those too — dependencies and unclear scope both live there.
- If any fetch fails, stop and tell the user. Don't estimate from partial/guessed ticket contents.

### 2. Get baseline anchors — REQUIRED before scoring

Read `baseline-table.json` (sibling of this SKILL.md) — it holds the team's persisted reference stories (key, points, summary, notes on why each earned its score). Use its entries as your comparison anchors in step 3 ("is this bigger or smaller than the 3?").

- If the table has entries: anchor against them directly, no need to ask the user first.
- If the table is empty or missing: ask the user for 2-4 reference stories ("Do you have reference stories I can anchor this against? e.g. 'we called X a 3, Y an 8'"). If they still have none, proceed but say explicitly the estimate is a rougher, unanchored guess.
- If the user supplies anchors ad hoc in chat (beyond what's in the table), use those too, and ask if they want the new one added to the table (step 6).

Do not skip anchoring entirely to save a turn. An estimate with no anchor is a guess, not a size — the source guide's entire point is that comparison-to-anchor is what makes estimates reproducible across people.

### 3. Score the 5 dimensions

Score the ticket against each dimension as small / medium / large, using the ticket's description, acceptance criteria, comments, and linked tickets as evidence. Compare each to the baseline anchors if provided.

| Dimension | Smaller when... | Bigger when... |
|---|---|---|
| 🏋 Amount of Work | Small, contained change | Many components to build or touch |
| 💡 Familiarity | Known territory, done before | Brand new — never built this before |
| ⚠️ Risk & Uncertainty | Clear and closed spec | Open-ended, unanswered questions |
| 🐛 Testing & Bug Fixing | Light validation | Heavy — new API, regression/edge-case coverage |
| 📆 Process Overhead & Dependencies | Finishable independently | Needs another team's approval, data, or a deploy outside your control |

None of these ask "how hard is this for a specific person" or "how long will it take" — they ask about the work itself. If you catch yourself reasoning about who'd do the work or how many days it'd take, stop and re-anchor on the dimensions.

### 4. Pick the number

Scale: `POINT_SCALE` (default 1, 2, 3, 5, 8, 13, 21). Each step is a real "closer to X or Y" choice, not a fine one — don't agonize between adjacent values like 5 vs 8 beyond one round of comparison to the anchors.

**If every dimension points large and the story feels like the top of the scale: don't force a number.** Say so directly and recommend splitting the ticket into smaller stories instead.

### 5. Output

Report in chat only — do not comment on or edit the ticket unless the user explicitly asks.

Structure the response as:

1. **Estimate:** the point value (or "largest value+ — recommend splitting")
2. **One-line ticket summary**
3. **Dimension breakdown** — each of the 5 dimensions, its size (small/medium/large), and the one-sentence reason, referencing the anchors if given
4. Offer: "Want the full analysis with a confidence range and split suggestions?"

### 6. Maintaining the baseline table

When the user asks to add, edit, or remove a baseline entry — or agrees to add the ticket just estimated — use the management script rather than editing `baseline-table.json` by hand:

```bash
python3 scripts/manage_baseline.py list
python3 scripts/manage_baseline.py add    --key PROJ-1234 --points 5 --summary "..." --notes "..."
python3 scripts/manage_baseline.py edit   --key PROJ-1234 --points 8
python3 scripts/manage_baseline.py remove --key PROJ-1234
```

Run from this skill's directory (paths above are relative to it). `--notes` should reference the 5 dimensions, same as existing entries — that's what makes the anchor useful for future comparisons. The script rejects `--points` values outside `POINT_SCALE`.

After estimating a new ticket, if the user seems to want it kept as a future anchor, offer to add it — don't add automatically.

## Platform adapters

| Operation | Jira + Confluence | GitHub Issues | GitLab Issues | Linear |
|---|---|---|---|---|
| Fetch ticket + comments | Atlassian MCP `getJiraIssue` (needs `cloudId` from `getAccessibleAtlassianResources`); or `acli jira workitem view PROJ-123 --fields '*all'` | `gh issue view <n> --comments` | `glab issue view <n> --comments` | Linear MCP `get_issue`, `list_comments` |
| Parent / linked tickets | `getJiraIssue` per linked key; or `acli jira workitem view <KEY>` | Issues referenced in the body (`#n`); `gh issue view <n>` | `glab issue view <n>` per `#n` mentioned | `get_issue` per related issue |
| Linked docs | MCP `getConfluencePage` (Confluence has no `acli` command) | URLs in the body; web fetch | URLs in the body; web fetch | `get_document`, or web fetch |

MCP tool names are as exposed by the Atlassian and Linear MCP servers; if yours prefixes or renames them, match by purpose.

## What NOT to do

- **Never state or imply an hours/days equivalent** — not in the estimate, and not if the user asks "how long will this take" (redirect: that's what team velocity is for, a separate number from size).
- **Never skip step 2** — read `baseline-table.json` first; only ask the user for anchors if it's empty or missing.
- **Never compare this estimate to another team's point values** — baselines aren't shared across teams; a 5 on one team isn't a 5 on another.
- **Never write the estimate back to the ticket** (comment, story-points field, etc.) without the user asking first.

## Example

User: "Estimate PROJ-501, it's about adding CSV export to the reports dashboard"

1. Fetch PROJ-501 (+ any linked tickets).
2. Read `baseline-table.json` — e.g. it has PROJ-101 (1 pt), PROJ-102 (3 pts), PROJ-103 (5 pts). Use these as anchors; no need to ask the user.
3. Score: Amount of Work = large (6 report types × schemas), Familiarity = medium (no existing export, but standard pattern), Risk = medium (streaming/100k-row requirement is somewhat open-ended), Testing = large (6-type × filter matrix), Dependencies = none.
4. Compare to anchors: clearly bigger than PROJ-103 (5, a single well-specified handler) — closer to 8 or 13.
5. Output: **Estimate: 8** + one-line summary + dimension table + offer for full analysis.
6. If the user wants PROJ-501 kept as a future anchor: `python3 scripts/manage_baseline.py add --key PROJ-501 --points 8 --summary "..." --notes "..."`.
