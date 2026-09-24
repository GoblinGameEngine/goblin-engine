"""
P-ELEV -- Pruett Farmers Co-operative elevator (crib-built country grain elevator), scale
shed and scale office.

Real example: Penfield Elevators, East Elevator, Front Street, Penfield, Champaign Co., IL --
HAER/HABS IL-1133-B (il0569) + site plan (il0476) (remake/reference/P-ELEV/).  Built 1919 on a
concrete foundation, bins of crib construction, cupola/headhouse framed in 2x6 studs, sheathed
in corrugated sheet metal from the outset, single leg driven originally by a gasoline engine,
wagon-scale shed added on the side c.1930.  Measured drawings: basement/first-floor/loft/
headhouse plans, 4 elevations (the west one carries a painted company sign), 2 sections.
Dimensions from Section AA (scale bar 10' = 225 px): bin block ~27' wide, eave 41'-3" above
grade, cupola ~10' wide, cupola eave ~63'-7", ridge ~67'-10"; driveway through the centre over
an 8' boot pit; hopper-bottom bins; scale shed ~12'-5" wide, eave ~15'.
Game use: walk-through driveway with working doors, ladder up the leg to the bin-top gallery
and the cupola (view over the village), scale shed with a truck scale, scale office.
Origin: centre of the bin block at grade. +Y north (driveway runs N-S).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbfurn as fu  # noqa: E402
import gbhouse as gh  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-elev")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-ELEV.glb")

b = g.Building("P-ELEV", TEX)
for k, t, tile in (("metal", "metal", 2.44), ("metal_roof", "metal_roof", 2.44), ("drive", "driveway", 3.0),
                   ("wood", "wood_int", 2.0), ("concrete", "concrete", 2.0), ("osiding", "office_siding", 1.0),
                   ("oroof", "office_roof", 1.0), ("trim", "trim", 1.0), ("panel", "sign_panel", 1.0),
                   ("owall", "office_wall", 2.0), ("ofloor", "office_floor", 2.0), ("door", "door", 1.0),
                   ("furniture", "furniture", 1.0), ("iron", "iron", 0.5)):
    b.mat(k, tex=t, tile_m=tile)
gh.std_house_materials(b, [])
for k, c in (("red", (0.62, 0.12, 0.1)), ("green", (0.12, 0.35, 0.18)), ("black", (0.06, 0.06, 0.06)),
             ("yellow", (0.9, 0.75, 0.15)), ("grain", (0.8, 0.66, 0.35))):
    b.mat(k, color=c, rough=0.6)


W, D = g.ft(27, 4), g.ft(29, 0)
X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
T = 0.15
EAVE = g.ft(41, 3)
PITCH = 33.0
DRV = g.ft(12, 0) / 2              # driveway half width
BIN_FLOOR = 4.2                    # underside of the overhead bin = driveway ceiling
GALLERY = EAVE + 0.05              # bin-top (distributor) floor
HH_W, HH_D = g.ft(10, 0), g.ft(14, 6)
HH_EAVE = g.ft(63, 7)
HH_RIDGE = g.ft(67, 10)
HH_FLOOR = HH_EAVE - 3.0           # head-pulley floor in the cupola

sh = b.part("shell-col")
sh.box((X0 - 0.05, Y0 - 0.05, -g.FOUND_DEPTH), (X1 + 0.05, Y1 + 0.05, 0.05), "concrete", sides="xXyY")
# upper foundation band stops at the drive-through and scale-shed doors (driveway is at grade)
for (xa, xb) in ((X0 - 0.05, -DRV + 0.1), (DRV - 0.1, X1 + 0.05)):
    for (ya, yb) in ((Y0 - 0.05, Y0), (Y1, Y1 + 0.05)):
        sh.box((xa, ya, 0.05), (xb, yb, 0.25), "concrete")
sh.box((X0 - 0.05, Y0, 0.05), (X0, Y1, 0.25), "concrete")
for (ya, yb) in ((Y0, -0.5), (0.5, Y1)):
    sh.box((X1, ya, 0.05), (X1 + 0.05, yb, 0.25), "concrete")
# driveway doors N + S (big double doors), small door into the scale shed (E), sign panel on W
ops = {
    "N": [dict(off=W / 2 - DRV + 0.1, w=2 * DRV - 0.2, sill=0.05, head=4.0)],
    "S": [dict(off=W / 2 - DRV + 0.1, w=2 * DRV - 0.2, sill=0.05, head=4.0)],
    "E": [dict(off=D / 2 - 0.5, w=1.0, sill=0.05, head=2.1)],
    "W": [],
}
fr = {
    "S": g.wall(sh, (X0, Y0), (X1, Y0), 0.05, EAVE, T, ops["S"], "metal", "wood"),
    "E": g.wall(sh, (X1, Y0), (X1, Y1), 0.05, EAVE, T, ops["E"], "metal", "wood"),
    "N": g.wall(sh, (X1, Y1), (X0, Y1), 0.05, EAVE, T, ops["N"], "metal", "wood"),
    "W": g.wall(sh, (X0, Y1), (X0, Y0), 0.05, EAVE, T, ops["W"], "metal", "wood"),
}
# gable ends above the eave (ridge N-S)
ridge = EAVE + W / 2 * math.tan(math.radians(PITCH))
g.gable_infill(sh, (X0, Y0), (X1, Y0), EAVE, ridge - 0.08, T, "metal", "wood")
g.gable_infill(sh, (X1, Y1), (X0, Y1), EAVE, ridge - 0.08, T, "metal", "wood")
roof = b.part("roof-col")
# main roof in three pieces so the cupola rises through an opening (no roof slab inside it)
_hh_y = g.ft(14, 6) / 2
for (ya, yb) in ((Y0 - 0.2, -_hh_y), (_hh_y, Y1 + 0.2)):
    g.gable_roof(roof, X0, X1, ya, yb, EAVE, PITCH, overhang_eave=0.3, overhang_rake=0.0, thick=0.12, mat_top="metal_roof",
                 mat_under="wood", ridge_axis="y", fascia="metal")
_tn = math.tan(math.radians(PITCH))
_hw = g.ft(10, 0) / 2
for sgn in (-1, 1):
    ze, zc = EAVE - 0.3 * _tn, EAVE + (W / 2 - _hw) * _tn
    q = [(sgn * (W / 2 + 0.3), -_hh_y, ze), (sgn * _hw, -_hh_y, zc), (sgn * _hw, _hh_y, zc), (sgn * (W / 2 + 0.3), _hh_y, ze)]
    nz = ((q[1][0] - q[0][0]) * (q[2][1] - q[0][1]) - (q[1][1] - q[0][1]) * (q[2][0] - q[0][0]))
    if nz < 0:
        q = q[::-1]
    roof.face(q, "metal_roof")
    roof.face([(v[0], v[1], v[2] - 0.14) for v in q[::-1]], "wood")
for side in ("N", "S"):
    g.door(b, "doorframe", fr[side], ops[side][0]["off"], ops[side][0]["w"], 4.0, T, f"drive_{side}", swing_in=False,
           leaves=2, mat="metal", threshold_z=0.05, panels=[(0.08, 0.08, 0.92, 0.92)], casing=0.08, trim="wood", leaf_thick=0.08)
g.door(b, "doorframe", fr["E"], ops["E"][0]["off"], 1.0, 2.1, T, "to_scale", swing_in=True, leaves=1, mat="wood",
       threshold_z=0.05, panels=[(0.12, 0.08, 0.88, 0.92)], casing=0.06, trim="wood")

# driveway floor (heavy planks) with the dump-pit grate; the four corner bins either side
fl = b.part("floor-col")
fl.box((X0 + T, Y0 + T, 0.0), (-0.7, Y1 - T, 0.05), "drive", sides="Z")
fl.box((0.7, Y0 + T, 0.0), (X1 - T, Y1 - T, 0.05), "drive", sides="Z")
fl.box((-0.7, Y0 + T, 0.0), (0.7, -1.0, 0.05), "drive", sides="Z")
fl.box((-0.7, 1.0, 0.0), (0.7, Y1 - T, 0.05), "drive", sides="Z")
gr = b.part("pit_grate-col")
for k in range(15):
    x = -0.68 + k * 0.097
    gr.box((x, -1.0, 0.0), (x + 0.03, 1.0, 0.05), "iron")
gr.box((-0.7, -1.0, 0.0), (0.7, 1.0, 0.012), "iron")        # walkable plate under the bars (collision)
pit = b.part("pit")
pit.prism([(-0.7, -1.0), (0.7, -1.0), (0.7, 1.0), (-0.7, 1.0)], -2.4, -0.01, "concrete", caps=True)
bins = b.part("bins-col")
PASS_Y, PASS_Z = 0.55, 2.3               # plank-lined passage through the east bins: driveway <-> scale-shed door
for sx in (-1, 1):
    xa, xb = sorted((sx * DRV, sx * (W / 2 - T)))
    if sx < 0:
        bins.box((xa, Y0 + T, 0.05), (xb, Y1 - T, EAVE), "wood")
    else:
        bins.box((xa, Y0 + T, 0.05), (xb, -PASS_Y, EAVE), "wood")
        bins.box((xa, PASS_Y, 0.05), (xb, Y1 - T, EAVE), "wood")
        bins.box((xa, -PASS_Y, PASS_Z), (xb, PASS_Y, EAVE), "wood")
        b.empty("light_passage", ((xa + xb) / 2, 0.0, PASS_Z - 0.2))
    for yy in (Y0 + T + 0.6, -0.6 if sx < 0 else -0.95, 0.6 if sx < 0 else 0.95, Y1 - T - 0.6):   # hopper chutes into the drive
        bins.box((sx * DRV - (0.25 if sx > 0 else -0.05), yy - 0.15, 1.9), (sx * DRV + (0.05 if sx > 0 else 0.25), yy + 0.15, 2.4), "wood")
# overhead bin above the driveway, hopper bottom (the driveway ceiling), hatch for the ladder shaft
LAD_X, LAD_Y = 0.9, 1.6                   # inside the cupola footprint so the ladder runs straight up
bins.box((-DRV, Y0 + T, BIN_FLOOR), (LAD_X - 0.45, Y1 - T, EAVE), "wood")
bins.box((LAD_X - 0.45, Y0 + T, BIN_FLOOR), (DRV, LAD_Y - 0.45, EAVE), "wood")
bins.box((LAD_X - 0.45, LAD_Y + 0.45, BIN_FLOOR), (DRV, Y1 - T, EAVE), "wood")
# the leg: bucket elevator casing from the boot pit to the cupola, with the head pulley housing
leg = b.part("leg-col")
leg.box((LAD_X - 0.4, 0.4, -2.4), (LAD_X + 0.25, 1.15, HH_EAVE - 0.6), "wood")
leg.box((LAD_X - 0.55, 0.3, HH_EAVE - 1.3), (LAD_X + 0.4, 1.25, HH_EAVE - 0.5), "wood")
# ladder in its shaft beside the leg (driveway -> gallery -> cupola floor)
lad = b.part("ladder_leg")
for side in (-0.22, 0.22):
    lad.box((LAD_X + side - 0.025, LAD_Y + 0.28, 0.05), (LAD_X + side + 0.025, LAD_Y + 0.33, HH_FLOOR + 1.1), "iron")
z = 0.35
while z < HH_FLOOR + 1.0:
    lad.box((LAD_X - 0.22, LAD_Y + 0.29, z), (LAD_X + 0.22, LAD_Y + 0.32, z + 0.03), "iron")
    z += 0.3
# bin-top gallery floor (plank), with the ladder hole; distributor spouts down into the bins
gal = b.part("gallery-col")
g.floor_with_holes(gal, X0 + T, X1 - T, Y0 + T, Y1 - T, GALLERY, 0.08, [(LAD_X - 0.45, LAD_X + 0.45, LAD_Y - 0.45, LAD_Y + 0.45)],
                   "wood", "wood")
g.spindle_rail(gal, [(LAD_X - 0.45, LAD_Y - 0.45), (LAD_X - 0.45, LAD_Y + 0.45), (LAD_X + 0.45, LAD_Y + 0.45)], GALLERY, 1.0, 0.25, "wood")
for (sx_, sy_) in ((-2.5, -2.5), (-2.5, 2.5), (2.5, -2.5), (2.5, 2.5), (0.0, -2.0)):
    gal.box((sx_ - 0.1, sy_ - 0.1, GALLERY), (sx_ + 0.1, sy_ + 0.1, GALLERY + 0.6), "iron")
b.empty("light_gallery", (0.0, 0.0, GALLERY + 2.0))
b.empty("light_drive", (0.0, -2.5, BIN_FLOOR - 0.3))
b.empty("light_drive", (0.0, 2.5, BIN_FLOOR - 0.3))

# cupola / headhouse: walls from the gallery through the roof, windows each side, gable roof
hh = b.part("headhouse-col")
hx0, hx1, hy0, hy1 = -HH_W / 2, HH_W / 2, -HH_D / 2, HH_D / 2
hops = {k: [dict(off=(HH_W if k in "NS" else HH_D) / 2 - 0.4, w=0.8, sill=HH_FLOOR + 0.9, head=HH_FLOOR + 1.8)] for k in "NSEW"}
hfr = {
    "S": g.wall_profile(hh, (hx0, hy0), (hx1, hy0), GALLERY, g.gable_top(HH_W, HH_EAVE, HH_RIDGE - 0.08), 0.12, hops["S"], "metal", "wood"),
    "E": g.wall(hh, (hx1, hy0), (hx1, hy1), GALLERY, HH_EAVE, 0.12, hops["E"], "metal", "wood"),
    "N": g.wall_profile(hh, (hx1, hy1), (hx0, hy1), GALLERY, g.gable_top(HH_W, HH_EAVE, HH_RIDGE - 0.08), 0.12, hops["N"], "metal", "wood"),
    "W": g.wall(hh, (hx0, hy1), (hx0, hy0), GALLERY, HH_EAVE, 0.12, hops["W"], "metal", "wood"),
}
for k in "NSEW":
    op = hops[k][0]
    g.window(b, "windows", hfr[k], op["off"], op["w"], op["sill"], op["head"], 0.12, sash_rows=1, sash_cols=2,
             glass_name="glass", casing=0.05, mats={"trim": "wood"})
g.floor_with_holes(hh, hx0 + 0.12, hx1 - 0.12, hy0 + 0.12, hy1 - 0.12, HH_FLOOR, 0.08,
                   [(LAD_X - 0.45, LAD_X + 0.45, LAD_Y - 0.45, LAD_Y + 0.45)] if hx0 < LAD_X < hx1 and hy0 < LAD_Y < hy1 else [],
                   "wood", "wood")
hr = b.part("headhouse_roof-col")
g.gable_roof(hr, hx0, hx1, hy0, hy1, HH_EAVE, math.degrees(math.atan((HH_RIDGE - HH_EAVE) / (HH_W / 2))), 0.25, 0.2, 0.1,
             "metal_roof", "wood", ridge_axis="y", fascia="metal")
hr.box((-0.02, hy1 - 0.4, HH_RIDGE), (0.02, hy1 - 0.36, HH_RIDGE + 1.2), "iron")          # lightning rod
hr.cylinder((0.0, hy1 - 0.38), 0.05, HH_RIDGE + 1.0, HH_RIDGE + 1.1, "glass", n=10)
b.empty("light_cupola", (0.0, 0.0, HH_EAVE - 0.3))
# diagonal cupola bracing seen in Section AA
for sx in (-1, 1):
    hh.box((sx * (HH_W / 2 - 0.3) - 0.08, hy0 + 0.3, GALLERY), (sx * (HH_W / 2 - 0.3) + 0.08, hy0 + 0.46, HH_FLOOR), "wood")

# scale shed (east, c.1930): drive-through, shed roof, truck scale platform
SX0, SX1 = X1, X1 + g.ft(12, 5)
ss = b.part("scaleshed-col")
s_hi, s_lo = g.ft(17, 0), g.ft(15, 3)
sops = [dict(off=0.4, w=SX1 - SX0 - 0.8, sill=0.05, head=3.9)]
g.wall(ss, (SX1, Y0), (SX1, Y1), 0.05, s_lo, T, [], "metal", "wood")
for (a, c, nm) in (((SX0, Y0), (SX1, Y0), "S"), ((SX1, Y1), (SX0, Y1), "N")):
    L = SX1 - SX0
    top = (lambda uu, a=a, c=c: s_hi + (s_lo - s_hi) * (abs((a[0] + (c[0] - a[0]) * uu / L) - SX0) / L))
    g.wall_profile(ss, a, c, 0.05, top, T, sops, "metal", "wood")
sr = [(SX0, Y0 - 0.3, s_hi), (SX1 + 0.3, Y0 - 0.3, s_lo - 0.05), (SX1 + 0.3, Y1 + 0.3, s_lo - 0.05), (SX0, Y1 + 0.3, s_hi)]
b.part("scaleshed_roof-col").face(sr, "metal_roof")
b.part("scaleshed_roof-col").face(sr[::-1], "wood")
scale = b.part("truck_scale-col")
scale.box((SX0 + 0.5, Y0 + 0.3, -0.02), (SX1 - 0.5, Y1 - 0.3, 0.07), "wood")
for (ya, yb) in ((Y0 + 0.3, Y0 + 0.36), (Y1 - 0.36, Y1 - 0.3)):
    scale.box((SX0 + 0.5, ya, -0.02), (SX1 - 0.5, yb, 0.08), "iron")
b.empty("light_scale", ((SX0 + SX1) / 2, 0.0, s_lo - 0.4))

# scale office (site plan: small frame building beside the scale) -- uses the house builder
OX0, OY0 = SX1 + 2.0, -2.8
ospec = dict(
    t_ext=0.15, t_int=0.1, era="modern", furnish=True,
    mats=dict(ext="osiding", int="owall", roof="oroof", found="concrete", floor="ofloor", ceiling="owall", trim="trim",
              door="door", fascia="trim", porch="wood", post="trim", furn="furniture"),
    blocks=[dict(name="office", rect=(OX0, OY0, OX0 + 4.3, OY0 + 5.6), floors=[(0.35, 2.75)], wall_top=2.85, found_top=0.3,
                 roof=dict(type="gable", ridge="y", pitch=30, eave_oh=0.35, rake_oh=0.3, thick=0.12))],
    rooms=[dict(name="OFFICE", rect=(OX0, OY0, OX0 + 4.3, OY0 + 5.6), type="sitting")],
    doors=[dict(name="office", at=(OX0 + 1.2, OY0 + 5.6), w=0.85, ext=True, glazed=(0.15, 0.5, 0.85, 0.9))],
    windows=[dict(at=(OX0, OY0 + 2.8), w=1.2, sill=0.9, h=1.2, cols=2),            # looks out on the scale
             dict(at=(OX0 + 2.9, OY0 + 5.6), w=0.9, sill=0.9, h=1.2), dict(at=(OX0 + 4.3, OY0 + 2.0), w=0.9, sill=0.9, h=1.2)],
    porches=[dict(rect=(OX0 + 0.6, OY0 + 5.6, OX0 + 1.8, OY0 + 6.4), z=0.33, post_top=0.35, posts=[], beam=False, skirt_mat="concrete",
                  steps=dict(at=(OX0 + 1.2, OY0 + 6.4), dir=(0, 1), width=1.1, mat="concrete"))],
    chimneys=[dict(at=(OX0 + 3.3, OY0 + 1.0), w=0.25, d=0.25, z0=2.75, top=4.8, mat="iron")],
)
gh.House(b, ospec).build()
op_ = b.part("office_fittings-col")
op_.box((OX0 + 0.16, OY0 + 2.0, 1.0), (OX0 + 0.45, OY0 + 3.6, 1.9), "iron")                 # the scale beam cabinet
fu.potbelly_stove(op_, (OX0 + 3.3, OY0 + 1.0, 0.35), "iron")
fu.safe(op_, (OX0 + 3.7, OY0 + 4.8, 0.35), -90, "iron", "brass")

# ------------------------------------------------------------------ signs, yard fence
sg = b.part("signs-col")
# painted company sign on the west wall (the Penfield west elevation carries one the same way)
sg.box((X0 - 0.03, -2.6, 6.2), (X0, 2.6, 9.4), "panel")
sg.box((X0 - 0.035, -2.5, 6.3), (X0 - 0.03, 2.5, 6.4), "green")
sg.box((X0 - 0.035, -2.5, 9.2), (X0 - 0.03, 2.5, 9.3), "green")
g.text_mesh(b, "sign_coop_1", "PRUETT FARMERS", 0.55, (X0 - 0.04, 0.0, 8.55), -math.pi / 2, "green", extrude=0.01)
g.text_mesh(b, "sign_coop_2", "CO-OP", 0.85, (X0 - 0.04, 0.0, 7.55), -math.pi / 2, "red", extrude=0.01)
g.text_mesh(b, "sign_coop_3", "GRAIN  ·  SEED  ·  FEED", 0.3, (X0 - 0.04, 0.0, 6.75), -math.pi / 2, "green", extrude=0.01,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
# scale shed + office signs
sg.box((SX0 + 0.3, Y1 + 0.02, 4.2), (SX1 - 0.3, Y1 + 0.05, 4.85), "yellow")
g.text_mesh(b, "sign_scale_1", "SCALE", 0.3, ((SX0 + SX1) / 2, Y1 + 0.055, 4.62), math.pi, "black", extrude=0.005,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
g.text_mesh(b, "sign_scale_2", "ALL TRUCKS STOP", 0.13, ((SX0 + SX1) / 2, Y1 + 0.055, 4.33), math.pi, "black", extrude=0.004,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
g.text_mesh(b, "sign_office_1", "OFFICE", 0.14, (OX0 + 1.2, OY0 + 5.61, 2.45), math.pi, "black", extrude=0.004,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
g.text_mesh(b, "sign_office_2", "CO-OP MEMBERS WELCOME", 0.06, (OX0 + 1.2, OY0 + 5.61, 2.3), math.pi, "black", extrude=0.003,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
# chain-link yard fence along the back with a gate + sign
gh.chainlink_fence(b, [(X0 - 3.0, Y0 - 6.0), (SX1 + 7.0, Y0 - 6.0)], 1.8, name="yard_fence", gate=(0, 3.0 + W / 2 - 1.8, 3.6))
# sign on the fence panel beside the gate (the gate spans x -1.8..1.8)
sg.box((X0 + 0.5, Y0 - 6.05, 1.0), (X0 + 1.9, Y0 - 6.02, 1.5), "panel")
g.text_mesh(b, "sign_notrespass_1", "NO TRESPASSING", 0.09, (X0 + 1.2, Y0 - 6.055, 1.34), 0.0, "red", extrude=0.003,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
g.text_mesh(b, "sign_notrespass_2", "PRUETT FARMERS CO-OP", 0.055, (X0 + 1.2, Y0 - 6.055, 1.16), 0.0, "black", extrude=0.003,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
# spilled grain on the driveway, a hand truck of sacks
b.part("grain").box((-0.9, -1.5, 0.05), (0.9, 1.5, 0.06), "grain")

b.finish(OUT)
