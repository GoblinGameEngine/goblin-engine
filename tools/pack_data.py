#!/usr/bin/env python3
"""
pack_data.py -- gzipped twins of the game's big data files, for the exported game.

  python3 tools/pack_data.py          (before every export: godot4 --export-release ...)

The project keeps each file plain (the tools write and read them so); the export ships <file>.gz instead
(export_presets.cfg) and the game reads either through DataFile (scripts/world/DataFile.gd: the same text, the same
MD5 for the bake fingerprints).  ~830 MB of JSON and .bin bakes ship as ~120 MB.  Only the files below: each one's game readers go
through DataFile.  A twin is rewritten when its file is newer; twins whose file is gone are removed.  Deterministic
(no name or time in the gzip header), so an unchanged file packs to the same bytes.
"""
import glob
import gzip
import os
import sys

GP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "godot_project")
PACKED = [
    "remake/terrain.json", "remake/road_furniture.json", "remake/placement.json", "remake/transit.json",
    "remake/characters/npc_fleet.json", "remake/characters/npc_paths.json", "remake/characters/npc_place_index.json",
    "remake/characters/lives/_index.json",
    "remake/rooms/*.json", "remake/rooms/solved/*.json",
    "remake/buildings/*.mats.json", "remake/buildings/*.kit.json", "remake/buildings/kit/*.mats.json",
    # the .bin bakes (FileAccess.store_var; read by DataFile.get_var): 185 MB -> 44 MB
    "remake/terrain.bin", "remake/placement.bin", "remake/road_furniture.bin", "remake/baked/pads.bin",
    "remake/characters/npc_fleet.bin", "remake/characters/npc_paths.bin", "remake/characters/lives/*.bin",
    "remake/baked/transit_lines.bin",
]


def main():
    want, wrote, kept, raw, packed = set(), 0, 0, 0, 0
    for pat in PACKED:
        for src in glob.glob(os.path.join(GP, pat)):
            dst = src + ".gz"
            want.add(os.path.normpath(dst))
            raw += os.path.getsize(src)
            if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
                kept += 1
            else:
                with open(src, "rb") as f:
                    data = gzip.compress(f.read(), compresslevel=9, mtime=0)
                tmp = dst + ".tmp"
                with open(tmp, "wb") as f:
                    f.write(data)
                os.replace(tmp, dst)
                wrote += 1
            packed += os.path.getsize(dst)
    gone = 0
    for pat in PACKED:
        for dst in glob.glob(os.path.join(GP, pat + ".gz")):
            if os.path.normpath(dst) not in want:
                os.remove(dst)
                gone += 1
    print(f"pack_data: {len(want)} files, {wrote} packed, {kept} up to date, {gone} stale removed; "
          f"{raw / 1e6:.0f} MB -> {packed / 1e6:.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
