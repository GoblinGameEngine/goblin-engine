"""spine.py -- E0, walkability first (r4_methods §5; Alexander, Gehl, Jacobs): the island's public network is laid
before anything is built -- main streets 9 m wide from the main bridges to a central plaza (a cross on big islands),
gate plazas at the bridges (the fast-travel arrival), an activity node every ~275 m, greens and the ponds' banks, so
that every cell is within ~230 m of green and every door, bridge and bank is on one connected network.
"""
import heapq
import math
from collections import deque

from lattice import (ARTERY, BANK, CELL, FREE, GATE, GREEN, LANE, MAIN, OUT, PASTURE, PLAZA, RESERVED, RIM, STREETS,
                     WALKABLE, WATER)

STEP_COST = {FREE: 1.0, GATE: 0.6, MAIN: 0.5, PLAZA: 0.5, LANE: 0.7, ARTERY: 0.6, BANK: 6.0, GREEN: 6.0, PASTURE: 9.0,
             RESERVED: 5.0, RIM: 9.0}
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def route(L, a, goal_set, turn_cost=2.5):
    """A* over the plan from cell a to any cell in goal_set; straight runs preferred (turns cost)"""
    gx = [g for g in goal_set]
    def h(c):
        return min(abs(c[0] - g[0]) + abs(c[1] - g[1]) for g in gx[:40])
    start = (a[0], a[1], -1)
    best = {start: 0.0}
    prev = {}
    pq = [(h(a), 0.0, start)]
    while pq:
        f, g, st = heapq.heappop(pq)
        i, j, d = st
        if (i, j) in goal_set:
            path = [(i, j)]
            while st in prev:
                st = prev[st]
                path.append((st[0], st[1]))
            return path[::-1]
        if g > best.get(st, 1e18):
            continue
        for k, (di, dj) in enumerate(DIRS):
            ni, nj = i + di, j + dj
            if not L.inb(ni, nj):
                continue
            c = STEP_COST.get(int(L.plan[ni, nj]))
            if c is None:
                continue
            g2 = g + c + (turn_cost if d not in (-1, k) else 0.0)
            ns = (ni, nj, k)
            if g2 < best.get(ns, 1e18):
                best[ns] = g2
                prev[ns] = st
                heapq.heappush(pq, (g2 + h((ni, nj)), g2, ns))
    return None


def widen(L, path, width, cls, over=(FREE, GATE, RESERVED)):
    """mark a path `width` cells wide (centred) as cls"""
    lo = -(width // 2)
    hi = lo + width
    for n, (i, j) in enumerate(path):
        a = path[max(n - 1, 0)]
        b = path[min(n + 1, len(path) - 1)]
        di, dj = b[0] - a[0], b[1] - a[1]
        pi, pj = (0, 1) if abs(di) >= abs(dj) else (1, 0)       # perpendicular to the run
        for o in range(lo, hi):
            for c in ((i + pi * o, j + pj * o),):
                if L.inb(*c) and L.plan[c] in over:
                    L.plan[c] = cls


def bfs_dist(L, seeds, passable):
    INF = 10 ** 9
    d = {}
    q = deque()
    for s in seeds:
        d[s] = 0
        q.append(s)
    while q:
        c = q.popleft()
        for di, dj in DIRS:
            n = (c[0] + di, c[1] + dj)
            if L.inb(*n) and n not in d and passable(int(L.plan[n])):
                d[n] = d[c] + 1
                q.append(n)
    return d


def lay_spine(L, rng, blocks, civ):
    plan = L.plan
    free = [(i, j) for i in range(L.nx) for j in range(L.nz) if plan[i, j] == FREE]
    if not free:
        return
    # the central plaza: at the free land's middle, clear of the edges (Pattern 61: 14-21 m, longer one way)
    ci = sum(c[0] for c in free) / len(free)
    cj = sum(c[1] for c in free) / len(free)
    ps = 5 if blocks <= 3 else (6 if blocks <= 6 else 7)
    ps = civ.params.get("plaza_cells", ps)
    pa, pb = ps, ps + (1 if blocks >= 4 else 0)
    best = None
    for (i, j) in free:
        cells = [(i + a, j + b) for a in range(pa) for b in range(pb)]
        if all(L.inb(*c) and plan[c] == FREE for c in cells):
            d = math.hypot(i + pa / 2 - ci, j + pb / 2 - cj)
            if best is None or d < best[0]:
                best = (d, cells)
    plaza = best[1] if best else [min(free, key=lambda c: math.hypot(c[0] - ci, c[1] - cj))]
    for c in plaza:
        plan[c] = PLAZA
    L.plaza = plaza
    L.plaza_c = (sum(c[0] for c in plaza) / len(plaza), sum(c[1] for c in plaza) / len(plaza))
    # the main bridges: the road bridges first, then one per side, spread round (2 on small islands, 4 on big)
    gates = sorted(L.gates, key=lambda g: (-g["width"], rng.random()))
    nmain = 2 if blocks < 6 else 4
    main, sides = [], set()
    for g in gates:
        if g["side"] not in sides or len(sides) >= 4:
            main.append(g)
            sides.add(g["side"])
        if len(main) >= nmain:
            break
    L.main_gates = main
    width = civ.params.get("main_cells", 3)
    plaza_set = set(plaza)
    L.main_paths = []
    for g in main:
        a = g["end"]
        if not L.inb(*a):
            continue
        path = route(L, a, plaza_set)
        if path is None:
            L.notes.append("no main street from bridge %d" % g["bridge"])
            continue
        widen(L, path, width, MAIN)
        L.main_paths.append(path)
        # the gate plaza: a 3 x 3 square at the street's bridge end (the arrival point)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                c = (a[0] + di, a[1] + dj)
                if L.inb(*c) and plan[c] in (FREE, GATE, MAIN):
                    plan[c] = PLAZA
    # the other bridges: a lane each to the nearest street, later (lanes)
    # an activity node every ~275 m: a second small square at the far end of the longest main street
    longest = max(L.main_paths, key=len) if L.main_paths else []
    if len(longest) * CELL > 90:
        m = longest[int(len(longest) * 0.55)]
        for di in range(-2, 2):
            for dj in range(-2, 2):
                c = (m[0] + di, m[1] + dj)
                if L.inb(*c) and plan[c] == FREE:
                    plan[c] = PLAZA
    # greens: the ponds' banks are public green; one more garden per three blocks, where green is furthest
    n_green = max(1, blocks // 3)
    gsz = civ.params.get("garden_cells", (5, 4))
    for _ in range(n_green):
        greens = [(i, j) for i in range(L.nx) for j in range(L.nz) if plan[i, j] in (BANK, GREEN)]
        dist = bfs_dist(L, greens, lambda p: p != OUT) if greens else {}
        best = None
        for (i, j) in free:
            cells = [(i + a, j + b) for a in range(gsz[0]) for b in range(gsz[1])]
            if not all(L.inb(*c) and plan[c] == FREE for c in cells):
                continue
            # touching a street (reached by the public), as far from green as possible
            touch = any(L.inb(c[0] + di, c[1] + dj) and plan[c[0] + di, c[1] + dj] in STREETS
                        for c in cells for di, dj in DIRS)
            d = dist.get((i, j), 999) + (40 if touch else 0) + rng.random()
            if best is None or d > best[0]:
                best = (d, cells)
        if best:
            for c in best[1]:
                plan[c] = GREEN
    # the arrival point: the first main gate's plaza, facing the central plaza
    g = main[0] if main else (L.gates[0] if L.gates else None)
    if g:
        a = g["end"]
        x, _, z = L.centre(*a)
        px, _, pz = L.centre(*L.plaza_c) if False else L.centre(int(L.plaza_c[0]), int(L.plaza_c[1]))
        yaw = math.atan2(-(px - x), -(pz - z))           # a front at -Z faces (-sin yaw, -cos yaw)
        L.travel = [round(x, 2), round(L.deck_y(x, z), 2), round(z, 2), round(yaw, 3)]
    else:
        x, _, z = L.centre(int(L.plaza_c[0]), int(L.plaza_c[1]))
        L.travel = [round(x, 2), round(L.deck_y(x, z), 2), round(z, 2), 0.0]


def connect_leftovers(L):
    """every walkable patch (banks, greens, gates, reserved pads) reaches the street network: carve a lane"""
    plan = L.plan
    walk = lambda p: p in WALKABLE
    streets = [(i, j) for i in range(L.nx) for j in range(L.nz) if plan[i, j] in (MAIN, PLAZA)]
    if not streets:
        return
    # (stubs first: a lane cell with no walkable cell beside it -- a dog-leg's corner touching only diagonally)
    for i in range(L.nx):
        for j in range(L.nz):
            if plan[i, j] in (LANE, ARTERY) and not any(L.inb(i + di, j + dj) and plan[i + di, j + dj] in WALKABLE
                                                       for di, dj in DIRS):
                plan[i, j] = FREE
    for _ in range(600):
        reach = bfs_dist(L, streets, walk)
        lonely = [(i, j) for i in range(L.nx) for j in range(L.nz) if walk(int(plan[i, j])) and (i, j) not in reach]
        if not lonely:
            return
        a = lonely[0]
        goal = set(reach.keys())
        path = route(L, a, goal, turn_cost=1.0)
        if path is None:
            L.notes.append("can't connect walkable patch at %s" % (a,))
            plan[a] = OUT if plan[a] == RIM else plan[a]
            continue
        for c in path:
            if plan[c] in (FREE,):
                plan[c] = LANE
            elif plan[c] == RESERVED:
                pass
