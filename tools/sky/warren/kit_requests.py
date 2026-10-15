#!/usr/bin/env python3
"""kit_requests.py -- research/sky_islands/warrens/kit_requests.md: the pieces each warren family's civ module wants
that the kit (pieces.json) doesn't have yet, with the stand-in the generator uses meanwhile; plus families without a
kit palette.  Rerun after adding a family or when the KIT stream publishes.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/kit_requests.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
from civ import CIVS  # noqa: E402
from pieces import KIT_JSON  # noqa: E402

GENERAL = [
    ("pave_*_skirt", "paving with a 0.6 m skirt down its four sides (or a riser piece): ground pieces stand flat at each cell's deck height, so on sloping streets the step between two cells shows a gap to the sky", "none (gaps)"),
    ("edge_parapet_rounded_k (cheaper)", "the rounded merlon parapet at <= 60 tris; at 172 it is the first thing the budget pass sheds in every medina/Yemeni/M'zab chunk", "edge_parapet_plain_k when over budget"),
]
OUT = os.path.join(ROOT, "research", "sky_islands", "warrens", "kit_requests.md")


def main():
    kit = json.load(open(KIT_JSON))
    have = kit["pieces"]
    L = ["# Kit requests from the GENERATOR (warren families)", "",
         "Written by `tools/sky/warren/kit_requests.py` from each civ module's SPEC (`tools/sky/warren/civ/`).",
         "Frames as pieces.json (`wall`/`edge`: +Z out of the cell, face plane at z 0; `cell`: centred). The generator",
         "uses the stand-in until the piece exists, then switches by id (tell it the id).", ""]
    L += ["## All families", "", "| piece | what | stand-in | status |", "|---|---|---|---|"]
    for pid, what, stand in GENERAL:
        L.append("| `%s` | %s | %s | %s |" % (pid, what, stand, "in the kit" if pid in have else "wanted"))
    L.append("")
    nopal = [c for c in sorted(CIVS) if c not in kit.get("palettes", {})]
    if nopal:
        L += ["## Palettes missing", "", "4 variants each (slot -> colour); the generator writes its own into the warren"
              " json until then: " + ", ".join("`%s`" % c for c in nopal), ""]
    for cid in sorted(CIVS):
        reqs = getattr(CIVS[cid], "SPEC", {}).get("kit_requests", [])
        if not reqs:
            continue
        L += ["## %s" % cid, "", "| piece | what | stand-in | status |", "|---|---|---|---|"]
        for pid, what, stand in reqs:
            L.append("| `%s` | %s | %s | %s |" % (pid, what, stand, "in the kit" if pid in have else "wanted"))
        L.append("")
    open(OUT, "w").write("\n".join(L) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
