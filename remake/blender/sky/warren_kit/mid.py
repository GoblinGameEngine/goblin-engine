"""mid.py -- the warren kit's MID level of detail: for every piece a lighter mesh in the same frame and slots, for
medium distances (between the full pieces near the player and the LOD1 boxes far off).

Two ways, by the piece's group:
  * wall / edge pieces (seen from the lane): a RELIEF IMPOSTOR. The full piece, its thin and tiny parts dropped
    (bars, ribs, studs, letters, cables, lattice sticks), is rasterized from the front into a 0.1 m height field of
    (slot, depth); the field is cleaned and greedy-merged into rectangles; each rectangle is a front quad at its depth
    with skirts down to its lower neighbours. So openings become inset dark panes (glass at its depth), balconies /
    oriels / roshans / jharokhas become plain boxes of their colour, signs flat lit panels.
  * cell / corner pieces (roofs, crowns, towers, decor): COMPONENT SIMPLIFICATION. Thin and tiny components are
    dropped; turned (lathe / cylinder) components are re-turned with 6-8 sides and half their rings; the rest kept.

A piece whose full mesh is already cheap (<= KEEP tris), or whose simplification saves too little, uses its full mesh
as its mid (pieces.json "mid" then points into kit.glb).
"""
import math

import numpy as np

from geom import Mesh, SLOTS

KEEP = 120            # pieces this cheap are their own mid
CELL = 0.15           # relief grid (m)
ZQ = 0.08             # relief depth quantum (m)


# ------------------------------------------------------------------ components
def _components(m):
    """[(slot, [tri, ...])]: triangles of one slot sharing vertices"""
    out = []
    for s in SLOTS:
        ts = m.tris[s]
        if not ts:
            continue
        parent = list(range(len(ts)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        seen = {}
        for i, t in enumerate(ts):
            for p in t[:3]:
                k = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
                if k in seen:
                    ra, rb = find(i), find(seen[k])
                    if ra != rb:
                        parent[ra] = rb
                else:
                    seen[k] = i
        groups = {}
        for i in range(len(ts)):
            groups.setdefault(find(i), []).append(ts[i])
        out += [(s, g) for g in groups.values()]
    return out


def _dims(tris):
    a = np.array([p for t in tris for p in t[:3]])
    lo, hi = a.min(axis=0), a.max(axis=0)
    return lo, hi, np.sort(hi - lo)


def _area(tris):
    return sum(0.5 * float(np.linalg.norm(np.cross(np.subtract(t[1], t[0]), np.subtract(t[2], t[0])))) for t in tris)


def _keep(slot, tris, thin, small):
    """drop bars / ribs / studs / letters / thin rods and cables (however they sag); keep panes and lit panels big enough
    to read"""
    lo, hi, d = _dims(tris)
    if slot not in ("glass",) and (slot not in ("wall", "roof", "ground") or len(tris) <= 2):
        if _area(tris) / max(d[2], 1e-6) < thin * 1.2:                   # mean girth: a rod, a cable, a strip
            return False
    if slot in ("glass", "emissive"):
        return d[1] >= 0.14 and d[2] >= 0.2
    if slot in ("wall", "roof", "ground"):
        return d[2] >= small
    return d[1] >= thin and d[2] >= small


def _filtered(m, thin, small):
    out = Mesh()
    for slot, tris in _components(m):
        if _keep(slot, tris, thin, small):
            out.tris[slot] += tris
    return out


# ------------------------------------------------------------------ relief impostor (walls, edges)
def relief(m, thin=0.09, small=0.16, cell=None, budget=0):
    """budget: tris of the piece's big flat layers (the holed wall body, an arch band, a frame) kept VERBATIM so their
    curves stay true; the rest becomes the height-field relief"""
    global CELL
    keep_cell = CELL
    CELL = cell or keep_cell
    try:
        return _relief(m, thin, small, budget)
    finally:
        CELL = keep_cell


def _flat_layer(tris):
    """a component lying in one facade plane (its lane-facing faces all at about the same depth)"""
    zs = []
    for t in tris:
        n = np.cross(np.subtract(t[1], t[0]), np.subtract(t[2], t[0]))
        ln = np.linalg.norm(n)
        if ln > 1e-9 and n[2] / ln > 0.9:
            zs += [t[0][2], t[1][2], t[2][2]]
    return bool(zs) and max(zs) - min(zs) < 0.03


def _relief(m, thin, small, budget):
    src = _filtered(m, thin, small)
    verb, used = [], 0
    if budget:
        comps = sorted(_components(src), key=lambda c: -_area(c[1]))
        for slot, ct in comps:
            if slot == "glass" or len(ct) > 90 or used + len(ct) > budget:
                continue
            if _dims(ct)[2][2] >= 0.6 and _flat_layer(ct):
                verb.append((slot, ct))
                used += len(ct)
    vids = {id(t) for _, ct in verb for t in ct}
    tris = [(s, t) for s in SLOTS for t in src.tris[s]]
    if not tris:
        return Mesh()
    allp = np.array([p for _, t in tris for p in t[:3]])
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    zfloor = lo[2]
    nx = max(1, int(math.ceil((hi[0] - lo[0]) / CELL - 1e-6)))
    ny = max(1, int(math.ceil((hi[1] - lo[1]) / CELL - 1e-6)))
    zbuf = np.full((nx, ny), -1e9)
    sbuf = np.full((nx, ny), -1, dtype=int)
    vbuf = np.zeros((nx, ny), bool)
    vzbuf = np.full((nx, ny), -1e9)                            # the verbatim layers' depth under every cell
    shade = {}
    cx = lo[0] + (np.arange(nx) + 0.5) * CELL
    cy = lo[1] + (np.arange(ny) + 0.5) * CELL
    for s, t in tris:
        a, b, c = (np.array(p, float) for p in t[:3])
        n = np.cross(b - a, c - a)
        ln = np.linalg.norm(n)
        if ln < 1e-9 or n[2] / ln < 0.05:
            continue                                            # only what faces the lane
        shade.setdefault(s, []).append(t[3])
        x0, x1 = min(a[0], b[0], c[0]), max(a[0], b[0], c[0])
        y0, y1 = min(a[1], b[1], c[1]), max(a[1], b[1], c[1])
        i0, i1 = max(0, int((x0 - lo[0]) / CELL - 0.5)), min(nx - 1, int((x1 - lo[0]) / CELL + 0.5))
        j0, j1 = max(0, int((y0 - lo[1]) / CELL - 0.5)), min(ny - 1, int((y1 - lo[1]) / CELL + 0.5))
        if i1 < i0 or j1 < j0:
            continue
        X, Y = np.meshgrid(cx[i0:i1 + 1], cy[j0:j1 + 1], indexing="ij")
        d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(d) < 1e-12:
            continue
        l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / d
        l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / d
        l3 = 1 - l1 - l2
        inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        Z = l1 * a[2] + l2 * b[2] + l3 * c[2]
        if id(t) in vids:
            vs = vzbuf[i0:i1 + 1, j0:j1 + 1]
            vw = inside & (Z > vs)
            vs[vw] = Z[vw]
        sub = zbuf[i0:i1 + 1, j0:j1 + 1]
        win = inside & (Z > sub + 1e-6)
        sub[win] = Z[win]
        sbuf[i0:i1 + 1, j0:j1 + 1][win] = SLOTS.index(s)
        vbuf[i0:i1 + 1, j0:j1 + 1][win] = id(t) in vids
    zq = np.where(sbuf >= 0, np.round(zbuf / ZQ) * ZQ, -1e9)
    near = (sbuf >= 0) & ~vbuf & (np.abs(zq - vzbuf) < 0.03)      # a relief rect would lie ON a verbatim layer: lift it
    zq[near] = vzbuf[near] + 0.03
    key = np.where(sbuf >= 0, sbuf * 100000 + np.round((zq - zfloor) * 1000).astype(int), -1)     # (depth in mm)
    # clean: a cell whose value hardly repeats round it takes its neighbourhood's
    k2 = key.copy()
    for i in range(nx):
        for j in range(ny):
            if key[i, j] < 0:
                continue
            nb = key[max(0, i - 1):i + 2, max(0, j - 1):j + 2].ravel()
            if (nb == key[i, j]).sum() <= 2:
                vals, cnt = np.unique(nb[nb >= 0], return_counts=True)
                if cnt.max() >= 4:
                    k2[i, j] = vals[cnt.argmax()]
    key = k2
    key[vbuf] = -2                                             # verbatim layers: no rects, but their depth bounds skirts
    out = Mesh()
    for slot, ct in verb:
        out.tris[slot] += ct
    sh = {s: float(np.mean(v)) for s, v in shade.items()}

    def kslot(k):
        return SLOTS[k // 100000]

    def kz(k):
        return zfloor + (k % 100000) / 1000.0
    done = np.zeros((nx, ny), bool)
    for i in range(nx):                                        # greedy rectangles
        for j in range(ny):
            k = key[i, j]
            if k < 0 or done[i, j]:
                continue
            w = 1
            while i + w < nx and key[i + w, j] == k and not done[i + w, j]:
                w += 1
            h = 1
            while j + h < ny and all(key[i + u, j + h] == k and not done[i + u, j + h] for u in range(w)):
                h += 1
            done[i:i + w, j:j + h] = True
            x0, x1 = lo[0] + i * CELL, lo[0] + (i + w) * CELL
            y0, y1 = lo[1] + j * CELL, lo[1] + (j + h) * CELL
            z = kz(k)
            s = kslot(k)
            if s == "glass":
                out.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), s, 1.0, uv=[(0, 1), (1, 1), (1, 0), (0, 0)])
            else:
                out.quad_facing((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), (0, 0, 1), s, sh.get(s, 1.0))

    def zat(i, j, si, sj):
        if 0 <= i < nx and 0 <= j < ny:
            if key[i, j] >= 0:
                return kz(key[i, j])
            if key[i, j] == -2:
                return float(zbuf[i, j])
        return max(zfloor, float(vzbuf[si, sj]))               # (off the field: down to the layer under it, not past)
    # skirts: down from each cell to a lower neighbour, merged into runs along the edge
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        runs = {}
        for i in range(nx):
            for j in range(ny):
                k = key[i, j]
                if k < 0:
                    continue
                z, zn = kz(k), zat(i + di, j + dj, i, j)
                if z <= zn + 1e-6:
                    continue
                if di:
                    line, pos = i, j
                else:
                    line, pos = j, i
                runs.setdefault((line, round(z, 4), round(zn, 4), kslot(k)), []).append(pos)
        for (line, z, zn, s), ps in runs.items():
            ps.sort()
            start = prev = ps[0]
            for p in ps[1:] + [None]:
                if p is not None and p == prev + 1:
                    prev = p
                    continue
                if di:
                    x = lo[0] + (line + (1 if di > 0 else 0)) * CELL
                    ya, yb = lo[1] + start * CELL, lo[1] + (prev + 1) * CELL
                    out.quad_facing((x, ya, zn), (x, yb, zn), (x, yb, z), (x, ya, z), (di, 0, 0), s, sh.get(s, 1.0) * 0.85)
                else:
                    y = lo[1] + (line + (1 if dj > 0 else 0)) * CELL
                    xa, xb = lo[0] + start * CELL, lo[0] + (prev + 1) * CELL
                    out.quad_facing((xa, y, zn), (xb, y, zn), (xb, y, z), (xa, y, z), (0, dj, 0), s, sh.get(s, 1.0) * 0.85)
                if p is not None:
                    start = prev = p
    return out


# ------------------------------------------------------------------ component simplification (cells, corners)
def _returned(slot, tris):
    """a turned component (lathe / cylinder about a vertical axis) re-turned with fewer sides and rings, else None"""
    pts = np.array([p for t in tris for p in t[:3]])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
    r = np.hypot(pts[:, 0] - cx, pts[:, 2] - cz)
    ang = np.sort(np.arctan2(pts[:, 2] - cz, pts[:, 0] - cx)[r > 0.01])
    if len(ang) < 6 or np.max(np.diff(np.concatenate([ang, ang[:1] + 2 * np.pi]))) > 1.2:
        return None                                              # not all the way round: a flat arch, a half shell
    ys = np.round(pts[:, 1], 3)
    prof = []
    for y in np.unique(ys):
        rr = r[ys == y]
        if rr.max() - rr.min() > 0.03 + 0.03 * rr.max():
            return None
        prof.append((float(rr.mean()) if rr.max() > 0.01 else 0.0, float(y)))
    if len(prof) < 2 or len(tris) < 20:
        return None
    if len(prof) > 3:
        prof = prof[:1] + prof[1:-1][::2] + prof[-1:]
    n = 8 if max(p[0] for p in prof) > 0.9 else 6
    out = Mesh()
    out.lathe(prof, slot, n=n, cx=cx, cz=cz, shade=float(np.mean([t[3] for t in tris])))
    return out if out.count() < len(tris) else None


def _decimate(slot, tris, ratio):
    """quadric decimation of one component (its vertices welded) to about ratio of its triangles"""
    import fast_simplification
    keys, pts, faces = {}, [], []
    for t in tris:
        f = []
        for p in t[:3]:
            k = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
            if k not in keys:
                keys[k] = len(pts)
                pts.append(k)
            f.append(keys[k])
        if len(set(f)) == 3:
            faces.append(f)
    if len(faces) < 16:
        return None
    P, F = fast_simplification.simplify(np.array(pts, float), np.array(faces, np.int64), target_reduction=1.0 - ratio)
    out = Mesh()
    shade = float(np.mean([t[3] for t in tris]))
    for a, b, c in F:
        pa, pb, pc = (tuple(float(v) for v in P[x]) for x in (a, b, c))
        if np.linalg.norm(np.cross(np.subtract(pb, pa), np.subtract(pc, pa))) > 1e-8:
            out.tri(pa, pb, pc, slot, shade)
    if not 0 < out.count() < len(tris):
        return None
    lo0, hi0, d0 = _dims(tris)                                  # reject a shredded result: the silhouette (bounds) or
    lo1, hi1, d1 = _dims([t for s in SLOTS for t in out.tris[s]])   # the skin (area) must survive
    if np.any(np.abs(np.subtract(lo1, lo0)) > 0.12 * max(d0[2], 0.3)) or np.any(np.abs(np.subtract(hi1, hi0)) > 0.12 * max(d0[2], 0.3)):
        return None
    if _area([t for s in SLOTS for t in out.tris[s]]) < 0.75 * _area(tris):
        return None
    return out


def simplify3d(m, thin=0.06, small=0.2, ratio=0.3):
    out = Mesh()
    for slot, tris in _components(m):
        if not _keep(slot, tris, thin, small):
            continue
        rt = _returned(slot, tris)
        if rt is None and len(tris) > 16 and slot != "glass":
            rt = _decimate(slot, tris, ratio)
        if rt is not None:
            out.add(rt)
        else:
            out.tris[slot] += tris
    return out


# ------------------------------------------------------------------ stairs: their ramps, made solid
def stair_mid(m, quads):
    """a stair at mid range: its walking ramps as slabs (two-sided tops, sides down to the flight's foot) in the stair's
    main slot -- the treads read as a slope, as the player walks them"""
    cnt = {s: len(m.tris[s]) for s in SLOTS}
    slot = max(cnt, key=cnt.get)
    out = Mesh()
    for q in quads:
        a, b, c, d = (tuple(p) for p in q)
        out.quad_facing(a, b, c, d, (0, 1, 0), slot)
        foot = min(p[1] for p in q) - 0.25
        out.quad_facing(tuple(np.add(a, (0, -0.06, 0))), tuple(np.add(b, (0, -0.06, 0))), tuple(np.add(c, (0, -0.06, 0))), tuple(np.add(d, (0, -0.06, 0))), (0, -1, 0), slot, 0.6)
        if len(quads) <= 3:
            for p0, p1 in ((a, b), (c, d)):                     # the flight's two sides
                n = np.cross(np.subtract(p1, p0), (0, 1, 0))
                ctr = np.mean([a, b, c, d], axis=0)
                mid = np.add(p0, p1) / 2
                if np.dot(n, mid - ctr) < 0:
                    n = -n
                out.quad_facing(p0, p1, (p1[0], foot, p1[2]), (p0[0], foot, p0[2]), tuple(n), slot, 0.8)
    return out


# ------------------------------------------------------------------ the mid of a piece
# ------------------------------------------------------------------ the mid of a piece
def mid_mesh(pid, d, m, ramps=None):
    """(mesh, how): the piece's mid mesh -- or (None, "full") when its full mesh is already cheap enough to be its own
    mid, or (empty Mesh, "none") when nothing of it should draw at mid range (thin overlays: cables, wires, bars)"""
    n = m.count()
    if ramps:
        return stair_mid(m, ramps), "ramp"
    if n <= KEEP:
        return None, "full"
    cands = []
    if d["group"] in ("wall", "edge"):
        bud = int(0.1 * n)
        cands.append(relief(m, budget=bud))
        for kw in (dict(thin=0.14, small=0.3), dict(thin=0.14, small=0.3, cell=0.2), dict(thin=0.2, small=0.4, cell=0.25),
                   dict(thin=0.25, small=0.5, cell=0.3, budget=0)):
            if min(q.count() for q in cands) <= 0.2 * n:
                break
            kw.setdefault("budget", bud)
            cands.append(relief(m, **kw))
    else:                                                       # (walls and edges: reliefs only -- decimating a holed
        for kw in (dict(), dict(thin=0.12, small=0.4, ratio=0.25), dict(thin=0.18, small=0.6, ratio=0.25)):  # slab tears it;
                                                                # below a quarter, decimation shreds domes and lintels)
            if cands and min(q.count() for q in cands) <= 0.2 * n:
                break
            cands.append(simplify3d(m, **kw))
    best = min(cands, key=lambda q: q.count())
    if best.count() == 0:
        return Mesh(), "none"
    if best.count() > 0.85 * n:
        return None, "full"
    return best, "mid"
