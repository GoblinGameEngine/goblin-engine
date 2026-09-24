"""
P-BR-RAIL -- C&NW main line over Deer Creek, west of Pruett (map crossing RAIL-03).

Real example: Norfolk Southern Railroad Bridge N-647.74 (Scioto Valley / N&W Stony Creek arch),
Pride, Ross Co., OH -- HAER OH-141 (remake/reference/P-BR-RAIL/): a single-track main line on
an embankment carried over a creek by a masonry arch culvert -- ca.1888 rock-faced ashlar
arch, extended 1909 in stone and brick, 1934 in concrete (16 photos + the railway's own plan
and section drawings extracted from the report).  Modelled as the ashlar arch (12' span) with
headwalls, wingwalls, coping and a date stone, carrying ballasted track on a 4.5 m fill.
Origin: track centreline at ground level (0) over the creek; track runs along +Y, creek along X.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbbridge as gbr  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
b = g.Building("P-BR-RAIL", os.path.join(ROOT, "remake", "textures", "p-bridges"))
gbr.bridge_materials(b)

SPAN = g.ft(12)
FILL = 4.5                   # track grade above the surrounding ground
BED = -2.4                   # creek bed well below the surrounding ground (arch opening ~4 m high)
BARREL = 12.0                # headwall to headwall along the creek
r = SPAN / 2
ZONE = r + 3.6               # headwall + wingwall half-width (fill retained vertically inside it)


def z_at(x, y):
    a, ax = abs(y), abs(x)
    ch, bank = 2.2, 3.0
    if a <= ch:
        z = BED
    elif a <= ch + bank:
        t = (a - ch) / bank
        z = BED * (1 - t * t * (3 - 2 * t))
    else:
        z = 0.0
    crest = 3.0
    XH = BARREL / 2 - 0.06                # fill steps down just BEHIND the headwall face
    if a <= r + 0.6:
        return z                          # arch opening: the creek channel runs straight through
    elif a <= ZONE:
        return FILL if ax <= XH else z
    if ax <= crest:
        return max(z, FILL)
    if ax <= crest + FILL * 1.5:
        return max(z, FILL - (ax - crest) / 1.5)
    return z


gbr.creek_terrain(b, L=60.0, W=40.0, ch_w=4.4, depth=2.4, bank_w=3.0, name="terrain", zfunc=z_at,
                  extra_xs=(-BARREL / 2 + 0.06, -BARREL / 2 + 0.05, BARREL / 2 - 0.06, BARREL / 2 - 0.05, -3.0, 3.0), extra_ys=(-ZONE, -ZONE - 0.01, ZONE, ZONE + 0.01, -(r + 0.6), r + 0.6))
gbr.water(b, -20.0, 20.0, -2.2, 2.2, BED + 0.35)
# the embankment is cut off where this standalone patch ends (it will join the line's grade when
# the crossing is placed on the ring map): close the cut with earth faces down to the ground
end = b.part("embankment_ends-col")
xs_ = [-20.0 + 0.5 * i for i in range(81)]
for yy in (-30.0, 30.0):
    for xa, xb in zip(xs_, xs_[1:]):
        za, zb = z_at(xa, yy), z_at(xb, yy)
        if max(za, zb) <= 0.01:
            continue
        q = [(xa, yy, 0.0), (xb, yy, 0.0), (xb, yy, zb), (xa, yy, za)]
        end.face(q, "bank")
        end.face(q[::-1], "bank")
# fill cap over the barrel (the terrain dips through the arch, so cover it at track grade)
b.part("fill_cap-col").box((-BARREL / 2, -(r + 0.6), FILL - 0.3), (BARREL / 2, r + 0.6, FILL), "grass")
spring = gbr.arch_barrel(b, SPAN, FILL, BARREL, BED, name="arch")
gbr.track(b, -30.0, 30.0, FILL)
# date stone over the arch ring on the downstream face; milepost by the track
g.text_mesh(b, "sign_datestone", "C&NW 1893", 0.25, (BARREL / 2 + 0.01, 0.0, spring + r + 1.0), math.pi / 2, "sign_black", extrude=0.01)
gbr.post_sign(b, "milepost", 2.6, 8.0, -math.pi / 2, [("MP", 0.12), ("214", 0.18)], board=(0.35, 0.55), height=FILL + 1.2)
b.finish(os.path.join(ROOT, "godot_project", "remake", "buildings", "P-BR-RAIL.glb"))
