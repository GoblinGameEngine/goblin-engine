#!/usr/bin/env python3
"""room_rects.py -- every building model's room rectangles, compact, for the game's interior split.

  python3 tools/rooms/room_rects.py

Reads godot_project/remake/rooms/*.json (tools/rooms/make_rooms.py; the sky islands' "Sky islands.json") and writes
godot_project/remake/rooms/_rects.json: {model id: [[x0, z0, x1, z1, y0, y1], ...]} in the model's Godot frame (the
frame of its kit placements).  RemakeBuilding.merge_kit puts a kit piece standing inside a room (furniture, fittings)
into the building's interior mesh, drawn only near (the user, 2026-10-14: "See where we don't need to render the
interior of buildings").  Packed by tools/pack_data.py.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOMS = os.path.join(ROOT, "godot_project", "remake", "rooms")


def main():
    # rooms are listed per placed building; the game merges per MODEL (shared by many placements): one entry each
    pl = json.load(open(os.path.join(ROOT, "godot_project", "remake", "placement.json")))
    model_of = {e["id"]: e.get("model", e["id"]) for e in pl["structures"]}
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOMS, "*.json"))):
        if os.path.basename(f).startswith("_"):
            continue
        d = json.load(open(f))
        for bid, b in (d.get("buildings") or {}).items():
            rects = []
            for r in (b.get("rooms") or {}).values():
                rc = r.get("rect")
                z = r.get("z") or [0.0, 3.0]
                if rc and len(rc) == 4:
                    rects.append([round(rc[0], 2), round(rc[1], 2), round(rc[2], 2), round(rc[3], 2),
                                  round(z[0], 2), round(z[1], 2)])
            mid = model_of.get(bid, bid)
            if rects and mid not in out:
                out[mid] = rects
    path = os.path.join(ROOMS, "_rects.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print(f"room_rects: {len(out)} models, {sum(len(v) for v in out.values())} rooms -> {path} "
          f"({os.path.getsize(path) // 1024} KB)")


if __name__ == "__main__":
    main()
