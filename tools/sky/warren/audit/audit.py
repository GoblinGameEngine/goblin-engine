#!/usr/bin/env python3
"""audit.py -- every offline check on a warren island, without the game.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/audit.py SKY-022 [SKY-071 ...] [--all] [--wdir DIR]
        [--skip pierce,zfight,...] [--quiet]

Writes reference/tmp/audit/<id>.json (summary + every hotspot: check, kind, xyz, cell (i, j, level), pieces, value)
and <id>.png (top-down heat map: collision heights, the walk graph, failed edges, unreachable doors, hotspots by
check), prints a short summary.  --all: every island with a warren file, then reference/tmp/audit/all.json totals.
Checks: holes, cracks, manifold, zfight, floating, intrusion, walk -- see checks.py."""
import collections
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble as A  # noqa: E402
import checks as K  # noqa: E402
import common as C  # noqa: E402
import img  # noqa: E402
import meshlib as M  # noqa: E402
import rays  # noqa: E402
import walkcheck as WC  # noqa: E402

COL = {"holes": (220, 0, 200), "cracks": (200, 110, 0), "manifold": (120, 0, 160), "zfight": (0, 170, 200),
       "floating": (120, 170, 0), "intrusion": (0, 60, 230), "walk": (230, 0, 0)}


def run(iid, wdir=None, skip=(), out_dir=None, png=True, quiet=False):
    out_dir = out_dir or C.OUT
    os.makedirs(out_dir, exist_ok=True)
    T = {}
    t0 = time.time()
    g = A.build(iid, wdir=wdir)
    T["assemble"] = time.time() - t0
    kit = A.kit()
    t = time.time()
    R = rays.Rays(g.ctri)
    deck = g.ctri[g.csrc == A.DECK]
    RS = rays.Rays(np.concatenate([g.rtri, deck.astype(np.float32)]))       # render + the deck
    RR = RS
    gp = np.concatenate([g.rsrc, np.full(len(deck), -2, np.int32)])          # group of each RS triangle
    g.gp = gp
    T["bvh"] = time.time() - t
    stats = {}
    hot = []

    def do(name, f):
        if name in skip:
            return None
        t = time.time()
        r = f()
        T[name] = round(time.time() - t, 2)
        return r
    W = do("walk_sim", lambda: WC.run(g, R))
    if W is not None:
        hot += K.walk(g, W)
        hot += do("holes_walk", lambda: K.holes_walk(g, R, W)) or []
    hot += do("holes_roof", lambda: K.holes_roof(g, RR)) or []
    hot += do("cracks", lambda: K.cracks(g, RR, kit)) or []
    hot += do("manifold", lambda: K.manifold(g, kit)) or []
    z = do("pairs", lambda: K.piece_pairs(g, kit, RS, gp))
    if z:
        hot += z[0]
        stats["pairs"] = z[1]
    hot += do("floating", lambda: K.floating(g, kit, RS, gp, None)) or []
    hot += do("into_room", lambda: K.into_room(g, kit, RS, gp)) or []
    if W is not None:
        hot += do("riser_gaps", lambda: K.riser_gaps(g, RS, W)) or []
    if W is not None:
        hot += do("intrusion", lambda: K.intrusions(g, kit, W, R, RS, gp)) or []
    T["total"] = round(time.time() - t0, 2)
    summ = collections.Counter((h["check"], h["kind"]) for h in hot)
    walk = {}
    if W is not None:
        ds = collections.Counter(d["status"] for d in W["doors"])
        cellq = np.array([W["edge_kind"][e] == "cell" for e in W["edge_id"]], bool)
        es = collections.Counter(W["edge_status"][cellq])
        vs = collections.Counter(W["edge_status"][~cellq])
        walk = {"doors": len(W["doors"]), "doors_status": dict(ds),
                "doors_ok": ds.get("ok", 0), "doors_reachable": len(W["doors"]) - sum(
                    v for k, v in ds.items() if k.startswith("unreachable") or k.startswith("no node")),
                "edges_tested_directed": int(cellq.sum()), "edges_status": dict(es),
                "virtual_edges_status": dict(vs),
                "nodes": int(len(W["nodes"])), "nodes_reached": len(W["reach"]), "nodes_reached_safe": len(W["reach_safe"]),
                "floor_missing_rooms": sum(1 for d in W["doors"] if d.get("floor_missing"))}
        # the market moorings' stations (tools/sky/warren/moorings.py): the walk from the street through the hall and
        # the passage onto the berth deck -- its last node reached from the arrival over passing edges
        ms = [m for m in (g.W["side"].get("moorings") or []) if m.get("kind") in ("pax", "cargo")]
        walk["moor_stations"] = len(ms)
        walk["moor_reached"] = sum(1 for m in ms if m.get("walk") and m["walk"][-1] in W["reach"])
        walk["moor_safe"] = sum(1 for m in ms if m.get("walk") and m["walk"][-1] in W["reach_safe"])
        walk["moor_unreached"] = [[m["kind"], m["side"], m["cell"], bool(m.get("connected"))] for m in ms
                                  if not (m.get("walk") and m["walk"][-1] in W["reach"])]
    res = {"island": iid, "civ": g.W["civ"], "render_tris": int(len(g.rtri)), "collision_tris": int(len(g.ctri)),
           "placements": int(len(g.recs)), "times_s": {k: round(float(v), 2) for k, v in T.items()},
           "summary": {"%s/%s" % k: v for k, v in sorted(summ.items())}, "walk": walk,
           "by_check": dict(collections.Counter(h["check"] for h in hot)), "stats": stats,
           "top_pieces": _top_pieces(hot), "hotspots": hot}
    json.dump(res, open(os.path.join(out_dir, iid + ".json"), "w"), indent=0, default=_js)
    if png:
        heatmap(g, R, W, hot, os.path.join(out_dir, iid + ".png"))
    if not quiet:
        print_summary(res)
    return res


def _js(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def _top_pieces(hot, n=12):
    c = collections.defaultdict(collections.Counter)
    for h in hot:
        for p in h["pieces"]:
            c[h["check"] + "/" + h["kind"]][p] += 1
    return {k: v.most_common(n) for k, v in c.items()}


def print_summary(res):
    w = res["walk"]
    print("%s (%s): %d placements, %d render / %d collision tris, %.1f s" % (
        res["island"], res["civ"], res["placements"], res["render_tris"], res["collision_tris"], res["times_s"]["total"]))
    if w:
        print("  walk: doors %d: ok %d, %s | directed edges %d: %s | nodes reached %d/%d (safe %d) | rooms without a"
              " floor behind the door %d" % (w["doors"], w["doors_ok"], {k: v for k, v in w["doors_status"].items()
                                                                           if k != "ok"}, w["edges_tested_directed"],
                                             w["edges_status"], w["nodes_reached"], w["nodes"], w["nodes_reached_safe"],
                                             w["floor_missing_rooms"]))
        if "moor_stations" in w:
            print("  moorings: stations %d, berths reached %d (safe %d), unreached %s" % (
                w["moor_stations"], w["moor_reached"], w["moor_safe"], w["moor_unreached"]))
    for k, v in res["summary"].items():
        tp = res["top_pieces"].get(k, [])[:3]
        print("  %-28s %6d   %s" % (k, v, ", ".join("%s %d" % x for x in tp)))
    print("  times %s" % res["times_s"])


GEOM = {"walk", "holes", "floating"}
GEOM_KINDS = {"pass", "clearance", "into_room", "render_clear", "missing_wall", "riser_gap", "see_through", "isolated",
              "unsupported", "room_floor_missing", "roof_open", "no_floor", "floor_off"}


def _base(g, R, px):
    pl = img.Plan(g.x0, g.z0, g.nx * C.CELL, g.nz * C.CELL, px)
    xs = g.x0 + (np.arange(pl.H) + 0.5) * px
    zs = g.z0 + (np.arange(pl.W) + 0.5) * px
    X, Z = np.meshgrid(xs, zs, indexing="ij")
    y, prim, n = R.down(np.stack([X.ravel(), Z.ravel()], 1), 80.0, 200.0)
    y = y.reshape(X.shape)
    src = np.where(prim >= 0, g.csrc[np.maximum(prim, 0)], 99).reshape(X.shape)
    rgb = np.full(X.shape + (3,), 255, np.uint8)
    ok = np.isfinite(y)
    if ok.any():
        lo, hi = np.percentile(y[ok], 2), np.percentile(y[ok], 98)
        v = np.clip((np.where(ok, y, lo) - lo) / max(hi - lo, 1e-3), 0, 1)
        shade = (225 - 125 * v).astype(np.uint8)
        rgb[ok] = np.stack([shade[ok]] * 3, 1)
        dk = ok & (src == A.DECK)
        rgb[dk] = (236, 226, 200)
    pl.raster(rgb)
    return pl


def heatmap(g, R, W, hot, path, px=0.5):
    """<id>.png: walk + geometry problems (holes, floating, intrusions, missing walls) as marks;
    <id>_render.png: render-only problems (z-fighting, piercing, cracks) as a per-cell density"""
    pl = _base(g, R, px)
    if W is not None:
        N = W["nodes"]
        E = W["edges_all"]
        for (a, b), k in zip(E, W["edge_kind"]):
            if k in ("cell",):
                pl.line(N[a], N[b], (160, 200, 235))
        st = collections.defaultdict(set)
        for e in W["bad_edges"]:
            st[e["edge"]].add(e["status"])
        for e, s in st.items():
            a, b = E[e]
            col = (230, 0, 0) if s - {"risky", "drop"} else (255, 150, 0)
            pl.line(N[a], N[b], col, 3)
        for d in W["doors"]:
            if d["status"] == "risky":
                pl.dot(d["centre"], (255, 170, 0), 1)
            elif d["status"] != "ok":
                pl.dot(d["centre"], (230, 0, 0), 3, outline=(90, 0, 0))
        pl.dot(N[W["start"]], (0, 200, 0), 6, outline=(0, 0, 0))
    cnt = collections.Counter()
    for hh in hot:
        if hh["check"] == "walk" or hh["kind"] not in GEOM_KINDS:
            continue
        cnt[hh["kind"]] += 1
        pl.cross(hh["at"], KCOL.get(hh["kind"], (0, 0, 0)), 3, 1)
    items = [((0, 200, 0), "travel point"), ((230, 0, 0), "edge blocked / door unreachable or entry blocked"),
             ((255, 150, 0), "edge risky (a lip the game takes only sometimes) / door reached only over one")]
    items += [(KCOL.get(k, (0, 0, 0)), "x %s (%d)" % (k, v)) for k, v in cnt.most_common()]
    pl.legend(items, "%s  rows = +X (south) down, columns = +Z (west) right; %.1f m/px; grey = collision height" %
              (g.iid, px))
    pl.save(path)
    # render problems: density per cell
    pl = _base(g, R, px)
    from PIL import Image
    dens = collections.defaultdict(collections.Counter)
    for hh in hot:
        if hh["kind"] in ("coplanar", "pierce", "see_through", "seam", "dup_across"):
            dens[hh["kind"]][(hh["cell"][0], hh["cell"][1])] += 1
    cols = {"coplanar": (0, 170, 200), "pierce": (0, 60, 230), "see_through": (200, 110, 0), "seam": (200, 110, 0),
            "dup_across": (120, 0, 160)}
    im = pl.im.convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(ov)
    s = C.CELL / px
    for k, c in dens.items():
        mx = max(c.values())
        for (i, j), n in c.items():
            a = int(60 + 170 * min(n / max(mx * 0.5, 1), 1))
            dr.rectangle([j * s, i * s, (j + 1) * s - 1, (i + 1) * s - 1], fill=cols[k] + (a,))
    pl.im = Image.alpha_composite(im, ov).convert("RGB")
    pl.dr = ImageDraw.Draw(pl.im)
    pl.legend([(cols[k], "%s (%d cells, %d)" % (k, len(c), sum(c.values()))) for k, c in dens.items()],
              "%s render problems per 3 m cell (darker = more)" % g.iid)
    pl.save(path.replace(".png", "_render.png"))


KCOL = {"pass": (0, 60, 230), "clearance": (0, 60, 230), "into_room": (0, 120, 255), "render_clear": (90, 140, 255),
        "missing_wall": (200, 110, 0), "riser_gap": (200, 60, 0), "see_through": (200, 110, 0), "isolated": (120, 170, 0),
        "unsupported": (120, 170, 0), "room_floor_missing": (220, 0, 200), "roof_open": (220, 0, 200),
        "no_floor": (220, 0, 200), "floor_off": (220, 0, 200)}


def all_ids():
    return sorted(f[:-7] for f in os.listdir(C.WR) if f.startswith("SKY-") and f.endswith(".bin.gz"))


def main():
    a = sys.argv[1:]
    skip = tuple(a[a.index("--skip") + 1].split(",")) if "--skip" in a else ()
    wdir = a[a.index("--wdir") + 1] if "--wdir" in a else None
    ids = [x for x in a if x.startswith("SKY-")]
    if "--all" in a:
        ids = all_ids()
    tot = collections.Counter()
    walk = collections.Counter()
    per = {}
    t0 = time.time()
    for iid in ids:
        try:
            r = run(iid, wdir=wdir, skip=skip, quiet="--quiet" in a or "--all" in a)
        except Exception as e:                       # (one bad island must not stop --all)
            import traceback
            traceback.print_exc()
            print(iid, "FAILED", repr(e))
            per[iid] = {"error": repr(e)}
            continue
        tot.update(r["summary"])
        w = r["walk"]
        if w:
            walk.update({"doors": w["doors"], "doors_ok": w["doors_ok"], "doors_reachable": w["doors_reachable"],
                         "floor_missing_rooms": w["floor_missing_rooms"], "moor_stations": w.get("moor_stations", 0),
                         "moor_reached": w.get("moor_reached", 0), "moor_safe": w.get("moor_safe", 0)})
            for k, v in w["doors_status"].items():
                walk["door " + k] += v
            for k, v in w["edges_status"].items():
                walk["edge " + k] += v
        per[iid] = {"summary": r["summary"], "walk": w, "s": r["times_s"]["total"]}
        if "--all" in a:
            print("%s %5.1f s  doors %d ok %d  %s" % (iid, r["times_s"]["total"], w.get("doors", 0), w.get("doors_ok", 0),
                                                     " ".join("%s=%d" % kv for kv in sorted(r["by_check"].items()))))
    if len(ids) > 1:
        res = {"islands": len(ids), "seconds": round(time.time() - t0, 1), "totals": dict(tot), "walk": dict(walk),
               "per_island": per}
        json.dump(res, open(os.path.join(C.OUT, "all.json"), "w"), indent=0, default=_js)
        print("TOTAL %d islands, %.0f s" % (len(ids), time.time() - t0))
        print("  walk", dict(walk))
        for k, v in sorted(tot.items()):
            print("  %-28s %7d" % (k, v))


if __name__ == "__main__":
    main()
