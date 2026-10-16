#!/usr/bin/env python3
"""calibrate.py -- the audit against what the game measured.

  contacts  every contact point of the in-game capsule sweep (reference/tmp/passcheck.gd results, pc3_<idx>.json)
            must lie on the assembled collision (verifies assemble.py's transforms and collision rules)
  walktest  walktest.gd replicated offline (same doors, same route on the folk graph, the walksim capsule) and
            compared with the in-game door walks of reference/tmp/pass3.out

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/calibrate.py [contacts|walktest|all] [SKY-022 ...]
"""
import json
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as A  # noqa: E402
import common as C  # noqa: E402
import rays  # noqa: E402
import walksim  # noqa: E402

PC_DIR = "/home/deck/.claude/jobs/204e5d66/tmp"
PASS3 = os.path.join(C.ROOT, "reference", "tmp", "pass3.out")
IDX = {"SKY-099": 98, "SKY-078": 77, "SKY-071": 70, "SKY-022": 21}
FACE_DIR = [(0, 0, 1), (1, 0, 0), (0, 0, -1), (-1, 0, 0)]


def vec(s):
    return np.array([float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", str(s))])


# ------------------------------------------------------------------ contacts
def contacts(iid, g=None, R=None):
    g = g or A.build(iid, render=False)
    R = R or rays.Rays(g.ctri)
    f = os.path.join(PC_DIR, "pc3_%d.json" % IDX[iid])
    if not os.path.exists(f):
        f = os.path.join(C.ROOT, "reference", "tmp", "pc2_%d.json" % IDX[iid])
    res = json.load(open(f))
    rng = np.random.default_rng(1)
    dirs = rng.normal(size=(4000, 3))
    out = {"on": 0, "off": 0, "skipped": 0, "by": {}}
    for e in res["blocked"]:
        if e[3] not in ("WarrenBody", "solid", "FenceBody"):
            out["skipped"] += 1               # (larks, the player, rest-info-less hits: not modelled / no point)
            continue
        p = vec(e[2])
        t, prim, _ = R.cast(np.tile(p, (len(dirs), 1)), dirs, 0.2)
        k = int(np.argmin(t))
        ok = bool(t[k] < 0.01)
        out["on" if ok else "off"] += 1
        want = {"WarrenBody": "warren", "solid": "bridge", "FenceBody": "fence"}[e[3]]
        got = g.csrc[prim[k]] if prim[k] >= 0 else None
        kind = None if got is None else ("bridge" if got == A.BRIDGE else "fence" if got == A.FENCE else
                                         "deck" if got == A.DECK else "warren")
        b = out["by"].setdefault(e[3], [0, 0, 0])
        b[0] += 1
        b[1] += ok
        b[2] += ok and kind == want
    return out


# ------------------------------------------------------------------ walktest replica
def folk_graph(side):
    w = side["walk"]
    nodes = np.array([[n[0], n[1], n[2]] for n in w["nodes"]], float)
    adj = [[] for _ in range(len(nodes))]
    for a, b in w["edges"]:
        adj[int(a)].append(int(b))
        adj[int(b)].append(int(a))
    return nodes, adj


def route(nodes, adj, frm, to):
    """walktest.gd _route: nearest nodes (flat + 10 |dy|), BFS, the door point appended"""
    df = np.hypot(nodes[:, 0] - frm[0], nodes[:, 2] - frm[2]) + np.abs(nodes[:, 1] - frm[1]) * 10
    dt = np.hypot(nodes[:, 0] - to[0], nodes[:, 2] - to[2]) + np.abs(nodes[:, 1] - to[1]) * 10
    a, b = int(np.argmin(df)), int(np.argmin(dt))
    prev = {a: -1}
    q = [a]
    h = 0
    while h < len(q):
        u = q[h]
        h += 1
        if u == b:
            break
        for v in adj[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    if b not in prev:
        return []
    out = [list(to)]
    u = b
    while u != -1:
        out.insert(0, nodes[u].tolist())
        u = prev[u]
    return out


def walktest_doors(side, n=10):
    tr = np.array(side["travel"][:3], float)
    fr = side["frame"]
    cand = []
    for k, d in enumerate(side["doors"]):
        if int(d[3]) > 0:
            continue
        dx, _, dz = FACE_DIR[int(d[4]) & 3]
        c = np.array([fr["x0"] + 3.0 * int(d[1]) + 1.5, 0.0, fr["z0"] + 3.0 * int(d[2]) + 1.5])
        p = c + np.array([dx, 0, dz]) * 2.1
        p[1] = 3.2 * int(d[3])
        cand.append((k, p, float(np.linalg.norm(p - tr))))
    cand.sort(key=lambda c: c[2])
    out = []
    for q in range(n):
        if not cand:
            break
        out.append(cand[int(float(q + 1) / (n + 1) * len(cand))])
    return out


def game_walks():
    """pass3.out -> {iid: [[door, 'ok', t] | [door, 'stuck', (x, y, z), wp, #]]}"""
    out = {}
    if not os.path.exists(PASS3):
        return out
    for line in open(PASS3):
        m = re.search(r'"result_str": "(.*)"', line)
        if not m:
            continue
        s = m.group(1).replace('\\"', '"')
        iid = re.search(r'"(SKY-\d+)"', s).group(1)
        res = []
        for part in re.findall(r"\[(\d+), \"(ok|stuck)\"(.*?)\](?=, \[|\]\])", s):
            door, kind, rest = int(part[0]), part[1], part[2]
            if kind == "ok":
                res.append([door, "ok"])
            else:
                pts = re.findall(r"\(([^)]*)\)", rest)
                res.append([door, "stuck", vec(pts[0]).tolist(), vec(pts[1]).tolist(),
                            int(re.search(r'"#", (\d+)', rest).group(1))])
        out[iid] = res
    return out


def walktest(iid, g=None, R=None, n=10, soft=0.0):
    g = g or A.build(iid, render=False)
    R = R or rays.Rays(g.ctri)
    side = g.W["side"]
    nodes, adj = folk_graph(side)
    tr = np.array(side["travel"][:3], float)
    doors = walktest_doors(side, n)
    paths = [route(nodes, adj, tr, d[1]) for d in doors]
    res, bt, trace = walksim.walk_paths(R, tr, [p if p else [d[1].tolist()] for p, d in zip(paths, doors)], soft=soft)
    out = []
    for d, p, r, k in zip(doors, paths, res, range(len(doors))):
        e = {"door": d[0], "result": r[0], "hazards": int(bt.hz_n[k])}
        hz = [h for h in bt.hz_list if h[0] == k]
        e["hazard_at"] = [h[2].tolist() for h in hz]
        if hz:
            e["hazard"] = "; ".join(g.label(h[1], h[2]) + " at " + str(np.round(h[2], 1).tolist()) for h in hz[:4])
        if r[0] != "ok":
            e["at"] = r[1]
            e["wp"] = r[2]
            e["wp_at"] = p[r[2]] if p else None
            bp = bt.block_prim[k]
            e["blocker"] = g.label(bp, bt.block_at[k]) if bp >= 0 else None
            e["block_at"] = np.round(bt.block_at[k], 2).tolist()
            e["fell"] = bool(bt.fell[k])
            e["path_len"] = len(p)
        out.append(e)
    return out


def door_point(side, k):
    d = side["doors"][k]
    fr = side["frame"]
    dx, _, dz = FACE_DIR[int(d[4]) & 3]
    return (round(fr["x0"] + 3.0 * int(d[1]) + 1.5 + dx * 2.1, 2), round(3.2 * int(d[3]), 2),
            round(fr["z0"] + 3.0 * int(d[2]) + 1.5 + dz * 2.1, 2))


def compare(iid, mine, game, side):
    """per door (matched by its point: doors sharing a cell and face are one door): same verdict? stuck spots near?"""
    gd = {door_point(side, r[0]): r for r in game}
    rows = []
    agree = 0
    for e in mine:
        gr = gd.get(door_point(side, e["door"]))
        gv = gr[1] if gr else "?"
        same = gv == ("ok" if e["result"] == "ok" else "stuck")
        near = None
        if same and gv == "stuck":
            gp = np.array(gr[2])
            mp = np.array(e["at"]) + [0, C.ORIGIN_ABOVE_FEET, 0]
            near = round(float(np.hypot(gp[0] - mp[0], gp[2] - mp[2])), 2)
        agree += same
        rows.append((e["door"], gv, e["result"], near, gr[2] if gr and gv == "stuck" else None,
                     e.get("at"), e.get("blocker"), e.get("wp")))
    return agree, rows


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("SKY") else "all"
    iids = [a for a in sys.argv[1:] if a.startswith("SKY")] or list(IDX)
    gw = game_walks()
    for iid in iids:
        g = A.build(iid, render=False)
        R = rays.Rays(g.ctri)
        if mode in ("contacts", "all"):
            c = contacts(iid, g, R)
            print("%s contacts: %d on the collision, %d off, %d skipped (larks/player/no point); by body %s"
                  % (iid, c["on"], c["off"], c["skipped"], c["by"]))
        if mode in ("walktest", "all"):
            import time
            t = time.time()
            t = time.time()
            strict = walktest(iid, g, R, soft=0.0)
            lenient = walktest(iid, g, R, soft=walksim.SOFT)
            v = verdicts(g.W["side"], strict, lenient, gw.get(iid, []))
            n_ok = sum(1 for x in v if x[1].startswith("agree"))
            print("%s walktest: %d/%d explained (%.1f s)" % (iid, n_ok, len(v), time.time() - t))
            for x in v:
                print("   door %5d  %-28s %s" % x)


def verdicts(side, strict, lenient, game):
    """per door: agree (both ok / stuck at the same spot or on the same graph edge) | agree, risky lip (the game
    stuck where the strict model refuses an edge the lenient one takes: stochastic in game) | DISAGREE"""
    gd = {door_point(side, r[0]): r for r in game}
    out = []
    for es, el in zip(strict, lenient):
        gr = gd.get(door_point(side, el["door"]))
        if gr is None:
            out.append((el["door"], "no game result", ""))
            continue
        if gr[1] == "ok":
            v = "agree (ok)" if el["result"] == "ok" else "DISAGREE (game ok)"
            note = "" if el["result"] == "ok" else "sim stuck at %s by %s" % (el.get("at"), el.get("blocker"))
            if el["result"] == "ok" and es["result"] != "ok":
                note = "strict model stuck at %s (%s): a risky lip the game took" % (es.get("at"), es.get("blocker"))
            out.append((el["door"], v, note))
            continue
        gp = np.array(gr[2])
        gwp = gr[4]

        def near(pts):
            return any(np.hypot(p[0] - gp[0], p[2] - gp[2]) < 2.5 for p in pts if p is not None)
        if el["result"] != "ok" and (near([el["at"]]) or el.get("wp") == gwp):
            out.append((el["door"], "agree (stuck)", "game %s, sim %s, wp %s/%s, blocker %s" % (
                gp.tolist(), el["at"], gwp, el.get("wp"), el.get("blocker"))))
        elif (es["result"] != "ok" and near([es["at"]])) or near(el.get("hazard_at", [])):
            out.append((el["door"], "agree (risky lip)", "game stuck %s; strict model: %s" % (
                gp.tolist(), es.get("blocker") if es["result"] != "ok" else el.get("hazard"))))
        else:
            out.append((el["door"], "DISAGREE (game stuck)", "game %s wp %s; lenient %s %s; strict %s %s" % (
                gp.tolist(), gwp, el["result"], el.get("at"), es["result"], es.get("at"))))
    return out


if __name__ == "__main__":
    main()
