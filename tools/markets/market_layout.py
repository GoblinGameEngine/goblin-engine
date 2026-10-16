#!/usr/bin/env python3
"""
market_layout.py -- one flea market's site plan in its own frame (research/flea_markets/00_plan.md §1.2-1.4, §2.1).

Site frame: u along the frontage, v away from the road (v = 0 on the site's front edge), metres. The core (lot and
floor) is centred on u = 0; the mooring field lies off one u end (`field_side` -1 / +1: the leeward end), the apron
off the other end and along the back.

    plan = layout(market_spec, field_side=-1, stalls=None)
      -> {"bbox": [u0, u1, v0, v1], "core": [...], "lot": {...}, "floor": poly, "apron": [poly...], "mooring": poly,
          "stalls": [[u, v, yaw, kind, row, shed]], "sheds": [...], "tent_slots": [...], "poles": [...],
          "festoons": [...], "deadmen": [...], "masts": [...], "stations": [...], "entrances": [...], "pylon": [...],
          "arch": [...], "bus": [...], "lanes": [[u0, v0, u1, v1, width]], "stats": {...}}

Yaw convention for stalls (and every piece): the direction the stall FACES (its customers' side), as an angle in the
site frame from +v toward +u: yaw 0 faces +v, pi faces -v. (The kit's pieces face +Z; the runtime maps site +v to the
piece's +Z at yaw 0.)
"""
import math

STRIP = 3.0                 # landscape strip along the front
STALL_W, STALL_D, AISLE = 2.75, 5.5, 7.3     # parking (tools/parking_lots.py)
BAY = 2 * STALL_D + AISLE   # 18.3 m: stall + aisle + stall
ISLAND = 2.0                # landscape island between bays (the lot poles stand in it)
END_AISLE = 7.3             # the drive round the bays' ends
FRONT_DRIVE = 7.3           # the lot's drive along its front (the entrance meets it)
FIRE = 6.0                  # fire lane / drop-off between the lot and the floor, round the floor, the vendor lane
PITCH = 3.0
ROW_AISLE = 6.0             # open aisles (fire access)
SHED_W = 12.0               # eave 1 + bay 3 + covered aisle 4 + bay 3 + eave 1
SHED_MAX = 120.0
CROSS_EVERY = 54.0          # a 6 m cross lane after every 18 pitches
FOOD_W, FOOD_D = 4.0, 8.0
COURT = 8.0                 # the food court in front of the trucks
APRON = 35.0
FIELD_GAP = 8.0
POLE_STEP = 24.0            # ~2.5 x the 9 m mounting height (IES RP-20)
FEST_H = 4.2


def rect(u0, u1, v0, v1):
    return [[round(u0, 2), round(v0, 2)], [round(u1, 2), round(v0, 2)], [round(u1, 2), round(v1, 2)], [round(u0, 2), round(v1, 2)]]


def _lot(spaces, Wc, tier):
    per_row = max(4, int((Wc - 2 * END_AISLE) / STALL_W))
    nb = max(1, int(math.ceil(spaces / (2.0 * per_row))))
    rows, poles = [], []
    v = STRIP + FRONT_DRIVE
    u0, u1 = -Wc / 2 + END_AISLE, -Wc / 2 + END_AISLE + per_row * STALL_W
    for b in range(nb):
        rows.append([round(u0, 2), round(u1, 2), round(v, 2), STALL_D, -1])
        rows.append([round(u0, 2), round(u1, 2), round(v + STALL_D + AISLE, 2), STALL_D, 1])
        v += BAY
        if b < nb - 1:
            v += ISLAND
    v_end = v + 2.0
    # poles: the front strip, every island between bays, the back edge; ~24 m along u
    nu = max(2, int(round((Wc - 6.0) / POLE_STEP)) + 1)
    us = [-Wc / 2 + 3.0 + k * (Wc - 6.0) / (nu - 1) for k in range(nu)]
    vs = [(STRIP, 2)]
    vv = STRIP + FRONT_DRIVE
    for b in range(nb - 1):
        vv += BAY
        vs.append((vv + ISLAND / 2, 4 if tier == "city" else 2))
        vv += ISLAND
    vs.append((v_end - 0.5, 2))
    for v_, heads in vs:
        for u_ in us:
            poles.append([round(u_, 2), round(v_, 2), heads])
    spaces_got = per_row * 2 * nb
    return {"rows": rows, "per_row": per_row, "bays": nb, "v0": STRIP, "v1": round(v_end, 2), "poles": poles,
            "spaces": spaces_got, "accessible": max(1, int(math.ceil(spaces_got / 25.0)))}


def _floor(kinds, Wc, v0):
    """the market floor from v0: food court, sheds, open rows, vendor lane; returns stalls, sheds, lanes, festoons"""
    Wu = Wc - 2 * FIRE                       # inside the side fire lanes
    ua, ub = -Wu / 2, Wu / 2
    stalls, sheds, lanes, fest = [], [], [], []
    v = v0
    # the food row: trucks either side of the central walk (10 m), facing +v onto the court
    nf = kinds["food"]
    per_side = int(math.ceil(nf / 2.0))
    k = 0
    for side in (-1, 1):
        for i in range(per_side):
            if k >= nf:
                break
            uc = side * (5.0 + FOOD_W / 2 + i * (FOOD_W + 1.0))
            if abs(uc) + FOOD_W / 2 > Wu / 2:
                uc = side * (Wu / 2 - FOOD_W / 2 - (abs(uc) - Wu / 2))
            stalls.append([round(uc, 2), round(v + FOOD_D / 2, 2), 0.0, 3, 0, -1])
            k += 1
    v += FOOD_D
    lanes.append([ua, v, ub, v + COURT, COURT])
    v += COURT
    # the covered sheds (every permanent bay): 3 m slices, a bay either side of the covered aisle
    ns = kinds["shed"]
    slices = int(math.ceil(ns / 2.0))
    per_shed = max(4, int(min(SHED_MAX, Wu) / PITCH))
    n_shed = int(math.ceil(slices / float(per_shed)))
    left = ns
    row = 1
    for si in range(n_shed):
        n_sl = min(per_shed, int(math.ceil(left / 2.0)))
        L = n_sl * PITCH
        s0 = -L / 2
        sid = len(sheds)
        sheds.append({"id": si, "u0": round(s0, 2), "u1": round(s0 + L, 2), "v0": round(v, 2), "v1": round(v + SHED_W, 2),
                      "bays": 0})
        for j in range(n_sl):
            uc = s0 + PITCH * (j + 0.5)
            for side in (0, 1):
                if left <= 0:
                    break
                # side 0: the bay on the front side of the covered aisle, facing +v into it; side 1 faces -v
                vc = v + 1.0 + PITCH / 2 if side == 0 else v + SHED_W - 1.0 - PITCH / 2
                stalls.append([round(uc, 2), round(vc, 2), 0.0 if side == 0 else round(math.pi, 4), 0, row + side, sid])
                sheds[-1]["bays"] += 1
                left -= 1
        row += 2
        v += SHED_W
        lanes.append([ua, v, ub, v + ROW_AISLE, ROW_AISLE])
        v += ROW_AISLE
    # open rows: back-to-back pitch pairs between 6 m aisles; doubles at the row ends; a cross lane every 54 m
    n_open, n_dbl = kinds["open"], kinds["open_double"]
    runs = []                                 # the u spans of pitches along a row, between cross lanes
    a = ua
    while a + PITCH <= ub + 1e-6:
        b = min(ub, a + CROSS_EVERY)
        n_p = int((b - a + 1e-6) / PITCH)
        if n_p > 0:
            runs.append((a, n_p))
        a = b + FIRE
    per_row = sum(n for _, n in runs)
    while n_open > 0 or n_dbl > 0:
        for side, vc, yaw in ((0, v + PITCH / 2, math.pi), (1, v + PITCH + PITCH / 2, 0.0)):
            # side 0 faces -v (the aisle in front of it), side 1 faces +v (the next aisle)
            slots = []
            for a_, n_p in runs:
                for j in range(n_p):
                    slots.append(a_ + PITCH * (j + 0.5))
            # doubles take two pitches at each end of the row
            ends = []
            if n_dbl > 0 and len(slots) >= 4:
                for e in (0, 1):
                    if n_dbl <= 0:
                        break
                    if e == 0:
                        pair = (slots.pop(0), slots.pop(0))
                    else:
                        pair = (slots.pop(), slots.pop())
                    ends.append(((pair[0] + pair[1]) / 2, 2))
                    n_dbl -= 1
            for uc, kd in ends:
                stalls.append([round(uc, 2), round(vc, 2), round(yaw, 4), kd, row + side, -1])
            i = 0
            while i < len(slots):
                if n_open > 0:
                    stalls.append([round(slots[i], 2), round(vc, 2), round(yaw, 4), 1, row + side, -1])
                    n_open -= 1
                    i += 1
                elif n_dbl > 0 and i + 1 < len(slots) and abs(slots[i + 1] - slots[i] - PITCH) < 0.01:
                    # (the open pitches are used up: the doubles left take two side by side)
                    stalls.append([round((slots[i] + slots[i + 1]) / 2, 2), round(vc, 2), round(yaw, 4), 2, row + side, -1])
                    n_dbl -= 1
                    i += 2
                else:
                    i += 1
        row += 2
        v += 2 * PITCH
        lanes.append([ua, v, ub, v + ROW_AISLE, ROW_AISLE])
        # festoons across the aisle, criss-cross every 6 m (00 §1.4: warm, at 4.2 m)
        u_ = ua + 1.0
        flip = 0
        while u_ + 6.0 <= ub - 1.0:
            va_, vb_ = (v + 0.4, v + ROW_AISLE - 0.4) if flip == 0 else (v + ROW_AISLE - 0.4, v + 0.4)
            fest.append([round(u_, 2), round(va_, 2), round(u_ + 6.0, 2), round(vb_, 2), FEST_H, 4])
            u_ += 6.0
            flip ^= 1
        v += ROW_AISLE
    # the last aisle is the vendor lane (6 m); the side fire lanes run the floor's depth
    v_end = v
    lanes.append([-Wc / 2, v0, -Wc / 2 + FIRE, v_end, FIRE])
    lanes.append([Wc / 2 - FIRE, v0, Wc / 2, v_end, FIRE])
    for a_, n_p in runs[:-1]:
        cu = a_ + n_p * PITCH + FIRE / 2
        lanes.append([cu - FIRE / 2, v0 + FOOD_D + COURT, cu + FIRE / 2, v_end, FIRE])
    return stalls, sheds, lanes, fest, v_end, per_row


VARIANTS = [("side", 1.0), ("back", 1.0), ("side", 0.75), ("back", 0.75), ("back", 1.3), ("side", 1.3)]


def layout(m, field_side=-1, stalls=None, variant=("side", 1.0)):
    """m: a markets_spec.MARKETS entry. stalls: an override of the stall count (the siting steps it down).
    variant: (where the mooring field goes -- "side": off the leeward end, the apron off the other end and along the
    back; "back": behind the core at its leeward end, the apron down the other side --, the core's width scale)."""
    import markets_spec as MS
    n = stalls or m["stalls"]
    kinds = MS.kinds_of(n) if stalls else m["kinds"]
    tier = m["tier"]
    spaces = int(math.ceil(n * MS.SPACES_PER_STALL))
    # the core's width: the floor's sheds want <= 120 m runs; the lot's area wants ~ a square-ish whole
    area = n * 23.0 + spaces * 32.0
    Wc = max(60.0, min(240.0, round(math.sqrt(area) * 1.15 * variant[1] / 6.0) * 6.0))
    lot = _lot(spaces, Wc, tier)
    f0 = lot["v1"] + FIRE
    st, sheds, lanes, fest, f1, per_row = _floor(kinds, Wc, f0)
    lanes.append([-Wc / 2, lot["v1"], Wc / 2, f0, FIRE])            # the fire lane and drop-off
    core_v1 = f1
    # the mooring field (leeward end) and the apron (the other end, and the back)
    fw, fd = MS.MOORING[tier]["field"]
    if variant[0] == "back" and fw > Wc:
        return None                                   # (the field is wider than the core: no "back" layout)
    if field_side < 0:
        au0, au1 = Wc / 2, Wc / 2 + APRON
    else:
        au0, au1 = -Wc / 2 - APRON, -Wc / 2
    if variant[0] == "side":
        if field_side < 0:
            fu0, fu1 = -Wc / 2 - FIELD_GAP - fw, -Wc / 2 - FIELD_GAP
        else:
            fu0, fu1 = Wc / 2 + FIELD_GAP, Wc / 2 + FIELD_GAP + fw
        fv0, fv1 = STRIP, STRIP + fd
        v_back = max(core_v1, fv1)
        apron_side = rect(au0, au1, STRIP, v_back)
        bu0, bu1 = min(fu0, au0, -Wc / 2), max(fu1, au1, Wc / 2)
        apron_back = rect(bu0, bu1, v_back, v_back + APRON)
        v_end = v_back + APRON
    else:
        # behind the core, flush with its leeward end (a deep, narrow site)
        if field_side < 0:
            fu0, fu1 = -Wc / 2, -Wc / 2 + fw
        else:
            fu0, fu1 = Wc / 2 - fw, Wc / 2
        fv0, fv1 = core_v1 + FIELD_GAP, core_v1 + FIELD_GAP + fd
        v_back = fv1
        bu0, bu1 = min(fu0, au0, -Wc / 2), max(fu1, au1, Wc / 2)
        apron_side = rect(au0, au1, STRIP, v_back)
        # the back strip: what the field leaves of the core's width behind it
        apron_back = rect(fu1, Wc / 2, core_v1, v_back) if field_side < 0 else rect(-Wc / 2, fu0, core_v1, v_back)
        v_end = v_back
    field = rect(fu0, fu1, fv0, fv1)
    # what's on the mooring ground (00 §1.2, §5.3): anchor blocks in a ring, masts, the ground stations' plinths
    mo = MS.MOORING[tier]
    fc = ((fu0 + fu1) / 2, (fv0 + fv1) / 2)
    nd = mo["deadmen"]
    deadmen = [[round(fc[0] + 0.4 * fw * math.cos(2 * math.pi * k / nd), 2), round(fc[1] + 0.4 * fd * math.sin(2 * math.pi * k / nd), 2)]
               for k in range(nd)]
    masts = [[round(fc[0] + (k - (mo["masts"] - 1) / 2) * 0.3 * fw, 2), round(fc[1], 2)] for k in range(mo["masts"])]
    stations = []
    for k in range(mo["ground_islands"]):
        # plinths along the field's outer edge and back, facing the field's middle
        t_ = (k + 0.5) / mo["ground_islands"]
        uu = fu0 + 6.0 + t_ * (fw - 12.0) if True else 0
        vv = fv1 - 6.0
        stations.append([round(uu, 2), round(vv, 2), round(math.pi, 4)])
    # tent slots (00 §5.6): ring 0 the apron's first 10 m along the lot, ring 1 the rest of the apron, ring 2 the
    # mooring field's margins
    slots = []
    sgn = 1 if field_side < 0 else -1               # the apron's side: +u when the field is on -u
    edge = Wc / 2 * sgn
    v_ = STRIP + 4.0
    while v_ + 3.0 <= v_back:
        slots.append([round(edge + sgn * 4.0, 2), round(v_, 2), round(-sgn * math.pi / 2, 4), 6, 0])
        v_ += 7.0
    for col in (14.0, 25.0):
        v_ = STRIP + 6.0
        while v_ + 4.5 <= v_back:
            slots.append([round(edge + sgn * (col + 1.0), 2), round(v_, 2), round(-sgn * math.pi / 2, 4), 9, 1])
            v_ += 10.0
    if variant[0] == "side":
        for row_v in (v_back + 6.0, v_back + 17.0, v_back + 28.0):
            u_ = bu0 + 6.0
            while u_ + 4.5 <= bu1:
                slots.append([round(u_, 2), round(row_v, 2), round(math.pi, 4), 9 if row_v > v_back + 10 else 6, 1])
                u_ += 10.0
    else:
        b_ = apron_back
        u_ = min(b_[0][0], b_[1][0]) + 6.0
        while u_ + 4.5 <= max(b_[0][0], b_[1][0]):
            v2 = core_v1 + 8.0
            while v2 + 4.5 <= v_back:
                slots.append([round(u_, 2), round(v2, 2), round(math.pi, 4), 9, 1])
                v2 += 11.0
            u_ += 11.0
    u_ = fu0 + 5.0
    while u_ + 3.0 <= fu1:
        slots.append([round(u_, 2), round(fv0 + 4.0, 2), 0.0, 6, 2])
        u_ += 8.0
    # entrances: cars at u = +-Wc/4 off the frontage road; walkers at the middle; vendors by the end aisle
    ent_u = Wc / 4.0
    entrances = [[0.0, -1.0, 0.0, "access"], [round(ent_u, 2), STRIP / 2, 0.0, "car"], [round(-ent_u, 2), STRIP / 2, 0.0, "car_exit"],
                 [0.0, round(f0 - FIRE / 2, 2), 0.0, "walk"],
                 [round(Wc / 2 - FIRE / 2, 2), round(f0, 2), 0.0, "vendor"]]
    pylon = [round(-ent_u - 8.0, 2), STRIP / 2, round(math.pi, 4)]
    arch = [0.0, round(f0 - 0.5, 2), round(math.pi, 4), 12.0 if tier == "city" else (10.0 if tier == "town" else 8.0)]
    bus = [round(ent_u + 18.0, 2), -4.0, 0.0]
    floor = rect(-Wc / 2, Wc / 2, lot["v1"], core_v1)
    lot_poly = rect(-Wc / 2, Wc / 2, STRIP, lot["v1"])
    bbox = [round(bu0, 2), round(bu1, 2), 0.0, round(v_end, 2)]
    k = {"shed": 0, "open": 0, "open_double": 0, "food": 0}
    for s in st:
        k[["shed", "open", "open_double", "food"][s[3]]] += 1
    stats = {"stalls": len(st), "kinds": k, "spaces": lot["spaces"], "floor_m2": round(Wc * (core_v1 - lot["v1"])),
             "parking_m2": round(Wc * (lot["v1"] - STRIP)),
             "apron_m2": round(sum(abs(a[1][0] - a[0][0]) * abs(a[2][1] - a[1][1]) for a in (apron_side, apron_back))),
             "mooring_m2": round(fw * fd), "tent_slots": len(slots), "core_w": Wc}
    return {"bbox": bbox, "core": [-Wc / 2, Wc / 2, 0.0, core_v1], "field_side": field_side, "variant": list(variant),
            "lot": {"poly": lot_poly, "rows": lot["rows"], "per_row": lot["per_row"], "spaces": lot["spaces"],
                    "accessible": lot["accessible"], "v0": lot["v0"], "v1": lot["v1"], "w": Wc},
            "floor": floor, "apron": [apron_side, apron_back], "mooring": field, "stalls": st, "sheds": sheds,
            "tent_slots": slots, "poles": lot["poles"], "festoons": fest, "deadmen": deadmen, "masts": masts,
            "stations": stations, "entrances": entrances, "pylon": pylon, "arch": arch, "bus": bus, "lanes": lanes,
            "stats": stats}


if __name__ == "__main__":
    import json
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import markets_spec as MS
    for m in MS.MARKETS:
        p = layout(m, variant=tuple(json.loads(sys.argv[1])) if len(sys.argv) > 1 else ("side", 1.0))
        if p is None:
            print("%-7s (no layout)" % m["id"])
            continue
        b = p["bbox"]
        print("%-7s %4d stalls %s  site %.0f x %.0f m  spaces %d  tents %d  sheds %d" % (
            m["id"], p["stats"]["stalls"], p["stats"]["kinds"], b[1] - b[0], b[3] - b[2], p["stats"]["spaces"],
            p["stats"]["tent_slots"], len(p["sheds"])))
