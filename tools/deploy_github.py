# -*- coding: utf-8 -*-
"""
把当前文件夹推到一个 GitHub 仓库（不需要装 git，走 REST API）。

用法：
    set GH_TOKEN=ghp_xxx           （或运行时按提示粘贴）
    python tools/deploy_github.py [仓库名]

权限只需要：fine-grained token → 该仓库的 Contents: Read and write + Metadata: Read
（首次建仓库还需要 Administration: Read and write，或者去网页先建一个空仓库）
"""
import base64
import getpass
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", ".vscode", ".idea", "node_modules"}
SKIP_FILES = {"online-state.json", "新建文本文档.txt"}
SKIP_EXT = {".pyc", ".log"}


def call(method, path, token, data=None, raw=False):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        API + path, data=body, method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "xinhuo-deploy",
        },
    )
    last = None
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                payload = r.read().decode("utf-8")
                return (payload if raw else json.loads(payload or "{}")), r.status
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")
            last = (e.code, detail)
            if e.code in (401, 429, 500, 502, 503, 504):
                time.sleep(1.5 * attempt)
                continue
            break
        except Exception as e:
            last = (0, str(e))
            time.sleep(1.5 * attempt)
            continue
    raise SystemExit("GitHub API %s %s -> %s\n%s" % (method, path, last[0], last[1][:600]))


def collect():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn in SKIP_FILES:
                continue
            if os.path.splitext(fn)[1].lower() in SKIP_EXT:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            if rel.startswith("tools/pylibs/") and fn.endswith(".pyc"):
                continue
            out.append((rel, full))
    return out


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print()
        print("  需要一个 GitHub token（只勾选本仓库 Contents 读写即可）")
        print("  生成地址： https://github.com/settings/tokens?type=beta")
        print()
        token = getpass.getpass("  粘贴 token（输入不显示）: ").strip()
    if not token:
        raise SystemExit("没有 token，退出")

    name = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not name:
        name = input("  仓库名（回车用 xinhuo-renyi）: ").strip() or "xinhuo-renyi"

    me, _ = call("GET", "/user", token)
    owner = me["login"]
    print("  账号：%s   仓库：%s" % (owner, name))

    # 1) 建仓库（已存在就复用）
    status = None
    try:
        _, status = call("POST", "/user/repos", token, {
            "name": name,
            "description": "薪火仁义 · 天全县仁义镇红色研学与在地体验小程序（数字乡村服务设计）",
            "private": False,
            "has_issues": True,
            "has_wiki": False,
            "auto_init": False,
        })
        print("  ✓ 已创建仓库")
    except SystemExit as e:
        if "422" in str(e):
            print("  · 仓库已存在，直接推送")
        else:
            raise

    # 2) 现有分支头（新仓库为空）
    head_sha = None
    base_tree = None
    try:
        ref, _ = call("GET", "/repos/%s/%s/git/ref/heads/main" % (owner, name), token)
        head_sha = ref["object"]["sha"]
        commit, _ = call("GET", "/repos/%s/%s/git/commits/%s" % (owner, name, head_sha), token)
        base_tree = commit["tree"]["sha"]
        print("  · 已有 main 分支，在此基础上追加提交")
    except SystemExit:
        print("  · 新仓库，创建首个提交")

    # 空仓库里 Git Data API 会返回 409，先用 Contents API 落一个初始提交
    if not head_sha:
        call("PUT", "/repos/%s/%s/contents/.gitignore" % (owner, name), token, {
            "message": "chore: init", "content": base64.b64encode(b"# init\n").decode("ascii")})
        ref, _ = call("GET", "/repos/%s/%s/git/ref/heads/main" % (owner, name), token)
        head_sha = ref["object"]["sha"]
        commit, _ = call("GET", "/repos/%s/%s/git/commits/%s" % (owner, name, head_sha), token)
        base_tree = commit["tree"]["sha"]
        print("  · 空仓库：已落初始提交")

    # 3) 上传文件为 blob
    files = collect()
    print("  上传 %d 个文件…" % len(files))
    entries = []
    for i, (rel, full) in enumerate(files, 1):
        with open(full, "rb") as f:
            data = f.read()
        blob, _ = call("POST", "/repos/%s/%s/git/blobs" % (owner, name), token, {
            "content": base64.b64encode(data).decode("ascii"),
            "encoding": "base64",
        })
        entries.append({"path": rel, "mode": "100755" if full.endswith(".cmd") else "100644",
                        "type": "blob", "sha": blob["sha"]})
        if i % 10 == 0 or i == len(files):
            print("    %d/%d" % (i, len(files)))

    # 4) 建树 + 提交 + 更新引用
    tree_payload = {"tree": entries}
    if base_tree:
        tree_payload["base_tree"] = base_tree
    tree, _ = call("POST", "/repos/%s/%s/git/trees" % (owner, name), token, tree_payload)

    commit_payload = {"message": "部署：薪火仁义交互原型 + 联机演示服务", "tree": tree["sha"]}
    if head_sha:
        commit_payload["parents"] = [head_sha]
    commit, _ = call("POST", "/repos/%s/%s/git/commits" % (owner, name), token, commit_payload)

    if head_sha:
        call("PATCH", "/repos/%s/%s/git/refs/heads/main" % (owner, name), token, {"sha": commit["sha"]})
    else:
        call("POST", "/repos/%s/%s/git/refs" % (owner, name), token,
             {"ref": "refs/heads/main", "sha": commit["sha"]})

    url = "https://github.com/%s/%s" % (owner, name)
    print()
    print("  ✓ 推送完成：%s" % url)
    print("  ✓ 仓库地址（给 Render 用）：%s.git" % url)
    print()
    return url


if __name__ == "__main__":
    main()
