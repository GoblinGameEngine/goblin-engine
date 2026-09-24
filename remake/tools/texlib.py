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


IMPORT_PARAMS = {"compress/mode": "2", "mipmaps/generate": "true", "detect_3d/compress_to": "0"}


def import_settings(webp):
    """Library textures are only ever used in 3D materials built at runtime, so Godot can't detect
    that and would import them lossless without mipmaps (shimmer + VRAM).  Write/patch the .import
    params: VRAM-compressed, mipmapped, normal maps flagged."""
    path = webp + ".import"
    params = dict(IMPORT_PARAMS)
    params["compress/normal_map"] = "1" if webp.endswith("_normal.webp") else "0"
    if os.path.exists(path):
        lines = open(path).read().split("\n")
        seen = set()
        for i, ln in enumerate(lines):
            k = ln.split("=", 1)[0]
            if k in params:
                lines[i] = f"{k}={params[k]}"
                seen.add(k)
        if "[params]" not in lines:
            lines.append("[params]")
        idx = lines.index("[params]") + 1
        for k in params:
            if k not in seen:
                lines.insert(idx, f"{k}={params[k]}")
        new = "\n".join(lines)
    else:
        new = '[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n\n[params]\n\n' + \
              "\n".join(f"{k}={v}" for k, v in params.items()) + "\n"
    if not os.path.exists(path) or open(path).read() != new:
        open(path, "w").write(new)
        return 1
    return 0


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
            n += import_settings(out)
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im = Image.open(src)
        im = im.convert("L") if kind == "rough" else im.convert("RGBA" if im.mode in ("RGBA", "LA") else "RGB")
        im.save(out, "WEBP", quality=QUALITY.get(kind, 88), method=4)
        import_settings(out)
        n += 1
    return n


if __name__ == "__main__":
    sets = sys.argv[1:] or sorted(d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d)))
    for s_ in sets:
        print(s_, publish(s_), "written")
