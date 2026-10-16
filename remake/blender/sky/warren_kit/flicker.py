"""flicker.py -- find and cure faces that can z-fight at distance: two faces facing the same way, less than MIN_GAP
apart, overlapping each other (a paint band, a tile inset, a sign panel or a strip laid flush on a wall; a pave top over
its joint sheet).  At 100+ m the depth buffer cannot tell 4 mm apart, so they shimmer.

  find(mesh_a, mesh_b=None)   -> [(tri_i, tri_j, gap, overlap_area)]   (within one mesh, or between two)
  separate(mesh)              -> the mesh with each offending component moved off its partner to MIN_GAP (the
                                 smaller one moves: outward if it is in front, inward if it is behind)
"""
import math

import numpy as np
from shapely.geometry import Polygon

from geom import Mesh, SLOTS

MIN_GAP = 0.025       # faces closer than this (and overlapping) may shimmer at distance
TOL_N = 0.995         # "facing the same way"


def _tri_arrays(m, comp_of=None):
    tris, slots, comps = [], [], []
    k = 0
    for s in SLOTS:
        for t in m.tris[s]:
            tris.append(np.array(t[:3], float))
            slots.append(s)
            comps.append(comp_of[k] if comp_of else 0)
            k += 1
    return tris, slots, comps


def _plane(t):
    n = np.cross(t[1] - t[0], t[2] - t[0])
    ln = np.linalg.norm(n)
    if ln < 1e-12:
        return None, None, 0.0
    n = n / ln
    return n, float(np.dot(n, t[0])), ln / 2


def _proj(t, n):
    """the triangle in 2D, on the plane of normal n"""
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    return Polygon([(float(np.dot(p, u)), float(np.dot(p, v))) for p in t])


def find(ma, mb=None, min_gap=MIN_GAP, min_area=2e-4):
    """pairs of same-facing faces closer than min_gap that overlap by more than min_area (m2)"""
    A, _, _ = _tri_arrays(ma)
    B = A if mb is None else _tri_arrays(mb)[0]
    pa = [_plane(t) for t in A]
    pb = pa if mb is None else [_plane(t) for t in B]
    # bucket B by its dominant normal and plane offset
    buckets = {}
    for j, (n, d, ar) in enumerate(pb):
        if n is None or ar < 1e-6:
            continue
        key = (round(n[0], 1), round(n[1], 1), round(n[2], 1))
        buckets.setdefault(key, []).append(j)
    out = []
    for i, (n, d, ar) in enumerate(pa):
        if n is None or ar < 1e-6:
            continue
        key = (round(n[0], 1), round(n[1], 1), round(n[2], 1))
        lo_i, hi_i = A[i].min(axis=0), A[i].max(axis=0)
        for j in buckets.get(key, []):
            if mb is None and j <= i:
                continue
            nj, dj, _ = pb[j]
            if float(np.dot(n, nj)) < TOL_N:
                continue
            gap = abs(dj - d)
            if gap >= min_gap:
                continue
            lo_j, hi_j = B[j].min(axis=0), B[j].max(axis=0)
            if np.any(lo_i > hi_j + min_gap) or np.any(lo_j > hi_i + min_gap):
                continue                                       # (the slack: the two lie in parallel planes apart)
            try:
                ov = _proj(A[i], n).intersection(_proj(B[j], n)).area
            except Exception:
                continue
            if ov > min_area:
                out.append((i, j, gap, ov))
    return out


def _basis(n):
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a)
    u /= np.linalg.norm(u)
    return u, np.cross(n, u)


def cure(m, min_gap=MIN_GAP, passes=10):
    """make every same-facing overlapping pair of faces at least min_gap apart, or remove the hidden part:
      * a small component in front of (or flush on) a bigger one -- a strip, a decal, a sign, a trim -- moves OUT along
        the face normal to min_gap (it stays the visible one);
      * a bigger face in front of a smaller one hides it: the hidden part of the smaller one is CUT AWAY;
      * two flush faces of like size (overlapping corners of boxes, a slab doubled) -- the later is cut away.
    returns (mesh, log) -- log: [(kind, slot, n_tris, detail)]"""
    from mid import _components
    import shapely
    log = []
    for _ in range(passes):
        comps = _components(m)
        flat, cid, carea = [], [], []
        for c, (s, ts) in enumerate(comps):
            carea.append(sum(0.5 * float(np.linalg.norm(np.cross(np.subtract(t[1], t[0]), np.subtract(t[2], t[0])))) for t in ts))
            for t in ts:
                flat.append((s, t))
                cid.append(c)
        mm = Mesh()
        idx = []
        for s in SLOTS:
            for k, (s2, t) in enumerate(flat):
                if s2 == s:
                    mm.tris[s].append(t)
                    idx.append(k)
        hits = find(mm, min_gap=min_gap, min_area=1e-4)          # (as the runtime check counts them: 1 cm2 and up)
        hits = [(idx[i], idx[j], g, ov) for i, j, g, ov in hits]
        if not hits:
            break
        shift, cut = {}, {}
        for ki, kj, g, ov in hits:
            if cid[ki] == cid[kj]:                                # within one part: cut the hidden (or later) face
                ti, tj = np.array(flat[ki][1][:3]), np.array(flat[kj][1][:3])
                n, di, _ = _plane(ti)
                dj = float(np.dot(n, tj[0]))
                back, front = (ki, kj) if (g < 0.002 and ki > kj) or (g >= 0.002 and di < dj) else (kj, ki)
                cut.setdefault(back, []).append(front)
                continue
            ti, tj = np.array(flat[ki][1][:3]), np.array(flat[kj][1][:3])
            n, di, _ = _plane(ti)
            dj = float(np.dot(n, tj[0]))
            ci, cj = cid[ki], cid[kj]
            if g < 0.002:
                small, big = (ki, kj) if carea[ci] <= carea[cj] else (kj, ki)
                if carea[cid[small]] > 0.3 * carea[cid[big]]:
                    if carea[cid[big]] < 0.08:                 # two little parts flush: the smaller steps out
                        nf, _, _ = _plane(np.array(flat[small][1][:3]))
                        v = nf * (min_gap + 0.003)
                        cur = shift.get(cid[small])
                        if cur is None or np.linalg.norm(v) > np.linalg.norm(cur):
                            shift[cid[small]] = v
                        continue
                    later = max(ki, kj)
                    cut.setdefault(later, []).append(min(ki, kj))
                    continue
                front, back = small, big
            else:
                front, back = (ki, kj) if di > dj else (kj, ki)
            cf, cb = cid[front], cid[back]
            if carea[cf] <= carea[cb] or flat[back][0] == "glass":
                need = min_gap + 0.003 - g
                nf, _, _ = _plane(np.array(flat[front][1][:3]))
                v = nf * need
                cur = shift.get(cf)
                if cur is None or np.linalg.norm(v) > np.linalg.norm(cur):
                    shift[cf] = v
            else:
                cut.setdefault(back, []).append(front)
        out = Mesh()
        for k, (s, t) in enumerate(flat):
            c = cid[k]
            if c in shift:
                v = shift[c]
                out.tris[s].append(tuple(tuple(float(x) for x in np.add(p, v)) for p in t[:3]) + tuple(t[3:]))
                continue
            if k in cut and s != "glass":
                tt = np.array(t[:3], float)
                n, d, _ = _plane(tt)
                u, w = _basis(n)
                poly = Polygon([(float(np.dot(p, u)), float(np.dot(p, w))) for p in tt])
                for o in cut[k]:
                    to = np.array(flat[o][1][:3], float)
                    try:
                        poly = poly.difference(Polygon([(float(np.dot(p, u)), float(np.dot(p, w))) for p in to]).buffer(1e-6))
                    except Exception:
                        pass
                kept = 0
                poly = poly.simplify(2e-4, preserve_topology=True)
                for g in getattr(poly, "geoms", [poly]):
                    if g.geom_type != "Polygon" or g.area < 1e-5:
                        continue
                    for tri in shapely.constrained_delaunay_triangles(g).geoms:
                        cc = list(tri.exterior.coords)[:3]
                        e = [np.hypot(cc[(q + 1) % 3][0] - cc[q][0], cc[(q + 1) % 3][1] - cc[q][1]) for q in range(3)]
                        if tri.area < 1e-6 or 2 * tri.area / max(e) < 2e-3:
                            continue                              # (no slivers: a sliver is a degenerate face)
                        pts = [tuple(float(x) for x in (u * a + w * b + n * d)) for a, b in cc]
                        out.tri_facing(*pts, tuple(n), s, t[3])
                        kept += 1
                log.append(("cut", s, 1, kept))
                continue
            out.tris[s].append(t)
        for c, v in shift.items():
            log.append(("moved", comps[c][0], len(comps[c][1]), [round(float(x), 3) for x in v]))
        m = out
    return m, log




def clip_x(m, x0=-1.5, x1=1.5, axis=0):
    """clip a bay's geometry to its own width: overhangs (eaves, roofs, louvres past the bay's ends) would lie flush on
    the neighbour bay's own in a row and shimmer.  Triangles are cut by the two planes (uvs carried along)."""
    out = Mesh()
    for s in SLOTS:
        for t in m.tris[s]:
            pts = [np.array(p, float) for p in t[:3]]
            uvs = [np.array(u, float) for u in t[4]] if t[4] else None
            poly = list(zip(pts, uvs or [None] * 3))
            for sign, lim in ((1, x0), (-1, x1)):
                if not poly:
                    break
                res = []
                for k in range(len(poly)):
                    (p, u), (q, w) = poly[k], poly[(k + 1) % len(poly)]
                    ip, iq = sign * (p[axis] - lim) >= -1e-9, sign * (q[axis] - lim) >= -1e-9
                    if ip:
                        res.append((p, u))
                    if ip != iq:
                        f = (lim - p[axis]) / (q[axis] - p[axis])
                        res.append((p + (q - p) * f, None if u is None else u + (w - u) * f))
                poly = res
            if len(poly) < 3:
                continue
            for k in range(1, len(poly) - 1):
                a, b, c = poly[0], poly[k], poly[k + 1]
                tri = [tuple(float(x) for x in a[0]), tuple(float(x) for x in b[0]), tuple(float(x) for x in c[0])]
                ar2 = np.linalg.norm(np.cross(np.subtract(tri[1], tri[0]), np.subtract(tri[2], tri[0])))
                el = max(np.linalg.norm(np.subtract(tri[(q + 1) % 3], tri[q])) for q in range(3))
                if ar2 < 1e-8 or ar2 / max(el, 1e-9) < 2e-3:
                    continue                                      # (a clipped sliver)
                uv = [tuple(a[1]), tuple(b[1]), tuple(c[1])] if uvs is not None else None
                out.tris[s].append((tri[0], tri[1], tri[2], t[3], uv))
    return out


def clip_threshold(m):
    """a wall bay's parts that straddle its floor line (an arch moulding wrapped under the threshold) are cut at y 0;
    parts wholly below it (brackets, corbels, struts hung under a projection) stay"""
    from mid import _components
    out = Mesh()
    for s, ts in _components(m):
        ys = [p[1] for t in ts for p in t[:3]]
        sub = Mesh()
        sub.tris[s] = list(ts)
        if min(ys) < -0.005 and max(ys) > 0.05:
            sub = clip_x(sub, 0.0, 1e9, axis=1)
        out.tris[s] += sub.tris[s]
    return out


WIDE = {"portal_pishtaq"}                                         # wall pieces meant to span several bays


def finish(pid, d, m):
    """the flicker pass every piece goes through before export: corner pieces stand 3 cm proud of the bays they join;
    bays are clipped to their own width and floor line; then cure() (offset or cut every near-coplanar overlap)"""
    log = []
    if d["group"] == "corner":
        out = Mesh()
        out.add(m, lambda p: (p[0] + 0.05, p[1], p[2] + 0.05))
        m = out
        log.append(("corner proud 5 cm", "", 0, ""))
    elif d["group"] in ("wall", "edge") and pid not in WIDE:
        n0 = m.count()
        m = clip_threshold(clip_x(m))
        if m.count() != n0:
            log.append(("clipped to the bay", "", m.count() - n0, ""))
        if d["group"] == "wall":                                  # what hangs under a projection (soffits, corbels)
            from mid import _components                          # steps 3 cm back, off the storey below's own
            out, hung = Mesh(), 0
            for s, ts in _components(m):
                ys = [p[1] for t in ts for p in t[:3]]
                if max(ys) <= 0.05 and min(ys) < -0.02:
                    hung += 1
                    out.tris[s] += [tuple((p[0], p[1], p[2] - 0.03) for p in t[:3]) + tuple(t[3:]) for t in ts]
                else:
                    out.tris[s] += ts
            if hung:
                log.append(("hung parts 3 cm back", "", hung, ""))
            m = out
    m, cl = cure(m)
    return m, log + cl
