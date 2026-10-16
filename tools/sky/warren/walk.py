"""walk.py -- what you can walk on, and the WALK CHECK (2026-10-15: "everything needs to be traversable").

The player: a ~1.8 m capsule with NO step-up (a lip of at most ~0.3 m), no jumping; it climbs only ramps and stairs
(pieces with ramp collision), and a stair only along its axis -- in at its foot, out at its head (its sides are a lip
mid-ramp).  The ground itself is laid out by walknet.py (the network built path by path); this module holds the
shared pieces and the checks:

  walk_cells(L)            the open walkable ground
  base_q(L, c)             the lowest paving over the deck, in half storeys (quarters, even)
  edge / connected(L,a,b)  the walk graph's rule (flat at one height; stairs along their axis)
  check(L, travel)         BFS from the arrival: the doors, shops, public cells and stairs that fail
  physical(L, recs, ...)   the check again from the placed pieces (paving heights, pieces.json "ramp" quads, a 0.3 m
                           step at each shared edge, the doorways), openings.py's blocked ways excluded
  carve, green_paths, ground_y
"""
import heapq
import os
import math
from collections import deque

from lattice import ARTERY, BANK, GATE, GREEN, LANE, MAIN, PASTURE, PLAZA, RESERVED, RIM, WALKABLE, WATER

Q = 0.8                                                  # a quarter storey
FACE = {0: (0, -1), 1: (-1, 0), 2: (0, 1), 3: (1, 0)}    # (pick.FACE)
ROT_OF = {v: k for k, v in FACE.items()}
OPP = {0: 2, 1: 3, 2: 0, 3: 1}
# (a rise of 2 quarters at most within two cells: every flight has its landing before the next -- no runs of stairs
# needing whole wide flights on a steep slope)
NEAR2 = [(di, dj) for di in range(-2, 3) for dj in range(-2, 3) if 0 < abs(di) + abs(dj) <= 2]
PUBLIC_W = {RIM, BANK, GREEN, PASTURE, MAIN, PLAZA, GATE, LANE, RESERVED, ARTERY}


def walk_cells(L):
    """the open walkable ground (courts included: a house's own, reached through its door)"""
    out = set()
    for i in range(L.nx):
        for j in range(L.nz):
            p = int(L.plan[i, j])
            if p in WALKABLE and p != WATER and not L.occ[i, j, int(L.gk[i, j])]:
                out.add((i, j))
    return out


def base_q(L, c):
    """the lowest paving over the deck at c, in half storeys (2 quarters): terraces 1.6 m apart, every rise a
    steps_up flight (fewer, wider plateaus than quarter-by-quarter grading)"""
    t = max(0, int(math.ceil(float(L.ground[c]) / Q - 0.05)))
    return t + (t & 1)


def _lipschitz(L, q, cells=None):
    heap = [(-v, c) for c, v in (q.items() if cells is None else ((c, q[c]) for c in cells))]
    heapq.heapify(heap)
    while heap:
        v, c = heapq.heappop(heap)
        v = -v
        if v != q[c]:
            continue
        for d in (NEAR2 if os.environ.get("WALK_NEAR", "2") == "2" else FACE.values()):
            n = (c[0] + d[0], c[1] + d[1])
            if n in q and q[n] < v - 2:
                q[n] = v - 2
                heapq.heappush(heap, (-q[n], n))


def rooms_of(L, lot, c):
    return [k for k in range(int(L.gk[c]), L.L) if L.occ[c[0], c[1], k] and L.lot[c] == lot["id"]]


def carve(L, starts, goal, max_len=12):
    """a passage from the reached ground to a shut-in place: the shortest run of non-walkable cells between them,
    cleared (whole columns) and made LANE.  starts: cells to reach; goal(c) -> True for the reached ground"""
    par = {c: None for c in starts}
    dq = deque(starts)
    hit = None
    while dq:
        c = dq.popleft()
        for d in FACE.values():
            n = (c[0] + d[0], c[1] + d[1])
            if not L.inb(*n) or n in par or L.plan[n] in (WATER, 0, 1) or L.block[n[0], n[1], :1].any():
                continue
            par[n] = c
            if goal(n):
                hit = n
                dq.clear()
                break
            dq.append(n)
    if hit is None:
        return 0
    path, c = [], par[hit]
    while c is not None and c not in starts:
        path.append(c)
        c = par[c]
    if len(path) > max_len:
        return 0
    for c in path:
        for k in range(L.L):
            if L.occ[c[0], c[1], k]:
                L.clear(c[0], c[1], k)
        L.plan[c] = LANE
        L.W.add(c)
        L.q[c] = max(0, base_q(L, c))
    _lipschitz(L, L.q, path)
    for c in path:
        _lipschitz(L, L.q, [c])
    return len(path)


def edge(L, c, rot):
    """(lo, hi) quarters of cell c's surface at its edge toward FACE[rot]"""
    v = L.q[c]
    s = L.stair.get(c)
    if not s:
        return (v, v)
    r0, r = s
    if rot == r0:
        return (v + r, v + r)
    if rot == OPP[r0]:
        return (v, v)
    return (v, v + r)


def connected(L, a, b):
    """the player crosses from a to b: flat edges at one height, a stair only at its foot (from behind) and its head
    (onward); beside a stair only the next stair of the same wide flight (same base, rise, direction)"""
    rot = ROT_OF[(b[0] - a[0], b[1] - a[1])]
    sa, sb = L.stair.get(a), L.stair.get(b)
    for c, s, r in ((a, sa, rot), (b, sb, OPP[rot])):
        if s and r not in (s[0], OPP[s[0]]):
            # (a side of a stair: a lip mid-ramp -- only its twin in the flight beside it)
            o = b if c is a else a
            so = L.stair.get(o)
            return bool(so) and so == s and L.q[o] == L.q[c]
    ea = edge(L, a, rot)
    eb = edge(L, b, OPP[rot])
    return ea[0] == eb[0] and ea[1] == eb[1] or (ea[0] == ea[1] == eb[0] == eb[1])


def check(L, travel):
    """BFS over the ground from the travel cell: what is reached, which doors and stairs fail"""
    seen = {travel}
    dq = deque([travel])
    while dq:
        c = dq.popleft()
        for d in FACE.values():
            n = (c[0] + d[0], c[1] + d[1])
            if n in L.W and n not in seen and connected(L, c, n):
                seen.add(n)
                dq.append(n)
    L.reached = seen
    fails = {"doors": [], "shops": [], "cells": [], "stairs": []}
    for lot in L.lots:
        if not lot.get("door"):
            continue
        c, rot = lot["door"]
        d = FACE[rot]
        m = (c[0] + d[0], c[1] + d[1])
        e = edge(L, m, OPP[rot]) if m in L.W else None
        sm = L.stair.get(m)
        if sm and sm[0] != OPP[rot] and not (m in getattr(L, "door_feet", ()) and sm[0] == rot):
            e = None                              # (a stair passing the door sideways: a lip)
        if m not in seen or e is None or not (e[0] <= 4 * lot["door_k"] <= e[1]):
            fails["doors"].append((lot["id"], c, m))
        for sc in lot.get("shop_cells", ()):
            if not any((sc[0] + dd[0], sc[1] + dd[1]) in seen for dd in FACE.values()):
                fails["shops"].append((lot["id"], sc))
    for c in L.W:
        if L.plan[c] in PUBLIC_W and c not in seen:
            fails["cells"].append(c)
    for c, (r0, r) in L.stair.items():
        # both ends: the top meets the cell it climbs to, the foot meets some cell at the stair's base
        top = (c[0] + FACE[r0][0], c[1] + FACE[r0][1])
        back = (c[0] - FACE[r0][0], c[1] - FACE[r0][1])
        foot_ok = (back in L.W and connected(L, back, c)) or c in getattr(L, "door_feet", ())
        top_ok = c in L.stoop or (top in L.W and connected(L, c, top))
        if not (top_ok and foot_ok):
            fails["stairs"].append(c)
    return fails


def ground_y(L, c):
    """the walking surface at a cell (graded quarters, else the deck)"""
    if c in getattr(L, "q", {}):
        return L.q[c] * Q
    return float(L.ground[c])


def green_paths(L):
    """paved paths through the greens and banks: from each run of the green's street edge (its middle) and from the
    pond shore to one another, along the shortest ways inside the green (made LANE: paved, no planting)"""
    seen = set()
    greenish = (GREEN, BANK, PASTURE)
    streetish = (MAIN, PLAZA, GATE, LANE, ARTERY, RIM, RESERVED)
    made = 0
    for i in range(L.nx):
        for j in range(L.nz):
            if L.plan[i, j] not in greenish or (i, j) in seen:
                continue
            comp = []
            dq = deque([(i, j)])
            seen.add((i, j))
            while dq:
                c = dq.popleft()
                comp.append(c)
                for d in FACE.values():
                    n = (c[0] + d[0], c[1] + d[1])
                    if L.inb(*n) and n not in seen and L.plan[n] in greenish and not L.occ[n[0], n[1], int(L.gk[n])]:
                        seen.add(n)
                        dq.append(n)
            if len(comp) < 6:
                continue
            cs = set(comp)
            # the entries: green cells touching a street, grouped in runs along the edge (one per run)
            edge = [c for c in comp if any(L.inb(c[0] + d[0], c[1] + d[1]) and L.plan[c[0] + d[0], c[1] + d[1]] in streetish
                                          for d in FACE.values())]
            runs, done = [], set()
            for c in edge:
                if c in done:
                    continue
                run, dq = [], deque([c])
                done.add(c)
                while dq:
                    a = dq.popleft()
                    run.append(a)
                    for d in FACE.values():
                        n = (a[0] + d[0], a[1] + d[1])
                        if n in done or n not in cs or n not in edge:
                            continue
                        done.add(n)
                        dq.append(n)
                runs.append(sorted(run)[len(run) // 2])
            # the pond shore: one cell per pond side
            shore = [c for c in comp if any(L.inb(c[0] + d[0], c[1] + d[1]) and L.plan[c[0] + d[0], c[1] + d[1]] == WATER
                                           for d in FACE.values())]
            anchors = runs[:8] + (shore[len(shore) // 2: len(shore) // 2 + 1] if shore else [])
            if len(anchors) < 2:
                continue
            # a BFS tree from the first anchor; the paths to the others
            par = {anchors[0]: None}
            dq = deque([anchors[0]])
            while dq:
                a = dq.popleft()
                for d in FACE.values():
                    n = (a[0] + d[0], a[1] + d[1])
                    if n in cs and n not in par:
                        par[n] = a
                        dq.append(n)
            for t in anchors[1:]:
                c = t
                while c is not None and c in par:
                    if L.plan[c] != LANE and not (L.plan[c] == BANK and c in shore and c != t):
                        L.plan[c] = LANE
                        made += 1
                    c = par[c]
    return made


# ---------------------------------------------------------------- the physical check (the placed kit pieces)
STEP = 0.3                                               # the player's step: a lip of at most 0.3 m


def _ramp_y(quads, x, z):
    """the ramp's height at local (x, z): the quad under the point (else the nearest), linear over its triangles"""
    best = None
    for qd in quads:
        xs = [p[0] for p in qd]
        zs = [p[2] for p in qd]
        cx = min(max(x, min(xs)), max(xs))
        cz = min(max(z, min(zs)), max(zs))
        dd = (cx - x) ** 2 + (cz - z) ** 2
        if best is None or dd < best[0]:
            best = (dd, qd, cx, cz)
    _, qd, x, z = best
    for t in ((qd[0], qd[1], qd[2]), (qd[0], qd[2], qd[3])):
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = t
        det = (z1 - z2) * (x0 - x2) + (x2 - x1) * (z0 - z2)
        if abs(det) < 1e-9:
            continue
        a = ((z1 - z2) * (x - x2) + (x2 - x1) * (z - z2)) / det
        b = ((z2 - z0) * (x - x2) + (x0 - x2) * (z - z2)) / det
        if a >= -1e-6 and b >= -1e-6 and a + b <= 1 + 1e-6:
            return a * y0 + b * y1 + (1 - a - b) * y2
    return sum(p[1] for p in qd) / 4.0


def physical(L, recs, pieces, blocked=()):
    """the walk check again, from the placed pieces themselves: each walk cell's surface is its paving (flat) or its
    stair's ramp quads (pieces.json "ramp", turned by the kit rot); two cells join where their surfaces meet within
    STEP at the middle of the shared edge (the way a player walks from centre to centre); a door where the outside
    surface at the door's edge meets the floor within STEP.  Returns the stats (and L.phys_reached)."""
    surf = {}
    for r in recs:
        kid, i, j, lv, kr, flags = r[:6]
        if (i, j) not in L.W:
            continue
        p = pieces.get(kid, {})
        kind = p.get("kind")
        y = 3.2 * lv + 0.8 * ((flags >> 4) & 3)
        if kind == "stair" and p.get("ramp"):
            surf[(i, j)] = ("ramp", y, kr, p["ramp"])
        elif kind == "ground" and surf.get((i, j), ("",))[0] != "ramp":
            surf[(i, j)] = ("flat", y)

    def h(c, rot):
        s = surf.get(c)
        if s is None:
            return None
        if s[0] == "flat":
            return s[1]
        _, y, kr, quads = s
        if rot is None:
            return y + _ramp_y(quads, 0.0, 0.0)
        dx, dz = FACE[rot][0] * 1.5, FACE[rot][1] * 1.5
        th = -kr * math.pi / 2                     # (world -> local: the kit rot undone)
        lx = dx * math.cos(th) + dz * math.sin(th)
        lz = -dx * math.sin(th) + dz * math.cos(th)
        return y + _ramp_y(quads, lx, lz)

    t = L.travel_cell
    seen = {t}
    dq = deque([t])
    bad = 0
    while dq:
        c = dq.popleft()
        for rot, d in FACE.items():
            n = (c[0] + d[0], c[1] + d[1])
            if n not in L.W or n in seen:
                continue
            a, b = h(c, rot), h(n, OPP[rot])
            if a is None or b is None or abs(a - b) > STEP or (c, n) in blocked or (n, c) in blocked:
                continue
            seen.add(n)
            dq.append(n)
    L.phys_reached = seen
    L.phys_h = h
    doors = ok = 0
    fails = []
    for lot in L.lots:
        if not lot.get("door"):
            continue
        c, rot = lot["door"]
        m = (c[0] + FACE[rot][0], c[1] + FACE[rot][1])
        doors += 1
        e = h(m, OPP[rot]) if m in seen else None
        if e is not None and abs(e - 3.2 * lot["door_k"]) <= STEP and lot["id"] not in getattr(L, "doors_blocked", ()):
            ok += 1
        elif len(fails) < 8:
            fails.append((lot["id"], c, m, None if e is None else round(e, 2), round(3.2 * lot["door_k"], 2),
                          L.q.get(m), L.stair.get(m), str(surf.get(m))[:40], [r[:6] for r in recs if (r[1], r[2]) == m and pieces.get(r[0], {}).get("kind") in ("ground", "stair")]))
    pub = [c for c in L.W if L.plan[c] in PUBLIC_W]
    return {"doors": doors, "doors_reached": ok, "public_cells": len(pub),
            "public_reached": sum(1 for c in pub if c in seen), "no_surface": sum(1 for c in L.W if c not in surf),
            "no_surface_at": [(c, int(L.plan[c]), sorted(set(r[0] for r in recs if (r[1], r[2]) == c))[:4]) for c in sorted(L.W) if c not in surf][:4],
            "door_failures": fails,
            "arrival": [t, str(surf.get(t))[:24], [(n, str(surf.get(n))[:24], sorted(set(r[0] for r in recs if (r[1], r[2]) == n)))
                                                   for n in ((t[0] + d[0], t[1] + d[1]) for d in FACE.values())]],
            "pass": ok == doors and all(c in seen for c in pub)}
