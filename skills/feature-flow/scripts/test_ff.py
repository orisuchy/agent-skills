#!/usr/bin/env python3
"""Self-check for ff.py against a fake herdr. Run: python3 test_ff.py"""
import os, subprocess, sys, tempfile

FF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ff.py")
FAKE = r'''#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
open(os.environ["FAKE_LOG"], "a").write(" ".join(a) + "\n")
n = sum(1 for _ in open(os.environ["FAKE_LOG"]))
def out(r): print(json.dumps({"result": r}))
if a[:2] == ["pane", "split"]: out({"pane": {"pane_id": f"w1:p{n}"}})
elif a[:2] == ["tab", "create"]: out({"tab": {"tab_id": "w1:t9"}, "root_pane": {"pane_id": "w1:p99"}})
elif a[:2] == ["agent", "start"]:
    if a[2] == "bad": print(json.dumps({"error": "agent_not_ready"}), file=sys.stderr); sys.exit(1)
    out({})
elif a[:2] == ["agent", "get"]: out({"agent": {"agent_session": {"value": "sid-" + a[2]}}})
elif a[:2] == ["agent", "read"]: out({"text": "> /cost\n  Total cost: $0.42\n  Total duration: 3m"})
elif a[:2] == ["agent", "list"]: out({"agents": [{"pane_id": "w1:p1", "agent_session": {"value": "sid-me"}}]})
else: out({})
'''


def run(*args, ok=True):
    p = subprocess.run([sys.executable, FF, *args], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (args, p.returncode, p.stdout, p.stderr)
    return p.stdout


with tempfile.TemporaryDirectory() as tmp:
    fake, log = os.path.join(tmp, "herdr"), os.path.join(tmp, "log")
    open(fake, "w").write(FAKE)
    os.chmod(fake, 0o755)
    os.environ.update(HERDR_BIN=fake, FAKE_LOG=log, HERDR_PANE_ID="w1:p1")
    os.chdir(tmp)
    st = lambda *p: open(os.path.join(".scratch/feat", *p)).read()
    calls = lambda: open(log).read().splitlines()

    run("orch", "feat")
    for i in (1, 2, 3, 4):
        run("start", "feat", f"impl-0{i}", "impl", f"0{i}-x", "haiku" if i == 1 else "sonnet")
    splits = [c for c in calls() if c.startswith(("pane split", "tab create"))]
    assert "--current --direction right" in splits[0], splits
    assert splits[1].startswith("pane split w1:p") and "down" in splits[1], splits
    assert splits[3].startswith("tab create"), splits          # 4th worker gets its own tab
    assert any("--model claude-haiku-5-5" in c for c in calls())
    ledger = st("usage.tsv").splitlines()
    assert ledger[0] == "orchestrator\torch\t-\topus\tsid-me", ledger
    assert ledger[1] == "impl-01\timpl\t01-x\thaiku\tsid-impl-01", ledger
    assert len(ledger) == 5

    out = run("close", "feat", "impl-04")
    assert "cost=$0.42" in out and "tab close w1:t9" in calls()[-1], (out, calls()[-1])
    run("close", "feat", "impl-02")
    assert calls()[-1].startswith("pane close"), calls()[-1]
    assert st("cost.tsv") == "impl-04\t$0.42\nimpl-02\t$0.42\n"
    assert [r.split("\t")[0] for r in st("panes.tsv").splitlines()] == ["impl-01", "impl-03"]

    last = st("panes.tsv").splitlines()[-1].split("\t")[1]
    run("start", "feat", "diag", "diag", "-", "sonnet")         # splits down from last column pane
    assert [c for c in calls() if c.startswith("pane split")][-1].startswith(f"pane split {last} --direction down")

    run("start", "feat", "bad", "impl", "05-y", "sonnet", ok=False)  # failed start still recorded
    assert st("usage.tsv").splitlines()[-1].startswith("bad\timpl\t05-y\tsonnet\t")
    assert "bad" in st("panes.tsv")

    run("close", "feat", "user-pane", ok=False)                 # never closes what it did not open
    print("ok")
