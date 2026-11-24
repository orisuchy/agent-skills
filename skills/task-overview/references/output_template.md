# Output Template

Fill in the structure below. Omit any section that genuinely doesn't apply (e.g., "Deviations from plan" if there were none) — but don't omit something just because it's mildly tedious to write.

---

```markdown
# {Ticket ID if any} — {short human title of the work}

**Date:** {YYYY-MM-DD}
**Branch(es):** {repo: branch, repo: branch}
**Type:** {New feature | Bug fix | Refactor | Mixed}

## What this was

{1–3 sentences: the feature or issue worked on. Frame it the way you'd describe it to yourself in a week. Include the user-visible problem or goal, not just the technical surface.}

## Plan / approach

{The plan as it stood when work began. Bullet points are fine. If the plan came from a ticket, link or paraphrase the relevant part. If the approach was decided mid-session, capture the chosen path and the alternative(s) that were rejected and why.}

## What was actually done

{Bullet list of the concrete changes made, in the order they happened or in the order that makes the most sense to re-read. Tie each bullet to the plan when possible. If something was scoped out, called out as follow-up, or punted to a later ticket, mention it here.}

## Deviations from plan

{Only include if applicable. Examples: "Discovered X assumption was wrong, so switched to Y", "Original approach hit a circular dependency, refactored Z first", "Cut scope on the admin UI piece — to be done in {follow-up ticket} if filed."}

## Files changed

{Group by repo if multi-repo. For each file: path, then a one-line "why" rooted in the plan, not just a description of the diff.}

### {repo-name}

- `path/to/file.ts` — {why this changed}
- `path/to/other.ts` — {why this changed}

## Code examples

{Pick the load-bearing changes — the ones a reader would need to see to understand the work. For new features, full snippets. For changes/fixes, before/after.}

### {Short label of what this snippet shows}

**File:** `path/to/file.ts:LINE`

For a new feature — full snippet:

```ts
// new code
```

For a change/fix — before/after:

```ts
// before
```

```ts
// after
```

{One sentence on what changed and why, if not already obvious from the surrounding sections.}

## Notes for future-me

{Anything else worth surfacing: tricky bits, gotchas hit during the work, follow-ups not yet ticketed, things tested manually vs. covered by tests, environments where this was/wasn't verified. This section is the "color commentary" — keep it brief but don't skip it.}

## Verification

{What was done to verify the change works: tests added/run, manual check, deployed to staging, etc. If verification was thin, say so honestly — that's useful information later.}
```

---

## Notes on filling this in

- **Headings are required as written** so the doc is greppable across many overview files.
- **Code blocks**: language-tag them properly (`ts`, `py`, `java`, `bash`, etc.).
- **Line numbers**: include them in file references when pointing at a specific hunk (`path/to/file.ts:142`).
- **Multi-repo grouping**: under "Files changed" and "Code examples", add a `### {repo-name}` subheading per repo. Skip the subheading if only one repo is involved.
- **Length**: short is fine. A small bug fix is a one-page doc. A big feature is several pages. Don't pad.
