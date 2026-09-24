"""
P-BR-US30 -- US 30 over Deer Creek, west of Pruett (map crossing SMALL-45).

Real example: Hill Creek Bridge, State Route 100 over Hill Creek, Pearl, Pike Co., IL --
HAER IL-118 (remake/reference/P-BR-US30/): a single-span riveted steel Warren pony truss with
verticals on concrete abutments, W-beam guardrail on the approaches (photos 1-10: elevation,
portal, underside floor system, gusset plates, rocker bearing).  The real bridge is skewed
55 deg; this crossing is square to the creek, so the skew is dropped (noted).  Span ~70'
(7 panels of 10'), roadway 24' between trusses, truss depth ~6' -- read from the photos
against the 12' lanes.  Signs (Pruett): county builder's plate, creek name, weight limit, US 30.
Origin: road centreline at deck level over the creek; road runs along +Y.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbbridge as gbr  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
b = g.Building("P-BR-US30", os.path.join(ROOT, "remake", "textures", "p-bridges"))
gbr.bridge_materials(b)

SPAN, WIDTH, H, PANELS = g.ft(70), g.ft(24), g.ft(6), 7
BED = -3.2
gbr.creek_terrain(b, L=60.0, W=40.0, ch_w=6.0, depth=3.2, bank_w=5.0, name="terrain")
gbr.water(b, -20.0, 20.0, -3.2, 3.2, BED + 0.6)
gbr.pony_truss(b, SPAN, WIDTH, H, PANELS, z_deck=0.0)
for s in (-1, 1):
    gbr.abutment(b, s * SPAN / 2, s, WIDTH, 0.0, BED, f"abutment_{'N' if s > 0 else 'S'}")
    gbr.road(b, min(s * SPAN / 2, s * 30.0), max(s * SPAN / 2, s * 30.0), 7.3, 0.0, name=f"road_{'N' if s > 0 else 'S'}")
    gbr.guardrail(b, [(-4.6, s * (SPAN / 2 + 0.3)), (-4.6, s * (SPAN / 2 + 9.0))], 0.0, name=f"gr_w_{s}")
    gbr.guardrail(b, [(4.6, s * (SPAN / 2 + 0.3)), (4.6, s * (SPAN / 2 + 9.0))], 0.0, name=f"gr_e_{s}")
# road through the truss (deck is the concrete slab); centre line across
m = b.part("road_marks")
m.box((-0.06, -SPAN / 2, 0.021), (0.06, SPAN / 2, 0.023), "paint_yellow")
# builder's plate on the south-west end post
g.text_mesh(b, "sign_plate_1", "BRANNOCK COUNTY", 0.09, (-WIDTH / 2 - 0.2, -SPAN / 2 + 0.9, 0.95), -math.pi / 2, "plate_bronze", extrude=0.01)
g.text_mesh(b, "sign_plate_2", "1931  ·  DEER CREEK", 0.07, (-WIDTH / 2 - 0.2, -SPAN / 2 + 0.9, 0.8), -math.pi / 2, "plate_bronze", extrude=0.01)
gbr.post_sign(b, "creek_name", 5.2, -SPAN / 2 - 6.0, 0.0, [("DEER CREEK", 0.18)], board=(1.6, 0.4), board_mat="sign_green",
              text_mat="sign_white")
gbr.post_sign(b, "weight", -5.2, SPAN / 2 + 6.0, math.pi, [("WEIGHT", 0.13), ("LIMIT", 0.13), ("15 TONS", 0.15)], board=(0.8, 0.9))
gbr.post_sign(b, "us30", 5.2, -SPAN / 2 - 12.0, 0.0, [("US", 0.16), ("30", 0.3)], board=(0.7, 0.75))
b.finish(os.path.join(ROOT, "godot_project", "remake", "buildings", "P-BR-US30.glb"))
