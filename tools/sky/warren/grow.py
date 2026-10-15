"""grow.py -- E1 (the founding plan: lanes, lots, the oldest masonry) and E2-E4 (centuries of accretion), generic and
driven by a civilization's params (civ/<id>.py); r4_design §2.

Lanes grow from the spine in the civ's grammar (a branching tree with bends and dead ends, or a jittered grid); the
free land between them is cut into lots, each with frontage (a door); courtyard civs keep courts open to the sky.  Then
each epoch: rooms rise on roofs (flush or set back), jetty over lanes, bridge narrow lanes (sabats: covered passages),
towers shoot up, courts fill (where the civ allows) -- everything checked for support (settle) and access.
"""
import math
from collections import deque

from lattice import (ARTERY, CIVIC, COURT, FREE, GATE, HOME, LANE, LOT, MAIN, OUT, PLAZA, RESERVED, RIM, SHOP, STREETS,
                     WALKABLE, WORK)
from pick import h01
from spine import DIRS, bfs_dist, connect_leftovers, route

LANEISH = {LANE, ARTERY}


# ------------------------------------------------------------------ lanes
def grow_lanes_tree(L, rng, p):
    """medina-like lanes: walkers set off from the streets into the free land, bending every few cells, branching,
    ending blind (cul-de-sacs) or meeting another lane; then any block too deep gets a lane cut to it"""
    plan = L.plan
    bend = p.get("bend_cells", (3, 7))
    edge = [(i, j, di, dj) for i in range(L.nx) for j in range(L.nz) if plan[i, j] in STREETS | {GATE}
            for di, dj in DIRS if L.inb(i + di, j + dj) and plan[i + di, j + dj] == FREE]
    rng.shuffle(edge)
    spacing = p.get("lane_spacing", 6)
    taken = []
    walkers = []
    for (i, j, di, dj) in edge:
        if any(abs(i - a) + abs(j - b) < spacing for a, b in taken):
            continue
        taken.append((i, j))
        walkers.append((i + di, j + dj, di, dj, p.get("lane_len", 14), 0))
    width2 = p.get("artery_share", 0.0)
    while walkers:
        i, j, di, dj, left, depth = walkers.pop()
        seg = rng.randint(*bend)
        cls = ARTERY if depth == 0 and rng.random() < width2 else LANE
        while left > 0:
            if not L.inb(i, j) or plan[i, j] != FREE:
                break
            plan[i, j] = cls
            if cls == ARTERY:                          # (a souq artery: two cells wide)
                pi, pj = (dj, di)
                if L.inb(i + pi, j + pj) and plan[i + pi, j + pj] == FREE:
                    plan[i + pi, j + pj] = ARTERY
            left -= 1
            seg -= 1
            ni, nj = i + di, j + dj
            ahead = plan[ni, nj] if L.inb(ni, nj) else OUT
            if ahead in WALKABLE and ahead != RIM:
                if rng.random() < p.get("loop", 0.5):
                    break                              # (joined: a loop)
                break
            if ahead != FREE:
                break
            if seg <= 0:
                seg = rng.randint(*bend)
                turn = rng.choice((-1, 1))
                odi, odj = di, dj
                di, dj = (-dj * turn, di * turn)           # (a bend)
                if rng.random() < p.get("branch", 0.35) and depth < 3:
                    walkers.append((i + odi, j + odj, odi, odj, max(4, left // 2), depth + 1))   # (and a branch on)
                ni, nj = i + di, j + dj
                if not L.inb(ni, nj) or plan[ni, nj] != FREE:
                    break
            i, j = ni, nj
    # blind alleys: some lanes end short of a meeting, the civ's dead-end share (derbs)
    # every block at most p["block_cells"] across: cut a lane from its deepest cell to the nearest street
    limit = p.get("block_cells", 14) // 2
    for _ in range(200):
        streets = [(i, j) for i in range(L.nx) for j in range(L.nz) if plan[i, j] in STREETS | {GATE}]
        d = bfs_dist(L, streets, lambda q: q == FREE)
        deep = [(v, c) for c, v in d.items() if plan[c] == FREE and v > limit]
        if not deep:
            break
        deep.sort(reverse=True)
        a = deep[0][1]
        goal = set(c for c in streets)
        path = route(L, a, goal, turn_cost=p.get("cut_turn", 3.0))
        if not path:
            break
        # bend it: a lane cut straight is a modern cut; jog it once in the middle
        for c in path:
            if plan[c] == FREE:
                plan[c] = LANE


def grow_lanes_grid(L, rng, p):
    """a jittered alley grid (Kowloon: the plot lines of 350 buildings, 1-2 m alleys, every 4-7 cells)"""
    plan = L.plan
    lo, hi = p.get("grid_cells", (4, 7))
    xs, x = [], rng.randint(1, lo)
    while x < L.nx:
        xs.append(x)
        x += rng.randint(lo, hi)
    zs, z = [], rng.randint(1, lo)
    while z < L.nz:
        zs.append(z)
        z += rng.randint(lo, hi)
    brk = p.get("break", 0.0)
    for axis, lines, length in ((0, xs, L.nz), (1, zs, L.nx)):
        for x in lines:
            t = 0
            off = 0
            gap = 0
            while t < length:
                if rng.random() < p.get("jog", 0.12):
                    # a dog-leg: the old plot lines aren't straight -- step the alley across, keeping it joined
                    step = rng.choice((-1, 1))
                    if abs(off + step) <= 2:
                        c = (x + off + step, t) if axis == 0 else (t, x + off + step)
                        if L.inb(*c) and plan[c] == FREE:
                            plan[c] = LANE
                        off += step
                if gap <= 0 and rng.random() < brk:
                    gap = rng.randint(2, 5)              # (a building straddles the old line: the alley stops)
                c = (x + off, t) if axis == 0 else (t, x + off)
                if gap > 0:
                    gap -= 1
                elif L.inb(*c) and plan[c] == FREE:
                    plan[c] = LANE
                t += 1
    # a few alleys end blind (the city was never planned)
    for _ in range(int(p.get("blind", 0.15) * (len(xs) + len(zs)) * 3)):
        i, j = rng.randrange(L.nx), rng.randrange(L.nz)
        if plan[i, j] == LANE:
            nb = sum(1 for di, dj in DIRS if L.inb(i + di, j + dj) and plan[i + di, j + dj] in WALKABLE)
            if nb == 2:
                plan[i, j] = FREE


# ------------------------------------------------------------------ lots
def cut_lots(L, rng, p):
    """the free land into lots by grown seeds; every lot fronts a lane or street (merged into a neighbour if not)"""
    plan = L.plan
    free = [(i, j) for i in range(L.nx) for j in range(L.nz) if plan[i, j] == FREE]
    rng.shuffle(free)
    lot_cells = p.get("lot_cells", (8, 24))
    sp = max(2, int(math.sqrt(sum(lot_cells) / 2)))
    seeds = []
    for c in free:
        if all(abs(c[0] - s[0]) + abs(c[1] - s[1]) >= sp for s in seeds):
            seeds.append(c)
    owner = {}
    q = deque()
    sizes = []
    for n, s in enumerate(seeds):
        owner[s] = n
        q.append(s)
        sizes.append(1)
    cap = [rng.randint(*lot_cells) for _ in seeds]
    while q:
        c = q.popleft()
        n = owner[c]
        for di, dj in (DIRS if rng.random() < 0.5 else DIRS[::-1]):
            m = (c[0] + di, c[1] + dj)
            if L.inb(*m) and plan[m] == FREE and m not in owner:
                if sizes[n] >= cap[n]:
                    continue
                owner[m] = n
                sizes[n] += 1
                q.append(m)
    # leftovers (lots all full): give them to a neighbour, or a new lot
    for c in free:
        if c not in owner:
            for di, dj in DIRS:
                m = (c[0] + di, c[1] + dj)
                if m in owner:
                    owner[c] = owner[m]
                    break
            else:
                owner[c] = len(cap)
                cap.append(1)
    groups = {}
    for c, n in owner.items():
        groups.setdefault(n, []).append(c)
    # frontage
    def front(cells):
        out = []
        for c in cells:
            for k, (di, dj) in enumerate(DIRS):
                m = (c[0] + di, c[1] + dj)
                if L.inb(*m) and plan[m] in STREETS | {GATE, RIM, RESERVED}:
                    out.append((c, m))
        return out
    merged = True
    while merged:
        merged = False
        for n in list(groups):
            if n not in groups:
                continue
            if not front(groups[n]):
                nb = None
                for c in groups[n]:
                    for di, dj in DIRS:
                        m = (c[0] + di, c[1] + dj)
                        if m in owner and owner[m] != n and owner[m] in groups:
                            nb = owner[m]
                            break
                    if nb is not None:
                        break
                if nb is not None:
                    for c in groups[n]:
                        owner[c] = nb
                    groups[nb] += groups.pop(n)
                    merged = True
    for n, cells in groups.items():
        fr = front(cells)
        lot = {"id": len(L.lots), "cells": cells, "court": [], "front": fr, "use": HOME, "kind": "house"}
        for c in cells:
            plan[c] = LOT
            L.lot[c] = lot["id"]
        L.lots.append(lot)


def courts(L, rng, p):
    """courtyard civs: the lot's inner cells (all four neighbours its own) become its court, open to the sky"""
    if not p.get("courts"):
        return
    cmin = p.get("court_min_lot", 10)
    for lot in L.lots:
        if len(lot["cells"]) < cmin or lot["kind"] != "house":
            continue
        cs = set(lot["cells"])
        inner = [c for c in lot["cells"] if all((c[0] + di, c[1] + dj) in cs for di, dj in DIRS)]
        if not inner:
            continue
        rng.shuffle(inner)
        want = max(1, min(len(inner), int(len(lot["cells"]) * p.get("court_share", 0.18))))
        court = [inner[0]]
        for c in inner[1:]:
            if len(court) >= want:
                break
            if any(abs(c[0] - a[0]) + abs(c[1] - a[1]) == 1 for a in court):
                court.append(c)
        for c in court:
            L.plan[c] = COURT
        lot["court"] = court


# ------------------------------------------------------------------ E1: the oldest masonry
def found(L, rng, p):
    lo, hi = p.get("e1_levels", (2, 3))
    for lot in L.lots:
        u = L.new_unit(lot["use"], lot["id"])
        lot["unit"] = u
        h = rng.randint(lo, hi) if lot["kind"] != "civic" else p.get("civic_levels", 2)
        for c in lot["cells"]:
            if L.plan[c] == COURT:
                continue
            g = int(L.gk[c]) + int(L.lift[c])
            for k in range(g, min(g + h, L.L)):
                if not L.block[c[0], c[1], k]:
                    L.set_room(c[0], c[1], k, u, 1)


# ------------------------------------------------------------------ E2-E4: centuries
def accrete(L, rng, p, epoch):
    e = p.get("epochs", {}).get(epoch, {})
    maxk = p.get("max_levels", 4)
    # rise: a lot (or its inner part: a setback) gets another storey
    for lot in L.lots:
        if rng.random() >= e.get("rise", 0.0):
            continue
        cells = [c for c in lot["cells"] if L.plan[c] != COURT]
        if not cells:
            continue
        cap = lot.get("cap", maxk)
        setback = rng.random() < e.get("setback", 0.3)
        front = set(c for c, _ in lot["front"])
        for c in cells:
            if setback and c in front and len(cells) > 3:
                continue
            k = L.top(*c) + 1
            if k <= 0 or k >= min(cap + int(L.gk[c]), L.L):
                continue
            if L.free_at(c[0], c[1], k) and (L.occ[c[0], c[1], k - 1] or k == L.gk[c]):
                L.set_room(c[0], c[1], k, lot["unit"], epoch)
    # towers: a few lots shoot up (tower civs), or all (Kowloon)
    for lot in L.lots:
        if lot.get("notower") or rng.random() >= e.get("tower", 0.0):
            continue
        t = rng.randint(*e.get("tower_levels", p.get("tower_levels", (5, 8))))
        cells = [c for c in lot["cells"] if L.plan[c] != COURT]
        tc = p.get("tower_cells")
        if not tc:
            lot["cap"] = max(lot.get("cap", maxk), t)     # (Kowloon: the whole lot may rise to it later)
        if tc and len(cells) > tc:
            # a tower house: a compact block of the house shoots up (r1: the odd tower house in the medina),
            # grown from a front cell so the tower stands on the lane
            seed = min((c for c, _ in lot["front"] if c in cells), key=lambda c: h01(L.seed, "tw", c), default=cells[0])
            cs = set(cells)
            pick = [seed]
            while len(pick) < tc:
                nb = sorted({(a[0] + d[0], a[1] + d[1]) for a in pick for d in DIRS} & cs - set(pick))
                if not nb:
                    break
                pick.append(min(nb, key=lambda c: abs(c[0] - seed[0]) + abs(c[1] - seed[1]) + h01(L.seed, "tw", c)))
            cells = pick
            lot["tower"] = cells
        for c in cells:
            for k in range(L.top(*c) + 1, min(int(L.gk[c]) + t, L.L)):
                if L.free_at(c[0], c[1], k) and L.occ[c[0], c[1], k - 1]:
                    L.set_room(c[0], c[1], k, lot["unit"], epoch)
    # jetties: an upper room steps out over a lane (one cell: cantilever), lanes narrowing upward
    shafts = getattr(L, "open_shafts", set())
    jet = e.get("jetty", 0.0)
    if jet > 0:
        adds = []
        for i in range(L.nx):
            for j in range(L.nz):
                if L.plan[i, j] not in LANEISH or (i, j) in shafts:
                    continue
                for k in range(int(L.gk[i, j]) + max(1, p.get("jetty_from", 1)), L.L):
                    if L.occ[i, j, k] or L.block[i, j, k]:
                        continue
                    for di, dj in DIRS:
                        a = (i + di, j + dj)
                        if L.inb(*a) and L.occ[a[0], a[1], k] and L.plan[a] == LOT and rng.random() < jet:
                            # keep a lane at least one cell open beneath the sky on wide lanes? jetties only over
                            # lanes the civ allows (all of them for Kowloon, the 2-wide ones elsewhere)
                            adds.append((i, j, k, int(L.unit[a[0], a[1], k])))
                            break
        for (i, j, k, u) in adds:
            if not L.occ[i, j, k]:
                L.set_room(i, j, k, u, epoch)
    # sabats: rooms across a narrow lane at level >= sabat_from, both sides built: covered passages
    sab = e.get("sabat", 0.0)
    if sab > 0:
        for i in range(L.nx):
            for j in range(L.nz):
                if L.plan[i, j] != LANE or (i, j) in shafts:
                    continue
                for k in range(int(L.gk[i, j]) + p.get("sabat_from", 1), L.L):
                    if L.occ[i, j, k] or L.block[i, j, k]:
                        continue
                    for (di, dj) in ((1, 0), (0, 1)):
                        a, b = (i + di, j + dj), (i - di, j - dj)
                        if L.inb(*a) and L.inb(*b) and L.occ[a[0], a[1], k] and L.occ[b[0], b[1], k] and \
                                rng.random() < sab:
                            L.set_room(i, j, k, int(L.unit[a[0], a[1], k]), epoch)
                            break
    # courts filled (only civs that allow it)
    fill = e.get("court_fill", 0.0)
    if fill > 0:
        for lot in L.lots:
            for c in list(lot["court"]):
                if rng.random() < fill:
                    for k in range(int(L.gk[c]), min(int(L.gk[c]) + max(1, L.top(*lot["cells"][0])), L.L)):
                        if L.free_at(c[0], c[1], k):
                            L.set_room(c[0], c[1], k, lot["unit"], epoch)
                    lot["court"].remove(c)
                    L.plan[c] = LOT
    # main streets, plazas, gates, pads and the rim stay open to the sky (walkability)
    for i in range(L.nx):
        for j in range(L.nz):
            if L.plan[i, j] in (MAIN, PLAZA, GATE, RESERVED, RIM):
                for k in range(L.L):
                    if L.occ[i, j, k]:
                        L.clear(i, j, k)
    L.settle()


def assign_uses(L, rng, p):
    """lots fronting the main streets and plazas keep shops on the ground floor; a few civic and work lots"""
    for lot in L.lots:
        on_main = [c for c, m in lot["front"] if L.plan[m] in (MAIN, PLAZA)]
        on_artery = [c for c, m in lot["front"] if L.plan[m] == ARTERY]
        lot["shops"] = on_main + on_artery
        if not on_main and on_artery and rng.random() < p.get("work_share", 0.15):
            lot["use"] = WORK


def roof_shacks(L, rng, share):
    """E5: tin huts on the roofs (Kowloon's roof village; a few elsewhere), one storey, in small clusters"""
    if share <= 0:
        return
    for lot in L.lots:
        for c in lot["cells"]:
            k = L.top(*c)
            if k < 0 or k + 1 >= L.L or rng.random() >= share:
                continue
            if L.free_at(c[0], c[1], k + 1):
                L.set_room(c[0], c[1], k + 1, int(L.unit[c[0], c[1], k]), 5)
