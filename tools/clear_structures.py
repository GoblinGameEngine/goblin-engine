#!/usr/bin/env python3
"""
clear_structures.py -- every building clear of every road and of the rail line, on the roads as they finally are.

  python3 tools/clear_structures.py [--dry]

placement.py clears the buildings off the roads, but road_fix.py --after-placement reshapes the road lines after it (and
the rail line was never cleared): where.py check found 56 buildings standing in a carriageway and 95 on the Ring Line's
track (2026-10-13).  This runs placement's own clear_of_roads (roads and now the rail corridor) and clear_of_each_other
on the current placement.json.  regen_world.sh runs it after road_fix2; everything downstream of placement follows.
"""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "remake", "tools"))
import placement  # noqa: E402

placement.CARRIAGEWAY_ONLY = True       # (out of the roads; a porch over a sidewalk, as placement left it, is let be)

OUT = os.path.join(ROOT, "godot_project", "remake", "placement.json")


def main():
    out = json.load(open(OUT))["structures"]
    before = {e["id"]: (e["s"], e["x"]) for e in out}
    # clear_of_each_other can push a building back into a road (its way out is the shallowest one when none is
    # clear): a few rounds of both, then one still standing in a road is left out (17 were, 2026-10-14)
    for rnd in range(4):
        placement.clear_of_roads(out, quiet=True)
        placement.clear_of_each_other(out)
        if not any(e["kind"] != "crossing" and not e.get("over_water") and placement.road_conflict(e) for e in out):
            break
    # (a pier's building is only left out: it can't move off its pier)
    inroad = {e["id"] for e in out if e["kind"] != "crossing" and placement.road_conflict(e)}
    out[:] = [e for e in out if e["id"] not in inroad]
    after = {e["id"]: (e["s"], e["x"]) for e in out}
    moved = [i for i in after if after[i] != before[i]]
    gone = [i for i in before if i not in after]
    print("clear_structures: %d still in a road after %d rounds, left out" % (len(inroad), rnd + 1))
    print("clear_structures: %d moved, %d left out (no room clear of the roads): %s" % (len(moved), len(gone), " ".join(gone[:30])))
    if "--dry" not in sys.argv:
        with open(OUT, "w") as f:
            json.dump({"structures": out}, f, indent=0)


if __name__ == "__main__":
    main()
