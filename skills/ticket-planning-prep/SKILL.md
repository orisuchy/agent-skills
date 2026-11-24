---
name: ticket-planning-prep
description: Analyze a ticket to prepare for implementation planning. Works with Jira (+ Confluence), GitHub Issues, GitLab Issues, and Linear. Fetches the ticket, comments, linked tickets and docs, identifies affected code areas, surfaces technical questions, and prepares actionable context for the planning phase. Use when starting work on a ticket before planning, e.g. "prepare PROJ-123 for planning", "let's start with PROJ-123", "I need to work on #42".
---

# Ticket Planning Preparation

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `OUTPUT_DIR` | `./notes` | Folder for saved analyses (`<TICKET-ID>-analysis.md`). Ask the user if they want another. |
| `BASE_BRANCH` | repo default branch | Branch the work branch is created from (Step 8). |

## Overview

Bridge ticket understanding and planning: gather all ticket context, identify affected code areas, surface technical uncertainties, and prepare actionable information for the planning phase. Unlike `ticket-analyzer` (plain-language summary for newcomers), this output is technical and written for the implementer.

Use as **step 1** of: 1. Ticket analysis (this skill) → 2. Planning → 3. Implementation.

## When to Use This Skill

Use when the user:
- Asks to "analyze" or "prepare" a ticket for planning
- Provides a ticket ID (e.g. `PROJ-123`, `#42`), key, or URL before starting work
- Says "let's start with [ticket]" or "I need to work on [ticket]"
- Wants to know what is needed before planning implementation

## Workflow

### Step 1: Data Acquisition

Detect the tracker from the URL, ID format, or `git remote -v`; ask the user if unclear. Use whichever tool in **Platform adapters** the agent has; if none, ask the user to paste the ticket text.

1. **Primary ticket:** fetch with description, status, priority, assignee, type, labels, sprint/estimate, custom fields that may hold requirements, comments, and issue links (parent, epic, blocked by, blocks, relates to).
2. **Attachments (conditional):** if the ticket has attachments, ask the user a multiple-choice question (Claude Code: `AskUserQuestion`; otherwise plain text): "Attachments found — fetch and analyze? Yes / No". If yes, fetch each (web fetch for text/PDF, image tools for images) and include findings under Code Context or Key Decisions.
3. **Linked tickets:** collect all linked keys in one pass and fetch them together (in parallel if the agent can). Parents carry architectural context, epics carry business context, "blocked by" tickets are dependencies, related tickets may show similar implementations.
4. **Comments:** look for technical decisions and rationale, requirement changes, constraints, links to docs/PRs/code, and edge cases.
5. **Linked docs (Confluence, wiki, specs):** gather doc URLs from the description, comments, and the ticket's remote links (Jira); deduplicate and fetch together. Skip silently if there are none. Add a **Docs** sub-section inside "Key Decisions & Context": for each page, title, URL, and the sections relevant to the ticket.

**Failure handling:** if the primary ticket cannot be fetched, STOP and tell the user. Do not continue with incomplete data. Missing linked tickets or docs are non-fatal: note what is missing in the summary.

## Platform adapters

| Operation | Jira + Confluence | GitHub Issues | GitLab Issues | Linear |
|---|---|---|---|---|
| Fetch ticket + comments | Atlassian MCP `getJiraIssue` (needs `cloudId` from `getAccessibleAtlassianResources`); or `acli jira workitem view PROJ-123 --fields '*all'` | `gh issue view <n> --comments` | `glab issue view <n> --comments` | Linear MCP `get_issue`, `list_comments` |
| Linked tickets | `getJiraIssue` per linked key; or `acli jira workitem view <KEY>` | Issues referenced in the body (`#n`); `gh issue view <n>` | `glab issue view <n>` per `#n` mentioned | `get_issue` per related issue |
| Remote links / linked docs | MCP `getJiraIssueRemoteIssueLinks`, `getConfluencePage` (Confluence has no `acli` command) | URLs in the body; web fetch | URLs in the body; web fetch | `get_document`, or web fetch |
| Find ticket when ID unknown | MCP `searchJiraIssuesUsingJql`; or `acli jira workitem search --jql "text ~ 'keyword'"` | `gh issue list --search "keyword"` | `glab issue list --search "keyword"` | `list_issues` with `query` |

MCP tool names are as exposed by the Atlassian and Linear MCP servers; if your server prefixes or renames them, match by purpose. On `getJiraIssue`, `expand: "renderedFields,names,schema,transitions,changelog"` gives full detail.

### Step 1b: Session Name

Compute SESSION-NAME and keep it for Step 8: `{TICKET-ID}-{short description}`, under ~5 words, lowercase phrase (example: `PROJ-123-public api devices limit`). If the agent supports renaming sessions, print the line so the user can run it (Claude Code: `/rename {SESSION-NAME}`).

### Step 2: Requirements Analysis

Extract:
1. **What:** primary objective, acceptance criteria (explicit and implicit), validation criteria, out-of-scope items.
2. **Why:** business driver or user need, problem solved, impact if not done, link to parent/epic.
3. **Constraints:** technical, performance, security, backwards compatibility, code style or architecture to follow.
4. **Key decisions:** decisions made in comments, approaches ruled out (and why), answered questions, changes of direction.

### Step 3: Code Context Discovery

1. Extract search keywords from the title, description, and technical terms (class names, methods, modules, feature names).
2. Explore the codebase. If the agent can run sub-agents, delegate a thorough search (Claude Code: `Agent` with `subagent_type="Explore"`, breadth "very thorough"); otherwise search directly. Give it the ticket ID, a one-sentence objective, and the keywords, and ask it to:
   - find files likely to be modified
   - locate existing utilities, helpers, or similar implementations (DRY check), including common shared directories (`utils/`, `helpers/`, `lib/`, `shared/`, `common/`)
   - identify integration points and dependencies
   - flag complex or risky areas
3. Record specific files with line references. Look for PR/commit links in comments for prior implementation context.

### Step 4: Technical Questions

Surface what planning must resolve:
- **Approach:** modify existing vs create new; which layer; edge cases; performance impact.
- **Reuse (DRY):** can an existing utility/class be reused or generalized; similar functionality elsewhere.
- **Architecture:** fit with current design; changes to related systems; interaction with existing features; refactor first?
- **Unknowns:** external APIs/libraries to research, scalability, security, testing strategy.
- **Clarifications:** ambiguous requirements, missing acceptance criteria, undefined error handling, unclear scope.

### Step 5: Implementation Approaches

Outline plausible approaches from the requirements and code context. For each: name, description, pros, cons, files affected, complexity (Simple/Moderate/Complex). Give a recommendation and what needs validating if one is clearly best. Do not force several approaches when one is clearly right; say so if more exploration is needed.

### Step 6: Summary Creation

Use these sections (emoji headings optional):

- **Ticket Overview:** ID and title, link, status, priority, type, sprint.
- **Requirements:** what, why, constraints.
- **Code Context:** affected areas (files/modules, patterns to follow, risky areas); relevant code as `file_path:line_number`, similar implementations, related PRs/commits; **Existing Functionality (DRY Check)**: reusable functions/utilities, code that could be generalized, or explicitly "No similar functionality found".
- **Planning Questions:** technical uncertainties; clarifications needed.
- **Implementation Approaches:** approaches with pros/cons/complexity; recommendation if any.
- **Chosen Approach:** decision and one-sentence why; what was ruled out; key assumptions; open risks.
- **Key Decisions & Context:** decisions from comments, ruled-out approaches, direction changes, docs.
- **Dependencies & Blockers:** blocking tickets, related tickets, external dependencies.
- **Implementation Kickoff:** start here (first file and change, one sentence); ordered concrete tasks; unresolved risks known before starting; next step: hand this analysis to your planning step (Claude Code: `/writing-plans` or plan mode).

### Step 7: Output Delivery

1. Display the summary inline (always).
2. **Finalization check** before saving:
   - Is Chosen Approach filled in? If not, decide now.
   - Do Planning Questions have unresolved critical items? Resolve them or move them to Implementation Kickoff → Unresolved risks.
   - Are the Kickoff tasks concrete enough to start coding from in a fresh session with no prior context?
3. Ask one question (Claude Code: `AskUserQuestion`; otherwise plain text), "Save to file?": "Yes - `OUTPUT_DIR/[TICKET-ID]-analysis.md`" / "Yes - I'll specify location" / "No - inline only".
4. If saving, write Markdown to the chosen path (create the folder if needed).
5. Ask: "Analysis complete. Ready to start planning?"

### Step 8: Branch Setup

Runs automatically, no prompt, only inside a git repository.

1. Branch name from SESSION-NAME: lowercase, spaces → hyphens (`PROJ-123-public api devices limit` → `proj-123-public-api-devices-limit`).
2. Determine `BASE_BRANCH` (default: `git symbolic-ref --short refs/remotes/origin/HEAD` minus the `origin/` prefix).
3. Run `git checkout <BASE_BRANCH> && git pull origin <BASE_BRANCH> && git checkout -b <branch_name>`. If the working tree is dirty or the checkout fails, skip and warn: "Could not create branch from <BASE_BRANCH> — create it manually."
4. Report: `Branch <branch_name> created from <BASE_BRANCH>` or the warning.

## Guidelines

- **Tone:** technical and precise; written for the implementer, thorough but concise.
- **Priorities:** code context is critical (always explore the real codebase); technical questions guide planning; flag ambiguous requirements; approaches are helpful but never forced.
- **Focus on:** information for planning decisions, patterns and conventions, reusable existing code (DRY), constraints, uncertainties.
- **Avoid:** oversimplifying technical concepts, assumptions not checked against the codebase, jumping to solutions without exploration, ignoring edge cases.

**Quality checks before finalizing:** requirements clear and complete; codebase actually explored; affected files named; DRY check done including shared directories; technical questions surfaced; dependencies noted; Chosen Approach is a decision, not just options; Kickoff tasks work for a fresh session; unresolved risks flagged explicitly rather than buried in open questions.

## Example Usage

> "Analyze PROJ-123 for planning"

1. Detect the tracker; fetch the primary ticket.
2. Fetch linked tickets and docs together; ask about attachments if present.
3. Print the session-name line; store SESSION-NAME.
4. Analyze requirements (Step 2), explore the code (Step 3), list questions (Step 4), outline approaches (Step 5).
5. Show the summary inline; ask whether to save to `OUTPUT_DIR/PROJ-123-analysis.md`.
6. Create the work branch from the base branch.

> "Let's work on #42"

Treat as step 1 of the workflow, follow the same flow, and end with "Analysis complete. Ready to start planning?"

## Integration with Planning Phase

After this skill the user has full ticket understanding, identified code context, and surfaced questions. Next, enter the agent's planning mode (Claude Code: plan mode), explore the uncertainties, decide, then implement. This skill provides the "what" and "why" so planning can focus on the "how".
