"""pick.py -- the dual-grid piece pass (r4_design §3): the grown lattice to kit-piece placements.

Every exterior face of a room gets a wall piece chosen by the civ's facade grammar from what it faces (street, lane,
court, air over a lane ...), its level, use, age and its facade column (openings stack up a wall); corners from the
four cells round each corner; roof fields and edges on tops; soffits under overhangs and bridges; plinths on slopes;
paving on the open ground (DECK: following the deck), arches at tunnel mouths, steps on slopes; interiors only in the
cells you can enter; then the civ's marks, the newest layer (E5) and the sign anchors.
"""
import math

from lattice import (ARTERY, BANK, CELL, CIVIC, COURT, GATE, GREEN, HOME, LANE, LOT, MAIN, OUT, PASTURE, PLAZA,
                     RESERVED, RIM, SHOP, STOREY, STREETS, WALKABLE, WATER, WORK)

# rot -> the neighbour across that face (FORMAT.md: rot 0 the -Z face, 1 -X, 2 +Z, 3 +X)
FACE = {0: (0, -1), 1: (-1, 0), 2: (0, 1), 3: (1, 0)}
ROT_OF = {v: k for k, v in FACE.items()}
CORNER_ROT = {(-1, -1): 0, (-1, 1): 1, (1, 1): 2, (1, -1): 3}
OUT_NAME = {MAIN: "main", PLAZA: "plaza", ARTERY: "artery", LANE: "lane", COURT: "court", GREEN: "green", BANK: "bank",
            PASTURE: "green", RIM: "rim", GATE: "gate", RESERVED: "reserved", WATER: "water", OUT: "void", LOT: "lot"}
PAVE = {MAIN: "pave_main", ARTERY: "pave_main", PLAZA: "pave_plaza", GATE: "pave_plaza", LANE: "pave_lane",
        RIM: "pave_lane", RESERVED: "pave_plaza", COURT: "pave_court", GREEN: "pave_garden", BANK: "pave_garden",
        PASTURE: "pave_garden"}
DECK = 4
MIRROR = 8


def h01(*a):
    """a stable hash in [0, 1) of the arguments (local, deterministic: no world positions)"""
    x = 2166136261
    for v in a:
        for ch in str(v):
            x = ((x ^ ord(ch)) * 16777619) & 0xFFFFFFFF
        x = ((x ^ 0x9E37) * 16777619) & 0xFFFFFFFF
    return (x % 1000003) / 1000003.0


class Out:
    def __init__(self):
        self.recs = []          # (piece, i, j, level, rot, flags, variant, slot, epoch)
        self.anchors = []       # [name, x, y, z, yaw]

    def emit(self, piece, i, j, level, rot, flags, variant, slot, epoch):
        self.recs.append((piece, int(i), int(j), int(level), int(rot) & 3, int(flags), int(variant) & 15,
                          int(slot) & 15, int(epoch) & 15))


def walk_ground(L, n):
    """the surface next door: graded ground, a building's ground floor, the deck"""
    if n in L.q:
        return L.q[n] * 0.8
    if not L.inb(*n):
        return -99.0
    if L.occ[n[0], n[1], int(L.gk[n])]:
        return int(L.gk[n]) * STOREY
    return float(L.ground[n])


def lane_width(L, n, d):
    """open walkable cells in a row from n onward along d (the lane's width across this face)"""
    w = 0
    c = n
    while L.inb(*c) and L.plan[c] in WALKABLE and w < 5:
        w += 1
        c = (c[0] + d[0], c[1] + d[1])
    return w


def covered_at(L, c):
    """a lane cell with rooms over it (a tunnel)"""
    g = int(L.gk[c])
    return any(L.occ[c[0], c[1], k] for k in range(g + 1, min(g + 3, L.L)))


def is_slot(L, c, d, k):
    """open cell c at level k with rooms on both sides along d"""
    a = (c[0] - d[0], c[1] - d[1])
    b = (c[0] + d[0], c[1] + d[1])
    return (L.inb(*c) and not L.occ[c[0], c[1], k] and L.inb(*a) and L.inb(*b) and bool(L.occ[a[0], a[1], k])
            and bool(L.occ[b[0], b[1], k]))


DOORLIKE = ("door", "noren", "basso", "gate", "portal", "pend", "moon_gate", "five_foot_way", "qilou", "shopboards",
            "shopfront", "triangles")


def _is_doorlike(pid):
    return any(t in pid for t in DOORLIKE)


def choose_doors(L, rng, civ):
    """each lot's front door (prefer lanes for homes, the street for shops), and its shop cells"""
    for lot in L.lots:
        lot["door"] = None
        fr = [(c, m) for c, m in lot["front"] if L.occ[c[0], c[1], int(L.gk[c])] and L.plan[c] != COURT]
        if not fr:
            continue
        pref = (LANE, ARTERY, RIM, GATE, RESERVED, MAIN, PLAZA) if lot["use"] != CIVIC else (PLAZA, MAIN, LANE, ARTERY)
        fr.sort(key=lambda cm: (pref.index(L.plan[cm[1]]) if L.plan[cm[1]] in pref else 9, h01(L.seed, cm)))
        c, m = fr[0]
        lot["door"] = (c, ROT_OF[(m[0] - c[0], m[1] - c[1])])
        shops = set()
        for c2, m2 in lot["front"]:
            if L.plan[m2] in (MAIN, PLAZA, ARTERY) and lot["use"] != CIVIC and L.occ[c2[0], c2[1], int(L.gk[c2])] \
                    and h01(L.seed, "shop", c2) < civ.params.get("shop_share", 1.0):
                shops.add(c2)
        lot["shop_cells"] = shops


def run(L, civ, rng):
    o = Out()
    choose_doors(L, rng, civ)
    # the walkable ground graded, the entrances placed where the ground meets them, the walk check (walk.py)
    import walk
    tc = L.cell_of(L.travel[0], L.travel[2])
    import walknet
    L.walk_stats = walknet.solve(L, civ, tc)
    x, _, z = L.centre(*L.travel_cell)
    L.travel[1] = round(walk.ground_y(L, L.travel_cell), 2)
    door_at = {}
    shop_cell = {}
    lot_use = {}
    for lot in L.lots:
        if lot.get("door"):
            door_at[(lot["door"][0], lot["door"][1], lot["door_k"])] = lot["id"]
        for c in lot.get("shop_cells", ()):
            shop_cell[c] = lot["id"]
        for c in lot["cells"]:
            lot_use[c] = lot["use"]
    collect = {"lane_spans": [], "roofs": [], "junctions": [], "arteries": [], "covered": [], "upper_faces": []}
    L.faces_on_lanes = []
    L.roof_cells = []
    L.open_lanes = []
    L.shop_faces = []
    L.street_upper = []
    nx, nz, NL = L.nx, L.nz, L.L
    occ = L.occ
    # ---------------------------------------------------------------- the shell
    for i in range(nx):
        for j in range(nz):
            g = int(L.gk[i, j])
            for k in range(NL):
                if not occ[i, j, k]:
                    continue
                ep = int(L.epoch[i, j, k])
                use = lot_use.get((i, j), HOME)
                if k == g and (i, j) in shop_cell:
                    use = SHOP
                # faces
                for rot, (di, dj) in FACE.items():
                    n = (i + di, j + dj)
                    if L.inb(*n) and occ[n[0], n[1], k]:
                        continue                                    # (a party wall: no exterior)
                    pn = int(L.plan[n]) if L.inb(*n) else OUT
                    gn = int(L.gk[n]) if L.inb(*n) else 0
                    if L.inb(*n) and k < gn and pn != OUT:
                        continue                                    # (against the slope: buried)
                    if k == g and k == gn or (k == g and pn in WALKABLE):
                        outward = OUT_NAME.get(pn, "lane")
                    else:
                        outward = "air" if pn not in (COURT,) else "court"
                        if pn in (MAIN, PLAZA):
                            outward = OUT_NAME[pn]
                    if pn == LANE and (n in getattr(L, "open_shafts", ())) and k > g:
                        outward = "shaft"
                    # a slot: the open cell outside is one cell wide between this room and another at this level
                    slot = None
                    far = (n[0] + di, n[1] + dj)
                    if k > g and L.inb(*far) and occ[far[0], far[1], k]:
                        slot = "lane" if pn in WALKABLE and k <= int(L.gk[n]) + 2 else "blind"
                        for sd in ((dj, di), (-dj, -di)):
                            m = (n[0] + sd[0], n[1] + sd[1])
                            if not L.inb(*m) or not occ[m[0], m[1], k] and not is_slot(L, m, (di, dj), k):
                                slot = "end"                # (the slot opens here: seen from outside)
                                break
                    ctx = {"level": k, "gk": g, "ground": k == g, "use": use, "epoch": ep, "outward": outward,
                           "door": door_at.get(((i, j), rot, k)) is not None, "i": i, "j": j, "rot": rot,
                           "lane_w": lane_width(L, n, (di, dj)) if L.inb(*n) else 0,
                           "stack": h01(L.seed, "stack", i, j, rot), "rnd": h01(L.seed, "f", i, j, k, rot),
                           "covered": L.inb(*n) and pn in (LANE, ARTERY) and covered_at(L, n), "slot": slot}
                    pc = civ.facade(ctx)
                    if pc and not ctx["door"] and _is_doorlike(pc[0]):
                        # no door onto air, none onto ground that does not meet its floor: a door is an entrance only
                        ok = k == g and n in L.W and L.q[n] == 4 * k and not (use == SHOP and n in L.stoop)
                        if not ok:
                            pc = ("wall_window_s" if k > g else "wall_plain", pc[1], pc[2])
                    if pc and ctx["door"] and not _is_doorlike(pc[0]):
                        pc = (getattr(civ, "SPEC", {}).get("facade", {}).get("door", "wall_door"), pc[1], pc[2])
                    if pc:
                        o.emit(pc[0], i, j, k, rot, 0, pc[1], pc[2], ep)
                        if k == g and L.ground[i, j] < g * STOREY - 0.05:
                            # the base course down to the sloping deck, under this bay
                            o.emit("plinth", i, j, k, rot, 0, pc[1], pc[2], min(ep, 1))
                            L.plinths = getattr(L, "plinths", 0) + 1
                        if ctx["door"] or (use == SHOP and outward in ("main", "plaza", "artery") and k == g
                                           and n in L.W and L.q[n] == 4 * k):
                            L.shop_faces.append((i, j, k, rot, use, bool(ctx["door"])))
                        if pn in (LANE, ARTERY):
                            L.faces_on_lanes.append((i, j, rot, k, ep))
                        if k > g:
                            collect["upper_faces"].append((i, j, k, rot, ctx["stack"]))
                            if outward in ("main", "plaza", "artery") and k - g <= 4:
                                L.street_upper.append((i, j, k, rot))
                    # roof edge on this face if this is a top cell
                # corners (outer: both side neighbours empty; inner: both full, the diagonal empty)
                for (sx, sz), crot in CORNER_ROT.items():
                    a = (i + sx, j)
                    b = (i, j + sz)
                    dgl = (i + sx, j + sz)
                    fa = L.inb(*a) and occ[a[0], a[1], k]
                    fb = L.inb(*b) and occ[b[0], b[1], k]
                    fd = L.inb(*dgl) and occ[dgl[0], dgl[1], k]
                    pc = None
                    if not fa and not fb:
                        pc = civ.corner("out", k, ep)
                    elif fa and fb and not fd:
                        pc = civ.corner("in", k, ep)
                    if pc:
                        o.emit(pc[0], i, j, k, crot, 0, pc[1], pc[2], ep)
                # the top: roof field and edges
                if k + 1 >= NL or not occ[i, j, k + 1]:
                    pc = civ.roof_field(i, j, k, ep)
                    o.emit(pc[0], i, j, k + 1, 0, 0, pc[1], pc[2], ep)
                    L.roof_cells.append((i, j, k + 1))
                    collect["roofs"].append((i, j, k + 1))
                    for rot, (di, dj) in FACE.items():
                        n = (i + di, j + dj)
                        if L.inb(*n) and occ[n[0], n[1], k] and (k + 1 < NL and occ[n[0], n[1], k + 1]):
                            continue                                # (the wall goes on up next door)
                        if L.inb(*n) and occ[n[0], n[1], k]:
                            continue                                # (next door's roof at the same height: no edge)
                        pc = civ.roof_edge({"use": use, "epoch": ep, "level": k + 1, "i": i, "j": j, "rot": rot})
                        if pc:
                            o.emit(pc[0], i, j, k + 1, rot, 0, pc[1], pc[2], ep)
                # the underside: a room over air
                if k > g and not occ[i, j, k - 1]:
                    o.emit("soffit", i, j, k, 0, 0, 0, civ.slot("wall", ep, (i, j)), ep)
    # ---------------------------------------------------------------- the open ground
    for i in range(nx):
        for j in range(nz):
            pc = int(L.plan[i, j])
            if pc not in PAVE:
                continue
            g = int(L.gk[i, j])
            if occ[i, j, g] or (i, j) not in L.q:
                continue
            # the graded ground (walk.py): flat paving at q quarters, or the stair up to the higher cell; never on
            # the deck any more (QBITS carry the quarter, the level the storey)
            qv = L.q[(i, j)]
            lv, qf = qv // 4, (qv % 4) << 4
            st = L.stair.get((i, j))
            low = False
            for rot, (di, dj) in FACE.items():
                n = (i + di, j + dj)
                ny = walk_ground(L, n)
                if ny < qv * 0.8 - 0.05:
                    low = True
                # a retaining wall where the neighbour lies more than the skirt below (not where a stair climbs up)
                ns = L.stair.get(n)
                if ny < qv * 0.8 - 0.6 and not (ns and FACE[ns[0]] == (-di, -dj)) and not (L.inb(*n) and occ[n[0], n[1], int(L.gk[n])]):
                    drop = qv * 0.8 - max(ny, -12.8)
                    for t in range(int(math.ceil(drop / 1.6))):
                        qq = qv - 2 * t
                        if qq < 0:
                            break
                        o.emit("plinth", i, j, qq // 4, rot, (qq % 4) << 4, 1, civ.slot("wall", 1, (i, j)), 0)
                if L.inb(*n) and L.plan[n] == WATER:
                    o.emit(getattr(civ, "kerb", "kerb_straight"), i, j, lv, rot, qf, 0, civ.slot("paving"), 0)
            for (sx, sz), crot in CORNER_ROT.items():
                dg = (i + sx, j + sz)
                if L.inb(*dg) and L.plan[dg] == WATER and L.plan[i + sx, j] != WATER and L.plan[i, j + sz] != WATER:
                    o.emit("kerb_post", i, j, lv, crot, qf, 0, civ.slot("paving"), 0)
            if st:
                piece = "step_low_4" if st[1] == 1 else "steps"
                piece = getattr(civ, "steps_map", {}).get(piece, piece)
                o.emit(piece, i, j, lv, st[0], qf, 0, civ.slot("paving"), 0)
            else:
                pv = civ.pave(L, pc, (i, j), PAVE[pc])
                o.emit(pv + ("_skirt" if low and not pv.endswith("_skirt") else ""), i, j, lv, 0, qf, 0,
                       civ.slot("paving"), 0)
            if pc in (LANE, ARTERY):
                cov = covered_at(L, (i, j))
                if not cov:
                    L.open_lanes.append((i, j))
                # the lane's axis: along the walkable neighbours
                axis = 1 if (L.inb(i + 1, j) and L.plan[i + 1, j] in WALKABLE) or \
                    (L.inb(i - 1, j) and L.plan[i - 1, j] in WALKABLE) else 0
                span_rot = 1 if axis == 0 else 0    # a span across the lane
                nb = sum(1 for (di, dj) in FACE.values() if L.inb(i + di, j + dj) and L.plan[i + di, j + dj] in WALKABLE)
                if nb >= 3:
                    collect["junctions"].append((i, j))
                if pc == ARTERY:
                    collect["arteries"].append((i, j))
                if cov:
                    # a tunnel: its ceiling height is the first room over it
                    kk = next(k for k in range(g + 1, NL) if occ[i, j, k])
                    collect["covered"].append((i, j, kk, span_rot))
                    # the tunnel's mouths: an arch where an open lane meets it
                    for rot, (di, dj) in FACE.items():
                        n = (i + di, j + dj)
                        if L.inb(*n) and L.plan[n] in WALKABLE and not covered_at(L, n) and not occ[n[0], n[1], int(L.gk[n])]:
                            # (on the paving, at its height on that edge: a stair's head is 2 quarters up)
                            qa = qv + (st[1] if st and st[0] == rot else 0)
                            o.emit("arch_mouth", i, j, qa // 4, rot, (qa % 4) << 4, 1, civ.slot("wall", 1, (i, j)), 1)
                else:
                    # an open lane between two walls of at least 2 storeys: a place for spans (beams, cables, laundry)
                    hi = g + 1
                    sides = [((i + 1, j), (i - 1, j)), ((i, j + 1), (i, j - 1))][0 if span_rot == 1 else 1]
                    if all(L.inb(*c) and occ[c[0], c[1], hi] for c in sides):
                        collect["lane_spans"].append((i, j, span_rot, hi))
    # ---------------------------------------------------------------- interiors (only where one can go in)
    L.enter = []
    entered = set()
    for n, (i, j, k, rot, use, is_door) in enumerate(L.shop_faces):
        enter = use == SHOP or (is_door and h01(L.seed, "enter", i, j) < civ.params.get("enter_doors", 0.25)) or \
            (L.lot[i, j] >= 0 and L.lots[L.lot[i, j]]["use"] == CIVIC)
        if not enter or (i, j, k) in entered:
            continue                         # (a cell with two shop/door faces: its interior once)
        entered.add((i, j, k))
        L.enter.append((i, j, k))
        o.emit("interior_floor", i, j, k, 0, 0, 0, civ.slot("paving"), 1)
        o.emit("interior_ceiling", i, j, k, 0, 0, h01(L.seed, "ceil", i, j) * 6, civ.slot("trim"), 1)
        # (furniture budgeted: a counter in every shop, shelves in a third, a table in half the houses one enters)
        if use == SHOP:
            o.emit("counter", i, j, k, rot, 0, 0, civ.slot("frame"), 2)     # (the kit's +Z to the shopfront)
            if h01(L.seed, "shelves", i, j) < 0.33:
                o.emit("shelves", i, j, k, rot, 0, 0, civ.slot("frame"), 2)
        elif h01(L.seed, "table", i, j) < 0.5:
            o.emit("table_set", i, j, k, rot, 0, 0, civ.slot("frame"), 2)
        o.emit("lamp", i, j, k, 0, 0, 0, civ.slot("emissive"), 3)
    # ---------------------------------------------------------------- the civ's marks, the newest layer, signs
    civ.marks(L, rng, o.emit)
    ks = getattr(L, "kerb_skip", None)
    if ks:
        # (no kerb across the head of a flight down into the water)
        kp = getattr(civ, "kerb", "kerb_straight")
        o.recs = [r for r in o.recs if not (r[0] == kp and (r[1], r[2], r[4]) in ks)]
    civ.overlay(L, rng, o.emit, collect)
    sign_anchors(L, civ, o)
    L.collect = collect
    return o


def sign_anchors(L, civ, o):
    """SkySigns' anchors: a board over every shop and lit door on a street, blades standing out at shops (the civ's
    sign density), and -- tower civs -- neon blades stacked up the walls over the main streets; [name, x, y, z, yaw]
    in the island frame, +Z out of the face"""
    dens = civ.params.get("sign", 0.5)
    n = 0
    for (i, j, k, rot, use, is_door) in L.shop_faces:
        if use != SHOP and h01(L.seed, "sd", i, j) > dens * 0.8:
            continue
        di, dj = FACE[rot]
        x, y, z = L.centre(i, j, k)
        fx, fz = x + di * (CELL / 2 + 0.25), z + dj * (CELL / 2 + 0.25)
        yaw = math.atan2(di, dj)
        kind = "board" if use == SHOP else "box"
        o.anchors.append(["sign_%s_2.4x0.7_%d" % (kind, n), round(fx, 2), round(y + 2.75, 2), round(fz, 2), round(yaw, 4)])
        n += 1
        if use == SHOP and h01(L.seed, "blade", i, j, rot) < dens * 0.8:
            # a blade at the bay's edge, standing out from the wall
            ox, oz = (dj, -di)
            o.anchors.append(["sign_blade_0.6x2.4_%d" % n, round(fx + ox * 1.3, 2), round(y + 4.4, 2),
                              round(fz + oz * 1.3, 2), round(math.atan2(ox, oz), 4)])
            n += 1
    # over the streets: the neon canyon (tower civs: tall blades up the first storeys; the medina: a few small ones)
    share = civ.params.get("street_blades", 0.35 if civ.lanes == "grid" else 0.08)
    for (i, j, k, rot) in getattr(L, "street_upper", ()):
        if h01(L.seed, "up", i, j, k, rot) >= share:
            continue
        di, dj = FACE[rot]
        x, y, z = L.centre(i, j, k)
        ox, oz = (dj, -di)
        fx, fz = x + di * (CELL / 2 + 0.25) + ox * 1.2, z + dj * (CELL / 2 + 0.25) + oz * 1.2
        size = "0.8x3.6" if share >= 0.2 else "0.5x1.6"
        o.anchors.append(["sign_blade_%s_%d" % (size, n), round(fx, 2), round(y + 1.6, 2), round(fz, 2),
                          round(math.atan2(ox, oz), 4)])
        n += 1
