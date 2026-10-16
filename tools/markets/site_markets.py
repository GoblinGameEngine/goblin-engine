#!/usr/bin/env python3
"""
site_markets.py -- every town's flea market sited on its outskirts, inside its limits (research/flea_markets/00_plan.md
§1.1-1.4, §3), on the map as it stands: a post-pass over the game data, so the map stays the layout authority and the
plans, the catalog and the inventory are left alone.

    ~/.venvs/ssc-assets/bin/python tools/markets/site_markets.py [--only Calder,Pruett] [--dry]

Reads  godot_project/remake/terrain.json (roads, rail, areas), placement.json (every structure's footprint),
       terrain_base_raw.bin.gz (the natural ground), terrain_level.bin.gz (water), landcover.png (woods),
       characters/npc_place_index.json (schools and hospitals), law/settlements.json, tools/settlegen/towns.py.
Writes terrain.json: the market areas -- "parking" (with a "lot" record, type "market": road_furniture paints its
       stalls, street_lamps lights it, NpcTraffic parks in its rows), "market_floor" (paved), "market_apron" and
       "mooring_field" (lawn) -- and each market's access drive as a town street ("market": id). Idempotent: the
       areas and drives it made before are taken out first.
       godot_project/remake/markets/flea_markets.json (tools/markets/make_markets.py), with each market's limits.

The search (00 §1.1; the industrial-park pass, tools/settlegen/city.py _jobs_pass, as its model):
  * the limits: the ellipse (u/U)^2 + (v/V)^2 <= 1 round the town's heart, U, V the plan's reach (city.py plan_city);
    the outskirts r = hypot(u/U, v/V) in [0.60, 0.95] (villages 0.50) -- the whole site inside r 0.95;
  * a 40 m candidate grid, sorted by |r - 0.78| plus a little for the leeward (-s) side, a hashed jitter;
  * two orientations: the site's front facing the town's middle across x, or along s;
  * the whole site free in a 2 m raster of every road (its full right of way), the rail, every structure (+3 m),
    every area, woods and water; dry; the lot and floor no steeper than 4 %;
  * >= 250 m from any school or hospital; an access drive of <= 260 m to a main road (or <= 140 m to any town
    street), itself on free ground;
  * if no candidate fits, the stalls step down 15 % (at most 3 times) -- else the market is reported "no_site".
"""
import gzip
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "settlegen"))
import markets_spec as MS  # noqa: E402
import market_layout as ML  # noqa: E402
import make_markets as MM  # noqa: E402

GD = os.path.join(ROOT, "godot_project", "remake")
CELL = 2.0
GRID = 40.0
R_OUT = 1.0                 # (the whole site inside the limits; its centre r <= R_CEN)
R_CEN = 0.95
R_IN = {"city": 0.60, "town": 0.60, "village": 0.50}
R_BEST = 0.78
SLOPE_MAX = 0.04
SCHOOL_CLEAR = 250.0
DRIVE_MAIN = 260.0
DRIVE_ANY = 140.0
STEP_DOWN = (1.0, 0.85, 0.72, 0.61)
ROW_EXTRA = {"hwy": 12.0, "county": 8.0, "main": 6.0, "street": 4.0, "alley": 2.0, "gravel": 4.0}


def wrap(d, C):
    return (d + C / 2) % C - C / 2


LIMIT_P = 4.0               # the limits' superellipse exponent (2 = the plan's inscribed ellipse; 4 = a rounded box)


def rnorm(u, v, U, V):
    """the normalised radius of the city limits: 1 on the limit line (|u/U|^p + |v/V|^p = 1)"""
    return (abs(u / U) ** LIMIT_P + abs(v / V) ** LIMIT_P) ** (1.0 / LIMIT_P)


class World:
    def __init__(self):
        self.ter = json.load(open(os.path.join(GD, "terrain.json")))
        self.C = 2 * math.pi * self.ter["R"]
        rs = self.ter["raster"]
        self.nx, self.ny, self.step, self.x0 = rs["nx"], rs["ny"], rs["step_m"], rs["x0"]
        raw = os.path.join(GD, "terrain_base_raw.bin.gz")
        self.base = np.frombuffer(gzip.open(raw if os.path.exists(raw) else os.path.join(GD, rs["base"])).read(), np.float16).reshape(self.ny, self.nx)
        self.level = np.frombuffer(gzip.open(os.path.join(GD, rs["level"])).read(), np.float16).reshape(self.ny, self.nx)
        lc = Image.open(os.path.join(GD, "landcover.png"))
        self.lc = np.asarray(lc)[:, :, 0]
        self.lc_step = self.ter.get("landcover_step_m", 8.0)
        self.structs = json.load(open(os.path.join(GD, "placement.json")))["structures"]
        wp = os.path.join(GD, "walks.json")
        self.walks = json.load(open(wp)).get("walks", []) if os.path.exists(wp) else []
        self.law = {s["name"]: s for s in json.load(open(os.path.join(GD, "law", "settlements.json")))["settlements"]}
        units = json.load(open(os.path.join(GD, "characters", "npc_place_index.json")))["units"]
        crowd = {u["building"] for u in units if u.get("type") in ("school", "college", "hospital", "childcare")}
        self.crowd = [(e["s"], e["x"]) for e in self.structs if e["id"] in crowd or e["kind"] == "school"]
        # take out what an earlier run made
        self.ter["areas"] = [a for a in self.ter["areas"] if not a.get("market")]
        self.ter["roads"] = [r for r in self.ter["roads"] if not r.get("market")]

    def footprint(self, e, pad=3.0):
        c, s_ = math.cos(e["yaw"]), math.sin(e["yaw"])
        out = []
        for lx, lz in ((e["fmin"][0] - pad, e["fmin"][1] - pad), (e["fmax"][0] + pad, e["fmin"][1] - pad),
                       (e["fmax"][0] + pad, e["fmax"][1] + pad), (e["fmin"][0] - pad, e["fmax"][1] + pad)):
            out.append((e["s"] + lx * s_ - lz * c, e["x"] + lx * c + lz * s_))
        return out

    def height(self, s, x):
        i = int((s % self.C) / self.step) % self.nx
        j = min(self.ny - 1, max(0, int((x - self.x0) / self.step)))
        return float(self.base[j, i])

    def wet(self, s, x):
        i = int((s % self.C) / self.step) % self.nx
        j = int((x - self.x0) / self.step)
        if not (0 <= j < self.ny):
            return True
        return float(self.level[j, i]) > -9000.0


def town_frame(W, name):
    """(s0, x0, U, V): the heart and the plan's reach (city.py plan_city)"""
    import towns as TS
    spec = next((s for s in TS.SPECS if s["name"] == name), None)
    pop = spec["pop"] if spec else 7000
    wf = bool(spec and spec.get("waterfront"))
    U = (spec or {}).get("half_u", (600.0 + 13.0 * math.sqrt(pop)) * (1.35 if wf else 1.0))
    V = (spec or {}).get("half_v", 450.0 + 13.0 * math.sqrt(pop))
    c = W.law[name]["centre"]
    s0 = c[0]
    # the heart's x: Main Street's (the town's longest main road running along s near the centre)
    best, bx = 0.0, c[1]
    for r in W.ter["roads"]:
        if r.get("town") != name or r.get("cls") not in ("main",):
            continue
        pts = r["pts"]
        near = [p for p in pts if abs(wrap(p[0] - s0, W.C)) < 400.0]
        if len(near) < 2:
            continue
        span = abs(wrap(near[-1][0] - near[0][0], W.C))
        dx = abs(near[-1][1] - near[0][1])
        if span > best and dx < 0.15 * span + 20.0:
            best, bx = span, float(np.median([p[1] for p in near]))
    if spec and spec.get("x") is not None and not spec.get("coast"):
        s0, bx = float(spec["s"]), float(spec["x"])
    return s0, bx, U, V


class Window:
    """A 2 m occupancy raster round one town (u = wrap(s - s0), v = x - x0: axis-aligned with the ring)."""

    def __init__(self, W, s0, x0, U, V):
        self.W, self.s0, self.x0 = W, s0, x0
        self.u0, self.v0 = -U - 400.0, -V - 400.0
        self.u1, self.v1 = U + 400.0, V + 400.0
        self.nu, self.nv = int((self.u1 - self.u0) / CELL) + 1, int((self.v1 - self.v0) / CELL) + 1
        img = Image.new("L", (self.nu, self.nv), 0)
        d = ImageDraw.Draw(img)
        C = W.C
        for r in W.ter["roads"]:
            pts = r["pts"]
            if not any(self._in(p) for p in pts[:: max(1, len(pts) // 20)] + [pts[-1]]):
                continue
            hw = max(r.get("hl", r["w"] / 2), r.get("hr", r["w"] / 2)) + r.get("lawn", 0.0) + r.get("walk", 0.0)
            width = 2 * hw + ROW_EXTRA.get(r.get("cls", "street"), 4.0)
            d.line([self.px(p) for p in pts], fill=1, width=max(1, int(round(width / CELL))), joint="curve")
        rail = W.ter.get("rail", {}).get("pts", [])
        seg = [p for p in rail if self._in(p)]
        if len(seg) > 1:
            d.line([self.px(p) for p in rail if abs(wrap(p[0] - s0, C)) < self.u1 + 200], fill=1, width=int(30 / CELL))
        for e in W.structs:
            if abs(wrap(e["s"] - s0, C)) > self.u1 + 100 or abs(e["x"] - x0) > self.v1 + 100:
                continue
            d.polygon([self.px(p) for p in W.footprint(e)], fill=1)
        for a in W.ter["areas"]:
            if self._in(a["poly"][0]):
                d.polygon([self.px(p) for p in a["poly"]], fill=1)
        for wk in W.walks:                                    # (docks, piers, boardwalks: over the water too)
            if wk.get("pts") and self._in(wk["pts"][0]):
                d.line([self.px(p) for p in wk["pts"]], fill=1, width=max(1, int((float(wk.get("w", 4.0)) + 6.0) / CELL)))
            elif wk.get("rect") and self._in(wk["rect"][:2]):
                r_ = wk["rect"]
                d.rectangle([self.px((r_[0] - r_[2] / 2 - 4, r_[1] - r_[3] / 2 - 4)), self.px((r_[0] + r_[2] / 2 + 4, r_[1] + r_[3] / 2 + 4))], fill=1)
        self.geo = np.asarray(img).astype(bool)
        self.occ = self.geo.copy()
        # woods and water off the land cover and the water level (8 m rasters), sampled on an 8 m grid and blown up
        K = 4
        cu_ = np.arange(0, self.nu, K)
        cv_ = np.arange(0, self.nv, K)
        ss = (s0 + self.u0 + cu_ * CELL) % C
        xx = x0 + self.v0 + cv_ * CELL
        li = (ss / W.lc_step).astype(int) % W.lc.shape[1]
        lj = np.clip(((xx - W.x0) / W.lc_step).astype(int), 0, W.lc.shape[0] - 1)
        woods = np.isin(W.lc[np.ix_(lj, li)], (3, 5))
        wi = (ss / W.step).astype(int) % W.nx
        wj = np.clip(((xx - W.x0) / W.step).astype(int), 0, W.ny - 1)
        wet = W.level[np.ix_(wj, wi)].astype(np.float32) > -9000.0
        out = ((xx < -W.ter["W"] / 2 + 60) | (xx > W.ter["W"] / 2 - 60))[:, None] & np.ones(len(cu_), bool)[None, :]
        bad = woods | wet | out
        # the heart's own land: the dry ground joined to the heart without crossing water (a market across a river or
        # on an island in the town's limits is not its outskirts)
        from scipy import ndimage
        lab, _ = ndimage.label(~(wet | out))
        hi, hj = int(-self.u0 / CELL / K), int(-self.v0 / CELL / K)
        hv = lab[min(hj, lab.shape[0] - 1), min(hi, lab.shape[1] - 1)]
        if hv == 0:                                   # (the heart's cell is wet: the nearest dry label)
            ys, xs = np.nonzero(lab)
            k_ = int(np.argmin((ys - hj) ** 2 + (xs - hi) ** 2))
            hv = lab[ys[k_], xs[k_]]
        self.home = lab == hv
        self.K = K
        self.cu_c, self.cv_c = cu_, cv_
        # (a woods or water cell blocks its 8 m square and the next one round: the land cover is coarse)
        bad = bad | np.roll(bad, 1, 0) | np.roll(bad, -1, 0) | np.roll(bad, 1, 1) | np.roll(bad, -1, 1)
        big = np.repeat(np.repeat(bad, K, 0), K, 1)[:self.nv, :self.nu]
        self.occ = self.occ | big
        self.wet_c = wet & ~out                               # (8 m cells: open water, for the pier markets)

    def wet_at(self, u, v):
        i, j = int((u - self.u0) / CELL / self.K), int((v - self.v0) / CELL / self.K)
        return 0 <= j < self.wet_c.shape[0] and 0 <= i < self.wet_c.shape[1] and bool(self.wet_c[j, i])

    def geo_at(self, u, v, r=0.0):
        i, j = int((u - self.u0) / CELL), int((v - self.v0) / CELL)
        k = int(math.ceil(r / CELL))
        if i - k < 0 or j - k < 0 or i + k >= self.nu or j + k >= self.nv:
            return True
        return bool(self.geo[j - k:j + k + 1, i - k:i + k + 1].any())

    def home_at(self, u, v):
        i, j = int((u - self.u0) / CELL / self.K), int((v - self.v0) / CELL / self.K)
        return 0 <= j < self.home.shape[0] and 0 <= i < self.home.shape[1] and bool(self.home[j, i])

    def _in(self, p):
        u = wrap(p[0] - self.s0, self.W.C)
        v = p[1] - self.x0
        return self.u0 <= u <= self.u1 and self.v0 <= v <= self.v1

    def px(self, p):
        return ((wrap(p[0] - self.s0, self.W.C) - self.u0) / CELL, (p[1] - self.x0 - self.v0) / CELL)

    def free_box(self, umin, umax, vmin, vmax):
        i0, i1 = int(math.floor((umin - self.u0) / CELL)), int(math.ceil((umax - self.u0) / CELL))
        j0, j1 = int(math.floor((vmin - self.v0) / CELL)), int(math.ceil((vmax - self.v0) / CELL))
        if i0 < 0 or j0 < 0 or i1 >= self.nu or j1 >= self.nv:
            return False
        return not self.occ[j0:j1 + 1, i0:i1 + 1].any()

    def stamp_box(self, umin, umax, vmin, vmax):
        i0, i1 = int(math.floor((umin - self.u0) / CELL)), int(math.ceil((umax - self.u0) / CELL))
        j0, j1 = int(math.floor((vmin - self.v0) / CELL)), int(math.ceil((vmax - self.v0) / CELL))
        self.occ[max(0, j0):j1 + 1, max(0, i0):i1 + 1] = True

    def free_strip(self, a, b, width, skip_end=0.0):
        """a straight strip from a to b (window u, v) clear (its last skip_end metres may touch the road it meets)"""
        L = math.dist(a, b)
        n = max(2, int(L / CELL) + 1)
        r = int(math.ceil(width / 2 / CELL))
        for k in range(n):
            t = k / (n - 1)
            if L * (1 - t) < skip_end:
                break
            u, v = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            i, j = int((u - self.u0) / CELL), int((v - self.v0) / CELL)
            if i - r < 0 or j - r < 0 or i + r >= self.nu or j + r >= self.nv:
                return False
            if self.occ[j - r:j + r + 1, i - r:i + r + 1].any():
                return False
        return True


def site_frame(cu, cv, vdir, plan):
    """the site frame placed so its bbox centre is at window (cu, cv): returns (origin (u, v), udir, vdir) in the window
    frame. vdir is +-u or +-v (axis-aligned); udir = vdir turned -90 deg (u x v = +1)"""
    udir = (vdir[1], -vdir[0])
    b = plan["bbox"]
    mu, mv = (b[0] + b[1]) / 2, (b[2] + b[3]) / 2
    o = (cu - udir[0] * mu - vdir[0] * mv, cv - udir[1] * mu - vdir[1] * mv)
    return o, udir, vdir


def to_win(o, ud, vd, a, b):
    return (o[0] + ud[0] * a + vd[0] * b, o[1] + ud[1] * a + vd[1] * b)


def bbox_win(o, ud, vd, b):
    pts = [to_win(o, ud, vd, a, c) for a in (b[0], b[1]) for c in (b[2], b[3])]
    return min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)


def site_one(W, m, others):
    name = m["town"]
    s0, x0, U, V = town_frame(W, name)
    win = Window(W, s0, x0, U, V)
    for (umin, umax, vmin, vmax, s_, x_) in others:          # (markets sited already, if their windows overlap)
        du = wrap(s_ - s0, W.C)
        dv = x_ - x0
        win.stamp_box(umin + du, umax + du, vmin + dv, vmax + dv)
    rng = random.Random(MS.MARKETS.index(m) * 7919 + 303)
    tier = m["tier"]
    rmin = R_IN[tier]
    # the town's streets for the access drive: (window u, v, cls)
    st_pts = []
    for r in W.ter["roads"]:
        if r.get("cls") == "alley" or r.get("cls") == "hwy" or (r.get("town") not in (name, None)) or (r.get("town") is None and r.get("cls") != "county"):
            continue
        for p in r["pts"][::2]:
            if win._in(p):
                q = (wrap(p[0] - s0, W.C), p[1] - x0)
                st_pts.append((q[0], q[1], r.get("cls"), r))
    st_arr = np.array([(q[0], q[1]) for q in st_pts]) if st_pts else np.zeros((0, 2))
    is_main = np.array([q[2] in ("main", "county") for q in st_pts], bool) if st_pts else np.zeros(0, bool)
    crowd = [(wrap(c[0] - s0, W.C), c[1] - x0) for c in W.crowd if abs(wrap(c[0] - s0, W.C)) < U + 600 and abs(c[1] - x0) < V + 600]
    for k_step, f in enumerate(STEP_DOWN):
        n = int(round(m["stalls"] * f / 10.0) * 10) if f < 1.0 else m["stalls"]
        plans = {}
        for var in ML.VARIANTS:
            for side in (-1, 1):
                pl_ = ML.layout(m, side, None if f == 1.0 else n, var)
                if pl_ is not None:
                    plans[(side, var)] = pl_
        cands = []
        for iu in range(int(-U / GRID), int(U / GRID) + 1):
            for iv in range(int(-V / GRID), int(V / GRID) + 1):
                cu, cv = iu * GRID, iv * GRID
                r = rnorm(cu, cv, U, V)
                if r < rmin or r > R_CEN:
                    continue
                score = abs(r - R_BEST) + (0.04 if cu > 0 else 0.0) + rng.random() * 0.03
                cands.append((score, cu, cv))
        cands.sort()
        why = {"r": 0, "occ": 0, "slope": 0, "crowd": 0, "drive": 0}
        for score, cu, cv in cands:
            for vdir in ((0.0, 1.0 if cv >= 0 else -1.0), (1.0 if cu >= 0 else -1.0, 0.0)):
                udir = (vdir[1], -vdir[0])
                # the leeward end (-s, west) holds the mooring field
                side = -1 if udir[0] > 0.3 else (1 if udir[0] < -0.3 else -1)
                p = None
                for var in ML.VARIANTS:
                    p_ = plans.get((side, var))
                    if p_ is None:
                        continue
                    o, ud, vd = site_frame(cu, cv, vdir, p_)
                    bu0, bu1, bv0, bv1 = bbox_win(o, ud, vd, p_["bbox"])
                    if any(rnorm(a, b, U, V) > R_OUT for a in (bu0, bu1) for b in (bv0, bv1)):
                        why["r"] += 1
                        continue
                    if not win.free_box(bu0, bu1, bv0, bv1):
                        why["occ"] += 1
                        continue
                    if not win.home_at((bu0 + bu1) / 2, (bv0 + bv1) / 2):
                        why["across"] = why.get("across", 0) + 1
                        continue
                    p = p_
                    break
                if p is None:
                    continue
                # flat enough: the lot and floor
                c0, c1 = p["core"][0], p["core"][1]
                hs = []
                for a in np.linspace(c0, c1, 6):
                    for b in np.linspace(0.0, p["core"][3], 6):
                        q = to_win(o, ud, vd, a, b)
                        hs.append((a, b, W.height(s0 + q[0], x0 + q[1])))
                A = np.array([[h[0], h[1], 1.0] for h in hs])
                z = np.array([h[2] for h in hs])
                g = np.linalg.lstsq(A, z, rcond=None)[0]
                if math.hypot(g[0], g[1]) > SLOPE_MAX or (z.max() - z.min()) > 0.06 * math.hypot(c1 - c0, p["core"][3]):
                    why["slope"] += 1
                    continue
                mid = ((bu0 + bu1) / 2, (bv0 + bv1) / 2)
                half = 0.5 * math.hypot(bu1 - bu0, bv1 - bv0)
                if any(math.hypot(q[0] - mid[0], q[1] - mid[1]) < SCHOOL_CLEAR + half for q in crowd):
                    why["crowd"] += 1
                    continue
                # the access drive: from the frontage's middle straight out (against vdir) or to the nearest street
                fr = to_win(o, ud, vd, 0.0, 0.0)
                if st_arr.shape[0] == 0:
                    continue
                d2 = np.hypot(st_arr[:, 0] - fr[0], st_arr[:, 1] - fr[1])
                # only streets in front of the site (not behind or beside it)
                ahead = ((st_arr[:, 0] - fr[0]) * vd[0] + (st_arr[:, 1] - fr[1]) * vd[1]) < -4.0
                okm = ahead & is_main & (d2 <= DRIVE_MAIN)
                oka = ahead & (d2 <= DRIVE_ANY)
                pick = None
                for ok in (okm, oka):
                    if ok.any():
                        idx = np.where(ok)[0]
                        k = idx[np.argmin(d2[idx])]
                        q = st_pts[k]
                        hw = max(q[3].get("hl", q[3]["w"] / 2), q[3].get("hr", q[3]["w"] / 2))
                        start = (fr[0] - vd[0] * 1.0, fr[1] - vd[1] * 1.0)
                        if d2[k] < 8.0 or win.free_strip(start, (q[0], q[1]), 9.0, skip_end=hw + q[3].get("walk", 0.0) + q[3].get("lawn", 0.0) + 6.0):
                            pick = (k, q, float(d2[k]))
                            break
                if pick is None:
                    why["drive"] += 1
                    continue
                return emit(W, m, p, s0, x0, U, V, o, ud, vd, pick, n, score, (bu0, bu1, bv0, bv1), win)
        print("  %s: no site at %d stalls (step %d): %s" % (m["id"], n, k_step, why))
        if m.get("pier"):
            break
    if m.get("pier"):
        return site_pier(W, m, win, s0, x0, U, V, st_pts, rng)
    return None


def site_pier(W, m, win, s0, x0, U, V, st_pts, rng):
    """a floating pier market (market_pier.py) from a free spot on the heart's shore near a street: every deck sample over
    open water clear (6 m) of roads, docks, bridges and structures, the landing dry on the heart's land, the whole
    pier inside the limits"""
    import market_pier as MP
    if not st_pts:
        return None
    st = np.array([(q[0], q[1]) for q in st_pts])
    best = None
    K = win.K
    cand = []
    for j in range(win.home.shape[0]):
        for i in range(win.home.shape[1]):
            if not win.home[j, i]:
                continue
            nb = win.wet_c[max(0, j - 1):j + 2, max(0, i - 1):i + 2]
            if not nb.any():
                continue
            u = win.u0 + (i + 0.5) * CELL * K
            v = win.v0 + (j + 0.5) * CELL * K
            if rnorm(u, v, U, V) > 0.97:
                continue
            d = float(np.min(np.hypot(st[:, 0] - u, st[:, 1] - v)))
            if d > 60.0:
                continue
            cand.append((d + rng.random() * 3.0, u, v))
    cand.sort()
    tried = 0
    for d, u, v in cand:
        for kq in range(16):
            th = 2 * math.pi * kq / 16
            vd = (math.cos(th), math.sin(th))
            ud = (vd[1], -vd[0])
            for side in (1, -1):
                p = MP.pier_layout(m, side)
                tried += 1
                o = (u, v)
                ok = True
                # the water parts: the gangway's outer half and every deck, sampled every 4 m
                for (a0, b0, a1, b1) in [(-1.3, 6.0, 1.3, 12.0)] + [tuple(dk) for dk in p["pier"]["decks"]]:
                    for a in np.arange(a0 + 1.0, a1, 4.0):
                        for b in np.arange(b0 + 1.0, b1, 4.0):
                            q = to_win(o, ud, vd, a, b)
                            if not win.wet_at(*q) or win.geo_at(q[0], q[1], 6.0) or rnorm(q[0], q[1], U, V) > 1.0:
                                ok = False
                                break
                        if not ok:
                            break
                    if not ok:
                        break
                if not ok:
                    continue
                lq = to_win(o, ud, vd, 0.0, -2.0)
                if win.wet_at(*lq) or not win.home_at(*lq):
                    continue
                ls_ = (s0 + lq[0], x0 + lq[1])
                if any(math.hypot(wrap(e["s"] - ls_[0], W.C), e["x"] - ls_[1]) < 40.0 and _in_poly(W.footprint(e, 1.0), ls_, W.C)
                       for e in W.structs):
                    continue
                best = (d, p, o, ud, vd)
                break
            if best:
                break
        if best:
            break
    if not best:
        print("  %s: no pier site either (%d tried)" % (m["id"], tried))
        return None
    d, p, o, ud, vd = best
    C = W.C
    org = (s0 + o[0], x0 + o[1])
    yaw = math.atan2(ud[1], ud[0])
    frame = {"s": round(org[0] % C, 2), "x": round(org[1], 2), "yaw": round(yaw, 6)}

    def ring(a, b):
        q = to_win(o, ud, vd, a, b)
        return [round((s0 + q[0]) % C, 2), round(x0 + q[1], 2)]
    # the deck's height: the water's level under the head and deck, plus the freeboard; the landing's: the shore's
    lv = []
    for dk in p["pier"]["decks"][:2]:
        c = ring((dk[0] + dk[2]) / 2, (dk[1] + dk[3]) / 2)
        i = int((c[0] % C) / W.step) % W.nx
        j = int((c[1] - W.x0) / W.step)
        lv.append(float(W.level[j, i]))
    deck_h = round(max(lv) + p["pier"]["freeboard"], 2)
    lc = ring(0.0, -2.0)
    p["pier"]["deck_h"] = deck_h
    p["pier"]["landing_h"] = round(W.height(*lc), 2)
    limits = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        c_, s_ = math.cos(a), math.sin(a)
        k = (abs(c_) ** LIMIT_P + abs(s_) ** LIMIT_P) ** (-1.0 / LIMIT_P)
        limits.append([round((s0 + U * c_ * k) % C, 1), round(x0 + V * s_ * k, 1)])
    cen = ring(0.0, (p["core"][3] + 12.0) / 2)
    site = {"frame": frame, "limits_r": round(rnorm(wrap(cen[0] - s0, C), cen[1] - x0, U, V), 3), "limits_sx": limits,
            "heart_sx": [round(s0 % C, 1), round(x0, 1)], "reach": [round(U, 1), round(V, 1)], "centre_sx": cen,
            "bbox": p["bbox"], "core": p["core"],
            "site": [[p["bbox"][0], p["bbox"][2]], [p["bbox"][1], p["bbox"][2]], [p["bbox"][1], p["bbox"][3]], [p["bbox"][0], p["bbox"][3]]],
            "floor": p["floor"], "apron": p["apron"], "mooring": p["mooring"], "lot_poly": p["lot"]["poly"],
            "entrances": p["entrances"], "pylon": p["pylon"], "arch": p["arch"], "bus": p["bus"], "stalls": p["stalls"],
            "sheds": [], "tent_slots": p["tent_slots"], "lanes": p["lanes"],
            "lot": {"spaces": 0, "accessible": 0, "rows": [], "per_row": 0, "bike_racks": p["pier"]["bike_racks"]},
            "poles": [], "festoons": [], "pier_festoons": p["festoons"], "deadmen": p["deadmen"], "masts": p["masts"],
            "stations": p["stations"], "drive_sx": [], "field_side": p["field_side"], "pier": p["pier"],
            "stats": dict(p["stats"], stalls_spec=m["stalls"], stepped=False, score=round(d, 3), pier=True)}
    print("  %s: a floating pier off the shore, landing %.0f m from a street, deck at %.2f m (landing %.2f)" % (
        m["id"], d, deck_h, p["pier"]["landing_h"]))
    bb = bbox_win(o, ud, vd, p["bbox"])
    return site, [], None, bb


def _in_poly(poly, p, C):
    n = len(poly)
    c = False
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ax, bx = a[0], a[0] + wrap(b[0] - a[0], C)
        px = a[0] + wrap(p[0] - a[0], C)
        if (a[1] > p[1]) != (b[1] > p[1]) and px < (bx - ax) * (p[1] - a[1]) / (b[1] - a[1] + 1e-12) + ax:
            c = not c
    return c


def emit(W, m, p, s0, x0, U, V, o, ud, vd, pick, n, score, bb, win):  # noqa: C901
    C = W.C
    # the site frame on the ring: (s, x) = origin + u * udir + v * vdir (axis-aligned; a proper rotation)
    org = (s0 + o[0], x0 + o[1])
    yaw = math.atan2(ud[1], ud[0])
    frame = {"s": round(org[0] % C, 2), "x": round(org[1], 2), "yaw": round(yaw, 6)}

    def ring(a, b):
        q = to_win(o, ud, vd, a, b)
        return [round((s0 + q[0]) % C, 2), round(x0 + q[1], 2)]

    def poly(pp):
        return [ring(a, b) for a, b in pp]

    tag = m["id"]
    areas = [{"kind": "parking", "town": m["town"], "market": tag, "poly": poly(p["lot"]["poly"])},
             {"kind": "market_floor", "town": m["town"], "market": tag, "poly": poly(p["floor"])},
             {"kind": "mooring_field", "town": m["town"], "market": tag, "poly": poly(p["mooring"])}]
    for ap in p["apron"]:
        areas.append({"kind": "market_apron", "town": m["town"], "market": tag, "poly": poly(ap)})
    # the lot record (tools/parking_lots.py's format: a lot-centred frame, dir = u, rows [u0, u1, v_front, depth, facing])
    L = p["lot"]
    lc = (0.0, (L["v0"] + L["v1"]) / 2)
    rows = [[r[0], r[1], round(r[2] - lc[1], 2), r[3], r[4]] for r in L["rows"]]
    acc = ring(0.0, -1.0)
    areas[0]["lot"] = {"type": "market", "market": tag, "town": m["town"], "city": None, "spaces": L["spaces"],
                       "accessible": L["accessible"], "centre": ring(*lc), "dir": [round(ud[0], 4), round(ud[1], 4)],
                       "w": L["w"], "d": round(L["v1"] - L["v0"], 2), "rows": rows, "per_row": L["per_row"],
                       "access": acc, "stop": None}
    # the access drive: a town street from the street it meets to the lot's front
    k, q, dist = pick
    a = ring(0.0, -1.0)
    b = [round((s0 + q[0]) % C, 2), round(x0 + q[1], 2)]
    drive = None
    if dist >= 8.0:
        nseg = max(2, int(dist / 3.0) + 1)
        pts = [[round(b[0] + wrap(a[0] - b[0], C) * t / (nseg - 1), 2), round(b[1] + (a[1] - b[1]) * t / (nseg - 1), 2)] for t in range(nseg)]
        drive = {"cls": "street", "w": 7, "town": m["town"], "name": m["name"].replace("The ", "") + " Drive", "market": tag, "pts": pts}
    # limits: the 48-point ellipse (00 §1.1)
    def _lim(a):
        c_, s_ = math.cos(a), math.sin(a)
        k = (abs(c_) ** LIMIT_P + abs(s_) ** LIMIT_P) ** (-1.0 / LIMIT_P)
        return [round((s0 + U * c_ * k) % C, 1), round(x0 + V * s_ * k, 1)]
    limits = [_lim(2 * math.pi * i / 48) for i in range(48)]
    cen = ring((p["core"][0] + p["core"][1]) / 2, p["core"][3] / 2)
    r_c = rnorm(wrap(cen[0] - s0, C), cen[1] - x0, U, V)
    site = {"frame": frame, "limits_r": round(r_c, 3), "limits_sx": limits, "heart_sx": [round(s0 % C, 1), round(x0, 1)],
            "reach": [round(U, 1), round(V, 1)], "centre_sx": cen, "bbox": p["bbox"], "core": p["core"],
            "site": [[p["bbox"][0], p["bbox"][2]], [p["bbox"][1], p["bbox"][2]], [p["bbox"][1], p["bbox"][3]], [p["bbox"][0], p["bbox"][3]]],
            "floor": p["floor"], "apron": p["apron"], "mooring": p["mooring"], "lot_poly": p["lot"]["poly"],
            "entrances": p["entrances"], "pylon": p["pylon"], "arch": p["arch"], "bus": p["bus"], "stalls": p["stalls"],
            "sheds": p["sheds"], "tent_slots": p["tent_slots"], "lanes": p["lanes"],
            "lot": {"spaces": L["spaces"], "accessible": L["accessible"], "rows": L["rows"], "per_row": L["per_row"]},
            "poles": p["poles"], "festoons": p["festoons"], "deadmen": p["deadmen"], "masts": p["masts"], "stations": p["stations"],
            "drive_sx": drive["pts"] if drive else [a, b], "field_side": p["field_side"],
            "stats": dict(p["stats"], stalls_spec=m["stalls"], stepped=n != m["stalls"], score=round(score, 3))}
    return site, areas, drive, bb


def main():
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    dry = "--dry" in sys.argv
    W = World()
    sites, all_areas, drives, report = {}, [], [], []
    done = []
    old = {}
    if only:
        try:
            for e in json.load(open(MM.OUT))["markets"]:
                if e.get("sited") and e["town"] not in only:
                    old[e["town"]] = e
        except (OSError, ValueError):
            pass
    for m in sorted(MS.MARKETS, key=lambda m: -m["stalls"]):
        if only and m["town"] not in only:
            continue
        print("%s %s (%s, %d stalls)" % (m["id"], m["name"], m["town"], m["stalls"]), flush=True)
        got = site_one(W, m, done)
        if not got:
            report.append((m["id"], "no_site"))
            continue
        site, areas, drive, bb = got
        s0, x0, U, V = town_frame(W, m["town"])
        done.append(bb + (s0, x0))
        sites[m["town"]] = site
        all_areas += areas
        if drive:
            drives.append(drive)
        report.append((m["id"], "r %.2f, %d stalls%s, drive %.0f m, at (%.0f, %.0f)" % (
            site["limits_r"], len(site["stalls"]), " (STEPPED DOWN)" if site["stats"]["stepped"] else "",
            math.dist(drive["pts"][0], drive["pts"][-1]) if drive else 0.0, site["centre_sx"][0], site["centre_sx"][1])
            + ("  (floating pier)" if site.get("pier") else "")))
    for r in report:
        print("  %-7s %s" % r)
    if dry:
        return
    if only:
        # keep the other markets' areas and drives (World took every market's out)
        keep_towns = set(old)
        ter0 = json.load(open(os.path.join(GD, "terrain.json")))
        all_areas += [a for a in ter0["areas"] if a.get("market") and a["town"] in keep_towns]
        drives += [r for r in ter0["roads"] if r.get("market") and r["town"] in keep_towns]
        for t, e in old.items():
            sites[t] = {k: v for k, v in e.items() if k not in ("id", "town", "name", "sign", "region", "tier", "pop", "draw",
                                                                 "great_fair_month", "mooring_tier", "tents_min", "sited")}
    W.ter["areas"] += all_areas
    W.ter["roads"] += drives
    tp = os.path.join(GD, "terrain.json")
    with open(tp + ".tmp", "w") as f:
        json.dump(W.ter, f, indent=0)
    os.replace(tp + ".tmp", tp)
    MM.write(sites)
    import write_limits
    write_limits.main()
    print("terrain.json: %d market areas, %d drives; %s: %d sited" % (len(all_areas), len(drives), MM.OUT, len(sites)))


if __name__ == "__main__":
    main()
