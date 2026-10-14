#!/usr/bin/env python3
"""
import_flags.py -- Godot import settings for the kit-built buildings.

  python3 tools/buildings/import_flags.py [--lods]     (then godot4 --headless --import again)

A building with shared parts (<ID>.kit.json) has its visual mesh rebuilt at load by RemakeBuilding.merge_kit, which
keeps only LOD0 and drops the shadow mesh -- so the import's generated LODs and shadow meshes (42% of a building .scn)
are never used.  The same goes for the kit pieces themselves.  Turns both off in their .glb.import files; --lods also
the distance versions' (LOD1 keeps its generated LODs).  New glbs get
an .import file (with Godot's defaults) on their first import: run this after it, and import again.
"""
import glob
import os
import sys

BLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "godot_project", "remake", "buildings")
OFF = (("meshes/generate_lods=true", "meshes/generate_lods=false"),
       ("meshes/create_shadow_meshes=true", "meshes/create_shadow_meshes=false"))


def main():
    files = [f[:-len(".kit.json")] + ".glb.import" for f in glob.glob(os.path.join(BLD, "*.kit.json"))]
    files += glob.glob(os.path.join(BLD, "kit", "*.glb.import"))
    if "--lods" in sys.argv:                 # the distance versions too (<ID>.lod1/2/3.glb)
        files += glob.glob(os.path.join(BLD, "*.lod[123].glb.import"))
    changed = 0
    for f in files:
        if not os.path.exists(f):
            continue
        s = open(f).read()
        t = s
        for a, b in OFF:
            t = t.replace(a, b)
        if f.endswith(".lod1.glb.import"):
            # LOD1 keeps Godot's own LODs (all off cost ~0.3 ms GPU in a mid view of Calder; shadow meshes off alone:
            # within noise, 2026-10-13) -- 0.72 -> 0.47 GB
            t = t.replace("meshes/generate_lods=false", "meshes/generate_lods=true")
        if t != s:
            open(f, "w").write(t)
            changed += 1
    print(f"import flags: {changed} changed of {len(files)}")


if __name__ == "__main__":
    main()
