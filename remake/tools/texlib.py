#!/usr/bin/env python3
"""
texlib.py -- publish the generated textures (remake/textures/<set>/<name>_{albedo,normal,rough}.png,
from texgen.py) into the game's shared texture library, godot_project/remake/textures/<set>/*.webp.

Buildings' glbs carry no images: each material names a library texture in its .mats.json sidecar
and Godot loads it from here once, however many buildings use it.

  python texlib.py [SET ...]        (default: every set)
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "textures")
DST = os.path.join(HERE, "..", "..", "godot_project", "remake", "textures")
QUALITY = {"albedo": 88, "normal": 92, "rough": 80}


def publish(tset):
    n = 0
    for fn in sorted(os.listdir(os.path.join(SRC, tset))):
        if not fn.endswith(".png"):
            continue
        stem = fn[:-4]
        kind = stem.rsplit("_", 1)[-1]
        out = os.path.join(DST, tset, stem + ".webp")
        src = os.path.join(SRC, tset, fn)
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = Image.open(src)
        im = im.convert("L") if kind == "rough" else im.convert("RGBA" if im.mode in ("RGBA", "LA") else "RGB")
        im.save(out, "WEBP", quality=QUALITY.get(kind, 88), method=4)
        n += 1
    return n


if __name__ == "__main__":
    sets = sys.argv[1:] or sorted(d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d)))
    for s_ in sets:
        print(s_, publish(s_), "written")
