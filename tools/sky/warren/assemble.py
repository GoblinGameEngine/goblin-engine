#!/usr/bin/env python3
"""assemble.py -- a warren's placement file assembled from the REAL kit pieces (remake/blender/sky/warren_kit:
the same builders that wrote kit.glb), palette-baked, into one .npz of triangles for render_warren.py (Blender).
It also checks the placement maths of FORMAT.md end to end: what the runtime does, this does in numpy.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/assemble.py SKY-100 OUT.npz [--box i0,j0,i1,j1]
"""
import argparse
import gzip
import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "remake", "blender", "sky", "warren_kit"))
import geom  # noqa: E402
from pieces import PIECES  # noqa: E402  (the kit's pieces.py: warren_kit is first on the path for this name)

GP = os.path.join(ROOT, "godot_project")
WR = os.path.join(GP, "remake", "sky", "warrens")


def read_bin(path):
    raw = gzip.open(path).read()
    o = [0]

    def rd(fmt):
        v = struct.unpack_from(fmt, raw, o[0])
        o[0] += struct.calcsize(fmt)
        return v

    def rs():
        (n,) = rd("<H")
        s = raw[o[0]:o[0] + n].decode()
        o[0] += n
        return s
    assert raw[:4] == b"WRN1"
    o[0] = 4
    (ver,) = rd("<H")
    civ = rs()
    x0, z0, cell, storey = rd("<ffff")
    nx, nz, lv = rd("<HHB")
    (npal,) = rd("<B")
    o[0] += 3 * npal
    ids = [rs() for _ in range(rd("<H")[0])]
    species = [rs() for _ in range(rd("<H")[0])]
    (nch,) = rd("<H")
    o[0] += 10 * nch
    (nrec,) = rd("<I")
    recs = np.frombuffer(raw, dtype=np.dtype([("p", "<u2"), ("i", "u1"), ("j", "u1"), ("k", "u1"), ("rf", "u1"),
                                              ("pe", "u1")]), count=nrec, offset=o[0])
    o[0] += 7 * nrec
    (nu,) = rd("<H")
    o[0] += 5 * nu
    (nd,) = rd("<H")
    o[0] += 7 * nd
    travel = rd("<ffff")
    (nf,) = rd("<I")
    fol = []
    for _ in range(nf):
        sp, fx, fz, fy, fr, fs = rd("<BhhBBB")
        fol.append((species[sp], fx / 10.0, fy / 4.0, fz / 10.0, fr / 256.0 * math.tau, fs / 64.0))
    return dict(ver=ver, civ=civ, x0=x0, z0=z0, cell=cell, storey=storey, nx=nx, nz=nz, ids=ids, recs=recs,
                travel=travel, foliage=fol)


def piece_arrays(pid, cache={}):
    """a kit piece -> {slot: (tris (n, 3, 3) float32, shade (n,))}"""
    if pid not in cache:
        m = PIECES[pid]["build"]()
        d = {}
        for s, ts in m.tris.items():
            if ts:
                d[s] = (np.array([t[:3] for t in ts], np.float32), np.array([t[3] for t in ts], np.float32))
        cache[pid] = d
    return cache[pid]


def srgb_lin(h):
    h = h.lstrip("#")
    c = np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iid")
    ap.add_argument("out")
    ap.add_argument("--box", default="")
    a = ap.parse_args()
    f = read_bin(os.path.join(WR, a.iid + ".bin.gz"))
    pal = json.load(open(os.path.join(WR, "pieces.json")))["palettes"].get(f["civ"]) or \
        json.load(open(os.path.join(WR, a.iid + ".json")))["palettes"]
    from lattice import Lattice
    isl = next(i for i in json.load(open(os.path.join(GP, "remake", "sky", "islands.json")))["islands"]
               if i["id"] == a.iid)
    L = Lattice(isl, 0)
    box = [int(v) for v in a.box.split(",")] if a.box else None
    r = f["recs"]
    rot = r["rf"] & 3
    deck = (r["rf"] & 4) > 0
    mount = (r["rf"] >> 4) & 3
    quarter = (r["rf"] >> 6) & 3
    pv = r["pe"] & 15
    cx = f["x0"] + f["cell"] * r["i"] + f["cell"] / 2
    cz = f["z0"] + f["cell"] * r["j"] + f["cell"] / 2
    cy = np.where(deck, [L.deck_y(x, z) for x, z in zip(cx, cz)], f["storey"] * r["k"].astype(np.float32) + 0.8 * quarter.astype(np.float32))
    keep = np.ones(len(r), bool)
    if box:
        keep = (r["i"] >= box[0]) & (r["j"] >= box[1]) & (r["i"] <= box[2]) & (r["j"] <= box[3])
    out_t, out_c, out_e = [], [], []
    for p in np.unique(r["p"][keep]):
        pid = f["ids"][p]
        sel = np.nonzero(keep & (r["p"] == p))[0]
        arrs = piece_arrays(pid)
        ang = rot[sel] * (math.pi / 2)
        c, s = np.cos(ang)[:, None, None], np.sin(ang)[:, None, None]
        # the mount's offset (FORMAT.md): face +1.5 along the piece's +Z, corner +1.5 on X and Z, cell none
        off = np.zeros((len(sel), 3), np.float32)
        off[mount[sel] == 1] = (0, 0, 1.5)
        off[mount[sel] == 2] = (1.5, 0, 1.5)
        for slot, (tri, shade) in arrs.items():
            P = tri[None, :, :, :] + off[:, None, None, :]                       # (n, t, 3, 3)
            x = c * P[..., 0] + s * P[..., 2]
            z = -s * P[..., 0] + c * P[..., 2]
            y = P[..., 1]
            X = x + cx[sel][:, None, None]
            Z = z + cz[sel][:, None, None]
            Y = y + cy[sel][:, None, None]
            T = np.stack([X, Y, Z], -1).reshape(-1, 3, 3)
            col = np.array([srgb_lin(pal[v % len(pal)].get(slot, "#cccccc")) for v in pv[sel]])   # (n, 3)
            C = (col[:, None, :] * shade[None, :, None]).reshape(-1, 3)
            out_t.append(T.astype(np.float32))
            out_c.append(C.astype(np.float32))
            out_e.append(np.full(len(T), slot == "emissive"))
    # (preview only) the ponds' water: the island draws its own water surface; here a flat sheet over WATER cells
    from lattice import WATER
    wc = srgb_lin(pal[0].get("water", "#3d7f8c"))
    W = []
    for i in range(L.nx):
        for j in range(L.nz):
            if L.plan[i, j] == WATER and (not box or (box[0] <= i <= box[2] and box[1] <= j <= box[3])):
                x, _, z = L.centre(i, j)
                y = L.deck_y(x, z) - 0.25
                q0, q1, q2, q3 = (x - 1.5, y, z - 1.5), (x + 1.5, y, z - 1.5), (x + 1.5, y, z + 1.5), (x - 1.5, y, z + 1.5)
                W += [(q0, q2, q1), (q0, q3, q2)]
    if W:
        out_t.append(np.array(W, np.float32))
        out_c.append(np.tile(wc, (len(W), 1)).astype(np.float32))
        out_e.append(np.zeros(len(W), bool))
    tris = np.concatenate(out_t)
    np.savez_compressed(a.out, tris=tris, cols=np.concatenate(out_c), emis=np.concatenate(out_e),
                        foliage=np.array([[x, y, z, sc] for (_, x, y, z, _, sc) in f["foliage"]], np.float32),
                        fol_sp=np.array([sp for (sp, *_r) in f["foliage"]]))
    print("assembled", a.iid, "placements", int(keep.sum()), "triangles", len(tris), "->", a.out)


if __name__ == "__main__":
    main()
