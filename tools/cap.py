# -*- coding: utf-8 -*-
"""批量重截 21 屏（状态栏定格 08:52 / 86%）"""
import os, subprocess, uuid, tempfile, sys

ROOT = r"C:\Users\春生\Desktop\农创"
SRC = os.path.join(ROOT, "薪火仁义-交互原型.html")
OUT = os.path.join(ROOT, "shots")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SUFFIX = "&bare=1&clock=08:52&bat=0.86"

PLAIN = ["home", "course", "book", "schedule", "confirm", "success", "trip", "map",
         "poi", "stamps", "cert", "stay", "room", "exp", "mine", "vendor", "verify", "dashboard"]

EXTRA = [
    ("map2", "map", "tapVillage('红军村')"),
    ("map3", "map", "tapVillage('红岩村'); mapNav();"),
    ("search", "home", "openSearch(); quickSearch('红军')"),
]


def render(name, screen, act=None):
    src = open(SRC, encoding="utf-8").read()
    inject = '<style>*{transition:none!important}</style>'
    if act:
        inject += ("<script>window.addEventListener('load',function(){setTimeout(function(){try{"
                   + act + "}catch(e){}},200);});</script>")
    page = os.path.join(tempfile.gettempdir(), "cap_%s.html" % uuid.uuid4().hex[:6])
    open(page, "w", encoding="utf-8").write(src.replace("</body>", inject + "</body>"))
    url = "file:///" + page.replace("\\", "/") + "#screen=" + screen + SUFFIX
    prof = os.path.join(tempfile.gettempdir(), "ep" + uuid.uuid4().hex[:6])
    out = os.path.join(OUT, name + ".png")
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--user-data-dir=" + prof,
                    "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=390,844", "--virtual-time-budget=4000",
                    "--screenshot=" + out, url],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        os.remove(page)
    except OSError:
        pass
    print("shot", name, flush=True)


if __name__ == "__main__":
    for s in PLAIN:
        render(s, s)
    for name, screen, act in EXTRA:
        render(name, screen, act)
    print("ALL DONE", flush=True)
