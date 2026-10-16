"""family.py -- a warren family from a SPEC (research/sky_islands/warrens r1/r2/r3 grammars): the generic engine's
growth params, the facade grammar as weighted tables per context, roofs, marks, the newest layer and the planting --
all data, so each family module (civ/<family>.py) is mostly its SPEC plus the odd override.

SPEC keys (all optional but params/palettes/facade):
  params      grow.py / spine.py params (lanes, lots, courts, levels, epochs, towers, sabats, jetties)
  lanes       "tree" (bending, branching) | "grid"
  palettes    4 variants {slot: "#rrggbb"} (slots: wall trim frame glass screen roof metal fabric emissive tile water
              ground plant) -- the runtime colours each house with one (pieces.json gets them via the KIT stream)
  variants    weights of the 4 variants per house; "ground_variant": a variant for the ground storey (e.g. a dark base)
  thick       1: thick (_k) walls, 0: thin (_t)
  facade      {"door": id, "door_civic": id, "shop": [(id, w)], "ground": {outward class: [(id, w)]},
               "upper": {outward class: [(id, w)]}, "tower": [(id, w)], "tower_from": storeys above ground}
              outward classes: street (main/plaza/artery/gate), lane, court, green (green/bank/rim/void/reserved/
              water), air (over a lower roof or a gap), shaft; missing classes fall back to "lane"
  cull_slots  True: no piece on faces into blind 1-cell slots (dense families)
  corner      outer corner id or None; corner_in True: the kit's inner filler
  roof        {"field": id, "edge": id, "edge_civic": id, "crown": id, "crown_share": p, "crown_civic": id,
               "crown_band": bool}
  marks       [{"type": "civic_tower", "pieces": [base, shaft, top], "storeys": n} | {"type": "civic_dome"} |
               {"type": "fountain"} | {"type": "stalls", "share": p} | {"type": "playground"}]
  overlay     {"cable": p, "dish": p, "laundry": p, "lantern": p, "festoon": p, "ac": p, "pipe": p, "tank": p,
               "antenna": p, "awning": p, "shoring": p, "fluoro": p}
  foliage     {"court": [species], "plaza": [...], "green": [...], "bank": [...], "lane_wall": [...], "roof": [...],
               "rates": {place: p}}
  kit_requests [(piece id, what it is, stand-in)]
"""
from civ.base import Civ
from lattice import ARTERY, CIVIC, COURT, GREEN, LANE, LOT, MAIN, PLAZA, SHOP

STREET = ("main", "plaza", "artery", "gate")
GREENISH = ("green", "bank", "rim", "void", "reserved", "water")


def wchoice(table, r):
    tot = sum(w for _, w in table)
    acc = 0.0
    for pid, w in table:
        acc += w / tot
        if r < acc:
            return pid
    return table[-1][0]


class FamilyCiv(Civ):
    SPEC = {}

    def __init__(self, isl, rng):
        super().__init__(isl, rng)
        sp = self.SPEC
        self.params = dict(sp.get("params", {}))
        self.lanes = sp.get("lanes", "tree")
        self.PALETTES = sp.get("palettes") or self._kit_palettes()
        self.palette = [v["wall"] for v in self.PALETTES]
        self.species = sorted({s for v in sp.get("foliage", {}).values() if isinstance(v, list) for s in v})

    def _kit_palettes(self):
        import json
        from pieces import KIT_JSON
        return json.load(open(KIT_JSON))["palettes"][self.id]

    # -- colour: one variant per house
    @property
    def base_palette(self):
        return self.SPEC.get("base_variant", 0)

    def lot_palette(self, lot):
        from pick import h01
        if lot.get("kind") == "civic" and "civic_variant" in self.SPEC:
            return self.SPEC["civic_variant"]
        w = self.SPEC.get("variants", (1, 1, 1, 1))
        r = h01(self.isl["id"], "pal", lot["id"]) * sum(w)
        acc = 0
        for n, x in enumerate(w):
            acc += x
            if r < acc:
                return n
        return 0

    def cell_palette(self, lot, rel):
        gv = self.SPEC.get("ground_variant")
        if gv is not None and rel == 0:
            return gv
        return self.lot_palette(lot)

    def slot(self, name, epoch=1, ij=(0, 0)):
        return 0

    # -- the plan
    def mark_lots(self, L, rng):
        """the civic building: the biggest lot on (or next to) the central plaza"""
        self.L = L
        best = None
        pc = L.plaza_c
        for lot in L.lots:
            if len(lot["cells"]) < self.params.get("civic_min_cells", 10):
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
            lot["cap"] = self.params.get("civic_levels", 2)
            lot["notower"] = True
            self.civic = lot

    def before_found(self, L, rng):
        """stilt houses (diaojiaolou): lots on the drop (next to green, bank, rim or the edge) stand their back cells
        on stilts a storey up"""
        from lattice import BANK, OUT, RIM
        share = self.params.get("stilts", 0)
        if not share:
            return
        from pick import h01
        edge = (GREEN, BANK, RIM, OUT)
        for lot in L.lots:
            if lot.get("kind") == "civic" or h01(L.seed, "stilt", lot["id"]) >= share:
                continue
            cs = set(lot["cells"])
            front = set(c for c, _ in lot["front"])
            drop = any(L.inb(c[0] + a, c[1] + b) and L.plan[c[0] + a, c[1] + b] in edge
                       for c in cs for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if not drop:
                continue
            for c in cs - front:
                L.lift[c] = 1

    def courts_for_civic(self, L, rng):
        lot = getattr(self, "civic", None)
        if not lot or not self.SPEC.get("civic_court", False):
            return
        cs = set(lot["cells"])
        inner = [c for c in lot["cells"] if all((c[0] + a, c[1] + b) in cs for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        inner.sort()
        court = inner[: max(1, int(len(inner) * 0.5))]
        for c in court:
            L.plan[c] = COURT
        lot["court"] = court

    # -- the facades
    def _cls(self, out):
        if out in STREET:
            return "street"
        if out in GREENISH:
            return "green"
        return out if out in ("lane", "court", "air", "shaft") else "lane"

    def facade(self, ctx):
        f = self.SPEC["facade"]
        th = self.SPEC.get("thick", 0)
        # (epoch 5 was the roof village -- its huts become ov_shack overlays and their rooms are cleared before the
        # pieces (make_warren.py); a room of epoch 5 still standing here was grown later (walknet storeys) and needs
        # its walls: the audit's SKY-071 rooms open on every side at the top)
        if self.SPEC.get("cull_slots") and ctx.get("slot") == "blind":
            return None
        if self.SPEC.get("cull_slots") and ctx.get("slot") == "lane":
            return ("wall_plain", th, 0)
        cls = self._cls(ctx["outward"])
        if ctx["ground"]:
            if ctx["door"]:
                return (f.get("door_civic", f.get("door", "wall_door")) if ctx["use"] == CIVIC else f.get("door", "wall_door"), th, 0)
            if ctx["use"] == SHOP and cls == "street" and f.get("shop"):
                return (wchoice(f["shop"], ctx["rnd"]), th, 0)
            if ctx["use"] == CIVIC and f.get("civic_ground"):
                return (wchoice(f["civic_ground"], ctx["rnd"]), th, 0)
            g = f["ground"]
            return (wchoice(g.get(cls) or g["lane"], ctx["rnd"]), th, 0)
        rel = ctx["level"] - ctx["gk"]
        vf = f.get("variant_upper")
        if vf:
            L = self.L
            lid = int(L.lot[ctx["i"], ctx["j"]])
            if lid >= 0:
                t = vf.get(self.lot_palette(L.lots[lid]))
                if t:
                    pid = wchoice(t, ctx["stack"])
                    return (pid, th, 0) if pid else None
        if f.get("tower") and rel >= f.get("tower_from", 99):
            return (wchoice(f["tower"], ctx["stack"]), th, 0)
        if ctx["use"] == CIVIC and f.get("civic_upper"):
            return (wchoice(f["civic_upper"], ctx["stack"]), th, 0)
        u = f["upper"]
        t = u.get(cls) or u["lane"]
        pid = wchoice(t, ctx["stack"])
        return (pid, th, 0) if pid else None

    def pave(self, L, plan_class, c, default):
        """SPEC "pave": {generator paving id: kit paving id} (e.g. the falaj lane, herringbone brick)"""
        return self.SPEC.get("pave", {}).get(default, default)

    def corner(self, kind, level, epoch):
        th = self.SPEC.get("thick", 0)
        if kind == "out":
            c = self.SPEC.get("corner", "corner_out")
            return (c, th, 0) if c else None
        return ("corner_in", th, 0) if self.SPEC.get("corner_in", True) else None

    def roof_field(self, i, j, level, epoch):
        return (self.SPEC.get("roof", {}).get("field", "roof_terrace"), 0, 0)

    def roof_edge(self, ctx):
        r = self.SPEC.get("roof", {})
        th = self.SPEC.get("thick", 0)
        if ctx["use"] == CIVIC and r.get("edge_civic"):
            return (r["edge_civic"], th, 0)
        if r.get("edge_street"):
            # a house front on a street or lane gets the family's front piece (gables), the rest the plain edge
            from pick import FACE, h01
            L = self.L
            di, dj = FACE[ctx["rot"]]
            n = (ctx["i"] + di, ctx["j"] + dj)
            lid = int(L.lot[ctx["i"], ctx["j"]])
            if lid >= 0 and L.inb(*n) and L.plan[n] in (LANE, ARTERY, MAIN, PLAZA) \
                    and not L.occ[n[0], n[1], ctx["level"] - 1]:
                lot = L.lots[lid]
                key = (ctx["i"], ctx["j"], ctx["rot"], ctx["level"])
                if lot.setdefault("front_piece", key) == key:      # one per house (its first street bay)
                    return (wchoice(r["edge_street"], h01(L.seed, "gable", ctx["i"], ctx["j"])), th, 0)
        e = r.get("edge", "parapet_plain")
        return (e, th, 0) if e else None

    def pitched(self, L, lot, lv):
        """the kit's pitched roof run for this house at this roof level, or None (SPEC roof.pitched:
        {"run": id, "end": id, "share": p, "variants": [..], "max_rel": n, "civic": bool})"""
        from pick import h01
        pr = self.SPEC.get("roof", {}).get("pitched")
        if not pr:
            return None
        if lot.get("use") == CIVIC and not pr.get("civic", False):
            return None
        if "variants" in pr and self.lot_palette(lot) not in pr["variants"]:
            return None
        if "max_rel" in pr:
            g = min(int(L.gk[c]) for c in lot["cells"])
            if lv - g > pr["max_rel"]:
                return None
        if h01(L.seed, "pitch", lot["id"]) >= pr.get("share", 1.0):
            return None
        return (pr["run"], pr.get("end", pr["run"]))

    def roof_extra(self, L, i, j, lv):
        """kit pieces added on a roof field (kitmap): crowns (pitched-roof stand-ins, domes)"""
        from pick import h01
        r = self.SPEC.get("roof", {})
        lot = L.lots[L.lot[i, j]] if L.lot[i, j] >= 0 else None
        if lot is not None and lot.get("use") == CIVIC and r.get("crown_civic"):
            return [r["crown_civic"]]
        if r.get("crown") and h01(L.seed, "crown", i, j) < r.get("crown_share", 1.0):
            return [r["crown"]]
        return []

    def edge_extra(self):
        return ["crown_band"] if self.SPEC.get("roof", {}).get("crown_band") else []

    # -- marks
    def marks(self, L, rng, emit):
        lot = getattr(self, "civic", None)
        for m in self.SPEC.get("marks", []):
            t = m["type"]
            if t == "civic_tower" and lot:
                cs = [c for c in lot["cells"] if L.plan[c] == LOT]
                doorc = set(tuple(o["door"][0]) for o in L.lots if o.get("door"))
                cs = [c for c in cs if tuple(c) not in doorc] or cs   # (the tower not in a doorway)
                if not cs:
                    continue
                c = max(cs, key=lambda c: (c[0] + c[1]))
                g = int(L.gk[c])
                n = m.get("storeys", 5)
                base, shaft, top = m["pieces"][:3]
                crowns = m["pieces"][3:]
                for k in range(g, g + n):
                    if k < L.L and not L.block[c[0], c[1], k]:
                        emit(base if k == g else shaft, c[0], c[1], k, 0, 0, 0, 0, 1)
                if g + n < L.L and top:
                    emit(top, c[0], c[1], g + n, 0, 0, 0, 0, 1)
                for q, cr in enumerate(crowns):           # (a cupola, a spire: stacked on the top piece)
                    if g + n + 1 + q < L.L:
                        emit(cr, c[0], c[1], g + n + 1 + q, 0, 0, 0, 0, 1)
                L.landmark = c
            elif t == "fountain":
                pc = (int(L.plaza_c[0]), int(L.plaza_c[1]))
                kc = getattr(L, "keep_clear", set())
                if pc in kc:
                    # (not on a door's step or a stair: the nearest clear plaza cell)
                    free = [c for c in L.plaza if tuple(c) not in kc]
                    pc = min(free, key=lambda c: abs(c[0] - pc[0]) + abs(c[1] - pc[1])) if free else None
                if pc is not None:
                    emit(m.get("piece", "fountain_basin"), int(pc[0]), int(pc[1]), 0, 0, 4, 0, 0, 1)
            elif t == "stalls":
                for c in L.plaza:
                    if rng.random() < m.get("share", 0.15) and tuple(c) not in getattr(L, "keep_clear", ()):
                        emit("market_stall", c[0], c[1], 0, rng.randrange(4), 4, 0, 0, 2)
            elif t == "roof_towers":
                # wind towers, corner towers: small stacks standing on a share of the roofs
                from pick import h01
                lo, hi = m.get("storeys", (1, 2))
                for (i, j, k) in L.roof_cells:
                    if h01(L.seed, "rt", i, j) >= m.get("share", 0.05):
                        continue
                    n = lo + int(h01(L.seed, "rtn", i, j) * (hi - lo + 1))
                    for kk in range(k, min(k + n, L.L)):
                        if L.block[i, j, kk]:
                            break
                        emit(m["piece"], i, j, kk, 0, 0, 0, 0, 3)
                    else:
                        if m.get("top") and k + n < L.L:
                            emit(m["top"], i, j, k + n, 0, 0, 0, 0, 3)
            elif t == "water_bridge":
                # bridges over the narrow necks of the ponds: land, 1-2 water cells, land (span 3 along +Z from the
                # first cell)
                from lattice import WATER, WALKABLE
                n = 0
                for i in range(L.nx):
                    for j in range(L.nz):
                        if n >= m.get("max", 3):
                            break
                        for d, kr in (((0, 1), 0), ((1, 0), 1)):
                            a = (i - d[0], j - d[1])
                            if not (L.inb(*a) and L.plan[a] in WALKABLE and L.plan[a] != WATER and L.plan[i, j] == WATER):
                                continue
                            c1, c2 = (i + d[0], j + d[1]), (i + 2 * d[0], j + 2 * d[1])
                            if L.inb(*c2) and L.plan[c1] != WATER and L.plan[c1] in WALKABLE:
                                s0 = a                        # land, water, land: start on the near bank
                            elif L.inb(*c2) and L.plan[c1] == WATER and L.plan[c2] in WALKABLE and L.plan[c2] != WATER:
                                s0 = (i, j)                   # water, water, land
                            else:
                                continue
                            # (the generator's rot whose kit rot turns +Z along d: kit = gen + 2)
                            emit(m["piece"], s0[0], s0[1], 0, (kr + 2) & 3, 4, 0, 0, 2)
                            n += 1
                            break
            elif t == "plan_piece":
                # a piece on a share of the cells of a plan class (a tram on the main street, a windmill on a green,
                # a basketball court): along the street where it has an axis
                from lattice import PLAN_NAMES
                from pick import h01
                cls = PLAN_NAMES.index(m["cls"]) if isinstance(m["cls"], str) else m["cls"]
                n = 0
                for i in range(L.nx):
                    for j in range(L.nz):
                        if L.plan[i, j] != cls or L.occ[i, j, int(L.gk[i, j])] or h01(L.seed, m["piece"], i, j) >= m["share"] \
                                or (i, j) in getattr(L, "keep_clear", ()):
                            continue
                        alongx = L.inb(i + 1, j) and L.plan[i + 1, j] == cls and L.inb(i - 1, j) and L.plan[i - 1, j] == cls
                        emit(m["piece"], i, j, 0, 3 if alongx else 0, 4, 0, 0, m.get("epoch", 5))
                        n += 1
                        if n >= m.get("max", 99):
                            break
                    if n >= m.get("max", 99):
                        break
            elif t == "door_face" and lot and lot.get("door"):
                # a monumental portal on the civic door's face (pishtaq)
                (c, rot) = lot["door"]
                emit(m["piece"], c[0], c[1], int(L.gk[c]), rot, 0, 0, 0, 1)
            elif t == "gate_piece" and lot and lot.get("door"):
                # a gate before the civic door (a torii)
                from pick import FACE
                (c, rot) = lot["door"]
                di, dj = FACE[rot]
                n = (c[0] + di * 2, c[1] + dj * 2)
                if L.inb(*n) and not L.occ[n[0], n[1], int(L.gk[n])]:
                    emit(m["piece"], n[0], n[1], 0, 1 if di == 0 else 0, 4, 0, 0, 1)
            elif t == "bank_steps":
                # ghats: broad steps down into the water from the pond banks.  The flight stands IN the water cell
                # (2026-10-15: the bank stays flat paving for the walk), its top at the bank's graded edge: a
                # toward_water piece hangs down from y 0 along +Z; the plain "steps" rise out of the water to the bank
                from lattice import BANK, WATER
                from pick import FACE
                used = set()
                L.kerb_skip = getattr(L, "kerb_skip", set())
                span = 2 if m.get("piece") == "ghat_steps_wide" else 1
                for i in range(L.nx):
                    for j in range(L.nz):
                        if L.plan[i, j] != BANK or L.occ[i, j, int(L.gk[i, j])] or (i, j) not in getattr(L, "q", {}):
                            continue
                        qb = L.q[(i, j)]
                        for rot, (di, dj) in FACE.items():
                            n = (i + di, j + dj)
                            if n in used or not all(L.inb(i + di * s, j + dj * s) and L.plan[i + di * s, j + dj * s] == WATER
                                                    for s in range(1, span + 1)):
                                continue
                            if m.get("toward_water"):
                                emit(m["piece"], n[0], n[1], qb // 4, rot, (qb % 4) << 4, 0, 0, 0)
                            elif qb >= 2:
                                qq = qb - 2
                                emit(m.get("piece", "steps"), n[0], n[1], qq // 4, (rot + 2) & 3, (qq % 4) << 4, 0, 0, 0)
                            else:
                                continue
                            used.update((i + di * s, j + dj * s) for s in range(1, span + 1))
                            L.kerb_skip.add((i, j, rot))
                            break
            elif t == "playground" and L.roof_cells:
                k = max(c[2] for c in L.roof_cells)
                flat = [c for c in L.roof_cells if c[2] >= k - 1]
                c = flat[len(flat) // 2]
                emit("roof_playground", c[0], c[1], c[2], 0, 0, 0, 0, 5)

    # -- the newest layer
    def overlay(self, L, rng, emit, cells):
        o = self.SPEC.get("overlay", {})
        for (i, j, rot, k) in cells["lane_spans"]:
            r = rng.random()
            if r < o.get("shoring", 0):
                emit("shoring_beam", i, j, k, rot, 0, 0, 0, 3)
            elif r < o.get("shoring", 0) + o.get("cable", 0):
                emit("cable_span", i, j, k + 1, rot, 0, 0, 0, 5)
            elif r < o.get("shoring", 0) + o.get("cable", 0) + o.get("lane_laundry", 0):
                emit("laundry", i, j, k + 1, rot, 0, 0, 0, 4)
        for (i, j, rot, k) in cells["lane_spans"]:
            r = rng.random()
            acc = 0.0
            for pid, p in o.get("spans", []):
                acc += p
                if r < acc:
                    emit(pid, i, j, k + 1, rot, 0, 0, 0, 5)
                    break
            # sagging cables at further storeys (a canyon of wires two or three levels deep)
            for dk in range(1, o.get("cable_levels", 1)):
                if L.occ[i, j, min(k + dk, L.L - 1)] or rng.random() >= o.get("cable", 0):
                    continue
                emit("cable_span", i, j, k + 1 + dk, rot, 0, 0, 0, 5)
        band = o.get("band")
        if band:
            from pick import h01
            for (i, j, k, rot, stack) in cells["upper_faces"]:
                if k - int(L.gk[i, j]) >= band.get("from", 1) and h01(L.seed, "band", i, j, rot) < band["p"]:
                    emit(band["piece"], i, j, k, rot, 0, 0, 0, 2)
        for (i, j, k, rot) in cells["covered"]:
            if rng.random() < o.get("fluoro", 0):
                emit("fluoro_tube", i, j, k, rot, 0, 0, 0, 5)
        for (i, j, k, rot, stack) in cells["upper_faces"]:
            if rng.random() < o.get("ac", 0):
                emit("ac_unit", i, j, k, rot, 0, 0, 0, 5)
            if stack < 0.3 and rng.random() < o.get("pipe", 0):
                emit("pipe_run", i, j, k, rot, 0, 0, 0, 4)
        for (i, j, k) in cells["roofs"]:
            r = rng.random()
            acc = 0.0
            for key, pid in (("dish", "satellite_dish"), ("tank", "water_tank"), ("antenna", "antenna"),
                             ("laundry", "laundry")):
                acc += o.get(key, 0)
                if r < acc:
                    emit(pid, i, j, k, rng.randrange(4), 0, 0, 0, 5)
                    break
        for (i, j) in cells["junctions"]:
            if rng.random() < o.get("lantern", 0):
                emit("lantern", i, j, int(L.gk[i, j]) + 1, rng.randrange(4), 0, 0, 0, 5)
        for (i, j) in cells["arteries"]:
            if rng.random() < o.get("festoon", 0):
                emit("festoon", i, j, int(L.gk[i, j]) + 1, 0, 0, 0, 0, 5)
        if o.get("sign_column"):
            # vertical lit sign stacks up the street faces of the towers (one column per shop bay, a share)
            from pick import h01
            for (i, j, k, rot, use, is_door) in L.shop_faces:
                if h01(L.seed, "sigcol", i, j, rot) >= o["sign_column"]:
                    continue
                kk = k + 1
                while kk < L.L and L.occ[i, j, kk] and kk - k <= o.get("sign_column_max", 8):
                    emit("wall_sign_column_t", i, j, kk, rot, 0, 0, 0, 5)
                    kk += 1
        if o.get("vending"):
            for (i, j, rot, k, epoch) in L.faces_on_lanes:
                if k == int(L.gk[i, j]) and rng.random() < o["vending"]:
                    emit("ov_vending_machine", i, j, k, rot, 0, 0, 0, 5)
        if o.get("pole"):
            # (a pole stands at its cell's centre: never on a walk cell -- the audit found 2,798 walk edges blocked by
            # poles on junctions; one goes on an open cell beside the junction that nobody walks, or none)
            from lattice import WALKABLE as _WK
            for (i, j) in cells["junctions"]:
                if rng.random() < o["pole"]:
                    for di, dj in ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        c = (i + di, j + dj)
                        if L.inb(*c) and c not in L.W and int(L.plan[c]) in _WK and not L.occ[c[0], c[1], int(L.gk[c])] \
                                and c not in getattr(L, "keep_clear", ()):
                            emit(o.get("pole_piece", "utility_pole"), c[0], c[1], 0, rng.randrange(4), 4, 0, 0, 4)
                            break
        if o.get("covered_piece"):
            # a vault carrying the lane under the houses (abbara): on a share of the covered lane cells
            for (i, j, k, rot) in cells["covered"]:
                if rng.random() < o["covered_piece"][1]:
                    emit(o["covered_piece"][0], i, j, int(L.gk[i, j]), rot, 0, 0, 0, 1)
        for pid, p in o.get("roof_items", []):
            for (i, j, k) in cells["roofs"]:
                if rng.random() < p:
                    emit(pid, i, j, k, rng.randrange(4), 0, 0, 0, 5)
        # pieces hung on faces: {"piece", "p", "where": ground|upper|top, "street": only street-facing}
        # (the entrances: a lot's door, every door face, a shop cell's first shop face (its door, units.make_units):
        # nothing hung at the ground storey goes on them -- benches, panels, shutters stood in the doorways, the
        # audit's door entries)
        entr = set()
        first = {}
        for (i, j, k, rot, use, d) in L.shop_faces:
            first.setdefault((i, j, k), rot)
            if d:
                entr.add((i, j, k, rot))
        entr |= {(i, j, k, r) for (i, j, k), r in first.items()}
        for lot in L.lots:
            if lot.get("door"):
                (dc, dr) = lot["door"]
                entr.add((dc[0], dc[1], lot.get("door_k", int(L.gk[dc])), dr))
        for fi in o.get("face_items", []):
            from pick import h01
            if fi.get("where", "ground") == "ground":
                src = [(i, j, k, rot) for (i, j, rot, k, ep) in L.faces_on_lanes if k == int(L.gk[i, j])]
                if fi.get("shops"):
                    src = [(i, j, k, rot) for (i, j, k, rot, use, d) in L.shop_faces if use == SHOP]
                    if "shutter" in fi["piece"]:
                        # (a shutter down over the shop's own door shuts it -- units.make_units takes a shop cell's
                        # first shop face as its door; the audit found shops entered through a closed shutter)
                        first = {}
                        for (i, j, k, rot, use, d) in L.shop_faces:
                            first.setdefault((i, j, k), rot)
                        src = [(i, j, k, rot) for (i, j, k, rot) in src if first.get((i, j, k)) != rot]
            else:
                src = [(i, j, k, rot) for (i, j, k, rot, st) in cells["upper_faces"]]
                if fi.get("where") == "top":
                    src = [(i, j, k, rot) for (i, j, k, rot) in src if k + 1 >= L.L or not L.occ[i, j, k + 1]]
            if fi.get("where", "ground") == "ground":
                src = [(i, j, k, rot) for (i, j, k, rot) in src if (i, j, k, rot) not in entr]
            for (i, j, k, rot) in src:
                if h01(L.seed, fi["piece"], i, j, k, rot) < fi["p"]:
                    emit(fi["piece"], i, j, k + fi.get("dk", 0), rot, 0, 0, 0, fi.get("epoch", 4))
        if o.get("wall_pots"):
            for (i, j, rot, k, epoch) in L.faces_on_lanes:
                if k == int(L.gk[i, j]) and rng.random() < o["wall_pots"]:
                    emit("planter", i, j, k, rot, 0, 0, 0, 4)
        if o.get("street_stair"):
            # outdoor stairs up the fronts (Montreal plex): a spiral on the street before a share of the doors
            from pick import FACE
            for lot in L.lots:
                if not lot.get("door") or rng.random() >= o["street_stair"]:
                    continue
                (c, rot) = lot["door"]
                di, dj = FACE[rot]
                n = (c[0] + di, c[1] + dj)
                if L.inb(*n) and L.plan[n] in (LANE, MAIN) and not L.occ[n[0], n[1], int(L.gk[n])]:
                    emit(o.get("street_stair_piece", "stair_spiral"), n[0], n[1], 0, rot, 4, 0, 0, 3)
        if o.get("awning"):
            from pick import FACE
            for (i, j, k, rot, use, is_door) in L.shop_faces:
                if use == SHOP and rng.random() < o["awning"]:
                    di, dj = FACE[rot]
                    n = (i + di, j + dj)
                    if L.inb(*n) and not L.occ[n[0], n[1], k]:
                        emit("awning", n[0], n[1], k, 0, 0, 0, 0, 5)

    # -- planting
    def foliage(self, L, rng):
        from lattice import BANK
        fo = self.SPEC.get("foliage", {})
        rates = {"court": 0.6, "plaza": 0.08, "green": 0.35, "bank": 0.3, "lane_wall": 0.05, "roof": 0.04, "lane": 0.02}
        rates.update(fo.get("rates", {}))
        out = []
        for lot in L.lots:
            for c in (lot.get("court") or [])[:4]:
                if fo.get("court") and rng.random() < rates["court"]:
                    out.append((rng.choice(fo["court"]), c, 0.0, rng.uniform(0.85, 1.15)))
        for i in range(L.nx):
            for j in range(L.nz):
                pc = L.plan[i, j]
                key = {PLAZA: "plaza", GREEN: "green", BANK: "bank"}.get(int(pc))
                if key and fo.get(key) and rng.random() < rates[key]:
                    out.append((rng.choice(fo[key]), (i, j), 0.0, rng.uniform(0.8, 1.2)))
        for (i, j, rot, k, epoch) in L.faces_on_lanes:
            if fo.get("lane_wall") and k == int(L.gk[i, j]) and rng.random() < rates["lane_wall"]:
                out.append((rng.choice(fo["lane_wall"]), (i, j), rot, rng.uniform(0.8, 1.3)))
        for (i, j) in L.open_lanes:
            if fo.get("lane") and rng.random() < rates["lane"]:
                out.append((rng.choice(fo["lane"]), (i, j), 0.0, 1.0))
        for (i, j, k) in L.roof_cells:
            if fo.get("roof") and rng.random() < rates["roof"]:
                out.append((rng.choice(fo["roof"]), (i, j, k), 0.0, rng.uniform(0.8, 1.2)))
        return out
