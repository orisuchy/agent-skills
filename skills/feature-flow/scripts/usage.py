#!/usr/bin/env python3
"""Sum token usage per agent from Claude Code transcripts. Usage: usage.py <ledger.tsv> [cost.tsv]
Ledger columns (tab-separated): name, role, ticket, model, session_id[, kind].
Rows of other agent kinds print n/a: only Claude Code transcripts are read."""
import glob, json, os, sys

def tally(sid):
    t = dict(turns=0, input=0, output=0, cache_write=0, cache_read=0)
    paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl"))
    if not paths:
        return None
    seen = set()  # streamed responses repeat the same message id
    for line in open(paths[0]):
        try:
            m = json.loads(line).get("message") or {}
        except ValueError:
            continue
        u = m.get("usage")
        if m.get("role") != "assistant" or not u or m.get("id") in seen:
            continue
        seen.add(m.get("id"))
        t["turns"] += 1
        t["input"] += u.get("input_tokens", 0)
        t["output"] += u.get("output_tokens", 0)
        t["cache_write"] += u.get("cache_creation_input_tokens", 0)
        t["cache_read"] += u.get("cache_read_input_tokens", 0)
    return t

cost = {}
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
    for r in open(sys.argv[2]):
        k, _, v = r.rstrip("\n").partition("\t")
        cost[k] = v
cols = ["turns", "input", "output", "cache_write", "cache_read"]
print("| agent | role | ticket | model | " + " | ".join(cols) + " | cost |")
print("|" + "---|" * (5 + len(cols)))
total = dict.fromkeys(cols, 0)
for row in open(sys.argv[1]):
    f = row.rstrip("\n").split("\t")
    if len(f) < 5:
        continue
    kind = f[5] if len(f) > 5 else "claude"
    if kind != "claude":
        print(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | n/a ({kind}) |" + " |" * (len(cols) - 1) + f" {cost.get(f[0], 'n/a')} |")
        continue
    t = tally(f[4])
    if t is None:
        print(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | transcript not found ({f[4]}) |" + " |" * len(cols))
        continue
    for c in cols:
        total[c] += t[c]
    print("| " + " | ".join(f[:4]) + " | " + " | ".join(f"{t[c]:,}" for c in cols) + f" | {cost.get(f[0], 'n/a')} |")
print("| **total** | | | | " + " | ".join(f"**{total[c]:,}**" for c in cols) + " | |")
