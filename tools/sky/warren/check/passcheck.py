#!/usr/bin/env python3
"""passcheck.py ISLAND RESULT.json : which kit pieces the player's capsule hit on a walk-graph edge.

RESULT.json is reference/tmp/passcheck.gd's result: {"blocked": [[a, b, hit point, collider, fraction], ...]}, points in
the island frame.  Each hit point is matched to the placements whose box (pieces.json bounds, placed as FORMAT.md v3
says) lies within 6 cm of it; the report counts pieces by id."""
import collections, json, math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import lods  # noqa: E402  (its warren reader)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
PJ = json.load(open(os.path.join(ROOT, "godot_project", "remake", "sky", "warrens", "pieces.json")))["pieces"]


def vec(s):
    return [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", str(s))]


def boxes(iid):
    side, civ, x0, z0, cell, nx, nz, ids, recs = lods.read_warren(iid)
    by = collections.defaultdict(list)
    for r in recs:
        pid = ids[r["p"]]
        b = PJ.get(pid, {}).get("bounds")
        if not b:
            continue
        fl = int(r["rf"])
        rot, mount, quarter = fl & 3, (fl >> 4) & 3, fl >> 6
        cx, cz = x0 + 3 * int(r["i"]) + 1.5, z0 + 3 * int(r["j"]) + 1.5
        y = 3.2 * int(r["k"]) + 0.8 * quarter
        a = rot * math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        off = {0: (0, 0), 1: (0, 1.5), 2: (1.5, 1.5)}[mount]
        pts = []
        for px in (b[0][0], b[1][0]):
            for pz in (b[0][2], b[1][2]):
                lx, lz = px + off[0], pz + off[1]
                # Basis(UP, a) * (lx, lz): x' = x cos + z sin, z' = -x sin + z cos
                pts.append((cx + lx * ca + lz * sa, cz - lx * sa + lz * ca))
        xs = [p[0] for p in pts]
        zs = [p[1] for p in pts]
        box = (min(xs), y + b[0][1], min(zs), max(xs), y + b[1][1], max(zs))
        by[(int(r["i"]), int(r["j"]))].append((pid, box, PJ[pid].get("kind"), PJ[pid].get("collide")))
    return by, x0, z0


def main():
    iid, res = sys.argv[1], json.load(open(sys.argv[2]))
    by, x0, z0 = boxes(iid)
    count = collections.Counter()
    where = {}
    unmatched = 0
    for e in res["blocked"]:
        p = vec(e[2])
        i, j = int((p[0] - x0) // 3), int((p[2] - z0) // 3)
        hits = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for pid, bx, kind, col in by.get((i + di, j + dj), []):
                    d = max(bx[0] - p[0], p[0] - bx[3], bx[1] - p[1], p[1] - bx[4], bx[2] - p[2], p[2] - bx[5], 0.0)
                    if d < 0.06 and kind not in ("ground", "slab", "roof", "stair"):
                        hits.append(pid)
        if not hits:
            unmatched += 1
            count["(no piece: %s)" % e[3]] += 1
        for pid in set(hits):
            count[pid] += 1
            where.setdefault(pid, (round(p[0], 1), round(p[1], 1), round(p[2], 1)))
    print(iid, "edges tested", res.get("edges_tested"), "blocked", len(res["blocked"]), "unmatched", unmatched)
    for pid, n in count.most_common(40):
        k = PJ.get(pid, {})
        print("  %4d  %-32s kind %-10s collide %-6s e.g. %s" % (n, pid, k.get("kind"), k.get("collide"), where.get(pid)))


if __name__ == "__main__":
    main()
