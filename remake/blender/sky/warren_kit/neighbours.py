"""neighbours.py -- the lattice audit: z-fight candidates BETWEEN pieces that touch in the warren lattice (run after a
build; prints the pairs).  Same piece repeated along a row (x +3), stacked a storey (y +3.2), a wall bay beside a corner
piece at its end, an edge piece on a wall's top, ground pieces side by side and under kerbs and skirts."""
import sys

import geom
from flicker import _plane, _tri_arrays
from flicker import find as _find


def find(a, b, min_area=0.002):
    """cross-piece pairs, less those lying in a storey line (y 0 / 3.2, facing up or down): those faces are sealed
    between the two stacked storeys or the corner and its bay, never seen"""
    A, _, _ = _tri_arrays(a)
    out = []
    for i, j, g, ov in _find(a, b, min_area=min_area):
        n, d, _ = _plane(A[i])
        if abs(abs(n[1]) - 1.0) < 1e-3 and min(abs(abs(d) - 0.0), abs(abs(d) - 3.2), abs(abs(d) - 6.4)) < 0.03:
            continue
        out.append((i, j, g, ov))
    return out
from pieces import PIECES


def built(pid, cache={}):
    if pid not in cache:
        import flicker
        cache[pid] = flicker.finish(pid, PIECES[pid], PIECES[pid]["build"]())[0]
    return cache[pid]


def moved(m, dx=0.0, dy=0.0, dz=0.0):
    out = geom.Mesh()
    out.add(m, geom.move(dx, dy, dz))
    return out


def audit(ids=None):
    ids = ids or list(PIECES)
    out = []
    from flicker import WIDE
    walls = [p for p in ids if PIECES[p]["group"] in ("wall", "edge") and p not in WIDE]
    corners = [p for p in PIECES if PIECES[p]["group"] == "corner"]
    grounds = [p for p in ids if PIECES[p]["kind"] in ("ground",) and PIECES[p]["span"] == [1, 1]]
    for p in walls:                                             # a row of the same bay, and a storey stacked
        m = built(p)
        lo, hi = m.bounds()
        tests = [("row", moved(m, 3.0))]
        if PIECES[p]["group"] == "wall" and hi[1] <= 3.3:          # (edges and multi-storey pieces do not stack)
            tests.append(("stack", moved(m, 0.0, 3.2)))
        for tag, n in tests:
            h = find(m, n, min_area=0.002)
            if h:
                out.append((p, tag, p, len(h), round(min(x[2] for x in h), 3)))
    plain = built("wall_plain_k")
    for c in corners:                                           # a corner at a bay's +X end
        h = find(moved(built(c), 1.5), plain, min_area=0.002)
        if h:
            out.append((c, "corner@bay", "wall_plain_k", len(h), round(min(x[2] for x in h), 3)))
    for g in grounds:                                           # paving side by side, and its skirt / kerbs
        m = built(g)
        h = find(m, moved(m, 3.0), min_area=0.002)
        if h:
            out.append((g, "row", g, len(h), round(min(x[2] for x in h), 3)))
        for k, km in (("kerb_straight", moved(built("kerb_straight"), 0.0, 0.0, 1.5)), ("kerb_post", moved(built("kerb_post"), 1.5, 0.0, 1.5)),
                      ("pave_skirt", built("pave_skirt"))):
            if k == g or (k == "pave_skirt" and g.endswith("_skirt")):
                continue
            h = find(m, km, min_area=0.002)
            if h:
                out.append((g, "with", k, len(h), round(min(x[2] for x in h), 3)))
    return out


if __name__ == "__main__":
    for r in audit(sys.argv[1:] or None):
        print(r)
