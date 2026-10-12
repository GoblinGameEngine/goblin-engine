#!/usr/bin/env python3
"""check_models.py -- mesh-level checks on the game's building models (the user, 2026-10-09: "You need to have tools that
you can use to check that every model is manifold"). Reads the shipped glbs in godot_project/remake/buildings (numpy, no
Blender), so it checks exactly what the game draws. Complements remake/blender/gbaudit.py, which runs at build time on
the plan (rooms sealed, furniture inside the walls, door leaves solid) and passes on all 8,085 planned buildings.

Each building's visual mesh is welded by position (glTF splits a vertex wherever its normal or UV changes) and cut into
pieces (connected parts: a window's sash, a chair, a wall run). Per piece:

  open_solid     a piece that isn't flat but has open edges you can see through (gap_edges: a box missing a face).
                 Open edges that lie along another face's edge (tjunction_edges) or flat on another face (seated_edges:
                 a wall standing on a slab) are closed to the eye and counted, not flagged. So are edges with more
                 than one face on them (boxes butted end to end); miswound_edges counts edges with two faces wound
                 the same way round (one face of the pair is backwards); buried_edges, open edges below
                 the ground (y < -0.05 in the glb frame); embedded_edges, open ends sunk inside another solid.
  nonmanifold    an edge shared by more than two triangles (a fin, two solids welded along an edge)
  inside_out     a closed piece whose volume is negative: its faces wound inward (dark, lit from inside)
  flipped        triangles whose winding disagrees with their own vertex normals (lit wrong)
Per mesh:
  degenerate     zero-area triangles (waste; break normals and collision)
  duplicate      the same triangle twice, same way round (z-fighting)
  zfight         two triangles of DIFFERENT pieces in one plane, facing the same way, overlapping (flicker);
                 zfight_hidden counts those pressed against a face looking back at them (unseen), zfight_same those
                 of one material (UVs are by world position, so both draw the same pixels: unseen, only overdraw)
  bad_number     a NaN or infinite coordinate
Open flat pieces (glass, decals, floor finishes, one-sided planes) are counted, not flagged.

    python3 tools/buildings/check_models.py [ID ...] [--all] [--lods] [--jobs N] [--report PATH] [--dir GLBS]
    python3 tools/buildings/check_models.py --explain ID [ID ...] [--dir GLBS]   (worst places + marks for render_marks)

Writes a JSON report (default reference/tmp/model_check.json): per building its counts and the worst places (positions
in the glb frame), and prints a summary by defect and by building family.
"""
import json
import os
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glbmesh import Glb, components, weld, world_prims  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
BUILDINGS = os.path.join(ROOT, "godot_project", "remake", "buildings")
DEFAULT_BUILDINGS = BUILDINGS
REPORT = os.path.join(ROOT, "reference", "tmp", "model_check.json")
FLAT_TOL = 0.002        # m: a piece this close to one plane is a sheet (open edges are fine)
AREA_EPS = 1e-8         # m^2: below this a triangle is degenerate
ZF_PLANE = 0.002        # m: two faces this close to the same plane z-fight
ZF_COVER = 0.03         # m: ...unless a face this close in front looks back at them (hidden)
EXPLAIN_ZF = 40          # z-fight spots --explain lists per building
DEFECTS = ("open_solid", "gap_edges", "tjunction_edges", "seated_edges", "miswound_edges", "buried_edges", "embedded_edges", "nonmanifold", "inside_out", "flipped", "degenerate", "duplicate", "zfight", "zfight_same", "zfight_hidden", "bad_number")


def _pt_tri_dist(q, a, b, c):
    """Distance from point q to each triangle (a, b, c)."""
    n = np.cross(b - a, c - a)
    nn = np.maximum((n * n).sum(1), 1e-18)
    dpl = ((q - a) * n).sum(1)
    p = q - n * (dpl / nn)[:, None]
    inside = (((np.cross(b - a, p - a) * n).sum(1) >= 0) & ((np.cross(c - b, p - b) * n).sum(1) >= 0) &
              ((np.cross(a - c, p - c) * n).sum(1) >= 0))
    best = np.abs(dpl) / np.sqrt(nn)
    seg = np.full(len(a), np.inf)
    for s0, s1 in ((a, b), (b, c), (c, a)):
        d = s1 - s0
        t = np.clip(((q - s0) * d).sum(1) / np.maximum((d * d).sum(1), 1e-18), 0, 1)
        seg = np.minimum(seg, np.linalg.norm(s0 + d * t[:, None] - q, axis=1))
    return np.where(inside, best, seg)


def check(path, explain=None):
    g = Glb(path)
    Ps, Ns, Is, Ms = [], [], [], []
    base = 0
    for node, mesh, P, N, U, I, mat in world_prims(g, lambda n: not n.endswith("-colonly") and "collision" not in n):
        Ps.append(P)
        Ns.append(N if N is not None else np.zeros_like(P))
        Is.append(I + base)
        Ms.append(np.full(len(I), mat, dtype=object))
        base += len(P)
    out = {"id": os.path.basename(path)[:-4], "counts": Counter(), "where": defaultdict(list), "pieces": 0, "sheets": 0, "tris": 0}
    if not Ps:
        return out
    P = np.concatenate(Ps)
    MAT = np.concatenate(Ms)
    N = np.concatenate(Ns)
    I = np.concatenate(Is)
    out["tris"] = int(len(I))
    c = out["counts"]
    w = out["where"]

    def note(kind, n, at=None):
        c[kind] += int(n)
        if at is not None and len(w[kind]) < 6:
            w[kind].append([round(float(v), 2) for v in at])

    bad = ~np.isfinite(P).all(1)
    if bad.any():
        note("bad_number", bad.sum(), [0, 0, 0])
        P = np.nan_to_num(P)
    W = weld(P)
    T = W[I]                                                  # triangles over welded vertices
    a, b, cc = P[I[:, 0]], P[I[:, 1]], P[I[:, 2]]
    fn = np.cross(b - a, cc - a)
    area2 = np.linalg.norm(fn, axis=1)
    degen = (area2 < 2 * AREA_EPS) | (T[:, 0] == T[:, 1]) | (T[:, 1] == T[:, 2]) | (T[:, 0] == T[:, 2])
    if degen.any():
        note("degenerate", degen.sum(), a[degen][0])
    ok = ~degen
    # duplicates: the same three welded vertices, same winding (rotations of one triangle are the same triangle)
    rot = np.argmin(T, axis=1)
    canon = np.stack([T[np.arange(len(T)), rot], T[np.arange(len(T)), (rot + 1) % 3], T[np.arange(len(T)), (rot + 2) % 3]], 1)
    _, first, cnt = np.unique(canon[ok], axis=0, return_index=True, return_counts=True)
    dup = cnt > 1
    if dup.any():
        note("duplicate", (cnt[dup] - 1).sum(), a[ok][first[dup][0]])
    # flipped: the face normal against its vertices' normals
    unit = fn / np.maximum(area2[:, None], 1e-12)
    vn = N[I[:, 0]] + N[I[:, 1]] + N[I[:, 2]]
    has_vn = np.linalg.norm(vn, axis=1) > 0.5
    flip = ok & has_vn & (np.einsum("ij,ij->i", unit, vn) < -0.3)
    if flip.any():
        note("flipped", flip.sum(), a[flip][0])
    # pieces over the welded topology
    T2 = T[ok]
    lab = components(T2, int(W.max()) + 1)
    plab = lab[T2[:, 0]]
    # edges: each undirected welded edge's uses one way round against the other. In a closed, consistently wound surface
    # they balance (two solids that touch along an edge use it twice each way: still balanced); an edge used more one
    # way than the other is open -- a hole's rim -- or a fin.
    nvw = int(W.max()) + 1
    e = np.concatenate([T2[:, [0, 1]], T2[:, [1, 2]], T2[:, [2, 0]]])
    fwd = e[:, 0] < e[:, 1]
    key = np.minimum(e[:, 0], e[:, 1]) * nvw + np.maximum(e[:, 0], e[:, 1])
    uk, inv = np.unique(key, return_inverse=True)
    bal = np.zeros(len(uk), np.int64)
    np.add.at(bal, inv, np.where(fwd, 1, -1))
    uses = np.bincount(inv)
    edge_piece = np.concatenate([plab, plab, plab])
    open_e = bal[inv] != 0
    nm_e = (uses[inv] > 2) & (bal[inv] != 0)                    # (more than two faces, and not in balanced pairs)
    pieces = np.unique(plab)
    out["pieces"] = int(len(pieces))
    Pw = np.zeros((nvw, 3))
    Pw[W] = P
    MAT2 = MAT[ok]
    # each piece: flat (a sheet: open edges are its outline, fine) or solid
    tri_order = np.argsort(plab, kind="stable")
    cuts = np.flatnonzero(np.diff(plab[tri_order])) + 1
    groups = np.split(tri_order, cuts)
    flat_of = {}
    for grp in groups:
        pts = Pw[np.unique(T2[grp])]
        ctr = pts.mean(0)
        thick = 0.0
        if len(pts) >= 3:
            sv = np.linalg.svd(pts - ctr, full_matrices=False, compute_uv=False)
            thick = sv[-1] / max(np.sqrt(len(pts)), 1.0) * 2.0
        flat_of[int(plab[grp[0]])] = thick < FLAT_TOL
    solid_edge = ~np.array([flat_of[int(pc)] for pc in edge_piece]) if len(edge_piece) else np.zeros(0, bool)
    # an open edge of a solid lying along another face's edge (a panel meeting a wall mid-edge: a T-junction) is closed
    # to the eye though not in topology; one that doesn't is a gap you can see through
    # only an edge with one face on it can be seen through; one with more (wall boxes butted together, one end face
    # between them) is closed, however lopsided its windings
    misw = solid_edge & (uses[inv] == 2) & (bal[inv] != 0)
    c["miswound_edges"] += int(misw.sum() // 2)
    if explain is not None and misw.any():
        mi = np.flatnonzero(misw)
        explain.append(["_miswound", 0, 0, None, None, [[[round(float(v), 3) for v in Pw[e[k, 0]]], [round(float(v), 3) for v in Pw[e[k, 1]]],
                                                          MAT2[k % len(T2)]] for k in mi[:4000]]])
    open_e = open_e & solid_edge & (uses[inv] == 1)
    # below grade (the glb's y = 0 is the ground) nobody sees the rim: a footing's open bottom
    buried = open_e & (np.maximum(Pw[e[:, 0], 1], Pw[e[:, 1], 1]) < -0.05)
    c["buried_edges"] += int(buried.sum())
    open_e &= ~buried
    oe_idx = np.flatnonzero(open_e)
    gap_by = Counter()
    if len(oe_idx):
        ea, eb = Pw[e[oe_idx, 0]], Pw[e[oe_idx, 1]]
        mid = (ea + eb) * 0.5
        segs_a = np.concatenate([Pw[T2[:, 0]], Pw[T2[:, 1]], Pw[T2[:, 2]]])
        segs_b = np.concatenate([Pw[T2[:, 1]], Pw[T2[:, 2]], Pw[T2[:, 0]]])
        CELLM = 0.5
        cell = {}
        lo = np.floor(np.minimum(segs_a, segs_b) / CELLM).astype(np.int64)
        hi = np.floor(np.maximum(segs_a, segs_b) / CELLM).astype(np.int64)
        span = (hi - lo).max(1)
        for si in np.flatnonzero(span <= 6):
            for cx in range(lo[si, 0], hi[si, 0] + 1):
                for cy in range(lo[si, 1], hi[si, 1] + 1):
                    for cz in range(lo[si, 2], hi[si, 2] + 1):
                        cell.setdefault((cx, cy, cz), []).append(si)
        big = np.flatnonzero(span > 6)
        covered = np.zeros(len(oe_idx), bool)
        mc = np.floor(mid / CELLM).astype(np.int64)
        for k in range(len(oe_idx)):
            cand = np.array(list(cell.get(tuple(mc[k]), [])) + big.tolist(), dtype=np.int64)
            if not len(cand):
                continue
            sa, sb = segs_a[cand], segs_b[cand]
            d = sb - sa
            L2 = np.maximum((d * d).sum(1), 1e-12)
            t = np.clip(((mid[k] - sa) * d).sum(1) / L2, 0, 1)
            dist = np.linalg.norm(sa + d * t[:, None] - mid[k], axis=1)
            same = (np.linalg.norm(sa - ea[k], axis=1) + np.linalg.norm(sb - eb[k], axis=1) < 1e-6) | \
                   (np.linalg.norm(sa - eb[k], axis=1) + np.linalg.norm(sb - ea[k], axis=1) < 1e-6)
            covered[k] = ((dist < 0.001) & ~same).any()
        # an open edge lying flat on another face (a wall standing on a slab, a panel against a wall) is seated: closed
        # to the eye. Test three points along it against the triangles near them, not counting those it belongs to.
        tri_lo = np.floor(np.minimum(np.minimum(Pw[T2[:, 0]], Pw[T2[:, 1]]), Pw[T2[:, 2]]) / CELLM).astype(np.int64)
        tri_hi = np.floor(np.maximum(np.maximum(Pw[T2[:, 0]], Pw[T2[:, 1]]), Pw[T2[:, 2]]) / CELLM).astype(np.int64)
        tspan = (tri_hi - tri_lo).max(1)
        tcell = {}
        for ti in np.flatnonzero(tspan <= 6):
            for cx in range(tri_lo[ti, 0], tri_hi[ti, 0] + 1):
                for cy in range(tri_lo[ti, 1], tri_hi[ti, 1] + 1):
                    for cz in range(tri_lo[ti, 2], tri_hi[ti, 2] + 1):
                        tcell.setdefault((cx, cy, cz), []).append(ti)
        tbig = np.flatnonzero(tspan > 6).tolist()
        ev = e[oe_idx]
        seated = np.zeros(len(oe_idx), bool)
        for k in np.flatnonzero(~covered):
            ok_all = True
            for f in (0.2, 0.5, 0.8):
                q = ea[k] + (eb[k] - ea[k]) * f
                cand = np.array(tcell.get(tuple(np.floor(q / CELLM).astype(np.int64)), []) + tbig, dtype=np.int64)
                if len(cand):
                    tv = T2[cand]
                    cand = cand[~(((tv == ev[k, 0]).any(1)) & ((tv == ev[k, 1]).any(1)))]
                if not len(cand) or _pt_tri_dist(q, Pw[T2[cand, 0]], Pw[T2[cand, 1]], Pw[T2[cand, 2]]).min() > 0.001:
                    ok_all = False
                    break
            seated[k] = ok_all
        covered |= seated
        c["seated_edges"] += int(seated.sum())
        # an open end buried inside another solid (a partition run 5 cm into the wall it meets) can't be seen either:
        # from the edge's midpoint, rays along three axes each cross the other pieces' faces an odd number of times
        emb = np.zeros(len(oe_idx), bool)
        rest = np.flatnonzero(~covered)
        if len(rest):
            V0, V1, V2 = Pw[T2[:, 0]], Pw[T2[:, 1]], Pw[T2[:, 2]]
            E1, E2 = V1 - V0, V2 - V0
            for k in rest:
                other = plab != edge_piece[oe_idx[k]]
                o_ = mid[k]
                odd = 0
                for dvec in ((0.577, 0.577, 0.578), (-0.6, 0.48, 0.64), (0.41, -0.82, 0.4)):
                    dvec = np.array(dvec)
                    pv = np.cross(dvec, E2[other])
                    det = (E1[other] * pv).sum(1)
                    okd = np.abs(det) > 1e-12
                    inv_ = np.where(okd, 1.0 / np.where(okd, det, 1.0), 0.0)
                    tv = o_ - V0[other]
                    uu = (tv * pv).sum(1) * inv_
                    qv = np.cross(tv, E1[other])
                    vv = (qv @ dvec) * inv_
                    tt = (E2[other] * qv).sum(1) * inv_
                    hit = okd & (uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (tt > 1e-5)
                    odd += int(hit.sum()) % 2
                emb[k] = odd >= 2
        covered |= emb
        c["embedded_edges"] += int(emb.sum())
        if explain is not None:
            explain.append(["_gap_segments", 0, 0, None, None,
                            [[[round(float(v), 3) for v in ea[k]], [round(float(v), 3) for v in eb[k]]] for k in np.flatnonzero(~covered)[:4000]]])
        c["tjunction_edges"] += int((covered & ~seated).sum())
        c["gap_edges"] += int((~covered).sum())
        gap_by = Counter(edge_piece[oe_idx[~covered]].tolist())
    nm_by = Counter(edge_piece[nm_e & solid_edge].tolist())
    open_by_piece = Counter(edge_piece[bal[inv] != 0].tolist())
    for grp in groups:
        pc = int(plab[grp[0]])
        if flat_of[pc]:
            out["sheets"] += 1
            continue
        pts = Pw[np.unique(T2[grp])]
        ctr = pts.mean(0)
        if gap_by.get(pc):
            note("open_solid", 1, ctr)
            if explain is not None:
                explain.append(["open_solid", int(gap_by[pc]), len(grp), Counter(MAT2[grp].tolist()).most_common(2),
                                [round(float(v), 2) for v in pts.max(0) - pts.min(0)], [round(float(v), 2) for v in ctr]])
        if nm_by.get(pc):
            note("nonmanifold", 1, ctr)
            if explain is not None:
                explain.append(["nonmanifold", int(nm_by[pc]), len(grp), Counter(MAT2[grp].tolist()).most_common(2),
                                [round(float(v), 2) for v in pts.max(0) - pts.min(0)], [round(float(v), 2) for v in ctr]])
        if not open_by_piece.get(pc):              # truly closed only: a seated/T-junction rim makes volume meaningless
            tri = T2[grp]
            v0, v1, v2 = Pw[tri[:, 0]], Pw[tri[:, 1]], Pw[tri[:, 2]]
            vol = np.einsum("ij,ij->i", v0, np.cross(v1, v2)).sum() / 6.0
            if vol < -1e-6:
                note("inside_out", 1, ctr)
    # z-fighting: a triangle whose centroid lies inside a triangle of ANOTHER piece in the same plane, facing the same way
    okI = np.flatnonzero(ok)
    if len(okI):
        un = unit[okI]
        MATk = MAT[okI]
        A, B, Cc = a[okI], b[okI], cc[okI]
        cen = (A + B + Cc) / 3.0
        dpl = np.einsum("ij,ij->i", un, cen)
        nq = np.round(un * 50).astype(np.int64)                 # (normals to ~1 degree)
        dq = np.round(dpl / ZF_PLANE).astype(np.int64)
        gk = {}
        for i, kk in enumerate(zip(nq[:, 0], nq[:, 1], nq[:, 2], dq)):
            gk.setdefault(kk, []).append(i)
        zf = 0

        def covered(q, n0, kk, ax, ay):
            # the pair is pressed against a face looking back at it (a foot on the floor, a bookcase back on its wall):
            # a triangle facing the other way, 0..ZF_COVER in front of the plane, over the spot. Nobody sees the flicker.
            qn = (-kk[0], -kk[1], -kk[2])
            q2 = np.array([q @ ax, q @ ay])
            for t in range(0, int(ZF_COVER / ZF_PLANE) + 1):
                grp = gk.get(qn + (-kk[3] - t,))
                if not grp:
                    continue
                g_ = np.array(grp)
                a_, b_, c_ = A[g_], B[g_], Cc[g_]
                a2_ = np.stack([a_ @ ax, a_ @ ay], 1)
                v0, v1, v2 = np.stack([b_ @ ax, b_ @ ay], 1) - a2_, np.stack([c_ @ ax, c_ @ ay], 1) - a2_, q2 - a2_
                den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
                den = np.where(np.abs(den) < 1e-12, 1e-12, den)
                l1 = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
                l2 = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
                if ((l1 >= -1e-6) & (l2 >= -1e-6) & (l1 + l2 <= 1 + 1e-6)).any():
                    return True
            return False

        for kk, idx in gk.items():
            if len(idx) < 2:
                continue
            idx = np.array(idx)
            pcs = plab[idx]
            if len(np.unique(pcs)) < 2:
                continue
            # in-plane frame
            n0 = un[idx[0]]
            ax = np.cross(n0, [0.0, 1.0, 0.0] if abs(n0[1]) < 0.9 else [1.0, 0.0, 0.0])
            ax /= np.linalg.norm(ax)
            ay = np.cross(n0, ax)
            def uv(X):
                return np.stack([X @ ax, X @ ay], 1)
            a2, b2, c2, m2 = uv(A[idx]), uv(B[idx]), uv(Cc[idx]), uv(cen[idx])
            lo = np.minimum(np.minimum(a2, b2), c2)
            hi = np.maximum(np.maximum(a2, b2), c2)
            for ii in range(len(idx)):
                cand = np.flatnonzero((pcs != pcs[ii]) & (lo[:, 0] <= m2[ii, 0]) & (hi[:, 0] >= m2[ii, 0])
                                      & (lo[:, 1] <= m2[ii, 1]) & (hi[:, 1] >= m2[ii, 1]))
                if not len(cand):
                    continue
                p = m2[ii]
                v0 = b2[cand] - a2[cand]
                v1 = c2[cand] - a2[cand]
                v2 = p - a2[cand]
                den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
                den = np.where(np.abs(den) < 1e-12, 1e-12, den)
                l1 = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
                l2 = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
                inside = (l1 > 0.01) & (l2 > 0.01) & (l1 + l2 < 0.99)
                if inside.any():
                    if covered(cen[idx[ii]], n0, kk, ax, ay):
                        c["zfight_hidden"] += 1
                        continue
                    if (MATk[idx[cand[inside]]] == MATk[idx[ii]]).all():
                        # same material: the builder maps UVs by world position (gblib face()), so both draw the
                        # same pixels and the tie can't be seen -- only overdraw
                        c["zfight_same"] += 1
                        continue
                    zf += 1
                    if explain is not None and zf <= EXPLAIN_ZF:
                        explain.append(["zfight", 1, 1, [MATk[idx[ii]], MATk[idx[cand[inside][0]]]],
                                        [round(float(v), 2) for v in n0], [round(float(v), 2) for v in cen[idx[ii]]]])
                    if len(w["zfight"]) < 6:
                        w["zfight"].append([round(float(v), 2) for v in cen[idx[ii]]])
        if zf:
            c["zfight"] += zf
    return out


def run(path):
    try:
        r = check(path)
        r["counts"] = dict(r["counts"])
        r["where"] = dict(r["where"])
        return r
    except Exception as ex:                                  # noqa: BLE001 -- a broken file is a finding, not a crash
        return {"id": os.path.basename(path)[:-4], "error": repr(ex), "counts": {}, "where": {}}


def explain_one(i):
    ex = []
    r = check(os.path.join(BUILDINGS, i if i.endswith(".glb") else i + ".glb"), ex)
    print(r["id"], dict(r["counts"]), "pieces", r["pieces"], "sheets", r["sheets"])
    seg = [x for x in ex if x[0] == "_gap_segments"]
    zf = [x[5] for x in ex if x[0] == "zfight"]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    marks = os.path.join(os.path.dirname(REPORT), "marks_%s.json" % r["id"])
    mw = [x for x in ex if x[0] == "_miswound"]
    json.dump({"id": r["id"], "gaps": seg[0][5] if seg else [], "zfight": zf, "miswound": mw[0][5] if mw else []}, open(marks, "w"))
    print("  marks ->", marks)
    ex = [x for x in ex if not x[0].startswith("_")]
    kinds = Counter(x[0] for x in ex)
    for k in kinds:
        rows = [x for x in ex if x[0] == k]
        print("  %s x%d" % (k, len(rows)))
        if k == "zfight":
            pairs = Counter(tuple(sorted(x[3])) for x in rows)
            for pr, n in pairs.most_common(8):
                print("     %3d  %s" % (n, " vs ".join(pr)))
        else:
            for x in sorted(rows, key=lambda x: -x[1])[:12]:
                print("     edges %4d tris %5d  %s  size %s  at %s" % (x[1], x[2], x[3], x[4], x[5]))


def main(argv):
    global BUILDINGS
    if "--dir" in argv:                                       # another folder of glbs (a trial build)
        k = argv.index("--dir")
        BUILDINGS = os.path.abspath(argv[k + 1])
        argv = argv[:k] + argv[k + 2:]
    if "--explain" in argv:
        for i in argv[argv.index("--explain") + 1:]:
            explain_one(i)
        return
    ids = [a for a in argv if not a.startswith("--")]
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 3
    whole = "--all" in argv or not ids
    # only a whole-library run of the game's glbs writes the default report: a few ids or a trial folder must not
    # overwrite the hour-long one (they go to model_check_partial.json)
    report = argv[argv.index("--report") + 1] if "--report" in argv else \
        REPORT if whole and BUILDINGS == DEFAULT_BUILDINGS else REPORT.replace(".json", "_partial.json")
    lods = "--lods" in argv
    if "--jobs" in argv:
        ids.remove(str(jobs))
    if "--report" in argv:
        ids.remove(report)
    if "--all" in argv or not ids:
        files = sorted(f for f in os.listdir(BUILDINGS) if f.endswith(".glb") and (lods or ".lod" not in f))
    else:
        files = [i if i.endswith(".glb") else i + ".glb" for i in ids]
    paths = [os.path.join(BUILDINGS, f) for f in files]
    t0 = time.time()
    with Pool(jobs) as pool:
        res = pool.map(run, paths, chunksize=4)
    tot = Counter()
    fam = defaultdict(Counter)
    bad_b = Counter()
    for r in res:
        for k, v in r["counts"].items():
            tot[k] += v
            fam[r["id"].split("-")[0]][k] += v
            bad_b[k] += 1
    os.makedirs(os.path.dirname(report), exist_ok=True)
    json.dump({"checked": len(res), "seconds": round(time.time() - t0, 1), "totals": dict(tot), "buildings_with": dict(bad_b),
               "buildings": res}, open(report, "w"), separators=(",", ":"))
    print("checked %d models in %.0f s -> %s" % (len(res), time.time() - t0, report))
    errs = [r for r in res if "error" in r]
    for d in DEFECTS:
        print("  %-12s %8d   in %5d buildings" % (d, tot.get(d, 0), bad_b.get(d, 0)))
    print("  sheets (open flat pieces, fine) %d of %d pieces" % (sum(r.get("sheets", 0) for r in res), sum(r.get("pieces", 0) for r in res)))
    if errs:
        print("  unreadable: %d (%s)" % (len(errs), errs[0]["error"][:80]))
    worst = sorted(res, key=lambda r: -sum(r["counts"].get(d, 0) for d in DEFECTS[:4]))[:8]
    print("worst:", ", ".join("%s %s" % (r["id"], dict(r["counts"])) for r in worst if r["counts"]))


if __name__ == "__main__":
    main(sys.argv[1:])
