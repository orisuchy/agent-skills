---
name: write-tests-from-plan
description: Turn a test plan into approved tickets, implemented tests and a self-review in this repo. Use when asked to "automate this test plan", "write tests for case …", or given a test-management case id, a QA ticket key, or a test plan.
---

# Write tests from a plan

Steps and pointers only. Rules live in the linked docs; read them, do not restate them.
Read first: [AGENTS.md](../../../AGENTS.md), [{{agent workflow doc}}](../../../{{docs/agent-workflow.md}}),
[{{writing-tests doc}}](../../../{{docs/writing-tests.md}}), {{other rule docs: allure, CONTEXT.md, issue tracker}}.

## 1. Get the plan
- Test-management case ids or a folder: [{{test-management lookup section}}](../../../{{docs/writing-tests.md#…}}). Delete this line if the repo has no test-management tool.
- A plan already published to the test-management tool: use the lookup above with its ids. Not published yet: read the plan attachment on the tracker ticket, or the plan file.
- Pasted text or a QA ticket: use as given.
- No source works: stop and ask. Never invent steps.

## 2. Triage each case
One line per case: automatable here or not, with the reason. Apply {{the repo's "cannot be automated" note}}.
Before calling a step UI-only, search {{the helper API docs}} for it.
UI-only checks are listed as out of scope, never dropped silently.

## 3. Map each automatable case
- Product terms: {{CONTEXT.md / glossary}}. Unknown term: ask, or note the gap.
- Nearest sibling test to copy: {{where the docs say to look}}, then grep `{{tests dir}}/`.
- Helpers: {{helpers section}}; helpers that fail silently: {{section}}. Fixtures and markers: {{docs}}.
- The file and class the test goes in.
- {{Exact-assertion rule pointer, e.g. "Event actions: the exact-set rule in writing-tests §1."}}
- An expectation you derived, not copied from a test or a capture, is marked "inferred" in the ticket and the report.
- For each endpoint the test writes through, check the helper's body against what the product accepts. Sources, in
  order: the the product's controller/DTO if the developer has it checked out (ask for the path in the step 4 ask; never write a
  local path into the repo), else a captured request from the console (no auth headers) from the user. Neither: say
  so in the ticket's "Not verifiable offline".
- A plan step the helper cannot express: call the client directly with the product's body (from the sources above),
  or ask. Never narrow the case's scope silently.

## 4. Write tickets
- One ticket per test-file concern, in `.scratch/<feature>/issues/`, from [ticket-template.md](ticket-template.md).
- Ask the user once, every question together: scope, product source or captured request (step 3), beta run yes or no
  ([{{test-authoring section}}](../../../{{docs/agent-workflow.md#…}})).
  Write the beta answer into each ticket's "Done when".
- Show the tickets and wait for approval. A change the user dictates counts as approval of that change; any other change is shown again before implementing.

## 5. Implement
One fresh `/implement <ticket>` per ticket, or `/feature-flow` for several.
If `/implement` is not available, implement each ticket yourself under
[{{test-authoring section}}](../../../{{docs/agent-workflow.md#…}}), one commit per ticket.
A revision after a failed beta run is a new commit; a second beta run needs the user's yes.

## 6. Self-review
Run `/review` (or your agent's code-review command) on the branch (standards: the docs above; spec: the plan).
If `/review` is not available, check the diff against {{named doc sections: steps, links, attachments, names, logging, teardown, assertion messages, setup proven}}.
Then check plan coverage: every plan step is {{a reporting step, e.g. an `allure.step`}}; every case id is {{a marker with a matching link}}.

## 7. Report
Fill the [PR/MR template](../../../{{.github/pull_request_template.md or .gitlab/merge_request_templates/Default.md}}), including its test-cases section.
Write it to `.scratch/<feature>/mr-description.md` and show it in the report.
