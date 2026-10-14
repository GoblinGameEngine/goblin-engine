#!/usr/bin/env python3
"""make_islands.py -- lay out the 100 sky islands (research/sky_islands/00_plan.md) from the canon
(godot_project/remake/bible/sky_islands.json, tools/bible/canon_sky.py) and write

  godot_project/remake/sky/islands.json         every island's layout (the contract's schema, plus the extras below)
  godot_project/remake/sky/islands/<id>.rock.glb    the landmass: the deck (relief, pond and lake basins; "deck-col"
                                                    collides) and the rocky underside, vertex coloured
  godot_project/remake/sky/islands/<id>.lod1.glb    1-3 km: coarse rock + deck + every building as a coloured box
  godot_project/remake/sky/islands/<id>.lod2.glb    the whole station away: a few hundred triangles

  ~/.venvs/ssc-assets/bin/python tools/sky/make_islands.py [--ids SKY-001 ...] [--no-glb] [--previews]

The islands' buildings are copies of the shared models in tools/sky/models.py (remake/catalog/SKY-M-NN.json, built
by tools/build_library.py --ids): each placed building names its model.  Fences, paths, balloons, moss and vines are
data here and are drawn by the game (MultiMesh / generated ribbons), not baked into the glbs (the user, 2026-10-14:
"use all the tricks we've learned to reduce the footprint of this addition").

Local frame (the contract): +X south, +Y up, +Z west, -Z east; y = 0 is the deck at its edge and every dock face.
A building's yaw turns it about +Y; its front (the door side) then faces (-sin yaw, -cos yaw) in (X, Z), and its lot
is w across the front by d deep, centred on (x, z).

Extras beyond the contract's sketch (all local metres):
  "height": {"x0", "z0", "step", "nx", "nz", "data"}   the deck's height grid, int16 centimetres, base64, row-major
                                                       in z (data[iz * nx + ix] is at (x0 + ix*step, z0 + iz*step))
  "graph": {"nodes": [[x, z], ...], "edges": [[a, b, width], ...]}  the walkable path network (paths, roads, the
                                                       promenade inside the fence, and spurs to every door, bridge,
                                                       pad stair, hoist, launcher, pen gate and pond bank)
  buildings[].model, .use, .door [x, z] (the front door on the path), .storeys
  pads[].y and .roof (the building whose roof it is on: larks sit in cradles on the tallest roofs -- the canon)
  hoists[].yaw, launchers[].yaw: the PART's yaw about +Y such that its +Z (sin yaw, cos yaw) points out over the edge
    (parts.json: "stand at the deck edge with +Z out"); buildings' yaw is the other convention (front = -Z turned)
  bridges[].clear: the metres inland its style needs kept free (bridge_styles.json); fence_gaps: the perimeter fence's
    openings ({at, width, bridge index}); cloud_nets: [x, y, z, yaw] on roofs; moss rim/under entries end in the part
    name (moss_a/moss_b/vine_a/vine_b, parts.json); "parts" and "bridge_styles" name the shared part lists
  "moss": {"rim": [[x, z, len], ...], "under": [[x, y, z, len], ...]}   hanging moss and vine cards
  water[]: + "area"; pastures[]: + "animals"; animal_spawns: [x, z, kind] or [x, z, kind, y] (on a roof)
"""
import argparse
import base64
import hashlib
import json
import math
import os
import random
import sys
import time

import numpy as np
import shapely
import shapely.affinity
import shapely.ops
from scipy.spatial import Delaunay
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glb  # noqa: E402
from models import MODELS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
CANON = os.path.join(ROOT, "godot_project", "remake", "bible", "sky_islands.json")
OUT_DIR = os.path.join(ROOT, "godot_project", "remake", "sky")
GLB_DIR = os.path.join(OUT_DIR, "islands")
RES = "res://remake/sky/islands/"
IMG = os.path.join(ROOT, "research", "sky_islands", "img")

BLOCK_M2 = 8000.0
PATH_W = 2.5
ROAD_W = 6.0
FENCE_IN = 1.0
PROM_IN = 3.25                # the promenade path's centre line, in from the edge
INTERIOR_IN = 5.5             # lots start this far in
BRIDGE_W = 3.6
ROAD_BRIDGE_W = 6.0
ALONG_GRID = 20.0             # bridges sit on multiples of this along a face: any two islands can line up a pair
BALLOON_SPACING = 115.0
PAD_R = 6.0
HSTEP = 4.0                   # the height grid
MESH_STEP = 4.0               # the deck mesh's grid

MODEL = {m["id"]: m for m in MODELS}
STYLES_JSON = os.path.join(ROOT, "godot_project", "remake", "sky", "bridges", "bridge_styles.json")
STYLES = json.load(open(STYLES_JSON))["styles"] if os.path.exists(STYLES_JSON) else {}
PARTS = "res://remake/sky/parts/parts.json"


def cut_clear(poly, clear_u):
    """a pasture or pen kept out of the bridges' working room: the largest piece left"""
    if clear_u.is_empty:
        return poly
    q = poly.difference(clear_u.buffer(0.5))
    if q.geom_type == "MultiPolygon":
        q = max(q.geoms, key=lambda g: g.area)
    return q if q.geom_type == "Polygon" else Polygon()


# ------------------------------------------------------------------ helpers
def rng_for(seed, salt):
    return random.Random(int(hashlib.sha1(f"{seed}:{salt}".encode()).hexdigest()[:12], 16))


def model_dims(m):
    """(lot w, lot d, height to the parapet top, storeys)"""
    tr, st = m["traits"], m["traits"]["storeys"]
    w, d = m["lot"]["w"], m["lot"]["d"]
    if m["kind"] == "condo":
        h = 0.45 + 3.0 * st + 1.2
    elif m["kind"] == "store":
        h = 0.2 + 3.6 + (st - 1) * 3.35 + 0.3 + 1.4
    else:
        h = 0.35 + 4.4 + (st - 1) * 4.2 + 0.4 + 1.2
    return w, d, h, st


def body_color(m):
    h = m["traits"]["colors"]["body"].lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def roof_top(m):
    """the roof surface (wall_top), below the parapet"""
    return model_dims(m)[2] - (1.2 if m["kind"] != "store" else 1.4)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def blob(rnd, cx, cz, area, wobble=0.18, n=28, aspect=1.0):
    r0 = math.sqrt(area / math.pi)
    ph = [rnd.uniform(0, math.tau) for _ in range(4)]
    amp = [wobble * rnd.uniform(0.4, 1.0) / (k + 1) for k in range(4)]
    rot = rnd.uniform(0, math.pi)
    pts = []
    for i in range(n):
        a = math.tau * i / n
        r = r0 * (1 + sum(amp[k] * math.sin((k + 2) * a + ph[k]) for k in range(4)))
        x, z = r * math.cos(a) * aspect, r * math.sin(a) / aspect
        pts.append((cx + x * math.cos(rot) - z * math.sin(rot), cz + x * math.sin(rot) + z * math.cos(rot)))
    p = Polygon(pts).buffer(0)
    k = math.sqrt(area / max(p.area, 1e-6))
    return shapely.affinity.scale(p, k, k, origin=(cx, cz))


# ------------------------------------------------------------------ the outline
def make_outline(isl, rnd):
    """An irregular blob of the island's area, cut flat on four dock faces (N -X, S +X, E -Z, W +Z)."""
    area = isl["blocks"] * BLOCK_M2
    aspect = rnd.uniform(0.82, 1.25)
    for _ in range(40):
        ph = [rnd.uniform(0, math.tau) for _ in range(6)]
        amp = [rnd.uniform(0.05, 0.13) / (1 + 0.5 * k) for k in range(6)]
        pts = []
        n = 96
        for i in range(n):
            a = math.tau * i / n
            r = 1.0 + sum(amp[k] * math.sin((k + 2) * a + ph[k]) for k in range(6))
            # a squarer blob: a superellipse (exponent 3) under the wobble
            c, s = math.cos(a), math.sin(a)
            se = (abs(c) ** 3 + abs(s) ** 3) ** (-1 / 3)
            pts.append((r * se * c * aspect, r * se * s / aspect))
        p = Polygon(pts).buffer(0)
        if p.geom_type != "Polygon":
            continue
        minx, minz, maxx, maxz = p.bounds
        cut = {k: rnd.uniform(0.86, 0.93) for k in "NSEW"}
        p = p.intersection(box(minx * cut["N"], minz * cut["E"], maxx * cut["S"], maxz * cut["W"]))
        k = math.sqrt(area / p.area)
        p = shapely.affinity.scale(p, k, k, origin=(0, 0))
        p = shapely.set_precision(p, 0.01)
        minx, minz, maxx, maxz = p.bounds
        faces = {"N": minx, "S": maxx, "E": minz, "W": maxz}
        segs = face_segments(p, faces)
        if all(max(b - a for a, b in segs[s]) >= 14.0 for s in "NSEW"):
            return p, faces, segs
    raise RuntimeError(f"{isl['id']}: no outline with four dock faces")


def face_segments(p, faces):
    """the straight stretches along each dock face: [(a0, a1), ...] along it (Z for N/S, X for E/W) -- a face can be
    broken where the outline dips in between two stretches"""
    out = {}
    for s, v in faces.items():
        if s in "NS":
            line = LineString([(v, -1e4), (v, 1e4)])
        else:
            line = LineString([(-1e4, v), (1e4, v)])
        inter = p.exterior.intersection(line.buffer(0.02))
        pieces = []
        for g in getattr(inter, "geoms", [inter]):
            cs = [c[1] if s in "NS" else c[0] for c in getattr(g, "coords", [])
                  if abs((c[0] if s in "NS" else c[1]) - v) < 0.005]
            if len(cs) >= 2:
                pieces.append((min(cs), max(cs)))
        out[s] = sorted(pieces) or [(0.0, 0.0)]
    return out


# ------------------------------------------------------------------ the grid of lots
def axis_cells(rnd, lo, hi, sizes, road_at0):
    """Cells across an axis's span lo..hi, separated by paths.  A big island's road runs along 0 (bridges line up on
    it): cells go outward from it.  Otherwise the cells fill the span exactly, centred, so a small island loses no
    more than it must.  Returns [(c0, c1)], [(separator centre, width, is_road)]."""
    cells, seps = [], []
    if road_at0:
        seps.append((0.0, ROAD_W, True))
        for sgn in (1, -1):
            at = ROAD_W / 2
            lim = hi if sgn > 0 else -lo
            while True:
                fit = [z for z in sizes if at + z <= lim + z * 0.35]
                if not fit:
                    break
                sz = rnd.choice(fit)
                a, b = at, at + sz
                cells.append((a, b) if sgn > 0 else (-b, -a))
                seps.append((sgn * (b + PATH_W / 2), PATH_W, False))
                at = b + PATH_W
    else:
        at = lo
        seq = []
        while True:
            fit = [z for z in sizes if at + z <= hi + 4.0]
            if not fit:
                break
            sz = rnd.choice(fit)
            seq.append(sz)
            at += sz + PATH_W
        span = sum(seq) + PATH_W * max(0, len(seq) - 1)
        at = (lo + hi) / 2 - span / 2
        for k, sz in enumerate(seq):
            cells.append((at, at + sz))
            if k < len(seq) - 1:
                seps.append((at + sz + PATH_W / 2, PATH_W, False))
            at += sz + PATH_W
    cells.sort()
    seps.sort()
    return cells, seps


def choose_model(rnd, cw, cd, use, prefer_tall=False, ok=None):
    """the best model for a cell cw (along X) x cd (along Z) whose door would open on a path (ok(model, yaw)):
    returns (model, yaw) or None"""
    best = []
    for m in MODELS:
        if m["sky"]["use"] != use:
            continue
        w, d, h, st = model_dims(m)
        for yaw in (0.0, math.pi, math.pi / 2, -math.pi / 2):
            ex, ez = (w, d) if abs(math.sin(yaw)) < 0.5 else (d, w)
            if ex <= cw + 0.01 and ez <= cd + 0.01 and (ok is None or ok(m, yaw)):
                fill = ex * ez / (cw * cd)
                best.append((fill + rnd.uniform(0, 0.25) + (st * 0.02 if prefer_tall else 0.0), m["id"], yaw))
    if not best:
        return None
    best.sort(reverse=True)
    top = [b for b in best if b[0] >= best[0][0] - 0.12]
    _, mid, yaw = rnd.choice(top)
    return MODEL[mid], yaw


def needed_uses(isl):
    """the buildings an island must have besides its homes, in order.  The small islands (1-2 blocks) keep to a hall and
    an infirmary (with homes upstairs) and, from 2 blocks, a gas works: their markets and shops are on the ground
    floors of the hall and the blocks of flats"""
    j, b, pop = isl["jobs"], isl["blocks"], isl["population"]
    uses = ["hall", "infirmary"]
    if b >= 2:
        uses.append("gasworks")
    if pop > 350:
        uses.append("school")
    if b <= 2:
        return uses
    if pop > 1600:
        uses.append("school")
    if b >= 3 or j.get("envelope_wright", 0) >= 12:
        uses.append("envelope_loft")
    if j.get("roper", 0) >= 15 or b >= 6:
        uses.append("ropewalk")
    if b >= 5:
        uses.append("gasworks")
    uses += ["market"] * (1 + b // 4)
    uses += ["workshop"] * (1 + (j.get("smith", 0) + j.get("mender", 0) + j.get("sparks", 0) + j.get("weaver", 0)) // 45)
    uses += ["shops"] * (b // 2)
    return uses


# ------------------------------------------------------------------ one island
def layout(isl):
    rnd = rng_for(isl["seed"], "layout")
    deck, faces, segs = make_outline(isl, rnd)
    fence_poly = deck.buffer(-FENCE_IN, join_style="mitre")
    prom_poly = deck.buffer(-PROM_IN, join_style="mitre")
    interior = deck.buffer(-INTERIOR_IN, join_style="mitre")
    big = isl["blocks"] >= 6
    minx, minz, maxx, maxz = interior.bounds
    # cells sized to the models' lots (22/30/40 x 20-28; turned either way), so the buildings fill them
    sizes_x = [22.0, 22.0, 24.0, 30.0, 30.0, 40.0]
    sizes_z = [21.0, 21.0, 23.0, 24.0, 24.0, 28.0]
    xc, xs = axis_cells(rnd, minx, maxx, sizes_x, big)
    zc, zs = axis_cells(rnd, minz, maxz, sizes_z, big)

    # ---- cells: whole ones are lots, the rest green
    cells = []
    for i, (x0, x1) in enumerate(xc):
        for j, (z0, z1) in enumerate(zc):
            r = box(x0, z0, x1, z1)
            whole = interior.contains(r)
            part = r.intersection(interior)
            cells.append({"i": i, "j": j, "rect": (x0, z0, x1, z1), "whole": whole,
                          "part": part if not part.is_empty else None, "use": None})
    # building sites: the whole cells and the edge's partial ones big enough for a lot (fronts_path checks the lot fits)
    whole = [c for c in cells if c["whole"] or (c["part"] is not None and c["part"].area >= 420.0)]
    site = deck.buffer(-4.0, join_style="mitre")
    site_ids = {id(c) for c in whole}
    rnd.shuffle(whole)
    centre = Point(0, 0)

    def dist0(c):
        x0, z0, x1, z1 = c["rect"]
        return math.hypot((x0 + x1) / 2, (z0 + z1) / 2)

    # ---- bridges: on each face's straight stretch, at multiples of ALONG_GRID
    bridges = []
    for s in "NSEW":
        L = sum(b - a for a, b in segs[s])
        k = 1 if L < 60 else (2 if L < 120 else 3)
        # on the ends of the grid's paths (a bridge's working room then lies along a path, not across lots)
        seps_here = [v for v, _, _ in (xs if s in "EW" else zs)]
        cands = [float(v) for v in seps_here if any(a0 + 4 <= v <= a1 - 4 for a0, a1 in segs[s])]
        if not cands:
            for a0, a1 in segs[s]:
                cands += [float(a) for a in np.arange(math.ceil((a0 + 5) / ALONG_GRID) * ALONG_GRID, a1 - 5 + 1e-6, ALONG_GRID)]
        if not cands:
            a0, a1 = max(segs[s], key=lambda q: q[1] - q[0])
            cands = [round((a0 + a1) / 2, 1)]
        pick = []
        if 0.0 in cands:
            pick.append(0.0)
        mid = pick[0] if pick else sum(cands) / len(cands)
        rest = sorted([c for c in cands if c not in pick], key=lambda c: -abs(c - mid))
        if not pick and rest:
            pick.append(rest.pop(-1))
        while len(pick) < k and rest:
            c = rest.pop(0)
            if all(abs(c - p) >= 18.0 for p in pick):
                pick.append(c)
        for a in sorted(pick):
            wdt = ROAD_BRIDGE_W if big and a == 0.0 else BRIDGE_W
            bridges.append({"side": s, "along": round(float(a), 2), "width": wdt})

    def face_point(s, a, inset=0.0):
        v = faces[s]
        if s == "N":
            return (v + inset, a)
        if s == "S":
            return (v - inset, a)
        if s == "E":
            return (a, v + inset)
        return (a, v - inset)

    # the room each bridge needs on the deck behind it (bridge_styles.json "clear": a telescope's or a gangplank's
    # run inland, a swing span's stowed length along the face) is kept free of lots, pens and ponds
    style = STYLES.get(isl.get("bridge_style"), {})
    clears = []
    for br_ in bridges:
        st = STYLES.get(isl.get("bridge_style") + ("_road" if br_["width"] >= ROAD_W else ""), style)
        cl = st.get("clear") or {}
        o = {"N": (-1.0, 0.0), "S": (1.0, 0.0), "E": (0.0, -1.0), "W": (0.0, 1.0)}[br_["side"]]
        xb = (o[1], -o[0])                                  # the bridge's local +X (= +Y x out), in (X, Z)
        f0 = face_point(br_["side"], br_["along"], 0.0)
        hw = br_["width"] / 2 + 0.2
        rects = [(-hw, hw, -max(cl.get("inland", 0.0), 2.0) - 1.0)]
        if "along" in cl:
            rects.append((cl["along"][0] - 0.5, cl["along"][1] + 0.5, -cl.get("out", 4.6) - 0.5))
        for (x0_, x1_, zin) in rects:
            q = [(f0[0] + xb[0] * xx + o[0] * zz, f0[1] + xb[1] * xx + o[1] * zz)
                 for xx, zz in ((x0_, 0.5), (x1_, 0.5), (x1_, zin), (x0_, zin))]
            clears.append(Polygon(q))
        br_["clear"] = round(max(cl.get("inland", 0.0), cl.get("out", 0.0)), 1)
    clear_u = unary_union(clears) if clears else Polygon()

    # ---- water: the lake (in from the middle, over a 2x2 of cells), then the ponds
    water = []
    used_cells = set()
    wcanon = isl.get("water") or {}
    lake_m2 = float(wcanon.get("lake_m2") or 0.0)
    ponds = list(wcanon.get("ponds_m2") or [400.0])
    taken = unary_union([])

    def can_build(c):
        # the smallest lot fits in it somewhere on the site, clear of the bridges' room (cached)
        if "fits" not in c:
            x0, z0, x1, z1 = c["rect"]
            c["fits"] = False
            for (ex, ez) in ((22.0, 21.0), (21.0, 22.0)):
                if ex > x1 - x0 + 0.01 or ez > z1 - z0 + 0.01:
                    continue
                for fx, fz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cx = (x0 + x1) / 2 + fx * ((x1 - x0) - ex) / 2
                    cz = (z0 + z1) / 2 + fz * ((z1 - z0) - ez) / 2
                    lot = box(cx - ex / 2, cz - ez / 2, cx + ex / 2, cz + ez / 2)
                    if site.contains(lot) and not lot.buffer(-1.0).intersects(clear_u):
                        c["fits"] = True
        return c["fits"]

    def free_cells():
        return [c for c in whole if id(c) not in used_cells and can_build(c)]

    # cells kept for buildings: what the island's trades and halls need, and homes for its people (~160 a block of
    # flats), but never more than three quarters of the whole cells
    reserve = min(len(needed_uses(isl)) + math.ceil(isl["population"] / 110.0), int(len(free_cells()) * 0.8))

    if lake_m2 > 0:
        cands = sorted(free_cells(), key=lambda c: -dist0(c))
        placed = False
        for c in cands[: max(3, len(cands) // 2)]:
            x0, z0, x1, z1 = c["rect"]
            cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
            poly = blob(rnd, cx, cz, lake_m2, wobble=0.22, n=36, aspect=rnd.uniform(0.8, 1.3))
            if interior.buffer(-4).contains(poly) and not poly.buffer(1.5).intersects(clear_u):
                water.append({"poly": poly, "kind": "lake", "depth": round(rnd.uniform(3.5, 5.5), 1)})
                for c2 in whole:
                    if box(*c2["rect"]).intersects(poly.buffer(3)):
                        used_cells.add(id(c2))
                        c2["use"] = "water"
                placed = True
                break
        if not placed:
            ponds.append(lake_m2 * 0.4)
    for a in ponds:
        # a pond may spill over its cell's paths onto the neighbouring cells, if they're still free (the paths round
        # it are cut away later)
        cands = [((c["rect"][0] + c["rect"][2]) / 2, (c["rect"][1] + c["rect"][3]) / 2) for c in free_cells()]
        cands += [(c["part"].representative_point().x, c["part"].representative_point().y) for c in cells
                  if c["part"] is not None and not c["whole"] and c["use"] is None]
        rnd.shuffle(cands)
        ok_area = interior.buffer(-2.0)
        # the green corners first (they'd be green anyway), then the whole cells; smaller if it won't fit
        part_first = sorted(cands, key=lambda q: 0 if not any(abs(q[0] - (c["rect"][0] + c["rect"][2]) / 2) < 0.01 and
                                                              abs(q[1] - (c["rect"][1] + c["rect"][3]) / 2) < 0.01 for c in whole) else 1)
        done = False
        for k_ in (1.0, 0.7, 0.5, 0.35):
            for (cx, cz) in part_first:
                poly = blob(rnd, cx, cz, max(90.0, a * k_), wobble=0.2, n=24, aspect=rnd.uniform(0.75, 1.3))
                if not ok_area.contains(poly) or poly.buffer(1.5).intersects(clear_u):
                    continue
                touched = [c for c in cells if box(*c["rect"]).intersects(poly.buffer(2.0))]
                if any(id(c) in used_cells or c["use"] is not None for c in touched):
                    continue
                if len(free_cells()) - sum(1 for c in touched if id(c) in site_ids) < reserve and (water or k_ > 0.35):
                    continue
                water.append({"poly": poly, "kind": "pond", "depth": round(rnd.uniform(1.2, 2.2), 1)})
                for c in touched:
                    used_cells.add(id(c))
                    c["use"] = "pond_garden"
                done = True
                break
            if done:
                break
    # ---- pastures and pens (livestock), from the canon's head counts
    lv = isl.get("livestock") or {}
    pastures = []
    goat_sheep = int(lv.get("goat", 0)) + int(lv.get("sheep", 0)) + int(lv.get("pig", 0))
    need_m2 = goat_sheep * 18.0 + int(lv.get("rabbit", 0)) * 1.5
    rolling = isl["relief"] == "rolling"
    # the edge's partial cells first (green anyway), then whole cells as paddocks
    edge = sorted([c for c in cells if id(c) not in site_ids and c["part"] is not None and c["use"] is None and c["part"].area > 140],
                  key=lambda c: -c["part"].area)
    got = 0.0
    for c in edge:
        if got >= need_m2:
            break
        poly = c["part"].buffer(-1.5)
        if poly.is_empty or poly.area < 100:
            continue
        if poly.geom_type == "MultiPolygon":
            poly = max(poly.geoms, key=lambda q: q.area)
        c["use"] = "pasture"
        pastures.append({"poly": poly, "kind": "pasture"})
        got += poly.area
    while got < need_m2 * 0.6:
        cands = sorted([c for c in free_cells() if c["whole"]], key=lambda c: -dist0(c))
        if not cands or len(free_cells()) <= reserve:
            break
        c = cands[0]
        used_cells.add(id(c))
        c["use"] = "pasture"
        x0, z0, x1, z1 = c["rect"]
        poly = box(x0 + 1, z0 + 1, x1 - 1, z1 - 1) if c["whole"] else c["part"].buffer(-1.0)
        if poly.geom_type == "MultiPolygon":
            poly = max(poly.geoms, key=lambda q: q.area)
        pastures.append({"poly": poly, "kind": "pasture"})
        got += poly.area
    # a pen with a coop and hutches in one more cell (hens, geese, rabbits; the roof coops are on the buildings)
    cands = sorted([c for c in free_cells() if c["whole"]], key=dist0)
    if cands and len(free_cells()) > reserve:
        c = cands[len(cands) // 2]
        used_cells.add(id(c))
        c["use"] = "pens"
        x0, z0, x1, z1 = c["rect"]
        xm = (x0 + x1) / 2
        pastures.append({"poly": box(x0 + 1, z0 + 1, xm - 0.5, z1 - 1), "kind": "pen"})
        pastures.append({"poly": box(xm + 0.5, z0 + 1, x1 - 1, (z0 + z1) / 2), "kind": "coop"})
    # wild: the remaining green corners (hedge, scrub, the pond margins)
    for c in cells:
        if c["part"] is not None and id(c) not in site_ids and c["use"] is None:
            poly = c["part"].buffer(-1.0)
            if not poly.is_empty and poly.area > 60:
                if poly.geom_type == "MultiPolygon":
                    poly = max(poly.geoms, key=lambda q: q.area)
                c["use"] = "wild"
                pastures.append({"poly": poly, "kind": "wild"})
    for w in water:
        ring = w["poly"].buffer(4.0).difference(w["poly"].buffer(0.5))
        pastures.append({"poly": ring, "kind": "wild", "margin": True})

    for p_ in pastures:
        if not p_.get("margin"):
            p_["poly"] = cut_clear(p_["poly"], clear_u)
    pastures = [p_ for p_ in pastures if not p_["poly"].is_empty and p_["poly"].area > 20.0]
    # ---- paths and roads: the grid's separators, the promenade inside the fence
    sep_lines, road_lines = [], []
    reach = prom_poly.buffer(0.6)                          # (a little past the promenade: they cross it, so they node)
    for (v, wdt, road) in xs:
        ln = LineString([(v, minz - 50), (v, maxz + 50)]).intersection(reach)
        (road_lines if road else sep_lines).append(ln)
    for (v, wdt, road) in zs:
        ln = LineString([(minx - 50, v), (maxx + 50, v)]).intersection(reach)
        (road_lines if road else sep_lines).append(ln)
    wet = unary_union([w["poly"].buffer(1.6) for w in water]) if water else None
    pens = unary_union([p["poly"] for p in pastures if p["kind"] in ("pasture", "pen", "coop") and not p.get("margin")]) \
        if pastures else None

    def clip(lines):
        g = unary_union([l for l in lines if not l.is_empty])
        if wet is not None:
            g = g.difference(wet)
        if pens is not None and not pens.is_empty:
            g = g.difference(pens.buffer(-0.5))
        return [l for l in getattr(g, "geoms", [g]) if l.length > 1.0]
    paths = clip(sep_lines)
    roads = clip(road_lines) if big else []
    promenade = LineString(prom_poly.exterior.coords)

    # the connected network (a stub cut off by a pen or the water is dropped): what doors and spurs may join
    base = node_graph_main([(l, PATH_W) for l in paths] + [(l, ROAD_W) for l in roads] + [(promenade, PATH_W)])
    base_lines = [(LineString([base["nodes"][a], base["nodes"][b]]), w) for a, b, w in base["edges"]]
    net = MultiLineString([l.coords for l, _ in base_lines])
    road_net = unary_union([l for l, w in base_lines if w >= ROAD_W]) if roads else None
    if road_net is not None and road_net.is_empty:
        road_net = None

    def fronts_path(c, m, yaw):
        x0, z0, x1, z1 = c["rect"]
        w, d, h, st = model_dims(m)
        fx, fz = -math.sin(yaw), -math.cos(yaw)
        ex, ez = (w, d) if abs(math.sin(yaw)) < 0.5 else (d, w)
        cx = (x0 + x1) / 2 + fx * ((x1 - x0) - ex) / 2
        cz = (z0 + z1) / 2 + fz * ((z1 - z0) - ez) / 2
        dx, dz = cx + fx * d / 2, cz + fz * d / 2
        lot = box(cx - ex / 2, cz - ez / 2, cx + ex / 2, cz + ez / 2)
        if not site.contains(lot) or lot.buffer(-1.0).intersects(clear_u):
            return False
        for t in (PATH_W / 2, 2.0, 2.75, 3.5, 4.25):          # (the promenade can be a few metres out)
            if Point(dx + fx * t, dz + fz * t).distance(net) < 0.35:
                return True
        return road_net is not None and Point(dx + fx * ROAD_W / 2, dz + fz * ROAD_W / 2).distance(road_net) < 0.35

    # ---- buildings: the uses the island needs first (hall and school near the middle), dwellings in the rest
    buildings = []
    uses = needed_uses(isl)
    cands = sorted(free_cells(), key=dist0)
    order = []
    for u in uses:
        if u in ("hall", "school", "market", "infirmary"):
            order.append((u, "centre"))
        else:
            order.append((u, "any"))
    for u, where in order:
        pool = free_cells()
        if not pool:
            break
        pool.sort(key=dist0)
        if where == "any":
            rnd.shuffle(pool)
        for c in pool:
            x0, z0, x1, z1 = c["rect"]
            pick = choose_model(rnd, x1 - x0, z1 - z0, u, ok=lambda m, y, c=c: fronts_path(c, m, y))
            if pick:
                used_cells.add(id(c))
                c["use"] = u
                buildings.append((c, pick[0], pick[1]))
                break
    for c in free_cells():
        x0, z0, x1, z1 = c["rect"]
        pick = choose_model(rnd, x1 - x0, z1 - z0, "dwelling", prefer_tall=True, ok=lambda m, y, c=c: fronts_path(c, m, y))
        if pick:
            used_cells.add(id(c))
            c["use"] = "dwelling"
            buildings.append((c, pick[0], pick[1]))
        else:
            c["use"] = "green"
            poly = box(x0 + 1, z0 + 1, x1 - 1, z1 - 1) if c["whole"] else c["part"].buffer(-1.0)
            if poly.geom_type == "MultiPolygon":
                poly = max(poly.geoms, key=lambda q: q.area)
            if not poly.is_empty:
                pastures.append({"poly": poly, "kind": "wild"})

    for p_ in pastures:
        if not p_.get("margin"):
            p_["poly"] = cut_clear(p_["poly"], clear_u)
    pastures = [p_ for p_ in pastures if not p_["poly"].is_empty and p_["poly"].area > 20.0]
    # ---- the height grid: rolling hills that die away to y = 0 along the edge band, basins for the water
    bx0, bz0, bx1, bz1 = deck.bounds
    gx = np.arange(math.floor(bx0 / HSTEP) * HSTEP, bx1 + HSTEP, HSTEP)
    gz = np.arange(math.floor(bz0 / HSTEP) * HSTEP, bz1 + HSTEP, HSTEP)
    GX, GZ = np.meshgrid(gx, gz)
    pts = shapely.points(GX.ravel(), GZ.ravel())
    edge_d = shapely.distance(pts, deck.exterior).reshape(GX.shape)
    inside = shapely.contains(deck, pts).reshape(GX.shape)
    edge_d = np.where(inside, edge_d, 0.0)
    H = np.zeros_like(GX)
    hills = []
    if rolling:
        nh = 2 + isl["blocks"] // 2
        for _ in range(nh):
            p = interior.representative_point() if _ == 0 else None
            for _try in range(30):
                x = rnd.uniform(minx, maxx)
                z = rnd.uniform(minz, maxz)
                if interior.contains(Point(x, z)):
                    break
            r = rnd.uniform(28.0, 70.0)
            h = min(r * rnd.uniform(0.06, 0.12), 9.0)
            hills.append([round(x, 1), round(z, 1), round(r, 1), round(h, 2)])
            H += h * np.exp(-((GX - x) ** 2 + (GZ - z) ** 2) / (r * r))
        H *= smoothstep(PROM_IN + 3.0, 26.0, edge_d)
    # water: a flat surface a little under the lowest ground round it, the bed dished below it
    wout = []
    for w in water:
        poly = w["poly"]
        ring = np.array(poly.exterior.coords)
        ground = sample(H, gx, gz, ring[:, 0], ring[:, 1])
        level = float(ground.min()) - 0.25
        dd = shapely.distance(pts, poly.exterior).reshape(GX.shape)
        ins = shapely.contains(poly, pts).reshape(GX.shape)
        bed = level - np.minimum(w["depth"], 0.35 + dd * 0.45)
        H = np.where(ins, bed, H)
        # the banks come down to the waterline within 3 m
        bank = (~ins) & (dd < 3.0)
        H = np.where(bank, (level + 0.12) + (H - (level + 0.12)) * smoothstep(0.0, 3.0, dd), H)
        w["level"] = level
        wout.append({"outline": rnd_pts(ring), "level": round(level, 2), "depth": w["depth"], "kind": w["kind"],
                     "area": round(poly.area)})
    H = np.where(inside, H, 0.0)

    def ground_at(x, z):
        return float(sample(H, gx, gz, np.array([x]), np.array([z]))[0])

    # ---- placed buildings
    bout = []
    for n, (c, m, yaw) in enumerate(buildings):
        x0, z0, x1, z1 = c["rect"]
        w, d, h, st = model_dims(m)
        cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
        fx, fz = -math.sin(yaw), -math.cos(yaw)
        ex, ez = (w, d) if abs(math.sin(yaw)) < 0.5 else (d, w)
        # pushed to the front edge of its cell: the door on the path
        cw, cd = x1 - x0, z1 - z0
        cx += fx * (cw - ex) / 2
        cz += fz * (cd - ez) / 2
        door = (cx + fx * d / 2, cz + fz * d / 2)
        y = ground_at(*door)
        bout.append({"id": f"{isl['id']}-{n + 1:02d}", "model": m["id"], "use": m["sky"]["use"], "x": round(cx, 2),
                     "z": round(cz, 2), "yaw": round(yaw, 4), "w": w, "d": d, "h": round(h, 2), "y": round(y, 2),
                     "storeys": st, "homes": m["sky"]["homes"], "door": [round(door[0], 2), round(door[1], 2)],
                     "_rect": (cx - ex / 2, cz - ez / 2, cx + ex / 2, cz + ez / 2)})

    # ---- hoists (cargo lines) at the edge between the faces, facing out; line-rocket launchers, one per side
    hoists = []
    nho = 1 if isl["blocks"] <= 3 else (2 if isl["blocks"] <= 6 else 3)
    diag = [math.pi / 4, 5 * math.pi / 4, 3 * math.pi / 4, 7 * math.pi / 4]
    for a in diag[:nho]:
        far = Point(1e4 * math.cos(a), 1e4 * math.sin(a))
        ray = LineString([(0, 0), far.coords[0]])
        hit = ray.intersection(deck.exterior)
        q = hit if hit.geom_type == "Point" else min(getattr(hit, "geoms", [hit]), key=lambda g: g.distance(Point(0, 0)))
        ln = math.hypot(q.x, q.y)
        x, z = q.x * (ln - 2.5) / ln, q.y * (ln - 2.5) / ln
        yaw = math.atan2(q.x, q.y)                         # (the part's +Z, (sin yaw, cos yaw), points out over the edge)
        hoists.append({"x": round(x, 2), "z": round(z, 2), "yaw": round(yaw, 4)})
    launchers = []
    for s in "NSEW":
        a0, a1 = max(segs[s], key=lambda q: q[1] - q[0])
        used = [b["along"] for b in bridges if b["side"] == s]
        best, bd = None, -1
        for a in np.linspace(a0 + 3, a1 - 3, 13):
            dd = min([abs(a - u) for u in used] or [99])
            if dd > bd:
                best, bd = a, dd
        x, z = face_point(s, float(best), 2.0)
        launchers.append({"side": s, "x": round(x, 2), "z": round(z, 2),
                          "yaw": {"N": -math.pi / 2, "S": math.pi / 2, "E": math.pi, "W": 0.0}[s]})     # (+Z out)

    # ---- lark cradles on the tallest roofs (the canon: "larks sit in cradles on the island's tallest roofs")
    pads = []
    tall = sorted([b for b in bout if min(MODEL[b["model"]]["lot"]["w"], MODEL[b["model"]]["lot"]["d"]) >= 20],
                  key=lambda b: -b["h"])
    for b in tall[: max(2, int(isl.get("aerostats", 2)))]:
        m = MODEL[b["model"]]
        pads.append({"x": b["x"], "z": b["z"], "yaw": b["yaw"], "y": round(b["y"] + roof_top(m), 2), "roof": b["id"]})
    while len(pads) < max(2, int(isl.get("aerostats", 2))):
        # (no roof big enough left: a cradle on the deck by the promenade)
        a = math.tau * len(pads) / 5
        p = prom_poly.buffer(-PAD_R - 1).exterior.interpolate(prom_poly.buffer(-PAD_R - 1).exterior.length * a / math.tau)
        pads.append({"x": round(p.x, 2), "z": round(p.y, 2), "yaw": 0.0, "y": round(ground_at(p.x, p.y), 2), "roof": None})

    # ---- balloons: a hex cluster over the island, anchored on the open deck
    nbal = int(isl.get("balloons") or (math.ceil(1.6 * isl["blocks"]) + 1))
    cen = deck.centroid
    rot = rnd.uniform(0, math.pi / 3)
    lat = []
    R = 6
    for i in range(-R, R + 1):
        for j in range(-R, R + 1):
            x = (i + j * 0.5) * BALLOON_SPACING
            z = j * BALLOON_SPACING * math.sqrt(3) / 2
            lat.append((x * math.cos(rot) - z * math.sin(rot), x * math.sin(rot) + z * math.cos(rot)))
    off = (rnd.uniform(-0.5, 0.5) * BALLOON_SPACING, rnd.uniform(-0.5, 0.5) * BALLOON_SPACING) if nbal > 1 else (0, 0)
    lat.sort(key=lambda p: math.hypot(p[0] + off[0], p[1] + off[1]))
    chosen = lat[:nbal]
    mx = sum(p[0] for p in chosen) / nbal
    mz = sum(p[1] for p in chosen) / nbal
    lots_u = unary_union([box(*b["_rect"]).buffer(1.5) for b in bout]) if bout else None
    anchor_ok = deck.buffer(-6.0)
    if lots_u is not None:
        anchor_ok = anchor_ok.difference(lots_u)
    if wet is not None:
        anchor_ok = anchor_ok.difference(wet)
    balloons = []
    for (x, z) in chosen:
        x, z = x - mx + cen.x, z - mz + cen.y
        p = Point(x, z)
        q = p if anchor_ok.contains(p) else shapely.ops.nearest_points(anchor_ok, p)[0]
        balloons.append({"x": round(x, 1), "z": round(z, 1), "anchor": [round(q.x, 2), round(ground_at(q.x, q.y), 2), round(q.y, 2)]})

    # ---- the path graph: every line noded together, with spurs to doors, bridges, hoists, launchers, pads, gates, banks
    spurs = []
    for b in bout:
        fx, fz = -math.sin(b["yaw"]), -math.cos(b["yaw"])
        dx, dz = b["door"]
        q = shapely.ops.nearest_points(net, Point(dx + fx * 1.0, dz + fz * 1.0))[0]
        v = (q.x - dx, q.y - dz)
        ln = math.hypot(*v) or 1.0
        spurs.append(LineString([(dx - fx * 0.2, dz - fz * 0.2), (q.x + v[0] / ln * 0.3, q.y + v[1] / ln * 0.3)]))
    for br in bridges:
        f0 = face_point(br["side"], br["along"], 0.0)
        f1 = face_point(br["side"], br["along"], PROM_IN)
        q = shapely.ops.nearest_points(net, Point(*f1))[0]
        v = (q.x - f1[0], q.y - f1[1])
        ln = math.hypot(*v) or 1.0
        spurs.append(LineString([f0, f1, (q.x + v[0] / ln * 0.3, q.y + v[1] / ln * 0.3)] if ln > 0.05 else
                                [f0, face_point(br["side"], br["along"], PROM_IN + 1.0)]))
    for h in hoists + launchers:
        p = Point(h["x"], h["z"])
        q = promenade.interpolate(promenade.project(p))
        v = (q.x - p.x, q.y - p.y)
        ln = math.hypot(*v) or 1.0
        spurs.append(LineString([(p.x, p.y), (q.x + v[0] / ln, q.y + v[1] / ln)]))
    for p_ in pastures:
        if p_["kind"] in ("pasture", "pen", "coop") and not p_.get("margin"):
            poly = p_["poly"]
            allp = net
            a, bpt = shapely.ops.nearest_points(poly.exterior, allp)
            v = (bpt.x - a.x, bpt.y - a.y)
            ln = math.hypot(*v) or 1.0
            spurs.append(LineString([(a.x, a.y), (bpt.x + v[0] / ln, bpt.y + v[1] / ln)]))
            p_["gate"] = [round(a.x, 2), round(a.y, 2)]
    for w in water:
        allp = net
        a, bpt = shapely.ops.nearest_points(w["poly"].buffer(1.0).exterior, allp)
        v = (bpt.x - a.x, bpt.y - a.y)
        ln = math.hypot(*v) or 1.0
        spurs.append(LineString([(a.x, a.y), (bpt.x + v[0] / ln, bpt.y + v[1] / ln)]))
    graph = node_graph_main(base_lines + [(l, 1.6) for l in spurs])

    # ---- animals: spawn points from the canon's head counts and wildlife
    spawns = []
    arnd = rng_for(isl["seed"], "animals")

    def pts_in(poly, n):
        out = []
        if poly.is_empty:
            return out
        x0_, z0_, x1_, z1_ = poly.bounds
        for _ in range(n * 30):
            if len(out) >= n:
                break
            x, z = arnd.uniform(x0_, x1_), arnd.uniform(z0_, z1_)
            if poly.contains(Point(x, z)):
                out.append((x, z))
        return out
    pasture_u = unary_union([p["poly"] for p in pastures if p["kind"] == "pasture"]) if pastures else Polygon()
    pen_u = unary_union([p["poly"] for p in pastures if p["kind"] in ("pen", "coop")]) if pastures else Polygon()
    wild_u = unary_union([p["poly"] for p in pastures if p["kind"] == "wild"]) if pastures else Polygon()
    water_u = unary_union([w["poly"] for w in water]) if water else Polygon()
    for kind, per in (("goat", 4), ("sheep", 4), ("pig", 2)):
        n = int(lv.get(kind, 0))
        if n:
            for x, z in pts_in(pasture_u if not pasture_u.is_empty else pen_u, max(1, n // per)):
                spawns.append([round(x, 1), round(z, 1), kind])
    for kind, per in (("hen", 12), ("goose", 6), ("rabbit", 10)):
        n = int(lv.get(kind, 0))
        if n:
            for x, z in pts_in(pen_u, max(1, min(6, n // per // 3))):
                spawns.append([round(x, 1), round(z, 1), kind])
    for kind, per in (("duck", 5), ("goose", 8)):
        n = int(lv.get(kind, 0))
        if n:
            for x, z in pts_in(water_u, max(1, n // per)):
                spawns.append([round(x, 1), round(z, 1), kind])
    # roof coops, dove lofts and hives on the dwellings' roofs
    roofs = [b for b in bout if b["use"] == "dwelling" and not any(p["roof"] == b["id"] for p in pads)]
    arnd.shuffle(roofs)
    for kind, per in (("hen", 25), ("dove", 30), ("bee", 15)):
        n = int(lv.get(kind, 0))
        for b in roofs[: max(1, n // per)] if n else []:
            m = MODEL[b["model"]]
            spawns.append([b["x"], b["z"], kind, round(b["y"] + roof_top(m), 2)])
        roofs = roofs[max(1, n // per):] + roofs[: max(1, n // per)]
    if lv.get("fish"):
        for w in water:
            c = w["poly"].representative_point()
            spawns.append([round(c.x, 1), round(c.y, 1), "fish"])
    for kind in isl.get("wildlife") or []:
        if kind in ("frog", "dragonfly", "heron"):
            where = water_u.buffer(3) if not water_u.is_empty else wild_u
        elif kind in ("swallow", "swift", "ballooning_spider", "tern", "gull"):
            where = deck.buffer(-1).difference(deck.buffer(-10))      # the rim
        else:
            where = wild_u if not wild_u.is_empty else deck.buffer(-6)
        for x, z in pts_in(where, 2 if kind not in ("cat", "heron") else 1):
            spawns.append([round(x, 1), round(z, 1), kind])

    # ---- moss and vines: data for shared cards (rim) -- the underside's are added with the rock mesh
    mrnd = rng_for(isl["seed"], "moss")
    rim = []
    ext = deck.exterior
    n = int(ext.length / 3.0)
    for i in range(n):
        if mrnd.random() < 0.62:
            p = ext.interpolate(ext.length * (i + mrnd.random() * 0.6) / n)
            # long beards away from the dock faces (they'd foul the bridges there)
            near_face = any(abs(p.x - faces[s]) < 0.3 for s in "NS") or any(abs(p.y - faces[s]) < 0.3 for s in "EW")
            ln = mrnd.uniform(1.5, 4.0) if near_face else mrnd.uniform(2.0, 16.0) * (1.0 if mrnd.random() < 0.7 else 1.6)
            part = ("moss_a" if ln < 3.0 else "moss_b") if ln < 4.5 else ("vine_a" if ln < 9.0 else "vine_b")
            rim.append([round(p.x, 2), round(p.y, 2), round(ln, 1), part])

    depth = round(0.3 * math.sqrt(isl["blocks"] * BLOCK_M2) + rnd.uniform(4.0, 14.0), 1)    # (28 m .. 100 m)
    # cloud nets (the canon: the islands drink from cloud nets and snowmelt) across the wind on some dwellings' roofs
    cloud_nets = []
    nrnd = rng_for(isl["seed"], "nets")
    padded = {p_["roof"] for p_ in pads}
    for b in bout:
        if b["use"] == "dwelling" and b["id"] not in padded and nrnd.random() < 0.45:
            m = MODEL[b["model"]]
            cloud_nets.append([b["x"], round(b["y"] + roof_top(m), 2), b["z"], 0.0])   # (yaw 0: the net's plane X-Y faces
                                                                                       # the east wind along Z)
    out = {"id": isl["id"], "name": isl["name"], "blocks": isl["blocks"], "population": isl["population"],
           "bridge_style": isl.get("bridge_style"), "outline": rnd_pts(np.array(deck.exterior.coords)[:-1][::-1] if not deck.exterior.is_ccw else np.array(deck.exterior.coords)[:-1]),
           "faces": {k: round(v, 2) for k, v in faces.items()},
           "face_spans": {k: [[round(a, 2), round(b, 2)] for a, b in v] for k, v in segs.items()},
           "relief": {"kind": isl["relief"], "hills": hills}, "depth": depth,
           "height": pack_height(H, gx, gz),
           "buildings": [{k: v for k, v in b.items() if not k.startswith("_")} for b in bout],
           "paths": [rnd_pts(np.array(l.coords)) for l in paths],
           "roads": [rnd_pts(np.array(l.coords)) for l in roads],
           "promenade": rnd_pts(np.array(promenade.coords)),
           "fence": rnd_pts(np.array(fence_poly.exterior.coords)),
           "fence_gaps": [{"at": [round(c_[0], 2), round(c_[1], 2)], "width": round(br_["width"] + 1.0, 1), "bridge": k}
                          for k, br_ in enumerate(bridges)
                          for c_ in [face_point(br_["side"], br_["along"], FENCE_IN)]],
           "cloud_nets": cloud_nets,
           "bridges": bridges, "balloons": balloons, "pads": pads, "hoists": hoists, "launchers": launchers,
           "water": wout,
           "pastures": [{"outline": rnd_pts(np.array(p["poly"].exterior.coords)) if p["poly"].geom_type == "Polygon"
                         else [rnd_pts(np.array(g.exterior.coords)) for g in p["poly"].geoms],
                         "kind": p["kind"], **({"gate": p["gate"]} if "gate" in p else {}),
                         **({"margin": True} if p.get("margin") else {})}
                        for p in pastures if not p["poly"].is_empty and p["poly"].geom_type in ("Polygon", "MultiPolygon")
                        and not p.get("margin")],
           "pond_margins": [rnd_pts(np.array(w["poly"].buffer(4.0).exterior.coords)) for w in water],
           "animal_spawns": spawns, "graph": graph, "moss": {"rim": rim, "under": []},
           "lod": {"rock": RES + isl["id"] + ".rock.glb", "lod1": RES + isl["id"] + ".lod1.glb",
                   "lod2": RES + isl["id"] + ".lod2.glb"}}
    ctx = {"deck": deck, "H": H, "gx": gx, "gz": gz, "inside": inside, "water": water, "pastures": pastures,
           "bout": bout, "faces": faces, "depth": depth, "rnd": rng_for(isl["seed"], "rock")}
    check(out, ctx)
    return out, ctx


def sample(H, gx, gz, xs, zs):
    fx = np.clip((np.asarray(xs) - gx[0]) / HSTEP, 0, len(gx) - 1.0001)
    fz = np.clip((np.asarray(zs) - gz[0]) / HSTEP, 0, len(gz) - 1.0001)
    ix, iz = np.floor(fx).astype(int), np.floor(fz).astype(int)
    tx, tz = fx - ix, fz - iz
    h00, h10 = H[iz, ix], H[iz, ix + 1]
    h01, h11 = H[iz + 1, ix], H[iz + 1, ix + 1]
    return (h00 * (1 - tx) + h10 * tx) * (1 - tz) + (h01 * (1 - tx) + h11 * tx) * tz


def pack_height(H, gx, gz):
    a = np.clip(np.round(H * 100), -32768, 32767).astype("<i2")
    return {"x0": float(gx[0]), "z0": float(gz[0]), "step": HSTEP, "nx": int(len(gx)), "nz": int(len(gz)),
            "data": base64.b64encode(a.tobytes()).decode()}


def rnd_pts(a):
    return [[round(float(p[0]), 2), round(float(p[1]), 2)] for p in a]


def node_graph_main(lines):
    """node_graph, keeping only the piece the promenade is in (stubs cut off by a pen or the water are dropped)"""
    g = node_graph(lines)
    n = len(g["nodes"])
    adj = [[] for _ in range(n)]
    for a, b, _ in g["edges"]:
        adj[a].append(b)
        adj[b].append(a)
    comp = [-1] * n
    sizes = []
    for s in range(n):
        if comp[s] >= 0:
            continue
        stack, k = [s], len(sizes)
        comp[s] = k
        cnt = 0
        while stack:
            u = stack.pop()
            cnt += 1
            for v in adj[u]:
                if comp[v] < 0:
                    comp[v] = k
                    stack.append(v)
        sizes.append(cnt)
    main = max(range(len(sizes)), key=lambda k: sizes[k])
    keep = [i for i in range(n) if comp[i] == main]
    re = {o: i for i, o in enumerate(keep)}
    return {"nodes": [g["nodes"][i] for i in keep],
            "edges": [[re[a], re[b], w] for a, b, w in g["edges"] if a in re and b in re]}


def node_graph(lines):
    """The walkable network: all lines noded where they cross; nodes merged within 0.05 m; edges carry a width."""
    geoms = []
    widths = []
    for l, w in lines:
        for g in getattr(l, "geoms", [l]):
            if g.geom_type == "LineString" and g.length > 0.05:
                geoms.append(g)
                widths.append(w)
    noded = unary_union(geoms)
    segs = list(getattr(noded, "geoms", [noded]))
    nodes, ix, edges = [], {}, []

    def nid(p):
        k = (round(p[0] / 0.05), round(p[1] / 0.05))
        if k not in ix:
            ix[k] = len(nodes)
            nodes.append([round(p[0], 2), round(p[1], 2)])
        return ix[k]
    tree = shapely.STRtree(geoms)
    for s in segs:
        cs = list(s.coords)
        mid = s.interpolate(0.5, normalized=True)
        # the widest source line under this piece gives its width
        cand = tree.query(mid.buffer(0.05))
        w = max([widths[i] for i in cand if geoms[i].distance(mid) < 0.05] or [PATH_W])
        for a, b in zip(cs, cs[1:]):
            ia, ib = nid(a), nid(b)
            if ia != ib:
                edges.append([ia, ib, w])
    return {"nodes": nodes, "edges": edges}


# ------------------------------------------------------------------ checks
def check(out, ctx):
    deck = ctx["deck"]
    fence = Polygon(out["fence"])
    rects = []
    for b in ctx["bout"]:
        r = box(*b["_rect"])
        assert fence.buffer(-1.0).contains(r), f"{b['id']} not inside the fence"
        for o in rects:
            assert r.intersection(o).area < 0.01, f"{b['id']} overlaps another lot"
        rects.append(r)
    for w in ctx["water"]:
        for r in rects:
            assert not r.intersects(w["poly"]), f"water under a building on {out['id']}"
    # every bridge, door and pad reaches the network: the graph is one connected piece holding them
    nodes = np.array(out["graph"]["nodes"])
    adj = {i: [] for i in range(len(nodes))}
    for a, b, _ in out["graph"]["edges"]:
        adj[a].append(b)
        adj[b].append(a)
    seen = {0}
    stack = [0]
    while stack:
        k = stack.pop()
        for j in adj[k]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    big = max(len(seen), 1)

    def reached(x, z, what):
        d = np.hypot(nodes[:, 0] - x, nodes[:, 1] - z)
        k = int(np.argmin(d))
        assert d[k] < 0.5 and k in seen, f"{out['id']}: {what} at ({x:.1f}, {z:.1f}) is off the path network ({d[k]:.2f} m)"
    for b in out["buildings"]:
        reached(*b["door"], b["id"] + " door")
    for br in out["bridges"]:
        f = out["faces"][br["side"]]
        x, z = (f, br["along"]) if br["side"] in "NS" else (br["along"], f)
        reached(x, z, f"bridge {br['side']}{br['along']}")
    assert len(seen) == len(nodes), f"{out['id']}: the path network falls in pieces ({len(seen)} of {len(nodes)} nodes)"
    assert len(out["pads"]) >= 2
    assert any(w["kind"] for w in out["water"]), f"{out['id']}: no pond"


# ------------------------------------------------------------------ meshes
ZONE = {"grass": (0.42, 0.55, 0.30), "pasture": (0.58, 0.62, 0.34), "wild": (0.30, 0.42, 0.24), "pen": (0.52, 0.42, 0.30),
        "lot": (0.55, 0.53, 0.50), "edge": (0.60, 0.58, 0.54), "bed": (0.30, 0.26, 0.20), "bank": (0.40, 0.34, 0.24)}


def deck_mesh(out, ctx, step):
    deck, H, gx, gz = ctx["deck"], ctx["H"], ctx["gx"], ctx["gz"]
    ext = deck.exterior
    ring = [ext.interpolate(d).coords[0] for d in np.arange(0, ext.length, step * 0.75)]
    inner = deck.buffer(-1.2)
    bx0, bz0, bx1, bz1 = deck.bounds
    gxs = np.arange(bx0, bx1, step)
    gzs = np.arange(bz0, bz1, step)
    GX, GZ = np.meshgrid(gxs, gzs)
    P = np.c_[GX.ravel(), GZ.ravel()]
    P = P[shapely.contains(inner, shapely.points(P[:, 0], P[:, 1]))]
    extra = []
    for w in ctx["water"] if step <= 4.0 else []:
        e = w["poly"].exterior
        extra += [e.interpolate(d).coords[0] for d in np.arange(0, e.length, 2.0)]
        e2 = w["poly"].buffer(-1.5)
        if not e2.is_empty and e2.geom_type == "Polygon":
            extra += [e2.exterior.interpolate(d).coords[0] for d in np.arange(0, e2.exterior.length, 3.0)]
    P = np.vstack([np.array(ring), P] + ([np.array(extra)] if extra else []))
    tri = Delaunay(P)
    T = tri.simplices
    cen = P[T].mean(axis=1)
    keep = shapely.contains(deck.buffer(0.01), shapely.points(cen[:, 0], cen[:, 1]))
    T = T[keep]
    y = sample(H, gx, gz, P[:, 0], P[:, 1])
    y[: len(ring)] = 0.0
    # colours by zone
    col = np.tile(np.array(ZONE["grass"]), (len(P), 1))
    pts = shapely.points(P[:, 0], P[:, 1])
    for p in ctx["pastures"]:
        k = "wild" if p["kind"] == "wild" else ("pen" if p["kind"] in ("pen", "coop") else "pasture")
        m = shapely.contains(p["poly"].buffer(0.5), pts)
        col[m] = ZONE[k]
    for b in ctx["bout"]:
        m = shapely.contains(box(*b["_rect"]).buffer(1.0), pts)
        col[m] = ZONE["lot"]
    for w in ctx["water"]:
        m = shapely.contains(w["poly"].buffer(1.2), pts)
        col[m] = ZONE["bank"]
        m = shapely.contains(w["poly"].buffer(-0.5), pts)
        col[m] = ZONE["bed"]
    d_edge = shapely.distance(pts, ext)
    col[d_edge < 1.6] = ZONE["edge"]
    jit = rng_np(out["id"], step).uniform(0.93, 1.05, (len(P), 1))
    col = np.clip(col * jit, 0, 1)
    V = np.c_[P[:, 0], y, P[:, 1]]
    # glTF winding: counter-clockwise seen from above (+Y): in (x, z) that is clockwise
    a, b_, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    up = np.cross(b_ - a, c - a)[:, 1]
    T = np.where((up > 0)[:, None], T, T[:, ::-1])
    return V, T.ravel(), col, ring


def rng_np(key, salt):
    return np.random.default_rng(int(hashlib.sha1(f"{key}:{salt}".encode()).hexdigest()[:8], 16))


def fbm(key, x, z, octaves=5, base=0.012):
    """smooth 2D noise in -1..1: summed sine waves at random headings (cheap, deterministic per island)"""
    g = rng_np(key, "fbm")
    out = np.zeros_like(np.asarray(x, float))
    amp, f, tot = 1.0, base, 0.0
    for _ in range(octaves):
        for _k in range(3):
            a = g.uniform(0, math.tau)
            out += amp * np.sin((np.cos(a) * x + np.sin(a) * z) * f * math.tau + g.uniform(0, math.tau))
            tot += amp
        amp *= 0.55
        f *= 2.1
    return out / tot * 2.2


def rock_mesh(out, ctx, ring, step, lip=1.6, ridges=True):
    """The underside: an upside-down mountain under the deck.  Over a grid of the deck's plan, the rock hangs
    -(lip + (depth - lip) * shape(u) * noise) below it, u the distance in from the edge over the deepest such
    distance -- so the keels and buttresses follow the island's own shape, and a noise field (with ridges) breaks it
    into several hanging peaks.  The edge ring drops straight down `lip` first (the deck's rim).  Strata in the
    colours, moss near the rim.  ring: the deck mesh's edge points (y = 0), in order."""
    deck = ctx["deck"]
    depth = ctx["depth"]
    key = out["id"]
    R = np.array(ring)
    n = len(R)
    inner = deck.buffer(-step * 0.6)
    bx0, bz0, bx1, bz1 = deck.bounds
    GX, GZ = np.meshgrid(np.arange(bx0, bx1, step), np.arange(bz0, bz1, step))
    P = np.c_[GX.ravel(), GZ.ravel()]
    if not inner.is_empty:
        P = P[shapely.contains(inner, shapely.points(P[:, 0], P[:, 1]))]
    else:
        P = P[:0]
    c = deck.representative_point()
    P = np.vstack([R, P, [[c.x, c.y]]])
    d = shapely.distance(shapely.points(P[:, 0], P[:, 1]), deck.exterior)
    d[:n] = 0.0
    u = np.clip(d / max(d.max(), 1.0), 0.0, 1.0)
    nz = fbm(key, P[:, 0], P[:, 1], base=1.0 / max(60.0, math.sqrt(deck.area) * 0.7))
    rid = 1.0 - np.abs(fbm(key + "r", P[:, 0], P[:, 1], octaves=3, base=1.0 / 45.0)) if ridges else 0.5
    shape = u ** 0.62
    y = -(lip + (depth - lip) * shape * np.clip(0.62 + 0.32 * nz + 0.22 * (rid - 0.5), 0.25, 1.35))
    y[:n] = -lip
    # a few boulders' worth of roughness, more lower down
    y += fbm(key + "b", P[:, 0], P[:, 1], octaves=3, base=1.0 / 9.0) * (0.4 + 2.2 * u)
    tri = Delaunay(P)
    T = tri.simplices
    cen = P[T].mean(axis=1)
    T = T[shapely.contains(deck.buffer(0.01), shapely.points(cen[:, 0], cen[:, 1]))]
    V = np.c_[P[:, 0], y, P[:, 1]]
    # facing down: in glTF (CCW front) the normal must point -Y
    a_, b_, c_ = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    dn = np.cross(b_ - a_, c_ - a_)[:, 1]
    T = np.where((dn < 0)[:, None], T, T[:, ::-1])
    # the rim: the deck's edge (y 0) straight down to the underside's edge ring (y -lip), pushed out a hand's width
    cx, cz = deck.centroid.x, deck.centroid.y
    off = len(V)
    top = np.c_[R[:, 0], np.zeros(n), R[:, 1]]
    V = np.vstack([V, top])
    side = []
    for i in range(n):
        j = (i + 1) % n
        side += [(off + i, i, off + j), (off + j, i, j)]
    side = np.array(side)
    a_, b_, c_ = V[side[:, 0]], V[side[:, 1]], V[side[:, 2]]
    nrm = np.cross(b_ - a_, c_ - a_)
    outw = np.c_[a_[:, 0] - cx, np.zeros(len(a_)), a_[:, 2] - cz]
    if (np.einsum("ij,ij->i", nrm, outw) < 0).mean() > 0.5:
        side = side[:, ::-1]
    T = np.vstack([T, side])
    # colours: strata by depth (wavy), darker in the hollows, moss green near the rim
    g = rng_np(key, "rockcol")
    strata = np.array([(0.47, 0.43, 0.38), (0.40, 0.37, 0.34), (0.53, 0.48, 0.41), (0.36, 0.33, 0.31),
                       (0.45, 0.41, 0.37), (0.50, 0.44, 0.36)])
    yy = V[:, 1] + fbm(key + "s", V[:, 0], V[:, 2], octaves=2, base=1.0 / 70.0) * 2.5
    C = strata[(np.floor(-yy / 3.2).astype(int)) % len(strata)]
    moss = np.clip(1.0 - (-V[:, 1] - lip) / 7.0, 0.0, 1.0) * np.clip(0.55 + 0.5 * fbm(key + "m", V[:, 0], V[:, 2], 3, 1 / 15.0), 0, 1)
    C = C * (1 - 0.6 * moss[:, None]) + np.array((0.27, 0.40, 0.19)) * 0.6 * moss[:, None]
    C = np.clip(C * g.uniform(0.9, 1.08, (len(C), 1)), 0, 1)
    return V, T.ravel(), C


def boxes_mesh(bout, roof=True):
    V, T, C = [], [], []
    for b in bout:
        m = MODEL[b["model"]]
        bc = np.array(body_color(m))
        x0, z0, x1, z1 = b["_rect"]
        # (the lot's building, not the whole lot: shrink by the passage and escape)
        x0, z0, x1, z1 = x0 + 1.5, z0 + 1.5, x1 - 1.5, z1 - 1.5
        y0, y1 = b["y"] - 0.5, b["y"] + b["h"]
        base = len(V)
        for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
            V.append((x, y0, z))
            C.append(bc * 0.85)
        for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
            V.append((x, y1, z))
            C.append(bc * 0.85)
        for i in range(4):
            j = (i + 1) % 4
            T += [(base + i, base + j, base + 4 + j), (base + i, base + 4 + j, base + 4 + i)]
        if roof:
            r = len(V)
            for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
                V.append((x, y1, z))
                C.append((0.42, 0.42, 0.42))
            T += [(r, r + 2, r + 1), (r, r + 3, r + 2)]
    if not V:
        return None
    V, T, C = np.array(V, float), np.array(T), np.array(C)
    # outward from each box: fix the winding per triangle against the box centre
    return V, T, C


def fix_boxes(V, T, bout):
    out = []
    T = T.reshape(-1, 3)
    per = 10 if True else 8
    for k, tri in enumerate(T):
        a, b_, c = V[tri]
        n = np.cross(b_ - a, c - a)
        bi = k // per
        bx = bout[bi]
        cx = (bx["_rect"][0] + bx["_rect"][2]) / 2
        cz = (bx["_rect"][1] + bx["_rect"][3]) / 2
        mid = (a + b_ + c) / 3
        o = mid - np.array((cx, bx["y"] + bx["h"] / 2, cz))
        if abs(n[1]) > 1e-6 and abs(n[0]) + abs(n[2]) < 1e-6:
            o = np.array((0, 1.0, 0))
        out.append(tri if np.dot(n, o) >= 0 else tri[::-1])
    return np.array(out).ravel()


def write_glbs(out, ctx):
    os.makedirs(GLB_DIR, exist_ok=True)
    sizes = {}
    tris = {}
    # rock: the full deck (collides) + the underside
    V, T, C, ring = deck_mesh(out, ctx, MESH_STEP)
    RV, RT, RC = rock_mesh(out, ctx, ring, 6.0)
    nodes = [{"name": "deck-col", "positions": V, "indices": T, "colors": C, "material": "sky_deck"},
             {"name": "rock", "positions": RV, "indices": RT, "colors": RC, "material": "sky_rock"}]
    sizes["rock"] = glb.write(os.path.join(GLB_DIR, out["id"] + ".rock.glb"), nodes)
    tris["rock"] = (len(T) + len(RT)) // 3
    # underside moss: points on the rock facing down, for hanging cards
    g = rng_np(out["id"], "under")
    nrm = glb.smooth_normals(RV, RT)
    down = np.where((nrm[:, 1] < -0.45) & (RV[:, 1] < -2.0))[0]
    if len(down):
        pick = g.choice(down, size=min(len(down), max(8, int(ctx["deck"].length / 8))), replace=False)
        out["moss"]["under"] = [[round(float(RV[i, 0]), 2), round(float(RV[i, 1]), 2), round(float(RV[i, 2]), 2),
                                 round(float(g.uniform(1.5, 9.0)), 1), "moss_b" if i % 3 else "vine_a"] for i in sorted(pick)]
    # lod1: coarse deck and rock, the buildings as boxes
    V1, T1, C1, ring1 = deck_mesh(out, ctx, 12.0)
    RV1, RT1, RC1 = rock_mesh(out, ctx, ring1, 18.0)
    nodes = [{"name": "deck", "positions": V1, "indices": T1, "colors": C1, "material": "sky_deck"},
             {"name": "rock", "positions": RV1, "indices": RT1, "colors": RC1, "material": "sky_rock"}]
    bm = boxes_mesh(ctx["bout"])
    nb = 0
    if bm:
        BV, BT, BC = bm
        BT = fix_boxes(BV, BT, ctx["bout"])
        nodes.append({"name": "buildings", "positions": BV, "indices": BT, "colors": BC, "material": "sky_lod_bldg"})
        nb = len(BT) // 3
    sizes["lod1"] = glb.write(os.path.join(GLB_DIR, out["id"] + ".lod1.glb"), nodes)
    tris["lod1"] = (len(T1) + len(RT1)) // 3 + nb
    # lod2: the outline cut to ~28 points, a fan deck, three rings of rock, the tallest buildings
    simp = ctx["deck"].simplify(max(2.0, math.sqrt(ctx["deck"].area) / 14), preserve_topology=True)
    ring2 = [c for c in simp.exterior.coords][:-1]
    if Polygon(ring2).exterior.is_ccw != ctx["deck"].exterior.is_ccw:
        pass
    # keep the ring's direction as the deck mesh ring's (both walk the exterior the same way)
    P = np.array(ring2)
    cen = ctx["deck"].centroid
    V2 = np.vstack([np.c_[P[:, 0], np.zeros(len(P)), P[:, 1]], [[cen.x, 0.0, cen.y]]])
    n = len(P)
    T2 = np.array([(i, (i + 1) % n, n) for i in range(n)])
    a, b_, c = V2[T2[:, 0]], V2[T2[:, 1]], V2[T2[:, 2]]
    if (np.cross(b_ - a, c - a)[:, 1] < 0).mean() > 0.5:
        T2 = T2[:, ::-1]
    C2 = np.tile(np.array(ZONE["grass"]), (len(V2), 1))
    RV2, RT2, RC2 = rock_mesh(out, ctx, ring2, max(30.0, math.sqrt(ctx["deck"].area) / 4.5), ridges=False)
    nodes = [{"name": "deck", "positions": V2, "indices": T2.ravel(), "colors": C2, "material": "sky_deck"},
             {"name": "rock", "positions": RV2, "indices": RT2, "colors": RC2, "material": "sky_rock"}]
    tallest = sorted(ctx["bout"], key=lambda b: -b["h"])[:8]
    bm = boxes_mesh(tallest, roof=True)
    nb2 = 0
    if bm:
        BV, BT, BC = bm
        BT = fix_boxes(BV, BT, tallest)
        nodes.append({"name": "buildings", "positions": BV, "indices": BT, "colors": BC, "material": "sky_lod_bldg"})
        nb2 = len(BT) // 3
    sizes["lod2"] = glb.write(os.path.join(GLB_DIR, out["id"] + ".lod2.glb"), nodes)
    tris["lod2"] = len(T2) + len(RT2) // 3 + nb2
    return sizes, tris


# ------------------------------------------------------------------ previews
def preview(out, ctx, path):
    from PIL import Image, ImageDraw
    deck = ctx["deck"]
    x0, z0, x1, z1 = deck.bounds
    pad = 40
    S = 3.0 if max(x1 - x0, z1 - z0) < 250 else 2.0
    W, Hh = int((z1 - z0) * S) + 2 * pad, int((x1 - x0) * S) + 2 * pad
    im = Image.new("RGB", (W, Hh), (150, 180, 215))
    d = ImageDraw.Draw(im)

    # drawn with north (-X) up and east (-Z) to the right: screen x = (z1 - z) , screen y = (x - x0)
    def P(x, z):
        return (pad + (z1 - z) * S, pad + (x - x0) * S)

    def poly(pts, **kw):
        if len(pts) > 2:
            d.polygon([P(*p) for p in pts], **kw)
    poly(out["outline"], fill=(110, 140, 80), outline=(60, 50, 40))
    for p in out["pastures"]:
        col = {"pasture": (170, 180, 90), "pen": (150, 120, 80), "coop": (190, 150, 90), "wild": (60, 100, 50)}[p["kind"]]
        o = p["outline"]
        for q in (o if o and isinstance(o[0][0], list) else [o]):
            poly(q, fill=col)
    for w in out["water"]:
        poly(w["outline"], fill=(70, 120, 180), outline=(40, 70, 110))
    for l in out["roads"]:
        d.line([P(*p) for p in l], fill=(80, 80, 80), width=max(1, int(ROAD_W * S)))
    for l in out["paths"] + [out["promenade"]]:
        d.line([P(*p) for p in l], fill=(205, 190, 160), width=max(1, int(PATH_W * S)))
    nodes = out["graph"]["nodes"]
    for a, b, w in out["graph"]["edges"]:
        if w < 2.0:
            d.line([P(*nodes[a]), P(*nodes[b])], fill=(220, 205, 170), width=max(1, int(1.6 * S)))
    d.line([P(*p) for p in out["fence"]], fill=(40, 40, 40), width=1)
    for b in ctx["bout"]:
        x0_, z0_, x1_, z1_ = b["_rect"]
        m = MODEL[b["model"]]
        bc = tuple(int(c * 255) for c in body_color(m))
        q = [P(x0_ + 1.5, z0_ + 1.5), P(x1_ - 1.5, z1_ - 1.5)]
        d.rectangle([min(q[0][0], q[1][0]), min(q[0][1], q[1][1]), max(q[0][0], q[1][0]), max(q[0][1], q[1][1])], fill=bc,
                    outline=(30, 30, 30))
        d.ellipse([P(*b["door"])[0] - 2, P(*b["door"])[1] - 2, P(*b["door"])[0] + 2, P(*b["door"])[1] + 2], fill=(200, 30, 30))
    for p in out["pads"]:
        c = P(p["x"], p["z"])
        r = PAD_R * S
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(240, 200, 40), width=2)
    for br in out["bridges"]:
        f = out["faces"][br["side"]]
        x, z = (f, br["along"]) if br["side"] in "NS" else (br["along"], f)
        o = {"N": (-13, 0), "S": (13, 0), "E": (0, -13), "W": (0, 13)}[br["side"]]
        d.line([P(x, z), P(x + o[0], z + o[1])], fill=(120, 70, 30), width=max(2, int(br["width"] * S)))
    for h in out["hoists"]:
        c = P(h["x"], h["z"])
        d.rectangle([c[0] - 4, c[1] - 4, c[0] + 4, c[1] + 4], fill=(30, 30, 160))
    for h in out["launchers"]:
        c = P(h["x"], h["z"])
        d.polygon([(c[0], c[1] - 5), (c[0] - 4, c[1] + 4), (c[0] + 4, c[1] + 4)], fill=(200, 60, 160))
    for b in out["balloons"]:
        c = P(b["x"], b["z"])
        r = 50 * S
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(255, 255, 255), width=1)
        a = P(b["anchor"][0], b["anchor"][2])
        d.line([c, a], fill=(255, 255, 255), width=1)
    for s in out["animal_spawns"]:
        c = P(s[0], s[1])
        d.ellipse([c[0] - 1.5, c[1] - 1.5, c[0] + 1.5, c[1] + 1.5], fill=(255, 120, 0) if len(s) == 3 else (255, 0, 255))
    d.text((6, 6), f"{out['id']} {out['name']}  {out['blocks']} blocks  pop {out['population']}  "
                   f"{len(out['buildings'])} buildings   N up, E right", fill=(0, 0, 0))
    im.save(path)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--no-glb", action="store_true")
    ap.add_argument("--previews", nargs="*", help="ids to draw to research/sky_islands/img/<id>.png")
    a = ap.parse_args()
    canon = json.load(open(CANON))
    isls = canon["islands"]
    if a.ids:
        isls = [i for i in isls if i["id"] in a.ids]
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, "islands.json")
    old = {}
    if a.ids and os.path.exists(path):
        old = {i["id"]: i for i in json.load(open(path))["islands"]}
    t0 = time.time()
    tot = {"buildings": 0, "rock": 0, "lod1": 0, "lod2": 0, "tri_rock": 0, "tri_lod1": 0, "tri_lod2": 0}
    uses = {}
    models = {}
    for isl in isls:
        out, ctx = layout(isl)
        if not a.no_glb:
            sz, tr = write_glbs(out, ctx)
            for k in sz:
                tot[k] += sz[k]
                tot["tri_" + k] += tr[k]
        if a.previews is not None and (not a.previews or isl["id"] in a.previews):
            os.makedirs(IMG, exist_ok=True)
            preview(out, ctx, os.path.join(IMG, isl["id"] + ".png"))
        tot["buildings"] += len(out["buildings"])
        for b in out["buildings"]:
            uses[b["use"]] = uses.get(b["use"], 0) + 1
            models[b["model"]] = models.get(b["model"], 0) + 1
        old[isl["id"]] = out
        cap = sum(b["homes"] for b in out["buildings"]) * 2.6
        out["housing"] = {"homes": sum(b["homes"] for b in out["buildings"]), "per_home": round(isl["population"] / max(1, cap / 2.6), 2)}
        print(f"{isl['id']} {isl['name']:<18} {isl['blocks']:>2} blk  {len(out['buildings']):>3} bldg  "
              f"{len(out['bridges'])} br  {len(out['balloons']):>2} bal  {len(out['water'])} water  "
              f"{len(out['animal_spawns']):>3} animals", flush=True)
    allisl = [old[k] for k in sorted(old)]
    with open(path, "w") as f:
        json.dump({"version": 1, "generated": "tools/sky/make_islands.py", "contract": "research/sky_islands/00_plan.md",
                   "parts": PARTS, "bridge_styles": "res://remake/sky/bridges/bridge_styles.json",
                   "models": {m["id"]: {"use": m["sky"]["use"], "kind": m["kind"], "w": m["lot"]["w"], "d": m["lot"]["d"],
                                        "h": round(model_dims(m)[2], 2), "roof": round(roof_top(m), 2),
                                        "storeys": m["traits"]["storeys"],
                                        "glb": "res://remake/buildings/%s.glb" % m["id"]} for m in MODELS},
                   "islands": allisl}, f, separators=(",", ":"))
    print(f"{len(isls)} islands in {time.time() - t0:.0f} s: {tot['buildings']} buildings; uses {uses}")
    print(f"glbs: rock {tot['rock'] / 1e6:.1f} MB ({tot['tri_rock']} tris), lod1 {tot['lod1'] / 1e6:.1f} MB "
          f"({tot['tri_lod1']} tris), lod2 {tot['lod2'] / 1e6:.2f} MB ({tot['tri_lod2']} tris)")
    print(f"islands.json {os.path.getsize(path) / 1e6:.1f} MB; models used: {len(models)} of {len(MODELS)}")


if __name__ == "__main__":
    main()
