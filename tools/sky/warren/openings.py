"""openings.py -- does the player fit?  (2026-10-15, "the player character does not fit through a lot of the arches")

The player is a capsule (radius 0.18, height 1.45); every way it walks must leave a clear box of at least
CLEAR_W x CLEAR_H (1.0 m x 2.2 m) -- from centre to centre of two walk cells joined on the walk graph, and from the
step outside each door 0.5 m into the house through its door piece.  The box starts STEP_LIFT over the walking surface
(the paving, steps and kerbs under it are the floor, not an obstacle) and is tested against the placed pieces' real
triangles (kit.glb; pieces.json "pass" clear boxes / "collide": "frame" boxes once the KIT publishes them).

  scan(L, recs, pieces)  -> {"edges": [(c, n, [record index])], "doors": [(lot id, [record index])]}
  fix(L, recs, pieces)   -> recs with the obstructions cleared (decor dropped, portals swapped for a wider piece
                            or dropped), and the stats
"""
import math
import os

import numpy as np

CLEAR_W = 1.0
CLEAR_H = 2.2
STEP_LIFT = 0.35
KIT_GLB = os.path.join(os.path.dirname(__file__), "..", "..", "..", "godot_project", "remake", "sky", "warrens", "kit",
                       "kit.glb")
LEAF = ("wk_frame", "wk_metal", "wk_glass")
EPS = 0.02             # (an opening exactly CLEAR_W x CLEAR_H passes)
REMOVABLE = ("overlay", "decor", "sign", "cell")    # (what may simply be taken out of the way)
# dressing placed as a structure (plan_piece shares): kept while it only overhangs, but when it still BLOCKS the
# walk after the swaps it goes too (SKY-079 2026-10-16: a windmill on a green choke cell cut 14 doors off).  A real
# landmark (a pagoda, a tower) is never in this set.
LAST_RESORT = ("windmill_round",)
FLOORISH = ("ground", "stair", "water_edge", "interior", "ceiling", "slab", "bridge")   # (a bridge is walked on)
FACE = {0: (0, -1), 1: (-1, 0), 2: (0, 1), 3: (1, 0)}
_geo = {}
_door_geo = {}
_framed = set()


def _box_tris(lo, hi):
    """a box as 12 triangles"""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], float)
    f = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1), (3, 2, 6), (3, 6, 7), (0, 3, 7), (0, 7, 4),
         (1, 5, 6), (1, 6, 2)]
    return v[np.array(f)]


def geometry(pieces=None):
    """the pieces' collision as triangles: pieces.json "frame" boxes (KIT, 2026-10-15) where a piece has them, else
    its mesh (its leaf, studs and glass left out of a door's)"""
    if pieces is not None and not _framed:
        geometry()
        for pid, v in pieces.items():
            if v.get("frame"):
                T = np.concatenate([_box_tris(np.array(a, float), np.array(b, float)) for a, b in v["frame"]])
                _geo[pid] = T
                _door_geo[pid] = T
                _framed.add(pid)
    if not _geo:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "check"))
        import kitglb
        for pid, v in kitglb.read(KIT_GLB).items():
            # (a door piece's leaf, handle and glass open: the way in is the frame's opening)
            doorish = any(w in pid for w in ("door", "shopfront", "portal", "gate", "noren"))
            tris = [t for m, t in v[0] if not (doorish and m in LEAF)]
            if tris:
                _geo[pid] = np.concatenate(tris).astype(np.float64)
            # (the piece seen as a doorway: only its wall and its frame trim -- the leaf, studs and carving swing open)
            dt = [t for m, t in v[0] if m in ("wk_wall", "wk_trim")]
            if dt:
                _door_geo[pid] = np.concatenate(dt).astype(np.float64)
    return _geo


def _box_hits(tri, lo, hi):
    """triangles (N,3,3) against the box lo..hi: a bool per triangle (separating axis test)"""
    if len(tri) == 0:
        return np.zeros(0, bool)
    c = (lo + hi) / 2.0
    h = (hi - lo) / 2.0
    v = tri - c
    # the box's axes
    mn, mx = v.min(axis=1), v.max(axis=1)
    hit = np.all((mn <= h) & (mx >= -h), axis=1)
    if not hit.any():
        return hit
    v = v[hit]
    idx = np.nonzero(hit)[0]
    e = [v[:, 1] - v[:, 0], v[:, 2] - v[:, 1], v[:, 0] - v[:, 2]]
    ok = np.ones(len(v), bool)
    # the triangle's normal
    nrm = np.cross(e[0], e[1])
    d = np.einsum("ij,ij->i", nrm, v[:, 0])
    r = np.abs(nrm) @ h
    ok &= np.abs(d) <= r + 1e-9
    # the nine cross axes
    for ei in e:
        for k in range(3):
            ax = np.zeros_like(ei)
            # axis = unit_k x ei
            if k == 0:
                ax[:, 1], ax[:, 2] = -ei[:, 2], ei[:, 1]
            elif k == 1:
                ax[:, 0], ax[:, 2] = ei[:, 2], -ei[:, 0]
            else:
                ax[:, 0], ax[:, 1] = -ei[:, 1], ei[:, 0]
            p = np.einsum("nij,nj->ni", v, ax)
            rr = np.abs(ax) @ h
            ok &= ~((p.min(axis=1) > rr + 1e-9) | (p.max(axis=1) < -rr - 1e-9))
    out = np.zeros(len(tri), bool)
    out[idx[ok]] = True
    return out


class Scene:
    """the placed pieces' triangles in the world, by cell"""

    def __init__(self, L, recs, pieces):
        self.L = L
        self.recs = recs
        self.pieces = pieces
        self.geo = geometry(pieces)
        self.by = {}
        self.cache = {}
        for n, r in enumerate(recs):
            if pieces.get(r[0], {}).get("kind") in FLOORISH or r[0] not in self.geo:
                continue
            self.by.setdefault((r[1], r[2]), []).append(n)

    def world(self, n, door=False):
        t = self.cache.get((n, door))
        if t is not None:
            return t
        kid, i, j, lv, kr, flags, mnt = self.recs[n][:7]
        T = (_door_geo.get(kid, self.geo[kid]) if door else self.geo[kid]).copy()
        if mnt == 1:
            T[..., 2] += 1.5
        elif mnt == 2:
            T[..., 0] += 1.5
            T[..., 2] += 1.5
        th = kr * math.pi / 2
        cs, sn = math.cos(th), math.sin(th)
        x = T[..., 0] * cs + T[..., 2] * sn
        z = -T[..., 0] * sn + T[..., 2] * cs
        if flags & 4:
            y0 = float(self.L.ground[i, j])
        else:
            y0 = 3.2 * lv + 0.8 * ((flags >> 4) & 3)
        cx, cz = (i + 0.5) * 3.0, (j + 0.5) * 3.0       # (cell-local world: x along i, z along j, 3 m cells)
        W = np.stack([x + cx, T[..., 1] + y0, z + cz], axis=-1)
        self.cache[(n, door)] = (W, W.reshape(-1, 3).min(0), W.reshape(-1, 3).max(0))
        return self.cache[(n, door)]

    def blockers(self, lo, hi, cells, door_face=None):
        lo = lo + np.array([EPS, 0.0, EPS])
        hi = hi - np.array([EPS, EPS, EPS])
        out = []
        for c in cells:
            for n in self.by.get(c, ()):
                r = self.recs[n]
                W, a, b = self.world(n, door_face is not None and (r[1], r[2], r[4], r[6]) == door_face)
                if np.any(b < lo) or np.any(a > hi):
                    continue
                if _box_hits(W, lo, hi).any():
                    out.append(n)
        return out


def _near(c):
    return [c] + [(c[0] + d[0], c[1] + d[1]) for d in FACE.values()]


def scan(L, recs, pieces, surf_h):
    """surf_h(c, rot) -> the walking surface height at cell c's edge toward FACE[rot] (or None); the cell centre
    via rot None.  Edges between joined walk cells and the doors."""
    S = Scene(L, recs, pieces)
    res = {"edges": [], "doors": []}
    hw = CLEAR_W / 2
    done = set()
    for c in L.phys_reached:
        for rot, d in FACE.items():
            n = (c[0] + d[0], c[1] + d[1])
            if n not in L.phys_reached or (n, c) in done:
                continue
            done.add((c, n))
            ys = [surf_h(c, None), surf_h(c, rot), surf_h(n, None)]
            if any(y is None for y in ys):
                continue
            ax = 0 if d[0] else 2
            cc = np.array([(c[0] + 0.5) * 3.0, 0.0, (c[1] + 0.5) * 3.0])
            nc = np.array([(n[0] + 0.5) * 3.0, 0.0, (n[1] + 0.5) * 3.0])
            lo, hi = np.minimum(cc, nc), np.maximum(cc, nc)
            other = 2 - ax
            lo[other] -= hw
            hi[other] += hw
            lo[ax] += 0.2                                  # (not into the cells beyond)
            hi[ax] -= 0.2
            lo[1] = max(ys) + STEP_LIFT - 0.0
            hi[1] = min(ys) + CLEAR_H
            if hi[1] - lo[1] < CLEAR_H - STEP_LIFT - 1.7:   # (a stair: the box rides its slope, split in two)
                pass
            bl = S.blockers(lo, hi, set(_near(c) + _near(n)))
            # (a door piece on the crossed face: a closed door between two ways, walk-through only into a room)
            for k in list(S.by.get(c, ())) + list(S.by.get(n, ())):
                r = recs[k]
                if pieces.get(r[0], {}).get("pass_kind") == "door" and r[6] == 1 and (
                        ((r[1], r[2]) == c and r[4] == (rot + 2) & 3) or ((r[1], r[2]) == n and r[4] == rot)):
                    bl.append(k)
            if bl:
                res["edges"].append((c, n, bl))
    for lot in L.lots:
        if not lot.get("door"):
            continue
        c, rot = lot["door"]
        d = FACE[rot]
        m = (c[0] + d[0], c[1] + d[1])
        y = 3.2 * lot["door_k"]
        mc = np.array([(m[0] + 0.5) * 3.0, 0.0, (m[1] + 0.5) * 3.0])
        hc = np.array([(c[0] + 0.5) * 3.0, 0.0, (c[1] + 0.5) * 3.0])
        face = (mc + hc) / 2
        inner = face + (hc - mc) / 3.0 * 0.5             # (0.5 m into the house)
        lo, hi = np.minimum(mc, inner), np.maximum(mc, inner)
        ax = 0 if d[0] else 2
        other = 2 - ax
        lo[other] -= hw
        hi[other] += hw
        lo[ax] += 0.1 if mc[ax] < inner[ax] else 0.0
        lo[1], hi[1] = y + STEP_LIFT, y + CLEAR_H
        bl = S.blockers(lo, hi, {c, m}, door_face=(c[0], c[1], (rot + 2) & 3, 1))
        if bl:
            res["doors"].append((lot["id"], bl))
            if os.environ.get("WALK_DEBUG") and len(res["doors"]) <= 3:
                print("DOOR BOX", lot["id"], lo.round(2), hi.round(2))
    return res


def occupied(L, recs, pieces, surf_h):
    """walk cells whose middle a structure stands in (a temple, a tower foot): the landmark's footprint, off the walk"""
    S = Scene(L, recs, pieces)
    out = set()
    for c in list(L.W):
        y = surf_h(c, None)
        if y is None:
            continue
        x, z = (c[0] + 0.5) * 3.0, (c[1] + 0.5) * 3.0
        bl = S.blockers(np.array([x - 0.5, y + STEP_LIFT, z - 0.5]), np.array([x + 0.5, y + CLEAR_H, z + 0.5]), _near(c))
        if any(pieces.get(recs[n][0], {}).get("kind") not in REMOVABLE + ("wall", "passage", "edge", "corner") for n in bl):
            out.add(c)
    return out


def prune_graph(L, recs, pieces, blocked_ground, landmark):
    """the runtime's walk graph (units.walk_graph) against the same collision: ground edges the ground check found
    blocked (and a landmark's footprint) go; a roof cell a solid piece stands on (a shack, a tank, an aerial) leaves
    the graph; a roof-to-roof step, plank or level edge whose clear box something cuts (a parapet, a tank) goes, and
    its ladder or planks with it.  Returns (recs, stats)."""
    S = Scene(L, recs, pieces)
    nodes, edges, index = L.walk["nodes"], L.walk["edges"], L.walk_index
    key_of = {v: k for k, v in index.items()}
    hw = CLEAR_W / 2
    dead = set()
    for n, key in key_of.items():
        if key[0] == "g" and (key[1], key[2]) in landmark:
            dead.add(n)
        elif key[0] == "r":
            i, j = key[1], key[2]
            y = nodes[n][1]
            x, z = (i + 0.5) * 3.0, (j + 0.5) * 3.0
            if S.blockers(np.array([x - hw, y + STEP_LIFT, z - hw]), np.array([x + hw, y + CLEAR_H, z + hw]), _near((i, j))):
                dead.add(n)
    bg = set(blocked_ground) | set((b, a) for a, b in blocked_ground)
    keep, cut = [], []
    for e, (a, b) in enumerate(edges):
        ka, kb = key_of.get(a), key_of.get(b)
        bad = a in dead or b in dead
        if not bad and ka and kb and ka[0] == "g" and kb[0] == "g" and ((ka[1], ka[2]), (kb[1], kb[2])) in bg:
            bad = True
        if not bad and ka and kb and ka[0] == "r" and kb[0] == "r" and nodes[a][1] == nodes[b][1]:
            # (a level roof crossing, over one cell or a plank's gap: the box from centre to centre)
            p, q = np.array([(ka[1] + 0.5) * 3.0, 0, (ka[2] + 0.5) * 3.0]), np.array([(kb[1] + 0.5) * 3.0, 0, (kb[2] + 0.5) * 3.0])
            lo, hi = np.minimum(p, q), np.maximum(p, q)
            ax = 0 if ka[1] != kb[1] else 2
            lo[2 - ax] -= hw
            hi[2 - ax] += hw
            lo[ax] += 0.2
            hi[ax] -= 0.2
            lo[1], hi[1] = nodes[a][1] + STEP_LIFT, nodes[a][1] + CLEAR_H
            cells = set()
            for c in ((ka[1], ka[2]), (kb[1], kb[2])):
                cells.update(_near(c))
            for s in range(1, 3):
                cells.update(_near((ka[1] + (kb[1] - ka[1]) * s // 3, ka[2] + (kb[2] - ka[2]) * s // 3)))
            if S.blockers(lo, hi, cells):
                bad = True
        (cut if bad else keep).append(e)
    gone_extra = set()
    for e in cut:
        x = L.edge_extra.get(e)
        if x:
            for t in ([x[1]] if x[0] == "ladder" else x[1]):
                gone_extra.add((x[0] if x[0] == "ladder" else "bridge_plank", t[0], t[1], t[2]))
    L.walk["edges"] = [edges[e] for e in keep]
    for n in dead:
        nodes[n][3] = "blocked"
    recs = [r for r in recs if not ((("ladder" if "ladder" in r[0] else "bridge_plank" if "plank" in r[0] else ""),
                                     r[1], r[2], r[3]) in gone_extra)]
    return recs, {"graph_edges_cut": len(cut), "graph_nodes_blocked": len(dead), "ladders_planks_removed": len(gone_extra)}


def is_door_piece(L, r, lid, pieces=None):
    """the record is the wall piece on the lot's door face"""
    c, rot = L.lots[lid]["door"]
    if pieces is not None and pieces.get(r[0], {}).get("kind") not in ("wall", "passage"):
        return False
    return (r[1], r[2]) == tuple(c) and r[6] == 1 and r[4] == (rot + 2) & 3


def fix(L, recs, pieces, surf_h):
    """clear what stands in the way: decoration goes, a too-small portal / arch / door piece is swapped for the plain
    one of its family (a wider opening) or goes; returns (recs, stats)"""
    before = scan(L, recs, pieces, surf_h)
    nb_e, nb_d = len(before["edges"]), len(before["doors"])
    culprits = {}
    for _, _, bl in before["edges"]:
        for n in bl:
            culprits[n] = culprits.get(n, 0) + 1
    door_piece = set()
    for lid, bl in before["doors"]:
        c, rot = L.lots[lid]["door"]
        for n in bl:
            culprits[n] = culprits.get(n, 0) + 1
            if is_door_piece(L, recs[n], lid, pieces):
                door_piece.add(n)                          # (the door's own piece, whatever the KIT calls it)
    kinds = {}
    kit_small = {}
    kept = {}
    recs = list(recs)
    gone = set()
    swaps = 0
    for n in culprits:
        kid = recs[n][0]
        kind = pieces.get(kid, {}).get("kind")
        kinds[kid] = kinds.get(kid, 0) + 1
        if n in door_piece or (kind in ("wall", "passage", "edge", "corner") and ("door" in kid or "portal" in kid)):
            kit_small[kid] = kit_small.get(kid, 0) + 1     # (the KIT's door opening itself is short: reported, kept)
            continue
        if kind in ("wall", "passage", "edge", "corner"):
            t = "_t" if kid.endswith("_t") else "_k"
            if "door" in kid or "portal" in kid:
                alt = "wall_door" + t
            elif "arch" in kid or "gate" in kid or kind == "passage":
                alt = "wall_arch_round" + t
            elif "shopfront" in kid:
                alt = "wall_shopfront_a" + t
            else:
                alt = "wall_window_m" + t                  # (a ground-floor balcony or jetty over the walk)
            for a in (alt, alt[:-2] + ("_k" if t == "_t" else "_t"), "wall_plain" + t):
                if a in pieces and a != kid:
                    recs[n] = (a,) + tuple(recs[n][1:])
                    swaps += 1
                    break
            continue                                      # (a wall is never just taken away: no holes)
        if kind == "roof":
            # (a roof whose eaves hang over the way at head height: the plain one inside its own cell)
            for a in ("roof_tin", "roof_terrace"):
                if a in pieces and a != kid:
                    recs[n] = (a,) + tuple(recs[n][1:])
                    swaps += 1
                    break
            continue
        if kind not in REMOVABLE:
            kept[kid] = kept.get(kid, 0) + 1              # (a tower, a roof, a bridge: structure stays, reported)
            continue
        gone.add(n)
    recs = [r for n, r in enumerate(recs) if n not in gone]
    after = scan(L, recs, pieces, surf_h)
    # what still blocks after the swaps (the plain piece too small as well): it goes
    still = set(n for _, _, bl in after["edges"] for n in bl) | set(n for _, bl in after["doors"] for n in bl)
    still = set(n for n in still if pieces.get(recs[n][0], {}).get("kind") in REMOVABLE or recs[n][0] in LAST_RESORT)
    if still:
        recs = [r for n, r in enumerate(recs) if n not in still]
        after = scan(L, recs, pieces, surf_h)
    stats = {"edges_blocked_before": nb_e, "doors_blocked_before": nb_d, "pieces_swapped": swaps,
             "pieces_removed": len(gone) + len(still), "edges_blocked_after": len(after["edges"]),
             "doors_blocked_after": len(after["doors"]),
             "kit_door_too_small": kit_small, "structure_kept": kept,
             "culprits": sorted(kinds.items(), key=lambda kv: -kv[1])[:10],
             "still_blocking": sorted(set(recs[n][0] for _, _, bl in after["edges"] for n in bl) |
                                     set(recs[n][0] for _, bl in after["doors"] for n in bl))[:10]}
    return recs, stats
