#!/usr/bin/env python3
"""make_warren.py -- grow a sky island's warren city and write its placements (research/sky_islands/warrens/r4_design.md;
FORMAT.md).

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/make_warren.py [SKY-100:maghrebi_medina SKY-071:kowloon_walled ...]
      [--no-preview]

E0 the spine (main streets, plazas, greens, ponds' banks, gates) -> E1 the founding (lanes in the civ's grammar, lots,
courts, the oldest masonry) -> E2..E4 accretion (rise, setback, jetty, sabat, towers, infill) -> E5 the newest layer
(roof shacks; cables, signs, dishes...) -> units, doors, the walk graph -> the dual-grid piece pass -> foliage ->
godot_project/remake/sky/warrens/<id>.bin.gz + <id>.json, previews in research/sky_islands/img/warren_*.png.
Deterministic: the island's seed.
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

import grow  # noqa: E402
import pick  # noqa: E402
import preview  # noqa: E402
import units as U  # noqa: E402
import writer  # noqa: E402
from civ import civ_for  # noqa: E402
from lattice import LANE, Lattice  # noqa: E402
import kitmap
import walk as walkmod  # noqa: E402
from spine import connect_leftovers, lay_spine  # noqa: E402

ISLANDS = os.path.join(ROOT, "godot_project", "remake", "sky", "islands.json")
OUT = os.path.join(ROOT, "godot_project", "remake", "sky", "warrens")
IMG = os.path.join(ROOT, "research", "sky_islands", "img")
MILESTONE = ["SKY-100:maghrebi_medina", "SKY-071:kowloon_walled"]


def seed_of(iid):
    return int(hashlib.sha1(("warren:" + iid).encode()).hexdigest()[:8], 16)


def build(isl, civ_id, do_preview=True):
    t0 = time.time()
    seed = seed_of(isl["id"])
    rng = random.Random(seed)
    L = Lattice(isl, seed)
    civ = civ_for(civ_id, isl, rng)
    p = civ.params
    blocks = int(isl.get("blocks", 3))
    # E0
    lay_spine(L, rng, blocks, civ)
    if hasattr(civ, "frame"):
        civ.frame(L, rng)
    # E1
    if civ.lanes == "grid":
        grow.grow_lanes_grid(L, rng, p)
    else:
        grow.grow_lanes_tree(L, rng, p)
    connect_leftovers(L)
    if hasattr(civ, "after_lanes"):
        civ.after_lanes(L, rng)
    grow.cut_lots(L, rng, p)
    civ.mark_lots(L, rng)
    grow.courts(L, rng, p)
    if hasattr(civ, "courts_for_civic"):
        civ.courts_for_civic(L, rng)
    grow.assign_uses(L, rng, p)
    if hasattr(civ, "before_found"):
        civ.before_found(L, rng)
    grow.found(L, rng, p)
    # E2..E4
    for e in (2, 3, 4):
        grow.accrete(L, rng, p, e)
    # E5: the roof village (Kowloon) or a few roof rooms
    grow.roof_shacks(L, rng, p.get("shacks", 0.22 if civ.lanes == "grid" else 0.02))
    removed = L.settle()
    # the E5 roof huts become the kit's shack overlays (ov_shack_*) on the roof they stand on, not rooms
    import numpy as np
    shacks = [(int(i), int(j), int(k)) for i, j, k in zip(*np.nonzero((L.occ > 0) & (L.epoch == 5)))]
    for (i, j, k) in shacks:
        L.clear(i, j, k)
    # paved paths through the greens (walk.py), then the pieces, units, walking
    import walk
    paths = walk.green_paths(L)
    o = pick.run(L, civ, rng)
    units, doors = U.make_units(L, civ)
    lattice_homes = sum(u["homes"] for u in units)
    surplus = U.balance_homes(L, civ, units, isl.get("population"))
    walk = U.walk_graph(L, civ)
    for (i, j, k, rot) in dict.fromkeys(L.ladders):
        o.emit("ladder", i, j, k, rot, 0, 0, civ.slot("metal"), 5)
    for (i, j, k, rot) in dict.fromkeys(L.planks):
        o.emit("bridge_plank", i, j, k, rot, 0, 0, civ.slot("frame"), 5)
    kit = kitmap.load_kit()
    if kit is None:
        raise SystemExit("no kit: " + kitmap.KIT_JSON)
    if civ.id not in kit["palettes"] and hasattr(civ, "PALETTES"):
        kit["palettes"][civ.id] = civ.PALETTES          # (the family's own until the KIT stream adds them)
    o.recs, dropped = kitmap.translate(L, civ, o.recs, kit, shacks)
    walkmod.physical(L, o.recs, kit["pieces"])
    # the player's clear box through every way and door (openings.py): what blocks is cleared (decor dropped, a
    # balcony/shopfront/arch over the walk swapped for a plain or wider piece), then the budget, then again (the
    # budget's own swaps), then the check
    import openings
    o.recs, ostats = openings.fix(L, o.recs, kit["pieces"], L.phys_h)
    shed = {}
    for _ in range(3):
        o.recs, sh = kitmap.budget(L, o.recs, kit, civ.params.get("chunk_tris", 25000))
        shed.update(sh)
        if not sh:
            break
        o.recs, ostats2 = openings.fix(L, o.recs, kit["pieces"], L.phys_h)
        for k in ("edges_blocked_after", "doors_blocked_after", "still_blocking", "kit_door_too_small"):
            ostats[k] = ostats2[k]
        ostats["pieces_swapped"] += ostats2["pieces_swapped"]
        ostats["pieces_removed"] += ostats2["pieces_removed"]
        if not ostats2["pieces_swapped"] and not ostats2["pieces_removed"]:
            break
    occ = openings.occupied(L, o.recs, kit["pieces"], L.phys_h)
    for c in occ:
        L.W.discard(c)                                   # (a landmark's footprint: off the walk)
    left = openings.scan(L, o.recs, kit["pieces"], L.phys_h)
    # (a door whose only obstruction is its own door piece -- the KIT's frame 2.17 m clear, not 2.2 -- is a KIT
    # request; the door stays)
    L.doors_blocked = set(lid for lid, bl in left["doors"] if not all(openings.is_door_piece(L, o.recs[n], lid, kit["pieces"]) for n in bl))
    L.walk_stats["physical"] = walkmod.physical(L, o.recs, kit["pieces"], set((c, n) for c, n, _ in left["edges"]))
    L.walk_stats["physical"]["openings"] = ostats
    L.walk_stats["physical"]["landmark_cells"] = len(occ)
    o.recs, gstats = openings.prune_graph(L, o.recs, kit["pieces"], [(c, n) for c, n, _ in left["edges"]], occ)
    L.walk_stats["physical"]["graph"] = gstats
    if os.environ.get("WALK_DEBUG"):
        S = openings.Scene(L, o.recs, kit["pieces"])
        for lid, bl in left["doors"][:3]:
            lot = L.lots[lid]
            print("BLOCKED DOOR", lid, lot["door"], lot["door_k"], [(o.recs[k][:7]) for k in bl])
            for k in bl:
                W, a, b = S.world(k)
                print("   piece world aabb", a.round(2), b.round(2))
        for c, n, bl in left["edges"][:6]:
            print("BLOCKED EDGE", c, n, L.q.get(c), L.stair.get(c), L.q.get(n), L.stair.get(n), [o.recs[k][:7] for k in bl])
    L.lights = kitmap.lights(L, civ, o.recs, kit)
    comps = U.components(L)
    U.mark_private_roofs(L)
    fol = writer.foliage_instances(L, civ, civ.foliage(L, rng))
    # checks
    tether_hits = int((L.occ.astype(bool) & L.block).sum())
    unsup = sum(1 for k in range(1, L.L) for i, j in zip(*np.nonzero(L.occ[:, :, k])) if not L.supported(int(i), int(j), k))
    lanes = int((L.plan == LANE).sum())
    covered = sum(1 for i in range(L.nx) for j in range(L.nz) if L.plan[i, j] == LANE and pick.covered_at(L, (i, j)))
    homes = sum(u["homes"] for u in units)
    stats = {
        "civ": civ.id, "city": getattr(civ, "city", None), "blocks": blocks, "population": isl.get("population"),
        "lattice": [L.nx, L.nz], "rooms": int(L.occ.sum()),
        "rooms_by_level": [int(L.occ[:, :, k].sum()) for k in range(L.L) if L.occ[:, :, k].any()],
        "rooms_by_epoch": [int(((L.occ > 0) & (L.epoch == e)).sum()) for e in range(6)],
        "lots": len(L.lots), "units": len(units), "homes": homes, "lattice_homes": lattice_homes, "homes_repurposed": surplus,
        "units_by_kind": {kd: sum(1 for u in units if u["kind"] == kd) for kd in sorted(set(u["kind"] for u in units))}, "doors": len(doors),
        "enter_cells": len(getattr(L, "enter", [])),
        "lanes_cells": lanes, "lanes_covered_share": round(covered / max(lanes, 1), 2),
        "placements": len(o.recs), "anchors": len(o.anchors), "lights": len(L.lights), "foliage": len(fol),
        "walk_nodes": len(walk["nodes"]), "walk_edges": len(walk["edges"]), "walk_components": comps[:5],
        "tether_violations": tether_hits, "unsupported": unsup, "settle_removed": removed,
        "roof_shacks": len(shacks), "green_path_cells": paths, "walk_check": L.walk_stats, "chunks_shed": len(shed), "plinths": getattr(L, "plinths", 0), "missing_from_kit": dropped, "duplicates_removed": getattr(L, "dup_removed", 0),
        "build_s": round(time.time() - t0, 2),
    }
    os.makedirs(OUT, exist_ok=True)
    writer.write(L, civ, o, units, doors, fol, os.path.join(OUT, isl["id"] + ".bin.gz"),
                 os.path.join(OUT, isl["id"] + ".json"), stats, kit)
    if do_preview:
        os.makedirs(IMG, exist_ok=True)
        title = "%s %s -- %s (%s)" % (isl["id"], isl.get("name"), civ.name, getattr(civ, "city", "") or "")
        preview.plan_image(L, 6, fol, title).save(os.path.join(IMG, "warren_%s_plan.png" % isl["id"]))
        preview.slices_image(L, 3, title).save(os.path.join(IMG, "warren_%s_levels.png" % isl["id"]))
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--family", action="append", default=[], help="every island assigned to this family")
    ap.add_argument("--all", action="store_true", help="every island whose family has a civ module")
    a = ap.parse_args()
    data = json.load(open(ISLANDS))
    by = {i["id"]: i for i in data["islands"]}
    specs = list(a.ids)
    if a.family or a.all:
        from civ import CIVS
        asg = json.load(open(os.path.join(OUT, "assign.json")))["assign"]
        specs += ["%s:%s" % (iid, f) for iid, f in sorted(asg.items())
                  if (f in a.family) or (a.all and f in CIVS)]
    for spec in (specs or MILESTONE):
        iid, civ_id = spec.split(":")
        st = build(by[iid], civ_id, not a.no_preview)
        print(iid, json.dumps({k: v for k, v in st.items() if k not in ("missing_from_kit",)}))
        print("  generator pieces the kit has nothing for (dropped):", st["missing_from_kit"])


if __name__ == "__main__":
    main()
