#!/usr/bin/env python3
"""street_lamps.py -- street lighting for the ring floor (research/night/00_brief.md).

The user, 2026-10-14: "The towns need streetlights. the south coast towns need colored lights in the trees by the beach
and on the street along the beach ... There needs to be good artificial illumination on the streets and in the cities and
town centers. All streets with buildsings need lights."

Reads terrain.json (roads, areas), road_furniture.json (per-point context r/t/c, junctions, overlaps; signs and masts to
keep clear of), placement.json (buildings) and walks.json, and writes godot_project/remake/street_lamps.json:

  lamps    [s, x, yaw, kind] * n    a post every SPACING m on every street with buildings within BUILT_R m (both sides
                                    staggered on wide roads, alternating on narrow ones), behind the kerb (in the tree
                                    lawn or at the kerb edge of the sidewalk), its arm reaching over the road (yaw: the
                                    arm, local -z, faces the road -- placement.py's convention).  kind 0 street (cobra
                                    head), 1 town-centre ornamental (closer, warmer, brighter), 2 alley (short), 3 the
                                    beach street's (south coast)
  strings  [s0, x0, h0, s1, x1, h1, scheme] * n   festoons: across the town centres' main streets (scheme 2), along
                                    the south coast's beach streets and promenades (scheme 1, multicolour)
  palms    [s, x, yaw, scale] * n   palms along the south coast's beach streets and promenades, their crowns wrapped in
                                    coloured lights (there are no trees by those beaches: the cover there is all town)

    ~/.venvs/ssc-assets/bin/python tools/street_lamps.py         (after road_furniture.py; then tools/pack_data.py)
Deterministic.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from where import World, point_in  # noqa: E402

GD = os.path.join(HERE, "..", "godot_project", "remake")
OUT = os.path.join(GD, "street_lamps.json")

BUILT_R = 40.0                 # m: a street with a building this near is lit
SPACING = {0: 30.0, 1: 22.0, 2: 34.0, 3: 24.0}
MIN_GAP = 9.0                  # m between any two lamps (parallel roads, junctions)
SIGN_CLEAR = 1.4               # m from a sign post or mast
SOUTH = ("Playa Verde", "Oceanview", "Solana Point", "Pelican Cove")
BEACH_R = 140.0                # m: a street this near a south beach is the beach street
FESTOON_EVERY = 36.0           # m along a centre's main street between strings across it
PALM_EVERY = 13.0

W = World()
R, C = W.R, W.C
T = W.ter
F = json.load(open(os.path.join(GD, "road_furniture.json")))
ROADS = T["roads"]


def wd(a):
    return (a + C / 2) % C - C / 2


def dist(a, b):
    return math.hypot(wd(b[0] - a[0]), b[1] - a[1])


def yaw_facing(f):
    return math.atan2(-f[1], f[0])


# ------------------------------------------------------------------ indexes
G = 20.0


class Grid:
    def __init__(self):
        self.g = {}

    def key(self, p):
        return (int((p[0] % C) // G), int(math.floor(p[1] / G)))

    def add(self, p, v=None):
        self.g.setdefault(self.key(p), []).append((p, v))

    def near(self, p, r):
        ci, cj = self.key(p)
        n = int(math.ceil(r / G))
        ncol = int(math.ceil(C / G))
        for di in range(-n, n + 1):
            for dj in range(-n, n + 1):
                for q, v in self.g.get(((ci + di) % ncol, cj + dj), ()):
                    if dist(p, q) <= r:
                        yield q, v


posts = Grid()
for sg in F["signs"]:
    posts.add((sg["s"], sg["x"]))
for key in ("signals", "xings"):
    for e in F[key]:
        for m in e.get("masts", []):
            posts.add((m[0], m[1]))

STRUCT = [e for e in W.st if e.get("kind") != "crossing"]
FOOT = Grid()
for e in STRUCT:
    FOOT.add((e["s"], e["x"]), e)

lamp_grid = Grid()

# the town centres: each settlement's middle (its structures' mean), out to a radius by its size -- and the plazas and
# squares, wherever they are
TOWNS = {}
for e in STRUCT:
    if e.get("settlement"):
        TOWNS.setdefault(e["settlement"], []).append(e)
CENTRES = []
for t, es in TOWNS.items():
    cs = sum(math.cos(e["s"] / R) for e in es)
    sn = sum(math.sin(e["s"] / R) for e in es)
    CENTRES.append(((math.atan2(sn, cs) % (2 * math.pi)) * R, sum(e["x"] for e in es) / len(es), 90.0 + 2.2 * math.sqrt(len(es))))
for a in T["areas"]:
    if a.get("kind") in ("square", "plaza"):
        xs = [q[1] for q in a["poly"]]
        ss = [a["poly"][0][0] + wd(q[0] - a["poly"][0][0]) for q in a["poly"]]
        CENTRES.append((sum(ss) / len(ss) % C, sum(xs) / len(xs), 110.0))


def in_centre(p, cls, ctx):
    if cls == "main" and ctx == "c":
        return True
    return any(dist(p, (c[0], c[1])) < c[2] for c in CENTRES if abs(wd(p[0] - c[0])) < 800)

SBEACH = [a for a in T["areas"] if a.get("kind") == "beach" and a.get("town") in SOUTH]
BEACH_C = []
for a in SBEACH:
    xs = [p[1] for p in a["poly"]]
    cs = sum(math.cos(p[0] / R) for p in a["poly"])
    sn = sum(math.sin(p[0] / R) for p in a["poly"])
    BEACH_C.append(((math.atan2(sn, cs) % (2 * math.pi)) * R, sum(xs) / len(xs), a))


def near_beach(p):
    """the south beach area within BEACH_R of p (its polygon's nearest vertex), or None"""
    for c in BEACH_C:
        if abs(wd(p[0] - c[0])) > 3000:
            continue
        for q in c[2]["poly"][::3]:
            if dist(p, q) < BEACH_R:
                return c
    return None


def in_building(p, pad=0.6):
    for q, e in FOOT.near(p, 40.0):
        fp = W.footprint(e, -pad)
        if point_in(W, p, fp):
            return True
    return False


def buildings_within(p, r):
    return sum(1 for _ in FOOT.near(p, r))


def in_carriageway(p, margin=0.5):
    for d, hw, name, cls in W.roads_near(p[0], p[1], 14.0, sided=True):
        if d < hw + margin:
            return True
    return False


def clear_spot(p):
    return not any(True for _ in posts.near(p, SIGN_CLEAR)) and not any(True for _ in lamp_grid.near(p, MIN_GAP)) \
        and not in_carriageway(p) and not in_building(p)


# ------------------------------------------------------------------ the lamps
lamps = []
strings = []
palms = []
beach_roads = set()


def walk_road(ri):
    """[(point, tangent, k)] every 1 m along road ri"""
    pts = ROADS[ri]["pts"]
    out = []
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        L = dist(a, b)
        if L < 1e-6:
            continue
        t = (wd(b[0] - a[0]) / L, (b[1] - a[1]) / L)
        n = max(1, int(L))
        for i in range(n):
            f = i / n
            out.append(((a[0] + wd(b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), t, k))
    return out


n_seen = 0
for ri, rd in enumerate(ROADS):
    cls = rd["cls"]
    ctxs = F["ctx"][ri]
    dups = F["dup"][ri]
    jns = F["jn"][ri]
    pts = rd["pts"]
    if len(pts) < 2:
        continue
    alley = cls == "alley"
    wide = cls in ("main", "county", "hwy") or float(rd.get("w", 6)) >= 11.0
    beach = rd.get("city") is not None and any(near_beach(p) for p in pts[::max(1, len(pts) // 6)]) and cls != "alley"
    if beach:
        beach_roads.add(ri)
    hl = float(rd.get("hl", rd["w"] * 0.5))
    hr = float(rd.get("hr", rd["w"] * 0.5))
    lawn = float(rd.get("lawn", 0.0) or 0.0)
    back = lawn * 0.5 if lawn > 0.8 else 0.6
    run = 0.0
    nxt = {1: 0.0, -1: 0.0}                  # per side: the distance along at which it next wants a lamp
    if wide:
        nxt[-1] = 0.5 * 26.0                 # (staggered)
    side = 1
    for p, t, k in walk_road(ri):
        run += 1.0
        if dups[min(k, len(dups) - 1)] == "1":
            continue                         # (junctions are lit too: clear_spot keeps a post out of every carriageway)
        ctx = ctxs[min(k, len(ctxs) - 1)]
        kind = 2 if alley else (3 if beach else (1 if ctx != "r" and in_centre(p, cls, ctx) else 0))
        sp = SPACING[kind]
        for sd in ((1, -1) if wide else (side,)):
            if run < nxt[sd]:
                continue
            nb = buildings_within(p, BUILT_R)
            if not beach and (nb == 0 or (ctx == "r" and nb < 2)):      # (a beach street is lit end to end)
                nxt[sd] = run + 6.0
                continue
            nrm = (-t[1] * sd, t[0] * sd)                     # sd 1: the right of travel along the points
            half = hr if sd == 1 else hl
            ok = None
            for extra in (0.0, 0.8, 1.6):
                q = (p[0] + nrm[0] * (half + back + extra), p[1] + nrm[1] * (half + back + extra))
                if clear_spot(q):
                    ok = q
                    break
            if ok is None:
                nxt[sd] = run + 3.0                           # (try a little further on)
                continue
            lamps.append([round(ok[0] % C, 2), round(ok[1], 2), round(yaw_facing((-nrm[0], -nrm[1])), 3), kind])
            lamp_grid.add(ok)
            nxt[sd] = run + sp
            if not wide:
                side = -side
                nxt[side] = run + sp
            n_seen += 1

# ------------------------------------------------------------------ festoons across the town centres' main streets
for ri, rd in enumerate(ROADS):
    if rd["cls"] not in ("main", "county", "street") or float(rd.get("w", 6)) < 9.0:
        continue
    ctxs = F["ctx"][ri]
    hl = float(rd.get("hl", rd["w"] * 0.5))
    hr = float(rd.get("hr", rd["w"] * 0.5))
    run, nx = 0.0, FESTOON_EVERY * 0.5
    for p, t, k in walk_road(ri):
        run += 1.0
        if run < nx or ctxs[min(k, len(ctxs) - 1)] == "r" or F["jn"][ri][min(k, len(F["jn"][ri]) - 1)] == "1":
            continue
        if not in_centre(p, rd["cls"], ctxs[min(k, len(ctxs) - 1)]):
            continue
        if buildings_within(p, 30.0) < 3:
            continue
        a = (p[0] - t[1] * (hr + 0.8), p[1] + t[0] * (hr + 0.8))
        b = (p[0] + t[1] * (hl + 0.8), p[1] - t[0] * (hl + 0.8))
        if in_building(a) or in_building(b):
            continue
        strings.append([round(a[0] % C, 2), round(a[1], 2), 6.6, round(b[0] % C, 2), round(b[1], 2), 6.6, 2])
        nx = run + FESTOON_EVERY

# ------------------------------------------------------------------ the south coast: beach streets and promenades
def beach_side(p, t, c):
    """+1 if the beach lies to the right of travel along t at p, else -1"""
    v = (wd(c[0] - p[0]), c[1] - p[1])
    return 1 if (-t[1]) * v[0] + t[0] * v[1] > 0 else -1


for ri in sorted(beach_roads):
    rd = ROADS[ri]
    hl = float(rd.get("hl", rd["w"] * 0.5))
    hr = float(rd.get("hr", rd["w"] * 0.5))
    prev = None
    run, nxt_f, nxt_p = 0.0, 0.0, 6.0
    for p, t, k in walk_road(ri):
        run += 1.0
        c = near_beach(p)
        if c is None:
            prev = None
            continue
        sd = beach_side(p, t, c)
        half = hr if sd == 1 else hl
        nrm = (-t[1] * sd, t[0] * sd)
        if run >= nxt_f:
            q = (p[0] + nrm[0] * (half + 1.2), p[1] + nrm[1] * (half + 1.2))
            if not in_carriageway(q, 0.3) and not in_building(q):
                if prev is not None and dist(prev, q) < 16.0:
                    strings.append([round(prev[0] % C, 2), round(prev[1], 2), 5.2, round(q[0] % C, 2), round(q[1], 2), 5.2, 1])
                prev = q
            else:
                prev = None
            nxt_f = run + 12.0
        if run >= nxt_p:
            q = (p[0] + nrm[0] * (half + 3.6), p[1] + nrm[1] * (half + 3.6))
            if not in_carriageway(q, 1.5) and not in_building(q, 1.5) and not any(True for _ in posts.near(q, 2.5)):
                h = (int(q[0] * 7.0) * 2654435761 + int(q[1] * 3.0) * 40503) % 1000 / 1000.0
                palms.append([round(q[0] % C, 2), round(q[1], 2), round(h * 6.283, 2), round(0.85 + 0.35 * h, 2)])
            nxt_p = run + PALM_EVERY

for wk in W.walks:
    if wk.get("settlement") not in SOUTH or wk.get("kind") not in ("promenade", "boardwalk"):
        continue
    pts = wk.get("pts") or []
    if len(pts) < 2:
        continue
    half = float(wk.get("w", 6.0)) * 0.5
    for sd in (1, -1):
        prev, run, nxt_f, nxt_p = None, 0.0, 0.0, 7.0
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            L = dist(a, b)
            if L < 1e-6:
                continue
            t = (wd(b[0] - a[0]) / L, (b[1] - a[1]) / L)
            nrm = (-t[1] * sd, t[0] * sd)
            for i in range(int(L)):
                p = (a[0] + t[0] * i, a[1] + t[1] * i)
                run += 1.0
                if run >= nxt_f:
                    q = (p[0] + nrm[0] * (half - 0.4), p[1] + nrm[1] * (half - 0.4))
                    if prev is not None and dist(prev, q) < 16.0:
                        strings.append([round(prev[0] % C, 2), round(prev[1], 2), 4.4, round(q[0] % C, 2), round(q[1], 2), 4.4, 1])
                    prev = q
                    nxt_f = run + 10.0
                if sd == 1 and run >= nxt_p:
                    q = (p[0] + nrm[0] * (half + 2.5), p[1] + nrm[1] * (half + 2.5))
                    if not in_carriageway(q, 1.5) and not in_building(q, 1.5):
                        h = (int(q[0] * 5.0) * 2654435761 + int(q[1] * 11.0) * 40503) % 1000 / 1000.0
                        palms.append([round(q[0] % C, 2), round(q[1], 2), round(h * 6.283, 2), round(0.9 + 0.3 * h, 2)])
                    nxt_p = run + PALM_EVERY

# ------------------------------------------------------------------ the coastal walks' own lamp posts (CoastalWalks.gd
# draws them: a post every 24 m from 12 m in, alternating sides, hw - 0.3 out; a deck's at its 4 corners): their places,
# for the bulbs, pools and real lights (heights: CoastalWalks._deck_z at run time)
WKINDS = []
walk_lamps = []
for wk in W.walks:
    if (wk.get("traits") or {}).get("lighting") != "lamp_posts":
        continue
    kd = str(wk.get("kind"))
    if kd not in WKINDS:
        WKINDS.append(kd)
    ki = WKINDS.index(kd)
    hw = float(wk.get("w", 4.0)) * 0.5
    if wk.get("pts"):
        pts = wk["pts"]
        run, nxt = 0.0, 12.0
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            L = dist(a, b)
            if L < 1e-6:
                continue
            t = (wd(b[0] - a[0]) / L, (b[1] - a[1]) / L)
            while nxt <= run + L:
                f = (nxt - run) / L
                c = (a[0] + wd(b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                sgn = 1.0 if int(nxt / 24.0) % 2 == 0 else -1.0
                q = (c[0] - t[1] * (hw - 0.3) * sgn, c[1] + t[0] * (hw - 0.3) * sgn)
                if not in_carriageway(q, 0.2):
                    walk_lamps.append([round(q[0] % C, 2), round(q[1], 2), ki])
                nxt += 24.0
            run += L
    elif wk.get("rect"):
        r = wk["rect"]
        hs, hx = float(r[2]) * 0.5, float(r[3]) * 0.5
        for ks, kx in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            walk_lamps.append([round((r[0] + (hs - 0.5) * ks) % C, 2), round(r[1] + (hx - 0.5) * kx, 2), ki])

# ------------------------------------------------------------------ car parks: lot poles (kind 5, research/flea_markets/
# 00_plan.md §1.4, §3.6: a 9 m pole with 1-4 heads, ~24 m apart, lit dusk to dawn) on every lot -- the flea markets' from
# their own pole plans (flea_markets.json), every other lot (downtown, park & ride: unlit until now) along its rows'
# backs; and the markets' aisle festoons (scheme 4, market warm, 4.2 m)
FM_P = os.path.join(GD, "markets", "flea_markets.json")
FM = [m for m in json.load(open(FM_P))["markets"] if m.get("sited")] if os.path.exists(FM_P) else []
n_lot = 0
for m in FM:
    f = m["frame"]
    ca, sa = math.cos(f["yaw"]), math.sin(f["yaw"])
    at = lambda u, v, f=f, ca=ca, sa=sa: ((f["s"] + u * ca - v * sa) % C, f["x"] + u * sa + v * ca)
    for u, v, heads in m["poles"]:
        q = at(u, v)
        lamps.append([round(q[0], 2), round(q[1], 2), round(f["yaw"], 3), 5])
        n_lot += 1
    for u0, v0, u1, v1, h, sch in m["festoons"]:
        a, b = at(u0, v0), at(u1, v1)
        strings.append([round(a[0], 2), round(a[1], 2), h, round(b[0], 2), round(b[1], 2), h, sch])
    if m.get("pier"):
        # a floating pier: its aisles' strings at an absolute height (StreetLights ABS_H: over the water, not the bed)
        dh = float(m["pier"]["deck_h"])
        for u0, v0, u1, v1, h, sch in m.get("pier_festoons", []):
            a, b = at(u0, v0), at(u1, v1)
            ah = round(100000.0 + dh + h, 2)
            strings.append([round(a[0], 2), round(a[1], 2), ah, round(b[0], 2), round(b[1], 2), ah, sch])
            n_lot += 0
for A in T["areas"]:
    lt = A.get("lot")
    if not lt or lt.get("type") == "market":
        continue
    c, u = lt["centre"], lt["dir"]
    n_ = (-u[1], u[0])
    W_, D_ = float(lt.get("w", 44.0)), float(lt.get("d", 36.6))
    nu = max(2, int(round((W_ - 6.0) / 24.0)) + 1)
    for b_ in (-D_ / 2 + 1.0, 0.0, D_ / 2 - 1.0):
        for k in range(nu):
            a_ = -W_ / 2 + 3.0 + k * (W_ - 6.0) / (nu - 1)
            q = (c[0] + u[0] * a_ + n_[0] * b_, c[1] + u[1] * a_ + n_[1] * b_)
            if not in_building(q, 1.0):
                lamps.append([round(q[0] % C, 2), round(q[1], 2), round(math.atan2(u[1], u[0]), 3), 5])
                n_lot += 1
print("lot poles %d (%d markets)" % (n_lot, len(FM)))

flat = lambda rows: [v for r in rows for v in r]  # noqa: E731
json.dump({"version": 1, "lamps": flat(lamps), "strings": flat(strings), "palms": flat(palms), "walk_lamps": flat(walk_lamps), "walk_kinds": WKINDS,
           "kinds": {"0": "street", "1": "centre", "2": "alley", "3": "beach", "5": "lot pole"},
           "schemes": {"1": "beach multicolour", "2": "town-centre warm festoon", "4": "market warm"}},
          open(OUT, "w"), separators=(",", ":"))
from collections import Counter  # noqa: E402
print("walk lamps %d" % len(walk_lamps))
print("lamps %d by kind %s; strings %d (%s); palms %d; beach roads %d -> %s (%.1f MB)" % (
    len(lamps), dict(Counter(l[3] for l in lamps)), len(strings), dict(Counter(s[6] for s in strings)), len(palms),
    len(beach_roads), OUT, os.path.getsize(OUT) / 1e6))
