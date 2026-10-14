#!/usr/bin/env python3
"""make_sky_rooms.py -- the room manifests of the sky islands' building models (tools/rooms/make_rooms.building over each
SKY-M-NN's raw plan), for NpcOccupancy.  The islands place copies of these models (islands.json buildings[].model), so
the manifest is keyed by MODEL id, not by placed building: a placed building's rooms, doors, units and posts are its
model's.

  ~/.venvs/ssc-assets/bin/python tools/sky/make_sky_rooms.py      -> godot_project/remake/rooms/Sky islands.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "rooms"))
sys.path.insert(0, HERE)
import make_rooms as mr  # noqa: E402
from models import MODELS  # noqa: E402


def main():
    blds = {}
    for m in MODELS:
        raw = json.load(open(os.path.join(mr.RAW, m["id"] + ".json")))
        blds[m["id"]] = mr.building(m["id"], raw, m, {"households": m["sky"]["homes"]})
    out = os.path.join(mr.OUT, "Sky islands.json")
    with open(out, "w") as f:
        json.dump({"_about": "Rooms, units, doors, posts of the sky islands' building MODELS, keyed by model id (a placed "
                             "building is a copy of its model: islands.json buildings[].model) -- tools/sky/make_sky_rooms.py",
                   "settlement": "Sky islands", "by_model": True, "buildings": blds}, f, separators=(",", ":"))
    units = sum(len(b["units"]) for b in blds.values())
    beds = sum(len(r["beds"]) for b in blds.values() for r in b["rooms"].values())
    print(f"{len(blds)} models, {units} units, {beds} beds -> {out}")


if __name__ == "__main__":
    main()
