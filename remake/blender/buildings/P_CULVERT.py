"""
P-CULVERT -- US 30 over a farm drainage ditch east of Pruett (map crossing CULVERT-22).

Real example: Minnesota Bridge L2194, 200th Ave over an unnamed stream, Magnolia, Rock Co., MN
-- HAER (mn0632) (remake/reference/P-CULVERT-L2194/): a small two-cell cast-in-place reinforced
concrete box culvert by local builder Perley N. Gillham -- cells ~8' wide, 21'-0" barrel,
solid concrete railings with moulded coping and cylindrical end posts, builder's inscription
on the south railing.  No photos survive, so concrete detailing follows MN Bridge 5722 (US 63,
1932 standard box culvert, 2 photos: P-CULVERT-5722/).  Adapted: the barrel is lengthened to
carry US 30's two lanes + shoulders (noted).
Origin: road centreline at road level over the ditch; road runs along +Y, ditch along X.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbbridge as gbr  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
b = g.Building("P-CULVERT", os.path.join(ROOT, "remake", "textures", "p-bridges"))
gbr.bridge_materials(b)

CELL_W, CELL_H, BARREL = g.ft(8), 1.3, 11.0
BED = -(CELL_H + 0.3)
gbr.creek_terrain(b, L=40.0, W=40.0, ch_w=4.6, depth=-BED, bank_w=2.5, name="terrain")
gbr.water(b, -20.0, 20.0, -2.3, 2.3, BED + 0.25)
top, total = gbr.box_culvert(b, 2, CELL_W, CELL_H, BARREL, 9.0, BED)
for s in (-1, 1):
    gbr.road(b, min(s * total / 2, s * 20.0), max(s * total / 2, s * 20.0), 7.3, 0.0, name=f"road_{'N' if s > 0 else 'S'}")
b.part("deck-col").box((-4.65, -total / 2, -0.3), (4.65, total / 2, 0.0), "asphalt")
m = b.part("road_marks")
m.box((-0.06, -total / 2, 0.021), (0.06, total / 2, 0.023), "paint_yellow")
# solid railings with moulded coping + cylindrical end posts along both road edges (Gillham type)
rl = b.part("railings-col")
for sx in (-1, 1):
    x = sx * 4.9
    rl.box((x - 0.15, -total / 2 - 0.4, 0.0), (x + 0.15, total / 2 + 0.4, 0.75), "concrete")
    rl.box((x - 0.22, -total / 2 - 0.4, 0.75), (x + 0.22, total / 2 + 0.4, 0.85), "concrete")
    for yy in (-total / 2 - 0.4, total / 2 + 0.4):
        rl.cylinder((x, yy), 0.3, 0.0, 1.05, "concrete", n=16)
        rl.cylinder((x, yy), 0.34, 1.05, 1.12, "concrete", n=16)
g.text_mesh(b, "sign_builder", "E. OSTLIE  BUILDER  1913", 0.09, (-4.9 - 0.155, 0.0, 0.42), -math.pi / 2, "sign_black", extrude=0.004)
b.finish(os.path.join(ROOT, "godot_project", "remake", "buildings", "P-CULVERT.glb"))
