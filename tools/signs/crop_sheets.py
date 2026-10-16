#!/usr/bin/env python3
"""Cut the Grok sign sheets (research/flea_markets/08_signage_briefs.md) into game sign atlases.

    ~/.venvs/ssc-assets/bin/python tools/signs/crop_sheets.py            # all sets
    ~/.venvs/ssc-assets/bin/python tools/signs/crop_sheets.py --debug    # also box overlays in /tmp/signs_debug
    ~/.venvs/ssc-assets/bin/python tools/signs/crop_sheets.py --full     # RGBA atlases instead of 256-colour

In:  reference/grok/signs/<sheet>/<sheet>_img1.jpg (gitignored; <sheet>_fix.jpg wins if present)
     tools/signs/sheet_manifest.py (what is in every cell)
Out: godot_project/remake/signs/<atlas>.png        RGBA, 256 px cells, transparent surround (road_signs.png style)
     godot_project/remake/signs/<atlas>_emit.png   L, 128 px cells: night/emissive mask (bright + saturated parts)
     godot_project/remake/signs/signs.json         cell index: id -> atlas, i, j, region, uv, kind, market/family/biz ...
     research/flea_markets/img/signs_<atlas>.jpg    contact sheet (day on grey | night preview), for review

Per cell: split on the sheet's grid (or the hand boxes in BOXES for sheets Grok laid out freely), key out the
background by flood fill from the cell border (magenta-hued pixels, plus pixels close to the cell's own border
colours, so per-cell tiles and soft drop shadows go too), keep the main blobs, despill magenta at the edges, trim,
and fit into a 256 px cell with a small pad.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from sheet_manifest import SHEETS  # noqa: E402

SRC = os.path.join(ROOT, "reference", "grok", "signs")
OUT = os.path.join(ROOT, "godot_project", "remake", "signs")
IMG = os.path.join(ROOT, "research", "flea_markets", "img")
FONT = os.path.join(ROOT, "godot_project", "ui", "pda", "DejaVuSans-Bold.ttf")
CELL = 256
PAD = 6
EMIT_DIV = 2          # the emissive mask is stored at half resolution
COLS = 8

# Atlases: name -> sheets packed into it (in order).
ATLASES = {
    "markets": ["A1", "A2", "A3", "A4", "A5"],
    "sky_a": ["B1", "B2", "B3", "B4"],
    "sky_b": ["B5", "B6", "B7", "B8", "B9"],
    "biz": ["C1", "C2", "C3", "C4"],
    "mascots": ["G1", "G2"],
    "ads": ["G3", "G4"],
    "small": ["G5", "G10"],
    "stalls": ["G6", "G9"],
    "goods": ["G7", "G8"],
}

# Sheets Grok did not lay out on the asked grid: hand boxes (x0, y0, x1, y1 on the 1024 px sheet) per cell index of
# the manifest (0-based), plus extra cells (id, box, info) that Grok added and are worth keeping.
BOXES = {
    "G9": {   # the light strings run across two or three cells
        0: (40, 10, 215, 248), 1: (295, 10, 480, 252), 2: (585, 4, 705, 252), 3: (835, 4, 965, 252),
        4: (0, 278, 256, 348), 5: (262, 278, 782, 362), 6: (0, 382, 782, 474), 7: (790, 252, 1012, 506),
        8: (62, 500, 198, 762), 9: (272, 500, 502, 728), 10: (528, 502, 762, 748), 11: (808, 498, 998, 748),
        12: (0, 856, 264, 934), 13: (346, 766, 428, 1024), 14: (546, 766, 744, 1024), 15: (822, 772, 988, 1024),
    },
    "B1": {   # Grok grouped by kind into columns, plus a duplicate star and a wood frame
        0: (22, 20, 318, 198), 1: (360, 16, 525, 352), 2: (575, 20, 750, 195),
        3: (22, 222, 318, 396), 4: (372, 553, 512, 800), 5: (565, 205, 760, 405),
        6: (22, 420, 318, 598), 7: (812, 200, 966, 400), 8: (808, 410, 976, 636),
        9: (22, 620, 318, 798), 10: (372, 362, 512, 551), 11: (594, 590, 730, 806),
        12: (22, 818, 318, 1002), 13: (320, 800, 525, 1004), 14: (560, 812, 760, 1004),
        15: (785, 662, 1002, 1004),
    },
    "B2": {   # a 5 x 4 grid of coloured tiles (one row per culture), two empty tiles and two extras
        0: (12, 12, 356, 202), 1: (366, 12, 538, 202), 2: (746, 12, 1012, 202),
        3: (12, 212, 356, 405), 4: (548, 212, 738, 405), 5: (746, 212, 1012, 405),
        6: (12, 415, 356, 607), 7: (548, 415, 738, 607), 8: (746, 415, 1012, 607),
        9: (12, 617, 356, 810), 10: (366, 617, 538, 810), 11: (548, 617, 738, 810),
        12: (12, 820, 356, 1012), 13: (366, 820, 538, 1012), 14: (548, 820, 738, 1012),
        15: (746, 820, 1012, 1012),
    },
}
# Sheets where Grok drew a flat coloured tile behind (some) signs: key the tile colour too.
TILED = {"B2", "C1", "C2", "C4", "G2", "G6", "G10"}
EXTRAS = {
    "B1": [("sky_maghrebi_medina_emblem2", (805, 20, 980, 195),
            {"family": "maghrebi_medina", "slot": "c", "desc": "second eight-point star, violet neon"}),
           ("sky_mzab_ghadames_frame", (570, 418, 755, 590),
            {"family": "mzab_ghadames", "slot": "a", "desc": "palm-rib cross-lashed frame"})],
    "B2": [("sky_hejazi_roshan_blade2", (548, 12, 738, 202),
            {"family": "hejazi_roshan", "slot": "b", "desc": "plain vertical lightbox with turquoise LED"}),
           ("sky_persian_desert_emblem2", (746, 617, 1012, 810),
            {"family": "persian_desert", "slot": "c", "desc": "glowing tile medallion"})],
}


# ------------------------------------------------------------------------------------------------ keying
def _rgb_to_hsv(a):
    a = a.astype(np.float32) / 255.0
    mx, mn = a.max(-1), a.min(-1)
    v = mx
    s = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return s, v


def _magenta_like(a):
    r, g, b = (a[..., k].astype(np.int16) for k in range(3))
    m = np.minimum(r, b)
    # hue near magenta: red and blue both well above green, and not too far apart (pink-magenta to purple-magenta)
    return (((m - g > 32) & (r > 70) & (r * 2 > g * 3)) | ((m - g > 18) & (r > 55) & (b * 10 > g * 18))) \
        & (np.abs(r - b) < 120)


def _border_colours(a):
    """Dominant colours on the cell border that are not magenta (per-cell tiles Grok sometimes draws)."""
    h, w, _ = a.shape
    ring = np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3), a[:, :4].reshape(-1, 3),
                           a[:, -4:].reshape(-1, 3)])
    ring = ring[~_magenta_like(ring[None])[0]]
    if len(ring) < 0.15 * (2 * (h + w) * 4):
        return []
    q = (ring // 24).astype(np.int32)
    keys, inv, counts = np.unique(q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2], return_inverse=True, return_counts=True)
    out = []
    for k in np.argsort(-counts)[:3]:
        if counts[k] > 0.08 * len(ring):
            out.append(ring[inv == k].mean(0))
    return out


def _tile_pass(a_s, bg, tol):
    """Grok sometimes puts each sign on a flat coloured tile. Find the dominant colour just inside the current
    background edge and flood it (connected to the background) with a tight tolerance, so sign outlines stop it."""
    edge = ndimage.binary_dilation(bg, iterations=8) & ~ndimage.binary_dilation(bg, iterations=4)
    if edge.sum() < 50:
        return bg
    px = a_s[edge]
    q = (px // 28).astype(np.int32)
    keys, inv, counts = np.unique(q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2], return_inverse=True, return_counts=True)
    k = np.argmax(counts)
    if counts[k] < 0.22 * len(px):
        return bg
    c = px[inv == k].mean(0)
    if _magenta_like(c[None, None].astype(np.uint8))[0, 0]:
        return bg
    near = np.sqrt(((a_s - c) ** 2).sum(-1)) < tol
    seam = ndimage.binary_dilation(bg, iterations=5)      # the anti-aliased band between magenta and tile
    lab, n = ndimage.label(near | seam)
    hit = np.unique(lab[bg])
    grown = np.isin(lab, hit[hit > 0]) & (near | seam)
    # a "tile" must be a large flat area; otherwise this colour is the sign itself touching the background
    new = grown & ~bg
    if new.sum() < 0.12 * bg.size:
        return bg
    ys, xs = np.nonzero(new)
    h, w = bg.shape
    if (ys.max() - ys.min()) < 0.78 * h or (xs.max() - xs.min()) < 0.78 * w:
        return bg      # not a cell-sized tile: it is a board touching the background
    return grown


def key_cell(a, tol=34, tiled=False):
    """a: HxWx3 uint8 -> alpha HxW uint8 (255 = sign)."""
    a_s = ndimage.median_filter(a, size=(3, 3, 1)).astype(np.float32)
    cand = _magenta_like(a)
    af = a.astype(np.float32)
    lab, n = ndimage.label(cand)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    if bg.sum() < 0.02 * bg.size:      # no magenta round this cell: start from the border ring itself
        bg = np.zeros_like(bg)
        bg[:3], bg[-3:], bg[:, :3], bg[:, -3:] = True, True, True, True
    for _ in range(2 if tiled else 0):
        bg = _tile_pass(a_s, bg, 22)
    # enclosed pockets of background (inside rope loops, bunting, bracket scrolls): same colour as the cell's bg
    if bg.any():
        ref = np.median(af[bg & _magenta_like(a)], 0) if (bg & _magenta_like(a)).any() else np.median(af[bg], 0)
        close = np.sqrt(((af - ref) ** 2).sum(-1)) < 38
        plab, pn = ndimage.label(close & ~bg)
        if pn:
            psz = ndimage.sum(np.ones_like(close), plab, range(1, pn + 1))
            pocket = np.isin(plab, [i + 1 for i, s in enumerate(psz) if s >= 25])
            bg |= pocket
    fg = ~bg
    fg = ndimage.binary_opening(fg, iterations=1)
    lab, n = ndimage.label(fg)
    if n == 0:
        return np.zeros(fg.shape, np.uint8)
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    touch = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    big = sizes.max()
    # small parts are kept (letters, bulbs) unless they touch the cell edge: those are slivers of a neighbour
    keep = [i + 1 for i, s in enumerate(sizes)
            if s >= max(80, 0.012 * big) and not ((i + 1) in touch and s < 0.35 * big)]
    fg = np.isin(lab, keep)
    fg = ndimage.binary_erosion(fg, iterations=1)
    alpha = Image.fromarray((fg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    return np.array(alpha)


def despill(a, alpha):
    """Pull the magenta fringe out of edge pixels (within 3 px of the background)."""
    out = a.astype(np.int16).copy()
    near = ndimage.binary_dilation(alpha < 128, iterations=3) & (alpha > 0)
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    m = np.minimum(r, b)
    spill = np.clip(m - g, 0, None) * near
    out[..., 0] = r - spill * 0.7
    out[..., 2] = b - spill * 0.7
    return np.clip(out, 0, 255).astype(np.uint8)


def emissive(rgba):
    """Night mask: neon, LEDs, bulbs: bright, saturated (or near-white hot cores) and small or brighter than their
    surroundings. Large flat painted areas (pastel boards) stay dark."""
    a = rgba[..., :3]
    s, v = _rgb_to_hsv(a)
    hp = v - ndimage.uniform_filter(v, 9)
    lit = ((v > 0.84) & (s > 0.60)) | ((v > 0.97) & (s > 0.12) & (hp > 0.04))
    lit &= rgba[..., 3] > 128
    lit = ndimage.binary_opening(lit, iterations=1)
    lab, n = ndimage.label(lit)
    if n:
        sz = ndimage.sum(lit, lab, range(1, n + 1))
        mhp = ndimage.mean(hp, lab, range(1, n + 1))
        keep = [i + 1 for i in range(n) if sz[i] <= 1800 or mhp[i] > 0.03]
        lit = np.isin(lab, keep)
    m = Image.fromarray((lit * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    return np.array(m)


def cut(sheet_rgb, box, tiled=False):
    x0, y0, x1, y1 = box
    a = sheet_rgb[y0:y1, x0:x1]
    alpha = key_cell(a, tiled=tiled)
    if alpha.max() == 0:
        return None, None
    a = despill(a, alpha)
    ys, xs = np.nonzero(alpha > 8)
    ty0, ty1, tx0, tx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.dstack([a, alpha])[ty0:ty1, tx0:tx1]
    im = Image.fromarray(rgba, "RGBA")
    w, h = im.size
    k = (CELL - 2 * PAD) / max(w, h)
    nw, nh = max(1, round(w * k)), max(1, round(h * k))
    # premultiply-safe resize: resize colour on alpha-weighted values
    im = im.resize((nw, nh), Image.LANCZOS)
    cell = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    ox, oy = (CELL - nw) // 2, (CELL - nh) // 2
    cell.paste(im, (ox, oy))
    arr = np.array(cell)
    arr[arr[..., 3] == 0, :3] = 0
    return arr, (int(ox), int(oy), int(nw), int(nh))


def sheet_image(name):
    for fn in ("%s_fix.jpg" % name, "%s_img1.jpg" % name):
        p = os.path.join(SRC, name, fn)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB")
            if im.size != (1024, 1024):
                im = im.resize((1024, 1024), Image.LANCZOS)
            return np.array(im), p
    return None, None


def sheet_cells(name):
    """[(cell dict, box)] for a sheet, manifest order, then extras."""
    sh = SHEETS[name]
    rows, cols = sh.get("rows", sh["grid"]), sh.get("cols", sh["grid"])
    sx, sy = 1024 / cols, 1024 / rows
    out = []
    for k, c in enumerate(sh["cells"]):
        if name in BOXES:
            box = BOXES[name][k]
        else:
            r, q = divmod(k, cols)
            box = (round(q * sx), round(r * sy), round((q + 1) * sx), round((r + 1) * sy))
        out.append((dict(c, sheet=name, sheet_cell=k + 1), box))
    for cid, box, info in EXTRAS.get(name, []):
        out.append((dict(info, id=cid, kind="island", sheet=name, sheet_cell=None, extra=True), box))
    return out


# ------------------------------------------------------------------------------------------------ packing
def label_font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def build(debug=False):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    index = {"cell_px": CELL, "emit_px": CELL // EMIT_DIV, "cols": COLS, "atlases": {}, "cells": {}}
    report = []
    for atlas, sheets in ATLASES.items():
        tiles = []
        for name in sheets:
            rgb, path = sheet_image(name)
            if rgb is None:
                report.append("%s: missing sheet" % name)
                continue
            if debug:
                dbg = Image.fromarray(rgb.copy())
                d = ImageDraw.Draw(dbg)
            for c, box in sheet_cells(name):
                arr, content = cut(rgb, box, tiled=name in TILED)
                if debug:
                    d.rectangle(box, outline=(0, 255, 0), width=3)
                    d.text((box[0] + 4, box[1] + 2), c["id"][-18:], fill=(255, 255, 0))
                if arr is None:
                    report.append("%s: %s empty after keying" % (name, c["id"]))
                    continue
                tiles.append((c, arr, content))
            if debug:
                os.makedirs("/tmp/signs_debug", exist_ok=True)
                dbg.save("/tmp/signs_debug/%s.jpg" % name, quality=80)
        n = len(tiles)
        rows = (n + COLS - 1) // COLS
        W, H = COLS * CELL, rows * CELL
        atlas_im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        emit_im = Image.new("L", (W // EMIT_DIV, H // EMIT_DIV), 0)
        day = Image.new("RGB", (W, H), (96, 98, 104))
        night = Image.new("RGB", (W, H), (14, 16, 26))
        for k, (c, arr, content) in enumerate(tiles):
            i, j = k % COLS, k // COLS
            x, y = i * CELL, j * CELL
            tile = Image.fromarray(arr, "RGBA")
            atlas_im.paste(tile, (x, y))
            em = emissive(arr)
            emit_im.paste(Image.fromarray(em).resize((CELL // EMIT_DIV,) * 2, Image.BILINEAR),
                          (x // EMIT_DIV, y // EMIT_DIV))
            day.paste(tile, (x, y), tile)
            f = arr[..., :3].astype(np.float32)
            lum = em[..., None] / 255.0
            nt = np.clip(f * 0.18 + f * lum * 1.35, 0, 255).astype(np.uint8)
            nt_im = Image.fromarray(nt)
            night.paste(nt_im, (x, y), tile)
            info = {k2: v for k2, v in c.items() if k2 not in ("id",)}
            info.update({"atlas": atlas, "i": i, "j": j,
                         "region": [x, y, CELL, CELL],
                         "uv": [round(x / W, 6), round(y / H, 6), round(CELL / W, 6), round(CELL / H, 6)],
                         "content": list(content),
                         "emissive": round(float((em > 128).mean()), 3)})
            if c["id"] in index["cells"]:
                raise SystemExit("duplicate cell id %s" % c["id"])
            index["cells"][c["id"]] = info
        atlas_path = os.path.join(OUT, "%s.png" % atlas)
        emit_path = os.path.join(OUT, "%s_emit.png" % atlas)
        if FULL:
            atlas_im.save(atlas_path, optimize=True)
        else:   # 256-colour palette with alpha: ~6x smaller; the game imports it as RGBA8 / VRAM-compressed anyway
            atlas_im.quantize(256, method=Image.Quantize.FASTOCTREE,
                              dither=Image.Dither.FLOYDSTEINBERG).save(atlas_path, optimize=True)
        emit_im.save(emit_path, optimize=True)
        index["atlases"][atlas] = {"png": "res://remake/signs/%s.png" % atlas,
                                   "emit": "res://remake/signs/%s_emit.png" % atlas,
                                   "size": [W, H], "cells": n, "sheets": sheets}
        # contact sheet: day | night, with ids
        lab = label_font(13)
        cs = Image.new("RGB", (W * 2 + 16, H), (40, 40, 44))
        cs.paste(day, (0, 0))
        cs.paste(night, (W + 16, 0))
        dr = ImageDraw.Draw(cs)
        for k, (c, _a, _c) in enumerate(tiles):
            x, y = (k % COLS) * CELL, (k // COLS) * CELL
            t = c["id"].replace("sky_", "").replace("biz_", "")
            dr.rectangle((x, y + CELL - 18, x + CELL - 1, y + CELL - 1), fill=(0, 0, 0))
            dr.text((x + 4, y + CELL - 17), t[:30], fill=(255, 255, 255), font=lab)
        cs = cs.resize((cs.width // 2, cs.height // 2), Image.LANCZOS)
        cs_path = os.path.join(IMG, "signs_%s.jpg" % atlas)
        cs.save(cs_path, quality=82, optimize=True)
        report.append("%s: %d cells, %dx%d, %s %.0f KB, emit %.0f KB, contact %s" % (
            atlas, n, W, H, os.path.relpath(atlas_path, ROOT), os.path.getsize(atlas_path) / 1024,
            os.path.getsize(emit_path) / 1024, os.path.relpath(cs_path, ROOT)))
    sp = os.path.join(OUT, "signs.json")
    keep = json.load(open(sp)) if os.path.exists(sp) else {}
    keep.update(index)                    # (other tools' sections -- flags, banners, city -- are kept)
    with open(sp, "w") as f:
        json.dump(keep, f, indent=1, ensure_ascii=False)
    print("\n".join(report))
    print("cells: %d -> %s" % (len(index["cells"]), os.path.relpath(os.path.join(OUT, "signs.json"), ROOT)))


FULL = "--full" in sys.argv          # keep full RGBA atlases (about 6x bigger)

if __name__ == "__main__":
    build(debug="--debug" in sys.argv)
