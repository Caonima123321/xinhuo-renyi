# -*- coding: utf-8 -*-
"""
在 Render 上创建并部署本仓库的 Web Service。

用法：
    set RENDER_API_KEY=rnd_xxx
    python tools/deploy_render.py https://github.com/<你>/<仓库> [服务名]

Render API Key：控制台右上角头像 → Account Settings → API Keys → Create API Key
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.render.com/v1"


def call(method, path, key, data=None):
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        API + path, data=body, method=method,
        headers={"Authorization": "Bearer " + key, "Accept": "application/json",
                 "Content-Type": "application/json", "User-Agent": "xinhuo-deploy"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            payload = r.read().decode("utf-8")
            return json.loads(payload or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise SystemExit("Render API %s %s -> %s\n%s" % (method, path, e.code, detail[:800]))


def main():
    key = os.environ.get("RENDER_API_KEY")
    if not key:
        print()
        print("  需要 Render API Key：控制台 → Account Settings → API Keys")
        print()
        import getpass
        key = getpass.getpass("  粘贴 API Key（输入不显示）: ").strip()
    if not key:
        raise SystemExit("没有 key，退出")

    repo = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not repo:
        repo = input("  仓库地址（https://github.com/xxx/yyy）: ").strip()
    repo = repo.rstrip("/")
    if repo.endswith(".git"):
        repo = repo[:-4]
    name = (sys.argv[2] if len(sys.argv) > 2 else "").strip() or "xinhuo-renyi"

    owners = call("GET", "/owners?limit=20", key)
    if not owners:
        raise SystemExit("拿不到 owner，请确认 key 有权限")
    owner_id = owners[0]["owner"]["id"]
    print("  owner: %s" % owners[0]["owner"].get("name") or owner_id)

    # 已经有同名服务就直接给地址
    existing = call("GET", "/services?limit=50", key)
    for item in existing:
        s = item.get("service", {})
        if s.get("name") == name:
            print("  · 已存在服务 %s，直接复用" % name)
            print("  ✓ 地址：%s" % s.get("serviceDetails", {}).get("url", s.get("url", "")))
            return

    payload = {
        "type": "web_service",
        "name": name,
        "ownerId": owner_id,
        "repo": repo,
        "branch": "main",
        "autoDeploy": "yes",
        "envVars": [{"key": "PYTHON_VERSION", "value": "3.12.6"}],
        "serviceDetails": {
            "env": "python",
            "plan": "free",
            "region": "singapore",
            "healthCheckPath": "/healthz",
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "python tools/server.py",
            },
        },
    }
    try:
        svc = call("POST", "/services", key, payload)
    except SystemExit as e:
        print()
        print("  API 建服务失败，可以改用 Blueprint（仓库里已有 render.yaml）：")
        print("  Render 控制台 → New + → Blueprint → 选仓库 → Apply")
        raise

    sid = svc.get("service", {}).get("id") or svc.get("id")
    url = (svc.get("service", {}).get("serviceDetails", {}) or {}).get("url") or svc.get("service", {}).get("url", "")
    print("  ✓ 服务已创建：%s" % url or sid)
    print("  · 正在构建（约 2–4 分钟）…")

    ready = False
    for _ in range(70):
        time.sleep(6)
        try:
            d = call("GET", "/services/%s" % sid, key)
            s = d.get("service", d)
            url = (s.get("serviceDetails", {}) or {}).get("url") or url
            dep = s.get("lastDeploy") or {}
            st = dep.get("status") or s.get("suspended")
            print("    %s  %s" % (dep.get("status", "?"), url))
            if dep.get("status") == "live":
                ready = True
                break
        except SystemExit:
            break

    print()
    if ready:
        print("  ✓ 上线：%s" % url)
        print("  ✓ 扫码页：%s/join" % url)
    else:
        print("  · 构建还在跑，去控制台看进度：https://dashboard.render.com")
        print("  · 地址（构建完成后可用）：%s" % url)


if __name__ == "__main__":
    main()
