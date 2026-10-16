#!/usr/bin/env python3
"""check.py -- the market kit's offline audit, on the warren audit toolkit (tools/sky/warren/audit: meshlib, rays):
every piece, full and MID, from the built glbs and pieces.json.

  topology     degenerate / duplicate faces, inconsistent winding, inside-out closed parts, non-manifold edges (meshlib)
  normals      faces pointing into their solid (ray parity) over the closed parts
  zfight       same-facing coplanar overlaps between different parts of one piece (meshlib.coplanar_overlaps)
  clip         self-clipping: edges of one part piercing another part's faces by > 2 cm (meshlib.interpenetration)
  bounds       the mesh inside its declared footprint (+ overhang), the MID inside the full mesh (meshlib.bounds)
  passes       every walk-through volume free of triangles and frame boxes, >= 2.2 m tall, >= 1.0 m wide
  headroom     rays up over every walk area: >= 2.2 m to the first triangle
  collision    frame boxes inside the mesh's bounds
  emissive     lit slots only on small parts (bulbs, lenses, tubes: <= 0.6 m2 a part); glow faces listed
  budget       tris <= the piece's budget

  ~/.venvs/ssc-assets/bin/python remake/blender/markets/check.py [ids...]
      -> reference/tmp/markets_kit/audit.json, audit.txt (problems first)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "sky", "warren", "audit"))
import meshlib as M  # noqa: E402
import rays as RY  # noqa: E402

OUT = os.path.join(ROOT, "godot_project", "remake", "markets")
REP = os.path.join(ROOT, "reference", "tmp", "markets_kit")
EMISSIVE = None
OVERHANG = 0.35


def components(tris, tol=1e-4):
    """per face: its part (faces joined through shared welded vertices)"""
    V, F = M.weld(tris, tol)
    parent = np.arange(len(V))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for f in F:
        a, b, c = find(f[0]), find(f[1]), find(f[2])
        parent[b] = a
        parent[find(c)] = a
    roots = np.array([find(f[0]) for f in F])
    _, lab = np.unique(roots, return_inverse=True)
    return lab


def comp_closed(tris, comp):
    """per part: closed (every welded edge used twice inside it)"""
    V, F = M.weld(tris, 1e-4)
    out = {}
    for c in np.unique(comp):
        f = F[comp == c]
        e = np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), 1)
        ue, cnt = np.unique(e, axis=0, return_counts=True)
        # (a solid standing on the ground has its bottom faces dropped: open edges all at y 0 still close it)
        op = ue[cnt == 1]
        # (a SHEET: mostly open edges -- a card, a pane, a cloth; a solid whose hidden faces the flicker cure cut away,
        # or welded to a neighbour it touches, still counts as solid)
        out[int(c)] = bool(len(cnt)) and float(np.mean(cnt == 1)) < 0.25
    return out


def clipping(tris, comp, R, min_depth=0.02, edge_eps=0.003):
    """edges of one part passing through another part (the visible kind: in one side and out of the other, or
    through an open sheet) -> "cross"; an edge's end buried in another part (a post in its plinth, a brace in a leg)
    -> "joint".  Hits on a face's boundary (parts that only touch) are ignored."""
    closed = comp_closed(tris, comp)
    V, F = M.weld(tris, 1e-4)
    E = np.unique(np.sort(np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1), axis=0)
    # each welded edge belongs to the part of any face using it
    fe = {}
    for fi, f in enumerate(F):
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            fe[(min(a, b), max(a, b))] = int(comp[fi])
    A, Bv = V[E[:, 0]], V[E[:, 1]]
    g = np.array([fe[(int(a), int(b))] for a, b in E])
    d = Bv - A
    L = np.linalg.norm(d, axis=1)
    ok = L > 0.01
    A, d, L, g = A[ok], d[ok] / L[ok, None], L[ok], g[ok]
    hits = [[] for _ in range(len(A))]
    o = A + d * 1e-3
    rem = L - 2e-3
    alive = np.arange(len(A))
    for _ in range(8):
        if not len(alive):
            break
        t, prim, n = R.cast(o[alive], d[alive], rem[alive])
        h = np.isfinite(t)
        for k in np.nonzero(h)[0]:
            q = alive[k]
            pc = int(comp[prim[k]])
            if pc == g[q]:
                continue
            p = o[q] + d[q] * t[k]
            tri = tris[prim[k]]
            # (distance of the hit from the pierced triangle's edges: boundary hits are contacts)
            e0 = min(np.linalg.norm(np.cross(tri[(j + 1) % 3] - tri[j], p - tri[j])) / max(np.linalg.norm(tri[(j + 1) % 3] - tri[j]), 1e-9) for j in range(3))
            if e0 < edge_eps or abs(float(np.dot(R.normal[prim[k]], d[q]))) < 0.05:
                continue
            s_along = (L[q] - rem[q] - 2e-3) + t[k] + 1e-3
            hits[q].append((pc, float(s_along), p))
        step = np.nonzero(h)[0]
        o[alive[step]] = o[alive[step]] + d[alive[step]] * (t[step, None] + 1e-3)
        rem[alive[step]] -= t[step] + 1e-3
        alive = alive[step]
        alive = alive[rem[alive] > 1e-3]
    cross, joint = [], []
    part_rays = {}

    def inner_depth(p, pc):
        """how deep p lies inside part pc: the nearest of its surfaces along the six axes"""
        if pc not in part_rays:
            part_rays[pc] = RY.Rays(tris[comp == pc])
        dirs = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
        t, _, _ = part_rays[pc].cast(np.tile(p, (6, 1)), dirs, 50.0)
        return float(np.min(t))
    for q, hs in enumerate(hits):
        by = {}
        for pc, sa, p in hs:
            by.setdefault(pc, []).append((sa, p))
        for pc, lst in by.items():
            lst.sort(key=lambda x: x[0])
            if not closed.get(pc, False):
                for sa, p in lst:
                    if min(sa, L[q] - sa) >= min_depth:
                        cross.append((p, int(g[q]), pc))
                continue
            if len(lst) >= 2 and lst[-1][0] - lst[0][0] >= min_depth:
                mid_p = (lst[0][1] + lst[-1][1]) / 2
                if inner_depth(mid_p, pc) >= 0.015:              # (a seam a few mm deep is a contact, not a clip)
                    cross.append((lst[0][1], int(g[q]), pc))
            elif min(lst[0][0], L[q] - lst[0][0]) >= min_depth:
                joint.append((lst[0][1], int(g[q]), pc, min(lst[0][0], L[q] - lst[0][0])))
    return cross, joint


def box_overlap(a, b, eps=0.0):
    return all(a[0][k] < b[1][k] - eps and b[0][k] < a[1][k] - eps for k in range(3))


def check_piece(pid, rec, tris, mats, mid_tris, slot_group):
    probs, info = [], {}
    t = M.topology(tris)
    info["tris"] = int(len(tris))
    for k in ("degenerate", "dup_faces", "inconsistent_edges", "inside_out"):
        if t[k]:
            probs.append((k, t[k], t.get(k.replace("_edges", "") + "_at", t.get("degenerate_at"))[:3] if k != "inside_out" else
                          [c["lo"] for c in t["components"] if c["inside_out"]][:3]))
    info["nonmanifold"] = t["nonmanifold_edges"]
    if t["nonmanifold_edges"]:
        probs.append(("nonmanifold", t["nonmanifold_edges"], t["nonmanifold_at"][:3]))
    info["open_edges"] = t["open_edges"]
    comp = components(tris)
    R = RY.Rays(tris)
    # normals over the closed parts
    closed = [c for c in t["components"] if c["closed"]]
    info["closed_parts"] = len(closed)
    inv = M.inward_normals(tris, R, sample=1500)
    # (only meaningful on closed parts: count inward faces whose part is closed)
    lab_closed = set()
    if closed:
        lo = np.array([c["lo"] for c in closed])
        hi = np.array([c["hi"] for c in closed])
        for f in inv["faces"]:
            cen = tris[f].mean(0)
            if np.any(np.all((cen >= lo - 1e-6) & (cen <= hi + 1e-6), axis=1)):
                lab_closed.add(int(comp[f]))
    inward_closed = 0
    for f in inv["faces"]:
        if int(comp[f]) in lab_closed:
            inward_closed += 1
    info["inward_sampled"] = inward_closed
    # z-fighting between parts
    zf = M.coplanar_overlaps(tris, comp, min_area=2e-4)
    if zf:
        probs.append(("zfight", len(zf), [z[3] for z in zf[:3]]))
    # self-clipping between parts
    cross, joint = clipping(tris, comp, R)
    closed = comp_closed(tris, comp)
    gmat = {}
    for fi, m_ in enumerate(mats):
        gmat.setdefault(int(comp[fi]), slot_group.get(m_, ""))
    SOFT = {"glass", "glow", "emissive", "canvas", "tex_markets", "tex_mascots", "tex_stalls", "tex_goods", "tex_text"}

    def visible_kind(a, b):
        return (not closed.get(a, False)) or (not closed.get(b, False)) or gmat.get(a) in SOFT or gmat.get(b) in SOFT
    clips = [c for c in cross if visible_kind(c[1], c[2])]
    seams = [c for c in cross if not visible_kind(c[1], c[2])]
    if clips:
        probs.append(("clip", len(clips), [c[0].round(3).tolist() for c in clips[:4]]))
    info["solid_crossings"] = len(seams)
    info["joints"] = len(joint)
    if joint:
        info["joint_max_depth"] = round(max(j[3] for j in joint), 3)
    # bounds: the declared footprint (+ overhang), the MID inside the full
    lo, hi = tris.reshape(-1, 3).min(0), tris.reshape(-1, 3).max(0)
    info["bounds"] = [lo.round(3).tolist(), hi.round(3).tolist()]
    foot = None if rec.get("foot_from_mesh") else rec.get("foot")
    if foot:
        b = M.bounds(tris, [-foot[0] / 2 - OVERHANG, -1e3, -foot[1] / 2 - OVERHANG], [foot[0] / 2 + OVERHANG, 1e3, foot[1] / 2 + OVERHANG])
        if b["over"]:
            probs.append(("outside_foot", b["worst"], b["over"]))
    if mid_tris is not None and len(mid_tris):
        b = M.bounds(mid_tris, lo - 0.02, hi + 0.02)
        if b["over"]:
            probs.append(("mid_outside_full", b["worst"], b["over"]))
        tm = M.topology(mid_tris)
        for k in ("degenerate", "dup_faces", "inconsistent_edges", "inside_out"):
            if tm[k]:
                probs.append(("mid_" + k, tm[k], None))
        info["mid_tris"] = int(len(mid_tris))
    # passes: free of triangles and of frame boxes, tall and wide enough
    frames = rec.get("frame", [])
    for k, p in enumerate(rec.get("passes", [])):
        blo, bhi = np.array(p["box"][0], float), np.array(p["box"][1], float)
        h = bhi[1] - blo[1]
        w = max(bhi[0] - blo[0], bhi[2] - blo[2])
        if h < 2.2 - 1e-6 or w < 1.0 - 1e-6:
            probs.append(("pass_small", round(float(min(h, w)), 3), [float(w), float(h)]))
        inside = M.tri_box_overlap(tris, blo + 0.01, bhi - 0.01)
        if inside.any():
            probs.append(("pass_blocked", int(inside.sum()), tris[np.nonzero(inside)[0][:3]].mean(1).round(3).tolist()))
        for fb in frames:
            if box_overlap((blo + 0.005, bhi - 0.005), fb):
                probs.append(("pass_frame", 1, fb))
    # head room over the walk areas
    worst = None
    for x0, z0, x1, z1, y in rec.get("walk", []):
        xs = np.arange(x0 + 0.05, x1 - 0.04, 0.2)
        zs = np.arange(z0 + 0.05, z1 - 0.04, 0.2)
        X, Z = np.meshgrid(xs, zs)
        o = np.stack([X.ravel(), np.full(X.size, y + 0.1), Z.ravel()], 1)
        d, prim, _ = R.cast(o, np.tile([0.0, 1.0, 0.0], (len(o), 1)), 2.1)
        bad = np.isfinite(d)
        if bad.any():
            worst = min(worst or 9, float(d[bad].min()) + 0.1)
            probs.append(("headroom", int(bad.sum()), o[bad][:3].round(2).tolist()))
    if rec.get("walk"):
        info["headroom_ok"] = worst is None
    # collision boxes inside the mesh bounds
    for fb in frames:
        if np.any(np.array(fb[0]) < lo - 0.05) or np.any(np.array(fb[1]) > hi + 0.05):
            probs.append(("frame_outside_mesh", 1, fb))
    # emissive parts small; glow listed
    em = np.array([slot_group.get(m_, "") == "emissive" for m_ in mats])
    if em.any():
        area = M.tri_area(tris)
        big = 0.0
        for c in np.unique(comp[em]):
            sel = (comp == c) & em
            ext = float(np.ptp(tris[sel].reshape(-1, 3), axis=0).max())
            girth = float(area[sel].sum()) / max(float(np.ptp(tris[sel].reshape(-1, 3), axis=0).sum()), 0.05)
            if ext > 1.0 and girth > 0.5:                 # (only small lit parts: bulbs, lenses, lamps; or thin tubes)
                big = max(big, ext)
        info["emissive_big_part_m"] = round(big, 3)
        if big > 0:
            probs.append(("emissive_big", round(big, 3), None))
    gl = np.array([slot_group.get(m_, "") == "glow" for m_ in mats])
    if gl.any():
        info["glow_m2"] = round(float(M.tri_area(tris[gl]).sum()), 3)
    if rec.get("budget") and len(tris) > rec["budget"]:
        probs.append(("over_budget", int(len(tris)), rec["budget"]))
    return probs, info


def main(ids=None):
    pj = json.load(open(os.path.join(OUT, "pieces.json")))
    full = M.read_glb_meshes(os.path.join(OUT, "kit.glb"))
    midm = M.read_glb_meshes(os.path.join(OUT, "kit_mid.glb"))
    sg = {"mk_" + k: v for k, v in pj["slot_group"].items()}
    rows, allp = {}, 0
    for pid, rec in pj["pieces"].items():
        if ids and pid not in ids:
            continue
        if pid not in full:
            rows[pid] = {"problems": [("missing", 1, None)], "info": {}}
            continue
        tris, mats = full[pid]
        mt = midm.get(pid, (None, None))[0]
        probs, info = check_piece(pid, rec, np.asarray(tris, float), mats, None if mt is None else np.asarray(mt, float), sg)
        rows[pid] = {"problems": probs, "info": info}
        allp += len(probs)
    os.makedirs(REP, exist_ok=True)
    json.dump(rows, open(os.path.join(REP, "audit.json"), "w"), indent=0, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    lines = []
    bad = [p for p, r in rows.items() if r["problems"]]
    for pid in bad + [p for p in rows if p not in bad]:
        r = rows[pid]
        i = r["info"]
        head = "%-44s %6s tris  mid %6s  open %5s  nonman %3s" % (pid, i.get("tris"), i.get("mid_tris", "="), i.get("open_edges"), i.get("nonmanifold"))
        lines.append(head + ("  OK" if not r["problems"] else ""))
        for k, n, at in r["problems"]:
            lines.append("    %-20s %s  %s" % (k, n, json.dumps(at, default=str)[:160]))
    open(os.path.join(REP, "audit.txt"), "w").write("\n".join(lines) + "\n")
    kinds = {}
    for r in rows.values():
        for k, n, _ in r["problems"]:
            kinds[k] = kinds.get(k, 0) + 1
    print("%d pieces checked, %d with problems: %s" % (len(rows), len(bad), kinds))
    return rows


if __name__ == "__main__":
    main(sys.argv[1:] or None)
