# coplanar, overlapping, differently-coloured triangles inside each kit piece (z-fighting within a piece)
import sys, numpy as np, kitglb, collections
from shapely.geometry import Polygon
k = kitglb.read('/home/deck/goblin-engine/godot_project/remake/sky/warrens/kit/kit.glb')
EPS = float(sys.argv[1]) if len(sys.argv) > 1 else 0.004
res = []
for name, (prims, *_ ) in k.items():
    tris = []; mats = []
    for pi, (m, t) in enumerate(prims):
        tris.append(t); mats += [pi] * len(t)
    T = np.concatenate(tris); M = np.array(mats)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); a = np.linalg.norm(n, axis=1)
    ok = a > 1e-8; n[ok] /= a[ok, None]
    d = (n * T[:, 0]).sum(1)
    # bucket by normal (to 0.05) and offset (to EPS); also neighbours in offset
    key = collections.defaultdict(list)
    for i in np.nonzero(ok)[0]:
        nn = tuple(np.round(n[i] * 20).astype(int))
        key[(nn, int(np.floor(d[i] / EPS)))].append(i)
    area = 0.0; pairs = set()
    for (nn, dk), lst in key.items():
        cand = lst + key.get((nn, dk + 1), [])
        # also opposite-facing coplanar faces don't fight (back-face culled) -- only same normal
        if len(cand) < 2: continue
        nv = np.array(nn, float); nv /= np.linalg.norm(nv)
        u = np.cross(nv, [0, 0, 1] if abs(nv[2]) < 0.9 else [1, 0, 0]); u /= np.linalg.norm(u); v = np.cross(nv, u)
        polys = {i: Polygon([(p @ u, p @ v) for p in T[i]]) for i in cand}
        for x in range(len(cand)):
            for y in range(x + 1, len(cand)):
                i, j = cand[x], cand[y]
                if abs(d[i] - d[j]) > EPS: continue
                pi, pj = polys[i], polys[j]
                if not pi.is_valid or not pj.is_valid: continue
                ov = pi.intersection(pj).area
                if ov > 1e-4:
                    area += ov; pairs.add((prims[M[i]][0], prims[M[j]][0]))
    if area > 0.002:
        res.append((round(area, 3), name, sorted(pairs)[:4]))
res.sort(reverse=True)
print(len(res), "pieces with coplanar overlaps (area m2, piece, material pairs):")
for r in res[:60]: print(" ", r)
