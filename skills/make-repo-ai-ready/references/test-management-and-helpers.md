# Test-management reading and helper rules (C8, C9)

Reference shape: `docs/writing-tests.md` sections "where to find things", "reading cases from the test-management
tool", "when a helper looks wrong"; `docs/agent-workflow.md` (Forbidden exceptions, stop-and-ask "helper bug",
Reporting); the PR/MR template (definition of done, "test cases" section).

## C8 Helpers: where to find the API
- Point agents at the helper docs, not the helper source. A shared helper package may ship `<pkg>/AGENTS.md`
  (guide, read it) and `<pkg>/API.md` (generated, search it, do not read it whole). Give the find-spec command,
  the package list, which packages lack `AGENTS.md`, and a fallback (grep the public `def`s) for installed
  versions that predate `API.md`.
- In-repo helpers: the same rule, pointing at their docstrings or a generated API doc in this repo.

## C8 Helpers: diagnosis without reading the source
The main failure the reference experiment found: a helper that "returns nothing" had failed silently (a stale
request body, 400 ignored), and the test then saw no events. The doc section must say:
1. **Prove setup in the test**: after every state-changing setup call, read the object back or assert the
   response is ok. Name this repo's silent helpers and one example test that does it right.
2. **A negative test needs a positive control**; name any "no request sent" trap (e.g. `retries=0`).
3. **When to diagnose**: a helper acts against its docs, or a live run produces nothing (0 events, empty list,
   poll timeout). Check setup before changing data, timing or retries.
4. **Docs first** (`API.md` entry, `AGENTS.md` pitfalls), then **pick the suspect** (a traceback in a read or poll
   usually means an earlier setup call), then **read only that function** (grep its `def`, print its lines).
5. **Decide**: test wrong → fix the test; helper wrong → never patch or monkeypatch, the test may make the request
   itself with `# <pkg>.<fn> (v<version>) sends <old>; product expects <new>`, report with the proposed fix;
   docs wrong → propose the doc line for the helper package.
- agent-workflow: stop-and-ask "Helper bug" with that workaround allowed and reported.

## C9 Test management (`TEST_MGMT`)
Skip this section when `TEST_MGMT` is `none`; then plans arrive as pasted text or tracker tickets, and the
repo needs no case-id marker. Otherwise the steps are tool-independent:
- Read cases in this order: an MCP server for the tool if the session has one; the tool's REST API with an API
  token; else ask the user. Never write to the tool from the agent.
- The token is in the system environment or the repo's `.env` (system wins). One command takes it into a shell
  variable in the same call as the request and never prints it; agent-workflow lists this as the only exception to
  "never read `.env*`" and to "no network". Add the token variable to the env declaration if the repo has one.
- Record the case's title, description, steps (action and expected result per step) and the project/folder id.
  The project id is usually not derivable from the tracker key: list the projects and confirm.
- "cannot be automated" is not final: check the glossary's simulated-activity helpers first.
- Case id → a marker carrying the id + a matching `allure.link` (or the repo's reporting link); each case step →
  one `allure.step`.
- PR/MR template: a definition-of-done item for case status and a "test cases" section with one unticked
  "set to Automated" line per new marker. A person ticks it; the agent never writes to the tool.

### Worked example: Testmo
- MCP server if present; else REST with `TESTMO_TOKEN`.
- `GET /api/v1/projects/<id>/cases?folder_id=&per_page=100&page=N` until `next_page` is null; fields `name`,
  `custom_description`, `custom_steps[]` (`text1` action, `text3` expected) or `custom_draft_steps[]`; HTML fields.
  Check Testmo's API docs for the current shape before relying on these fields.
- Marker `testmo_<id>`; PR/MR line `Set to Automated: [case <id>](<case url>)`.
