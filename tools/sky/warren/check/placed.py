# placement-level coincident floors: per cell, the up-facing top surfaces of every placed piece at the same height
import sys, json, numpy as np, collections, kitglb
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__file__), '..'))
import lods
iid = sys.argv[1]
side, civ, x0, z0, cell, nx, nz, ids, recs = lods.read_warren(iid)
k = kitglb.read('/home/deck/goblin-engine/godot_project/remake/sky/warrens/kit/kit.glb')
tops = {}
for pid in set(ids):
    if pid not in k: continue
    T = np.concatenate([t for m, t in k[pid][0]])
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); a = np.linalg.norm(n, axis=1)
    up = (a > 1e-8) & (n[:, 1] / np.maximum(a, 1e-9) > 0.99)
    # up faces covering most of the cell's centre region, by height
    ys = collections.Counter(np.round(T[up][:, 0, 1], 3))
    area = collections.defaultdict(float)
    for t, aa in zip(T[up], a[up] / 2):
        area[round(float(t[0, 1]), 3)] += aa
    tops[pid] = {y: ar for y, ar in area.items() if ar > 1.0}
cnt = collections.Counter(); ex = {}
by = collections.defaultdict(list)
for r in recs:
    pid = ids[r['p']]
    if pid not in tops or not tops[pid]: continue
    fl = int(r['rf'])
    if (fl >> 4) & 3: continue                       # cell-mounted only
    y0 = 3.2 * int(r['k']) + 0.8 * (fl >> 6)
    for y, ar in tops[pid].items():
        by[(int(r['i']), int(r['j']), round(y0 + y, 2))].append((pid, ar, fl & 4))
for key, lst in by.items():
    if len(lst) > 1:
        names = tuple(sorted(p for p, a, d in lst))
        cnt[names] += 1; ex[names] = key
print(iid, "cells with 2+ pieces' floors at one height:", sum(cnt.values()))
for n, c in cnt.most_common(15): print("  ", c, n, "e.g. cell/y", ex[n])
