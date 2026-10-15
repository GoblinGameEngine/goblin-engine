#!/usr/bin/env python3
"""build.py -- build the warren kit: every piece in pieces.py into one glb library plus pieces.json (the contract the
GENERATOR and RUNTIME streams read), and per-civ preview glbs with the palettes baked (for the contact sheets).

  ~/.venvs/ssc-assets/bin/python remake/blender/sky/warren_kit/build.py [--previews]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom  # noqa: E402
from pieces import PALETTES, PIECES  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(ROOT, "godot_project", "remake", "sky", "warrens")
KIT = os.path.join(OUT, "kit")
RES = "res://remake/sky/warrens/kit/"
PREV = os.path.join(ROOT, "reference", "tmp", "warren_kit")


def hex_rgb(h, linear=True):
    """a palette colour for a PREVIEW glb (Blender reads COLOR_0 as linear: convert the sRGB hex, or it renders pale)"""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    if linear:
        c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return tuple(c)


def main(previews=False):
    os.makedirs(KIT, exist_ok=True)
    built = []
    meta = {}
    for pid, d in PIECES.items():
        m = d["build"]()
        built.append((pid, m))
        lo, hi = m.bounds()
        meta[pid] = {"glb": RES + "kit.glb", "mesh": pid, "group": d["group"], "kind": d["kind"], "civs": d["civs"],
                     "bay": [3.0, 3.2], "span": d["span"], "lod1": d["lod1"], "collide": d["collide"],
                     "slots": [s for s in geom.SLOTS if m.tris[s]], "tris": m.count(),
                     "bounds": [[round(v, 3) for v in lo], [round(v, 3) for v in hi]], "notes": d["notes"]}
    size = geom.export_glb(os.path.join(KIT, "kit.glb"), built)
    doc = {
        "version": 1,
        "contract": "research/sky_islands/warrens/00_brief.md (milestone 1); built by remake/blender/sky/warren_kit/build.py",
        "frames": {
            "wall": "x -1.5..1.5 across the bay, y 0..3.2 up, +Z out of the cell; body inside the cell z -t..0 (t 0.25 thin _t, 0.6 thick _k); ornaments reach +Z",
            "edge": "as wall, standing on a roof top (y 0 = roof top)",
            "corner": "origin on the cell's vertical edge; the occupied cell in -X/-Z; exposed faces +X and +Z",
            "cell": "origin at the cell centre, y 0 = the walking surface / roof top / (ceiling pieces) the ceiling; spans x, z -1.5..1.5 (span [nx, nz] cells along +X/+Z from the first)",
        },
        "units": {"cell": [3.0, 3.2, 3.0]},
        "slots": geom.SLOTS,
        "slot_mechanism": "each piece mesh has one surface per slot (material 'wk_<slot>'); COLOR_0 is a grey SHADE (baked AO/variation); the runtime multiplies it by the civ palette colour of that slot (palette index from the placement) into the merged chunk's vertex colour; glass surfaces carry pane UV0 0..1 for interior mapping; emissive surfaces glow at night",
        "lod1_rules": {"box": "draw the cell face / slab plainly instead", "keep": "keep at LOD1 (silhouette)", "drop": "gone at LOD1"},
        "collide": {"true": "the piece's triangles", "false": "none", "ramp": "stairs: a ramp plane over the piece's bounds rising along +Z"},
        "palettes": PALETTES,
        "pieces": meta,
    }
    with open(os.path.join(OUT, "pieces.json"), "w") as f:
        json.dump(doc, f, indent=1)
    tris = sum(v["tris"] for v in meta.values())
    print(f"{len(meta)} pieces, {tris} tris, kit.glb {size / 1024:.0f} KB")
    if previews:
        os.makedirs(PREV, exist_ok=True)
        for civ, pals in PALETTES.items():
            cols = {k: hex_rgb(v) for k, v in pals[0].items()}
            sel = [(pid, m) for pid, m in built if "shared" in PIECES[pid]["civs"] or civ in PIECES[pid]["civs"]]
            # laid out on a grid (by group), facing the camera (+Z toward -Y in Blender = the front)
            cols_n = 9
            laid = []
            for k, (pid, m) in enumerate(sel):
                gm = geom.Mesh()
                r, c = divmod(k, cols_n)
                gm.add(m, geom.move(c * 4.5, 0.0, -r * 5.0))
                laid.append((pid, gm))
            geom.export_glb(os.path.join(PREV, f"kit_{civ}.glb"), laid, colours=cols)
            with open(os.path.join(PREV, f"kit_{civ}.txt"), "w") as f:
                f.write("\n".join(f"{k // cols_n},{k % cols_n} {pid}" for k, (pid, _) in enumerate(sel)))
        print("previews in", PREV)
        # per family: its own marks beside a few shared walls, in its palette (the family sheets)
        shared = ["wall_plain_t", "wall_window_m_t", "wall_door_t", "wall_shopfront_a_t", "wall_plain_k", "wall_window_s_k"]
        for civ, pals in PALETTES.items():
            marks = [pid for pid, d in PIECES.items() if civ in d["civs"] and "shared" not in d["civs"]]
            if not marks:
                continue
            cols = {k: hex_rgb(v) for k, v in pals[0].items()}
            laid, bm = [], dict(built)
            zrow = 7.0
            for ids in (marks, shared):                          # the marks in front (packed by size), shared behind
                x, zrow = 0.0, zrow - 7.0
                for pid in ids:
                    lo, hi = bm[pid].bounds()
                    if x > 15.0:
                        x, zrow = 0.0, zrow - 7.0
                    gm = geom.Mesh()
                    gm.add(bm[pid], geom.move(x - lo[0], 0.0, zrow))
                    laid.append((pid, gm))
                    x += hi[0] - lo[0] + 1.2
            geom.export_glb(os.path.join(PREV, f"fam_{civ}.glb"), laid, colours=cols)
    return meta


if __name__ == "__main__":
    main("--previews" in sys.argv)
