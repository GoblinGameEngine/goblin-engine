#!/usr/bin/env python3
"""warren_fixture.py -- a stand-in warren for the RUNTIME stream to develop against before the GENERATOR's
(tools/sky/warren/) exists. Writes godot_project/remake/sky/warrens/<id>.bin.gz + <id>.json in the format of
research/sky_islands/warrens/format.md, with placeholder piece ids (SkyWarren draws placeholder boxes for any id
pieces.json doesn't know). Not a city generator: a dense mass on the island's deck, a main cross street, a plaza, lanes.

  python3 tools/sky/warren_fixture.py SKY-100 SKY-071
"""
import gzip
import json
import math
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "godot_project", "remake", "sky", "warrens")
LAYOUT = os.path.join(ROOT, "godot_project", "remake", "sky", "islands.json")
CELL, STOREY, CH = 3.0, 3.2, 8

PIECES = ["wall.plain", "wall.window", "wall.window_pair", "wall.door", "wall.shopfront", "wall.screen",
          "corner.out", "roof.terrace", "roof.parapet", "paving.main", "paving.lane", "paving.plaza",
          "overlay.ac", "overlay.lantern", "overlay.tank"]
P = {p: i for i, p in enumerate(PIECES)}


def inside(poly, x, z):
    c = False
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1 + 1e-12) + x1:
            c = not c
    return c


def build(isl):
    rnd = random.Random(isl["id"])
    f = isl["faces"]
    x0, z0 = f["N"] + 6.0, f["E"] + 6.0
    ni, nj = int((f["S"] - 6.0 - x0) // CELL), int((f["W"] - 6.0 - z0) // CELL)
    poly = isl["outline"]
    water = [w["outline"] for w in isl.get("water", [])]
    mi, mj = ni // 2, nj // 2
    h = {}
    for i in range(ni):
        for j in range(nj):
            x, z = x0 + CELL * i + 1.5, z0 + CELL * j + 1.5
            if not inside(poly, x, z) or any(inside(w, x, z) for w in water):
                continue
            # keep the edge band (fence, promenade) open, a main cross street (3 cells), a plaza, lanes every ~6
            edge = min(abs(x - f["N"]), abs(x - f["S"]), abs(z - f["E"]), abs(z - f["W"]))
            street = abs(i - mi) <= 1 or abs(j - mj) <= 1
            plaza = abs(i - mi) <= 4 and abs(j - mj) <= 4
            lane = (i % 7 == 3) or (j % 6 == 2 and rnd.random() < 0.8)
            if edge < 9.0:
                h[(i, j)] = -1                  # open ground
            elif plaza:
                h[(i, j)] = -3
            elif street:
                h[(i, j)] = -2
            elif lane:
                h[(i, j)] = -1
            else:
                dist = math.hypot(i - mi, j - mj) / max(ni, nj)
                h[(i, j)] = max(1, int(rnd.triangular(1, 7, 5 - 4 * dist)))
    recs = {}

    def put(i, j, k, piece, r, pal=0, ep=0):
        ck = (i // CH, j // CH)
        recs.setdefault(ck, []).append((P[piece], i % CH, j % CH, k, r & 3, (pal & 15) | ((ep & 15) << 4)))

    anchors, lights = [], []
    for (i, j), v in h.items():
        if v < 0:
            put(i, j, 0, {-1: "paving.lane", -2: "paving.main", -3: "paving.plaza"}[v], 0)
            continue
        pal = (i * 7 + j * 3) % 4
        for k in range(v):
            ep = min(5, k)
            for r, (di, dj) in enumerate([(0, -1), (-1, 0), (0, 1), (1, 0)]):
                nv = h.get((i + di, j + dj), -9)
                if nv > k:
                    continue                                  # (a neighbour's room: no wall here)
                if k == 0 and nv in (-2, -3):
                    piece = "wall.shopfront" if rnd.random() < 0.6 else "wall.door"
                    if piece == "wall.shopfront" and rnd.random() < 0.5:
                        a = math.pi * 0.5 * r
                        cx, cz = x0 + CELL * i + 1.5, z0 + CELL * j + 1.5
                        ox, oz = -math.sin(a) * 1.65, -math.cos(a) * 1.65
                        anchors.append([f"sign_{rnd.choice(['neon', 'lightbox', 'painted', 'dotmatrix'])}_2.4x0.8_{len(anchors)}",
                                        round(cx + ox, 2), 3.0, round(cz + oz, 2), round(a + math.pi, 3)])
                elif k == 0:
                    piece = "wall.door" if rnd.random() < 0.15 else "wall.plain"
                else:
                    piece = rnd.choice(["wall.window", "wall.window", "wall.window_pair", "wall.screen", "wall.plain"])
                put(i, j, k, piece, r, pal, ep)
            if (i + j) % 2 == 0 and rnd.random() < 0.3:
                put(i, j, k, "overlay.ac", rnd.randrange(4), pal, 5)
        put(i, j, v, "roof.terrace", 0, pal)
        for r, (di, dj) in enumerate([(0, -1), (-1, 0), (0, 1), (1, 0)]):
            if h.get((i + di, j + dj), -9) < v:
                put(i, j, v, "roof.parapet", r, pal)
        if rnd.random() < 0.08:
            put(i, j, v, "overlay.tank", 0, pal, 5)
        if rnd.random() < 0.05:
            put(i, j, v, "overlay.lantern", 0, pal, 4)
            lights.append([round(x0 + CELL * i + 1.5, 2), round(STOREY * v + 1.5, 2), round(z0 + CELL * j + 1.5, 2), 1.0])
    # the walk graph: open cells at level 0, 4-connected
    nodes, idx, edges = [], {}, []
    for (i, j), v in h.items():
        if v < 0:
            idx[(i, j)] = len(nodes)
            nodes.append([round(x0 + CELL * i + 1.5, 2), 0.0, round(z0 + CELL * j + 1.5, 2)])
    for (i, j), a in idx.items():
        for di, dj in ((1, 0), (0, 1)):
            b = idx.get((i + di, j + dj))
            if b is not None:
                edges.append([a, b, 3.0])
    travel = [round(x0 + CELL * mi + 1.5, 2), 0.0, round(z0 + CELL * mj + 1.5, 2), 0.0]
    head = {"version": 1, "id": isl["id"], "civ": "fixture", "origin": [round(x0, 3), round(z0, 3)],
            "size": [ni, nj, 8], "chunk": CH, "pieces": PIECES,
            "palettes": [{"wall": c, "trim": "#e8e0d0", "frame": "#5a3a22", "roof": "#b8a890", "metal": "#6a6e72",
                          "glass": "#9fb4c0", "screen": "#6b4a2e", "paving": "#b8ab96", "emissive": "#ffd090"}
                         for c in ("#d9c3a0", "#c98f6a", "#e6dccb", "#b77a5a")]}
    hb = json.dumps(head).encode()
    out = bytearray(b"WRN1") + struct.pack("<I", len(hb)) + hb + struct.pack("<I", len(recs))
    n = 0
    for (ci, cj), lst in sorted(recs.items()):
        out += struct.pack("<BBI", ci, cj, len(lst))
        for r in lst:
            out += struct.pack("<HBBBBB", *r)
            n += 1
    out += struct.pack("<I", 0)
    os.makedirs(OUT, exist_ok=True)
    with gzip.open(os.path.join(OUT, isl["id"] + ".bin.gz"), "wb") as fh:
        fh.write(bytes(out))
    side = {"id": isl["id"], "civ": "fixture", "travel": travel, "anchors": anchors,
            "walk": {"nodes": nodes, "edges": edges}, "units": [], "doors": [], "lights": lights, "species": []}
    with open(os.path.join(OUT, isl["id"] + ".json"), "w") as fh:
        json.dump(side, fh)
    print(f"{isl['id']}: {ni}x{nj} cells, {len(recs)} chunks, {n} placements, {len(anchors)} signs, {len(nodes)} walk nodes")


def main(ids):
    lay = json.load(open(LAYOUT))
    for isl in lay["islands"]:
        if isl["id"] in ids:
            build(isl)


if __name__ == "__main__":
    main(sys.argv[1:] or ["SKY-100", "SKY-071"])
