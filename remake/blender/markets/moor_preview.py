#!/usr/bin/env python3
"""moor_preview.py -- palette-baked preview glbs of the warren kit's mooring pieces for the contact sheets (two
families' palettes side by side), full and MID: reference/tmp/markets_kit/sheet_warren_moor_{full,mid}.glb"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "remake", "blender", "sky", "warren_kit"))
import geom  # noqa: E402
import flicker  # noqa: E402
import mid  # noqa: E402
from build import hex_rgb  # noqa: E402
from pieces import PALETTES, PIECES  # noqa: E402

PREV = os.path.join(ROOT, "reference", "tmp", "markets_kit")
IDS = ["moor_signal_mast", "moor_drop_cage_davit", "moor_line_house", "moor_station_cargo", "moor_station_pax"]
FAMS = ["hanseatic_gable", "maghrebi_medina"]


def main():
    for tag in ("full", "mid"):
        laid, x = [], 0.0
        z = 0.0
        for row, fam in enumerate(FAMS):
            cols = {k: hex_rgb(v) for k, v in PALETTES[fam][0].items()}
            x = 0.0
            for pid in IDS:
                d = PIECES[pid]
                m, _ = flicker.finish(pid, d, d["build"]())
                if tag == "mid":
                    mm, how = mid.mid_mesh(pid, d, m)
                    if how == "mid":
                        m = mm
                lo, hi = m.bounds()
                g = geom.Mesh()
                g.add(m, geom.move(x - lo[0], 0.0, z - hi[2]))
                laid.append((pid if row == 0 else pid + "_" + fam[:4], g, cols))
                x += hi[0] - lo[0] + 3.0
            z -= 30.0
        # one export per family (geom's exporter takes one colour table), merged by node into one glb via two files
        for fam_i, fam in enumerate(FAMS):
            sel = [(n, g) for n, g, c in laid[fam_i * len(IDS):(fam_i + 1) * len(IDS)]]
            geom.export_glb(os.path.join(PREV, f"sheet_warren_moor_{tag}_{fam_i}.glb"), sel, colours=laid[fam_i * len(IDS)][2])
    print("moor previews in", PREV)


if __name__ == "__main__":
    main()
