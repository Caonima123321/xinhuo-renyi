# -*- coding: utf-8 -*-
"""分阶段推送：先把能跑的最小集推到 main，再补其余文件。
用法： python tools/push_phase.py core|rest
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "Caonima123321"
REPO = "xinhuo-renyi"
TOKEN = os.environ.get("GH_TOKEN", "")

CORE = [
    "薪火仁义-交互原型.html",
    "index.html",
    "tools/server.py",
    "render.yaml",
    "requirements.txt",
    "README.md",
    ".gitignore",
]
REST_SKIP = {".git", "__pycache__", ".vscode", ".idea", "node_modules", "online-state.json"}


def call(method, path, data=None):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    last = (0, "")
    for attempt in range(1, 7):
        req = urllib.request.Request(
            API + path, data=body, method=method,
            headers={"Authorization": "Bearer " + TOKEN,
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28",
                     "Content-Type": "application/json",
                     "Connection": "close",
                     "User-Agent": "xinhuo-push"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            last = (e.code, detail)
            if e.code in (401, 403, 404, 429, 500, 502, 503, 504):
                time.sleep(min(3 * attempt, 15))
                continue
            raise SystemExit("API %s %s -> %s\n%s" % (method, path, e.code, detail[:400]))
        except Exception as e:
            last = (0, str(e))
            time.sleep(2 * attempt)
    raise SystemExit("API %s %s 重试耗尽 -> %s\n%s" % (method, path, last[0], last[1][:300]))


def walk_all():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in REST_SKIP]
        for fn in filenames:
            if fn.endswith(".pyc") or fn == "新建文本文档.txt":
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            out.append((rel, full))
    return out


def main():
    if not TOKEN:
        raise SystemExit("缺少 GH_TOKEN")
    phase = sys.argv[1] if len(sys.argv) > 1 else "core"

    ref = call("GET", "/repos/%s/%s/git/ref/heads/main" % (OWNER, REPO))
    head = ref["object"]["sha"]
    commit = call("GET", "/repos/%s/%s/git/commits/%s" % (OWNER, REPO, head))
    base_tree = commit["tree"]["sha"]

    if phase == "core":
        files = [(r, os.path.join(ROOT, r)) for r in CORE if os.path.exists(os.path.join(ROOT, r))]
    else:
        done = {r for r in CORE if r != "requirements.txt"}
        files = [(rel, full) for rel, full in walk_all() if rel not in done]

    print("  阶段 %s：%d 个文件" % (phase, len(files)))
    entries = []
    failed = []
    for i, (rel, full) in enumerate(files, 1):
        data = open(full, "rb").read()
        try:
            blob = call("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO),
                        {"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"})
        except SystemExit as e:
            failed.append(rel)
            print("    ! %s 失败：%s" % (rel, str(e)[:100]))
            continue
        entries.append({"path": rel, "mode": "100755" if rel.endswith((".cmd", ".sh")) else "100644",
                        "type": "blob", "sha": blob["sha"]})
        if i % 5 == 0 or i == len(files):
            print("    %d/%d  %s" % (i, len(files), rel))

    for rel in list(failed):
        full = os.path.join(ROOT, rel.replace("/", os.sep))
        try:
            data = open(full, "rb").read()
            blob = call("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO),
                        {"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"})
            entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
            failed.remove(rel)
            print("    \u2713 重试成功 %s" % rel)
        except SystemExit:
            pass

    tree = call("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO), {"tree": entries, "base_tree": base_tree})
    new = call("POST", "/repos/%s/%s/git/commits" % (OWNER, REPO),
               {"message": "deploy: %s 批次（%d 文件）" % (phase, len(entries)), "tree": tree["sha"], "parents": [head]})
    call("PATCH", "/repos/%s/%s/git/refs/heads/main" % (OWNER, REPO), {"sha": new["sha"], "force": True})
    print("  ✓ %s 完成，%d 个文件已提交 %s" % (phase, len(entries), new["sha"][:8]))
    if failed:
        print("  ! 失败 %d 个：%s" % (len(failed), ", ".join(failed[:8])))


if __name__ == "__main__":
    main()
