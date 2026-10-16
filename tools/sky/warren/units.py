"""units.py -- who lives where, and how one walks: units (households, shops, works, civic halls) with their doors,
and the walk graph over every level (the open ground, the public roofs, stairs and ladders between them).

Units: a courtyard civ's house is one household unit (big ones two); a tower civ's lot is one unit per storey above
the ground floor (flats), with shops and works on the ground.  Each unit's door is its lot's door (the stair in a tower).
"""
from collections import defaultdict

from lattice import CIVIC, HOME, SHOP, STOREY, WALKABLE, WATER, WORK
from pick import FACE, h01


def make_units(L, civ):
    flats = civ.params.get("flats_per_level", civ.lanes == "grid")
    units, doors = [], []
    for lot in L.lots:
        if not lot.get("door"):
            continue
        cells = defaultdict(int)          # level -> rooms
        for c in lot["cells"]:
            for k in range(L.L):
                if L.occ[c[0], c[1], k] and L.lot[c] == lot["id"]:
                    cells[k] += 1
        if not cells:
            continue
        g0 = min(cells)
        floors = len(cells)
        dc, drot = lot["door"]
        use = lot["use"]
        if use == CIVIC:
            units.append({"use": CIVIC, "homes": 0, "floors": floors, "cells": sum(cells.values()), "lot": lot["id"]})
            doors.append((len(units) - 1, dc, lot["door_k"], drot, 1))
            continue
        shops = lot.get("shop_cells", set())
        if shops:
            units.append({"use": SHOP, "homes": 0, "floors": 1, "cells": len(shops), "lot": lot["id"]})
            for c in sorted(shops):
                for rot, (di, dj) in FACE.items():
                    m = (c[0] + di, c[1] + dj)
                    if m in L.W and L.q[m] == 4 * int(L.gk[c]) and m not in L.stoop:
                        doors.append((len(units) - 1, c, int(L.gk[c]), rot, 1))
                        break
        if flats:
            for k in sorted(cells):
                if k == g0 and (shops or use == WORK):
                    if use == WORK:
                        units.append({"use": WORK, "homes": 0, "floors": 1, "cells": cells[k], "lot": lot["id"]})
                        doors.append((len(units) - 1, dc, lot["door_k"], drot, 0))
                    continue
                homes = max(1, cells[k] // 3)          # (Kowloon's flats: ~23 m2 -- three cells a flat, roughly)
                units.append({"use": HOME, "homes": homes, "floors": 1, "cells": cells[k], "lot": lot["id"],
                              "level": k})
                doors.append((len(units) - 1, dc, lot["door_k"], drot, 0))
        else:
            rooms = sum(cells.values())
            homes = 1 if rooms < 18 else 2               # (extended families: one house, sometimes two)
            if use == WORK:
                units.append({"use": WORK, "homes": 0, "floors": floors, "cells": rooms, "lot": lot["id"]})
            else:
                units.append({"use": HOME, "homes": homes, "floors": floors, "cells": rooms, "lot": lot["id"]})
            doors.append((len(units) - 1, dc, lot["door_k"], drot, 0))
    # the enter flags: shops always (select.py made their interiors), a share of house doors
    enter = set((c[0], c[1], c[2]) for c in getattr(L, "enter", []))
    doors = [(u, c, k, rot, 1 if (c[0], c[1], k) in enter else e) for (u, c, k, rot, e) in doors]
    L.units = units
    L.doors = doors
    return units, doors


STORE, VACANT = 6, 7          # (unit uses beyond lattice.py's: a storeroom, an empty unit)
KIND_USE = {"workshop": WORK, "factory": WORK, "dentist": WORK, "store": SHOP, "shrine": CIVIC, "storeroom": STORE,
            "vacant": VACANT}
SURPLUS = {     # what the flats beyond the canon population are, by storeys above the ground (r2: Kowloon's
                # dentists, noodle and fishball factories, shrines; the medina's workshops and storerooms)
    "grid": [(1, (("factory", .3), ("workshop", .3), ("dentist", .15), ("store", .15), ("shrine", .02), ("vacant", .08))),
             (5, (("workshop", .3), ("factory", .2), ("storeroom", .2), ("dentist", .05), ("vacant", .23), ("shrine", .02))),
             (99, (("vacant", .45), ("storeroom", .35), ("workshop", .2)))],
    "tree": [(99, (("workshop", .35), ("store", .2), ("storeroom", .3), ("vacant", .15)))],
}


def balance_homes(L, civ, units, population):
    """keep every unit the lattice makes, but the homes beyond the canon population become workshops, stores,
    storerooms, vacant units (and Kowloon's factories, dentists, shrines) -- homes ~ population"""
    for u in units:
        u.setdefault("kind", {HOME: "home", SHOP: "shop", WORK: "workshop", CIVIC: "civic"}.get(u["use"], "other"))
    homes = sum(u["homes"] for u in units)
    surplus = homes - int(population or homes)
    if surplus <= 0:
        return 0
    table = SURPLUS["grid" if civ.params.get("flats_per_level", civ.lanes == "grid") else "tree"]
    order = sorted((n for n, u in enumerate(units) if u["use"] == HOME), key=lambda n: h01(L.seed, "surplus", n))
    moved = 0
    for n in order:
        if surplus <= 0:
            break
        u = units[n]
        lot = L.lots[u["lot"]]
        g = min(int(L.gk[c]) for c in lot["cells"])
        rel = u.get("level", g) - g
        kinds = next(t for top, t in table if rel <= top)
        r = h01(L.seed, "kind", n)
        acc = 0.0
        kind = kinds[-1][0]
        for kd, w in kinds:
            acc += w
            if r < acc:
                kind = kd
                break
        surplus -= u["homes"]
        moved += u["homes"]
        u["use"] = KIND_USE[kind]
        u["kind"] = kind
        u["homes"] = 0
    return moved


def walk_graph(L, civ):
    """nodes: every open walkable ground cell (at the deck), the public roofs (tower civs' roof plateau), the stair
    cores between; edges between neighbours (steps where the deck rises, ladders where roofs differ a storey)"""
    nodes, index = [], {}
    def add(key, x, y, z, kind):
        index[key] = len(nodes)
        nodes.append([round(x, 2), round(y, 2), round(z, 2), kind])
    import walk
    for (i, j) in sorted(L.W):
        x, _, z = L.centre(i, j)
        # (a stair cell's node at the middle of its ramp)
        st = L.stair.get((i, j))
        y = L.q[(i, j)] * walk.Q + (st[1] * walk.Q / 2 if st else 0.0)
        add(("g", i, j), x, y, z, "stair" if st else "ground")
    edges = []
    L.stairs_out = []
    L.ladders = []                          # (i, j, level, rot): a ladder up a roof step
    L.planks = []                           # (i, j, level, rot): a plank across a gap between roofs
    L.edge_extra = {}                       # edge index -> the ladder / planks it needs
    L.walk_keys = None
    for (i, j) in sorted(L.W):
        a = index[("g", i, j)]
        for di, dj in ((1, 0), (0, 1)):
            n = (i + di, j + dj)
            if n in L.W and walk.connected(L, (i, j), n):
                sa, sb = L.stair.get((i, j)), L.stair.get(n)
                if sa and sb and walk.FACE[sa[0]] != (di, dj) and walk.FACE[sa[0]] != (-di, -dj):
                    # (side by side across a wide flight: the kit's ramps are 2.8 m wide in their 3 m cells, a 20 cm
                    # slot between them the capsule can't cross mid-flight -- the audit's walk; up one ramp instead)
                    L.walk_side_cut = getattr(L, "walk_side_cut", 0) + 1
                    continue
                edges.append([a, index[("g", n[0], n[1])]])
    # a courtyard house's court: reached through its door (the court is the house's own, but it is on the graph)
    for lot in L.lots:
        if not lot.get("court") or not lot.get("door"):
            continue
        dc, drot = lot["door"]
        di, dj = FACE[drot]
        outside = index.get(("g", dc[0] + di, dc[1] + dj))
        for c in lot["court"]:
            n = index.get(("g", c[0], c[1]))
            if n is not None and outside is not None:
                edges.append([outside, n])
                break
    # public roofs: in a tower civ the roof plateau is the plaza (ladders between roofs a storey apart)
    if civ.params.get("roof_walk", civ.lanes == "grid"):
        roofs = {(i, j): k for (i, j, k) in L.roof_cells}
        for (i, j), k in roofs.items():
            x, _, z = L.centre(i, j)
            add(("r", i, j), x, k * STOREY, z, "roof")
        rot_of = {(0, -1): 0, (-1, 0): 1, (0, 1): 2, (1, 0): 3}
        for (i, j), k in roofs.items():
            a = index[("r", i, j)]
            for di, dj in ((1, 0), (0, 1)):
                kb = roofs.get((i + di, j + dj))
                if kb is not None and abs(kb - k) <= 1:
                    if kb != k and h01(L.seed, "ladder", i, j, di) > 0.25:
                        continue                      # (not every roof step has its ladder)
                    edges.append([a, index[("r", i + di, j + dj)]])
                    if kb != k:                       # a ladder up the step, on the lower roof
                        lo, d = ((i, j), (di, dj)) if kb > k else ((i + di, j + dj), (-di, -dj))
                        L.ladders.append((lo[0], lo[1], min(k, kb), rot_of[d]))
                        L.edge_extra[len(edges) - 1] = ("ladder", L.ladders[-1])
                    continue
                # a plank across a one- or two-cell gap to a roof at the same height (over a lane or a light well)
                for gap in (2, 3):
                    kc = roofs.get((i + di * gap, j + dj * gap))
                    mid = [(i + di * s, j + dj * s) for s in range(1, gap)]
                    if kc is not None and abs(kc - k) == 0 and all(m not in roofs and L.inb(*m) and
                                                                   not L.occ[m[0], m[1], k - 1] for m in mid):
                        edges.append([a, index[("r", i + di * gap, j + dj * gap)]])
                        for m in mid:
                            L.planks.append((m[0], m[1], k, rot_of[(di, dj)] & 1))
                        L.edge_extra[len(edges) - 1] = ("planks", [(m[0], m[1], k, rot_of[(di, dj)] & 1) for m in mid])
                        break
        # stair cores: a public stair from the ground to the roof every ~40 m, at a door on a lane
        stairs = 0
        for lot in L.lots:
            if not lot.get("door") or h01(L.seed, "stair", lot["id"]) > 0.35:
                continue
            c, rot = lot["door"]
            di, dj = FACE[rot]
            g = index.get(("g", c[0] + di, c[1] + dj))
            r = index.get(("r", c[0], c[1]))
            if g is None or r is None:
                continue
            x, _, z = L.centre(*c)
            prev = g
            top = L.top(*c)
            for k in range(int(L.gk[c]), top + 1):
                add(("s", c[0], c[1], k), x, k * STOREY + 0.1, z, "stair")
                edges.append([prev, index[("s", c[0], c[1], k)]])
                prev = index[("s", c[0], c[1], k)]
            edges.append([prev, r])
            stairs += 1
        L.stair_cores = stairs
    # the doors' own nodes link to the ground outside them
    L.walk = {"nodes": nodes, "edges": edges}
    L.walk_index = index
    return L.walk


def components(L):
    """connected pieces of the walk graph (one is the goal)"""
    nodes, edges = L.walk["nodes"], L.walk["edges"]
    parent = list(range(len(nodes)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    sizes = defaultdict(int)
    for n in range(len(nodes)):
        sizes[find(n)] += 1
    return sorted(sizes.values(), reverse=True)


def mark_private_roofs(L):
    """roofs not joined to the public network (a tower's own roof, reached by its own stair) are labelled private"""
    nodes, edges = L.walk["nodes"], L.walk["edges"]
    parent = list(range(len(nodes)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    count = defaultdict(int)
    for n in range(len(nodes)):
        count[find(n)] += 1
    main = max(count, key=count.get) if count else -1
    for n in range(len(nodes)):
        if find(n) != main and nodes[n][3] == "roof":
            nodes[n][3] = "roof_private"
