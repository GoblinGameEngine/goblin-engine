#!/usr/bin/env python3
"""sheets.py -- the kit's contact sheets: every preview sheet rendered in Blender (full by day, MID by day, and the lit
sheets by night too), each composed into research/flea_markets/img/kit_<sheet>[_mid].png, palette-quantised to <= 400 KB.

  ~/.venvs/ssc-assets/bin/python remake/blender/markets/build.py --previews
  ~/.venvs/ssc-assets/bin/python remake/blender/markets/sheets.py [sheet ...]
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PREV = os.path.join(ROOT, "reference", "tmp", "markets_kit")
IMG = os.path.join(ROOT, "research", "flea_markets", "img")
NIGHT = {"signs_a", "signs_b", "tents", "lights", "ropeway", "furniture", "warren_moor"}
LIMIT = 400 * 1024
TITLES = {"local": "local market: sheds, pitches, canopies, displays, lot poles", "lot": "lot paint, kerbs, island ends, festoon pole",
          "goods": "goods clusters (goods atlas cards)", "signs_a": "entrance arches + landmark sign mounts 1-11",
          "signs_b": "landmark sign mounts 12-22, island fair boards", "tents": "islanders' tents (dressed)",
          "furniture": "tent furniture", "lights": "festoons and Skein lanterns", "ropeway": "gondolas, drop cage, ropes, anchors, masts, ground station",
          "world": "MARKETS-WORLD: food trucks, office, gate house, restrooms, bike rack, the floating pier",
          "warren_moor": "island side (warren kit), seen from the rim: line house, top stations, davit, signal mast"}


def blender(out, glb, night=False, w=1500, h=950, az=-24, el=26):
    cmd = ["flatpak", "run", "org.blender.Blender", "-b", "--factory-startup", "--python", os.path.join(HERE, "render.py"), "--",
           out, glb, "night" if night else "day", str(w), str(h), str(az), str(el)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(out):
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("render failed: " + out)


def save_small(im, path):
    """a palette PNG under LIMIT: fewer colours, then a smaller image, until it fits"""
    for scale in (1.0, 0.9, 0.8, 0.7, 0.6):
        src = im if scale == 1.0 else im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        for colours in (256, 192, 128, 96, 64):
            q = src.convert("RGB").quantize(colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            q.save(path, optimize=True)
            if os.path.getsize(path) <= LIMIT:
                return os.path.getsize(path), q.size, colours
    return os.path.getsize(path), q.size, colours


def label(im, text):
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype(os.path.join(ROOT, "reference", "fonts", "Oswald.ttf"), 26)
    except OSError:
        f = ImageFont.load_default()
    d.rectangle((0, 0, im.width, 38), fill=(20, 22, 28))
    d.text((12, 4), text, font=f, fill=(240, 240, 240))
    return im


def main(only=None):
    os.makedirs(IMG, exist_ok=True)
    def glb_of(k, tag):
        if k == "warren_moor":
            return ";".join(os.path.join(PREV, f"sheet_warren_moor_{tag}_{i}.glb") for i in (0, 1))
        return os.path.join(PREV, f"sheet_{k}_{tag}.glb")
    keys = [k for k in TITLES if os.path.exists(glb_of(k, "full").split(";")[0])]
    for k in keys:
        if only and k not in only:
            continue
        for tag in ("full", "mid"):
            glb = glb_of(k, tag)
            day = os.path.join(PREV, f"r_{k}_{tag}_day.png")
            az = 156 if k == "warren_moor" else -24                     # (the moorings from the rim side, -z)
            blender(day, glb, az=az)
            shots = [(day, "", "full" if tag == "full" else "MID level")]
            if k in NIGHT and tag == "full":
                nt = os.path.join(PREV, f"r_{k}_{tag}_night.png")
                blender(nt, glb, night=True, az=az)
                shots.append((nt, "_night", "full, at night"))
            for src, suffix, what in shots:
                sheet = label(Image.open(src).convert("RGB"), "%s  -- %s" % (TITLES[k], what))
                out = os.path.join(IMG, f"kit_{k}{'' if tag == 'full' else '_mid'}{suffix}.png")
                size, dim, cols = save_small(sheet, out)
                print(out, size // 1024, "KB", dim, cols, "colours")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
