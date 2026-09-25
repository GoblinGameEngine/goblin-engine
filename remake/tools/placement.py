#!/usr/bin/env python3
"""
placement.py -- the map's placement manifest for the remake buildings.

  python3 remake/tools/placement.py      -> godot_project/remake/placement.json

Joins remake/inventory/map_inventory.json (where everything stands on the ring: arc position s,
axial position x, facing) with the built glbs (godot_project/remake/buildings/<ID>.glb) and writes
one entry per placeable structure:

  {"id", "kind", "settlement", "glb", "s", "x", "yaw", "min": [x, y, z], "max": [x, y, z],
   "fmin": [x, z], "fmax": [x, z]}      (fmin/fmax: the massing footprint, from the LOD2)

yaw (radians) turns the building about the floor's up axis so its front (glb local -z, Blender +y)
faces the right way: forward on the ring is +s, right is +x, so a front pointing along (ds, dx)
needs yaw = atan2(-dx, ds) (RingCoords.place_on_ring's convention).  min/max are the merged
visual mesh's bounds in the glb's own frame (Godot axes; y up, foundations reach below 0): the
placer samples the terrain over that footprint and far-away stand-ins use it as their box.

Structures come from the settlements' inventory entries (front = the side facing their front_edge),
farmsteads from their exported parts (the house faces away from the barn, everything else faces the
house), crossings from their road ends (the road runs along the glb's local forward axis).
Entries whose glb isn't built yet are listed on stderr and skipped.
"""
import json
import math
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INV = os.path.join(ROOT, "remake", "inventory", "map_inventory.json")
BLD = os.path.join(ROOT, "godot_project", "remake", "buildings")
OUT = os.path.join(ROOT, "godot_project", "remake", "placement.json")


# the Pruett slice was modelled before the catalog, under its own names: inventory id -> its glbs
# (several share a lot side by side along the front)
ALIAS = {"P-001": ["P-STORE", "P-TAVERN"], "P-002": ["P-CHURCH"], "P-003": ["P-PO"], "P-004": ["P-HOUSE1"],
         "P-005": ["P-HOUSE2"], "P-006": ["P-HOUSE3"], "P-007": ["P-HOUSE4"], "P-008": ["P-ELEV"], "P-009": ["P-DEPOT"]}


def glb_bounds(path, any_mesh=False):
    """Bounds of the *_visual mesh (union of its primitives' POSITION accessors), glb frame; with
    any_mesh, of every mesh (a .lod2.glb's single massing mesh)."""
    with open(path, "rb") as f:
        data = f.read()
    n = struct.unpack("<I", data[12:16])[0]
    j = json.loads(data[20:20 + n])
    lo, hi = [1e9] * 3, [-1e9] * 3
    for node in j["nodes"]:
        if "mesh" not in node or not (any_mesh or node.get("name", "").endswith("_visual")):
            continue
        t = node.get("translation", [0, 0, 0])
        for prim in j["meshes"][node["mesh"]]["primitives"]:
            acc = j["accessors"][prim["attributes"]["POSITION"]]
            for k in range(3):
                lo[k] = min(lo[k], acc["min"][k] + t[k])
                hi[k] = max(hi[k], acc["max"][k] + t[k])
    return (lo, hi) if lo[0] < 1e9 else None


def yaw_facing(ds, dx):
    return math.atan2(-dx, ds)


def main():
    inv = json.load(open(INV))
    out, missing = [], []

    def add(rid, kind, settlement, s, x, yaw):
        if rid in ALIAS:
            names = ALIAS[rid]
            bounds = [glb_bounds(os.path.join(BLD, f"{n}.glb")) for n in names]
            widths = [b[1][0] - b[0][0] + 1.0 for b in bounds]
            # side by side along the building's local x (right turns to (cos yaw, sin yaw) in (x, s))
            off = -sum(widths) / 2
            for n, w in zip(names, widths):
                c = off + w / 2
                off += w
                _add(n, kind, settlement, s + math.sin(yaw) * c, x + math.cos(yaw) * c, yaw)
            return
        _add(rid, kind, settlement, s, x, yaw)

    def _add(rid, kind, settlement, s, x, yaw, model=None):
        # model: the glb it uses when that's another structure's (a crossing reusing an existing
        # bridge on the expanded map); the entry keeps its own id
        glb = os.path.join(BLD, f"{model or rid}.glb")
        if not os.path.exists(glb):
            missing.append(rid)
            return
        b = glb_bounds(glb)
        if b is None:
            missing.append(rid + " (no _visual mesh)")
            return
        # the footprint the building stands on: its massing (LOD2, no yard props), else the visual bounds
        lod2 = os.path.join(BLD, f"{model or rid}.lod2.glb")
        f = glb_bounds(lod2, any_mesh=True) if os.path.exists(lod2) else None
        f = f or b
        out.append({"id": rid, "kind": kind, "settlement": settlement, "glb": f"res://remake/buildings/{model or rid}.glb",
                    "model": model or rid,
                    "s": round(s, 2), "x": round(x, 2), "yaw": round(yaw, 4),
                    "min": [round(v, 2) for v in b[0]], "max": [round(v, 2) for v in b[1]],
                    "fmin": [round(f[0][0], 2), round(f[0][2], 2)], "fmax": [round(f[1][0], 2), round(f[1][2], 2)]})

    for st in inv["structures"]:
        (a0, a1), (b0, b1) = st["front_edge"] if st.get("front_edge") else ((st["s"], st["x"]), (st["s"], st["x"] + 1))
        fs, fx = (a0 + b0) / 2 - st["s"], (a1 + b1) / 2 - st["x"]
        add(st["id"], st["kind"], st["settlement"], st["s"], st["x"], yaw_facing(fs, fx))

    for fm in inv["farmsteads"]:
        parts = {p["part"]: p for p in fm.get("parts", [])}
        house = parts.get("house")
        for name, p in parts.items():
            if name == "house":
                barn = parts.get("barn") or p
                ds, dx = p["s"] - barn["s"], p["x"] - barn["x"]
            else:
                ds, dx = house["s"] - p["s"], house["x"] - p["x"]
            add(f"{fm['id']}-{name}", "farm", None, p["s"], p["x"], yaw_facing(ds, dx) if (ds or dx) else 0.0)

    for c in inv["crossings"]:
        (as_, ax), (bs, bx) = c.get("ends") or ((c["s"], c["x"]), (c["s"] + 1, c["x"]))
        if c.get("model", c["id"]) is None:
            missing.append(c["id"] + " (no model yet)")
            continue
        _add(c["id"], "crossing", None, c["s"], c["x"], yaw_facing(bs - as_, bx - ax), c.get("model"))

    with open(OUT, "w") as f:
        json.dump({"structures": out}, f, indent=0)
    print(f"placement: {len(out)} placed -> {OUT}")
    if missing:
        print(f"not built ({len(missing)}): {' '.join(missing)}", file=sys.stderr)


if __name__ == "__main__":
    main()
