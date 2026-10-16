#!/usr/bin/env python3
"""render.py -- offline views of an assembled island (no game, no GPU): one Embree ray per pixel against the render
triangles + the deck, coloured by the kit palette (pieces.json palettes[civ][variant][slot]), lit by a sun with a
shadow ray, sky behind.  The first piece of the phase-2 geo toolkit's `render`.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/render.py SKY-022 --persp EYE_X,EYE_Y,EYE_Z TX,TY,TZ [--fov 55]
  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/render.py SKY-022 --top            (orthographic, from above)
      [--size 960x600] [--out file.png] [--label "text"] [--problems]   (--problems: audit hotspots marked)

Frame: the island's (+X south, +Y up, +Z west).  ~1-3 s for a 960 x 600 view."""
import json
import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as A  # noqa: E402
import common as C  # noqa: E402
import rays as RY  # noqa: E402

SUN = np.array([0.45, 0.8, 0.3])
SUN = SUN / np.linalg.norm(SUN)
SKY_TOP, SKY_LOW = np.array([0.42, 0.62, 0.86]), np.array([0.80, 0.86, 0.92])
DECK = np.array([0.74, 0.70, 0.58])
WATER = np.array([0.24, 0.46, 0.52])


def _hex(h):
    h = h.lstrip("#")
    return np.array([int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)])


def colours(g):
    """per render triangle: its palette colour (slot x the placement's palette variant)"""
    pals = A.kit().pj["palettes"].get(g.W["civ"]) or [{}]
    slots = A.SLOTS
    pv = (g.recs["pe"] & 15).astype(int)[g.rsrc] % len(pals)
    table = np.zeros((len(pals), len(slots), 3))
    for v, pal in enumerate(pals):
        for s, name in enumerate(slots):
            table[v, s] = _hex(pal.get(name, pal.get("wall", "#bbbbbb")))
    return table[pv, g.rslot.astype(int)]


def render(g, eye, target=None, size=(960, 600), fov=55.0, ortho=None, marks=None):
    deck = g.ctri[g.csrc == A.DECK].astype(np.float32)
    tris = np.concatenate([g.rtri, deck])
    R = RY.Rays(tris)
    col = np.concatenate([colours(g), np.tile(DECK, (len(deck), 1))])
    W, H = size
    if ortho is not None:                              # (x0, x1, z0, z1): straight down
        x0, x1, z0, z1 = ortho
        u = (np.arange(W) + 0.5) / W
        v = (np.arange(H) + 0.5) / H
        Z, X = np.meshgrid(z0 + (z1 - z0) * u, x0 + (x1 - x0) * v)
        o = np.stack([X.ravel(), np.full(X.size, 200.0), Z.ravel()], 1)
        d = np.tile([0.0, -1.0, 0.0], (len(o), 1))
    else:
        eye = np.asarray(eye, float)
        f = np.asarray(target, float) - eye
        f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0])
        r /= np.linalg.norm(r)
        up = np.cross(r, f)
        t = np.tan(np.radians(fov) / 2)
        px = (np.arange(W) + 0.5) / W * 2 - 1
        py = 1 - (np.arange(H) + 0.5) / H * 2
        PX, PY = np.meshgrid(px * t, py * t * H / W)
        d = f[None] + PX.ravel()[:, None] * r[None] + PY.ravel()[:, None] * up[None]
        d /= np.linalg.norm(d, axis=1)[:, None]
        o = np.tile(eye, (len(d), 1))
    tt, prim, n = R.cast(o, d, 2000.0)
    hit = np.isfinite(tt)
    img = np.zeros((len(o), 3))
    sky = SKY_LOW[None] + (SKY_TOP - SKY_LOW)[None] * np.clip(d[:, 1:2] * 2.5, 0, 1)
    img[~hit] = sky[~hit]
    if hit.any():
        hi = np.nonzero(hit)[0]
        p = o[hi] + d[hi] * tt[hi, None]
        nn = n[hi]
        lam = np.clip(nn @ SUN, 0, 1)
        so, _, _ = R.cast(p + nn * 0.01, np.tile(SUN, (len(hi), 1)), 500.0)
        lit = ~np.isfinite(so)
        shade = 0.38 + 0.62 * lam * lit
        c = col[prim[hi]] * shade[:, None]
        # (ponds: the island draws its water apart -- the deck under a pond outline shows as water here)
        isdeck = prim[hi] >= len(g.rtri)
        if isdeck.any() and g.isl.get("water"):
            import shapely
            from shapely.geometry import Polygon
            wet = np.zeros(int(isdeck.sum()), bool)
            pp = p[isdeck]
            for w in g.isl["water"]:
                wet |= shapely.contains_xy(Polygon([(q[0], q[1]) for q in w["outline"]]), pp[:, 0], pp[:, 2])
            cc = c[isdeck]
            cc[wet] = WATER * (0.75 + 0.25 * lam[isdeck][wet, None])
            c[isdeck] = cc
        if ortho is None:
            fog = np.clip((tt[hi] - 60) / 400, 0, 0.6)[:, None]
            c = c * (1 - fog) + SKY_LOW[None] * fog
        img[hi] = c
    im = Image.fromarray((np.clip(img, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8).reshape(H, W, 3))
    if marks and ortho is not None:
        dr = ImageDraw.Draw(im)
        x0, x1, z0, z1 = ortho
        for p, rgb in marks:
            cx = (p[2] - z0) / (z1 - z0) * W
            cy = (p[0] - x0) / (x1 - x0) * H
            dr.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], outline=rgb, width=2)
    return im


def label(im, text):
    dr = ImageDraw.Draw(im)
    w = 7 * len(text) + 12
    dr.rectangle([0, im.height - 18, w, im.height], fill=(0, 0, 0))
    dr.text((6, im.height - 15), text, fill=(255, 255, 255))
    return im


def main():
    a = sys.argv[1:]
    iid = next(x for x in a if x.startswith("SKY-"))
    size = tuple(int(v) for v in a[a.index("--size") + 1].split("x")) if "--size" in a else (960, 600)
    out = a[a.index("--out") + 1] if "--out" in a else os.path.join(C.OUT, iid + "_view.png")
    t0 = time.time()
    g = A.build(iid)
    marks = None
    if "--top" in a:
        ortho = (g.x0, g.x0 + g.nx * C.CELL, g.z0, g.z0 + g.nz * C.CELL)
        if "--problems" in a:
            rj = os.path.join(C.OUT, iid + ".json")
            if os.path.exists(rj):
                r = json.load(open(rj))
                marks = [(h["at"], (230, 0, 0)) for h in r["hotspots"] if h["check"] in ("walk", "holes")]
        im = render(g, None, size=size, ortho=ortho, marks=marks)
    else:
        eye = [float(v) for v in a[a.index("--persp") + 1].split(",")]
        tg = [float(v) for v in a[a.index("--persp") + 2].split(",")]
        fov = float(a[a.index("--fov") + 1]) if "--fov" in a else 55.0
        im = render(g, eye, tg, size=size, fov=fov)
    txt = a[a.index("--label") + 1] if "--label" in a else "%s  offline render (audit toolkit, no game)" % iid
    label(im, txt)
    im.save(out, optimize=True)
    print(out, "%.1f s" % (time.time() - t0), "%d KB" % (os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
