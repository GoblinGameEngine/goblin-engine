#!/usr/bin/env python3
"""mutate.py -- does each check catch its fault, and only its fault?

Island faults (records edited in a copy of the island's files under reference/tmp/audit/mut/<fault>/, audited with
--wdir, compared with the unmodified copy; new hotspots within 2 cells of the fault are listed by check):
  floor     delete the paving under a ground walk node          -> holes (no_floor), walk
  raise     raise a paving cell one quarter (0.8 m; records hold quarters, so not 0.5)   -> holes (floor_off), walk
  arch      a solid box piece put in a walk-through opening      -> intrusion (pass), walk
  wall      remove an exterior wall bay of a room                -> cracks (missing_wall)
  dup       duplicate a wall placement                           -> manifold (dup_across) [+ zfight]
  float     lift a ground-standing piece a storey                -> floating
Kit faults (in memory, bounds.check_kit / meshlib.topology):
  flip      a piece's faces all flipped                          -> inside_out (+ inward normals)
  flip1     one face flipped                                     -> inconsistent winding
  scale     a piece's mesh scaled up 10 %                        -> bounds declared
  shift     a wall's mesh moved 20 cm out (+z)                   -> bounds declared (+ slot)
  colbox    a piece's collision box grown past its mesh          -> bounds collision>mesh

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/mutate.py [SKY-099] [fault ...]
"""
import collections
import json
import os
import shutil
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as A  # noqa: E402
import audit as AU  # noqa: E402
import bounds as BD  # noqa: E402
import checks as CK  # noqa: E402
import common as C  # noqa: E402

EXPECT = {"floor": {"holes", "walk"}, "raise": {"holes", "walk", "cracks"}, "arch": {"intrusion", "walk"},
          "wall": {"cracks"}, "dup": {"manifold", "zfight"}, "float": {"floating"}}
MUT = os.path.join(C.OUT, "mut")


def _copy(iid, name, recs=None):
    d = os.path.join(MUT, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    W = C.read_warren(iid)
    C.write_warren_records(iid, d, W["recs"] if recs is None else recs)
    return d


def _rec(W, n):
    return W["recs"][n].copy()


def pick(iid, fault):
    """-> (new records, the fault's cell (i, j), what was done)"""
    g = A.build(iid, render=False)
    K = A.kit()
    W = g.W
    recs = W["recs"]
    ids = W["ids"]
    side = W["side"]
    N = np.array([n[:3] for n in side["walk"]["nodes"]])
    kinds = [n[3] for n in side["walk"]["nodes"]]
    rng = np.random.default_rng(7)
    kind_of = np.array([K.P.get(p, {}).get("kind", "") for p in ids])
    pk = recs["p"]
    mount = (recs["rf"] >> 4) & 3
    if fault in ("floor", "raise"):
        # a ground node in the middle of flat ground: its cell's whole-cell paving
        cand = []
        cells = {g.ij(N[k]): N[k, 1] for k in range(len(N)) if kinds[k] == "ground"}
        for (i, j), y in cells.items():
            if all(cells.get((i + a, j + b)) == y for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                m = np.nonzero((recs["i"] == i) & (recs["j"] == j) & (kind_of[pk] == "ground") & (mount == 0))[0]
                if len(m) == 1:
                    cand.append((i, j, int(m[0])))
        i, j, n = cand[len(cand) // 2]
        if fault == "floor":
            return np.delete(recs, n), (i, j), "deleted %s at (%d,%d)" % (ids[pk[n]], i, j)
        r = recs.copy()
        q = int(r["rf"][n]) >> 6
        if q < 3:
            r["rf"][n] = (int(r["rf"][n]) & 0x3F) | ((q + 1) << 6)
        else:
            r["rf"][n] = int(r["rf"][n]) & 0x3F
            r["k"][n] += 1
        return r, (i, j), "raised %s at (%d,%d) by 0.8 m" % (ids[pk[n]], i, j)
    if fault == "arch":
        # a walk-through piece with a walk edge through it; a box-collision piece whose box fills its pass volume
        cell_nodes = {g.ij(N[k]) for k in range(len(N)) if kinds[k] == "ground"}
        boxes = [p for p, pid in enumerate(ids) if K.rule.get(pid, ("",))[0] == "box" and pid in K.aabb]
        for n in np.nonzero(np.array([bool(K.P.get(ids[p], {}).get("pass")) for p in pk]))[0]:
            i, j, rot = int(recs["i"][n]), int(recs["j"][n]), int(recs["rf"][n] & 3)
            di, dj = CK.FACE[rot]
            if (i, j) not in cell_nodes or (i + di, j + dj) not in cell_nodes:
                continue
            ps = np.array(K.P[ids[pk[n]]]["pass"], float)
            for p in boxes:
                lo, hi = K.aabb[ids[p]]
                if lo[1] <= ps[0][1] + 0.3 and hi[1] > 1.0 and lo[0] < ps[0][0] and hi[0] > ps[1][0] and \
                        lo[2] < ps[1][2] and hi[2] > ps[0][2]:
                    r = recs[n:n + 1].copy()
                    r["p"] = p
                    r["rf"] = (int(recs["rf"][n]) & 0xC7) | (1 << 4)      # (same rot/quarter, face mount)
                    return np.concatenate([recs, r]), (i, j), "put %s in %s at (%d,%d) face %d" % (
                        ids[p], ids[pk[n]], i, j, rot)
        raise RuntimeError("no arch with a walk edge through it")
    if fault == "wall":
        rooms = CK.levels(side)
        for n in rng.permutation(np.nonzero((kind_of[pk] == "wall") & (mount == 1))[0]):
            pid = ids[pk[n]]
            if CK.is_opening(pid, K.P[pid]):
                continue
            i, j, k, rot = int(recs["i"][n]), int(recs["j"][n]), int(recs["k"][n]), int(recs["rf"][n] & 3)
            di, dj = CK.FACE[rot]
            if (i, j, k) in rooms and (i + di, j + dj, k) not in rooms:
                return np.delete(recs, n), (i, j), "removed %s at (%d,%d,%d) face %d" % (pid, i, j, k, rot)
    if fault == "dup":
        n = int(np.nonzero((kind_of[pk] == "wall") & (mount == 1))[0][0])
        return np.concatenate([recs, recs[n:n + 1]]), (int(recs["i"][n]), int(recs["j"][n])), \
            "duplicated %s at (%d,%d)" % (ids[pk[n]], recs["i"][n], recs["j"][n])
    if fault == "float":
        for n in rng.permutation(np.nonzero(np.isin(kind_of[pk], ["decor", "cell", "tower"]) & (mount == 0))[0]):
            r = recs.copy()
            r["k"][n] += 1
            return r, (int(recs["i"][n]), int(recs["j"][n])), "lifted %s at (%d,%d) a storey" % (
                ids[pk[n]], recs["i"][n], recs["j"][n])
    raise RuntimeError("no target for " + fault)


def keyset(res, near=None, rad=2):
    out = collections.Counter()
    for h in res["hotspots"]:
        if near is not None and (abs(h["cell"][0] - near[0]) > rad or abs(h["cell"][1] - near[1]) > rad):
            continue
        out[(h["check"], h["kind"], tuple(h["cell"]))] += 1
    return out


def run_island(iid, faults):
    base_dir = _copy(iid, "base")
    base = AU.run(iid, wdir=base_dir, out_dir=os.path.join(MUT, "base"), png=False, quiet=True)
    rows = []
    for f in faults:
        recs, cell, what = pick(iid, f)
        d = _copy(iid, f, recs)
        res = AU.run(iid, wdir=d, out_dir=d, png=True, quiet=True)
        bk = keyset(base, cell)
        mk = keyset(res, cell)
        new = mk - bk
        by = collections.Counter()
        kinds = collections.defaultdict(set)
        for (ch, kd, c), n in new.items():
            by[ch] += n
            kinds[ch].add(kd)
        caught = bool(set(by) & EXPECT[f])
        extra = set(by) - EXPECT[f]
        rows.append({"fault": f, "what": what, "cell": cell, "new_by_check": dict(by),
                     "kinds": {k: sorted(v) for k, v in kinds.items()}, "caught": caught, "others": sorted(extra)})
        print("%-6s %-55s caught=%s  new=%s  others=%s" % (f, what, caught, {k: sorted(v) for k, v in kinds.items()},
                                                          sorted(extra) or "-"))
    return rows


def run_kit():
    rows = []
    K = C.Kit()
    mounts = BD.all_mounts()
    base = {(r["piece"], r["check"], r["side"]) for r in BD.check_kit(K, mids={}, mounts=mounts)}
    cases = []
    p1 = "wall_plain_t"
    K1 = C.Kit()
    K1.mesh[p1] = K1.mesh[p1] * 1.1
    cases.append(("scale", p1, K1, {"declared"}))
    p2 = "wall_window_s_t"
    K2 = C.Kit()
    K2.mesh[p2] = K2.mesh[p2] + np.array([0, 0, 0.2])
    cases.append(("shift", p2, K2, {"declared", "slot"}))
    p3 = "int_counter"
    K3 = C.Kit()
    lo, hi = K3.aabb[p3]
    K3.rule[p3] = ("box", (lo - np.array([0.0, 0.0, 0.0]), hi + np.array([0.15, 0.0, 0.0])))
    cases.append(("colbox", p3, K3, {"collision>mesh"}))
    # normals (meshlib.topology / inward_normals, as kitmesh.py runs them)
    import meshlib as M
    import rays as RY
    t0 = K.mesh["wall_plain_t"]
    for name, tm, want in (("flip", t0[:, [0, 2, 1]], "inside_out"), ("flip1", np.concatenate([t0[:1, [0, 2, 1]], t0[1:]]),
                                                                       "inconsistent_edges")):
        b, m = M.topology(t0), M.topology(tm)
        caught = m[want] > b[want]
        others = sorted(k for k in ("inside_out", "inconsistent_edges", "nonmanifold_edges", "open_edges", "dup_faces")
                        if k != want and m[k] != b[k])
        inw = M.inward_normals(tm, RY.Rays(tm))["fraction"]
        rows.append({"fault": name, "piece": "wall_plain_t", "new": {want: m[want], "inward_frac": inw},
                     "caught": bool(caught), "others": others})
        print("%-6s %-24s caught=%s  %s=%s inward_frac=%.2f  others=%s" % (name, "wall_plain_t", caught, want, m[want],
                                                                         inw, others or "-"))
    for name, pid, Km, want in cases:
        got = {(r["piece"], r["check"], r["side"]) for r in BD.check_kit(Km, mids={}, mounts=mounts, pieces={pid})}
        new = {x for x in got if x not in base}
        checks = {x[1] for x in new}
        caught = bool(checks & want)
        others = sorted(checks - want - {"slot"})
        rows.append({"fault": name, "piece": pid, "new": sorted(new), "caught": caught, "others": others})
        print("%-6s %-24s caught=%s  new=%s  others=%s" % (name, pid, caught, sorted(new), others or "-"))
    return rows


def main():
    a = sys.argv[1:]
    iid = next((x for x in a if x.startswith("SKY-")), "SKY-099")
    faults = [x for x in a if x in EXPECT] or list(EXPECT)
    out = {"island": iid, "island_faults": run_island(iid, faults)}
    out["kit_faults"] = run_kit()
    json.dump(out, open(os.path.join(MUT, "mutate.json"), "w"), indent=1, default=str)
    n = sum(r["caught"] for r in out["island_faults"] + out["kit_faults"])
    print("caught %d/%d -> %s" % (n, len(out["island_faults"]) + len(out["kit_faults"]),
                                  os.path.join(MUT, "mutate.json")))


if __name__ == "__main__":
    main()
