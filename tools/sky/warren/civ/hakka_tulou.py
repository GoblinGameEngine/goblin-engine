"""Hakka tulou: earthen ring-houses (r2_hakka_tulou.md: Yongding and Nanjing counties, Fujian).

The mark: huge round rammed-earth fortresses 30-75 m across, blank and ochre outside with a stone base and only tiny
slit windows high up and one massive gate; inside, 3-5 storeys of timber galleries with lattice doors ringing a
courtyard with the ancestral hall at its centre; one continuous grey tile roof round each ring with a wide eave; 5-12
rings of different sizes in a valley, linked by lanes and later infill; tea terraces as the green."""
import math

from civ.family import FamilyCiv
from lattice import COURT, FREE, LANE


class HakkaTulou(FamilyCiv):
    id = "hakka_tulou"
    name = "Hakka tulou rings"
    arch_mouth = "wall_arch_round"
    covered_ceiling = "floor_slab"
    SPEC = {
        "lanes": "tree",
        "params": {
            "bend_cells": (5, 10), "lane_spacing": 7, "lane_len": 10, "branch": 0.2, "loop": 0.3, "artery_share": 0.1,
            "block_cells": 14, "cut_turn": 3.0, "lot_cells": (3, 6), "courts": False,
            "e1_levels": (3, 4), "max_levels": 5, "civic_levels": 1, "work_share": 0.1, "civic_min_cells": 2,
            "shop_share": 0.3, "ring_radius": (4, 12),
            "epochs": {2: {"rise": 0.45, "setback": 0.0}, 3: {"rise": 0.35, "setback": 0.0}, 4: {"rise": 0.15, "setback": 0.0}},
            "plaza_cells": 6, "main_cells": 3, "garden_cells": (6, 5), "sign": 0.3, "street_blades": 0.02,
            "shacks": 0.0,
        },
        "variants": (0.35, 0.3, 0.25, 0.1), "civic_variant": 3,
        "thick": 1,
        "facade": {
            "door": "wall_door",
            "shop": [("wall_shopfront", 0.6), ("wall_door", 0.4)],
            "ground": {"street": [("wall_plain", 1.0)], "lane": [("wall_plain", 1.0)], "green": [("wall_plain", 1.0)],
                       "court": [("wall_door", 0.4), ("wall_screen", 0.4), ("wall_plain", 0.2)]},
            "upper": {"street": [("wall_plain", 0.85), ("wall_window_s", 0.15)],
                      "lane": [("wall_plain", 0.88), ("wall_window_s", 0.12)],
                      "green": [("wall_plain", 0.85), ("wall_window_s", 0.15)],
                      "air": [("wall_plain", 0.9), ("wall_window_s", 0.1)],
                      "court": [("wall_gallery_timber_t", 0.7), ("wall_screen", 0.3)]},
        },
        "corner": None,
        "roof": {"field": "roof_terrace", "edge": "edge_eave_pagoda", "crown_civic": "roof_tile_flying_eave",
                 "pitched": {"run": "roof_kawara_low", "end": "roof_kawara_low_end", "share": 1.0}},
        "marks": [{"type": "stalls", "share": 0.08}],
        "overlay": {"lantern": 0.5, "festoon": 0.3, "cable": 0.08, "dish": 0.03},
        "foliage": {"green": ["tea_bushes", "tea_bushes", "china_fir", "camphor", "bamboo", "banana"],
                    "bank": ["bamboo", "banana"], "plaza": ["camphor"], "rates": {"green": 0.55}},
        "kit_requests": [
            ("tulou_ring_wall", "a curved rammed-earth ring segment (outer face, stone base, slits) for rings of R 15-35 m (wall, curved)", "straight earth bays on a cell ring"),
            ("tulou_gallery_ring", "the inner timber gallery ring with lattice doors (wall, curved)", "wall_gallery_timber_t"),
            ("roof_ring_tile", "the continuous ring roof with a 2-3 m outer eave (roof, curved run)", "roof_kawara_low runs"),
            ("tulou_gate", "the single massive gate with a stone frame (wall, door)", "wall_door_portal_k"),
            ("ancestral_hall", "the central ancestral hall pavilion (crown)", "roof_tile_flying_eave"),
        ],
    }

    def frame(self, L, rng):
        """the rings: placed on open land, each a band of house cells round a courtyard (kept off the lanes'
        growth until the lanes are laid), a gate passage out to the nearest walkable cell"""
        lo, hi = self.params["ring_radius"]
        from lattice import BANK, GATE, GREEN, OUT, PASTURE, RESERVED, RIM, WATER
        cand = [(i, j) for i in range(L.nx) for j in range(L.nz) if L.plan[i, j] not in (OUT, RIM, WATER)]
        rng.shuffle(cand)
        self.rings = []
        taken = set()
        for R in range(hi, 2, -1):                 # (the big rings first, then smaller ones into what's left)
            for (ci, cj) in cand:
                if len(self.rings) >= 12:
                    break
                if len(self.rings) and R > lo + 2 and rng.random() < 0.5:
                    continue
                disc = [(i, j) for i in range(ci - R - 1, ci + R + 2) for j in range(cj - R - 1, cj + R + 2)
                        if math.hypot(i - ci, j - cj) <= R + 0.5]
                # the band must be open land (or a green / lane the ring may take over); the court may hold anything
                # but the island's edge (a plaza or a garden inside a ring is the clan's court)
                ok = True
                for c in disc:
                    if not L.inb(*c) or c in taken or L.plan[c] in (OUT, RIM, WATER, BANK, GATE, RESERVED) \
                            or L.block[c[0], c[1], :2].any():
                        ok = False
                        break
                    if math.hypot(c[0] - ci, c[1] - cj) > R - 1.7 and L.plan[c] not in (FREE, GREEN, LANE, PASTURE):
                        ok = False
                        break
                if not ok:
                    continue
                self._ring(L, ci, cj, R, disc, taken)

    def _ring(self, L, ci, cj, R, disc, taken):
        """one ring: its band of house cells and its court (both held as court until the lanes are laid)"""
        if True:
            band, inner = [], []
            for c in disc:
                d = math.hypot(c[0] - ci, c[1] - cj)
                (band if d > R - 1.7 else inner).append(c)
            for c in disc:
                taken.add(c)
                for a in (-2, -1, 0, 1, 2):
                    for b in (-2, -1, 0, 1, 2):
                        taken.add((c[0] + a, c[1] + b))
            for c in band:
                L.plan[c] = COURT                  # (held as court until the lanes are laid)
            hall = [c for c in inner if math.hypot(c[0] - ci, c[1] - cj) < 1.5]
            for c in inner:
                if L.plan[c] == FREE:
                    L.plan[c] = COURT
            self.rings.append((ci, cj, R, band, hall))

    def after_lanes(self, L, rng):
        from collections import deque
        from lattice import GREEN, WALKABLE
        # the valley between the rings stays tea terraces (no infill) while the island has rings
        if self.rings:
            ring_cells = set(c for r in self.rings for c in r[3] + r[4])
            for i in range(L.nx):
                for j in range(L.nz):
                    if L.plan[i, j] == FREE and (i, j) not in ring_cells:
                        L.plan[i, j] = GREEN
        for (ci, cj, R, band, hall) in self.rings:
            for c in band + hall:
                L.plan[c] = FREE
            # the gate: a passage through the band toward the nearest walkable cell outside
            bset = set(band)
            best = None
            for c in band:
                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (c[0] + a, c[1] + b)
                    if L.inb(*n) and n not in bset and L.plan[n] in WALKABLE and L.plan[n] != COURT:
                        d = math.hypot(c[0] - ci, c[1] - cj)
                        if best is None or d > best[0]:
                            best = (d, c, (a, b))
            if best is None:
                # no street touches the ring: cut a lane outward from the band's outermost cell to a walkable cell
                c0 = max(band, key=lambda c: math.hypot(c[0] - ci, c[1] - cj))
                q, seen = deque([(c0, [c0])]), {c0}
                while q:
                    c, path = q.popleft()
                    if L.plan[c] in WALKABLE and L.plan[c] != COURT and c not in bset:
                        for p in path:
                            if L.plan[p] in (FREE,):
                                L.plan[p] = LANE
                        break
                    for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        n = (c[0] + a, c[1] + b)
                        if L.inb(*n) and n not in seen and len(path) < 40:
                            seen.add(n)
                            q.append((n, path + [n]))
            else:
                _, c, (a, b) = best
                # walk inward from the outer cell through the band to the court
                cur = c
                while L.inb(*cur) and cur in bset:
                    L.plan[cur] = LANE
                    cur = (cur[0] - a, cur[1] - b)
