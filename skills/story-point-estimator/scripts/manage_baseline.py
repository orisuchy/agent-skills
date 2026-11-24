#!/usr/bin/env python3
"""Add, edit, remove, or list entries in the story-point baseline table.

The baseline table anchors new estimates to known, already-sized tickets.
Data file: ../baseline-table.json (sibling of this scripts/ directory).

Usage:
  manage_baseline.py list
  manage_baseline.py add    --key PROJ-1234 --points 5 --summary "..." [--notes "..."]
  manage_baseline.py edit   --key PROJ-1234 [--points 8] [--summary "..."] [--notes "..."]
  manage_baseline.py remove --key PROJ-1234
"""
import argparse
import json
import os
import sys
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "baseline-table.json"

# Allowed point values; override with POINT_SCALE="1,2,3,5,8" (default: Fibonacci).
FIBONACCI = {int(x) for x in os.environ.get("POINT_SCALE", "1,2,3,5,8,13,21").split(",")}


def load():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open() as f:
        return json.load(f)


def save(entries):
    with DATA_FILE.open("w") as f:
        json.dump(entries, f, indent=2)
        f.write("\n")


def cmd_list(args):
    entries = load()
    if not entries:
        print("Baseline table is empty.")
        return
    for e in sorted(entries, key=lambda x: x["points"]):
        print(f"{e['points']:>3}  {e['key']:<12} {e['summary']}")


def cmd_add(args):
    if args.points not in FIBONACCI:
        sys.exit(f"error: --points must be one of {sorted(FIBONACCI)} (POINT_SCALE)")
    entries = load()
    if any(e["key"] == args.key for e in entries):
        sys.exit(f"error: {args.key} already exists. Use 'edit' to change it.")
    entries.append({
        "key": args.key,
        "points": args.points,
        "summary": args.summary,
        "notes": args.notes or "",
    })
    save(entries)
    print(f"Added {args.key} — {args.points} points.")


def cmd_edit(args):
    if args.points is not None and args.points not in FIBONACCI:
        sys.exit(f"error: --points must be one of {sorted(FIBONACCI)} (POINT_SCALE)")
    entries = load()
    for e in entries:
        if e["key"] == args.key:
            if args.points is not None:
                e["points"] = args.points
            if args.summary is not None:
                e["summary"] = args.summary
            if args.notes is not None:
                e["notes"] = args.notes
            save(entries)
            print(f"Updated {args.key}.")
            return
    sys.exit(f"error: {args.key} not found. Use 'add' to create it.")


def cmd_remove(args):
    entries = load()
    remaining = [e for e in entries if e["key"] != args.key]
    if len(remaining) == len(entries):
        sys.exit(f"error: {args.key} not found.")
    save(remaining)
    print(f"Removed {args.key}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all baseline entries, sorted by points").set_defaults(func=cmd_list)

    p_add = sub.add_parser("add", help="Add a new baseline entry")
    p_add.add_argument("--key", required=True, help="Ticket key, e.g. PROJ-1234")
    p_add.add_argument("--points", required=True, type=int, help="Point value (must be in POINT_SCALE)")
    p_add.add_argument("--summary", required=True, help="Short ticket summary")
    p_add.add_argument("--notes", default="", help="Why it earned this score (reference the 5 dimensions)")
    p_add.set_defaults(func=cmd_add)

    p_edit = sub.add_parser("edit", help="Edit an existing baseline entry")
    p_edit.add_argument("--key", required=True)
    p_edit.add_argument("--points", type=int)
    p_edit.add_argument("--summary")
    p_edit.add_argument("--notes")
    p_edit.set_defaults(func=cmd_edit)

    p_remove = sub.add_parser("remove", help="Remove a baseline entry")
    p_remove.add_argument("--key", required=True)
    p_remove.set_defaults(func=cmd_remove)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
