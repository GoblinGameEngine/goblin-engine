"""pairs.py -- piece-against-piece checks done once per CONFIGURATION, not per placement.

An island has ~10^5 pairs of placements whose boxes overlap, but only ~10^4 distinct configurations (piece a, its
rot/mount/mirror, piece b, its rot/mount/mirror, b's offset from a to the mm).  Each configuration is checked once
with meshlib -- coplanar overlaps (z-fighting), interpenetration (edges piercing faces), duplicate faces -- in a's
frame; the results are mapped back onto every instance.  Configurations are cached on disk across islands
(reference/tmp/audit/cache/pairs_<kit hash>.pkl): the kit is shared, so --all gets faster as it goes."""
import hashlib
import os
import pickle

import numpy as np
from scipy.spatial import cKDTree

import common as C
import meshlib as M
import rays as RY

_CACHE = {}
_CACHE_PATH = [None]
_DIRTY = [0]


def _cache_path():
    if _CACHE_PATH[0] is None:
        h = hashlib.sha1()
        for f in (C.KIT_GLB, C.PIECES_JSON, os.path.join(C.HERE, "meshlib.py"), os.path.abspath(__file__)):
            h.update(str(os.path.getmtime(f)).encode())
        _CACHE_PATH[0] = os.path.join(C.CACHE, "pairs_%s.pkl" % h.hexdigest()[:12])
        if os.path.exists(_CACHE_PATH[0]):
            try:
                _CACHE.update(pickle.load(open(_CACHE_PATH[0], "rb")))
            except Exception:
                pass
    return _CACHE_PATH[0]


def save_cache():
    p = _cache_path()
    if _DIRTY[0]:
        os.makedirs(C.CACHE, exist_ok=True)
        tmp = p + ".tmp"
        pickle.dump(_CACHE, open(tmp, "wb"))
        os.replace(tmp, p)
        _DIRTY[0] = 0


def boxes(g):
    n = len(g.recs)
    lo = np.full((n, 3), np.inf)
    hi = np.full((n, 3), -np.inf)
    v = g.rtri.reshape(-1, 3)
    src = np.repeat(g.rsrc, 3)
    np.minimum.at(lo, src, v)
    np.maximum.at(hi, src, v)
    return lo, hi


def overlapping(g, lo, hi, grow=0.002):
    ok = np.isfinite(lo[:, 0])
    ids = np.nonzero(ok)[0]
    c = (lo[ids] + hi[ids]) / 2
    r = np.linalg.norm(hi[ids] - lo[ids], axis=1).max() / 2 + grow
    pr = cKDTree(c).query_pairs(2 * r, output_type="ndarray")
    a, b = ids[pr[:, 0]], ids[pr[:, 1]]
    ov = np.all((lo[a] <= hi[b] + grow) & (lo[b] <= hi[a] + grow), 1)
    return a[ov], b[ov]


def _local(K, pid, rf):
    m = K.mesh[pid].copy()
    if (rf >> 3) & 1:
        m[..., 0] = -m[..., 0]
        m = m[:, [0, 2, 1]]
    a = (rf & 3) * np.pi / 2
    c, s = np.cos(a), np.sin(a)
    out = m.copy()
    out[..., 0] = m[..., 0] * c + m[..., 2] * s
    out[..., 2] = -m[..., 0] * s + m[..., 2] * c
    return out


def config(K, pa, rfa, pb, rfb, dt):
    """the checks for one configuration: {"zf": [(point, normal, area)], "pi": [(point, normal, edges)],
    "dup": n} in a's frame (a's origin at 0)"""
    key = (pa, rfa, pb, rfb, dt)
    _cache_path()
    r = _CACHE.get(key)
    if r is not None:
        return r
    A = _local(K, pa, rfa)
    B = _local(K, pb, rfb) + np.array(dt, float) / 1000.0
    T = np.concatenate([A, B])
    G = np.r_[np.zeros(len(A), int), np.ones(len(B), int)]
    zf = []
    SA = K.slot[pa]
    SB = K.slot[pb]
    for a, b, ar, at, smp in M.coplanar_overlaps(T, G):
        for q, n, fa, fb in smp:
            fa, fb = (fa, fb) if G[fa] == 0 else (fb, fa)
            zf.append((q, n, ar / max(len(smp), 1), str(SA[fa]), str(SB[fb - len(A)])))
    R = RY.Rays(T)
    pi = []
    for (a, b), (cnt, at, smp) in M.interpenetration(T, G, R).items():
        for q, n, hg in smp:
            pi.append((q, n, cnt / max(len(smp), 1), hg))
    dup = sum(n for _, _, n, _ in M.duplicates_across(T, G, facing="same"))
    b2b = sum(n for _, _, n, _ in M.duplicates_across(T, G, facing="opposite"))
    r = {"zf": zf, "pi": pi, "dup": dup, "b2b": b2b}
    _CACHE[key] = r
    _DIRTY[0] += 1
    return r


def run(g, K):
    """-> per instance rows: zfight [(a, b, world point, normal, area)], pierce [(a, b, point, normal, edges,
    pierced)], dup [(a, b, n)], plus counts"""
    lo, hi = boxes(g)
    a, b = overlapping(g, lo, hi)
    P = g.P
    rf = g.recs["rf"].astype(int)
    pk = g.recs["p"].astype(int)
    dt = np.round((P["t"][b] - P["t"][a]) * 1000).astype(np.int64)
    key = np.stack([pk[a], rf[a] & 0x3B, pk[b], rf[b] & 0x3B, dt[:, 0], dt[:, 1], dt[:, 2]], 1)
    u, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    zf, pi, dup = [], [], []
    b2b = 0
    res = [config(K, g.ids[k[0]], int(k[1]), g.ids[k[2]], int(k[3]), (int(k[4]), int(k[5]), int(k[6]))) for k in u]
    for q in range(len(a)):
        r = res[inv[q]]
        b2b += r.get("b2b", 0)
        if not (r["zf"] or r["pi"] or r["dup"]):
            continue
        ta = P["t"][a[q]]
        for p, n, ar, sa, sb in r["zf"]:
            zf.append((a[q], b[q], p + ta, n, ar, sa, sb))
        for p, n, e, hg in r["pi"]:
            pi.append((a[q], b[q], p + ta, n, e, a[q] if hg == 0 else b[q]))
        if r["dup"]:
            dup.append((a[q], b[q], r["dup"]))
    save_cache()
    return {"zf": zf, "pi": pi, "dup": dup, "b2b": int(b2b), "pairs": int(len(a)), "configs": int(len(u))}
