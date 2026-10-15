"""Kowloon Walled City: the fused block (r2_kowloon_walled.md; Girard & Lambot, City of Darkness; the Japanese
survey's cross-section).

The mark is the section: ~350 buildings poured hard against each other until they fused into one mass.
- An alley grid of the old plot lines (1-2 m, jogging, some blind) laid at ground level only; towers of 4-12 m
  frontage fill every plot.  From storey 3 up every floor steps out over the alleys and the alleys roof over: they
  become dripping tunnels lit by fluorescent tubes, pipes and cables along their ceilings.
- 2-4 storey brick at the bottom (the 1950s rebuild), concrete towers to 10-14 storeys above, an almost flat roof
  plateau (the flight path's limit), a few light wells punched down through it.
- Small steel windows behind welded grilles low down, mesh cages on ~40% of upper bays, AC boxes everywhere, pipes
  down every second bay; no ornament but signs: a projecting sign at nearly every ground door.
- The roof is the plaza: a village of tin huts, water tanks on stilts, an aerial forest, ladders and planks between
  roofs a storey apart, laundry, a playground; warning lights at the plateau's corners.
- On the island the block is framed (as the park that replaced it): a broad paved street round and through it, a
  market square, the pond garden with willows and bamboo.
"""
from lattice import CIVIC, GREEN, HOME, LANE, LOT, MAIN, PLAZA, SHOP, WORK
from civ.base import Civ

# concrete, concrete_light, concrete_dark, once_painted, green_grey, tile, brick_old, rust, steel, tin, fluoro, red,
# blue, tank_blue, warm_window
PAL = ["#8e8a80", "#a9a497", "#6f6c63", "#c2bba9", "#5d6b66", "#b8a27a", "#8a5a3c", "#7a4a2a", "#4a4f52",
       "#9aa3a5", "#e8fff2", "#e83a3a", "#3a7bff", "#3b6fb5", "#ffcf7a"]
CON, CON_L, CON_D, PAINT, GREY_G, TILE, BRICK, RUST, STEEL, TIN, FLUORO, RED, BLUE, TANK, WARM = range(15)


class KowloonWalled(Civ):
    id = "kowloon_walled"
    name = "Kowloon Walled City"
    lanes = "grid"
    palette = PAL
    species = ["banyan_wall", "potted_plants", "willow", "bamboo", "reeds"]

    def __init__(self, isl, rng):
        super().__init__(isl, rng)
        self.params = {
            "grid_cells": (3, 6), "jog": 0.3, "blind": 0.25,
            "lot_cells": (4, 14), "courts": False,
            "e1_levels": (2, 4), "max_levels": 12, "civic_levels": 3, "tower_levels": (8, 12),
            "jetty_from": 3, "sabat_from": 2, "work_share": 0.35,
            "epochs": {2: {"rise": 0.7, "setback": 0.1, "tower": 0.45, "jetty": 0.25, "sabat": 0.2,
                           "tower_levels": (7, 9)},
                       3: {"rise": 0.7, "setback": 0.05, "tower": 0.5, "jetty": 0.45, "sabat": 0.5,
                           "tower_levels": (8, 11)},
                       4: {"rise": 0.7, "setback": 0.0, "tower": 0.7, "jetty": 0.6, "sabat": 0.75,
                           "tower_levels": (11, 12)}},
            "ring_inset": 11, "ring_cells": 3, "edge_cap": 5, "break": 0.06,
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5),
            "cable": 0.3, "enter_doors": 0.08, "sign": 1.0, "light_wells": 0.05,
        }

    def pave(self, L, plan_class, c, default):
        return "pave_main" if default == "pave_lane" else default     # (poured concrete alleys)

    def lot_palette(self, lot):
        """a kit palette variant per tower (0 grey concrete, 1 mint, 2 buff, 3 dark): the city's patchwork"""
        from pick import h01
        r = h01(self.isl["id"], "pal", lot["id"])
        return 0 if r < 0.35 else (1 if r < 0.6 else (2 if r < 0.82 else 3))

    def slot(self, name, epoch=1, ij=(0, 0)):
        if name == "wall":
            if epoch <= 1:
                return BRICK
            if epoch == 5:
                return TIN
            return (CON, CON_L, CON_D, PAINT, GREY_G, TILE)[(ij[0] * 7 + ij[1] * 13 + epoch) % 6]
        return {"trim": CON_D, "frame": STEEL, "screen": STEEL, "roof": CON_D, "metal": STEEL, "glass": CON_D,
                "fabric": RED, "emissive": FLUORO, "paving": CON_D}.get(name, CON)

    def frame(self, L, rng):
        """the block framed (the park that replaced it, and the research's island plan): a broad paved street round
        the core a few rows in from the rim; outside it a lower edge of 3-5 storey walk-ups (tong lau) facing it"""
        import numpy as np
        from collections import deque
        from lattice import FREE, OUT
        dist = np.full((L.nx, L.nz), 10 ** 6, np.int32)
        q = deque()
        for i in range(L.nx):
            for j in range(L.nz):
                if L.plan[i, j] == OUT:
                    dist[i, j] = 0
                    q.append((i, j))
        for i in range(L.nx):                         # (the lattice's own border counts as outside)
            for j in (0, L.nz - 1):
                if dist[i, j]:
                    dist[i, j] = 0
                    q.append((i, j))
        for j in range(L.nz):
            for i in (0, L.nx - 1):
                if dist[i, j]:
                    dist[i, j] = 0
                    q.append((i, j))
        while q:
            i, j = q.popleft()
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if L.inb(a, b) and dist[a, b] > dist[i, j] + 1:
                    dist[a, b] = dist[i, j] + 1
                    q.append((a, b))
        d0 = self.params["ring_inset"]
        d1 = d0 + self.params["ring_cells"]
        for i in range(L.nx):
            for j in range(L.nz):
                if d0 <= dist[i, j] < d1 and L.plan[i, j] == FREE:
                    L.plan[i, j] = MAIN
        L.edge = dist < d0

    def mark_lots(self, L, rng):
        """the walk-up edge outside the ring street (5 storeys at most, no towers); the light wells: a few lane cells
        never covered (shafts down through the mass)"""
        edge = getattr(L, "edge", None)
        if edge is not None:
            for lot in L.lots:
                if sum(1 for c in lot["cells"] if edge[c]) * 2 >= len(lot["cells"]):
                    lot["cap"] = self.params["edge_cap"]
                    lot["notower"] = True
                    lot["edge"] = True
        L.open_shafts = set()
        lanes = [(i, j) for i in range(L.nx) for j in range(L.nz) if L.plan[i, j] == LANE]
        for c in lanes:
            if rng.random() < self.params["light_wells"]:
                L.open_shafts.add(c)
        # a temple on the plaza (Tin Hau): a low civic lot
        for lot in L.lots:
            if any(L.plan[m] == PLAZA for _, m in lot["front"]) and len(lot["cells"]) >= 6:
                lot["kind"] = "civic"
                lot["use"] = CIVIC
                lot["cap"] = 2
                break

    def facade(self, ctx):
        r = ctx["rnd"]
        e = ctx["epoch"]
        w = self.slot("wall", e, (ctx["i"], ctx["j"]))
        out = ctx["outward"]
        if e >= 5:
            return ("shack_panel", 0, TIN)
        if ctx["ground"]:
            if ctx["door"]:
                return ("wall_door", 0, STEEL)
            if out in ("main", "plaza", "artery", "lane", "gate", "green", "bank", "reserved"):
                if ctx["use"] == CIVIC:
                    return ("wall_shopfront", 0, RED)
                if out in ("main", "plaza", "artery", "gate"):
                    return ("wall_shopfront", 0, w) if r < 0.7 else ("wall_door", 0, STEEL)
                # the alleys: roller shutters and workshop doors between blank walls
                return ("wall_shopfront", 0, w) if r < 0.25 else (("wall_door", 0, STEEL) if r < 0.35 else
                                                                   ("wall_plain", 0, w))
            return ("wall_window_grille", 0, w) if r < 0.3 else ("wall_plain", 0, w)
        rel = ctx["level"] - ctx["gk"]
        s = ctx["stack"]
        # what can't be seen gets nothing: faces into blind slots between towers; a slot over an alley a blank wall
        if ctx["slot"] == "blind":
            return None
        if ctx["slot"] == "lane":
            return ("wall_window_s", 0, w) if s < 0.12 else ("wall_plain", 0, w)
        if out == "shaft":                  # light wells: a window every third floor, the rest left to the dark
            return ("wall_window_s", 0, w) if rel % 3 == 0 else None
        # mostly blank concrete with sparse windows (r2: "a cliff of small windows, cages, AC boxes")
        if rel <= 3:
            return ("wall_window_grille", 0, w) if s < 0.35 else (("wall_window_s", 0, w) if s < 0.6 else
                                                                   ("wall_plain", 0, w))
        if s < 0.05:
            return ("wall_kowloon_stack_t", 0, w)          # (the dense hero bay: cage, AC, laundry, pipes, sign)
        if s < 0.14:
            return ("wall_balcony_cage", 0, w)
        if s < 0.22:
            return ("wall_window_pair", 0, w)
        if s < 0.45:
            return ("wall_window_s", 0, w)
        return ("wall_plain", 0, w)

    def corner(self, kind, level, epoch):
        # (the concrete towers meet plainly; only the inner corners need the kit's filler)
        return ("corner_in", 0, self.slot("wall", epoch)) if kind == "in" else None

    def roof_edge(self, ctx):
        return ("parapet_plain", 0, CON_D)

    def roof_field(self, i, j, level, epoch):
        return ("roof_terrace", 0, CON_D)

    def marks(self, L, rng, emit):
        # aircraft warning lights at the plateau's highest corners; a playground on the widest roof
        tops = sorted(L.roof_cells, key=lambda c: -c[2])
        for c in tops[:4]:
            emit("warning_light", c[0], c[1], c[2], 0, 0, 0, RED, 5)
        if L.roof_cells:
            k = max(c[2] for c in L.roof_cells)
            flat = [c for c in L.roof_cells if c[2] >= k - 1]
            if flat:
                c = flat[len(flat) // 2]
                emit("roof_playground", c[0], c[1], c[2], 0, 0, 0, BLUE, 5)

    def overlay(self, L, rng, emit, cells):
        p = self.params
        # the tunnels: fluorescent tubes and cable trays along every covered alley's ceiling
        for (i, j, k, rot) in cells["covered"]:
            emit("fluoro_tube", i, j, k, rot, 0, 0, FLUORO, 5)
            if rng.random() < p["cable"]:
                emit("cable_span", i, j, k, rot, 0, 1, STEEL, 5)
        for (i, j, rot, k) in cells["lane_spans"]:
            if rng.random() < p["cable"] * 0.6:
                emit("cable_span", i, j, k + 1, rot, 0, 0, STEEL, 5)
        # walls: AC boxes and down pipes
        for (i, j, k, rot, stack) in cells["upper_faces"]:
            if rng.random() < 0.1:
                emit("ac_unit", i, j, k, rot, 0, 0, STEEL, 5)
            if stack < 0.25 and rng.random() < 0.3:
                emit("pipe_run", i, j, k, rot, 0, 0, RUST, 4)
        # the roof village: tanks on stilts, the aerial forest, laundry
        for (i, j, k) in cells["roofs"]:
            r = rng.random()
            if r < 0.07:
                emit("water_tank", i, j, k, rng.randrange(4), 0, 0, TANK, 4)
            elif r < 0.19:
                emit("antenna", i, j, k, rng.randrange(4), 0, 0, STEEL, 5)
            elif r < 0.25:
                emit("laundry", i, j, k, rng.randrange(4), 0, 0, rng.choice((RED, BLUE, PAINT, WARM)), 5)

    def foliage(self, L, rng):
        out = []
        for i in range(L.nx):
            for j in range(L.nz):
                pc = L.plan[i, j]
                r = rng.random()
                if pc == GREEN and r < 0.35:
                    out.append((rng.choice(["willow", "bamboo", "bamboo", "banyan_tree"]), (i, j), 0.0,
                                rng.uniform(0.8, 1.2)))
                elif pc == 4 and r < 0.35:                         # BANK
                    out.append((rng.choice(["willow", "reeds", "reeds", "bamboo"]), (i, j), 0.0, rng.uniform(0.8, 1.2)))
                elif pc == PLAZA and r < 0.05:
                    out.append(("banyan_tree", (i, j), 0.0, rng.uniform(0.9, 1.2)))
        # self-sown banyans strangling old walls and roof edges; pots on the roof edges
        for (i, j, rot, k, epoch) in L.faces_on_lanes:
            if epoch <= 1 and rng.random() < 0.04:
                out.append(("banyan_wall", (i, j, k), rot, rng.uniform(0.7, 1.2)))
        for (i, j, k) in L.roof_cells:
            if rng.random() < 0.08:
                out.append(("potted_plants", (i, j, k), 0.0, rng.uniform(0.8, 1.2)))
        return out
