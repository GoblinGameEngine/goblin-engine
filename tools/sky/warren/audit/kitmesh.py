#!/usr/bin/env python3
"""kitmesh.py -- meshlib's topology + normals checks on every mesh of a GLB (default: the warren kit, kit.glb and
kit_mid.glb), ranked.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/audit/kitmesh.py [file.glb ...]
      -> reference/tmp/audit/kitmesh_<glb>.txt / .json

Per mesh: open edges (holes in a would-be closed part), non-manifold edges (> 2 faces), inconsistent winding
(a shared edge walked the same way by both faces: a flipped face), inside-out closed parts (negative volume in
glTF's counter-clockwise convention), the fraction of faces whose normal points into the solid (ray parity),
degenerate and duplicate faces."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import meshlib as M  # noqa: E402
import rays as RY  # noqa: E402


def check_glb(path):
    rows = []
    for name, (tris, mats) in sorted(M.read_glb_meshes(path).items()):
        if not len(tris):
            continue
        t = M.topology(tris)
        inv = M.inward_normals(tris, RY.Rays(tris), sample=600)
        rows.append({"mesh": name, "faces": t["faces"], "open": t["open_edges"], "nonmanifold": t["nonmanifold_edges"],
                     "inconsistent": t["inconsistent_edges"], "inside_out": t["inside_out"],
                     "closed": t["closed_components"], "components": len(t["components"]),
                     "inward_frac": round(inv["fraction"], 3), "degenerate": t["degenerate"], "dup": t["dup_faces"],
                     "double_sided": t["double_sided"], "nonmanifold_at": t["nonmanifold_at"][:3],
                     "inconsistent_at": t["inconsistent_at"][:3]})
    return rows


def main():
    files = sys.argv[1:] or [C.KIT_GLB, os.path.join(C.WR, "kit", "kit_mid.glb")]
    os.makedirs(C.OUT, exist_ok=True)
    for f in files:
        rows = check_glb(f)
        score = lambda r: (r["inconsistent"] * 3 + r["inside_out"] * 50 + r["nonmanifold"] * 2 +
                           (r["inward_frac"] > 0.3) * 40 + r["dup"])
        rows.sort(key=lambda r: -score(r))
        base = os.path.splitext(os.path.basename(f))[0]
        json.dump(rows, open(os.path.join(C.OUT, "kitmesh_%s.json" % base), "w"), indent=0)
        lines = ["%-32s %6s %6s %6s %6s %5s %6s %6s %5s" % ("mesh", "faces", "open", "nonman", "incons", "inout",
                                                          "inward", "degen", "dup")]
        for r in rows:
            lines.append("%-32s %6d %6d %6d %6d %5d %6.2f %6d %5d" % (r["mesh"], r["faces"], r["open"], r["nonmanifold"],
                                                                  r["inconsistent"], r["inside_out"], r["inward_frac"],
                                                                  r["degenerate"], r["dup"]))
        open(os.path.join(C.OUT, "kitmesh_%s.txt" % base), "w").write("\n".join(lines) + "\n")
        n = len(rows)
        print("%s: %d meshes; with inconsistent winding %d, inside-out parts %d, non-manifold %d, open %d, "
              "> 30 %% faces inward %d, duplicate faces %d" % (
                  base, n, sum(r["inconsistent"] > 0 for r in rows), sum(r["inside_out"] > 0 for r in rows),
                  sum(r["nonmanifold"] > 0 for r in rows), sum(r["open"] > 0 for r in rows),
                  sum(r["inward_frac"] > 0.3 for r in rows), sum(r["dup"] > 0 for r in rows)))
        for line in lines[:13]:
            print("  " + line)


if __name__ == "__main__":
    main()
