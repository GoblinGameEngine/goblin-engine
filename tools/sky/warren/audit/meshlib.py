"""meshlib.py -- reusable mesh checks for ANY triangle soup or GLB (the warren audit is one client; phase 2 points it
at kit pieces, city buildings, vehicles, characters, terrain and roads).

Input everywhere: tris (T, 3, 3) float, optionally group (T,) int (which part / placement each triangle belongs to).
Output: plain dicts of counts plus hotspot lists [{"at": [x, y, z], "groups": [..], "value": ..}] -- readable as text.

  weld(tris, tol)                    -> V (n,3), F (T,3): vertices merged on a tol grid (default 1 mm)
  topology(tris, tol)                -> open / non-manifold / inconsistent-winding edges, degenerate + duplicate
                                        faces, components (closed?, signed volume, inside-out?)
  inward_normals(tris, rays)         -> faces whose normal points into the solid (ray parity), for open meshes too
  coplanar_overlaps(tris, group)     -> z-fighting: same-facing coplanar overlapping faces of different groups
  duplicates_across(tris, group)     -> identical faces in different groups (welded)
  interpenetration(tris, group, R)   -> edges of one group piercing faces of another (Embree), per group pair
  bounds(tris, lo, hi, tol)          -> how far a mesh leaves a box, per side (m) + the triangles outside
  read_glb_meshes(path)              -> {node name: tris} in the glb's own frame (node transforms applied)
"""
import collections

import numpy as np

import common as C


# ------------------------------------------------------------------ topology
def weld(tris, tol=1e-3):
    v = np.asarray(tris, float).reshape(-1, 3)
    q = np.round(v / tol).astype(np.int64)
    _, first, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    return v[first], inv.reshape(-1, 3)


def tri_area(tris):
    t = np.asarray(tris, float)
    return 0.5 * np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1)


def topology(tris, tol=1e-3, area_eps=1e-8):
    """edge and face topology of a soup after welding"""
    tris = np.asarray(tris, float)
    V, F = weld(tris, tol)
    area = tri_area(tris)
    degen = (area < area_eps) | (F[:, 0] == F[:, 1]) | (F[:, 1] == F[:, 2]) | (F[:, 0] == F[:, 2])
    good = np.nonzero(~degen)[0]
    Fg = F[good]
    # duplicate faces (same vertex set): same winding = a true duplicate, opposite = a double-sided pair
    key = np.sort(Fg, 1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    dup_groups = collections.defaultdict(list)
    for f, g in zip(good, inv.reshape(-1)):
        if cnt[g] > 1:
            dup_groups[g].append(int(f))
    dup_same, dup_opp = [], []
    for g, fs in dup_groups.items():
        rot = [_canon(F[f]) for f in fs]
        if len(set(rot)) < len(rot):
            dup_same.append(fs)
        else:
            dup_opp.append(fs)
    # directed edges
    e = np.concatenate([Fg[:, [0, 1]], Fg[:, [1, 2]], Fg[:, [2, 0]]])
    fe = np.concatenate([good, good, good])
    und = np.sort(e, 1)
    uk, uinv, ucnt = np.unique(und, axis=0, return_inverse=True, return_counts=True)
    uinv = uinv.reshape(-1)
    open_e = np.nonzero(ucnt == 1)[0]
    nonman = np.nonzero(ucnt > 2)[0]
    # winding: on a 2-face edge the two directed copies must be opposite
    two = ucnt[uinv] == 2
    fwd = e[:, 0] < e[:, 1]
    s = np.zeros(len(uk), int)
    np.add.at(s, uinv[two], np.where(fwd[two], 1, -1))
    incons = np.nonzero((ucnt == 2) & (s != 0))[0]
    # components (faces joined by manifold edges)
    comp = _components(len(tris), uinv, fe, ucnt)
    comps = []
    for c in np.unique(comp[good]):
        fs = good[comp[good] == c]
        # (closed = every edge of the component used exactly twice by the component's own faces)
        mine = uinv[np.isin(fe, fs)]
        _, cc = np.unique(mine, return_counts=True)
        closed = bool(len(cc)) and bool(np.all(cc == 2))
        vol = signed_volume(tris[fs])
        comps.append({"faces": int(len(fs)), "closed": bool(closed), "volume": float(vol),
                      "inside_out": bool(closed and vol < -1e-9), "lo": tris[fs].reshape(-1, 3).min(0).tolist(),
                      "hi": tris[fs].reshape(-1, 3).max(0).tolist()})

    def emid(ix):
        return [V[uk[i]].mean(0).round(3).tolist() for i in ix]
    return {"faces": int(len(tris)), "verts": int(len(V)), "degenerate": int(degen.sum()),
            "degenerate_at": [tris[i].mean(0).round(3).tolist() for i in np.nonzero(degen)[0][:20]],
            "dup_faces": int(sum(len(x) - 1 for x in dup_same)), "double_sided": int(len(dup_opp)),
            "open_edges": int(len(open_e)), "open_at": emid(open_e[:40]),
            "nonmanifold_edges": int(len(nonman)), "nonmanifold_at": emid(nonman[:40]),
            "inconsistent_edges": int(len(incons)), "inconsistent_at": emid(incons[:40]),
            "components": comps, "inside_out": int(sum(c["inside_out"] for c in comps)),
            "closed_components": int(sum(c["closed"] for c in comps))}


def _canon(f):
    f = list(f)
    k = f.index(min(f))
    return tuple(f[k:] + f[:k])


def _components(nt, uinv, fe, ucnt):
    parent = np.arange(nt)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    order = np.argsort(uinv, kind="stable")
    ue, fu = uinv[order], fe[order]
    for k in range(1, len(ue)):
        if ue[k] == ue[k - 1] and ucnt[ue[k]] == 2:
            a, b = find(fu[k]), find(fu[k - 1])
            if a != b:
                parent[a] = b
    return np.array([find(i) for i in range(nt)])


def signed_volume(tris):
    t = np.asarray(tris, float)
    return float(np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6.0)


def inward_normals(tris, rays, sample=4000, eps=1e-3):
    """faces whose normal points INTO the solid: a ray from the face centre along its normal crosses the mesh an odd
    number of times (parity, up to 9 crossings).  Meaningful for watertight-ish parts; rays = rays.Rays(tris)"""
    tris = np.asarray(tris, float)
    n = len(tris)
    idx = np.arange(n) if n <= sample else np.random.default_rng(0).choice(n, sample, replace=False)
    c = tris[idx].mean(1)
    nn = np.cross(tris[idx, 1] - tris[idx, 0], tris[idx, 2] - tris[idx, 0])
    ln = np.linalg.norm(nn, axis=1)
    ok = ln > 1e-12
    idx, c, nn = idx[ok], c[ok], nn[ok] / ln[ok, None]
    o = c + nn * eps
    hits = np.zeros(len(idx), int)
    alive = np.ones(len(idx), bool)
    for _ in range(9):
        if not alive.any():
            break
        ai = np.nonzero(alive)[0]
        t, prim, _ = rays.cast(o[ai], nn[ai], 1e4)
        h = np.isfinite(t)
        hits[ai[h]] += 1
        o[ai[h]] = o[ai[h]] + nn[ai[h]] * (t[h, None] + eps)
        alive[ai[~h]] = False
    inward = idx[hits % 2 == 1]
    return {"sampled": int(len(idx)), "inward": int(len(inward)), "fraction": float(len(inward) / max(len(idx), 1)),
            "faces": inward.tolist()[:200]}


# ------------------------------------------------------------------ across groups
def duplicates_across(tris, group, tol=1e-3, facing="same"):
    """identical faces (welded at tol) in different groups: -> [(group a, group b, count, at)].  facing "same":
    the same winding (a true duplicate: z-fights); "opposite": back-to-back (coincident internal faces between two
    solids: hidden, but non-manifold once welded); "any" both"""
    V, F = weld(tris, tol)
    key = np.sort(F, 1)
    _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    inv = inv.reshape(-1)
    sel = np.nonzero(cnt[inv] > 1)[0]
    by = collections.defaultdict(list)
    for f in sel:
        by[inv[f]].append(f)
    pairs = collections.Counter()
    where = {}
    for fs in by.values():
        for x in range(len(fs)):
            for y in range(x + 1, len(fs)):
                fa, fb = fs[x], fs[y]
                if group[fa] == group[fb]:
                    continue
                same = _canon(F[fa]) == _canon(F[fb])
                if facing == "same" and not same or facing == "opposite" and same:
                    continue
                k = (int(min(group[fa], group[fb])), int(max(group[fa], group[fb])))
                pairs[k] += 1
                where.setdefault(k, np.asarray(tris[fa]).mean(0).round(3).tolist())
    return [(a, b, n, where[(a, b)]) for (a, b), n in pairs.most_common()]


def coplanar_overlaps(tris, group, d_eps=0.002, ang_eps=0.01, min_area=1e-4, same_facing=True, max_bucket=4000):
    """z-fighting candidates: faces of different groups in the same plane (normals within ang_eps, plane offsets
    within d_eps), facing the same way, whose areas overlap by > min_area m^2.  -> [(group a, group b, area, at)]"""
    from shapely.geometry import Polygon
    t = np.asarray(tris, float)
    nn = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    ln = np.linalg.norm(nn, axis=1)
    ok = ln > 1e-10
    nn = np.where(ok[:, None], nn / np.maximum(ln, 1e-12)[:, None], 0)
    d = np.einsum("ij,ij->i", nn, t[:, 0])
    if not same_facing:
        # (opposite-facing coplanar faces too: fold each normal to a canonical hemisphere first)
        ax = np.argmax(np.abs(nn), 1)
        sg = np.sign(nn[np.arange(len(nn)), ax])
        nn = nn * sg[:, None]
        d = d * sg
    qn = np.round(nn / ang_eps).astype(np.int64)
    qd = np.round(d / d_eps).astype(np.int64)
    keys = np.concatenate([qn, qd[:, None]], 1)
    _, inv, cnt = np.unique(keys[ok], axis=0, return_inverse=True, return_counts=True)
    oi = np.nonzero(ok)[0]
    inv = inv.reshape(-1)
    out = collections.defaultdict(float)
    where = {}
    order = np.argsort(inv, kind="stable")
    starts = np.searchsorted(inv[order], np.arange(len(cnt)))
    for b in np.nonzero(cnt > 1)[0]:
        fs = oi[order[starts[b]:starts[b] + cnt[b]]]
        gs = group[fs]
        if len(np.unique(gs)) < 2 or len(fs) > max_bucket:
            continue
        # 2D in the plane
        n0 = nn[fs[0]]
        ax = np.argmax(np.abs(n0))
        keep = [k for k in range(3) if k != ax]
        polys = [Polygon(t[f][:, keep]) for f in fs]
        boxes = np.array([p.bounds for p in polys])
        for a in range(len(fs)):
            for c in range(a + 1, len(fs)):
                if gs[a] == gs[c]:
                    continue
                if boxes[a, 0] >= boxes[c, 2] or boxes[c, 0] >= boxes[a, 2] or boxes[a, 1] >= boxes[c, 3] or \
                        boxes[c, 1] >= boxes[a, 3]:
                    continue
                ip = polys[a].intersection(polys[c])
                ar = ip.area
                if ar > min_area:
                    k = (int(min(gs[a], gs[c])), int(max(gs[a], gs[c])))
                    out[k] += ar
                    smp = where.setdefault(k, [])
                    if len(smp) < 4:
                        rp = ip.representative_point()
                        q = np.zeros(3)
                        q[keep[0]], q[keep[1]] = rp.x, rp.y
                        q[ax] = (d[fs[a]] - n0[keep[0]] * rp.x - n0[keep[1]] * rp.y) / n0[ax]
                        smp.append((q, nn[fs[a]].copy(), int(fs[a]), int(fs[c])))
    return sorted([(a, b, round(v, 4), where[(a, b)][0][0].round(3).tolist(), where[(a, b)])
                   for (a, b), v in out.items()], key=lambda r: -r[2])


def interpenetration(tris, group, rays, eps=2e-3, graze=0.05, passes=3, only=None, min_depth=0.02, ray_group=None):
    """edges of one group's faces piercing another group's faces by more than min_depth (each edge cast as a ray
    against the whole soup; hits on the edge's own group are stepped past): -> {(group a, group b): [count, at,
    samples [(point, pierced face's normal, pierced group)]]}; `only` limits the faces whose edges are cast"""
    t = np.asarray(tris, float)
    fi = np.arange(len(t)) if only is None else np.asarray(only)
    a = np.concatenate([t[fi, 0], t[fi, 1], t[fi, 2]])
    b = np.concatenate([t[fi, 1], t[fi, 2], t[fi, 0]])
    g = np.concatenate([group[fi]] * 3)
    d = b - a
    L = np.linalg.norm(d, axis=1)
    keep = L > 4 * eps
    a, d, L, g = a[keep], d[keep] / L[keep, None], L[keep], g[keep]
    o = a + d * eps
    rem = L - 2 * eps
    out = {}
    alive = np.arange(len(a))
    for _ in range(passes):
        if not len(alive):
            break
        tt, prim, n = rays.cast(o[alive], d[alive], rem[alive])
        h = np.isfinite(tt)
        hg = np.where(h, (group if ray_group is None else ray_group)[np.maximum(prim, 0)], -1)
        other = h & (hg != g[alive]) & (np.abs(np.einsum("ij,ij->i", n, d[alive])) > graze)
        for k in np.nonzero(other)[0]:
            q = alive[k]
            # (how far the edge runs on past the face it pierces, the shorter way: joints overlapping a few mm
            # at a seam are not interpenetration)
            tk = (L[q] - rem[q] - 2 * eps) + tt[k] + eps
            if min(tk, L[q] - tk) < min_depth:
                continue
            key = (int(min(g[q], hg[k])), int(max(g[q], hg[k])))
            p = o[q] + d[q] * tt[k]
            e = out.get(key)
            if e is None:
                e = out[key] = [0, p.round(3).tolist(), []]
            e[0] += 1
            if len(e[2]) < 4:
                e[2].append((p, rays.normal[prim[k]].astype(float), int(hg[k])))
        step = h & ~other
        o[alive[step]] = o[alive[step]] + d[alive[step]] * (tt[step, None] + eps)
        rem[alive[step]] -= tt[step] + eps
        alive = alive[step]
        alive = alive[rem[alive] > eps]
    return out


# ------------------------------------------------------------------ bounds
def bounds(tris, lo, hi, tol=0.005):
    """how far a mesh (T,3,3) leaves the box lo..hi, per side (m, > tol), and which triangles have a vertex outside"""
    v = np.asarray(tris, float).reshape(-1, 3)
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    if not len(v):
        return {"over": {}, "outside_tris": np.zeros(0, int), "mesh_lo": None, "mesh_hi": None}
    mlo, mhi = v.min(0), v.max(0)
    over = {}
    for k, ax in enumerate("xyz"):
        if lo[k] - mlo[k] > tol:
            over["-" + ax] = round(float(lo[k] - mlo[k]), 4)
        if mhi[k] - hi[k] > tol:
            over["+" + ax] = round(float(mhi[k] - hi[k]), 4)
    vt = np.asarray(tris, float)
    out = np.nonzero(((vt < lo - tol) | (vt > hi + tol)).any(axis=(1, 2)))[0]
    return {"over": over, "worst": max(over.values()) if over else 0.0, "outside_tris": out,
            "mesh_lo": mlo.round(4).tolist(), "mesh_hi": mhi.round(4).tolist()}


def tri_box_overlap(tris, lo, hi):
    """(T,) bool: triangle intersects the axis-aligned box (separating axis test, vectorised)"""
    t = np.asarray(tris, float)
    c = (np.asarray(lo) + np.asarray(hi)) * 0.5
    h = (np.asarray(hi) - np.asarray(lo)) * 0.5
    v = t - c
    ok = np.ones(len(t), bool)
    for k in range(3):
        ok &= (v[:, :, k].min(1) <= h[k]) & (v[:, :, k].max(1) >= -h[k])
    e = [v[:, 1] - v[:, 0], v[:, 2] - v[:, 1], v[:, 0] - v[:, 2]]
    n = np.cross(e[0], e[1])
    dn = np.abs(np.einsum("ij,ij->i", n, v[:, 0]))
    r = np.abs(n) @ h
    ok &= dn <= r + 1e-9
    I = np.eye(3)
    for ei in e:
        for k in range(3):
            ax = np.cross(I[k][None, :], ei)
            p = np.stack([np.einsum("ij,ij->i", ax, v[:, m]) for m in range(3)], 1)
            rr = np.abs(ax) @ h
            ok &= (p.min(1) <= rr + 1e-9) & (p.max(1) >= -rr - 1e-9)
    return ok


# ------------------------------------------------------------------ glb in
def read_glb_meshes(path):
    """{node name: (tris (T,3,3), materials (T,))} with the node hierarchy's transforms applied"""
    g = C.read_gltf(path)
    out = {}
    stack = [(r, np.eye(4)) for r in g["roots"]]
    while stack:
        n, M = stack.pop()
        nd = g["nodes"][n]
        M2 = M @ nd["matrix"]
        if nd["mesh"] is not None:
            prims = g["meshes"][nd["mesh"]]
            if prims:
                tr = np.concatenate([C.xf_pts(M2, t.reshape(-1, 3)).reshape(-1, 3, 3) for _, t in prims])
                mt = np.concatenate([np.full(len(t), m, object) for m, t in prims])
                out[nd["name"]] = (tr, mt)
        for c in nd["children"]:
            stack.append((c, M2))
    return out


class TriIndex:
    """a uniform grid over triangle AABBs (any soup): query(lo, hi) -> candidate triangle ids"""

    def __init__(self, tris, cell=3.0):
        t = np.asarray(tris, float)
        self.cell = cell
        lo = np.floor(t.min(1) / cell).astype(np.int64)
        hi = np.floor(t.max(1) / cell).astype(np.int64)
        self.tlo, self.thi = t.min(1), t.max(1)
        keys, ids = [], []
        span = hi - lo + 1
        simple = (span <= 1).all(1)
        si = np.nonzero(simple)[0]
        keys.append(lo[si])
        ids.append(si)
        for k in np.nonzero(~simple)[0]:
            g = np.stack(np.meshgrid(*[np.arange(lo[k, a], hi[k, a] + 1) for a in range(3)], indexing="ij"), -1)
            g = g.reshape(-1, 3)
            keys.append(g)
            ids.append(np.full(len(g), k))
        K = np.concatenate(keys)
        I = np.concatenate(ids)
        code = self._code(K)
        o = np.argsort(code, kind="stable")
        self.code, self.ids = code[o], I[o]

    @staticmethod
    def _code(K):
        K = K + 2 ** 20
        return (K[:, 0] << 42) | (K[:, 1] << 21) | K[:, 2]

    def query(self, lo, hi):
        a = np.floor(np.asarray(lo) / self.cell).astype(np.int64)
        b = np.floor(np.asarray(hi) / self.cell).astype(np.int64)
        g = np.stack(np.meshgrid(*[np.arange(a[k], b[k] + 1) for k in range(3)], indexing="ij"), -1).reshape(-1, 3)
        c = self._code(g)
        l = np.searchsorted(self.code, c, "left")
        r = np.searchsorted(self.code, c, "right")
        if not len(c):
            return np.zeros(0, int)
        ids = np.unique(np.concatenate([self.ids[x:y] for x, y in zip(l, r)])) if (r > l).any() else np.zeros(0, int)
        if not len(ids):
            return ids
        ok = np.all(self.thi[ids] >= np.asarray(lo) - 1e-9, 1) & np.all(self.tlo[ids] <= np.asarray(hi) + 1e-9, 1)
        return ids[ok]


def coplanar_overlaps_cells(tris, group, cell=1.5, **kw):
    """coplanar_overlaps over a big soup: the plane buckets split by the faces' centroids on a `cell` grid (overlaps
    between faces whose centroids fall in different cells are missed: fine for kit-sized faces)"""
    t = np.asarray(tris, float)
    c = np.floor(t.mean(1) / cell).astype(np.int64)
    out = collections.defaultdict(float)
    where = {}
    # (run per coarse block so the plane keys stay small)
    code = (c[:, 0] + 2 ** 20) * 2 ** 42 + (c[:, 1] + 2 ** 20) * 2 ** 21 + (c[:, 2] + 2 ** 20)
    o = np.argsort(code, kind="stable")
    sc = code[o]
    bounds_ = np.nonzero(np.diff(sc))[0] + 1
    starts = np.r_[0, bounds_]
    ends = np.r_[bounds_, len(sc)]
    for s0, e0 in zip(starts, ends):
        if e0 - s0 < 2:
            continue
        ids = o[s0:e0]
        if len(np.unique(group[ids])) < 2:
            continue
        for a, b, ar, at, smp in coplanar_overlaps(t[ids], group[ids], **kw):
            out[(a, b)] += ar
            w = where.setdefault((a, b), [])
            w.extend(smp[:4 - len(w)])
    return sorted([(a, b, round(v, 4), where[(a, b)][0][0].round(3).tolist(), where[(a, b)])
                   for (a, b), v in out.items()], key=lambda r: -r[2])


def visible(points, normals, rays, group_of_prim, allowed, back=0.3, eps=0.004):
    """(n,) bool: is the point on a face visible from in front of it (along its normal)?  The view ray from
    p + n * back toward p may only meet faces of the `allowed` groups (per point, a set) before it gets there"""
    p = np.asarray(points, float).reshape(-1, 3)
    n = np.asarray(normals, float).reshape(-1, 3)
    n = n / np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
    out = np.ones(len(p), bool)
    o = p + n * back
    rem = np.full(len(p), back - eps)
    alive = np.arange(len(p))
    for _ in range(4):
        if not len(alive):
            break
        t, prim, _ = rays.cast(o[alive], -n[alive], rem[alive])
        h = np.isfinite(t)
        go = []
        for k in np.nonzero(h)[0]:
            q = alive[k]
            if int(group_of_prim[prim[k]]) in allowed[q]:
                go.append(k)
            else:
                out[q] = False
        go = np.array(go, int)
        if not len(go):
            break
        q = alive[go]
        o[q] = o[q] - n[q] * (t[go, None] + 1e-3)
        rem[q] -= t[go] + 1e-3
        alive = q[rem[q] > 0]
    return out
