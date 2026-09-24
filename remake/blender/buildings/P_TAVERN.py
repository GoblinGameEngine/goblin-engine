"""
P-TAVERN -- Deer Creek Tavern, Pruett (Main St / US 30).

Real example: Hassler Tavern, U.S. Route 6, DePue (near Princeton), Bureau County, Illinois,
c.1840s brick stagecoach tavern -- HABS ILL-142 / IL-14 (remake/reference/P-TAVERN/).
Dimensions from HABS sheet 1 (first + second floor plans, N-S section, north front elevation
"as restored") and sheet 2 (east elevation, fireplace/mantel details); later frame kitchen
wing from sheet 1 ("later addition", 22'-1 1/2" long) and photo 1.

Plan coordinates: origin = centre of the brick block at grade, +X east, +Y north.
FRONT = NORTH (as drawn).  yn(v) converts "feet from the north face" to +Y.
Pruett use: bar room (east), fish-fry dining lounge (west), rooms to let upstairs,
keg cellar below, fish-fry kitchen in the frame wing.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from mathutils import Vector  # noqa: E402

import gbfurn as fu  # noqa: E402
import gblib as g  # noqa: E402
from gblib import ft  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-tavern")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-TAVERN.glb")

b = g.Building("P-TAVERN", TEX)
for k, t, tile in (("brick", "brick", 1.0), ("brick_arch", "brick_arch", 0.6), ("roof", "roof", 1.0),
                   ("found", "foundation", 1.2), ("trim", "trim", 1.0), ("porch", "porch", 2.0),
                   ("floor", "floor", 2.0), ("plaster", "plaster", 2.0), ("bar", "bar", 1.0), ("door", "door", 1.0),
                   ("shutter", "shutter", 1.0), ("siding", "siding", 1.0), ("lino", "lino", 0.9144),
                   ("dirt", "dirt", 2.0), ("iron", "iron", 0.5), ("furn", "furniture", 1.0), ("ceiling", "ceiling", 2.0)):
    b.mat(k, tex=t, tile_m=tile)
b.mat("glass", color=(0.72, 0.8, 0.84), rough=0.05, alpha=0.2)
b.mat("brass", color=(0.75, 0.58, 0.26), rough=0.3, metal=1.0)
b.mat("threshold", color=(0.45, 0.43, 0.4), rough=0.9)
b.mat("mirror", color=(0.85, 0.88, 0.9), rough=0.03, metal=1.0)
b.mat("bottle", color=(0.25, 0.4, 0.2), rough=0.1, alpha=0.7)
b.mat("linen", color=(0.9, 0.88, 0.82), rough=0.9)
b.mat("quilt", color=(0.55, 0.18, 0.16), rough=0.9)
b.mat("china", color=(0.95, 0.95, 0.93), rough=0.2)
b.mat("steel", color=(0.7, 0.72, 0.74), rough=0.35, metal=0.9)
b.mat("enamel", color=(0.93, 0.93, 0.9), rough=0.3)
b.mat("oil", color=(0.55, 0.42, 0.1), rough=0.1)
b.mat("vinyl", color=(0.55, 0.08, 0.08), rough=0.5)
b.mat("neon_red", color=(1.0, 0.15, 0.1), emission=(1.0, 0.12, 0.08))
b.mat("neon_blue", color=(0.2, 0.5, 1.0), emission=(0.15, 0.45, 1.0))
b.mat("signboard", color=(0.12, 0.2, 0.14), rough=0.6)
b.mat("gold", color=(0.85, 0.7, 0.3), rough=0.35, metal=0.8)
b.mat("chalk", color=(0.1, 0.12, 0.1), rough=0.9)
b.mat("chalktext", color=(0.93, 0.93, 0.9), rough=0.9)
b.mat("rail", color=(0.45, 0.36, 0.26), rough=0.9)

# ------------------------------------------------------------------ dimensions (HABS sheet 1)
W = ft(37, 1)                 # east-west, sum of the front dimension string
D = ft(26, 10)                # north-south
X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
T = 0.33                      # brick bearing walls (plan poché ~13")
FL1 = ft(2, 6)                # porch / first floor above grade (section)
CEIL1 = FL1 + ft(9, 9.5)      # first-floor ceiling (section)
FL2 = CEIL1 + ft(1, 1)        # second floor (section)
KNEE = FL2 + ft(3, 0)         # brick knee wall top under the eaves (section / elevation)
RIDGE = ft(23, 7)             # elevation, scaled at 1/4" = 1'-0"
PITCH = math.degrees(math.atan((RIDGE - KNEE) / (D / 2)))
CEIL2 = FL2 + ft(7, 6)        # second-floor flat ceiling (section)
PORCH = ft(5, 10)             # porch depth front and rear (plan)
WIN_W, WIN_SILL, WIN_H = ft(3, 3.5), FL1 + ft(2, 4.25), ft(5, 7)
CELLAR = FL1 - 0.25 - ft(8, 0)    # dirt cellar floor (section: 8'-0" clear)


def yn(feet):                 # feet measured from the north (front) face -> +Y
    return Y1 - ft(feet)


def xw(feet):                 # feet measured from the west face -> +X
    return X0 + ft(feet)


front_win = [3.208, 9.8125, 24.979, 31.583]          # west edges of the 4 front/rear windows (ft)
door_w_ft = (16.4375, 21.646)                          # main entrance opening incl. pilasters
DOOR_W = ft(door_w_ft[1] - door_w_ft[0])
DOOR_HEAD = FL1 + 2.35                                 # leaves 2.0 m + transom (elevation)

shell = b.part("shell-col")
# fieldstone base course, brick above
shell.box((X0 - 0.02, Y0 - 0.02, -0.3), (X1 + 0.02, Y1 + 0.02, 0.45), "found", sides="xXyY")


def ops_from_west(lefts_ft, w, sill, head, total_w=W):
    """Openings given by west-edge feet, for a wall that runs EAST->WEST (offsets from the east)."""
    return [dict(off=total_w - ft(l) - w, w=w, sill=sill, head=head) for l in lefts_ft]


walls1 = {
    # north (front) wall runs east -> west, interior (south) on its left
    "N": ((X1, Y1), (X0, Y1), ops_from_west(front_win, WIN_W, WIN_SILL, WIN_SILL + WIN_H)
          + [dict(off=W - ft(door_w_ft[1]), w=DOOR_W, sill=FL1, head=DOOR_HEAD)]),
    "S": ((X0, Y0), (X1, Y0), [dict(off=ft(l), w=WIN_W, sill=WIN_SILL, head=WIN_SILL + WIN_H) for l in front_win]
          + [dict(off=ft(door_w_ft[0]), w=DOOR_W, sill=FL1, head=DOOR_HEAD)]),
    "E": ((X1, Y0), (X1, Y1), [dict(off=ft(1, 5.5), w=ft(3, 3), sill=FL1, head=FL1 + 2.1)]),     # door to the wing
    "W": ((X0, Y1), (X0, Y0), [dict(off=ft(3, 7), w=WIN_W, sill=WIN_SILL, head=WIN_SILL + WIN_H),
                               dict(off=ft(3, 7) + WIN_W + ft(12, 2), w=WIN_W, sill=WIN_SILL, head=WIN_SILL + WIN_H)]),
}
fr = {}
for k in ("N", "S"):
    a, c, ops = walls1[k]
    fr[k] = g.wall(shell, a, c, 0.45, KNEE, T, ops, "brick", "plaster")
# gable end walls: first-floor openings + second-floor gable windows (2nd floor plan) in one profile
gw_w = ft(3, 2.5)
gable_ops = {
    "E": walls1["E"][2] + [dict(off=ft(7, 3), w=gw_w, sill=FL2 + 0.62, head=FL2 + 1.9),
                           dict(off=ft(7, 3) + gw_w + ft(6, 8), w=gw_w, sill=FL2 + 0.62, head=FL2 + 1.9)],
    "W": walls1["W"][2] + [dict(off=ft(6, 8.5), w=gw_w, sill=FL2 + 0.62, head=FL2 + 1.9),
                           dict(off=ft(6, 8.5) + gw_w + ft(7, 3), w=gw_w, sill=FL2 + 0.62, head=FL2 + 1.9)],
}
for k in ("E", "W"):
    a, c, _ = walls1[k]
    fr[k] = g.wall_profile(shell, a, c, 0.45, g.gable_top(D, KNEE, RIDGE - 0.12), T, gable_ops[k], "brick", "plaster")

# brick jack-arch lintels + stone sills over the ground-floor windows; shutters on the front (restored)
trimp = b.part("trim")
for k in ("N", "S", "E", "W"):
    ops = walls1[k][2] if k in ("N", "S") else gable_ops[k]
    for op in ops:
        g.lintel(trimp, fr[k], op["off"], op["w"], op["head"], "brick_arch", h=0.18, over=0.1)
        if op["sill"] > FL1 + 0.1:
            g.window(b, "windows", fr[k], op["off"], op["w"], op["sill"], op["head"], T, sash_rows=2, sash_cols=3,
                     glass_name="glass")
            if k == "N":
                g.shutter_pair(trimp, fr[k], op["off"], op["w"], op["sill"], op["head"], "shutter")

# ------------------------------------------------------------------ entrances (double doors + transom + pilasters)
for k in ("N", "S"):
    op = [o for o in walls1[k][2] if o["sill"] == FL1][0]
    inset = 0.18                                      # pilasters take the outer part of the opening
    g.door(b, "doorframe", fr[k], op["off"] + inset, op["w"] - 2 * inset, FL1 + 2.0, T, "front" if k == "N" else "rear",
           swing_in=True, leaves=2, panels=[(0.15, 0.62, 0.85, 0.94), (0.15, 0.36, 0.85, 0.58), (0.15, 0.06, 0.85, 0.3)],
           mat="door", threshold_z=FL1)
    g.transom(b, fr[k], op["off"] + inset, op["w"] - 2 * inset, FL1 + 2.0, DOOR_HEAD, T, lights=4)
    for side in (op["off"], op["off"] + op["w"] - inset):                          # pilasters (photo 3)
        trimp.obox(fr[k], (side, -0.06, FL1), (side + inset, 0.0, DOOR_HEAD + 0.12), "trim")
        shell.obox(fr[k], (side, 0.0, FL1), (side + inset, T, DOOR_HEAD), "brick",
                   mats={"v1": "plaster"})                                          # fill behind the pilaster
    trimp.obox(fr[k], (op["off"] - 0.12, -0.12, DOOR_HEAD + 0.12), (op["off"] + op["w"] + 0.12, 0.0, DOOR_HEAD + 0.35), "trim")

# kitchen-wing door in the east wall (inside the wing)
opE = walls1["E"][2][0]
g.door(b, "doorframe", fr["E"], opE["off"], opE["w"], opE["head"], T, "bar_kitchen", swing_in=True, leaves=1, mat="door",
       threshold_z=FL1)

# ------------------------------------------------------------------ roof (ridge E-W) over both porches
roof = b.part("roof-col")
g.gable_roof_x(roof, X0, X1, Y0, Y1, KNEE, PITCH, overhang_eave=PORCH + 0.3, overhang_rake=0.3, thick=0.16,
               mat_top="roof", mat_under="ceiling", fascia="trim")
roof.box((X0 - 0.3, -0.09, RIDGE + 0.02), (X1 + 0.3, 0.09, RIDGE + 0.1), "roof")
# end chimneys, centred on the ridge (plan: fireplaces mid-wall at both gable ends)
for sx in (-1, 1):
    cx = sx * (W / 2 - T - 0.2)
    roof.box((cx - 0.35, -0.45, KNEE), (cx + 0.35, 0.45, ft(27, 9)), "brick")
    roof.box((cx - 0.4, -0.5, ft(27, 9) - 0.1), (cx + 0.4, 0.5, ft(27, 9)), "brick")

# restored front dormer over the west bedroom (elevation "dormers restored"; plan "original dormer")
dm = b.part("dormer-col")
dx, dw = xw(9.8), 1.2
dz0, dz1 = KNEE + 0.1, KNEE + 1.15
dy = Y1 - 0.15
dm.box((dx - dw / 2, dy - 1.4, dz0), (dx - dw / 2 + 0.1, dy, dz1), "trim")
dm.box((dx + dw / 2 - 0.1, dy - 1.4, dz0), (dx + dw / 2, dy, dz1), "trim")
g.gable_roof(dm, dx - dw / 2, dx + dw / 2, dy - 1.6, dy + 0.12, dz1, 42, 0.08, 0.1, 0.06, "roof", "trim", fascia="trim")
dfr = g.wall(dm, (dx + dw / 2, dy), (dx - dw / 2, dy), dz0, dz1, 0.08,
             [dict(off=0.15, w=dw - 0.3, sill=dz0 + 0.12, head=dz1 - 0.08)], "trim", "trim")
g.window(b, "windows", dfr, 0.15, dw - 0.3, dz0 + 0.12, dz1 - 0.08, 0.08, sash_rows=2, sash_cols=2, glass_name="glass")

# ------------------------------------------------------------------ porches (front + rear), Tuscan columns
por = b.part("porch-col")
col_x = [xw(0.36), xw(13.6), xw(23.1), xw(36.4)]
for side in (1, -1):
    y_wall = Y1 if side > 0 else Y0
    y_out = y_wall + side * PORCH
    ya, yb = sorted((y_wall, y_out))
    por.box((X0, ya, FL1 - 0.08), (X1, yb, FL1), "porch", mats={"x": "trim", "X": "trim", "y": "trim", "Y": "trim", "z": "porch"})
    por.box((X0, ya, 0.0), (X1, yb, FL1 - 0.08), "trim", sides="xXyY" if side else "")        # skirt board
    eave_z = KNEE - (PORCH) * math.tan(math.radians(PITCH))
    por.box((X0, y_out - side * 0.25 - 0.1, eave_z - 0.32), (X1, y_out - side * 0.25 + 0.1, eave_z + 0.05), "trim")  # beam
    for cx in col_x:
        g.column(por, cx, y_out - side * 0.25, FL1, eave_z - 0.32, 0.13, "trim")
    # steps between the middle columns (plan: 9'-8" wide)
    nst = 4
    for k in range(nst):
        z = FL1 - (k + 1) * FL1 / nst
        yy0 = y_out + side * k * 0.28
        yy1 = y_out + side * (k + 1) * 0.28
        por.box((col_x[1] + 0.2, min(yy0, yy1), 0), (col_x[2] - 0.2, max(yy0, yy1), z + FL1 / nst), "porch")

# ------------------------------------------------------------------ first floor: floor slab w/ cellar-stair hole
HALL_W0, HALL_W1 = xw(15.9), xw(15.9) + 0.12          # frame wall, lounge side
HALL_E0, HALL_E1 = xw(21.9), xw(21.9) + T             # brick wall, bar side
ST_X0, ST_X1 = HALL_E0 - 0.86, HALL_E0 - 0.01          # stair along the east hall wall
# Up flight (15 R) starts 2.25 m in from the front face and runs south; the cellar flight
# (12 R) tucks entirely under it: landing under the high end, descending back north, so no
# part of the cellar well lies outside the up-stair's footprint (checked: 2.16 + 0.8 <= 3.0).
UP_RUN, UP_N = 0.20, 15
UP_Y0 = Y1 - 2.25
UP_Y1 = UP_Y0 - UP_RUN * UP_N
CEL_TOP_Y = UP_Y1 + 0.8
CEL_N, CEL_RUN = 12, 0.18
CEL_BOT_Y = CEL_TOP_Y + CEL_RUN * CEL_N
assert CEL_BOT_Y <= UP_Y0

fl = b.part("floors-col")
g.floor_with_holes(fl, X0 + T, X1 - T, Y0 + T, Y1 - T, FL1, 0.25,
                   [(ST_X0, ST_X1, CEL_TOP_Y, CEL_BOT_Y)], "floor", "ceiling")
g.floor_with_holes(fl, X0 + T, X1 - T, Y0 + T, Y1 - T, FL2, 0.3,
                   [(ST_X0, ST_X1, UP_Y1 - 0.05, UP_Y0)], "floor", "ceiling")
# 1st-floor plaster ceiling, open over the stair well (headroom for the flight)
g.floor_with_holes(fl, X0 + T, X1 - T, Y0 + T, Y1 - T, CEIL1 + 0.02, 0.02, [(ST_X0, ST_X1, UP_Y1 - 0.05, UP_Y0)], "ceiling", "ceiling")

# interior partitions, ground floor
part = b.part("partitions-col")
lounge_doors = [dict(off=ft(4.0), w=ft(2, 10), sill=FL1, head=FL1 + 2.1),
                dict(off=ft(20.0), w=ft(2, 10), sill=FL1, head=FL1 + 2.1)]
# west hall wall runs south->north (left = west = lounge): offsets from the south face
wfr = g.wall(part, (HALL_W0 + 0.12, Y0 + T), (HALL_W0 + 0.12, Y1 - T), FL1, CEIL1, 0.12,
             [dict(off=D - 2 * T - o["off"] - o["w"], w=o["w"], sill=o["sill"], head=o["head"]) for o in lounge_doors],
             "plaster", "plaster")
for i, o in enumerate(lounge_doors):
    g.door(b, "doorframe", wfr, D - 2 * T - o["off"] - o["w"], o["w"], o["head"], 0.12, f"lounge_{'N' if i == 0 else 'S'}",
           swing_in=True, leaves=1, mat="door", threshold_z=FL1, panels=[(0.15, 0.55, 0.85, 0.92), (0.15, 0.08, 0.85, 0.45)])
# east hall wall (brick) runs north->south (left = east = bar room): offsets from the north face
efr = g.wall(part, (HALL_E0, Y1 - T), (HALL_E0, Y0 + T), FL1, CEIL1, T,
             [dict(off=o["off"] - T + 0.05, w=o["w"], sill=FL1, head=FL1 + 2.1) for o in lounge_doors], "plaster", "plaster")
for i, o in enumerate(lounge_doors):
    g.door(b, "doorframe", efr, o["off"] - T + 0.05, o["w"], FL1 + 2.1, T, f"bar_{'N' if i == 0 else 'S'}", swing_in=True,
           leaves=1, mat="door", threshold_z=FL1, panels=[(0.15, 0.55, 0.85, 0.92), (0.15, 0.08, 0.85, 0.45)])

# stairs: up (15 risers, section) and the cellar flight (12 risers) under it
g.stairs(b, "stair_up", (ST_X0, UP_Y0, FL1), (0, -1), ST_X1 - ST_X0, FL2 - FL1, UP_N, UP_RUN, "floor", "trim")
sr = b.part("stair_rail-col")
rh_ = (FL2 - FL1) / UP_N
rail_z = lambda y: FL1 + rh_ + 0.9 + (UP_Y0 - y) * (FL2 - FL1 - rh_) / (UP_N * UP_RUN)
for k in range(UP_N):                         # raking handrail + balusters following the pitch
    y = UP_Y0 - (k + 0.5) * UP_RUN
    z = FL1 + (k + 1) * rh_
    sr.box((ST_X0 + 0.005, y - 0.015, z), (ST_X0 + 0.04, y + 0.015, rail_z(y) - 0.02), "bar")
g.raking_rail(sr, (ST_X0 + 0.025, UP_Y0, rail_z(UP_Y0)), (ST_X0 + 0.025, UP_Y1, rail_z(UP_Y1)), "bar", w=0.07, h=0.06)
sr.box((ST_X0 - 0.03, UP_Y0 - 0.05, FL1), (ST_X0 + 0.08, UP_Y0 + 0.05, FL1 + 1.15), "bar")  # newel post
# under-stair plank closure with the cellar door (section "wood")
cl = b.part("understair-col")
rh_up = (FL2 - FL1) / UP_N
cdoor_off = (UP_Y0 - CEL_TOP_Y) + 0.03
cfr = g.wall_profile(cl, (ST_X0 - 0.03, UP_Y0), (ST_X0 - 0.03, UP_Y1), FL1,
                     lambda uu: max(FL1 + 0.05, FL1 + uu / UP_RUN * rh_up - 0.06), 0.03,
                     [dict(off=cdoor_off, w=0.76, sill=FL1, head=FL1 + 1.95)], "bar", "bar")
g.door(b, "doorframe", cfr, cdoor_off, 0.76, FL1 + 1.95, 0.03, "cellar", swing_in=False, leaves=1, mat="bar", threshold_z=FL1,
       panels=[(0.12, 0.1, 0.88, 0.92)])
g.stairs(b, "stair_cellar", (ST_X0, CEL_BOT_Y, CELLAR), (0, -1), ST_X1 - ST_X0, FL1 - 0.25 - CELLAR + 0.25, CEL_N, CEL_RUN,
         "floor", "trim")

# ------------------------------------------------------------------ cellar (8'-0", dirt floor, brick arch wall)
cel = b.part("cellar-col")
cel.box((X0 + T, Y0 + T, CELLAR - 0.1), (X1 - T, Y1 - T, CELLAR), "dirt", sides="Z")
for (a, c) in (((X0 + T, Y0 + T), (X1 - T, Y0 + T)), ((X1 - T, Y0 + T), (X1 - T, Y1 - T)),
               ((X1 - T, Y1 - T), (X0 + T, Y1 - T)), ((X0 + T, Y1 - T), (X0 + T, Y0 + T))):
    g.wall(cel, a, c, CELLAR, FL1 - 0.25, 0.02, [], "brick", "brick")
# cross wall under the hall/bar wall with an arched opening (section)
arch_y0, arch_w = -0.9, 1.3
afr = g.wall(cel, (HALL_E0, Y1 - T), (HALL_E0, Y0 + T), CELLAR, FL1 - 0.25, T,
             [dict(off=(Y1 - T) - (arch_y0 + arch_w), w=arch_w, sill=CELLAR, head=CELLAR + 1.75)], "brick", "brick")
for k in range(9):                                       # segmental arch ring
    a0, a1 = math.pi * k / 9, math.pi * (k + 1) / 9
    r = arch_w / 2
    cy = arch_y0 + r
    y_a, y_b = cy + r * math.cos(a0), cy + r * math.cos(a1)
    z_a, z_b = CELLAR + 1.75 + 0.35 * math.sin(a0), CELLAR + 1.75 + 0.35 * math.sin(a1)
    cel.box((HALL_E0, min(y_a, y_b), min(z_a, z_b)), (HALL_E0 + T, max(y_a, y_b), max(z_a, z_b) + 0.12), "brick_arch")
cf = b.part("cellar_stuff-col")
for i, (kx, ky) in enumerate(((X1 - 1.0, Y1 - 1.0), (X1 - 1.6, Y1 - 1.0), (X1 - 1.0, Y1 - 1.6), (X1 - 2.2, Y1 - 1.0),
                              (X1 - 1.6, Y1 - 1.6), (X1 - 1.0, Y1 - 2.2))):
    fu.keg(cf, (kx, ky, CELLAR), "furn", "iron")
fu.shelves(cf, (X0 + 1.3, Y1 - T - 0.25, CELLAR), 180, 1.8, 0.4, 1.8, 4, "furn")
fu.shelves(cf, (X0 + T + 0.25, 0.0, CELLAR), 90, 2.2, 0.4, 1.8, 4, "furn")
for k in range(12):                                   # canning jars on the shelves
    y = -0.9 + k * 0.16
    cf.cylinder((X0 + T + 0.25, y), 0.045, CELLAR + 0.105, CELLAR + 0.27, "bottle", n=8)
b.empty("light_cellar", (0.0, 0.0, FL1 - 0.35))
b.empty("light_cellar", (X1 - 2.0, Y1 - 2.0, FL1 - 0.35))

# ------------------------------------------------------------------ fireplaces (sheet 2 mantel details)
fp = b.part("fireplaces-col")
for (x_wall, sx, zf, rooms) in ((X0 + T, 1, FL1, "lounge"), (X1 - T, -1, FL1, "bar"), (X0 + T, 1, FL2, "bed_W"),
                               (X1 - T, -1, FL2, "bed_E")):
    bw, bd = 1.55, 0.45
    xa = x_wall
    xb = x_wall + sx * bd
    x_lo, x_hi = sorted((xa, xb))
    top = CEIL1 if zf == FL1 else KNEE + 0.8
    # chimney breast with a firebox recess (left, right, above)
    fp.box((x_lo, -bw / 2, zf), (x_hi, -0.42, top), "plaster")
    fp.box((x_lo, 0.42, zf), (x_hi, bw / 2, top), "plaster")
    fp.box((x_lo, -0.42, zf + 0.82), (x_hi, 0.42, top), "plaster")
    fb_lo, fb_hi = sorted((xa, xa + sx * 0.12))
    fp.box((fb_lo, -0.42, zf), (fb_hi, 0.42, zf + 0.82), "brick_arch")          # firebox back
    fu.mantel(fp, (xb, 0.0, zf), 90 if sx > 0 else -90, 1.6, "trim", "brick_arch", h=1.3, d=0.1, opening=(0.84, 0.82))
    b.empty("light_fire", (xa + sx * 0.3, 0.0, zf + 0.3))

# ------------------------------------------------------------------ bar room (east)
fz = FL1
bar = b.part("barroom-col")
bx = HALL_E1 + 0.3
fu.back_bar(bar, (bx, (yn(9.0) + yn(19.0)) / 2, fz), 90, ft(10), "bar", "mirror", "bottle")
fu.bar_counter(bar, (bx + 1.25, (yn(8.5) + yn(18.0)) / 2, fz), 90, ft(9.5), "bar", "bar", "brass")
for k in range(5):
    fu.stool(bar, (bx + 1.95, yn(9.3) + -k * 0.62, fz), "iron", "vinyl")
for (tx, ty) in ((X1 - 1.4, yn(4.5)), (X1 - 1.4, yn(22.0)), (bx + 2.6, yn(22.5))):
    fu.round_table(bar, (tx, ty, fz), 0.42, 0.75, "furn")
    for a in range(3):
        ang = a * 2 * math.pi / 3
        fu.chair(bar, (tx + 0.7 * math.cos(ang), ty + 0.7 * math.sin(ang), fz), math.degrees(ang) - 90, "furn")
# jukebox (NE corner) and a neon brand sign over the back bar (fictional brand)
bar.box((X1 - T - 0.95, Y1 - T - 0.65, fz), (X1 - T - 0.15, Y1 - T - 0.05, fz + 1.55), "bar")
bar.box((X1 - T - 0.9, Y1 - T - 0.67, fz + 1.0), (X1 - T - 0.2, Y1 - T - 0.64, fz + 1.4), "neon_blue")
g.text_mesh(b, "sign_neon_lager", "KETTLE RIVER LAGER", 0.13, (bx - 0.15, (yn(9.0) + yn(19.0)) / 2, fz + 2.2), math.pi / 2,
            "neon_red", extrude=0.01)
b.empty("light_bar", (bx + 1.2, yn(11), CEIL1 - 0.3))
b.empty("light_bar", (bx + 1.2, yn(17), CEIL1 - 0.3))
b.empty("light_bar", (X1 - 1.4, yn(4.5), CEIL1 - 0.3))

# ------------------------------------------------------------------ lounge (west): fish-fry dining
lo = b.part("lounge-col")
lx0 = X0 + T
for (tx, ty) in ((lx0 + 1.2, yn(6.5)), (lx0 + 3.0, yn(6.5)), (lx0 + 1.2, yn(19.5)), (lx0 + 3.0, yn(19.5)),
                 (lx0 + 2.9, yn(13.0))):
    fu.table(lo, (tx, ty, fz), 0, 1.1, 0.8, 0.76, "furn")
    for (ox, oy, yaw) in ((-0.35, -0.6, 180), (0.35, -0.6, 180), (-0.35, 0.6, 0), (0.35, 0.6, 0)):
        fu.chair(lo, (tx + ox, ty + oy, fz), yaw, "furn")
fu.dresser(lo, (HALL_W0 - 0.3, yn(10.5), fz), -90, 1.4, 0.5, 0.95, "furn", "brass", drawers=2)          # sideboard
# chalkboard fish-fry menu on the hall wall (Pruett use; Friday fish fry is a Midwest tavern staple)
mb = (HALL_W0 - 0.02, yn(13.0))
lo.box((mb[0] - 0.03, mb[1] - 0.75, fz + 1.35), (mb[0], mb[1] + 0.75, fz + 2.35), "chalk")
for i, line in enumerate(("FRIDAY FISH FRY", "Walleye  $14", "Lake Perch  $12", "Bluegill  $11",
                          "Coleslaw - Rye - Fries")):
    g.text_mesh(b, f"sign_menu_{i}", line, 0.1 if i else 0.13, (mb[0] - 0.035, mb[1], fz + 2.18 - i * 0.18), -math.pi / 2,
                "chalktext", extrude=0.002)
b.empty("light_lounge", (lx0 + 2.2, yn(7), CEIL1 - 0.3))
b.empty("light_lounge", (lx0 + 2.2, yn(19), CEIL1 - 0.3))
# hall: a wall-hung coat-hook rail on the west hall wall between the lounge doors (a floor-standing
# rack would block the narrow hall) + the brass hall light
hk = b.part("hooks")
hk.box((HALL_W1, -0.9, fz + 1.62), (HALL_W1 + 0.025, 0.7, fz + 1.74), "furn")
for k in range(7):
    y = -0.75 + k * 0.23
    hk.box((HALL_W1 + 0.025, y - 0.012, fz + 1.66), (HALL_W1 + 0.09, y + 0.012, fz + 1.69), "brass")
    hk.box((HALL_W1 + 0.07, y - 0.012, fz + 1.69), (HALL_W1 + 0.09, y + 0.012, fz + 1.73), "brass")
b.empty("light_hall", ((HALL_W1 + HALL_E0) / 2, yn(3), CEIL1 - 0.3))

# ------------------------------------------------------------------ second floor: hall, closets, two bedrooms
p2 = b.part("partitions2-col")
roof_under = lambda y: RIDGE - 0.16 / math.cos(math.radians(PITCH)) - abs(y) * math.tan(math.radians(PITCH))
top2 = lambda: (lambda uu, y0=Y1 - T: min(CEIL2, roof_under(y0 - uu)))
# bedroom doors at the stair head (2nd floor plan).  Both sit under the roof slope, so each is kept
# as close to the ridge as the plan allows: W just south of the ridge, E just south of the stair well
# (it can't open onto the well).  Heads stop below the rafters at the lower (south) jamb.
def bed_door(ys, ye, casing):
    head = min(FL2 + 2.0, roof_under(ys) - casing - 0.02)
    return head, ys, ye
BED = {"W": bed_door(-1.5, -0.7, 0.1), "E": bed_door(UP_Y1 - 0.05 - 0.72, UP_Y1 - 0.05, 0.06)}
for k, (hd, ys, ye) in BED.items():
    print(f"tavern bed_{k} door head above FL2:", round(hd - FL2, 3))
    assert hd - FL2 >= 1.8, "bedroom door too low for the player"
for (xw_, tag) in ((HALL_W0, "W"), (HALL_E0, "E")):
    hd, ys, ye = BED[tag]
    if tag == "W":
        # built south->north so the bedroom (west) is on the wall's left
        a, c = (xw_ + 0.12, Y0 + T), (xw_ + 0.12, Y1 - T)
        op = dict(off=ys - (Y0 + T), w=ye - ys, sill=FL2, head=hd)
        top = lambda uu: min(CEIL2, roof_under((Y0 + T) + uu))
    else:
        a, c = (xw_, Y1 - T), (xw_, Y0 + T)
        op = dict(off=(Y1 - T) - ye, w=ye - ys, sill=FL2, head=hd)
        top = lambda uu: min(CEIL2, roof_under((Y1 - T) - uu))
    f2 = g.wall_profile(p2, a, c, FL2, top, 0.12, [op], "plaster", "plaster")
    g.door(b, "doorframe", f2, op["off"], op["w"], op["head"], 0.12, f"bed_{tag}", swing_in=True, leaves=1, mat="door",
           threshold_z=FL2, casing=0.1 if tag == "W" else 0.06, panels=[(0.15, 0.55, 0.85, 0.92), (0.15, 0.08, 0.85, 0.45)])
# closets "C" at both ends of the upstairs hall (2nd floor plan)
for (yc0, yc1, tag) in ((Y1 - T - 1.25, Y1 - T, "N"), (Y0 + T, Y0 + T + 1.25, "S")):
    yf = yc0 if tag == "N" else yc1
    a, c = ((HALL_W1, yf), (HALL_E0, yf)) if tag == "N" else ((HALL_E0, yf), (HALL_W1, yf))
    L = HALL_E0 - HALL_W1
    # under-eave closets: low doors, the roof only leaves ~1.6 m of headroom out here
    chead = min(FL2 + 1.9, roof_under(yf) - 0.14)
    cfr2 = g.wall(p2, a, c, FL2, min(CEIL2, roof_under(yf)) - 0.02, 0.1, [dict(off=L - 0.85, w=0.7, sill=FL2, head=chead)],
                  "plaster", "plaster")
    g.door(b, "doorframe", cfr2, L - 0.85, 0.7, chead, 0.1, f"closet_{tag}", swing_in=False, leaves=1, mat="door",
           threshold_z=FL2, panels=[(0.15, 0.55, 0.85, 0.92), (0.15, 0.08, 0.85, 0.45)])
# sloped plaster ceilings (roof underside) + flat ceiling at 7'-6"
cl2 = b.part("ceiling2")
yflat = (RIDGE - 0.16 / math.cos(math.radians(PITCH)) - CEIL2) / math.tan(math.radians(PITCH))
cl2.box((X0 + T, -yflat, CEIL2), (X1 - T, yflat, CEIL2 + 0.02), "plaster", sides="z")
for s in (1, -1):
    ya, yb = s * yflat, s * (D / 2 - T)
    za, zb = CEIL2, roof_under(D / 2 - T)
    q = [(X0 + T, ya, za), (X1 - T, ya, za), (X1 - T, yb, zb), (X0 + T, yb, zb)]
    cl2.face(q if s < 0 else q[::-1], "plaster")
for (x0b, x1b, tag) in ((X0 + T, HALL_W0, "W"), (HALL_E1, X1 - T, "E")):
    bp = b.part(f"bedroom_{tag}-col")
    cx = (x0b + x1b) / 2
    fu.bed(bp, (cx, Y1 - T - 1.25, FL2), 0, 1.35, 1.95, "furn", "quilt")
    fu.dresser(bp, (cx + (0.9 if tag == "W" else -0.9), Y0 + T + 0.3, FL2), 180, 1.0, 0.5, 0.9, "furn", "brass",
               mirror_mat="mirror")
    fu.washstand(bp, (cx - (0.9 if tag == "W" else -0.9), Y0 + T + 0.3, FL2), 180, "furn", "china")
    fu.chair(bp, (cx + (1.2 if tag == "W" else -1.2), -0.3, FL2), 90 if tag == "W" else -90, "furn")
    b.empty("light_bedroom", (cx, 0.0, CEIL2 - 0.25))
b.empty("light_hall2", ((HALL_W1 + HALL_E0) / 2, yn(18), CEIL2 - 0.25))

# ------------------------------------------------------------------ frame kitchen wing (later addition) -- fish-fry kitchen
KW = ft(16, 0)                     # ASSUMED width (plan gives only its 22'-1 1/2" length); photo 1 shows a narrow wing
KL = ft(22, 1.5)
kx0, kx1, ky0, ky1 = X1, X1 + KW, Y0, Y0 + KL
K_EAVE = FL1 + 2.6
kw = b.part("wing-col")
kw.box((kx0, ky0, -0.2), (kx1, ky1, FL1 - 0.25), "found", sides="xXyY")
kops = {
    "S": [dict(off=0.7, w=0.9, sill=FL1, head=FL1 + 2.05), dict(off=2.6, w=0.9, sill=FL1 + 0.95, head=FL1 + 2.05)],
    "E": [dict(off=1.2, w=0.9, sill=FL1 + 0.95, head=FL1 + 2.05), dict(off=4.2, w=0.9, sill=FL1 + 0.95, head=FL1 + 2.05)],
    "N": [dict(off=1.9, w=0.9, sill=FL1 + 0.95, head=FL1 + 2.05)],
}
kfr = {
    "S": g.wall(kw, (kx0 + 0.02, ky0), (kx1, ky0), FL1 - 0.25, K_EAVE, 0.15, kops["S"], "siding", "plaster"),
    "E": g.wall(kw, (kx1, ky0), (kx1, ky1), FL1 - 0.25, K_EAVE, 0.15, kops["E"], "siding", "plaster"),
    "N": g.wall(kw, (kx1, ky1), (kx0 + 0.02, ky1), FL1 - 0.25, K_EAVE, 0.15, kops["N"], "siding", "plaster"),
}
for k, ops in kops.items():
    for op in ops:
        if op["sill"] > FL1 + 0.1:
            g.window(b, "windows", kfr[k], op["off"], op["w"], op["sill"], op["head"], 0.15, sash_rows=2, sash_cols=1,
                     glass_name="glass")
g.door(b, "doorframe", kfr["S"], 0.7, 0.9, FL1 + 2.05, 0.15, "kitchen_back", swing_in=False, leaves=1, mat="door",
       threshold_z=FL1, panels=[(0.12, 0.5, 0.88, 0.94), (0.12, 0.08, 0.88, 0.44)])
g.gable_infill(kw, (kx1, ky1), (kx0 + 0.02, ky1), K_EAVE, K_EAVE + KW / 2 * math.tan(math.radians(30)), 0.15, "siding", "plaster")
g.gable_infill(kw, (kx0 + 0.02, ky0), (kx1, ky0), K_EAVE, K_EAVE + KW / 2 * math.tan(math.radians(30)), 0.15, "siding", "plaster")
kr = b.part("wing_roof-col")
g.gable_roof(kr, kx0, kx1, ky0, ky1, K_EAVE, 30, 0.3, 0.25, 0.12, "roof", "ceiling", ridge_axis="y", fascia="trim")
kw.box((kx0 + 0.15, ky0 + 0.15, FL1 - 0.05), (kx1 - 0.15, ky1 - 0.15, FL1), "lino", sides="Z")
kw.box((kx0 + 0.15, ky0 + 0.15, K_EAVE - 0.1), (kx1 - 0.15, ky1 - 0.15, K_EAVE - 0.08), "ceiling", sides="z")
kit = b.part("kitchen-col")
fu.range_stove(kit, (kx1 - 0.55, ky0 + 2.6, FL1), -90, "enamel", "iron")
fu.fryer(kit, (kx1 - 0.55, ky0 + 3.5, FL1), -90, "steel", "oil")
fu.fryer(kit, (kx1 - 0.55, ky0 + 4.2, FL1), -90, "steel", "oil")
fu.sink_counter(kit, (kx0 + 2.2, ky1 - 0.45, FL1), 180, 2.2, "enamel", "steel", "steel")
fu.fridge(kit, (kx0 + 0.6, ky1 - 0.5, FL1), 180, "enamel", "steel")
fu.table(kit, (kx0 + 2.3, ky0 + 3.4, FL1), 90, 1.8, 0.8, 0.9, "steel")                    # prep table
fu.shelves(kit, (kx0 + 0.3, ky0 + 3.0, FL1), -90, 1.8, 0.45, 1.9, 5, "steel")
b.empty("light_kitchen", ((kx0 + kx1) / 2, ky0 + 2.0, K_EAVE - 0.3))
b.empty("light_kitchen", ((kx0 + kx1) / 2, ky0 + 5.0, K_EAVE - 0.3))
# back stoop
kst = b.part("stoop-col")
for k in range(3):
    z = FL1 - k * FL1 / 3
    kst.box((kx0 + 0.55, ky0 - 0.3 * (k + 1), 0), (kx0 + 1.75, ky0 - 0.3 * k, z), "found")

# ------------------------------------------------------------------ signs (Pruett names; relate to the building)
sg = b.part("signs-col")
# hanging board under the front porch beam, over the steps
hy = Y1 + PORCH - 0.25
hz = KNEE - PORCH * math.tan(math.radians(PITCH)) - 0.32
for x in (-0.95, 0.95):
    sg.box((x - 0.012, hy - 0.012, hz - 0.35), (x + 0.012, hy + 0.012, hz), "iron")
sg.box((-1.1, hy - 0.03, hz - 1.05), (1.1, hy + 0.03, hz - 0.35), "signboard")
sg.box((-1.15, hy - 0.04, hz - 1.1), (1.15, hy + 0.04, hz - 1.05), "gold")
sg.box((-1.15, hy - 0.04, hz - 0.35), (1.15, hy + 0.04, hz - 0.3), "gold")
for side, rot in ((1, math.pi), (-1, 0.0)):
    g.text_mesh(b, f"sign_tavern_name_{side}", "DEER CREEK TAVERN", 0.2, (0, hy + side * 0.035, hz - 0.62), rot, "gold")
    g.text_mesh(b, f"sign_tavern_est_{side}", "EST. 1851", 0.12, (0, hy + side * 0.035, hz - 0.88), rot, "gold")
# window neon/lettering (inside the glass, readable from the street)
wx = lambda west_ft: X0 + ft(west_ft) + WIN_W / 2
g.text_mesh(b, "sign_window_fishfry1", "FISH FRY", 0.14, (wx(3.208), Y1 - T * 0.65, WIN_SILL + 1.1), math.pi, "neon_red")
g.text_mesh(b, "sign_window_fishfry2", "FRIDAY", 0.14, (wx(3.208), Y1 - T * 0.65, WIN_SILL + 0.9), math.pi, "neon_red")
g.text_mesh(b, "sign_window_beer", "COLD BEER", 0.13, (wx(24.979), Y1 - T * 0.65, WIN_SILL + 1.0), math.pi, "neon_blue")
g.text_mesh(b, "sign_window_open", "OPEN", 0.18, (wx(31.583), Y1 - T * 0.65, WIN_SILL + 1.0), math.pi, "neon_red")
# hours card by the front door
g.text_mesh(b, "sign_hours", "OPEN 11 - 11  ·  CLOSED MON", 0.05,
            (X1 - ft(door_w_ft[1]) - 0.35, Y1 + 0.005, FL1 + 1.45), math.pi, "trim", font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
# porch bench
fu.bench(b.part("porch_bench-col"), (xw(6.5), Y1 + 0.45, FL1), 180, 1.8, "furn")
# split-rail fence along the west side lot line (research §2: rural lot furniture)
fe = b.part("fence-col")
fx = X0 - 4.0
for k in range(6):
    y = Y1 + 3.0 - k * 3.0
    fe.box((fx - 0.07, y - 0.07, 0), (fx + 0.07, y + 0.07, 1.3), "rail")
    if k < 5:
        for z in (0.45, 0.85, 1.2):
            fe.box((fx - 0.05, y - 3.0, z - 0.05), (fx + 0.05, y, z + 0.05), "rail")

b.finish(OUT)
