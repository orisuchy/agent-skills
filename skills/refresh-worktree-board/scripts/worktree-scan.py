"""Scan git repos for worktrees; print JSON, or write a self-contained HTML board.

Usage: python3 worktree-scan.py [--html OUT.html] [root ...]
Roots: args, else $WORKTREE_ROOTS (os.pathsep-separated), else the current directory.
No git fetch is done: ahead/behind and "upstream gone" are as of your last fetch.
"""
import hashlib, html, json, os, re, subprocess, sys, time

ARGS = sys.argv[1:]
HTML_OUT = ""
if "--html" in ARGS:
    i = ARGS.index("--html")
    HTML_OUT = ARGS[i + 1]
    del ARGS[i:i + 2]
ROOTS = ARGS or [r for r in os.environ.get("WORKTREE_ROOTS", "").split(os.pathsep) if r] or ["."]
SKIP = {"node_modules", ".venv", "venv", "target", "build", "dist"}


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def find_repos(root, depth=6):
    root = os.path.expanduser(root)
    for dirpath, dirs, files in os.walk(root):
        if dirpath[len(root):].count(os.sep) >= depth:
            dirs[:] = []
            continue
        if ".git" in dirs:  # real repo (worktrees have a .git *file*)
            yield dirpath
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith(".")]


def parse_porcelain(text):
    out, cur = [], {}
    for line in text.splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
            cur = {}
            continue
        k, _, v = line.partition(" ")
        cur[k] = v or True
    return out


def default_base(repo):
    ref = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if ref:
        return ref
    for b in ("origin/develop", "origin/main", "origin/master", "develop", "main"):
        if git(repo, "rev-parse", "--verify", "-q", b):
            return b
    return ""


def scan_repo(repo):
    wts = parse_porcelain(git(repo, "worktree", "list", "--porcelain"))
    if len(wts) < 2:
        return []
    base = default_base(repo)
    rows = []
    for i, w in enumerate(wts):
        path = w["worktree"]
        branch = w.get("branch", "").removeprefix("refs/heads/") if isinstance(w.get("branch"), str) else ""
        row = {
            "id": hashlib.sha1(path.encode()).hexdigest()[:16],
            "repo": os.path.basename(repo),
            "repoPath": repo,
            "path": path,
            "isMain": i == 0,
            "branch": branch,
            "detached": "detached" in w,
            "locked": "locked" in w,
            "prunable": "prunable" in w,
            "head": (w.get("HEAD") or "")[:8],
            "base": base,
        }
        m = re.search(r"[A-Za-z]+-\d+", branch)
        row["ticket"] = m.group(0).upper() if m else ""
        if row["prunable"] or not os.path.isdir(path):
            row["prunable"] = True
            rows.append(row)
            continue
        log = git(path, "log", "-1", "--format=%ct%x09%s")
        if log:
            ts, _, subj = log.partition("\t")
            row["lastCommitAt"] = int(ts)
            row["lastCommitSubject"] = subj[:120]
        status = git(path, "status", "--porcelain")
        row["dirty"] = len(status.splitlines()) if status else 0
        if branch:
            up = git(repo, "for-each-ref", "--format=%(upstream:short)\t%(upstream:track)", f"refs/heads/{branch}")
            upstream, _, track = up.partition("\t")
            row["upstream"] = upstream
            row["upstreamGone"] = "[gone]" in track
            if upstream and not row["upstreamGone"]:
                lr = git(path, "rev-list", "--left-right", "--count", f"{upstream}...HEAD").split()
                if len(lr) == 2:
                    row["behind"], row["ahead"] = int(lr[0]), int(lr[1])
            elif not upstream:
                # never pushed: count commits not on base
                n = git(path, "rev-list", "--count", f"{base}..HEAD") if base else ""
                row["ahead"] = int(n) if n.isdigit() else None
            row["mergedIntoBase"] = bool(base) and subprocess.run(
                ["git", "-C", repo, "merge-base", "--is-ancestor", f"refs/heads/{branch}", base]
            ).returncode == 0
        rows.append(row)
    return rows


def status(r):
    if r.get("prunable"):
        return "remove"
    if r.get("dirty") or r.get("ahead"):
        return "attention"
    if (r.get("mergedIntoBase") and not r.get("isMain")) or r.get("upstreamGone"):
        return "remove"
    return "ok"

def render_html(data):
    cols = ["repo", "branch", "ticket", "dirty", "ahead", "behind", "lastCommitSubject", "path", "status"]
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = ""
    for r in sorted(data["worktrees"], key=lambda r: (r["repo"], r["path"])):
        r = {**r, "status": status(r)}
        body += f'<tr class="{r["status"]}">' + "".join(
            f"<td>{html.escape(str(r.get(c, '') if r.get(c) is not None else ''))}</td>" for c in cols) + "</tr>"
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(data["scannedAt"]))
    return (f"<!doctype html><meta charset=utf-8><title>Worktree Board</title><style>"
            "body{font:14px system-ui;margin:1rem}table{border-collapse:collapse}td,th{border:1px solid #8884;padding:4px 8px;text-align:left}"
            "tr.attention{background:#fc03}tr.remove{background:#f003}</style>"
            f"<h1>Worktree Board</h1><p>Scanned {when}. Yellow = needs attention, red = safe to remove.</p>"
            f"<table><tr>{head}</tr>{body}</table>")

def main():
    rows, seen = [], set()
    for root in ROOTS:
        for repo in find_repos(root):
            real = os.path.realpath(repo)
            if real in seen:
                continue
            seen.add(real)
            rows.extend(scan_repo(repo))
    data = {"scannedAt": int(time.time()), "roots": ROOTS, "worktrees": rows}
    if HTML_OUT:
        with open(HTML_OUT, "w", encoding="utf-8") as f:
            f.write(render_html(data))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
