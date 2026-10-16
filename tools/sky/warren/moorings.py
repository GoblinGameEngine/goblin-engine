"""moorings.py -- the island side of the market moorings (research/flea_markets/00_plan.md sections 3.3 and 8.2;
requests.md K4): the line houses (each with its signal mast on the roof), the gondola top stations (passengers, and
cargo at 3 or more) and the drop-cage davit beside the first passenger station, on every island's rim.

  reserve(L)          before the spine: the sites chosen on the straight dock faces, their cells taken off the ground
                      (OUT: nothing built, paved or walked there) and a street strip behind each station kept open
                      (RESERVED: walkable public ground the walk network must reach)
  emit(L, o, kit)     after the grading (walknet): the kit pieces at the height of the street strip, the station's own
                      floor (whole-cell paving: its hall, passage and gates), the signal masts on the line house roofs
  walk(L)             after the walk graph is final: each station's walk -- the strip, through the hall and the
                      passage under the drive house, out through the rim gate onto the berth deck between the cabins
  doc(L)              the twin's "moorings" block (island frame: +X south, +Y up, +Z west); write_index() gathers all
                      islands' into remake/sky/moorings.json for SkyMooring / SkyRopeway

Pieces (the warren kit, remake/blender/sky/warren_kit/pieces_moor.py): CELL pieces spanning [nx, nz] cells along
their +X / +Z from the first cell; THE RIM IS -Z (the first row's outer face, z -1.5, on the deck edge; fairleads, the
davit's jib and the stations' berth decks reach out over the void).  Kit rot r = Basis(UP, r pi/2): the piece's -Z
faces E (r 0), N (1), W (2), S (3).  Deterministic: geometry only (no rng).

Counts (00 section 3.3): line houses 2 / 3 / 4 at 1-3 / 4-6 / 7+ blocks; stations 1 / 2 / 3 / 4 at 1-2 / 3-5 / 6-8
/ 9+ blocks, the first a passenger station, the last a cargo station when there are 3 or more; one davit.
"""
import glob
import json
import math
import os

from shapely.geometry import Point

from lattice import BANK, CELL, FREE, GATE, GREEN, OUT, PASTURE, RESERVED, RIM, STOREY, WATER

PIECE = {"pax": ("moor_station_pax", (4, 6)), "cargo": ("moor_station_cargo", (4, 5)),
         "line": ("moor_line_house", (3, 3)), "davit": ("moor_drop_cage_davit", (2, 2))}
MAST = "moor_signal_mast"
FACE_ROT = {"E": 0, "N": 1, "W": 2, "S": 3}
ZDIR = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}     # kit rot -> (di, dj) of the piece's +Z (inward)
XDIR = {0: (1, 0), 1: (0, -1), 2: (-1, 0), 3: (0, 1)}     # kit rot -> (di, dj) of the piece's +X
OVERHANG = 0.75          # m: the first row may stand this far out past the deck edge (else one row in: <= 2.25 m in)
BRIDGE_CLEAR = 5.0       # m along the face past a bridge's half width (its gate strip and the lashed neighbour)
# The STOWED swing girder lies along the face, not across it (bridges.json swing_girder; measured 2026-10-16):
# its model reaches 15.3 m (road 16.5) past the bridge centre to -along on the N and W faces and to +along on S
# and E, and 2.05 m (road 3.25) the other way.  BRIDGE_CLEAR alone left stations under the girder (SKY-040/-054:
# the berth walk blocked, audit walk/edge_blocked).
SWING_BACK = 16.3        # the girder's reach + 1 m (non-road; a road bridge adds SWING_ROAD)
SWING_FORE = 3.05
SWING_ROAD = 1.2
LAUNCH_CLEAR = 6.0
HOIST_CLEAR = 9.0
OK_GROUND = {RIM, FREE, GREEN, PASTURE}
RISE_MAX = {"pax": 4, "cargo": 4, "line": 2, "davit": 4}     # quarters the floor may stand over the rim's deck
OK_STRIP = {RIM, FREE, GREEN}
Q = 0.8
# a station's walk in its own frame (x across, z in from the rim; y 0 its floor): the street strip's node, through
# the hall (x 4.5: clear of the columns at x 3 / 7, the benches from x 5, the fare booth), the passage under the drive
# house, the middle rim gate (posts at x 2.97 / 6.03), out to the platform between the two berths (z -5)
# (past the middle gate the gantry's middle post stands at x 4.5, z -1.9: the walk passes it at x 3.7)
WALK_PAX = [(4.5, 15.5), (4.5, 12.75), (4.5, 9.75), (4.5, 7.0), (4.5, 4.0), (4.5, 1.2), (3.7, -0.7), (3.7, -3.2),
            (4.5, -5.0)]
WALK_CARGO = [(4.5, 14.0), (4.5, 12.0), (4.5, 9.0), (4.5, 6.0), (4.5, 3.0), (4.5, 1.2), (3.7, -0.7), (3.7, -3.4)]
ANCH = {}


def counts(blocks):
    b = int(blocks)
    lines = 2 if b <= 3 else (3 if b <= 6 else 4)
    st = 1 if b <= 2 else (2 if b <= 5 else (3 if b <= 8 else 4))
    kinds = ["pax"] * st
    if st >= 3:
        kinds[-1] = "cargo"
    return lines, kinds


def _rot_xz(rot, x, z):
    t = rot * math.pi / 2
    return x * math.cos(t) + z * math.sin(t), -x * math.sin(t) + z * math.cos(t)


def cells_of(o, rot, span):
    nx, nz = span
    X, Z = XDIR[rot], ZDIR[rot]
    return [(o[0] + a * X[0] + b * Z[0], o[1] + a * X[1] + b * Z[1]) for b in range(nz) for a in range(nx)]


def _face_rows(L, side):
    """the first row's index (i for N/S, j for E/W) and the coordinate of the face"""
    f = L.isl["faces"]
    if side == "N":
        d = float(f["N"]) - L.x0
        return (0 if d <= OVERHANG else 1), float(f["N"])
    if side == "S":
        e = L.x0 + CELL * L.nx - float(f["S"])
        return (L.nx - 1 if e <= OVERHANG else L.nx - 2), float(f["S"])
    if side == "E":
        d = float(f["E"]) - L.z0
        return (0 if d <= OVERHANG else 1), float(f["E"])
    e = L.z0 + CELL * L.nz - float(f["W"])
    return (L.nz - 1 if e <= OVERHANG else L.nz - 2), float(f["W"])


def _along(L, side, c):
    """a cell's centre along its face (z for N / S, x for E / W)"""
    x, _, z = L.centre(*c)
    return z if side in ("N", "S") else x


def _in_span(L, side, lo, hi):
    for a0, a1 in L.isl.get("face_spans", {}).get(side, []):
        if lo >= float(a0) + 0.5 and hi <= float(a1) - 0.5:
            return True
    return False


def _site(L, side, kind, along_cell, taken, relax=0):
    """the footprint of a `kind` piece on face `side` whose origin row cell is at `along_cell`, or None"""
    pid, span = PIECE[kind]
    rot = FACE_ROT[side]
    row, _ = _face_rows(L, side)
    o = (row, along_cell) if side in ("N", "S") else (along_cell, row)
    cells = cells_of(o, rot, span)
    strip = []
    back = []
    if kind in ("pax", "cargo"):
        X, Z = XDIR[rot], ZDIR[rot]
        strip = [(o[0] + a * X[0] + span[1] * Z[0], o[1] + a * X[1] + span[1] * Z[1]) for a in range(span[0])]
        # (and a second row behind it, open too: the walk climbs on from the doorway by a stair there, and no house
        # hems the doorway in)
        back = [(c[0] + Z[0], c[1] + Z[1]) for c in strip]
    for c in cells + strip + back:
        if not L.inb(*c) or c in taken:
            return None
    lat = [_along(L, side, c) for c in cells]
    lo, hi = min(lat) - CELL / 2, max(lat) + CELL / 2
    if not _in_span(L, side, lo, hi):
        return None
    X, Z = XDIR[rot], ZDIR[rot]
    for c in cells:
        p = int(L.plan[c])
        b = (c[0] - o[0]) * Z[0] + (c[1] - o[1]) * Z[1]       # (the row: 0 at the rim)
        x, _, z = L.centre(*c)
        if c in getattr(L, "bridge_cells", ()) or c in getattr(L, "lark_cells", ()):
            return None
        if p == OUT:
            if b > 1 or not L.outline.contains(Point(x, z)):
                return None
        elif p not in OK_GROUND:
            return None
        if L.block[c[0], c[1], :4].any():
            return None                                       # (a balloon's tether corridor)
    for c in strip + back:
        if int(L.plan[c]) not in (OK_STRIP | ({PASTURE} if relax else set())):
            return None
    # clear of the bridges (their gate strips, and the island lashed there), the launchers and the hoists
    swing = L.isl.get("bridge_style") == "swing_girder"
    for b in L.isl.get("bridges", []):
        if b["side"] == side:
            al_b = float(b["along"])
            hw = float(b.get("width", 3.6)) / 2 + (BRIDGE_CLEAR if not relax else 2.5)
            blo, bhi = al_b - hw, al_b + hw
            if swing:
                # the stowed girder's own reach along the face (never relaxed: it is solid steel on the walk)
                w = SWING_ROAD if float(b.get("width", 3.6)) >= 5.0 else 0.0
                if side in ("N", "W"):
                    blo = min(blo, al_b - SWING_BACK - w)
                    bhi = max(bhi, al_b + SWING_FORE + w)
                else:
                    blo = min(blo, al_b - SWING_FORE - w)
                    bhi = max(bhi, al_b + SWING_BACK + w)
            if hi > blo and lo < bhi:
                return None
    for la in L.isl.get("launchers", []):
        if la.get("side") == side:
            a = float(la["z"]) if side in ("N", "S") else float(la["x"])
            if hi > a - LAUNCH_CLEAR and lo < a + LAUNCH_CLEAR:
                return None
    for h in L.isl.get("hoists", []):
        for c in cells:
            x, _, z = L.centre(*c)
            if math.hypot(x - float(h["x"]), z - float(h["z"])) < HOIST_CLEAR:
                return None
    import walk
    qs = [walk.base_q(L, c) for c in cells]
    qstrip = [walk.base_q(L, c) for c in strip] or [max(qs)]
    # (and the row behind: a stair climbing on from the doorway there can't start below its own ground)
    qback = [walk.base_q(L, c) for c in back] or [0]
    q = max(max(qs), max(qstrip), max(qback))
    rim = min(walk.base_q(L, c) for c in cells[:span[0]])
    if q - rim > RISE_MAX.get(kind, 2) + 2 * min(relax, 1) + (4 if relax >= 2 and kind in ("pax", "cargo") else 0):
        return None                                   # (it would stand too high over the deck at the rim)
    return {"kind": kind, "piece": pid, "side": side, "rot": rot, "span": list(span), "origin": o, "cells": cells,
            "strip": strip, "back": back, "q0": q, "flat": max(qs) - min(qs) + max(qstrip) - min(qstrip),
            "along": (lo + hi) / 2}


def _candidates(L, side, kind, taken, relax=0):
    """every site on a face, best first: flat, low, nearest the middle of its span"""
    if side in ("N", "S"):
        n = L.nz
    else:
        n = L.nx
    out = []
    for a in range(n):
        s = _site(L, side, kind, a, taken, relax)
        if s:
            out.append(s)
    return out


def _score(s, used_faces, spread=None):
    pen = s["q0"] * 4.0 + s["flat"] * 3.0
    pen += 30.0 * used_faces.get(s["side"], 0)
    if spread:
        pen -= min(abs(s["along"] - a) for a in spread) * 0.02
    return pen


def _take(L, s, taken):
    if not hasattr(L, "pin_q"):
        L.pin_q = {}
        L.pin_s = {}
    for c in s["cells"]:
        L.plan[c] = OUT
    for n, c in enumerate(s["strip"]):
        L.plan[c] = RESERVED
        if 0 < n < len(s["strip"]) - 1:
            L.pin_q[c] = s["q0"]                      # (walknet: the doorway flat at the station's floor, or off the walk)
        else:
            L.pin_s[c] = s["q0"]                      # (its ends and the row behind: flat there, or a stair up from it)
    for c in s.get("back", []):
        L.plan[c] = RESERVED
        L.pin_s[c] = s["q0"]
    # (a cell's gap round every mooring: the next one never shares a wall)
    for c in s["cells"] + s["strip"] + s.get("back", []):
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                taken.add((c[0] + di, c[1] + dj))


def reserve(L):
    """choose and reserve the sites (call before the spine)"""
    L.moor = []
    L.moor_why = []
    lines, kinds = counts(L.isl.get("blocks", 3))
    taken = set()
    used = {}
    faces = [s for s in ("N", "S", "E", "W") if L.isl.get("face_spans", {}).get(s)]
    # the stations first (the biggest), each on another face where it can
    for n, kind in enumerate(kinds):
        best = None
        for relax in (0, 1, 2):
            for side in faces:
                for s in _candidates(L, side, kind, taken, relax):
                    sc = _score(s, used) + 50.0 * relax
                    if best is None or sc < best[0]:
                        best = (sc, s)
            if best:
                break
        if best is None:
            L.moor_why.append("no site for %s %d" % (kind, n))
            continue
        s = best[1]
        _take(L, s, taken)
        used[s["side"]] = used.get(s["side"], 0) + 1
        L.moor.append(s)
        if n == 0:
            # the davit beside the first passenger station, on the same face (either side of it)
            dv = None
            rot = s["rot"]
            X = XDIR[rot]
            o = s["origin"]
            span = s["span"][0]
            taken2 = taken - set((cc[0] + di, cc[1] + dj) for cc in s["cells"] for di in (-1, 0, 1) for dj in (-1, 0, 1))
            offs = [span, -2] + [k for g in range(1, 10) for k in (span + g, -2 - g)]
            for relax in (0, 1):
                for off in offs:
                    c = (o[0] + off * X[0], o[1] + off * X[1])
                    a = c[1] if s["side"] in ("N", "S") else c[0]
                    d = _site(L, s["side"], "davit", a, taken2, relax)
                    if d and not (set(d["cells"]) & set(s["cells"])):
                        dv = d
                        break
                if dv:
                    break
            if dv:
                _take(L, dv, taken)
                dv["beside"] = len(L.moor) - 1
                L.moor.append(dv)
            else:
                L.moor_why.append("no davit site")
    # the line houses, spread round the faces
    for n in range(lines):
        best = None
        spread = [m["along"] for m in L.moor]
        for relax in (0, 1):
            for side in faces:
                for s in _candidates(L, side, "line", taken, relax):
                    sc = _score(s, used, spread) + 50.0 * relax
                    if best is None or sc < best[0]:
                        best = (sc, s)
            if best:
                break
        if best is None:
            L.moor_why.append("no site for line house %d" % n)
            continue
        _take(L, best[1], taken)
        used[best[1]["side"]] = used.get(best[1]["side"], 0) + 1
        L.moor.append(best[1])
    L.moor_cells = set(c for m in L.moor for c in m["cells"])


def _anchors(kit, pid):
    if pid not in ANCH:
        ANCH[pid] = (kit["pieces"].get(pid) or {}).get("anchors", {})
    return ANCH[pid]


def emit(L, o, kit):
    """the pieces (after kitmap.translate: kit ids, records (kid, i, j, level, rot, flags, mount, palette, epoch))"""
    import pick
    for m in L.moor:
        # the height: the street strip's (walknet pins it there: L.pin_q); the davit stands at its station's
        q = int(m["q0"])
        if "beside" in m and "q" in L.moor[m["beside"]]:
            q = max(q, int(L.moor[m["beside"]]["q"]))
        m["q"] = q
        lv, qr = q // 4, q % 4
        flags = (qr & 3) << 4
        pal = 0
        i, j = m["origin"]
        o.recs.append((m["piece"], i, j, lv, m["rot"], flags, 0, pal, 4))
        # the piece's own floor: whole-cell paving under it (the hall, the passage, the gates; the line house's and
        # the davit's ground), at its height -- the deck is tucked under it by the runtime
        own = set(m["cells"])
        for c in m["cells"]:
            o.recs.append(("pave_plaza", c[0], c[1], lv, 0, flags, 0, pal, 4))
            # retaining walls where the floor stands over the ground outside it (pick.py's plinth stacks)
            for kr, (di, dj) in ZDIR.items():
                n = (c[0] + di, c[1] + dj)
                if n in own or n in m["strip"]:
                    continue
                ny = pick.walk_ground(L, n) if L.inb(*n) and int(L.plan[n]) != OUT else float(L.ground[c])
                drop = q * Q - max(ny, -12.8)
                if drop <= 0.3:
                    continue
                for t in range(int(math.ceil(drop / 1.6))):
                    qq = q - 2 * t
                    if qq < 0:
                        break
                    o.recs.append(("plinth_t", c[0], c[1], qq // 4, kr, (qq % 4) << 4, 1, pal, 4))
        if m["kind"] == "line":
            # the signal mast on the roof seat (x 3.0, z 1.1 in the house's frame: the next cell along +X, face-mounted
            # +1.5 z; y = the roof 6.4 m up)
            X = XDIR[m["rot"]]
            c = (i + X[0], j + X[1])
            q2 = q + 8
            o.recs.append((MAST, c[0], c[1], q2 // 4, m["rot"], ((q2 % 4) & 3) << 4, 1, pal, 4))


def _xf(L, m, x, y, z):
    """a point in the piece's frame -> the island frame"""
    i, j = m["origin"]
    cx, _, cz = L.centre(i, j)
    rx, rz = _rot_xz(m["rot"], x, z)
    return [round(cx + rx, 3), round(m["q"] * Q + y, 3), round(cz + rz, 3)]


def walk(L):
    """each station's walk on the twin's graph (the audit walks it with the capsule; islanders use it)"""
    W = L.walk
    idx = getattr(L, "walk_index", {}) or {}
    for n, m in enumerate(L.moor):
        m["walk"] = []
        m["connected"] = False
        if m["kind"] not in ("pax", "cargo"):
            continue
        start = None
        for c in m["strip"][1:3]:
            k = idx.get(("g", c[0], c[1]))
            if k is not None and c in L.q and c not in L.stair and int(L.q[c]) == m["q"]:
                start = (k, c)
                break
        if start is None:
            continue                                  # (its doorway is off the walk: no walk through it either)
        pts = WALK_PAX if m["kind"] == "pax" else WALK_CARGO
        prev = start[0]
        for (x, z) in pts:
            p = _xf(L, m, x, 0.0, z)
            W["nodes"].append([round(p[0], 2), round(p[1], 2), round(p[2], 2), "ground"])
            k = len(W["nodes"]) - 1
            m["walk"].append(k)
            if prev is not None:
                W["edges"].append([prev, k])
            prev = k
        m["connected"] = start is not None


# lamps for the warren's light field and flares (kitmap.lights' kinds): the stations' lit gate headers and the hall's
# arcade lamps, the line house's gate lamps
LAMPS = {"pax": [("fluoro", -0.885, 2.6, -1.35), ("fluoro", 4.5, 2.6, -1.35), ("fluoro", 9.885, 2.6, -1.35),
                 ("lantern", 0.6, 3.05, 14.3), ("lantern", 4.0, 3.05, 14.3), ("lantern", 7.6, 3.05, 14.3)],
         "cargo": [("fluoro", -0.885, 2.6, -1.35), ("fluoro", 4.5, 2.6, -1.35), ("fluoro", 9.885, 2.6, -1.35)],
         "line": [("lantern", 1.6, 2.9, -1.55), ("lantern", 4.4, 2.9, -1.55)]}


def lights(L):
    out = []
    for m in L.moor:
        if "q" not in m:
            continue
        for kind, x, y, z in LAMPS.get(m["kind"], []):
            p = _xf(L, m, x, y, z)
            out.append([round(p[0], 2), round(p[1], 2), round(p[2], 2), kind, "#ffe2b0"])
    return out


def doc(L, kit):
    out = []
    for m in L.moor:
        if "q" not in m:
            continue
        an = {}
        for name, a in _anchors(kit, m["piece"]).items():
            an[name] = _xf(L, m, float(a[0]), float(a[1]), float(a[2]))
        if m["kind"] == "line":
            ma = _anchors(kit, MAST).get("bell")
            if ma:
                X = XDIR[m["rot"]]
                an["bell"] = _xf(L, m, 3.0 + float(ma[0]), 6.4 + float(ma[1]), 1.5 + float(ma[2]))
        t = m["rot"] * math.pi / 2
        # the rim fence's gap in front of it (sky_island.gd _build_fence: no fence box whose middle lies within
        # width / 2 + 1.5 m of `at`: here the piece's own half width)
        fx = (m["span"][0] * CELL - CELL) / 2
        fp = _xf(L, m, fx, 0.0, -1.5)
        gap = {"at": [fp[0], fp[2]], "width": round(m["span"][0] * CELL - CELL, 2), "mooring": m["kind"]}
        out.append({"fence_gap": gap, "kind": m["kind"], "piece": m["piece"], "side": m["side"], "rot": m["rot"], "yaw": round(t, 6),
                    "cell": list(m["origin"]), "span": m["span"], "q": m["q"], "origin": _xf(L, m, 0.0, 0.0, 0.0),
                    "out": [round(-math.sin(t), 6), 0.0, round(-math.cos(t), 6)], "along": round(m["along"], 2),
                    "anchors": an, "walk": m.get("walk", []), "connected": m.get("connected", False),
                    **({"beside": m["beside"]} if "beside" in m else {})})
    return out


def stats(L):
    k = {}
    for m in L.moor:
        k[m["kind"]] = k.get(m["kind"], 0) + 1
    return {"placed": k, "why": L.moor_why,
            "stations_connected": sum(1 for m in L.moor if m["kind"] in ("pax", "cargo") and m.get("connected")),
            "stations": sum(1 for m in L.moor if m["kind"] in ("pax", "cargo")),
            "q": sorted(set(m.get("q", -1) for m in L.moor))}


def write_index(out_dir, dest):
    """every island's moorings (from the twins) in one small file for the runtime"""
    idx = {}
    for p in sorted(glob.glob(os.path.join(out_dir, "SKY-*.json"))):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        ms = d.get("moorings")
        if ms is None:
            continue
        idx[d["island"]] = [{k: v for k, v in m.items() if k != "walk"} for m in ms]
    json.dump({"version": 1, "about": "tools/sky/warren/moorings.py: each island's line houses, gondola top stations "
               "and drop-cage davit (island frame: +X south, +Y up, +Z west; anchors from the warren kit's pieces.json)",
               "islands": idx}, open(dest, "w"), separators=(",", ":"))
    return len(idx)
