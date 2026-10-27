# -*- coding: utf-8 -*-
"""
薪火仁义 · 联机演示服务
- 纯 Python 标准库，不依赖任何第三方服务
- 多台设备（手机 / 平板 / 电脑）打开同一地址，共享余位与订单，1.5 秒轮询同步
- 单机（双击 html）不受影响，本服务只是让原型多一种“多人同时在线”的演示方式

用法：
    python server.py            # 默认 8787 端口
    python server.py 9000       # 指定端口
"""
import json
import os
import socket
import sys
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, "薪火仁义-交互原型.html")
DATA = os.path.join(HERE, "online-state.json")
sys.path.insert(0, os.path.join(HERE, "pylibs"))

PORT = 8787
_env_port = os.environ.get("PORT")
if _env_port:
    try:
        PORT = int(_env_port)
    except ValueError:
        pass
elif len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

# 每天可售餐位（与原型里的 DATES 一致）
CAP = {17: 0, 18: 28, 19: 34, 20: 60, 21: 22, 22: 0, 23: 0}
WD = {17: "周日", 18: "周一", 19: "周二", 20: "周三", 21: "周四", 22: "周五", 23: "周六"}

LOCK = threading.Lock()
STATE = {"orders": [], "seq": {}}
SEEN = {}
ONLINE_WINDOW = 6.0


def load():
    if os.path.exists(DATA):
        try:
            with open(DATA, "r", encoding="utf-8") as f:
                d = json.load(f)
            STATE["orders"] = d.get("orders", [])
            STATE["seq"] = {int(k): v for k, v in d.get("seq", {}).items()}
        except Exception as e:
            print("! 读取 online-state.json 失败：", e)


def save():
    try:
        with open(DATA, "w", encoding="utf-8") as f:
            json.dump(STATE, f, ensure_ascii=False, indent=1)
    except Exception as e:
        print("! 保存失败：", e)


def taken(date):
    return sum(o["people"] for o in STATE["orders"] if o["date"] == date)


def free(date):
    return max(0, CAP.get(date, 0) - taken(date))


def snapshot():
    free_map = {str(d): free(d) for d in CAP}
    now = time.time()
    online = sum(1 for t in SEEN.values() if now - t < ONLINE_WINDOW)
    last = STATE["orders"][-1] if STATE["orders"] else None
    return {
        "dates": free_map,
        "cap": {str(d): CAP[d] for d in CAP},
        "wd": {str(d): WD[d] for d in WD},
        "orders": STATE["orders"][-20:],
        "count": len(STATE["orders"]),
        "online": online,
        "last": last,
        "ts": int(now * 1000),
    }


def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("223.5.5.5", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def qr_svg(text):
    try:
        import qrcode
        from qrcode.image.svg import SvgPathImage
        img = qrcode.make(text, image_factory=SvgPathImage, box_size=12, border=1)
        buf = __import__("io").BytesIO()
        img.save(buf)
        return buf.getvalue().decode("utf-8")
    except Exception:
        return ""


APPMODE_CSS = b"""<style id="appmode">
body.bare{overflow:hidden}
body.bare .stage{display:flex;justify-content:center;align-items:center;padding:0;min-height:100dvh}
@media (max-width:560px){
  body.bare .stage{align-items:flex-start}
  body.bare .phone{transform-origin:top center}
}
</style>"""

APPMODE_JS = b"""<script>
(function(){
  function fit(){
    var ph=document.querySelector('.phone'); if(!ph) return;
    var s=1;
    if(innerWidth<=560){ s=Math.min(1, innerWidth/390, innerHeight/844); }
    ph.style.transform = s<1 ? 'scale('+s+')' : '';
  }
  window.addEventListener('resize',fit);
  window.addEventListener('orientationchange',fit);
  if(document.readyState!=='loading'){fit();} else {document.addEventListener('DOMContentLoaded',fit);}
  setTimeout(fit,120); setTimeout(fit,600);
})();
</script>"""

JOIN_HTML = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>薪火仁义 · 联机演示</title>
<style>
body{{margin:0;background:#F5F0E6;color:#231E19;font:15px/1.7 "PingFang SC","Microsoft YaHei",sans-serif;
display:flex;min-height:100vh;align-items:center;justify-content:center;padding:24px}}
.card{{background:#fff;border-radius:22px;padding:34px 30px;max-width:520px;width:100%;
box-shadow:0 24px 60px -30px rgba(60,30,20,.45);text-align:center}}
h1{{font-family:Songti SC,SimSun,serif;font-size:24px;margin:0 0 6px;letter-spacing:2px}}
p.sub{{color:#8A7E6E;font-size:12.5px;margin:0 0 22px}}
.url{{font:600 15px/1.5 ui-monospace,Consolas,monospace;background:#F7E9E4;color:#A63A2E;
padding:12px 14px;border-radius:12px;word-break:break-all;margin:0 0 18px}}
.qr{{width:200px;height:200px;margin:0 auto 18px}}
.qr svg{{width:100%;height:100%;display:block}}
ol{{text-align:left;color:#6E6257;font-size:12.5px;padding-left:20px;margin:0}}
li{{margin:6px 0}}
.st{{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#3E5B45;margin-top:16px}}
.st b{{color:#3E5B45}}
</style></head><body><div class="card">
<h1>薪火仁义 · 联机演示</h1>
<p class="sub">多台设备打开同一地址，余位与订单实时同步</p>
<div class="url">{url}</div>
<div class="qr">{qr}</div>
<ol>
<li>{tip}</li>
<li>进「预约研学」→ 选日期与人数 → 查排程 → 支付订金</li>
<li>其他设备上的余位会在 1.5 秒内变化，右上角显示在线人数</li>
</ol>
<div class="st">● 当前在线 <b>{online}</b> 人 · 已收 <b>{count}</b> 单</div>
</div></body></html>"""


def public_base(handler):
    """按请求头推断对外可访问的地址：云上取 Host，本机取局域网 IP。"""
    host = (handler.headers.get("Host") or "").strip()
    proto = (handler.headers.get("X-Forwarded-Proto") or "http").strip()
    if host and "localhost" not in host and "127.0.0.1" not in host:
        return "%s://%s/" % (proto, host)
    return "http://%s:%d/" % (lan_ip(), PORT)


class Handler(BaseHTTPRequestHandler):
    server_version = "XinhuoRenyi/1.0"

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra:
            for k, v in extra.items():
                self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def do_GET(self):
        u = urlparse(self.path)
        path = u.path
        q = parse_qs(u.query)

        if path in ("/", "/index.html"):
            try:
                with open(PAGE, "rb") as f:
                    html = f.read()
                # 线上/联机打开时直接进「小程序模式」：去掉外侧流程导航，手机端铺满
                html = html.replace(b"<body>", b'<body class="bare">', 1)
                html = html.replace(b"</head>", APPMODE_CSS + b"</head>", 1)
                html = html.replace(b"</body>", APPMODE_JS + b"</body>", 1)
                self._send(200, html, "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, "找不到 薪火仁义-交互原型.html", "text/plain; charset=utf-8")
            return

        if path in ("/healthz", "/health"):
            self._send(200, "ok", "text/plain; charset=utf-8")
            return

        if path == "/api/state":
            cid = (q.get("c") or [""])[0]
            if cid:
                SEEN[cid] = time.time()
            with LOCK:
                data = snapshot()
            self._send(200, json.dumps(data, ensure_ascii=False))
            return

        if path == "/qr.svg":
            svg = qr_svg(public_base(self))
            if not svg:
                self._send(500, "二维码生成失败（缺 qrcode 库）", "text/plain; charset=utf-8")
                return
            self._send(200, svg, "image/svg+xml; charset=utf-8")
            return

        if path.rstrip("/") == "/tools/_probe.html" or path.startswith("/tools/") or path.startswith("/shots/"):
            rel = path.lstrip("/")
            full = os.path.realpath(os.path.join(ROOT, rel))
            if not full.startswith(os.path.realpath(ROOT)) or not os.path.isfile(full):
                self._send(404, json.dumps({"ok": False}), "application/json; charset=utf-8")
                return
            ext = os.path.splitext(full)[1].lower()
            ctype = {".html": "text/html; charset=utf-8", ".png": "image/png", ".jpg": "image/jpeg",
                     ".svg": "image/svg+xml", ".json": "application/json", ".js": "text/javascript"}.get(ext, "application/octet-stream")
            with open(full, "rb") as f:
                self._send(200, f.read(), ctype)
            return

        if path == "/join":
            base = public_base(self)
            custom = (q.get("u") or [""])[0]
            if custom.startswith("https://") or custom.startswith("http://"):
                base = custom
            with LOCK:
                s = snapshot()
            qr = qr_svg(base)
            self._send(200, JOIN_HTML.format(
                url=base, qr=qr or "", tip=(
                    "任何网络都能打开，扫上面的码即可（不用连同一个 Wi-Fi）"
                    if base.startswith("https://") or "onrender.com" in base
                    else "手机连同一个 Wi-Fi（或同一热点），扫上面的码 / 输入地址"),
                online=s["online"], count=s["count"]),
                "text/html; charset=utf-8")
            return

        self._send(404, json.dumps({"ok": False, "msg": "not found"}), "application/json; charset=utf-8")

    def do_POST(self):
        u = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            body = {}

        if u.path == "/api/order":
            try:
                date = int(body.get("date"))
                people = int(body.get("people"))
            except Exception:
                self._send(400, json.dumps({"ok": False, "msg": "参数不对"}, ensure_ascii=False))
                return
            if date not in CAP:
                self._send(400, json.dumps({"ok": False, "msg": "日期不在可约范围"}, ensure_ascii=False))
                return
            with LOCK:
                left = free(date)
                if left < people:
                    self._send(200, json.dumps({
                        "ok": False, "msg": "手慢了，这档只剩 %d 位" % left, "free": left
                    }, ensure_ascii=False))
                    return
                STATE["seq"][date] = STATE["seq"].get(date, 0) + 1
                oid = "XY-202605%02d-%03d" % (date, STATE["seq"][date])
                order = {
                    "id": oid, "date": date, "people": people,
                    "name": body.get("name") or "游客", "cid": body.get("cid") or "",
                    "ts": int(time.time() * 1000),
                }
                STATE["orders"].append(order)
                save()
                left2 = free(date)
                cnt = len(STATE["orders"])
            print("  + 新订单 %s  5月%d日 %d 人 → 余 %d 位（累计 %d 单）"
                  % (oid, date, people, left2, cnt))
            self._send(200, json.dumps({
                "ok": True, "id": oid, "free": left2, "count": cnt
            }, ensure_ascii=False))
            return

        if u.path == "/api/cancel":
            oid = body.get("id")
            with LOCK:
                before = len(STATE["orders"])
                STATE["orders"] = [o for o in STATE["orders"] if o["id"] != oid]
                save()
                removed = before - len(STATE["orders"])
            self._send(200, json.dumps({"ok": removed > 0, "removed": removed}, ensure_ascii=False))
            return

        if u.path == "/api/reset":
            with LOCK:
                STATE["orders"] = []
                STATE["seq"] = {}
                save()
            print("  · 已清空所有订单")
            self._send(200, json.dumps({"ok": True}, ensure_ascii=False))
            return

        self._send(404, json.dumps({"ok": False}, ensure_ascii=False))


def main():
    load()
    ip = lan_ip()
    url = "http://%s:%d/" % (ip, PORT)
    print()
    print("  薪火仁义 · 联机演示服务已启动")
    print("  本机打开：http://127.0.0.1:%d/" % PORT)
    print("  手机打开：%s   （需同一 Wi-Fi / 热点）" % url)
    print("  扫码页：  %sjoin" % url)
    print("  重置数据：curl -X POST http://127.0.0.1:%d/api/reset" % PORT)
    print("  按 Ctrl+C 停止")
    print()
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    httpd.daemon_threads = True
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  已停止")
        httpd.server_close()


if __name__ == "__main__":
    main()
