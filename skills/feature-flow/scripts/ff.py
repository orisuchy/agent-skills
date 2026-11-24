#!/usr/bin/env python3
"""Agent bookkeeping for feature-flow, so the orchestrator cannot forget a step.

  ff.py start <feature> <name> <role> <ticket> <model> [--kind KIND] [--cwd DIR]
      Opens a worker pane per the skill's Layout, starts the agent (KIND = any
      `herdr agent start --kind`, default claude), writes its ledger row (usage.tsv)
      with the session id. <model> is a tier (planner/implementer/mechanical) or a
      model id. Prints the agent's pane id.
  ff.py close <feature> <name>
      Captures /cost into cost.tsv (claude only, else n/a), fills a missing session
      id, closes the pane/tab this script opened. Never touches panes it did not open.
  ff.py orch <feature>
      Adds the orchestrator's own ledger row (agent whose pane is $HERDR_PANE_ID).

State lives in .scratch/<feature>/ under the current directory:
  usage.tsv  name, role, ticket, model, session_id, kind   (read by usage.py)
  cost.tsv   name, cost as printed by /cost, or n/a
  panes.tsv  name, pane_id, tab_id ('-' = pane in the right-hand worker column)
Set HERDR_BIN to point at a different herdr binary (used by the self-check).
"""
import json, os, re, subprocess, sys

HERDR = os.environ.get("HERDR_BIN", "herdr")
# Tier -> model id per agent kind. A kind without an entry uses the agent's own default.
# Aliases opus/sonnet/haiku stay for old ticket lines. Edit when new versions ship.
_CLAUDE = {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5"}
TIERS = {"claude": {**_CLAUDE, "planner": _CLAUDE["opus"], "implementer": _CLAUDE["sonnet"],
                    "mechanical": _CLAUDE["haiku"]}}
TIER_NAMES = ("planner", "implementer", "mechanical", *_CLAUDE)  # never sent as a literal id
DEFAULT_KIND = "claude"
MODEL_FLAG = {"claude", "codex", "gemini", "copilot"}  # --model checked in each CLI's help/docs
MAX_COLUMN = 3  # worker panes visible in the right column; more go to their own tab


def herdr(*args, check=True):
    p = subprocess.run([HERDR, *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        sys.exit(f"herdr {' '.join(args)} failed: {p.stderr.strip() or p.stdout.strip()}")
    try:
        return p.returncode, json.loads(p.stdout or p.stderr or "{}")  # herdr prints some errors on stderr
    except ValueError:
        return p.returncode, {}


def rows(path):
    if not os.path.exists(path):
        return []
    return [l.rstrip("\n").split("\t") for l in open(path) if l.strip()]


def write_rows(path, rs):
    with open(path, "w") as f:
        f.writelines("\t".join(r) + "\n" for r in rs)


def append(path, *fields):
    with open(path, "a") as f:
        f.write("\t".join(fields) + "\n")


def session_id(name):
    rc, out = herdr("agent", "get", name, check=False)
    try:
        return out["result"]["agent"]["agent_session"]["value"] or "-"
    except (KeyError, TypeError):
        return "-"


def model_args(kind, model):
    """Extra agent args for `herdr agent start`: [] means use the agent's default model."""
    m = TIERS.get(kind, {}).get(model) or (None if model in TIER_NAMES else model)
    if not m:
        return []
    if kind not in MODEL_FLAG:
        print(f"note: {kind} --model flag not verified; starting with its default model, not {m}", file=sys.stderr)
        return []
    return ["--", "--model", m]


def start(d, name, role, ticket, model, cwd, kind):
    panes = os.path.join(d, "panes.tsv")
    column = [r for r in rows(panes) if r[2] == "-"]
    tab = "-"
    if len(column) >= MAX_COLUMN:
        _, out = herdr("tab", "create", "--cwd", cwd, "--label", name, "--no-focus")
        t = out["result"]["tab"]
        pane, tab = out["result"]["root_pane"]["pane_id"], t.get("tab_id") or t["id"]
    else:
        target = ["--current", "--direction", "right"] if not column else [column[-1][1], "--direction", "down"]
        _, out = herdr("pane", "split", *target, "--cwd", cwd, "--no-focus")
        pane = out["result"]["pane"]["pane_id"]
    append(panes, name, pane, tab)  # record before start, so close can clean up a failed start

    rc, out = herdr("agent", "start", name, "--kind", kind, "--pane", pane, *model_args(kind, model), check=False)
    # Write the ledger row even when start reports agent_not_ready: the agent exists and spends tokens.
    append(os.path.join(d, "usage.tsv"), name, role, ticket, model, session_id(name), kind)
    print(pane)
    if rc != 0:
        sys.exit(f"agent start {name} returned an error (row recorded, pane {pane} kept): {json.dumps(out)}")


def close(d, name):
    panes = os.path.join(d, "panes.tsv")
    mine = [r for r in rows(panes) if r[0] == name]
    if not mine:
        sys.exit(f"{name} was not opened by ff.py start; not closing anything")
    _, pane, tab = mine[-1]

    # Session id disappears with the pane: fill it now if start could not read it.
    usage = os.path.join(d, "usage.tsv")
    ledger = rows(usage)
    sid, kind = "-", DEFAULT_KIND
    for r in reversed(ledger):
        if r[0] == name:
            if r[4] == "-":
                r[4] = session_id(name)
            sid, kind = r[4], (r[5] if len(r) > 5 else DEFAULT_KIND)  # old 5-column rows
            break
    write_rows(usage, ledger)

    cost = "n/a"  # /cost is a Claude Code command; other kinds have no equivalent here
    if kind == "claude":
        rc, _ = herdr("agent", "prompt", name, "/cost", "--wait", "--timeout", "60000", check=False)
        if rc == 0:
            _, out = herdr("agent", "read", name, "--source", "recent-unwrapped", "--lines", "20", check=False)
            text = json.dumps(out)  # the read text sits somewhere under .result; search all of it
            hits = re.findall(r"Total cost:\s*(\$[\d.,]+)", text)
            cost = hits[-1] if hits else "n/a"  # never estimate
    append(os.path.join(d, "cost.tsv"), name, cost)

    if tab == "-":
        herdr("pane", "close", pane, check=False)
    else:
        herdr("tab", "close", tab, check=False)
    write_rows(panes, [r for r in rows(panes) if r[0] != name])
    print(f"{name}\tsession={sid}\tcost={cost}")


def orch(d):
    me = os.environ.get("HERDR_PANE_ID")
    if not me:
        sys.exit("HERDR_PANE_ID is not set; run this inside the orchestrator's Herdr pane")
    _, out = herdr("agent", "list")
    agents = out.get("result", {}).get("agents", [])
    a = next((a for a in agents if a.get("pane_id") == me), None)
    sid = (a or {}).get("agent_session", {}).get("value") or "-"
    append(os.path.join(d, "usage.tsv"), "orchestrator", "orch", "-", "planner", sid, (a or {}).get("agent") or DEFAULT_KIND)
    print(sid)


def main(argv):
    if len(argv) < 2 or argv[0] not in ("start", "close", "orch"):
        sys.exit(__doc__)
    cmd, feature, rest = argv[0], argv[1], argv[2:]
    opts = {"--cwd": os.getcwd(), "--kind": DEFAULT_KIND}
    for flag in opts:
        if flag in rest:
            i = rest.index(flag)
            if i + 1 >= len(rest):
                sys.exit(__doc__)
            opts[flag] = rest[i + 1]
            rest = rest[:i] + rest[i + 2:]
    d = os.path.join(".scratch", feature)
    os.makedirs(d, exist_ok=True)
    if cmd == "start" and len(rest) == 4:
        start(d, *rest, opts["--cwd"], opts["--kind"])
    elif cmd == "close" and len(rest) == 1:
        close(d, rest[0])
    elif cmd == "orch" and not rest:
        orch(d)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
