---
name: ticket-analyzer
description: Analyze a ticket and give a junior-developer-friendly summary of what it wants, why, and what it touches. Works with Jira (keep "Jira" as a trigger), GitHub Issues, GitLab Issues, and Linear. Use when the user asks to analyze, summarize, or explain a ticket or issue (by ID, key, or URL), or asks "what does this ticket want?". Fetches the ticket, comments, linked tickets, and linked docs, then writes a simplified explanation.
---

# Ticket Analyzer

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `OUTPUT_DIR` | `./notes` | Folder for saved summaries (`<TICKET-ID>-Summary.<ext>`). Ask the user if they want another. |

## Overview

Analyze a ticket and create an easy-to-understand summary tailored for junior developers. Fetch the ticket, comments, linked tickets, linked docs (wiki pages, specs), and attachments, then translate it into clear, simplified language.

**Scope:** This skill is for *understanding* a ticket, not planning implementation. It does not run code-discovery sub-agents, suggest implementation approaches, or create branches. For planning prep, use the `ticket-planning-prep` skill.

## When to Use This Skill

Use this skill when the user:
- Asks to "analyze" or "summarize" a Jira ticket, GitHub/GitLab issue, or Linear issue
- Provides a ticket ID (e.g., "PROJ-123", "#42"), key, or URL
- Says "what does this ticket want?" or "explain this ticket"
- Wants to understand ticket requirements in simple terms

## Workflow

### Step 1: Data Acquisition

Detect the tracker from the URL, the ID format, or `git remote -v`; ask the user if unclear. Use whichever tool in **Platform adapters** the agent has; if none, ask the user to paste the ticket text. Aim for **two round-trips** — primary ticket first, then everything else in one batch. If the agent can run sub-agents or parallel tool calls, fetch the batch in parallel; otherwise fetch serially.

**Round 1 — Primary ticket (required):** fetch the ticket with its description, status, priority, comments, and issue links.

**Round 2 — Everything else:** from the primary ticket collect:
- All linked ticket keys (parent, epic, blocked by, blocks, relates to)
- All doc URLs in the description and comments (e.g. Confluence `https://acme.atlassian.net/wiki/...`) — deduplicate

Fetch each linked ticket and each linked doc. Also fetch the ticket's remote links (Jira) — they surface docs not embedded as text URLs. If that surfaces additional docs, fetch just those.

**Attachments (conditional):** if the primary ticket has attachments, ask the user a multiple-choice question (Claude Code: `AskUserQuestion`; otherwise plain text): "Attachments found — fetch and analyze? Yes / No". If yes, fetch each (web fetch for text/PDF, image tools for images) and incorporate findings into "Important Details".

**Failure handling:** If the primary ticket fetch fails, STOP and notify the user. Failures in Round 2 are non-fatal — note which pieces are missing in the final summary and continue.

## Platform adapters

| Operation | Jira + Confluence | GitHub Issues | GitLab Issues | Linear |
|---|---|---|---|---|
| Fetch ticket + comments | Atlassian MCP `getJiraIssue` (needs `cloudId` from `getAccessibleAtlassianResources`); or `acli jira workitem view PROJ-123 --fields '*all'` | `gh issue view <n> --comments` | `glab issue view <n> --comments` | Linear MCP `get_issue`, `list_comments` |
| Linked tickets | `getJiraIssue` per linked key; or `acli jira workitem view <KEY>` | Issues referenced in the body (`#n`); `gh issue view <n>` | `glab issue view <n>` per `#n` mentioned | `get_issue` per related issue |
| Remote links / linked docs | MCP `getJiraIssueRemoteIssueLinks`, `getConfluencePage` (Confluence has no `acli` command) | URLs in the body; web fetch | URLs in the body; web fetch | `get_document`, or web fetch |
| Find ticket when ID unknown | MCP `searchJiraIssuesUsingJql`; or `acli jira workitem search --jql "text ~ 'keyword'"` | `gh issue list --search "keyword"` | `glab issue list --search "keyword"` | `list_issues` with `query` |

MCP tool names above are as exposed by the Atlassian and Linear MCP servers; if your server prefixes or renames them, match by purpose. Use `expand: "renderedFields,names,schema,transitions"` on `getJiraIssue` for full detail.

### Step 2: Analysis

Build a complete mental model of the ticket:

1. **Requirements:** What is being asked? What problem does it solve? What are the acceptance criteria?
2. **Context:** How does this relate to parent/epic/linked tickets? What business need drives it? Any blockers?
3. **Decisions in comments:** Clarifications, requirement changes, ruled-out approaches, links to docs/PRs.
4. **Linked docs:** Identify the sections of fetched pages most relevant to this ticket — usually design notes, API contracts, or product specs.

### Step 3: Simplification

Translate technical content into junior-developer-friendly language:

- Replace jargon with plain equivalents where possible. Example: "Implement caching layer with Redis TTL" → "Add a cache that automatically deletes old data after a set time using Redis".
- When a technical term is unavoidable, explain it inline. Example: "Use `@Transactional` (this means all the database operations either succeed together or fail together — no half-finished state)".
- Use short sentences and bullet points for complex requirements.
- Always include the *why*, not just the *what*.

### Step 4: Summary Structure

Format the summary with these sections:

1. **Header** — Ticket ID + title, Ticket link, status, priority.
2. **What It Wants (The Goal)** — 2-3 sentences in plain language.
3. **Why It Matters (The Context)** — Business/technical reason, connection to parent or epic.
4. **What Needs to Change (Technical Scope)** — Affected areas at a high level, type of change (feature/bug/refactor), rough complexity (simple/moderate/complex). Do **not** dive into specific files or line numbers — that's planning's job.
5. **Important Details** — Acceptance criteria in plain language, key constraints, attachment findings (if any).
6. **Key Discussions** — Notable clarifications and decisions from comments.
7. **Linked Documentation** — For each fetched doc page: title, URL, and the most relevant section.
8. **Dependencies** — Blocking tickets and parent/epic context.

### Step 5: Output Delivery

#### 5.1 Quick Preview

Display a 2-4 sentence preview that captures the essence of the ticket. This lets the user redirect early if the analysis is off-target.

**Example:**
> **Quick Summary:** PROJ-2001 is a bug fix for timestamps showing impossible future years (e.g. 2075) in the Ticket Log. Devices sometimes have wrong clocks, and the system currently trusts whatever timestamp the device reports. The fix needs to validate timestamps server-side and clean up existing bad data with a migration.

#### 5.2 Gather Preferences

Ask the user one multiple-choice question set (Claude Code: a single `AskUserQuestion` call with several questions; otherwise plain text):

- **Output** — "Save to file", "Display inline", "Both"
- **Language** — "English", "Hebrew", "Ukrainian", "Other (I'll specify)"
- **File Format** *(only relevant if saving)* — "Markdown (.md)", "Plain Text (.txt)", "Word (.docx)", "PDF (.pdf)"
- **Location** *(only relevant if saving)* — "Default (`OUTPUT_DIR`)", "Custom (I'll specify)"

Include the file-format and location questions in the same call; ignore those answers if the user picked "Display inline".

#### 5.3 Deliver

- **Translation:** If language ≠ English, translate the entire summary before display/save.
- **Inline:** Output the full summary in the conversation.
- **Save:**
  - Default path: `OUTPUT_DIR/[TICKET-ID]-Summary.[ext]`
  - Markdown/Plain Text: write the file directly (strip markdown for `.txt`)
  - DOCX: use a docx skill or tool if available, else offer Markdown
  - PDF: use a pdf skill or tool if available, else offer Markdown
- **Confirm:** Tell the user the file path if saved.

## Guidelines

**Tone:**
- Write for a junior developer new to the project.
- Simple, direct language. Explain technical terms when used.
- Be concise but complete — don't drop important information for the sake of brevity.

**What to avoid:**
- Jargon without explanation.
- Assuming knowledge of internal frameworks or patterns.
- Diving into implementation specifics — this skill is about understanding, not planning.
- Being condescending while simplifying.

**Quality checks before finalizing:**
- ✓ All requirements captured
- ✓ Technical language explained or simplified
- ✓ The "why" is clear, not just the "what"
- ✓ Important comments and decisions included
- ✓ A junior dev could read this and act without follow-up questions

## Example Usage

**User:** "Analyze PROJ-123"

1. Fetch PROJ-123 (round 1).
2. Round 2 (parallel if possible): linked tickets + doc URLs from description/comments + remote issue links.
3. If remote links surfaced new docs, fetch those too.
4. If attachments exist, ask user; fetch in parallel if yes.
5. Analyze, simplify, structure (Steps 2-4).
6. Show quick preview, ask output preferences in one question set.
7. Translate if needed; deliver inline and/or save in chosen format.

---

**User:** "What does this ticket want?" *(with a ticket URL)*

1. Extract ticket ID from URL.
2. Run the workflow above; emphasize "What It Wants" and "Why It Matters" in the quick preview.
