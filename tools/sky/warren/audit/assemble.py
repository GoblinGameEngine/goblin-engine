#!/usr/bin/env python3
"""assemble.py -- an island's geometry, offline, as the game builds it.

  render     every placement's kit mesh (pieces.json + kit/kit.glb, FORMAT.md v3 transforms)
  collision  exactly sky_warren.gd's _load_pieces / _merge_chunk / _floor_slabs / _box_faces (per chunk, whole-cell
             floors merged per height into 0.4 m slabs, vertices snapped to 1 mm), plus the island's own bodies:
             the deck (rock.glb "deck-col", tucked 0.1 m under the paving within 2.2 m as _tuck_deck does), the rim
             fence (sky_island.gd _build_fence boxes) and the bridges (sky_bridge.gd: every mesh solid, stowed pose)

Collision triangle sources (Geo.csrc): >= 0 the placement's record index, SLAB -1, DECK -2, FENCE -3, BRIDGE -4.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/assemble.py SKY-022 [--no-cache]     (prints counts)

Cached per island in reference/tmp/audit/cache/<id>.npz (keyed by the inputs' mtimes)."""
import hashlib
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

SLAB, DECK, FENCE, BRIDGE, LARK = -1, -2, -3, -4, -5
SRC_NAME = {SLAB: "floor slab", DECK: "deck", FENCE: "fence", BRIDGE: "bridge", LARK: "parked lark"}
ASM_VERSION = 8
RAMP_UNDER = 0.2           # sky_warren.gd _ramp_under: every ramp quad is a slab this thick under its top
LARK_BOX = ((-0.95, 0.0, -2.35), (0.95, 2.75, 2.35))   # sky_skiff (fleet/sky_skiff.blueprint.json: +-2.3 long, cabin 2.7)

_KIT = [None]


def kit():
    if _KIT[0] is None:
        _KIT[0] = C.Kit()
    return _KIT[0]


class Geo:
    """an assembled island (see the module doc)"""

    def __init__(self, **kw):
        self.__dict__.update(kw)

    # a record's id / description
    def pid(self, n):
        return self.ids[int(self.recs["p"][n])]

    def cell(self, n):
        r = self.recs[n]
        return int(r["i"]), int(r["j"]), int(r["k"])

    def describe(self, src, at=None):
        """a collision source -> a short label (a slab or the deck: which cell's floor piece made it)"""
        src = int(src)
        if src >= 0:
            return self.pid(src)
        if src == SLAB and at is not None:
            n = self.floor_piece_at(at)
            return "slab:" + (self.pid(n) if n is not None else "?")
        return SRC_NAME.get(src, "?")

    def what(self, prim, at=None):
        """a collision triangle -> (label, record index or None): slabs resolve to the floor piece of the slab's
        cell nearest the point"""
        prim = int(prim)
        if prim < 0:
            return None, None
        src = int(self.csrc[prim])
        if src >= 0:
            return self.pid(src), src
        if src == SLAB:
            sl = self.slabs[self.cslab[prim]]
            _, ycm, i0, i1, j0, j1 = [int(v) for v in sl]
            if at is None:
                at = self.ctri[prim].mean(0)
            i = min(max(int(np.floor((at[0] - self.x0) / C.CELL)), i0), i1 - 1)
            j = min(max(int(np.floor((at[2] - self.z0) / C.CELL)), j0), j1 - 1)
            m = (self.fkeys[:, 0] == i) & (self.fkeys[:, 1] == j) & (self.fkeys[:, 2] == ycm)
            n = int(self.frec[m][0]) if m.any() else None
            if n is not None and n < 0:
                return "slab:room floor", None          # (sky_warren.gd _room_floors: an entered room's floor)
            return "slab:" + (self.pid(n) if n is not None else "?"), n
        return SRC_NAME.get(src, "?"), None

    def label(self, prim, at=None):
        return self.what(prim, at)[0]

    def floor_piece_at(self, p):
        """the record whose whole-cell floor makes the slab top nearest below/at p"""
        i = int(np.floor((p[0] - self.x0) / C.CELL))
        j = int(np.floor((p[2] - self.z0) / C.CELL))
        m = (self.fkeys[:, 0] == i) & (self.fkeys[:, 1] == j)
        if not m.any():
            return None
        ys = self.fkeys[m, 2] / 100.0
        k = int(np.argmin(np.abs(ys - p[1])))
        return int(self.frec[m][k])

    def ij(self, p):
        return int(np.floor((p[0] - self.x0) / C.CELL)), int(np.floor((p[2] - self.z0) / C.CELL))


def _inputs(iid, wdir):
    fs = [os.path.join(wdir, iid + ".bin.gz"), os.path.join(wdir, iid + ".json"), C.PIECES_JSON, C.KIT_GLB,
          C.ISLANDS_JSON, C.BRIDGES_JSON, os.path.abspath(__file__), os.path.join(C.HERE, "common.py")]
    h = hashlib.sha1(("v%d|" % ASM_VERSION + wdir).encode())
    for f in fs:
        h.update(("%s %s" % (f, os.path.getmtime(f) if os.path.exists(f) else 0)).encode())
    return h.hexdigest()[:16]


def build(iid, wdir=None, cache=True, render=True, bridges_down=False):
    wdir = wdir or C.WR
    key = _inputs(iid, wdir)
    cpath = os.path.join(C.CACHE, "%s_%s.npz" % (iid, "w" if wdir == C.WR else hashlib.sha1(wdir.encode()).hexdigest()[:8]))
    W = C.read_warren(iid, wdir)
    isl = C.island(iid)
    deck = C.Deck(isl)
    P = C.placements(W, deck)
    if cache and os.path.exists(cpath):
        z = np.load(cpath, allow_pickle=False)
        if str(z["key"]) == key and (not render or z["rtri"].size):
            d = {k: z[k] for k in z.files if k != "key"}
            return Geo(iid=iid, W=W, isl=isl, deck=deck, P=P, ids=W["ids"], recs=W["recs"], x0=W["x0"], z0=W["z0"],
                       nx=W["nx"], nz=W["nz"], **d)
    t0 = time.time()
    K = kit()
    col = collision(W, P, K, deck, isl, bridges_down)
    rend = render_tris(W, P, K) if render else {"rtri": np.zeros((0, 3, 3), np.float32), "rsrc": np.zeros(0, np.int32),
                                                 "rslot": np.zeros(0, np.int16)}
    d = dict(col, **rend)
    d["build_s"] = np.float64(time.time() - t0)
    if cache:
        os.makedirs(C.CACHE, exist_ok=True)
        np.savez(cpath, key=key, **d)
    return Geo(iid=iid, W=W, isl=isl, deck=deck, P=P, ids=W["ids"], recs=W["recs"], x0=W["x0"], z0=W["z0"],
               nx=W["nx"], nz=W["nz"], **d)


SLOTS = ["wall", "trim", "frame", "glass", "screen", "roof", "metal", "fabric", "emissive", "tile", "water", "ground",
         "plant", "accent", "accent2", ""]


LEAF_Z = (-0.14, -0.08)     # sky_warren.gd: a shut door's leaf, in the face piece's frame
LEAF_LAP = 0.03


def door_state(W):
    """sky_warren.gd _door_prep: the door records by face, from both sides (a face is open if any record there is
    entered), and the entered doors' cells"""
    st = {}
    entered = []
    for (unit, i, j, lv, rot, en) in W["doors"]:
        rot &= 3
        di, dj = C.roundi(np.sin(rot * np.pi / 2)), C.roundi(np.cos(rot * np.pi / 2))
        for key in ((i, j, lv, rot), (i + di, j + dj, lv, (rot + 2) % 4)):
            st[key] = st.get(key, False) or bool(en)
        if en:
            entered.append((i, j, lv))
    return st, entered


def leaves(W, P, K):
    """{record: (lo, hi)}: the shut door leaves sky_warren.gd _door_leaf adds (a pass_kind "door" piece on a face
    mount whose face has no entered door record -- none at all included)"""
    st, _ = door_state(W)
    out = {}
    recs = W["recs"]
    for n in range(len(recs)):
        pid = W["ids"][recs["p"][n]]
        spec = K.P.get(pid, {})
        if spec.get("pass_kind") != "door" or P["mount"][n] != 1:
            continue
        if st.get((int(recs["i"][n]), int(recs["j"][n]), int(recs["k"][n]), int(recs["rf"][n]) & 3), False):
            continue
        ps = spec.get("pass")
        if not ps or len(ps) < 2:
            continue
        out[n] = ((ps[0][0] - LEAF_LAP, 0.0, LEAF_Z[0]), (ps[1][0] + LEAF_LAP, ps[1][1] + LEAF_LAP, LEAF_Z[1]))
    return out


def render_tris(W, P, K):
    ids = W["ids"]
    pk = W["recs"]["p"]
    out, src, slot = [], [], []
    for p in np.unique(pk):
        pid = ids[p]
        if pid not in K.mesh or not len(K.mesh[pid]):
            continue
        idx = np.nonzero(pk == p)[0]
        m = K.mesh[pid].reshape(-1, 3)
        w = C.apply_many(P, idx, m).reshape(len(idx), -1, 3, 3)
        flip = P["mirror"][idx] == 1
        if flip.any():
            w[flip] = w[flip][:, :, [0, 2, 1]]
        out.append(w.reshape(-1, 3, 3).astype(np.float32))
        nt = len(K.mesh[pid])
        src.append(np.repeat(idx.astype(np.int32), nt))
        sl = np.array([SLOTS.index(s[3:]) if s.startswith("wk_") and s[3:] in SLOTS else len(SLOTS) - 1
                       for s in K.slot[pid]], np.int16)
        slot.append(np.tile(sl, len(idx)))
    for n, (lo, hi) in leaves(W, P, K).items():           # (the shut leaves are drawn too)
        t = _box_world(P, n, lo, hi)
        out.append(t.astype(np.float32))
        src.append(np.full(len(t), n, np.int32))
        slot.append(np.full(len(t), SLOTS.index("frame"), np.int16))
    if not out:
        return {"rtri": np.zeros((0, 3, 3), np.float32), "rsrc": np.zeros(0, np.int32), "rslot": np.zeros(0, np.int16)}
    return {"rtri": np.concatenate(out), "rsrc": np.concatenate(src), "rslot": np.concatenate(slot)}


def collision(W, P, K, deck, isl, bridges_down=False):
    ids = W["ids"]
    recs = W["recs"]
    tris, src = [], []
    fkeys, frec = [], []
    slabs = []                                   # [chunk, ycm, i0, i1 (excl), j0, j1 (excl)]
    slab_tris = []
    rules = [K.rule.get(p) for p in ids]
    whole = [K.whole_cell(p) if p in K.aabb else False for p in ids]
    leaf = leaves(W, P, K)
    _, entered = door_state(W)
    for ch, (ci, cj, first, cnt) in enumerate(W["table"]):
        floors = {}                              # (i, j, ycm) -> first record
        for n in range(first, first + cnt):
            r = rules[recs["p"][n]]
            if r is None or not r[0]:
                continue
            mode, data = r
            if mode == "ramp":
                q = _nomirror(P, n, data.reshape(-1, 3)).reshape(-1, 4, 3)
                t = np.concatenate([C.quads_tris(q), _ramp_under(q)])
            elif mode == "top":
                if P["deck"][n]:
                    continue                     # (DECK: the deck's own collision is the surface there)
                q = _nomirror(P, n, data)
                if whole[recs["p"][n]] and P["mount"][n] == 0:
                    k = (int(recs["i"][n]), int(recs["j"][n]), C.roundi(q[0, 1] * 100.0))
                    floors.setdefault(k, n)
                    continue
                t = C.quads_tris(q[None])
            elif mode == "mesh":
                t = _nomirror(P, n, data.reshape(-1, 3)).reshape(-1, 3, 3)
            elif mode == "frames":
                t = np.concatenate([_box_world(P, n, lo, hi) for lo, hi in data]) if data else np.zeros((0, 3, 3))
            else:                                # box
                t = _box_world(P, n, data[0], data[1])
            tris.append(t)
            src.append(np.full(len(t), n, np.int32))
            if n in leaf:                        # (sky_warren.gd _door_leaf: a shut door)
                t = _box_world(P, n, *leaf[n])
                tris.append(t)
                src.append(np.full(len(t), n, np.int32))
        # sky_warren.gd _room_floors: an entered door's room cell gets a whole-cell floor at its storey if none is
        # within 0.4 m
        for (i, j, lv) in entered:
            if not (ci * C.CH <= i < ci * C.CH + C.CH and cj * C.CH <= j < cj * C.CH + C.CH):
                continue
            ycm = C.roundi(C.STOREY * lv * 100.0)
            if not any(k[0] == i and k[1] == j and abs(k[2] - ycm) <= 40 for k in floors):
                floors[(i, j, ycm)] = -1
        for k, n in floors.items():
            fkeys.append(k)
            frec.append(n)
        for sl in _floor_slabs(floors):
            ycm, i0, i1, j0, j1 = sl
            lo = (W["x0"] + C.CELL * i0, ycm / 100.0 - C.SLAB_M, W["z0"] + C.CELL * j0)
            hi = (W["x0"] + C.CELL * i1, ycm / 100.0, W["z0"] + C.CELL * j1)
            t = C.box_tris(lo, hi)
            slab_tris.append((len(slabs), t))
            slabs.append([ch, ycm, i0, i1, j0, j1])
            tris.append(t)
            src.append(np.full(len(t), C_SLAB, np.int32))
    T = np.concatenate(tris) if tris else np.zeros((0, 3, 3))
    S = np.concatenate(src) if src else np.zeros(0, np.int32)
    T = C.snap_mm(T)
    slab_id = np.full(len(S), -1, np.int32)
    # slab ids: in order of appearance among SLAB triangles (12 each)
    sm = np.nonzero(S == C_SLAB)[0]
    slab_id[sm] = np.repeat(np.arange(len(slabs), dtype=np.int32), 12)[:len(sm)]
    # the island's own bodies
    gt = ground_top(W, P, K)
    dk = deck_tris(isl, W, gt)
    fn = fence_tris(isl, deck, W.get("side", {}).get("moorings") if isinstance(W, dict) else None)
    br = bridge_tris(isl, bridges_down)
    lk = lark_tris(isl, deck)
    parts = [T, dk, fn, br, lk]
    srcs = [S, np.full(len(dk), DECK, np.int32), np.full(len(fn), FENCE, np.int32), np.full(len(br), BRIDGE, np.int32),
            np.full(len(lk), LARK, np.int32)]
    ctri = np.concatenate([p.reshape(-1, 3, 3) for p in parts]).astype(np.float32)
    csrc = np.concatenate(srcs)
    cslab = np.concatenate([slab_id, np.full(len(ctri) - len(slab_id), -1, np.int32)])
    return {"ctri": ctri, "csrc": csrc, "cslab": cslab,
            "slabs": np.array(slabs, np.int32).reshape(-1, 6),
            "fkeys": np.array(fkeys, np.int32).reshape(-1, 3), "frec": np.array(frec, np.int32),
            "gtop": gt}


C_SLAB = SLAB


def _ramp_under(q):
    """sky_warren.gd _ramp_under: per quad its underside RAMP_UNDER along its upward normal and 4 edge faces"""
    out = []
    for qq in q:
        nrm = np.cross(qq[1] - qq[0], qq[2] - qq[0])
        ln = np.linalg.norm(nrm)
        if ln < 1e-12:
            continue
        nrm = nrm / ln
        if nrm[1] < 0.0:
            nrm = -nrm
        lo = qq - nrm * RAMP_UNDER
        out.append([lo[0], lo[2], lo[1]])
        out.append([lo[0], lo[3], lo[2]])
        for k in range(4):
            a, c = qq[k], qq[(k + 1) % 4]
            out.append([a, lo[k], lo[(k + 1) % 4]])
            out.append([a, lo[(k + 1) % 4], c])
    return np.array(out).reshape(-1, 3, 3) if out else np.zeros((0, 3, 3))


def _nomirror(P, n, pts):
    """collision ignores the mirror bit (the runtime turns cdata by the record's transform only)"""
    c, s = P["c"][n], P["s"][n]
    p = np.asarray(pts, float)
    out = np.empty_like(p)
    out[..., 0] = p[..., 0] * c + p[..., 2] * s
    out[..., 1] = p[..., 1]
    out[..., 2] = -p[..., 0] * s + p[..., 2] * c
    return out + P["t"][n]


def _box_world(P, n, lo, hi):
    c, s = P["c"][n], P["s"][n]
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return C.box_tris(lo, hi, R, P["t"][n])


def _floor_slabs(floors):
    """sky_warren.gd _floor_slabs: per height, greedy rectangles (runs along j per row i, carried along i while the
    same run repeats) -> [ycm, i0, i1 (excl), j0, j1 (excl)]"""
    out = []
    by_y = {}
    for (i, j, y) in floors:
        r = by_y.get(y)
        by_y[y] = [i, i, j, j] if r is None else [min(r[0], i), max(r[1], i), min(r[2], j), max(r[3], j)]
    for y, bb in by_y.items():
        open_ = {}
        for i in range(bb[0], bb[1] + 2):
            runs = {}
            if i <= bb[1]:
                j = bb[2]
                while j <= bb[3]:
                    if (i, j, y) not in floors:
                        j += 1
                        continue
                    e = j
                    while e + 1 <= bb[3] and (i, e + 1, y) in floors:
                        e += 1
                    runs[(j, e)] = True
                    j = e + 1
            for r in list(open_.keys()):
                if r not in runs:
                    out.append([y, open_[r], i, r[0], r[1] + 1])
                    del open_[r]
            for r in runs:
                if r not in open_:
                    open_[r] = i
    return out


def ground_top(W, P, K):
    """sky_warren.gd _ground_prep: per cell the lowest top of its cell-mounted top/ramp pieces (inf: none)"""
    g = np.full((W["nx"] + 2, W["nz"] + 2), np.inf)
    recs = W["recs"]
    ids = W["ids"]
    for n in range(len(recs)):
        r = K.rule.get(ids[recs["p"][n]])
        if r is None or r[0] not in ("top", "ramp") or P["mount"][n] != 0:
            continue
        top = P["y"][n] + (0.0 if r[0] == "ramp" else K.aabb[ids[recs["p"][n]]][1][1])
        i, j = int(recs["i"][n]), int(recs["j"][n])
        if top < g[i, j]:
            g[i, j] = top
    return g


def deck_tris(isl, W, gt):
    """the rock glb's deck-col mesh (its trimesh collision), tucked TUCK_M under the lowest paving within TUCK_R"""
    path = C.res_path(isl["lod"]["rock"])
    g = C.read_gltf(path)
    out = []
    stack = [(r, np.eye(4)) for r in g["roots"]]
    while stack:
        n, M = stack.pop()
        nd = g["nodes"][n]
        M2 = M @ nd["matrix"]
        if nd["mesh"] is not None and nd["name"].startswith("deck"):
            for _, t in g["meshes"][nd["mesh"]]:
                out.append(C.xf_pts(M2, t.reshape(-1, 3)))
        for c in nd["children"]:
            stack.append((c, M2))
    if not out:
        return np.zeros((0, 3, 3))
    v = np.concatenate(out)
    lo = np.full(len(v), np.inf)
    x0, z0 = W["x0"], W["z0"]
    ci = np.floor((v[:, 0] - x0) / C.CELL).astype(int)
    cj = np.floor((v[:, 2] - z0) / C.CELL).astype(int)
    i0 = np.floor((v[:, 0] - C.TUCK_R - x0) / C.CELL).astype(int)
    i1 = np.floor((v[:, 0] + C.TUCK_R - x0) / C.CELL).astype(int)
    j0 = np.floor((v[:, 2] - C.TUCK_R - z0) / C.CELL).astype(int)
    j1 = np.floor((v[:, 2] + C.TUCK_R - z0) / C.CELL).astype(int)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ii, jj = ci + di, cj + dj
            ok = (ii >= i0) & (ii <= i1) & (jj >= j0) & (jj <= j1) & (ii >= 0) & (jj >= 0) & \
                 (ii < gt.shape[0]) & (jj < gt.shape[1])
            val = np.full(len(v), np.inf)
            val[ok] = gt[ii[ok], jj[ok]]
            lo = np.minimum(lo, val)
    m = np.isfinite(lo) & (v[:, 1] > lo - C.TUCK_M)
    v[m, 1] = lo[m] - C.TUCK_M
    return v.reshape(-1, 3, 3)


def fence_tris(isl, deck, moorings=None):
    """sky_island.gd _build_fence: a 1.4 x 0.12 box per ~3 m segment, none within a gap's half width + 1.5 m (the
    bridges' gaps, and the market moorings' -- the twin's moorings[].fence_gap, ASM 8)"""
    pts = isl.get("fence") or []
    if len(pts) < 2:
        return np.zeros((0, 3, 3))
    gaps = list(isl.get("fence_gaps") or []) + [m["fence_gap"] for m in (moorings or []) if m.get("fence_gap")]
    out = []
    n = len(pts)
    for i in range(n):
        a = np.array(pts[i], float)
        b = np.array(pts[(i + 1) % n], float)
        L = float(np.linalg.norm(b - a))
        if L < 0.2:
            continue
        k_n = max(1, C.roundi(L / 3.0))
        d = (b - a) / L
        for k in range(k_n):
            p0 = a + d * (L * k / k_n)
            p1 = a + d * (L * (k + 1) / k_n)
            mid = (p0 + p1) * 0.5
            if any(np.hypot(mid[0] - g["at"][0], mid[1] - g["at"][1]) < float(g["width"]) * 0.5 + 1.5 for g in gaps):
                continue
            y0 = float(deck.y(p0[0], p0[1]))
            y1 = float(deck.y(p1[0], p1[1]))
            v = np.array([p1[0] - p0[0], y1 - y0, p1[1] - p0[1]])
            xa = v / np.linalg.norm(v)
            yb = np.array([0.0, 1.0, 0.0])
            zb = np.cross(xa, yb)
            zb /= np.linalg.norm(zb)
            R = np.stack([xa, yb, zb], 1)          # columns: Basis(xa, yb, zb)
            c = np.array([(p0[0] + p1[0]) * 0.5, (y0 + y1) * 0.5 + 0.7, (p0[1] + p1[1]) * 0.5])
            h = np.array([np.linalg.norm(v), 1.4, 0.12]) * 0.5
            out.append(C.box_tris(-h, h, R, c))
    return np.concatenate(out) if out else np.zeros((0, 3, 3))


_CANON = {}


def aerostats(iid):
    """remake/bible/sky_islands.json: the island's larks (sky_island.gd canon.aerostats, default 2)"""
    if not _CANON:
        import json
        p = os.path.join(C.GP, "remake", "bible", "sky_islands.json")
        if os.path.exists(p):
            for e in json.load(open(p)).get("islands", []):
                _CANON[e.get("id")] = e
    return int(_CANON.get(iid, {}).get("aerostats", 2))


def lark_tris(isl, deck):
    """sky_island.gd _build_props / _spawn_lark: a parked lark (a solid craft) on each of the first `aerostats` pads,
    at the pad's y (or the deck) + 0.02, turned by its yaw -- as a box"""
    out = []
    for p in (isl.get("pads") or [])[:aerostats(isl["id"])]:
        y = float(p["y"]) if "y" in p and p["y"] is not None else float(deck.y(p["x"], p["z"]))
        out.append(C.box_tris(LARK_BOX[0], LARK_BOX[1], C.rot_y(float(p.get("yaw", 0.0))),
                              np.array([float(p["x"]), y + 0.02, float(p["z"])])))
    return np.concatenate(out) if out else np.zeros((0, 3, 3))


_BR = {}


def bridge_tris(isl, down=False):
    """sky_bridge.gd: each bridge's glb, every mesh solid (trimesh), the moving nodes at deploy 0 (stowed) or 1"""
    import json
    styles = json.load(open(C.BRIDGES_JSON))["styles"]
    f = isl.get("faces", {})
    base = isl.get("bridge_style", "bascule_timber")
    out = []
    for b in isl.get("bridges", []):
        st = base + ("_road" if float(b.get("width", 3.6)) >= 5.0 else "")
        sp = styles.get(st)
        if sp is None:
            continue
        al = float(b["along"])
        side = b["side"]
        if side == "N":
            R, t = C.rot_y(-np.pi / 2), (f["N"], 0, al)
        elif side == "S":
            R, t = C.rot_y(np.pi / 2), (f["S"], 0, al)
        elif side == "E":
            R, t = C.rot_y(np.pi), (al, 0, f["E"])
        else:
            R, t = np.eye(3), (al, 0, f["W"])
        local = _bridge_local(sp, 1.0 if down else 0.0)
        local = np.concatenate([local, _ramp_box(float(sp.get("width", 3.6))).reshape(-1, 3)]) if len(local) else local
        if len(local):
            out.append(local @ R.T + np.asarray(t, float))
    return np.concatenate(out).reshape(-1, 3, 3) if out else np.zeros((0, 3, 3))


RAMP_FOOT, RAMP_HEAD, RAMP_T = (-1.7, -0.12), (-0.45, 0.03), 0.04     # sky_bridge.gd (z, y) in the bridge frame


def _ramp_box(w):
    """sky_bridge.gd ramp_box/_make_ramp: the threshold ramp's box (fixed on the bridge root, any pose)"""
    a = np.array([0.0, RAMP_FOOT[1], RAMP_FOOT[0]])
    b = np.array([0.0, RAMP_HEAD[1], RAMP_HEAD[0]])
    along = (b - a) / np.linalg.norm(b - a)
    up = np.cross(along, [1.0, 0.0, 0.0])
    Rb = np.stack([[1.0, 0.0, 0.0], up, along], 1)
    c = (a + b) * 0.5 - up * RAMP_T * 0.5
    h = np.array([w - 0.3, RAMP_T, np.linalg.norm(b - a)]) * 0.5
    return C.box_tris(-h, h, Rb, c)


def _bridge_local(sp, d):
    key = (sp["glb"], d)
    if key in _BR:
        return _BR[key]
    g = C.read_gltf(C.res_path(sp["glb"]))
    keys = {e["node"]: e["keys"] for e in sp.get("nodes", [])}
    out = []
    stack = [(r, np.eye(4)) for r in g["roots"]]
    while stack:
        n, M = stack.pop()
        nd = g["nodes"][n]
        L = nd["matrix"]
        if nd["name"] in keys:
            L = _at(keys[nd["name"]], d)
        M2 = M @ L
        if nd["mesh"] is not None:
            for _, t in g["meshes"][nd["mesh"]]:
                out.append(C.xf_pts(M2, t.reshape(-1, 3)))
        for c in nd["children"]:
            stack.append((c, M2))
    v = np.concatenate(out) if out else np.zeros((0, 3))
    _BR[key] = v
    return v


def _at(keys, d):
    k1 = 0
    while k1 < len(keys) - 1 and float(keys[k1 + 1][0]) < d:
        k1 += 1
    a = keys[k1][1]
    k2 = min(k1 + 1, len(keys) - 1)
    b = keys[k2][1]
    d0, d1 = float(keys[k1][0]), float(keys[k2][0])
    f = 0.0 if d1 <= d0 else min(max((d - d0) / (d1 - d0), 0.0), 1.0)
    pa, pb = np.array(a["pos"]), np.array(b["pos"])
    qa, qb = np.array(a["rot"], float), np.array(b["rot"], float)
    qa /= np.linalg.norm(qa)
    qb /= np.linalg.norm(qb)
    if np.dot(qa, qb) < 0:
        qb = -qb
    q = qa * (1 - f) + qb * f                    # (nlerp: the keys used are 0 and 1, where it is exact)
    sa, sb = np.array(a["scl"]), np.array(b["scl"])
    return C.trs(pa * (1 - f) + pb * f, q, sa * (1 - f) + sb * f)


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    for iid in a:
        t = time.time()
        g = build(iid, cache="--no-cache" not in sys.argv)
        cs = np.bincount(np.clip(-g.csrc, 0, 4), minlength=5)
        print("%s render %d tris, collision %d tris (pieces %d, slabs %d [%d], deck %d, fence %d, bridge %d), %.1f s"
              % (iid, len(g.rtri), len(g.ctri), cs[0], cs[1], len(g.slabs), cs[2], cs[3], cs[4], time.time() - t))


if __name__ == "__main__":
    main()
