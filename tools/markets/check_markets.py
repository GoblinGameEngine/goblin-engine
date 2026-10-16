#!/usr/bin/env python3
"""
check_markets.py -- the flea markets' site checks (research/flea_markets/00_plan.md §12 "check_markets").

    ~/.venvs/ssc-assets/bin/python tools/markets/check_markets.py [--quiet]

For every market in godot_project/remake/markets/flea_markets.json, against the game data as it stands (terrain.json,
placement.json, the rasters):
  * 22 markets, one per settlement; sited;
  * the whole site inside the limits (r <= 1), its centre on the outskirts: r in [0.60, 0.95] (villages [0.50, 0.95]);
  * the lot and floor no steeper than 4 %; dry;
  * no overlap with any structure, road (but its own drive) or other area;
  * the drive meets a street;
  * the stalls as markets_spec (00 §1.2) unless stepped down, permanent 35 % +- 1; paved spaces >= 1.8 x stalls;
  * every stall within 45 m of a 6 m lane; stalls inside the floor and off each other;
  * tent slots >= 60 / 36 / 24 by tier, inside the apron or the mooring field, off the lot and floor;
  * the mooring ground by tier (anchor blocks 24 / 12 / 8, masts 2 / 1 / 0).
Exit 1 on any failure.
"""
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import markets_spec as MS  # noqa: E402

GD = os.path.join(ROOT, "godot_project", "remake")
LIMIT_P = 4.0


def main():
    quiet = "--quiet" in sys.argv
    fm = json.load(open(os.environ.get("FM_PATH") or os.path.join(GD, "markets", "flea_markets.json")))["markets"]
    ter = json.load(open(os.path.join(GD, "terrain.json")))
    C = 2 * math.pi * ter["R"]
    wrap = lambda d: (d + C / 2) % C - C / 2
    rs = ter["raster"]
    nx, ny, step, x0r = rs["nx"], rs["ny"], rs["step_m"], rs["x0"]
    raw = os.path.join(GD, "terrain_base_raw.bin.gz")
    base = np.frombuffer(gzip.open(raw if os.path.exists(raw) else os.path.join(GD, rs["base"])).read(), np.float16).reshape(ny, nx)
    level = np.frombuffer(gzip.open(os.path.join(GD, rs["level"])).read(), np.float16).reshape(ny, nx)
    structs = json.load(open(os.path.join(GD, "placement.json")))["structures"]
    fails = []
    warns = []

    def fail(m, what):
        fails.append("%s: %s" % (m, what))

    def ij(s, x):
        return int((s % C) / step) % nx, min(ny - 1, max(0, int((x - x0r) / step)))

    def to_world(f, u, v):
        a = f["yaw"]
        return ((f["s"] + u * math.cos(a) - v * math.sin(a)) % C, f["x"] + u * math.sin(a) + v * math.cos(a))

    def inside(poly, p):
        # (ring polygon; p near it)
        n = len(poly)
        c = False
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            ay, by = a[1], b[1]
            ax, bx = a[0], a[0] + wrap(b[0] - a[0])
            px = a[0] + wrap(p[0] - a[0])
            if (ay > p[1]) != (by > p[1]) and px < (bx - ax) * (p[1] - ay) / (by - ay + 1e-12) + ax:
                c = not c
        return c

    def seg_d(p, a, b):
        ds, dx = wrap(b[0] - a[0]), b[1] - a[1]
        L2 = ds * ds + dx * dx or 1e-9
        t = max(0.0, min(1.0, (wrap(p[0] - a[0]) * ds + (p[1] - a[1]) * dx) / L2))
        return math.hypot(wrap(p[0] - a[0]) - ds * t, p[1] - a[1] - dx * t)

    # spatial grids (100 m) of road segments, footprints and non-market areas
    G = 100.0
    rg, fg, ag = {}, {}, {}
    for ri, r in enumerate(ter["roads"]):
        hw = max(r.get("hl", r["w"] / 2), r.get("hr", r["w"] / 2))
        for a, b in zip(r["pts"], r["pts"][1:]):
            for k in {(int((a[0] % C) // G), int(a[1] // G)), (int((b[0] % C) // G), int(b[1] // G))}:
                rg.setdefault(k, []).append((a, b, hw, ri))
    for e in structs:
        if e["kind"] == "crossing":
            continue
        c_, s_ = math.cos(e["yaw"]), math.sin(e["yaw"])
        poly = [(e["s"] + lx * s_ - lz * c_, e["x"] + lx * c_ + lz * s_) for lx, lz in
                ((e["fmin"][0], e["fmin"][1]), (e["fmax"][0], e["fmin"][1]), (e["fmax"][0], e["fmax"][1]), (e["fmin"][0], e["fmax"][1]))]
        fg.setdefault((int((e["s"] % C) // G), int(e["x"] // G)), []).append((e["id"], poly))
    for ai, a in enumerate(ter["areas"]):
        if a.get("market"):
            continue
        c = a["poly"][0]
        ag.setdefault((int((c[0] % C) // G), int(c[1] // G)), []).append((ai, a))

    def near(grid, p, r=1):
        k0 = (int((p[0] % C) // G), int(p[1] // G))
        n = int(round(C / G))
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                yield from grid.get(((k0[0] + di) % n, k0[1] + dj), ())

    by_town = {m["town"]: m for m in MS.MARKETS}
    if len(fm) != 22:
        fail("all", "%d markets, not 22" % len(fm))
    seen = set()
    for e in fm:
        mid = e["id"]
        spec = by_town[e["town"]]
        if e["town"] in seen:
            fail(mid, "two markets for %s" % e["town"])
        seen.add(e["town"])
        if not e.get("sited"):
            if "--allow-unsited" in sys.argv:
                warns.append("%s: not sited (no free land inside the limits)" % mid)
            else:
                fail(mid, "not sited (no free land inside the limits)")
            continue
        f = e["frame"]
        hs, hx = e["heart_sx"]
        U, V = e["reach"]
        rn = lambda p: (abs(wrap(p[0] - hs) / U) ** LIMIT_P + abs((p[1] - hx) / V) ** LIMIT_P) ** (1 / LIMIT_P)
        b = e["bbox"]
        corners = [to_world(f, u, v) for u in (b[0], b[1]) for v in (b[2], b[3])]
        if max(rn(p) for p in corners) > 1.0 + 1e-6:
            fail(mid, "site outside the limits (r %.3f)" % max(rn(p) for p in corners))
        rc = rn(e["centre_sx"])
        if e.get("pier"):
            # a floating pier market (market_pier.py): every deck over open water, the landing on dry land, tents, the
            # stalls on the deck, the mast and bollards; no paved lot (bike racks: Victory Bay is car-light)
            pr = e["pier"]
            dry_decks = 0
            for dk in pr["decks"] + [[-1.3, 6.0, 1.3, 12.0]]:
                for u in np.arange(dk[0] + 1.0, dk[2], 4.0):
                    for v in np.arange(dk[1] + 1.0, dk[3], 4.0):
                        p = to_world(f, u, v)
                        i, j = ij(*p)
                        if float(level[j, i]) <= -9000.0:
                            dry_decks += 1
            if dry_decks:
                fail(mid, "%d pier deck samples over dry land" % dry_decks)
            lp = to_world(f, 0.0, -2.0)
            i, j = ij(*lp)
            if float(level[j, i]) > -9000.0:
                fail(mid, "the pier's landing is in the water")
            if not (0.5 <= rc <= 0.95):
                fail(mid, "centre r %.3f outside [0.50, 0.95]" % rc)
            if len(e["stalls"]) != spec["stalls"]:
                fail(mid, "%d stalls, spec %d" % (len(e["stalls"]), spec["stalls"]))
            if len(e["tent_slots"]) < MS.TENTS_MIN[spec["tier"]]:
                fail(mid, "%d tent slots < %d" % (len(e["tent_slots"]), MS.TENTS_MIN[spec["tier"]]))
            if not e["masts"] or len(e["deadmen"]) < 8:
                fail(mid, "the pier head wants a mast and >= 8 bollards")
            if not quiet:
                print("%-7s %-17s ok-so-far  r %.2f  %3d stalls  pier (deck %.2f m)  %3d tents" % (
                    mid, e["town"], rc, len(e["stalls"]), pr["deck_h"], len(e["tent_slots"])))
            continue
        lo = 0.5 if spec["tier"] == "village" else 0.6
        if not (lo <= rc <= 0.95):
            fail(mid, "centre r %.3f outside [%.2f, 0.95]" % (rc, lo))
        # slope and water over the core
        core = e["core"]
        pts = [(a, v) for a in np.linspace(core[0], core[1], 8) for v in np.linspace(0.0, core[3], 8)]
        hh = []
        for a, v in pts:
            p = to_world(f, a, v)
            i, j = ij(*p)
            hh.append((a, v, float(base[j, i])))
            if float(level[j, i]) > -9000.0:
                fail(mid, "water under the core at (%.0f, %.0f)" % p)
                break
        A = np.array([[h[0], h[1], 1.0] for h in hh])
        g = np.linalg.lstsq(A, np.array([h[2] for h in hh]), rcond=None)[0]
        if math.hypot(g[0], g[1]) > 0.04:
            fail(mid, "the core slopes %.3f" % math.hypot(g[0], g[1]))
        # overlaps: sample the whole site every 4 m
        drive = e.get("drive_sx") or []
        hits = {"structure": set(), "road": set(), "area": set()}
        for u in np.arange(b[0] + 1.0, b[1] - 0.5, 4.0):
            for v in np.arange(b[2] + 1.0, b[3] - 0.5, 4.0):
                p = to_world(f, u, v)
                for a_, b_, hw, ri in near(rg, p):
                    if ter["roads"][ri].get("market") == mid:
                        continue
                    if seg_d(p, a_, b_) < hw:
                        hits["road"].add(ter["roads"][ri].get("name") or ter["roads"][ri].get("cls"))
                for sid, poly in near(fg, p):
                    if inside(poly, p):
                        hits["structure"].add(sid)
                for ai, a in near(ag, p, 3):
                    if inside(a["poly"], p):
                        hits["area"].add("%s#%d" % (a["kind"], ai))
        for k, v in hits.items():
            if v:
                fail(mid, "overlaps %d %s(s): %s" % (len(v), k, ", ".join(sorted(v)[:5])))
        # the drive meets a street
        if drive:
            end = drive[0]
            ok = any(seg_d(end, a_, b_) <= hw + 1.0 for a_, b_, hw, ri in near(rg, end) if ter["roads"][ri].get("market") != mid)
            if not ok:
                fail(mid, "the drive's end (%.0f, %.0f) meets no street" % tuple(end))
            mine = [r for r in ter["roads"] if r.get("market") == mid]
            if math.dist(drive[0], drive[-1]) >= 8.0 and not mine:
                fail(mid, "the drive is not in terrain.json")
        # stalls
        st = e["stalls"]
        k = {0: 0, 1: 0, 2: 0, 3: 0}
        for s in st:
            k[int(s[3])] += 1
        n = len(st)
        if not e["stats"].get("stepped") and n != spec["stalls"]:
            fail(mid, "%d stalls, spec %d" % (n, spec["stalls"]))
        perm = k[0] + k[3] // 2
        if abs(perm - 0.35 * n) > 1.0:
            fail(mid, "permanent %d of %d (not 35 %% +- 1)" % (perm, n))
        if e["lot"]["spaces"] < 1.8 * n - 1e-6:
            fail(mid, "%d paved spaces < 1.8 x %d" % (e["lot"]["spaces"], n))
        lanes = e["lanes"]
        fl = e["floor"]
        fu0, fu1 = min(q[0] for q in fl), max(q[0] for q in fl)
        fv0, fv1 = min(q[1] for q in fl), max(q[1] for q in fl)
        size = {0: (3, 3), 1: (3, 3), 2: (6, 3), 3: (4, 8)}
        boxes = []
        far = 0
        for s in st:
            w, h = size[int(s[3])]
            if abs(math.sin(s[2])) > 0.7:
                w, h = h, w
            bx = (s[0] - w / 2, s[0] + w / 2, s[1] - h / 2, s[1] + h / 2)
            if bx[0] < fu0 - 1e-6 or bx[1] > fu1 + 1e-6 or bx[2] < fv0 - 1e-6 or bx[3] > fv1 + 1e-6:
                fail(mid, "stall at (%.1f, %.1f) off the floor" % (s[0], s[1]))
            boxes.append(bx)
            dmin = min(math.hypot(max(l[0] - s[0], 0, s[0] - l[2]), max(l[1] - s[1], 0, s[1] - l[3])) for l in lanes)
            if dmin > 45.0:
                far += 1
        if far:
            fail(mid, "%d stalls more than 45 m from a lane" % far)
        boxes.sort()
        clash = 0
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                if boxes[j][0] >= boxes[i][1] - 0.01:
                    break
                if boxes[j][2] < boxes[i][3] - 0.01 and boxes[i][2] < boxes[j][3] - 0.01:
                    clash += 1
        if clash:
            fail(mid, "%d stall overlaps" % clash)
        # tents
        tmin = MS.TENTS_MIN[spec["tier"]]
        if len(e["tent_slots"]) < tmin:
            fail(mid, "%d tent slots < %d" % (len(e["tent_slots"]), tmin))
        ok_polys = list(e["apron"]) + [e["mooring"]]
        bad_t = 0
        for t in e["tent_slots"]:
            h = t[3] / 2
            cs = [(t[0] + du, t[1] + dv) for du in (-h, h) for dv in (-h, h)]
            inn = all(any(min(q[0] for q in P) - 1e-6 <= c[0] <= max(q[0] for q in P) + 1e-6 and
                          min(q[1] for q in P) - 1e-6 <= c[1] <= max(q[1] for q in P) + 1e-6 for P in ok_polys) for c in cs)
            if not inn:
                bad_t += 1
        if bad_t:
            fail(mid, "%d tent slots outside the apron and mooring field" % bad_t)
        mo = MS.MOORING[spec["tier"]]
        if len(e["deadmen"]) != mo["deadmen"] or len(e["masts"]) != mo["masts"]:
            fail(mid, "mooring ground %d blocks / %d masts, tier wants %d / %d" % (len(e["deadmen"]), len(e["masts"]), mo["deadmen"], mo["masts"]))
        if not quiet:
            print("%-7s %-17s ok-so-far  r %.2f  %3d stalls  %3d spaces  %3d tents  %s" % (
                mid, e["town"], rc, n, e["lot"]["spaces"], len(e["tent_slots"]), "(stepped)" if e["stats"].get("stepped") else ""))
    for w in warns:
        print("WARN", w)
    for x in fails:
        print("FAIL", x)
    print("check_markets: %d markets, %d failures" % (len(fm), len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
