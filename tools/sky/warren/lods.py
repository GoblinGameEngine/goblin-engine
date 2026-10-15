#!/usr/bin/env python3
"""lods.py -- r4 step 6: an island's distant models (godot_project/remake/sky/islands/<id>.lod1.glb, .lod2.glb, written
by tools/sky/make_islands.py) get their city from the warren's lattice instead of the round-2 buildings.

Each glb keeps its deck and rock; its "buildings" node is replaced by "warren_hull": the lattice's columns as boxes,
each to its top room's ceiling, coloured by the house's kit palette variant (pieces.json palettes[civ][variant].wall),
merged into rectangles.  lod1 at 2 x 2 cells (6 m), lod2 at 5 x 5 (15 m) in
steps of 3 storeys.  The runtime (SkyIsland) draws
"warren_hull" with lod_vc's massing material: a lit window grid at night.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/lods.py [SKY-100 SKY-071 ...]     (default: every island with a warren file)
"""
import gzip
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.dirname(HERE))
import glb  # noqa: E402  (tools/sky/glb.py)

GP = os.path.join(ROOT, "godot_project")
WR = os.path.join(GP, "remake", "sky", "warrens")
ISL = os.path.join(GP, "remake", "sky", "islands")
STOREY = 3.2


# ------------------------------------------------------------------ glb in (tools/sky/glb.py's own output)
def read_glb(path):
    raw = open(path, "rb").read()
    jl, _ = struct.unpack_from("<II", raw, 12)
    js = json.loads(raw[20:20 + jl])
    bl, _ = struct.unpack_from("<II", raw, 20 + jl)
    bin_ = raw[28 + jl:28 + jl + bl]
    types = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}
    dt = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}

    def acc(i):
        a = js["accessors"][i]
        v = js["bufferViews"][a["bufferView"]]
        n = a["count"] * types[a["type"]]
        arr = np.frombuffer(bin_, dt[a["componentType"]], n, v.get("byteOffset", 0))
        arr = arr.reshape(a["count"], types[a["type"]]) if types[a["type"]] > 1 else arr
        if a.get("normalized"):
            arr = arr.astype(np.float32) / 255.0
        return arr

    nodes = []
    for nd in js["nodes"]:
        pr = js["meshes"][nd["mesh"]]["primitives"][0]
        at = pr["attributes"]
        nodes.append({"name": nd["name"], "positions": acc(at["POSITION"]), "normals": acc(at["NORMAL"]),
                      "colors": acc(at["COLOR_0"]) if "COLOR_0" in at else None,
                      "indices": acc(pr["indices"]).astype(np.uint32),
                      "material": js["materials"][pr["material"]]["name"]})
    return nodes


# ------------------------------------------------------------------ the warren
def read_warren(iid):
    side = json.load(open(os.path.join(WR, iid + ".json")))
    raw = gzip.open(os.path.join(WR, iid + ".bin.gz")).read()
    o = [4]

    def rd(fmt):
        v = struct.unpack_from(fmt, raw, o[0])
        o[0] += struct.calcsize(fmt)
        return v

    def rs():
        (n,) = rd("<H")
        s = raw[o[0]:o[0] + n].decode()
        o[0] += n
        return s
    (ver,) = rd("<H")
    assert ver >= 2, "%s: format v%d (v2 needed)" % (iid, ver)
    civ = rs()
    x0, z0, cell, _st = rd("<ffff")
    nx, nz, _lv = rd("<HHB")
    (npal,) = rd("<B")
    o[0] += 3 * npal
    ids = [rs() for _ in range(rd("<H")[0])]
    for _ in range(rd("<H")[0]):
        rs()
    (nch,) = rd("<H")
    o[0] += 10 * nch
    (nrec,) = rd("<I")
    recs = np.frombuffer(raw, dtype=np.dtype([("p", "<u2"), ("i", "u1"), ("j", "u1"), ("k", "u1"), ("rf", "u1"),
                                              ("pe", "u1")]), count=nrec, offset=o[0])
    return side, civ, x0, z0, cell, nx, nz, ids, recs


def columns(side, nx, nz, ids, recs):
    """per cell: the top room's level (-1: none) and the house's palette variant (the walls' majority)"""
    top = np.full((nx, nz), -1, int)
    for lv in side["levels"]:
        k = lv["level"]
        for i, row in enumerate(lv["rows"]):
            for j, ch in enumerate(row):
                if ch == "#":
                    top[i, j] = max(top[i, j], k)
    walls = np.array([p.startswith(("wall", "corner", "edge")) for p in ids])
    var = np.zeros((nx, nz, 16), int)
    sel = recs[walls[recs["p"]]]
    np.add.at(var, (sel["i"].astype(int), sel["j"].astype(int), (sel["pe"] & 15).astype(int)), 1)
    return top, var


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[k:k + 2], 16) / 255.0 for k in (0, 2, 4)])


def hull(top, var, pal, x0, z0, cell, step, quant=1):
    """boxes over step x step cells: a block's top its columns' upper quartile (in quant storeys), its colour the
    majority variant's wall"""
    nx, nz = top.shape
    bx, bz = math.ceil(nx / step), math.ceil(nz / step)
    T = np.full((bx, bz), -1, int)
    V = np.zeros((bx, bz), int)
    for a in range(bx):
        for b in range(bz):
            t = top[a * step:(a + 1) * step, b * step:(b + 1) * step]
            occ = (t >= 0).mean()
            if occ < 0.34:
                continue
            T[a, b] = int(round(np.percentile(t[t >= 0], 75) / quant)) * quant
            V[a, b] = int(var[a * step:(a + 1) * step, b * step:(b + 1) * step].sum(axis=(0, 1)).argmax())
    # merge runs along b, then identical runs along a
    rects = []
    open_ = {}
    for a in range(bx + 1):
        runs = {}
        if a < bx:
            b = 0
            while b < bz:
                if T[a, b] < 0:
                    b += 1
                    continue
                e = b
                while e + 1 < bz and T[a, e + 1] == T[a, b] and V[a, e + 1] == V[a, b]:
                    e += 1
                runs[(b, e, T[a, b], V[a, b])] = True
                b = e + 1
        for key in list(open_):
            if key not in runs:
                rects.append((open_.pop(key), a) + key)
        for key in runs:
            if key not in open_:
                open_[key] = a
    V_, T_, C_ = [], [], []
    for (a0, a1, b0, b1, t, v) in rects:
        wall = hex_rgb(pal[min(v, len(pal) - 1)].get("wall", "#cccccc"))
        roof = wall * 0.85 + 0.15
        add_box(V_, T_, C_, x0 + a0 * step * cell, z0 + b0 * step * cell, x0 + a1 * step * cell,
                z0 + (b1 + 1) * step * cell, -0.5, (t + 1) * STOREY + 0.4, wall, roof)
    return np.array(V_, np.float32), np.array(T_, np.uint32).ravel(), np.array(C_, np.float32)


def add_box(V, T, C, x0, z0, x1, z1, y0, y1, wall, roof):
    """(make_islands.boxes_mesh's box: sides and a roof, wound outward from the box's centre)"""
    base = len(V)
    for y in (y0, y1):
        for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
            V.append((x, y, z))
            C.append(wall * 0.85)
    tris = []
    for i in range(4):
        j = (i + 1) % 4
        tris += [(base + i, base + j, base + 4 + j), (base + i, base + 4 + j, base + 4 + i)]
    r = len(V)
    for (x, z) in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
        V.append((x, y1, z))
        C.append(roof)
    tris += [(r, r + 2, r + 1), (r, r + 3, r + 2)]
    ctr = np.array(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    for tri in tris:
        a, b, c = (np.array(V[k]) for k in tri)
        n = np.cross(b - a, c - a)
        o = (a + b + c) / 3 - ctr
        if abs(n[1]) > 1e-6 and abs(n[0]) + abs(n[2]) < 1e-6:
            o = np.array((0, 1.0, 0))
        T.append(tri if np.dot(n, o) >= 0 else tri[::-1])


def main():
    ids = sys.argv[1:] or sorted(f[:-7] for f in os.listdir(WR) if f.endswith(".bin.gz"))
    pals = json.load(open(os.path.join(WR, "pieces.json")))["palettes"]
    for iid in ids:
        side, civ, x0, z0, cell, nx, nz, pids, recs = read_warren(iid)
        top, var = columns(side, nx, nz, pids, recs)
        pal = pals.get(civ) or [{"wall": "#cccccc"}]
        for lod, step, quant in (("lod1", 2, 1), ("lod2", 5, 3)):
            path = os.path.join(ISL, "%s.%s.glb" % (iid, lod))
            nodes = [n for n in read_glb(path) if n["name"] not in ("buildings", "warren_hull")]
            hv, ht, hc = hull(top, var, pal, x0, z0, cell, step, quant)
            nodes.append({"name": "warren_hull", "positions": hv, "indices": ht, "colors": hc, "material": "sky_lod_bldg"})
            size = glb.write(path, nodes)
            print("%s %s: %d boxes, %d tris, %d bytes" % (iid, lod, len(hv) // 12, len(ht) // 3, size))


if __name__ == "__main__":
    main()
