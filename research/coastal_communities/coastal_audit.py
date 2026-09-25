#!/usr/bin/env python3
"""Normalise coastal catalog traits to what the coastal generators read (deck, 2026-09-25).

  coastal_audit.py            report what would change
  coastal_audit.py --write    rewrite remake/catalog/<ID>.json in place

Covers every coastal prefix. Rules (from the deck's generator notes):
  houses   archetype -> coastal set by kind; foundation "piles" for raised houses; walls vocabulary;
           single houses get porch "stacked" (side piazzas).
  hotel/condo  roof flat|hip|hip_tile|mansard; balconies none|continuous|per_room.
  lighthouse   paint -> {bands: [hex...]}.
  industry     on_pilings true when the inventory lot is over water.
  all          every colour must be #rrggbb."""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAT = os.path.join(ROOT, "remake", "catalog")
INV = json.load(open(os.path.join(ROOT, "remake", "inventory", "coastal_inventory.json")))
PREFIXES = sorted({s["id"].split("-")[0] for s in INV["structures"] + INV["walks"]})
OVER_WATER = {s["id"] for s in INV["structures"] if s.get("over_water")}
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")

HOUSE_KINDS = {"house", "cottage", "beachhouse", "bungalow", "shingle", "singlehouse", "rowhouse"}
INDUSTRY = {"cannery", "fishhouse", "icehouse", "shed", "boatyard", "warehouse"}
COASTAL_ARCH = {"raised_beach_house", "contemporary_beach", "shingle_style", "nantucket_cape", "charleston_single",
                "lowcountry", "california_bungalow", "spanish_revival", "a_frame", "cottage_lake"}
INLAND_ARCH = {"i_house", "gable_front", "upright_and_wing", "foursquare", "bungalow", "workers_cottage", "queen_anne",
               "italianate", "cape_cod", "ranch", "minimal_traditional", "side_gable_cottage", "shotgun",
               "dutch_colonial", "tudor_revival", "split_level", "american_small_house", "prairie_box"}
WALLS = {"clapboard", "fiber_cement", "shingle", "cedar_shingle", "vinyl", "stucco", "brick", "board_and_batten",
         "wood", "block"}
WALL_MAP = {"wood_shingle": "shingle", "aluminum": "vinyl", "drop_siding": "clapboard", "asbestos_shingle": "shingle",
            "half_timber": "stucco", "stone": "block", "log": "wood", "concrete": "block", "metal": "vinyl"}
HOTEL_ROOF = {"flat", "hip", "hip_tile", "mansard"}
HOTEL_ROOF_MAP = {"parapet": "flat", "gable": "hip", "shed": "flat", "tile": "hip_tile"}
BALC_MAP = {"corner": "per_room", "glass": "per_room"}
# Sullivan's Island post-Hugo houses, beach colonies and anything the brief calls raised / on piles
RAISED_RE = re.compile(r"raised (on|over)|on piles|post-hugo|stilts|over carports|over tuck-under|over open", re.I)


def fix_colors(obj, log, path="colors"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("#") and not HEX.match(v):
                log.append(f"{path}.{k} {v!r} not hex")
            elif isinstance(v, (dict, list)):
                fix_colors(v, log, f"{path}.{k}")


def audit(rec):
    tr = rec.setdefault("traits", {})
    kind = rec.get("kind", "")
    log = []

    def setv(key, new, why=""):
        old = tr.get(key)
        if old != new:
            tr[key] = new
            log.append(f"{key}: {old!r} -> {new!r}{' (' + why + ')' if why else ''}")

    if kind in HOUSE_KINDS:
        arch = tr.get("archetype")
        walls = tr.get("walls")
        want = arch
        if kind == "singlehouse":
            want = "charleston_single"
        elif kind == "shingle":
            want = "nantucket_cape" if arch in ("cape_cod", "side_gable_cottage", "i_house", "nantucket_cape") else (
                arch if arch in ("queen_anne", "shingle_style") else "shingle_style")
        elif kind == "bungalow" and arch in ("bungalow", "gable_front", "workers_cottage"):
            want = "california_bungalow"
        elif kind == "beachhouse" and arch in INLAND_ARCH and arch not in ("queen_anne", "tudor_revival", "italianate"):
            want = "contemporary_beach"
        elif arch == "cape_cod" and walls == "wood_shingle" and rec.get("coast") == "east":
            want = "nantucket_cape"
        if want not in COASTAL_ARCH | INLAND_ARCH:
            want = "contemporary_beach"
        setv("archetype", want)
        if walls in WALL_MAP:
            setv("walls", WALL_MAP[walls])
        elif walls and walls not in WALLS:
            setv("walls", "clapboard", "unknown wall")
        raised = RAISED_RE.search(rec.get("brief", ""))
        if raised and tr.get("foundation") != "piles":
            setv("foundation", "piles", "raised")
        if kind == "singlehouse":
            p = dict(tr.get("porch") or {})
            if p.get("type") != "stacked":
                p.update(type="stacked", posts=p.get("posts", "columns"), rail=p.get("rail", "spindle"))
                setv("porch", p, "side piazzas")
    elif kind in ("hotel", "condo"):
        r = tr.get("roof")
        if r not in HOTEL_ROOF:
            setv("roof", HOTEL_ROOF_MAP.get(r, "flat"))
        b = tr.get("balconies")
        if b not in (None, "none", "continuous", "per_room"):
            setv("balconies", BALC_MAP.get(b, "per_room"))
        w = tr.get("walls")
        if w not in (None, "stucco", "concrete", "brick", "glass_curtain", "fiber_cement"):
            setv("walls", "stucco", "unknown wall")
    elif kind == "lighthouse":
        paint = tr.get("paint") or {}
        if "bands" not in paint:
            bands = [paint[k] for k in ("upper", "tower", "lower") if isinstance(paint.get(k), str)]
            if not bands:
                bands = [v for k, v in paint.items() if k not in ("lantern", "gallery", "trim") and isinstance(v, str)]
            new = dict(paint, bands=bands or ["#F4F4F2"])
            setv("paint", new, "bands")
    elif kind in INDUSTRY:
        if rec["id"] in OVER_WATER and not tr.get("on_pilings"):
            setv("on_pilings", True, "lot over water")
            tr.setdefault("pile_depth_m", 10.0)
    fix_colors(tr.get("colors") or {}, log)
    return log


def main():
    write = "--write" in sys.argv
    n = changed = 0
    kinds = {}
    for p in sorted(glob.glob(os.path.join(CAT, "*.json"))):
        sid = os.path.basename(p)[:-5]
        if sid.split("-")[0] not in PREFIXES or sid.startswith("_"):
            continue
        rec = json.load(open(p))
        n += 1
        log = audit(rec)
        if log:
            changed += 1
            kinds[rec.get("kind")] = kinds.get(rec.get("kind"), 0) + 1
            print(sid, "; ".join(log))
            if write:
                json.dump(rec, open(p, "w"), indent=1)
    print(f"{changed} of {n} records {'changed' if write else 'would change'}; by kind {kinds}")


if __name__ == "__main__":
    main()
