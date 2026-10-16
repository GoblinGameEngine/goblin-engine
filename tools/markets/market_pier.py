#!/usr/bin/env python3
"""
market_pier.py -- a floating pier market's plan in its site frame (the coordinator, 2026-10-16: Victory Bay's Regatta
Swap has no free land on its island, so it floats: "a moored pier deck off its shore with stall rows, a small lot or
bike racks on the shore end, and a mooring mast at the pier head").

Site frame: u along the shore, v out over the water; v = 0 is the shoreline (the gangway's landing on the island).
  landing    v -4 .. 0     on the shore: bike racks, the pylon
  gangway    v 0 .. 12     fm_pier_ramp, from the landing down to the deck
  deck       v 12 .. 12+L  26 m wide: four pitch columns facing two 6 m aisles (stalls back-to-back down the middle)
  head       30 x 30 m     the mooring mast at its middle, bollards round its edge (the islands' hawsers), the food
  raft       30 x 30 m     a tent float beside the head (the islanders' fair tents)
Everything over the water floats at the deck height (the lake's level + DECK_FREEBOARD); the kit's deck pieces
(fm_pier_deck_6, rails, ramp, bollards) are tiled over the `decks` rectangles.
"""
import math

import markets_spec as MS

RAMP_L = 12.0
DECK_W = 26.0
HEAD = 30.0
PITCH = 3.0
DECK_FREEBOARD = 0.55        # the deck's top over the water
COLS = [(-10.5, math.pi / 2), (-1.5, -math.pi / 2), (1.5, math.pi / 2), (10.5, -math.pi / 2)]   # (u, the way it faces)


def rect(u0, u1, v0, v1):
    return [[round(u0, 2), round(v0, 2)], [round(u1, 2), round(v0, 2)], [round(u1, 2), round(v1, 2)], [round(u0, 2), round(v1, 2)]]


def pier_layout(m, raft_side=1):
    n = m["stalls"]
    k = m["kinds"]
    slots_needed = k["shed"] + k["open"] + 2 * k["open_double"]
    rows = int(math.ceil(slots_needed / float(len(COLS))))
    d0 = RAMP_L
    L = rows * PITCH + 6.0
    d1 = d0 + L
    stalls = []
    # the slots column by column, nearest the gangway first: the permanent stalls (kind 0, no shed: canopied pitches
    # on the deck), then the doubles (two slots of a column), then the open pitches
    grid = [(ci, r) for r in range(rows) for ci in range(len(COLS))]
    used = set()

    def put(ci, r, kind, nslots):
        u, yaw = COLS[ci]
        v = d0 + 3.0 + PITCH * (r + 0.5) + (PITCH * 0.5 if nslots == 2 else 0.0)
        stalls.append([round(u, 2), round(v, 2), round(yaw, 4), kind, ci, -1])
        for j in range(nslots):
            used.add((ci, r + j))

    for kind, cnt in ((0, k["shed"]), (2, k["open_double"]), (1, k["open"])):
        placed = 0
        for ci, r in grid:
            if placed >= cnt:
                break
            if (ci, r) in used:
                continue
            if kind == 2:
                if r + 1 >= rows or (ci, r + 1) in used:
                    continue
                put(ci, r, 2, 2)
            else:
                put(ci, r, kind, 1)
            placed += 1
    # food: pitches at the head's deck end, facing the deck
    h0, h1 = d1, d1 + HEAD
    for j in range(k["food"]):
        u = (-6.0 if j % 2 == 0 else 6.0) * (1 + j // 2)
        stalls.append([round(u, 2), round(h0 + 3.0, 2), round(math.pi, 4), 3, -1, -1])
    # aisles (6 m, between the columns), the deck's edge walk, the cross walk at each end
    lanes = [[-9.0, d0, -3.0, d1, 6.0], [3.0, d0, 9.0, d1, 6.0], [-13.0, d0, 13.0, d0 + 3.0, 3.0], [-13.0, d1 - 3.0, 13.0, d1, 3.0]]
    fest = []
    for ua, ub in ((-9.0, -3.0), (3.0, 9.0)):
        v = d0 + 1.0
        flip = 0
        while v + 6.0 <= d1 - 1.0:
            fest.append([ua + 0.4 if flip == 0 else ub - 0.4, round(v, 2), ub - 0.4 if flip == 0 else ua + 0.4, round(v + 6.0, 2), 4.2, 4])
            v += 6.0
            flip ^= 1
    # the head: the mast at its middle, bollards round its edge, the ground stations (gangway plinths) at its far side
    hc = (0.0, (h0 + h1) / 2)
    mo = MS.MOORING[m["tier"]]
    nb = max(8, mo["deadmen"])
    bollards = []
    for j in range(nb):
        a = 2 * math.pi * j / nb
        bollards.append([round(hc[0] + 13.5 * math.cos(a), 2), round(hc[1] + 13.5 * math.sin(a), 2)])
    masts = [[hc[0], round(hc[1], 2)]]
    stations = [[round(-9.0 + 9.0 * j, 2), round(h1 - 3.0, 2), round(math.pi, 4)] for j in range(mo["ground_islands"])]
    # tents: round the mast on the head, and a 4 x 4 grid on the raft
    ru0, ru1 = (HEAD / 2, HEAD / 2 + HEAD) if raft_side > 0 else (-HEAD / 2 - HEAD, -HEAD / 2)
    tents = []
    for j in range(8):
        a = 2 * math.pi * (j + 0.5) / 8
        tents.append([round(hc[0] + 8.0 * math.cos(a), 2), round(hc[1] + 8.0 * math.sin(a), 2), round(a, 4), 6, 2])
    for iu in range(4):
        for iv in range(4):
            tents.append([round(ru0 + 4.5 + 7.0 * iu, 2), round(h0 + 4.5 + 7.0 * iv, 2), 0.0, 6, 1])
    decks = [[-DECK_W / 2, d0, DECK_W / 2, d1], [-HEAD / 2, h0, HEAD / 2, h1], [ru0, h0, ru1, h1]]
    bu0, bu1 = min(-HEAD / 2, ru0), max(HEAD / 2, ru1)
    entrances = [[0.0, -2.0, 0.0, "access"], [0.0, d0 + 1.0, 0.0, "walk"], [0.0, d0 + 1.0, 0.0, "vendor"]]
    kk = {"shed": 0, "open": 0, "open_double": 0, "food": 0}
    for st in stalls:
        kk[["shed", "open", "open_double", "food"][st[3]]] += 1
    return {"bbox": [round(bu0, 2), round(bu1, 2), -4.0, round(h1, 2)], "core": [-DECK_W / 2, DECK_W / 2, 0.0, round(d1, 2)],
            "field_side": raft_side, "variant": ["pier", 1.0],
            "lot": {"poly": rect(-6.0, 6.0, -4.0, 0.0), "rows": [], "per_row": 0, "spaces": 0, "accessible": 0, "v0": -4.0, "v1": 0.0, "w": 12.0},
            "floor": rect(-DECK_W / 2, DECK_W / 2, d0, d1), "apron": [rect(ru0, ru1, h0, h1)], "mooring": rect(-HEAD / 2, HEAD / 2, h0, h1),
            "stalls": stalls, "sheds": [], "tent_slots": tents, "poles": [], "festoons": fest, "deadmen": bollards, "masts": masts,
            "stations": stations, "entrances": entrances, "pylon": [6.0, -2.0, round(math.pi, 4)], "arch": [0.0, d0 + 0.6, round(math.pi, 4), 8.0],
            "bus": [-8.0, -3.0, 0.0], "lanes": lanes,
            "pier": {"decks": decks, "ramp": [0.0, RAMP_L / 2, 0.0, RAMP_L], "landing": [-6.0, -4.0, 6.0, 0.0],
                     "bike_racks": [[-4.0, -2.0, 0.0], [4.0, -2.0, 0.0]], "freeboard": DECK_FREEBOARD},
            "stats": {"stalls": len(stalls), "kinds": kk, "spaces": 0, "floor_m2": round(DECK_W * L), "parking_m2": 0,
                      "apron_m2": round(HEAD * HEAD), "mooring_m2": round(HEAD * HEAD), "tent_slots": len(tents), "core_w": DECK_W,
                      "bike_racks": 2}}


if __name__ == "__main__":
    for m in MS.MARKETS:
        if m.get("pier"):
            p = pier_layout(m)
            print(m["id"], p["stats"], p["bbox"])
