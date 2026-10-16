#!/usr/bin/env python3
"""bounds.py -- where models step outside their bounds.  The general part is meshlib.bounds (any tris vs any box);
this is the KIT client: every warren piece (kit.glb, and its MID model in kit_mid.glb) against

  declared   pieces.json "bounds" (the piece's own contract)
  slot       the envelope of its kind + mount (pieces.json "frames"): a cell piece in its 3 x 3 m cell (x span
             cells along +X/+Z); a wall / edge / face piece within its bay x +-1.5, its body no deeper into its own
             cell than its thickness (_t 0.25 m, _k 0.6 m, else 1.5) and reaching no further than OVERHANG over the
             neighbour; a corner in its corner (occupied cell -X/-Z, OVERHANG out); storey pieces (walls, interior,
             overlays, signs) within 0 .. 3.2 m
  collision  the runtime collision (sky_warren.gd rules: frame / ramp / box / top / mesh) vs the render mesh: the
             collision sticking out past the visible model, and (for blocking kinds) the visible model far beyond
             its collision
  mid        the MID model vs the full piece's mesh bounds

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/bounds.py [--png N] [--pieces id,id]
      -> reference/tmp/audit/bounds_kit.json, bounds_kit.txt (ranked), bounds/<piece>.png for the N worst

Ranked rows: piece, which bound, side, overrun cm, placements (all islands)."""
import collections
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import img  # noqa: E402
import meshlib as M  # noqa: E402

TOL = 0.01                 # 1 cm
OVERHANG = 0.6             # m a face piece may reach over its neighbour without saying so (eaves, signs, balconies)
CORNER_OUT = 0.35
STOREY_KINDS = ("wall", "interior", "overlay", "sign")
BLOCKING = ("tower", "decor", "cell", "corner")


def thickness(pid):
    if pid.endswith("_t"):
        return 0.25
    if pid.endswith("_k"):
        return 0.6
    return 1.5


def envelope(pid, spec, mount):
    """the slot envelope (lo, hi) of a piece by kind and mount; y unbounded unless a storey piece"""
    kind = spec.get("kind", "")
    nx, nz = spec.get("span", [1, 1])
    inf = 1e9
    if mount == 1:
        lo = [-1.5, -inf, -thickness(pid)]
        hi = [1.5, inf, OVERHANG]
        if kind in ("wall",):
            lo[1], hi[1] = 0.0, 3.2
        return np.array(lo), np.array(hi)
    if mount == 2:
        return np.array([-1.5, -inf, -1.5]), np.array([CORNER_OUT, inf, CORNER_OUT])
    lo = [-1.5, -inf, -1.5]
    hi = [-1.5 + 3 * nx, inf, -1.5 + 3 * nz]
    if kind in ("interior", "overlay", "sign"):
        lo[1], hi[1] = 0.0, 3.2
    return np.array(lo), np.array(hi)


def mount_of(pid, spec, mounts):
    m = mounts.get(pid)
    if m:
        return {"cell": 0, "face": 1, "corner": 2}[m]
    kind = spec.get("kind", "")
    if kind == "corner":
        return 2
    if kind in ("wall", "edge", "sign", "passage") or pid in ("ov_ac", "ov_lantern", "ov_fluoro", "ov_planter",
                                                              "ov_pipe_run", "ladder"):
        return 1
    return 0


def all_mounts():
    """piece id -> its mount, from the islands' twins (the generator's own word)"""
    out = {}
    for f in sorted(os.listdir(C.WR)):
        if f.startswith("SKY-") and f.endswith(".json"):
            try:
                with open(os.path.join(C.WR, f)) as fh:
                    head = fh.read(400000)
                i = head.find('"mounts"')
                if i < 0:
                    continue
                j = head.find("}", i)
                out.update(json.loads(head[head.find("{", i):j + 1]))
            except Exception:
                pass
    return out


def placements_count():
    """piece id -> placements over every island file"""
    cnt = collections.Counter()
    for f in sorted(os.listdir(C.WR)):
        if f.startswith("SKY-") and f.endswith(".bin.gz"):
            try:
                W = C.read_warren(f[:-7])
            except Exception:
                continue
            ids = W["ids"]
            u, n = np.unique(W["recs"]["p"], return_counts=True)
            for a, b in zip(u, n):
                cnt[ids[a]] += int(b)
    return cnt


def collision_tris(K, pid):
    mode, data = K.rule.get(pid, ("", None))
    if mode == "ramp":
        return C.quads_tris(data)
    if mode == "frames":
        return np.concatenate([C.box_tris(lo, hi) for lo, hi in data]) if data else np.zeros((0, 3, 3))
    if mode == "box":
        return C.box_tris(*data)
    if mode == "top":
        return C.quads_tris(data[None])
    if mode == "mesh":
        return data
    return np.zeros((0, 3, 3))


def check_kit(K=None, mids=None, mounts=None, pieces=None):
    K = K or C.Kit()
    mounts = mounts if mounts is not None else all_mounts()
    if mids is None:
        mids = {}
        mp = os.path.join(C.WR, "kit", "kit_mid.glb")
        if os.path.exists(mp):
            g = M.read_glb_meshes(mp)
            mids = {k: v[0] for k, v in g.items()}
    rows = []
    for pid, spec in K.P.items():
        if pieces and pid not in pieces:
            continue
        tris = K.mesh.get(pid)
        if tris is None or not len(tris):
            continue
        mount = mount_of(pid, spec, mounts)
        b = spec.get("bounds")
        if b:
            r = M.bounds(tris, b[0], b[1], TOL)
            for side, v in r["over"].items():
                rows.append({"piece": pid, "check": "declared", "side": side, "cm": round(v * 100, 1),
                             "outside": len(r["outside_tris"])})
            # the declared box itself against the slot
            lo, hi = envelope(pid, spec, mount)
            for k, ax in enumerate("xyz"):
                if lo[k] - b[0][k] > TOL:
                    rows.append({"piece": pid, "check": "declared>slot", "side": "-" + ax,
                                 "cm": round((lo[k] - b[0][k]) * 100, 1), "outside": 0})
                if b[1][k] - hi[k] > TOL:
                    rows.append({"piece": pid, "check": "declared>slot", "side": "+" + ax,
                                 "cm": round((b[1][k] - hi[k]) * 100, 1), "outside": 0})
        lo, hi = envelope(pid, spec, mount)
        r = M.bounds(tris, lo, hi, TOL)
        for side, v in r["over"].items():
            rows.append({"piece": pid, "check": "slot", "side": side, "cm": round(v * 100, 1),
                         "outside": len(r["outside_tris"]), "mount": ["cell", "face", "corner"][mount]})
        # collision vs render
        ct = collision_tris(K, pid)
        if len(ct):
            mlo, mhi = K.aabb[pid]
            r = M.bounds(ct, mlo, mhi, 0.02)
            for side, v in r["over"].items():
                rows.append({"piece": pid, "check": "collision>mesh", "side": side, "cm": round(v * 100, 1),
                             "outside": len(r["outside_tris"]), "cmode": K.rule[pid][0]})
            if K.rule[pid][0] == "box" and spec.get("kind") in BLOCKING:
                v = ct.reshape(-1, 3)
                r = M.bounds(tris, v.min(0), v.max(0), 0.10)
                for side, w in r["over"].items():
                    rows.append({"piece": pid, "check": "mesh>collision", "side": side, "cm": round(w * 100, 1),
                                 "outside": len(r["outside_tris"]), "cmode": "box"})
        # the MID model
        mm = mids.get(spec.get("mid", {}).get("mesh", pid) if isinstance(spec.get("mid"), dict) else None)
        if mm is not None and len(mm):
            mlo, mhi = K.aabb[pid]
            r = M.bounds(mm, mlo, mhi, 0.02)
            for side, v in r["over"].items():
                rows.append({"piece": pid, "check": "mid>full", "side": side, "cm": round(v * 100, 1),
                             "outside": len(r["outside_tris"])})
    return rows


def draw(K, pid, spec, mount, path, rows, mids=None):
    tris = K.mesh[pid]
    if rows and rows[0]["check"] == "mid>full" and mids and pid in mids:
        mlo, mhi = K.aabb[pid]
        mm = mids[pid]
        red = M.bounds(mm, mlo, mhi, 0.02)["outside_tris"]
        return img.views(mm, [(mlo, mhi, (0, 0, 220), "full piece's mesh box")], path, red=red,
                         title="%s MID model vs the full piece: %s" % (pid, "; ".join(
                             "%s %+.0f cm" % (r["side"], r["cm"]) for r in rows if r["check"] == "mid>full")))
    lo, hi = envelope(pid, spec, mount)
    vt = tris.reshape(-1, 3)
    elo = np.where(np.abs(lo) > 1e8, vt.min(0) - 0.05, lo)
    ehi = np.where(np.abs(hi) > 1e8, vt.max(0) + 0.05, hi)
    b = spec.get("bounds")
    boxes = [(elo, ehi, (0, 160, 0), "slot")]
    red = set()
    if b:
        boxes.append((np.array(b[0]), np.array(b[1]), (0, 0, 220), "declared"))
        red |= set(M.bounds(tris, b[0], b[1], TOL)["outside_tris"].tolist())
    red |= set(M.bounds(tris, lo, hi, TOL)["outside_tris"].tolist())
    ct = collision_tris(K, pid)
    if len(ct):
        v = ct.reshape(-1, 3)
        boxes.append((v.min(0), v.max(0), (230, 140, 0), "collision (%s)" % K.rule[pid][0]))
    title = "%s  [%s, %s]  " % (pid, spec.get("kind"), ["cell", "face", "corner"][mount]) + \
        "; ".join("%s %s %+.0f cm" % (r["check"], r["side"], r["cm"]) for r in rows[:4])
    return img.views(tris, boxes, path, red=sorted(red), title=title)


def main():
    a = sys.argv[1:]
    npng = int(a[a.index("--png") + 1]) if "--png" in a else 24
    pieces = set(a[a.index("--pieces") + 1].split(",")) if "--pieces" in a else None
    K = C.Kit()
    mounts = all_mounts()
    mids = {k: v[0] for k, v in M.read_glb_meshes(os.path.join(C.WR, "kit", "kit_mid.glb")).items()}
    rows = check_kit(K, mids=mids, mounts=mounts, pieces=pieces)
    cnt = placements_count()
    for r in rows:
        r["placements"] = cnt.get(r["piece"], 0)
    # (a "slot" row repeating a "declared>slot" row on the same side says nothing new: the declared box already
    # owns that overhang)
    dec = {(r["piece"], r["side"]) for r in rows if r["check"] == "declared>slot"}
    rows = [r for r in rows if not (r["check"] == "slot" and (r["piece"], r["side"]) in dec)]
    # rank: broken contracts first (mesh outside its declared box, collision past the mesh, MID past the piece),
    # then declared overhangs past the slot; within a class by overrun x how much the piece is used
    W = {"declared": 3, "collision>mesh": 3, "mid>full": 3, "slot": 2, "declared>slot": 1, "mesh>collision": 0.5}
    rows.sort(key=lambda r: -(W.get(r["check"], 1) * 1000 + min(r["cm"], 999) * (1 + np.log1p(r["placements"])) / 10))
    os.makedirs(os.path.join(C.OUT, "bounds"), exist_ok=True)
    json.dump(rows, open(os.path.join(C.OUT, "bounds_kit.json"), "w"), indent=0)
    by = collections.defaultdict(list)
    for r in rows:
        by[r["piece"]].append(r)
    lines = ["%-30s %-15s %-4s %7s %9s  %s" % ("piece", "bound", "side", "cm", "placed", "note")]
    for r in rows:
        lines.append("%-30s %-15s %-4s %7.1f %9d  %s" % (r["piece"], r["check"], r["side"], r["cm"], r["placements"],
                                                          r.get("mount", r.get("cmode", ""))))
    open(os.path.join(C.OUT, "bounds_kit.txt"), "w").write("\n".join(lines) + "\n")
    summ = collections.Counter(r["check"] for r in rows)
    # one line per class (MID walls 10 cm tall is one fact, not 60)
    cls = collections.defaultdict(list)
    for r in rows:
        cls[(r["check"], r["side"], r["cm"])].append(r["piece"])
    lines.append("")
    lines.append("classes (check, side, cm): pieces")
    for (ch, sd, cm), ps in sorted(cls.items(), key=lambda kv: -len(kv[1])):
        if len(ps) > 2:
            lines.append("  %-15s %-4s %6.1f cm  %3d pieces: %s" % (ch, sd, cm, len(ps), ", ".join(ps[:8])))
    open(os.path.join(C.OUT, "bounds_kit.txt"), "w").write("\n".join(lines) + "\n")
    print("kit bounds: %d rows over %d pieces  %s" % (len(rows), len(by), dict(summ)))
    seen = []
    for r in rows:
        if r["piece"] in seen or len(seen) >= npng:
            continue
        seen.append(r["piece"])
        spec = K.P[r["piece"]]
        draw(K, r["piece"], spec, mount_of(r["piece"], spec, mounts),
             os.path.join(C.OUT, "bounds", r["piece"] + ".png"), by[r["piece"]], mids)
    for line in lines[:31]:
        print(line)
    print("-> %s/bounds_kit.txt, bounds/<piece>.png (%d)" % (C.OUT, len(seen)))


if __name__ == "__main__":
    main()
