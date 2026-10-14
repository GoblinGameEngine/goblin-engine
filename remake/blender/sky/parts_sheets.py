"""parts_sheets.py -- compose parts_build.py's renders into research/sky_islands/img/ (PIL; ssc-assets venv).

  ~/.venvs/ssc-assets/bin/python remake/blender/sky/parts_sheets.py <render dir>
"""
import glob
import os
import sys

from PIL import Image, ImageDraw

SRC = sys.argv[1]
DST = os.path.join(os.path.dirname(__file__), "..", "..", "..", "research", "sky_islands", "img")
os.makedirs(DST, exist_ok=True)


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 * len(text) + 12, 20), fill=(30, 30, 30))
    d.text((6, 4), text, fill=(240, 240, 240))
    return im


styles = sorted({os.path.basename(p)[7:-6] for p in glob.glob(os.path.join(SRC, "bridge_*_0.png"))})
rows = []
for st in styles:
    ims = [label(Image.open(os.path.join(SRC, "bridge_%s_%s.png" % (st, t))).convert("RGB"), "%s  %s" % (st, n))
           for t, n in (("0", "stowed"), ("5", "half"), ("1", "deployed"))]
    row = Image.new("RGB", (sum(i.width for i in ims), ims[0].height))
    x = 0
    for i in ims:
        row.paste(i, (x, 0))
        x += i.width
    row.save(os.path.join(DST, "parts_bridge_%s.png" % st))
    rows.append(row.resize((row.width // 2, row.height // 2)))
sheet = Image.new("RGB", (rows[0].width * 2, rows[0].height * ((len(rows) + 1) // 2)), (255, 255, 255))
for k, r in enumerate(rows):
    sheet.paste(r, ((k % 2) * r.width, (k // 2) * r.height))
sheet.save(os.path.join(DST, "parts_bridges.png"))
parts = sorted(glob.glob(os.path.join(SRC, "part_*.png")))
ims = [label(Image.open(p).convert("RGB"), os.path.basename(p)[5:-4]) for p in parts]
cols = 4
w, h = ims[0].size
sheet = Image.new("RGB", (w * cols, h * ((len(ims) + cols - 1) // cols)), (255, 255, 255))
for k, im in enumerate(ims):
    sheet.paste(im, ((k % cols) * w, (k // cols) * h))
sheet.save(os.path.join(DST, "parts_props.png"))
print("wrote", DST)
