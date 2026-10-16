#!/usr/bin/env python3
"""
make_markets.py -- godot_project/remake/markets/flea_markets.json (research/flea_markets/00_plan.md §3.2).

Two ways in:
  * `write(sites)` from tools/map_expanded.py --game-data: `sites` = {town: site dict from tools/settlegen/market.py}
    (the full geometry: site, floor, apron, mooring polygons; stalls; sheds; lot rows; poles; tent slots; deadmen ...).
  * `python3 tools/markets/make_markets.py --spec-only`: no geometry, every market at its town's centre (law
    settlements.json) with its stalls listed by kind only. The pure model (FleaCalendar / FleaVendors) and its tests
    need nothing more; the generator's run replaces this file.

Coordinates: every list in a market's own site frame (u along the frontage, v away from the road, metres) unless the
key says `_sx` (ring s, x). `frame` = {s, x, yaw}: world = (s, x) + R(yaw) (u, v) with s' = s + u cos(yaw) - v sin(yaw),
x' = x + u sin(yaw) + v cos(yaw).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
sys.path.insert(0, HERE)
import markets_spec as MS  # noqa: E402

OUT = os.path.join(ROOT, "godot_project", "remake", "markets", "flea_markets.json")
LAW = os.path.join(ROOT, "godot_project", "remake", "law", "settlements.json")
KIND_ID = {"shed": 0, "open": 1, "open_double": 2, "food": 3}


def _base(m):
    return {"id": m["id"], "town": m["town"], "name": m["name"], "sign": m["sign"], "region": m["region"],
            "tier": m["tier"], "pop": m["pop"], "draw": m["draw"], "great_fair_month": m["great_fair_month"],
            "mooring_tier": m["mooring"], "tents_min": m["tents_min"]}


def _spec_stalls(m):
    out = []
    for kind in ("shed", "open", "open_double", "food"):
        for _ in range(m["kinds"][kind]):
            out.append([0.0, 0.0, 0.0, KIND_ID[kind], -1, -1])
    return out


def write(sites=None, out=OUT):
    """sites: {town: market.py site dict} (None: spec only)"""
    law = {s["name"]: s for s in json.load(open(LAW))["settlements"]}
    ms = []
    for m in MS.MARKETS:
        e = _base(m)
        site = (sites or {}).get(m["town"])
        if site:
            e.update(site)
            e["sited"] = True
        else:
            c = law[m["town"]]["centre"]
            e.update({"sited": False, "frame": {"s": c[0], "x": c[1], "yaw": 0.0}, "stalls": _spec_stalls(m),
                      "lot": {"spaces": m["spaces"], "accessible": max(1, m["spaces"] // 25), "rows": []}})
        k = {"shed": 0, "open": 0, "open_double": 0, "food": 0}
        for st in e["stalls"]:
            k[["shed", "open", "open_double", "food"][int(st[3])]] += 1
        e["stats"] = dict(e.get("stats", {}), stalls=len(e["stalls"]), permanent=k["shed"] + k["food"] // 2, kinds=k,
                          spaces=e["lot"]["spaces"])
        ms.append(e)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = {"version": 1, "_about": "The 22 flea markets (research/flea_markets/00_plan.md §3.2). Written by "
                                  "tools/markets/make_markets.py (from map_expanded --game-data); read by FleaData.",
           "categories": MS.CATEGORIES, "markets": ms}
    with open(out + ".tmp", "w") as f:
        json.dump(doc, f, separators=(",", ":"))
    os.replace(out + ".tmp", out)
    return doc


if __name__ == "__main__":
    if "--spec-only" not in sys.argv:
        sys.exit("usage: make_markets.py --spec-only   (the sited file comes from map_expanded --game-data)")
    d = write(None)
    print("%s: %d markets, %d stalls" % (OUT, len(d["markets"]), sum(m["stats"]["stalls"] for m in d["markets"])))
