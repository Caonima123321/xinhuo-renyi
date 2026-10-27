# -*- coding: utf-8 -*-
"""推送指定文件到仓库（复用已有分支头，追加一个提交）。
用法： python tools/push_file.py README.md 薪火仁义-设计说明书.docx
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
OWNER, REPO = "Caonima123321", "xinhuo-renyi"
TOKEN = os.environ.get("GH_TOKEN", "")


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
            raise SystemExit("API %s %s -> %s\n%s" % (method, path, e.code, detail[:300]))
        except Exception as e:
            last = (0, str(e))
            time.sleep(2 * attempt)
    raise SystemExit("重试耗尽 %s %s -> %s %s" % (method, path, last[0], last[1][:200]))


def main():
    files = sys.argv[1:]
    if not files:
        raise SystemExit("用法： push_file.py <相对路径> ...")
    ref = call("GET", "/repos/%s/%s/git/ref/heads/main" % (OWNER, REPO))
    head = ref["object"]["sha"]
    commit = call("GET", "/repos/%s/%s/git/commits/%s" % (OWNER, REPO, head))
    base_tree = commit["tree"]["sha"]

    entries = []
    for rel in files:
        full = os.path.join(ROOT, rel)
        data = open(full, "rb").read()
        blob = call("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO),
                    {"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"})
        entries.append({"path": rel.replace(os.sep, "/"), "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print("  blob ok %s (%.2f MB)" % (rel, len(data) / 1048576))

    tree = call("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO), {"tree": entries, "base_tree": base_tree})
    new = call("POST", "/repos/%s/%s/git/commits" % (OWNER, REPO),
               {"message": "docs: 补线上地址", "tree": tree["sha"], "parents": [head]})
    call("PATCH", "/repos/%s/%s/git/refs/heads/main" % (OWNER, REPO), {"sha": new["sha"], "force": True})
    print("  提交 %s" % new["sha"][:8])


if __name__ == "__main__":
    main()
