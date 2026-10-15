#!/usr/bin/env python3
"""farside_night.py -- the towns' lights at night, baked for the far side (the user, 2026-10-14: "We need to see
lights baked into the farside texture").

  python3 tools/farside_night.py            (~1-2 min; numpy + Pillow + scipy)

Writes godot_project/remake/farside/n_SS_XX.webp: one image per terrain far tile (the same tiles as the day images
f_SS_XX.webp, MapTerrainMesh.far_rect / StationGeo.farside_px), covering exactly the map rect the far side's shader maps
the day image to (tile_rect), at NIGHT_M m per pixel.  Black where it's dark; farside.gdshader adds it as emission at
night (squaring it: so the values here are the square root of the light).

What lights up, all from the world's own data (deterministic):
  - every building's windows (placement.json): warm mostly, some cool, by kind, size and storeys; stores and
    restaurants brighter with a neon accent; works under sodium floodlight;
  - a street lamp every LAMP_EVERY m each side of every street with buildings near it (terrain.json roads) -- or the
    STREETS stream's own lamps (remake/street_lamps.json) when they exist; main streets closer and brighter;
  - town centres (squares, plazas, main streets) brighter still, with strings of coloured lights;
  - the lamp-lit walks (walks.json lighting "lamp_posts": wharves, promenades, beach stairs);
  - the south coast's coloured festoons: its promenades and boardwalks, the Coast Hwy through its towns, and coloured
    lights in the trees round its beaches;
  - a soft glow over all of it (each town's sky-glow on its ground).
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = os.path.join(ROOT, "godot_project")
REM = os.path.join(GP, "remake")
OUT = os.path.join(REM, "farside")

R = 10000.0
CIRC = 2.0 * math.pi * R
LENGTH = 22400.0
HALF = LENGTH / 2.0
NIGHT_M = 8.0                       # m per pixel of the night images
FARSIDE_M = 4.0                     # (the day images' grid: the tiles' rects are aligned to it)
GROUP, FAR_G, CHUNK_X = 8, 3, 100.0
CHUNKS_ROUND = round(CIRC / 65.4 / (GROUP * FAR_G)) * GROUP * FAR_G
N_CX = math.ceil(LENGTH / CHUNK_X)
LAMP_EVERY = 30.0
SOUTH = {"Solana Point", "Pelican Cove", "Playa Verde", "Oceanview"}   # the South Sea's towns (map_expanded.py)
FESTOON = [(1.0, 0.25, 0.3), (0.3, 1.0, 0.4), (0.3, 0.55, 1.0), (1.0, 0.85, 0.2), (1.0, 0.35, 0.9), (0.3, 0.95, 1.0)]
WARM = (1.0, 0.72, 0.42)
COOL = (0.78, 0.86, 1.0)
SODIUM = (1.0, 0.58, 0.22)
LED = (1.0, 0.88, 0.7)


def h01(*parts):
    return int(hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


# ------------------------------------------------------------------ the far tiles (MapTerrainMesh / StationGeo)
def chunk_rect(cs_i, cx_i):
    cs = CIRC / CHUNKS_ROUND
    y0 = -HALF + cx_i * CHUNK_X
    return (cs_i * cs, y0, cs, min(CHUNK_X, HALF - y0))


def group_rect(gs, gx):
    a = chunk_rect(gs * GROUP, gx * GROUP)
    b = chunk_rect(min(gs * GROUP + GROUP, CHUNKS_ROUND) - 1, min(gx * GROUP + GROUP, N_CX) - 1)
    return (a[0], a[1], b[0] + b[2] - a[0], b[1] + b[3] - a[1])


def far_tiles():
    ngs, ngx = math.ceil(CHUNKS_ROUND / GROUP), math.ceil(N_CX / GROUP)
    for fs in range(0, ngs, FAR_G):
        for fx in range(0, ngx, FAR_G):
            a = group_rect(fs, fx)
            b = group_rect(min(fs + FAR_G, ngs) - 1, min(fx + FAR_G, ngx) - 1)
            r = (a[0], a[1], b[0] + b[2] - a[0], b[1] + b[3] - a[1])
            # StationGeo.farside_px, then back to metres: what far_side.gd puts in tile_rect
            p0 = (math.floor(r[0] / FARSIDE_M), math.floor((r[1] + HALF) / FARSIDE_M))
            p1 = (math.ceil((r[0] + r[2]) / FARSIDE_M), math.ceil((r[1] + r[3] + HALF) / FARSIDE_M))
            yield (fs // FAR_G, fx // FAR_G), (p0[0] * FARSIDE_M, p0[1] * FARSIDE_M - HALF,
                                               (p1[0] - p0[0]) * FARSIDE_M, (p1[1] - p0[1]) * FARSIDE_M)


# ------------------------------------------------------------------ the canvas: the whole ring at NIGHT_M m / px
W = int(math.ceil(CIRC / NIGHT_M))
H = int(math.ceil(LENGTH / NIGHT_M))
img = np.zeros((H, W, 3), np.float32)


def px(s, x):
    return (s % CIRC) / NIGHT_M, (x + HALF) / NIGHT_M


def dot(s, x, col, k, r=0.6):
    """a point light: a small disc of radius r px (bilinear spread), colour col * k"""
    c, rw = px(s, x)
    i0, j0 = int(math.floor(rw)), int(math.floor(c))
    for dj in (0, 1):
        for di in (0, 1):
            i, j = i0 + di, (j0 + dj) % W
            if 0 <= i < H:
                wgt = (1 - abs(rw - (i0 + di))) * (1 - abs(c - (j0 + dj)))
                img[i, j] += np.array(col, np.float32) * (k * max(wgt, 0.0) * (1.0 + r))


def rect(s0, x0, s1, x1, col, k):
    c0, r0 = px(s0, x0)
    c1, r1 = px(s1, x1)
    ja, jb = int(min(c0, c1)), int(max(c0, c1)) + 1
    ia, ib = max(0, int(min(r0, r1))), min(H, int(max(r0, r1)) + 1)
    if jb - ja > W // 2:
        return
    cols = [j % W for j in range(ja, jb)]
    img[ia:ib, cols] += np.array(col, np.float32) * k


def load(name):
    p = os.path.join(REM, name)
    if not os.path.exists(p) and os.path.exists(p + ".gz"):
        import gzip
        return json.load(gzip.open(p + ".gz"))
    return json.load(open(p))


def main():
    terrain = load("terrain.json")
    structures = load("placement.json")["structures"]
    walks = load("walks.json")["walks"]

    # ---------------------------------------------------------- buildings: windows
    grid = {}                         # 40 m cell -> [(s, x, settlement)]: where streets have buildings
    for e in structures:
        kind = e.get("kind", "house")
        if kind in ("crossing",):
            continue
        s, x, yaw = float(e["s"]), float(e["x"]), float(e.get("yaw", 0.0))
        grid.setdefault((int(s // 40), int(x // 40)), []).append((s, x, e.get("settlement")))
        fmin, fmax = e.get("fmin", [-6, -6]), e.get("fmax", [6, 6])
        c_, s_ = math.cos(yaw), math.sin(yaw)
        ds, dx = [], []
        for lx in (fmin[0], fmax[0]):
            for lz in (fmin[1], fmax[1]):
                dx.append(lx * c_ + lz * s_)          # (right = +x)
                ds.append(lx * s_ - lz * c_)          # (back = -s)
        storeys = max(1.0, float(e.get("max", [0, 6, 0])[1]) / 3.2)
        r = h01("b", e["id"])
        if kind in ("store", "restaurant", "strip", "bigbox", "kiosk", "bait", "motel"):
            col, k = (WARM if r < 0.6 else COOL), 0.9
        elif kind in ("industrial", "cannery", "fishhouse"):
            col, k = SODIUM, 0.7
        elif kind in ("civic", "church", "school", "landmark", "tower", "lighthouse", "clubhouse"):
            col, k = WARM, 0.65
        elif kind in ("farm", "shed", "comfort_station", "lifeguard"):
            col, k = WARM, 0.12
        else:                                          # homes: most lit warm, some cool, some dark
            col, k = (WARM if r < 0.8 else COOL), (0.0 if r > 0.93 else 0.32)
        k *= (0.6 + 0.8 * h01("lit", e["id"])) * min(2.2, 0.8 + 0.18 * storeys)
        if k > 0:
            # a few lit windows seen from above (a town at night is dark roofs and points of light, not a lit carpet):
            # one per ~120 m2 of footprint, scattered over it
            area = (max(ds) - min(ds)) * (max(dx) - min(dx))
            n = max(1, min(14, int(area / 120.0)))
            for q in range(n):
                fs, fx = h01("ws", e["id"], q), h01("wx", e["id"], q)
                dot(s + min(ds) + (max(ds) - min(ds)) * fs, x + min(dx) + (max(dx) - min(dx)) * fx, col, k * 0.9, r=0.0)
            if kind in ("store", "restaurant", "strip", "bigbox", "civic", "landmark", "church"):
                rect(s + min(ds), x + min(dx), s + max(ds), x + max(dx), col, k * 0.18)   # (a lit front, a floodlit wall)
        if kind in ("store", "restaurant", "strip", "bigbox", "motel") and r < 0.45:
            dot(s, x, FESTOON[int(r * 97) % len(FESTOON)], 1.4)   # (a neon sign)

    def near_buildings(s, x, rad=45.0):
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for (bs, bx, st) in grid.get((int(s // 40) + di, int(x // 40) + dj), []):
                    if abs(bs - s) < rad and abs(bx - x) < rad:
                        return st or True
        return None

    # ---------------------------------------------------------- street lamps
    lamps_file = os.path.join(REM, "street_lamps.json")
    n_lamps = 0
    if os.path.exists(lamps_file):
        # the STREETS stream's own lamps (tools/street_lamps.py): flat arrays -- lamps [s, x, yaw, kind] (kind 0 street,
        # 1 centre, 2 alley, 3 beach), strings [s0, x0, h0, s1, x1, h1, scheme] (1 beach multicolour, 2 centre warm),
        # palms [s, x, ., scale] (lit palms by the south coast's beaches)
        d = json.load(open(lamps_file))
        la = d.get("lamps", [])
        for i in range(0, len(la) - 3, 4):
            s, x, kind = float(la[i]), float(la[i + 1]), int(la[i + 3])
            col, k = [(LED, 0.9), (WARM, 1.3), (LED, 0.55), (FESTOON[(i // 4) % len(FESTOON)], 1.1)][min(kind, 3)]
            dot(s, x, col, k)
            n_lamps += 1
        st = d.get("strings", [])
        for i in range(0, len(st) - 6, 7):
            s0, x0, s1, x1, scheme = float(st[i]), float(st[i + 1]), float(st[i + 3]), float(st[i + 4]), int(st[i + 6])
            L = math.hypot(s1 - s0, x1 - x0)
            for q in range(max(1, int(L // 3))):
                f = q * 3 / max(L, 1)
                col = FESTOON[(q + i) % len(FESTOON)] if scheme == 1 else WARM
                dot(s0 + (s1 - s0) * f, x0 + (x1 - x0) * f, col, 0.5)
        pa = d.get("palms", [])
        for i in range(0, len(pa) - 3, 4):
            s, x = float(pa[i]), float(pa[i + 1])
            for q in range(3):
                dot(s + (h01("p", i, q) - 0.5) * 6, x + (h01("q", i, q) - 0.5) * 6, FESTOON[(i // 4 + q) % len(FESTOON)], 0.8)
    roads = terrain["roads"]
    for ri, rd in enumerate(roads):
        cls = rd.get("cls")
        pts = rd.get("pts", [])
        if len(pts) < 2 or cls in ("gravel",):
            continue
        w = float(rd.get("w", 8))
        every = 20.0 if cls == "main" else (40.0 if cls == "alley" else LAMP_EVERY)
        sodium = h01("city", rd.get("city", "")) < 0.35
        lamp_col = SODIUM if sodium else LED
        coast = rd.get("name") == "Coast Hwy"
        acc = h01("road", ri) * every
        for a, b in zip(pts, pts[1:]):
            s0, x0, s1, x1 = float(a[0]), float(a[1]), float(b[0]), float(b[1])
            dsg = (s1 - s0 + CIRC / 2) % CIRC - CIRC / 2
            L = math.hypot(dsg, x1 - x0)
            if L < 1e-3:
                continue
            ns, nx = -(x1 - x0) / L, dsg / L          # the side normal (s, x)
            t = acc
            while t < L:
                f = t / L
                s, x = s0 + dsg * f, x0 + (x1 - x0) * f
                where = near_buildings(s, x)
                if where:
                    south = where in SOUTH if isinstance(where, str) else False
                    if n_lamps == 0:
                        for side in (-1, 1):
                            o = w * 0.5 + 1.5
                            dot(s + ns * o * side, x + nx * o * side, lamp_col, 1.2 if cls == "main" else 0.9)
                    if cls == "main":                    # town centres: a string of coloured lights over the street
                        for k in range(3):
                            ff = (t + k * every / 3.0) / L
                            if ff < 1:
                                dot(s0 + dsg * ff, x0 + (x1 - x0) * ff, FESTOON[(ri + k) % len(FESTOON)], 0.7)
                    if coast and south:                  # the south coast's beach street: festoons
                        for k in range(4):
                            ff = (t + k * every / 4.0) / L
                            if ff < 1:
                                for side in (-1, 1):
                                    o = w * 0.5 + 3.0
                                    dot(s0 + dsg * ff + ns * o * side, x0 + (x1 - x0) * ff + nx * o * side,
                                        FESTOON[(k + int(t) // 7 + (side > 0)) % len(FESTOON)], 1.0)
                t += every
            acc = t - L

    # ---------------------------------------------------------- town centres: squares and plazas glow
    for ar in terrain.get("areas", []):
        kind = ar.get("kind")
        poly = ar.get("poly", [])
        if not poly:
            continue
        ss = [p[0] for p in poly]
        xs = [p[1] for p in poly]
        if kind in ("square", "plaza"):
            rect(min(ss), min(xs), max(ss), max(xs), WARM, 0.55)
            for i in range(len(poly)):                     # lamps and strings round the edge
                a, b = poly[i], poly[(i + 1) % len(poly)]
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                for k in range(int(L // 8)):
                    f = k * 8 / max(L, 1)
                    dot(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, FESTOON[k % len(FESTOON)] if k % 2 else LED, 0.9)
        elif kind == "beach" and (ar.get("town") in SOUTH or (min(xs) > 0)):
            # the south coast's beaches: coloured lights in the trees along their landward edge (the edge furthest from the
            # sea -- the south seas lie further +x), and scattered through the groves behind
            for i in range(len(poly)):
                a, b = poly[i], poly[(i + 1) % len(poly)]
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                for k in range(int(L // 6)):
                    f = k * 6 / max(L, 1)
                    s, x = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
                    if x < (min(xs) + max(xs)) * 0.5 + 10:
                        dot(s, x, FESTOON[(k + i) % len(FESTOON)], 1.1)
                        if h01("tree", s, x) < 0.5:
                            dot(s, x - 8 - 12 * h01("t2", s), FESTOON[(k + 3) % len(FESTOON)], 0.9)

    # ---------------------------------------------------------- the lit walks; the south's promenades in colour
    for wk in walks:
        pts = wk.get("pts", [])
        lit = (wk.get("traits") or {}).get("lighting") == "lamp_posts"
        south = wk.get("settlement") in SOUTH and wk.get("kind") in ("promenade", "boardwalk", "pier", "pier_head", "beach_stair",
                                                                     "beach_ramp", "finger", "wharf")
        if not (lit or south):
            continue
        acc = 0.0
        for a, b in zip(pts, pts[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            t = acc
            step = 6.0 if south else 24.0
            while t < L:
                f = t / max(L, 1e-3)
                s, x = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
                dot(s, x, FESTOON[int(t // step) % len(FESTOON)] if south else LED, 1.0 if south else 0.9)
                t += step
            acc = t - L

    # ---------------------------------------------------------- the glow; the tiles
    # the glow: a tight halo round each light, and a wide one over each town (seen from across the ring, where a
    # town is a few pixels, the halo is what carries -- the points alone average away in the far mipmaps)
    tight = np.stack([gaussian_filter(img[..., c], 1.5, mode=("constant", "wrap")) for c in range(3)], -1)
    wide = np.stack([gaussian_filter(img[..., c], 6.0, mode=("constant", "wrap")) for c in range(3)], -1)
    out = img + tight * 1.6 + wide * 4.0
    vmax = 3.0
    out = np.sqrt(np.clip(out / vmax, 0.0, 1.0))           # (the shader squares it back)
    out8 = (out * 255.0 + 0.5).astype(np.uint8)
    os.makedirs(OUT, exist_ok=True)
    total = 0
    n = 0
    for (ks, kx), (s0, x0, w, h) in far_tiles():
        c0, r0 = int(round(s0 / NIGHT_M)), int(round((x0 + HALF) / NIGHT_M))
        cw, rh = max(1, int(math.ceil(w / NIGHT_M))), max(1, int(math.ceil(h / NIGHT_M)))
        cols = [(c0 + j) % W for j in range(cw)]
        rows = [min(H - 1, max(0, r0 + i)) for i in range(rh)]
        tile = out8[np.ix_(rows, cols)]
        path = os.path.join(OUT, "n_%02d_%02d.webp" % (ks, kx))
        Image.fromarray(tile, "RGB").save(path, "WEBP", lossless=True, quality=100, method=6)
        total += os.path.getsize(path)
        n += 1
    lit_px = int((out8.max(-1) > 8).sum())
    print(f"farside_night: {n} tiles, {total / 1e6:.1f} MB, {lit_px} lit px of {W * H} "
          f"({'street_lamps.json' if n_lamps else 'derived'} lamps)")


if __name__ == "__main__":
    sys.exit(main())
