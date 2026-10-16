"""passes.py -- the walk-through openings of the kit's wall and edge pieces, and their collision as simple boxes.

The piece is looked at down its own Z axis on a 5 cm grid: a cell is CLEAR when nothing covers it front to back, a
DOOR cell when only a leaf covers it (a door, a grille, a screen, a curtain: slots frame / accent / metal / screen /
fabric / emissive), else SOLID.  The opening is the clear (+ door) region standing on the floor (its foot no higher
than 0.25 m: a threshold step); its PASS box is the widest rectangle in it at least 2.2 m tall (or the biggest one when
none is), and the FRAME is the solid region greedy-merged into boxes, each as deep as the masonry behind it.

  analyse(m) -> {"pass": [lo, hi] | None, "kind": "open" | "door" | None, "clear": [w, h], "foot": y, "frame": [[lo, hi], ...]}
"""
import math

import numpy as np

from geom import SLOTS

G = 0.05
LEAF = {"frame", "accent", "metal", "screen", "fabric", "emissive", "accent2"}
MIN_W, MIN_H, MAX_STEP = 1.0, 2.2, 0.25


def _passable(m):
    """the leaf triangles a walker may pass (they will not collide): door leaves (big thin panels) and bars, grilles and
    screens (thin strips) -- not timber columns or posts (they stay in the frame)"""
    from mid import _components
    ids = set()
    for s, ts in _components(m):
        if s not in LEAF:
            continue
        a = np.array([p for t in ts for p in t[:3]])
        dx, dy, dz = a.max(axis=0) - a.min(axis=0)
        if (dz <= 0.12 and dx >= 0.35 and dy >= 1.2) or min(dx, dz) <= 0.06 or max(dx, dy, dz) < 0.3:   # (panels, bars, fittings)
            ids |= {id(t) for t in ts}
    return ids


def _raster(m, x0, x1, y0, y1, zmin=-1e9, zmax=1e9, all_solid=False):
    passable = set() if all_solid else _passable(m)
    nx, ny = int(round((x1 - x0) / G)), int(round((y1 - y0) / G))
    cx = x0 + (np.arange(nx) + 0.5) * G
    cy = y0 + (np.arange(ny) + 0.5) * G
    solid = np.zeros((nx, ny), bool)
    leaf = np.zeros((nx, ny), bool)
    zlo = np.full((nx, ny), 1e9)
    zhi = np.full((nx, ny), -1e9)
    for s in SLOTS:
        for t in m.tris[s]:
            a, b, c = (np.array(p, float) for p in t[:3])
            if not zmin <= (a[2] + b[2] + c[2]) / 3 <= zmax:
                continue
            n = np.cross(b - a, c - a)
            ln = np.linalg.norm(n)
            if ln < 1e-12 or abs(n[2]) / ln < 0.05:
                continue                                        # (side faces do not stop a ray down Z)
            xs, ys = [a[0], b[0], c[0]], [a[1], b[1], c[1]]
            i0, i1 = max(0, int((min(xs) - x0) / G)), min(nx - 1, int((max(xs) - x0) / G))
            j0, j1 = max(0, int((min(ys) - y0) / G)), min(ny - 1, int((max(ys) - y0) / G))
            if i1 < i0 or j1 < j0:
                continue
            X, Y = np.meshgrid(cx[i0:i1 + 1], cy[j0:j1 + 1], indexing="ij")
            d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(d) < 1e-12:
                continue
            l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / d
            l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / d
            l3 = 1 - l1 - l2
            ins = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            Z = l1 * a[2] + l2 * b[2] + l3 * c[2]
            sl = (slice(i0, i1 + 1), slice(j0, j1 + 1))
            if id(t) in passable:
                leaf[sl] |= ins
            else:
                solid[sl] |= ins
                zlo[sl] = np.where(ins, np.minimum(zlo[sl], Z), zlo[sl])
                zhi[sl] = np.where(ins, np.maximum(zhi[sl], Z), zhi[sl])
    return cx, cy, solid, leaf, zlo, zhi


def _best_rect(free, cy, foot_max):
    """the widest free rectangle standing on the floor (its foot row at or below foot_max) at least MIN_H tall, else
    the biggest by area: (i0, i1, j0, j1)"""
    nx, ny = free.shape
    best, best_area = None, 0.0
    for j0 in range(ny):
        if cy[j0] < 0.075:
            continue                                            # (the floor is y 0: what hangs below it -- corbels,
                                                                #  decks -- never stands in a walker's way)
        if cy[j0] - G / 2 > foot_max:
            break
        h = np.zeros(nx, int)                                   # clear run up from row j0, per column
        for i in range(nx):
            k = j0
            while k < ny and free[i, k]:
                k += 1
            h[i] = k - j0
        for i0 in range(nx):
            mh = 10 ** 9
            for i1 in range(i0, nx):
                if h[i1] == 0:
                    break
                mh = min(mh, h[i1])
                w, hh = (i1 - i0 + 1) * G, mh * G
                score = (1e6 if hh >= MIN_H else 0.0) + (w * 1e3 if hh >= MIN_H else w * hh)
                if score > best_area:
                    best_area, best = score, (i0, i1, j0, j0 + mh - 1)
        if best is not None and best_area >= 1e6:
            break                                              # (the lowest floor row with a tall enough rect wins)
    return best


SLAB = 0.15        # the wall slab's depth limit: what stands further out (balconies, rails, decks) is a projection


def _boxes(solid, zlo, zhi, x0, y0, cut=None):
    """solid cells (5 cm) -> boxes on a 10 cm grid (a coarse cell solid if any of its four is, unless it touches the cut
    rect (i0, i1, j0, j1) in fine cells), merged in the face's plane, each as deep as its masonry"""
    keep = solid.copy()
    nx2, ny2 = keep.shape[0] // 2, keep.shape[1] // 2
    k2 = keep[:nx2 * 2, :ny2 * 2].reshape(nx2, 2, ny2, 2).any(axis=(1, 3))
    if cut is not None:
        i0, i1, j0, j1 = cut
        for ii in range(nx2):
            for jj in range(ny2):
                if k2[ii, jj] and i0 <= 2 * ii + 1 and 2 * ii <= i1 and j0 <= 2 * jj + 1 and 2 * jj <= j1:
                    k2[ii, jj] = False
    zl = np.where(solid, zlo, 1e9)[:nx2 * 2, :ny2 * 2].reshape(nx2, 2, ny2, 2).min(axis=(1, 3))
    zh = np.where(solid, zhi, -1e9)[:nx2 * 2, :ny2 * 2].reshape(nx2, 2, ny2, 2).max(axis=(1, 3))
    G2 = 2 * G
    boxes = []
    done = np.zeros_like(k2)
    for j in range(ny2):
        for i in range(nx2):
            if not k2[i, j] or done[i, j]:
                continue
            w = 1
            while i + w < nx2 and k2[i + w, j] and not done[i + w, j]:
                w += 1
            h = 1
            while j + h < ny2 and all(k2[i + u, j + h] and not done[i + u, j + h] for u in range(w)):
                h += 1
            done[i:i + w, j:j + h] = True
            sub = k2[i:i + w, j:j + h]
            za, zb = float(np.min(zl[i:i + w, j:j + h][sub])), float(np.max(zh[i:i + w, j:j + h][sub]))
            if za > 1e8 or zb < -1e8:
                za, zb = -0.3, 0.0
            if zb - za < 0.05:
                za -= 0.05
            boxes.append([[round(x0 + i * G2, 3), round(y0 + j * G2, 3), round(za, 3)], [round(x0 + (i + w) * G2, 3), round(y0 + (j + h) * G2, 3), round(zb, 3)]])
    return boxes


def _projections(m, pas):
    """the parts standing out of the wall slab (centred beyond SLAB): a box each (their own bounds) -- so a balcony
    stays a deck, a rail and posts with room to stand between them; nothing smaller than 15 cm; none entering the pass"""
    from mid import _components
    out = []
    for s, ts in _components(m):
        a = np.array([p for t in ts for p in t[:3]])
        lo, hi = a.min(axis=0), a.max(axis=0)
        if (lo[2] + hi[2]) / 2 <= SLAB or max(hi - lo) < 0.15:
            continue
        lo = lo.copy()
        if pas is not None:
            pl, ph = np.array(pas[0]), np.array(pas[1])
            if np.all(lo < ph - 1e-3) and np.all(hi > pl + 1e-3):
                lo[2] = max(lo[2], ph[2] + 0.005)              # (stepped out of the pass, in front of it)
                if lo[2] >= hi[2]:
                    continue
        if hi[2] - lo[2] < 0.04:
            lo[2] -= 0.02
            hi = hi.copy()
            hi[2] += 0.02
        out.append([[round(float(v), 3) for v in lo], [round(float(v), 3) for v in hi]])
    return out


def analyse(m, group="wall"):
    lo, hi = m.bounds()
    x0, x1 = -1.5, 1.5
    y0, y1 = -1.0, max(3.2, min(hi[1], 6.4))
    cx, cy, solid, leaf, zlo, zhi = _raster(m, x0, x1, y0, y1, zmax=SLAB)
    out = {"pass": None, "kind": None, "clear": [0.0, 0.0], "foot": None, "frame": []}
    r = _best_rect(~solid, cy, MAX_STEP)
    cut = None
    if r is not None:
        i0, i1, j0, j1 = r
        w, h = (i1 - i0 + 1) * G, (j1 - j0 + 1) * G
        foot = max(0.0, cy[j0] - G / 2 - G)                     # (the first row above the floor: its foot is y 0)
        h = h + (cy[j0] - G / 2 - foot)
        if w >= 0.6 and h >= 1.6:
            cut = r
            zs = zlo[solid]
            zb = float(zs.min()) if zs.size else -0.6
            out.update(kind="door" if bool(leaf[i0:i1 + 1, j0:j1 + 1].any()) else "open", clear=[round(w, 2), round(h, 2)],
                       foot=round(float(foot), 2))
            out["pass"] = [[round(x0 + i0 * G, 3), round(foot, 3), round(zb - 0.05, 3)], [round(x0 + (i1 + 1) * G, 3), round(foot + h, 3), SLAB]]
            cut = (i0, i1, int(round((foot - y0) / G)), j1)        # (the pass from its true foot: no box under it)
    frame = _boxes(solid, zlo, zhi, x0, y0, cut)
    frame += _projections(m, out["pass"])                    # balconies, rails, decks, posts: a box per part
    out["frame"] = frame
    return out
