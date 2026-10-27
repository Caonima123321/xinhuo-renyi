# -*- coding: utf-8 -*-
"""重建图片与 CSS 变量块（幂等）：裁切、去水印边、压缩、写回 --ph-* 变量"""
import base64, io, os, re
from PIL import Image

ROOT = r"C:\Users\春生\Desktop\农创"
OUT = os.path.join(ROOT, "assets", "img")
os.makedirs(OUT, exist_ok=True)

# name: (source, aspect, out_width, trim_bottom_ratio)
PLAN = {
    "hero":        ("cand8/path/06.jpg",  390 / 262, 1000, 0.07),
    "v-hongjun":   ("cand5/hall/07.jpg",  148 / 92, 520, 0.10),
    "v-hongyan":   ("cand5/hall/05.jpg",  148 / 92, 520, 0.10),
    "v-helin":     ("cand6/rice2/05.jpg", 148 / 92, 520, 0.0),
    "v-laochang":  ("cand5/hall/03.jpg",  148 / 92, 520, 0.07),
    "c-oneyear":   ("cand5/hero/00.jpg",  1.0, 380, 0.0),
    "c-twoday":    ("cand5/stay/05.jpg",  1.0, 380, 0.0),
    "g-rice":      ("cand6/rice2/09.jpg", 1.6, 420, 0.0),
    "g-rose":      ("cand6/lotus2/07.jpg", 1.6, 420, 0.12),
    "g-salt":      ("cand6/rub2/04.jpg",  1.6, 420, 0.0),
    "cover-course": ("cand5/hero/02.jpg", 390 / 196, 1000, 0.0),
    "cover-poi":   ("cand8/path/00.jpg",  390 / 214, 1000, 0.0),
    "stay-1":      ("cand5/stay/00.jpg",  354 / 132, 900, 0.0),
    "stay-2":      ("cand6/lotus2/00.jpg", 354 / 118, 900, 0.0),
    "cover-room":  ("cand5/stay/09.jpg",  390 / 172, 900, 0.0),
    "exp-tofu":    ("cand5/tofu/05.jpg",  1.0, 320, 0.12),
    "exp-folk":    ("cand7/folk2/00.jpg", 1.0, 320, 0.0),
    "exp-rub":     ("cand6/rub2/03.jpg",  1.0, 320, 0.0),
    "exp-fish":    ("cand6/fish2/00.jpg", 1.0, 320, 0.0),
}


def crop_to(im, aspect):
    w, h = im.size
    if w / h > aspect:
        nw = int(h * aspect)
        return im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    nh = int(w / aspect)
    top = max(0, int((h - nh) * 0.35))
    return im.crop((0, top, w, top + nh))


uris, total = {}, 0
for name, (src, aspect, outw, trim) in PLAN.items():
    im = Image.open(os.path.join(ROOT, "assets", src)).convert("RGB")
    if trim > 0:
        w, h = im.size
        im = im.crop((0, 0, w, int(h * (1 - trim))))
    im = crop_to(im, aspect)
    im = im.resize((outw, max(1, int(outw / aspect))), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=74, optimize=True, progressive=True)
    data = buf.getvalue()
    open(os.path.join(OUT, name + ".jpg"), "wb").write(data)
    total += len(data)
    uris[name] = "data:image/jpeg;base64," + base64.b64encode(data).decode()

print("images rebuilt: %d, %.2f MB" % (len(uris), total / 1024 / 1024))

html_path = os.path.join(ROOT, "薪火仁义-交互原型.html")
html = open(html_path, encoding="utf-8").read()
css = ('<style id="phvars">:root{\n'
       + "\n".join("--ph-%s:url(%s);" % (k, v) for k, v in uris.items())
       + "\n}</style>")
if re.search(r'<style id="phvars">.*?</style>', html, re.S):
    html = re.sub(r'<style id="phvars">.*?</style>', css, html, flags=re.S)
else:
    html = html.replace("</head>", css + "</head>", 1)
open(html_path, "w", encoding="utf-8").write(html)
print("css updated, html %.2f MB" % (len(html.encode()) / 1024 / 1024))

