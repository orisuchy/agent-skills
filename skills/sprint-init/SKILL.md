---
name: sprint-init
description: Initialize a new sprint by fetching your open tasks in the current sprint/iteration/cycle from your tracker (Jira, GitHub, GitLab, Linear), categorizing them (Features/Technical/Bugs), checking your calendar for a Code Freeze date, and organizing them in TASKS.md with proper prioritization. Use when starting a new sprint, syncing sprint tasks, or resetting the sprint board.
compatibility: Needs a tracker connection (Atlassian MCP, gh, glab, or Linear MCP) and optionally a calendar MCP (Outlook or Google Calendar). Tested with Jira + Outlook in Claude Code.
---

# Sprint Initialization Skill

Automate sprint setup: fetch tracker tasks, detect bug hierarchies, find the Code Freeze date, prioritize work, and populate TASKS.md.

## Configuration

| Setting | Default | Meaning |
| --- | --- | --- |
| `TASKS_FILE` | `./TASKS.md` | Sprint board file to (re)write. |
| `MEMORY_DIR` | `./memory` | Where sprint snapshot/reference notes go. |
| `WIKI_LOG` | `none` | Optional log file to append a sprint-init entry to (e.g. `./wiki/_log.md`). `none` skips it. |
| `CALENDAR` | `none` | Code Freeze source: `outlook`, `google`, or `none`. |
| `FREEZE_KEYWORD` | `Code Freeze` | Calendar event subject to search for. |
| Tracker | detected | Jira, GitHub, GitLab, or Linear. Detect from `git remote -v` / available tools, else ask. |
| Task filter | — | Ask the user once: project key / repo / team, plus any extra filter (labels, status). For Jira, e.g. site `acme.atlassian.net`, project `PROJ`. |

Ask the user for any value you cannot detect. Do not guess a tracker site or project.

## What this skill does

1. Fetches all open tasks assigned to the user in the current sprint/iteration/cycle
2. Categorizes each task as Feature, Technical, or Bug
3. Resolves bug sub-tasks to their parent (using the parent's priority)
4. Looks up the next Code Freeze date in the calendar (if configured)
5. Organizes `TASKS_FILE` by priority order (Features → Technical → Bugs)
6. Updates sprint notes in `MEMORY_DIR` and optionally `WIKI_LOG`
7. Flags critical-priority bugs for immediate attention

## Output

**`TASKS_FILE`** — Reorganized with:
- Code Freeze date at the top
- Sprint priority rules displayed
- Tasks grouped by category (🎯 FEATURES → 🔧 TECHNICAL → 🐛 BUGS)
- Bug sub-tasks nested under parent tickets
- Parent bug priority prominently displayed (e.g., **HIGHEST** for critical bugs)
- Subtask type indicated parenthetically

**Notes in `MEMORY_DIR`** created/updated:
- `sprint-current.md` — Current sprint snapshot with task counts, critical path, Code Freeze
- `sprint-rules.md` — Sprint priority rules and Code Freeze behavior (reference)
- `subtask-bugs.md` — How to handle bug sub-tasks (reference)

**`WIKI_LOG` entry** (only if configured) documenting the sprint init.

## Platform adapters

| Operation | Jira | GitHub | GitLab | Linear |
| --- | --- | --- | --- | --- |
| My open tasks in current sprint | Atlassian MCP `searchJiraIssuesUsingJql` with `assignee = currentUser() AND sprint in openSprints() AND statusCategory != Done` (plus project/labels; needs `cloudId` from `getAccessibleAtlassianResources`) | Milestone: `gh issue list --assignee @me --milestone "<name>" --state open --json number,title,labels,state`. Projects iteration: `gh project item-list <n> --owner <owner> --format json`, keep items whose iteration field is the current one | Iteration: `glab issue list --assignee=@me --iteration <id>`; milestone: `glab issue list --assignee=@me --milestone "<name>"` (open issues are the default) | Linear MCP `list_cycles` (current cycle), then `list_issues` with assignee `me` and that cycle, excluding completed/canceled states |
| Fetch parent of a sub-task | `getJiraIssue` on the parent key | `gh issue view <n> --json title,labels` for the parent issue (sub-issues link to a parent) | `glab issue view <n>` on the parent issue/epic | `get_issue` on the parent issue |
| Calendar: Code Freeze | Outlook MCP `outlook_calendar_search`, or Google Calendar MCP (list/search events) — match tool names by purpose | same | same | same |

MCP tool names are as exposed by each server; if yours are prefixed or renamed, match by purpose. Verify `gh`/`glab` flags with `--help` for your installed version.

## Workflow

### Step 1: Fetch tasks

1. Detect the tracker and collect the Configuration values.
2. Fetch the open tasks via the **Platform adapters** table.
3. For each task, extract: id/key, summary, status, priority, type, labels.

If tracker authentication fails, stop and ask the user to verify credentials.

### Step 2: Resolve bug sub-tasks

When a task is a sub-task (Jira `Sub-task`, or a child issue elsewhere):
1. Fetch the parent via the adapter table
2. Use the **parent's** type and priority, not the sub-task's
3. Link the sub-task to its parent for display in `TASKS_FILE`

### Step 3: Categorize tasks

Assign each task to a category by type (or label where the tracker has no types):

| Type / label | Category | Icon |
| --- | --- | --- |
| Story, Epic, Task, feature | **Feature (Business)** | 🎯 |
| Refactor, Technical Debt, Cleanup, Architecture, tech-debt | **Technical** | 🔧 |
| Bug | **Bug** | 🐛 |

If uncertain (e.g., a Story labeled "technical-debt"), ask the user.

### Step 4: Fetch Code Freeze date

If `CALENDAR` is `none` or the calendar tool is unavailable, skip this step and note it in `sprint-current.md`.

Otherwise:
1. Search the calendar for events with `FREEZE_KEYWORD` in the subject
2. Take the next upcoming one (after today)
3. Extract date and time, and calculate days remaining (warn if near)

If none is found, note it in memory but don't fail.

### Step 5: Organize TASKS_FILE

Use this exact template structure:

```markdown
# Tasks

**Code Freeze:** [date and time] — After this, only bugs can be solved
**Sprint priority:** Features → Technical → Bugs (post-freeze)

---

## 🎯 FEATURES (Business) — Priority 1

[List feature tasks, ordered by priority]

---

## 🔧 TECHNICAL (Refactoring / Architecture) — Priority 2

[List technical tasks, ordered by priority]

---

## 🐛 BUGS — Priority 3 (Active after Code Freeze)

### 🔴 CRITICAL (Highest priority bugs)

[Parent bugs with Highest priority, nested sub-tasks]

### Standard Bugs (Medium/Low priority)

[Parent bugs with Medium/Low priority, nested sub-tasks]

---

## Waiting On

## Done
```

If no Code Freeze date is known, write `**Code Freeze:** not set` and omit the "After this" clause.

### Step 6: Format tasks

For each task, use this format:

```markdown
- [ ] **[TICKET-KEY]** Status — [Title]
  - Status: [tracker status] | [Priority]
  - [Additional context: dependencies, created date, sub-tasks if parent]
```

For sub-tasks nested under parents:

```markdown
- [ ] **[PARENT-KEY]** Status — [Parent title]
  - Status: [tracker status] | **[PARENT PRIORITY]** ⚠️ (if Highest)
  - Sub-tasks assigned to you:
    - **[SUBTASK-KEY]** Sub-task — [Subtask title]
```

### Step 7: Update notes

Create or update in `MEMORY_DIR`:
- `sprint-current.md` — Sprint snapshot with Code Freeze, task counts, critical path
- `subtask-bugs.md` — Explanation of bug hierarchy (if first sprint)
- `sprint-rules.md` — Sprint priority rules (if first sprint)

If `WIKI_LOG` is not `none`, append:
```markdown
## [YYYY-MM-DD] setup | Sprint initialization (sprint-init skill)

**Tasks fetched:** N items (project/repo: X)
**Code Freeze:** [date] (~N days away)
**Breakdown:** X Features, Y Technical, Z Bugs

**Critical issues:** [List Highest-priority bugs if any]

**Files updated:**
- TASKS.md
- memory/sprint-current.md
```

## Edge cases

**Multiple Code Freeze dates:** Return the soonest upcoming one.

**No Code Freeze in calendar:** Note in `sprint-current.md`: "No Code Freeze date found in calendar. Check manually."

**Sub-tasks with no parent:** Log a warning but treat as standalone task.

**User not assigned to all sub-tasks:** Only include sub-tasks where the user is the assignee.

**Tracker has no sprint concept for the repo:** Ask the user which milestone/iteration/cycle to use.
