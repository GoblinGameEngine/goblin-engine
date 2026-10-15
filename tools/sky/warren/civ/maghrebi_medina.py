"""Maghrebi medina (r1_maghrebi_medina.md: Fez el-Bali, Marrakesh, Tunis), with the odd tower house.

The mark is not ornament on a block: it is the plan and the section.
- A continuous carved mass of courtyard houses (riads, dars), 2-4 storeys, the life turned inward: street walls ~90%
  blank, one studded horseshoe door per house, small grilled windows high up; courts ringed by horseshoe arcades and
  cedar galleries, open to the sky, planted with orange trees in fours.
- Lanes bend every 10-25 m, branch into blind derbs (dead ends ~40%), dip under rooms that bridge them (sabats: ~35%
  of narrow lanes covered somewhere), shored by timber beams across.  Souq arteries two cells wide with shops both
  sides under slatted canopies.
- Flat roof terraces at stepped heights: laundry, mint pots, a sea of satellite dishes; parapets plain.  Green tile
  only on the sacred: the mosque's hip roofs and its square Almohad minaret.  Zellige fountains in walls and squares.
- One wall colour per city (Fez sand, Marrakesh ochre-red, Tunis white and blue), chosen by the island.
- The newest layer, muted: LED-slat souq canopies, brass LED lanterns, derb neon numbers, a dish sea.
"""
from lattice import ARTERY, CIVIC, COURT, GREEN, HOME, LANE, LOT, MAIN, PLAZA, SHOP, WORK
from civ.base import Civ

CITIES = {
    # wall_old, wall, wall_new, lime, cedar, door, zellige green, blue, brass, roof, tin, lantern, terracotta, dish
    "fez": ["#c9a978", "#d6c19c", "#e2d3b2", "#efe6d3", "#6b4428", "#2f6b4a", "#2f7d4f", "#2d6fb0", "#b58b3b",
            "#cbb48d", "#8e9aa0", "#ffd27a", "#b8573d", "#dcdcd6"],
    "marrakesh": ["#b8573d", "#c46a4f", "#d08466", "#efe0cc", "#5e3a22", "#2f6b4a", "#2f7d4f", "#2d6fb0", "#b58b3b",
                  "#c27a5c", "#8e9aa0", "#ffd27a", "#a8462f", "#dcdcd6"],
    "tunis": ["#e9e4d6", "#f3f1ea", "#fbfaf5", "#ffffff", "#5e3a22", "#2d6fb0", "#2f7d4f", "#2d6fb0", "#b58b3b",
              "#e0dbcd", "#8e9aa0", "#ffd27a", "#b8573d", "#dcdcd6"],
}
WALL_OLD, WALL, WALL_NEW, LIME, CEDAR, DOOR, ZELLIGE, BLUE, BRASS, ROOF, TIN, LANTERN, TERRA, DISH = range(14)


class MaghrebiMedina(Civ):
    id = "maghrebi_medina"
    name = "Maghrebi medina"
    lanes = "tree"
    species = ["bitter_orange", "lemon", "date_palm", "fig", "bougainvillea", "jasmine", "grapevine_pergola",
               "pot_mint_geranium", "banana", "reeds"]

    def __init__(self, isl, rng):
        super().__init__(isl, rng)
        self.city = rng.choice(["fez", "fez", "marrakesh", "tunis"])
        self.palette = CITIES[self.city]
        self.params = {
            "bend_cells": (3, 8), "lane_spacing": 5, "lane_len": 18, "branch": 0.4, "loop": 0.35, "artery_share": 0.35,
            "block_cells": 12, "cut_turn": 4.0,
            "lot_cells": (8, 22), "courts": True, "court_min_lot": 9, "court_share": 0.2,
            "e1_levels": (2, 2), "max_levels": 4, "civic_levels": 2, "tower_levels": (5, 8), "tower_cells": 4,
            "sabat_from": 1, "work_share": 0.2,
            "epochs": {2: {"rise": 0.45, "setback": 0.35, "sabat": 0.2, "tower": 0.05},
                       3: {"rise": 0.35, "setback": 0.4, "sabat": 0.25, "tower": 0.06},
                       4: {"rise": 0.2, "setback": 0.5, "sabat": 0.15, "tower": 0.035}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (5, 4),
            "cable": 0.35, "sign": 0.45, "dish": 0.35, "lantern": 0.5,
        }

    def edge_extra(self):
        return ["crown_band"]

    def roof_extra(self, L, i, j, lv):
        lot = L.lots[L.lot[i, j]] if L.lot[i, j] >= 0 else None
        return ["green_hip"] if lot is not None and lot["use"] == CIVIC else []

    def pave(self, L, plan_class, c, default):
        """zellige court floors in the mosque and at each riad's heart; the rest of a court plain flags"""
        if default != "pave_court":
            return default
        lot = L.lots[L.lot[c]] if L.lot[c] >= 0 else None
        if lot is None or lot.get("use") == CIVIC or (lot.get("court") and c == lot["court"][len(lot["court"]) // 2]):
            return default
        return "pave_plaza"

    def lot_palette(self, lot):
        """a kit palette variant per house (pieces.json palettes: 0 Fez sand, 1 Marrakesh red, 2 Tunis white/blue,
        3 old ochre): mostly the island's city, a few houses of the others"""
        from pick import h01
        r = h01(self.isl["id"], "pal", lot["id"])
        main, other = {"fez": (0, 3), "marrakesh": (1, 3), "tunis": (2, 0)}[self.city]
        return main if r < 0.82 or lot.get("kind") == "civic" else (other if r < 0.95 else 3)

    @property
    def base_palette(self):
        return {"fez": 0, "marrakesh": 1, "tunis": 2}[self.city]

    def slot(self, name, epoch=1, ij=(0, 0)):
        if name == "wall":
            return WALL_OLD if epoch <= 1 else (WALL if epoch <= 3 else (TIN if epoch == 5 else WALL_NEW))
        return {"trim": LIME, "frame": CEDAR, "screen": CEDAR, "roof": ROOF, "metal": BRASS, "door": DOOR,
                "tile": ZELLIGE, "fabric": TERRA, "emissive": LANTERN, "paving": WALL_OLD}.get(name, WALL)

    # -- the plan
    def mark_lots(self, L, rng):
        """the mosque: the biggest lot on (or next to) the central plaza, its court kept large"""
        best = None
        pc = L.plaza_c
        for lot in L.lots:
            if len(lot["cells"]) < 12:
                continue
            on = any(L.plan[m] == PLAZA for _, m in lot["front"])
            d = min(abs(c[0] - pc[0]) + abs(c[1] - pc[1]) for c in lot["cells"])
            score = d - (6 if on else 0) - len(lot["cells"]) * 0.2
            if best is None or score < best[0]:
                best = (score, lot)
        if best:
            lot = best[1]
            lot["kind"] = "civic"
            lot["use"] = CIVIC
            lot["cap"] = 2
            lot["notower"] = True
            self.mosque = lot

    def courts_for_civic(self, L, rng):
        lot = getattr(self, "mosque", None)
        if not lot:
            return
        cs = set(lot["cells"])
        inner = [c for c in lot["cells"] if all((c[0] + a, c[1] + b) in cs for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        inner.sort(key=lambda c: (c[0], c[1]))
        court = inner[: max(1, int(len(inner) * 0.6))]
        for c in court:
            L.plan[c] = COURT
        lot["court"] = court

    # -- the facades
    def facade(self, ctx):
        r = ctx["rnd"]
        e = ctx["epoch"]
        w = self.slot("wall", e)
        thick = 1
        out = ctx["outward"]
        if ctx["ground"]:
            if ctx["door"]:
                return ("wall_door_studded", thick, DOOR)
            if ctx["use"] == SHOP and out in ("main", "plaza", "artery"):
                return ("wall_shopfront_arcade" if r < 0.6 else "wall_shopfront", thick, w)
            if ctx["use"] == CIVIC and out in ("main", "plaza", "lane", "artery"):
                return ("wall_blind_arch", thick, w) if r < 0.5 else ("wall_plain", thick, w)
            if out == "court":
                return ("wall_arch_horseshoe", thick, w)
            if out in ("green", "bank", "rim", "void", "reserved"):
                return ("wall_window_grille" if r < 0.25 else "wall_plain", thick, w)
            return ("wall_window_grille", thick, w) if r < 0.08 else ("wall_plain", thick, w)
        # upper storeys
        s = ctx["stack"]                     # one choice per facade column, so openings stack up the wall
        if out == "court":
            if ctx["use"] == CIVIC:
                return ("wall_window_m", thick, w) if s < 0.5 else ("wall_plain", thick, w)
            return ("wall_gallery", thick, CEDAR) if s < 0.5 else ("wall_window_m", thick, w)
        if e >= 5:
            return ("shack_panel", 0, TIN)
        if ctx["level"] - ctx["gk"] >= 4:                   # a tower house's upper storeys: qamariya lights, screens
            if s < 0.4:
                return ("wall_qamariya", thick, w)
            if s < 0.55:
                return ("wall_screen", thick, w)
            return ("wall_window_grille", thick, w) if s < 0.55 else ("wall_plain", thick, w)
        if out in ("main", "plaza"):
            if s < 0.35:
                return ("wall_window_grille", thick, w)
            if s < 0.55:
                return ("wall_screen", thick, w)           # a small mashrabiya over the street
            return ("wall_plain", thick, w)
        if out in ("lane", "artery", "air"):
            if s < 0.14:
                return ("wall_window_grille", thick, w)
            if s < 0.2:
                return ("wall_screen", thick, w)
            return ("wall_plain", thick, w)
        return ("wall_window_grille" if s < 0.3 else "wall_plain", thick, w)

    def corner(self, kind, level, epoch):
        return ("corner_round" if kind == "out" else "corner_in", 1, self.slot("wall", epoch))

    def roof_edge(self, ctx):
        if ctx["use"] == CIVIC:
            return ("edge_eave_tile_green", 0, ZELLIGE)
        return ("parapet_plain", 1, self.slot("wall", ctx["epoch"]))

    def roof_field(self, i, j, level, epoch):
        return ("roof_terrace", 0, ROOF)

    # -- the marks
    def marks(self, L, rng, emit):
        # the square minaret: a shaft at the mosque's corner, 6-7 storeys, with its lantern top
        lot = getattr(self, "mosque", None)
        if lot:
            cs = [c for c in lot["cells"] if L.plan[c] == LOT]
            if cs:
                c = max(cs, key=lambda c: (c[0] + c[1]))
                g = int(L.gk[c])
                top = g + 6
                for k in range(g, top):
                    if not L.block[c[0], c[1], k]:
                        emit("minaret_square", c[0], c[1], k, 0, 0, 0, WALL_OLD, 1)
                emit("minaret_top", c[0], c[1], top, 0, 0, 0, ZELLIGE, 1)
                L.landmark = c
        # zellige fountains: the central plaza's middle, and the gate plazas
        pc = L.plaza_c
        emit("zellige_fountain", int(pc[0]), int(pc[1]), 0, 0, 4, 0, ZELLIGE, 1)
        # souq stalls round the plaza's edge
        for c in L.plaza:
            if rng.random() < 0.18:
                emit("market_stall", c[0], c[1], 0, rng.randrange(4), 4, 0, TERRA, 2)

    def overlay(self, L, rng, emit, cells):
        p = self.params
        # timber shoring beams across narrow open lanes; cables across lanes, a few
        for (i, j, rot, k) in cells["lane_spans"]:
            r = rng.random()
            if r < 0.12:
                emit("shoring_beam", i, j, k, rot, 0, 0, CEDAR, 3)
            elif r < 0.12 + p["cable"] * 0.4:
                emit("cable_span", i, j, k + 1, rot, 0, 0, TIN, 5)
        # roofs: a sea of dishes, laundry, mint pots
        for (i, j, k) in cells["roofs"]:
            r = rng.random()
            if r < p["dish"] * 0.5:
                emit("satellite_dish", i, j, k, rng.randrange(4), 0, 0, DISH, 5)
            elif r < p["dish"] * 0.5 + 0.04:
                emit("laundry", i, j, k, rng.randrange(4), 0, 0, rng.choice((TERRA, BLUE, LIME, DOOR)), 4)
        # brass LED lanterns at lane junctions and over the souq arteries; festoons along the arteries
        for (i, j) in cells["junctions"]:
            if rng.random() < p["lantern"]:
                emit("lantern", i, j, int(L.gk[i, j]) + 1, 0, 0, 0, BRASS, 5)
        for (i, j) in cells["arteries"]:
            if rng.random() < 0.3:
                emit("festoon", i, j, int(L.gk[i, j]) + 1, 0, 0, 0, LANTERN, 5)

    def foliage(self, L, rng):
        out = []
        # courts: bitter oranges in fours (big courts), one orange or lemon (small), a palm in the largest
        for lot in L.lots:
            ct = lot.get("court") or []
            if not ct:
                continue
            if len(ct) >= 4:
                for c in ct[:4]:
                    out.append(("bitter_orange", c, 0.0, rng.uniform(0.85, 1.15)))
                if len(ct) >= 6:
                    out.append(("date_palm", ct[len(ct) // 2], 0.0, rng.uniform(0.9, 1.2)))
            else:
                out.append((rng.choice(["bitter_orange", "lemon", "banana"]), ct[0], 0.0, rng.uniform(0.8, 1.1)))
        # plazas: figs for shade and palms; greens: palms, oranges, figs; pond banks: palms and reeds
        for i in range(L.nx):
            for j in range(L.nz):
                pc = L.plan[i, j]
                r = rng.random()
                if pc == PLAZA and r < 0.08:
                    out.append((rng.choice(["fig", "date_palm"]), (i, j), 0.0, rng.uniform(0.9, 1.2)))
                elif pc == GREEN and r < 0.35:
                    out.append((rng.choice(["date_palm", "bitter_orange", "fig", "lemon"]), (i, j), 0.0,
                                rng.uniform(0.8, 1.2)))
                elif pc == 4 and r < 0.3:                          # BANK
                    out.append((rng.choice(["date_palm", "reeds", "reeds"]), (i, j), 0.0, rng.uniform(0.8, 1.2)))
        # old walls on lanes: bougainvillea and jasmine climbing; vines over some lanes
        for (i, j, rot, k, epoch) in L.faces_on_lanes:
            if k == int(L.gk[i, j]) and epoch <= 1 and rng.random() < 0.07:
                out.append((rng.choice(["bougainvillea", "jasmine"]), (i, j), rot, rng.uniform(0.8, 1.3)))
        for (i, j) in L.open_lanes:
            if rng.random() < 0.03:
                out.append(("grapevine_pergola", (i, j), 0.0, 1.0))
        # roof terraces: pots
        for (i, j, k) in L.roof_cells:
            if rng.random() < 0.04:
                out.append(("pot_mint_geranium", (i, j, k), 0.0, rng.uniform(0.8, 1.2)))
        return out
