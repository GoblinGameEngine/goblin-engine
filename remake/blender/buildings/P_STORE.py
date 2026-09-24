"""
P-STORE -- Pruett Mercantile (groceries, dry goods, hardware, feed & seed; owner's flat above).

Real example: Thompson Store, 109 West Grant Highway, Marengo, McHenry County, Illinois --
HABS ILL-143 (remake/reference/P-STORE/).  1845 two-storey frame block with a temple-front
gable (cornice returns, corner pilasters), 1868 shop front (two canted bays + panelled door,
sheet 2 at 3/4"=1'), and a later one-storey frame addition to the west with a bracketed porch.
Dimensions: sheet 1 (1st/2nd floor plans, east + north elevations, restoration elevation,
cornice detail), sheet 2 (shop front and entrance).

Origin: centre of the 1845 block at grade.  +X east, +Y north.  FRONT = NORTH.
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
TEX = os.path.join(ROOT, "remake", "textures", "p-store")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-STORE.glb")

b = g.Building("P-STORE", TEX)
for k, t, tile in (("siding", "siding", 1.0), ("siding_w", "siding_wing", 1.0), ("roof", "roof", 1.0),
                   ("found", "foundation", 1.2), ("trim", "trim", 1.0), ("shop", "shopfront", 1.0),
                   ("floor", "floor", 2.0), ("porch", "porch", 2.0), ("plaster", "plaster", 2.0),
                   ("bead", "beadboard", 1.0), ("counter", "counter", 1.0), ("door", "door", 1.0),
                   ("furn", "furniture", 1.0), ("chimney", "chimney", 1.0), ("lino", "lino", 0.9144),
                   ("iron", "iron", 0.5), ("ceiling", "ceiling", 2.0)):
    b.mat(k, tex=t, tile_m=tile)
b.mat("glass", color=(0.72, 0.8, 0.84), rough=0.05, alpha=0.2)
b.mat("brass", color=(0.75, 0.58, 0.26), rough=0.3, metal=1.0)
b.mat("threshold", color=(0.45, 0.43, 0.4), rough=0.9)
b.mat("gold", color=(0.85, 0.7, 0.3), rough=0.35, metal=0.8)
b.mat("signboard", color=(0.14, 0.24, 0.18), rough=0.6)
b.mat("sign_white", color=(0.95, 0.94, 0.9), rough=0.6)
b.mat("red", color=(0.62, 0.12, 0.1), rough=0.55)
b.mat("burlap", color=(0.62, 0.52, 0.36), rough=0.95)
b.mat("paper", color=(0.95, 0.93, 0.85), rough=0.8)
b.mat("linen", color=(0.9, 0.88, 0.82), rough=0.9)
b.mat("quilt", color=(0.22, 0.32, 0.5), rough=0.9)
b.mat("upholstery", color=(0.45, 0.3, 0.22), rough=0.9)
b.mat("china", color=(0.95, 0.95, 0.93), rough=0.2)
b.mat("steel", color=(0.62, 0.64, 0.66), rough=0.4, metal=0.9)
b.mat("nails", color=(0.4, 0.4, 0.42), rough=0.6, metal=0.7)
b.mat("globe", color=(0.95, 0.9, 0.7), emission=(1.0, 0.85, 0.5))
b.mat("pump", color=(0.7, 0.1, 0.08), rough=0.4)
b.mat("hose", color=(0.08, 0.08, 0.08), rough=0.7)
for i, c in enumerate(((0.75, 0.2, 0.15), (0.2, 0.35, 0.6), (0.85, 0.7, 0.2), (0.3, 0.55, 0.3), (0.9, 0.88, 0.8),
                       (0.55, 0.35, 0.2), (0.7, 0.72, 0.74))):
    b.mat(f"goods{i}", color=c, rough=0.6)
GOODS = [f"goods{i}" for i in range(7)]

# ------------------------------------------------------------------ dimensions
W = ft(20, 4.5)               # shop-front width (sheet 2: 8'-2 1/4" + 4'-0" + 8'-2 1/4")
D = ft(29, 9)                 # 1st floor plan
X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
T = 0.15                      # frame walls
ST_N, ST_RUN = 14, 0.19       # stair UP 14R along the east wall, SE corner
ST_LAND = 0.9                 # top landing (3 ft) between the last riser and the rear wall
ST_FOOT = T + ST_LAND + ST_N * ST_RUN     # stair foot, measured from the rear (south) face
FL1 = ft(1, 10)               # sheet 2: floor 1'-10" above grade
CEIL1 = FL1 + ft(8, 2)        # north elevation
FL2 = CEIL1 + ft(1, 0)
CEIL2 = FL2 + ft(7, 1)
EAVE = FL1 + ft(2, 2) + ft(5, 8.625) + ft(2, 7.25) + ft(5, 8.625) + ft(1, 10.75)   # east elevation string
RIDGE = EAVE + ft(5, 5.5)
PITCH = math.degrees(math.atan((RIDGE - EAVE) / (W / 2)))
WW, WH = ft(2, 11.5), ft(5, 8.625)
S1 = FL1 + ft(2, 2)           # 1st floor window sill
S2 = S1 + WH + ft(2, 7.25)    # 2nd floor window sill

shell = b.part("shell-col")
shell.box((X0 - 0.03, Y0 - 0.03, -0.25), (X1 + 0.03, Y1 + 0.03, FL1 - 0.05), "found", sides="xXyY")

# -- walls.  N = shop front (built separately below the cornice, clapboard above)
bay_w = ft(8, 2.25)
door_w = ft(4, 0)
SHOP_TOP = FL1 + ft(8, 8)                       # sheet 2: cornice top over the shop front
walls = {
    "S": ((X0, Y0), (X1, Y0), [dict(off=ft(2, 8.5), w=WW, sill=S1, head=S1 + WH),
                               dict(off=ft(2, 8.5) + WW + 0.1, w=ft(3, 1), sill=FL1, head=FL1 + 2.05),
                               dict(off=W - ft(4, 0) - WW, w=WW, sill=S2, head=S2 + WH)]),
    "E": ((X1, Y0), (X1, Y1), [dict(off=ft(4, 0), w=WW, sill=S1, head=S1 + WH),
                               dict(off=ST_FOOT + 0.12, w=ft(3, 1), sill=FL1, head=FL1 + 2.05),     # side door just past the stair foot
                               dict(off=D - ft(6, 3) - WW, w=WW, sill=S1, head=S1 + WH),
                               dict(off=ft(3, 6), w=WW, sill=S2, head=S2 + WH),
                               dict(off=D / 2 - WW / 2, w=WW, sill=S2, head=S2 + WH),
                               dict(off=D - ft(3, 6) - WW, w=WW, sill=S2, head=S2 + WH)]),
    "W": ((X0, Y1), (X0, Y0), [dict(off=ft(8, 6), w=ft(3, 1), sill=FL1, head=FL1 + 2.05),             # to the addition
                               dict(off=ft(5, 0), w=WW, sill=S2, head=S2 + WH),
                               dict(off=D - ft(5, 0) - WW, w=WW, sill=S2, head=S2 + WH)]),
}
fr = {}
for k in ("E", "W"):
    a, c, ops = walls[k]
    fr[k] = g.wall(shell, a, c, FL1 - 0.05, EAVE, T, ops, "siding", "plaster")
fr["S"] = g.wall_profile(shell, (X0, Y0), (X1, Y0), FL1 - 0.05, g.gable_top(W, EAVE, RIDGE - 0.1), T,
                         walls["S"][2] + [dict(off=W / 2 - 0.3, w=0.6, sill=EAVE + 0.4, head=EAVE + 0.9)], "siding", "plaster")
# north gable face above the shop front: 2 upper windows (restoration elevation), clapboard
nops = [dict(off=ft(3, 3), w=WW, sill=S2, head=S2 + WH), dict(off=W - ft(3, 3) - WW, w=WW, sill=S2, head=S2 + WH)]
fr["N"] = g.wall_profile(shell, (X1, Y1), (X0, Y1), SHOP_TOP, g.gable_top(W, EAVE, RIDGE - 0.1), T, nops, "siding", "plaster")
for k in ("S", "E", "W", "N"):
    ops = (walls[k][2] if k != "N" else nops)
    for op in ops:
        if op["sill"] > FL1 + 0.1 and op["head"] < RIDGE - 0.5 and op["w"] > 0.7:
            g.window(b, "windows", fr[k], op["off"], op["w"], op["sill"], op["head"], T, sash_rows=2, sash_cols=3,
                     glass_name="glass")
            # flat head casings with a small cornice cap (restoration elevation)
            b.part("trim").obox(fr[k], (op["off"] - 0.12, -0.05, op["head"] + 0.1), (op["off"] + op["w"] + 0.12, 0.0,
                                op["head"] + 0.16), "trim")
# attic louvre in the south gable
b.part("trim").obox(fr["S"], (W / 2 - 0.3, 0.02, EAVE + 0.4), (W / 2 + 0.3, 0.05, EAVE + 0.9), "shop")

# corner pilasters + frieze + pedimented gable with cornice returns (restoration elevation, cornice detail)
tr = b.part("trim")
for (cx, cy) in ((X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)):
    sx, sy = (1 if cx > 0 else -1), (1 if cy > 0 else -1)
    tr.box((cx - (0.2 if sx > 0 else 0.03), cy - (0.2 if sy > 0 else 0.03), FL1 - 0.05),
           (cx + (0.03 if sx > 0 else 0.2), cy + (0.03 if sy > 0 else 0.2), EAVE), "trim")
for (xa, xb) in ((X0 - 0.05, X0), (X1, X1 + 0.05)):
    tr.box((xa, Y0 - 0.05, EAVE - ft(1, 10.75)), (xb, Y1 + 0.05, EAVE), "trim")                      # frieze
    tr.box((xa - 0.15 if xa < 0 else xa, Y0 - 0.2, EAVE - 0.05), (xb if xa < 0 else xb + 0.15, Y1 + 0.2, EAVE + 0.1), "trim")
for (y_face, s) in ((Y1, 1), (Y0, -1)):
    # horizontal raking-cornice base (the "pediment" floor) + returns
    tr.box((X0 - 0.15, min(y_face, y_face + s * 0.25), EAVE - 0.05), (X1 + 0.15, max(y_face, y_face + s * 0.25), EAVE + 0.05), "trim")

roof = b.part("roof-col")
g.gable_roof(roof, X0, X1, Y0, Y1, EAVE, PITCH, overhang_eave=0.3, overhang_rake=0.28, thick=0.14, mat_top="roof",
             mat_under="trim", ridge_axis="y", fascia="trim")
roof.box((-0.09, Y0 - 0.28, RIDGE + 0.02), (0.09, Y1 + 0.28, RIDGE + 0.1), "roof")
# rear chimney (1st floor plan: flue on the rear wall, restoration elevation)
chx = -0.6
roof.box((chx - 0.25, Y0 + T, CEIL1), (chx + 0.25, Y0 + T + 0.45, RIDGE + 1.0), "chimney")

# ------------------------------------------------------------------ 1868 shop front (sheet 2)
sf = b.part("shopfront-col")
BASE = ft(2, 5.75)                      # panelled base
GLASS_T = BASE + ft(5, 7) + 0.1         # top of the glazing
CANT = ft(1, 4)                         # bay projection (plan / section thru window)
for side in (-1, 1):
    # bay from wall x=xa to xb (xa at the corner, xb toward the door)
    if side < 0:
        xa, xb = X0, X0 + bay_w
    else:
        xa, xb = X1 - bay_w, X1
    xin_a, xin_b = xa + CANT, xb - CANT             # front plane corners
    yf = Y1 + CANT
    corners = [(xa, Y1), (xin_a, yf), (xin_b, yf), (xb, Y1)]
    for (p0, p1) in zip(corners, corners[1:]):
        o = Vector((p0[0], p0[1], 0))
        u = (Vector((p1[0], p1[1], 0)) - o)
        L = u.length
        u.normalize()
        w_in = Vector((-u.y, u.x, 0))
        F = (o, u, w_in, Vector((0, 0, 1)))
        sf.obox(F, (0, 0, FL1), (L, 0.1, FL1 + BASE), "shop")                               # panelled base
        sf.obox(F, (0.12, -0.02, FL1 + 0.15), (L - 0.12, 0.0, FL1 + BASE - 0.12), "shop")    # raised panel
        sf.obox(F, (0, 0, FL1 + BASE), (L, 0.12, FL1 + BASE + 0.06), "trim")                 # sill
        for xm in (0.0, L - 0.05):
            sf.obox(F, (xm, 0.02, FL1 + BASE), (xm + 0.05, 0.1, GLASS_T), "shop")           # mullions
        cols = 4 if L > 1.2 else 1
        for c in range(1, cols):
            xm = L * c / cols
            sf.obox(F, (xm - 0.015, 0.04, FL1 + BASE), (xm + 0.015, 0.08, GLASS_T), "shop")
        for r in (1, 2):
            zm = FL1 + BASE + (GLASS_T - FL1 - BASE) * r / 3
            sf.obox(F, (0, 0.04, zm - 0.015), (L, 0.08, zm + 0.015), "shop")
        sf.obox(F, (0, 0, GLASS_T), (L, 0.12, GLASS_T + 0.08), "shop")
        gl = b.part("glass")
        P = lambda a, d, z: tuple(o + u * a + w_in * d + Vector((0, 0, z)))
        gl.face([P(0, 0.06, FL1 + BASE), P(L, 0.06, FL1 + BASE), P(L, 0.06, GLASS_T), P(0, 0.06, GLASS_T)], "glass")
        gl.face([P(L, 0.06, FL1 + BASE), P(0, 0.06, FL1 + BASE), P(0, 0.06, GLASS_T), P(L, 0.06, GLASS_T)], "glass")
    # bay roof (shed) + floor plate + transom band up to the cornice
    sf.prism([(xa, Y1), (xin_a, yf), (xin_b, yf), (xb, Y1)], GLASS_T + 0.08, SHOP_TOP - 0.3, "shop")
    sf.prism([(xa, Y1), (xin_a, yf), (xin_b, yf), (xb, Y1)], FL1 - 0.05, FL1, "floor")
# entrance: fluted pilasters + panelled door (sheet 2: 3'-1" x 6'-9 1/4")
dx0 = X0 + bay_w
nf = g.wall(sf, (X0 + bay_w + door_w, Y1), (X0 + bay_w, Y1), FL1, SHOP_TOP - 0.3, T,
            [dict(off=(door_w - ft(3, 1)) / 2, w=ft(3, 1), sill=FL1, head=FL1 + ft(6, 9.25))], "shop", "plaster")
g.door(b, "doorframe", nf, (door_w - ft(3, 1)) / 2, ft(3, 1), FL1 + ft(6, 9.25), T, "shop", swing_in=True, leaves=1,
       mat="door", threshold_z=FL1, panels=[(0.14, 0.86, 0.44, 0.94), (0.56, 0.86, 0.86, 0.94), (0.14, 0.5, 0.44, 0.82),
                                             (0.56, 0.5, 0.86, 0.82), (0.14, 0.38, 0.86, 0.46), (0.14, 0.06, 0.44, 0.33),
                                             (0.56, 0.06, 0.86, 0.33)])
for px in (dx0 + 0.05, dx0 + door_w - 0.25):
    for k in range(4):
        sf.box((px + k * 0.05, Y1 - 0.05, FL1), (px + k * 0.05 + 0.035, Y1 + 0.02, FL1 + ft(7, 6)), "shop")   # flutes
sf.box((X0 - 0.05, Y1 - 0.02, SHOP_TOP - 0.3), (X1 + 0.05, Y1 + CANT + 0.12, SHOP_TOP), "shop")          # cornice
sf.box((X0 - 0.1, Y1 - 0.02, SHOP_TOP), (X1 + 0.1, Y1 + CANT + 0.2, SHOP_TOP + 0.08), "trim")
# stoop: 4'-0" step (sheet 2) + front platform (1st floor plan)
sf.box((X0, Y1, FL1 - 0.25), (X1, Y1 + ft(5, 6), FL1 - 0.05), "porch")
sf.box((dx0, Y1 + ft(5, 6), 0), (dx0 + door_w, Y1 + ft(5, 6) + 0.3, (FL1 - 0.05) / 2), "porch")

# ------------------------------------------------------------------ floors, stair (UP 14R, SE corner)
ST_W = ft(3, 7)
st_x0 = X1 - T - ST_W
st_y_top = Y0 + T + ST_LAND
st_y_bot = st_y_top + ST_N * ST_RUN
fl = b.part("floors-col")
fl.box((X0 + T, Y0 + T, FL1 - 0.05), (X1 - T, Y1 - T, FL1), "floor", sides="Z")
g.floor_with_holes(fl, X0 + T, X1 - T, Y0 + T, Y1 - T, FL2, 0.3, [(st_x0, X1 - T, st_y_top, st_y_bot)], "floor", "ceiling")
fl.box((X0 + T, Y0 + T, CEIL2), (X1 - T, Y1 - T, CEIL2 + 0.02), "ceiling", sides="z")
g.stairs(b, "stair", (st_x0, st_y_bot, FL1), (0, -1), ST_W, FL2 - FL1, ST_N, ST_RUN, "floor", "trim")
# partition enclosing the stair (1st floor: stair runs along the east wall, rail on its open side)
sr = b.part("stair_rail-col")
rh_ = (FL2 - FL1) / ST_N
rail_z = lambda y: FL1 + rh_ + 0.9 + (st_y_bot - y) * (FL2 - FL1 - rh_) / (ST_N * ST_RUN)
for k in range(ST_N):                         # balusters under one raking handrail
    y = st_y_bot - (k + 0.5) * ST_RUN
    z = FL1 + (k + 1) * rh_
    sr.box((st_x0 - 0.02, y - 0.015, z), (st_x0 + 0.02, y + 0.015, rail_z(y) - 0.02), "counter")
g.raking_rail(sr, (st_x0, st_y_bot, rail_z(st_y_bot)), (st_x0, st_y_top, rail_z(st_y_top)), "counter", w=0.07, h=0.06)
sr.box((st_x0 - 0.05, st_y_bot - 0.05, FL1), (st_x0 + 0.06, st_y_bot + 0.05, FL1 + 1.1), "counter")
# upstairs rail around the well
g.spindle_rail(sr, [(st_x0, st_y_bot), (st_x0, st_y_top)], FL2, 0.9, 0.12, "counter")      # open onto the top landing

# ------------------------------------------------------------------ store room fit-out (1st floor, one open room)
sp = b.part("store_fittings-col")
# wainscot of beadboard all round (period store interiors)
for k in ("E", "W", "S"):
    a, c, ops = walls[k]
    o, u, w_in, L = g.wall_frame(a, c)
    Fw = (o, u, w_in, Vector((0, 0, 1)))
    cur = T
    for op in sorted([op for op in ops if op["sill"] < FL1 + 1.0], key=lambda d: d["off"]):
        if op["off"] - cur > 0.05:
            sp.obox(Fw, (cur, T, FL1), (op["off"] - 0.08, T + 0.012, FL1 + 0.95), "bead")
        cur = op["off"] + op["w"] + 0.08
    sp.obox(Fw, (cur, T, FL1), (L - T, T + 0.012, FL1 + 0.95), "bead")
# west wall: stocked shelving floor to ceiling, glass display counter in front of it
fu.stocked_shelves(sp, (X0 + T + 0.2, Y1 - 3.0, FL1), -90, 4.2, 0.4, 2.4, 6, "counter", GOODS, seed=11)
fu.display_case(sp, (X0 + T + 1.3, Y1 - 3.3, FL1), -90, 3.6, "counter", "glass")
fu.cash_register(sp, (X0 + T + 1.3, Y1 - 4.6, FL1 + 0.95), -90, "brass", "paper")
# east wall: shelving north of the side door, a plain counter + platform scale
fu.stocked_shelves(sp, (X1 - T - 0.2, Y1 - 1.9, FL1), 90, 2.6, 0.4, 2.4, 6, "counter", GOODS, seed=12)
fu.table(sp, (X1 - T - 1.3, Y1 - 1.9, FL1), 90, 2.2, 0.6, 0.92, "counter")
fu.platform_scale(sp, (X1 - T - 0.5, Y1 - 3.9, FL1), 90, "counter", "steel")
# centre: two display tables, cracker barrel, pickle barrel, pot-bellied stove toward the back
fu.table(sp, (0.3, Y1 - 2.2, FL1), 0, 1.6, 0.9, 0.8, "counter")
fu.table(sp, (0.3, Y1 - 4.1, FL1), 0, 1.6, 0.9, 0.8, "counter")
for (tx, ty) in ((0.3, Y1 - 2.2), (0.3, Y1 - 4.1)):
    for k in range(8):
        sp.box((tx - 0.7 + (k % 4) * 0.36, ty - 0.35 + (k // 4) * 0.4, FL1 + 0.8), (tx - 0.46 + (k % 4) * 0.36,
               ty - 0.08 + (k // 4) * 0.4, FL1 + 0.8 + 0.08 + (k % 3) * 0.05), GOODS[k % 7])
fu.barrel(sp, (-0.9, Y1 - 5.6, FL1), "furn", "iron", lid_mat="furn")
fu.barrel(sp, (-0.3, Y1 - 5.9, FL1), "furn", "iron", lid_mat="furn")
fu.potbelly_stove(sp, (chx, Y0 + T + 1.1, FL1), "iron")
sp.box((chx - 0.07, Y0 + T + 0.2, FL1 + 2.25), (chx + 0.07, Y0 + T + 1.15, FL1 + 2.39), "iron")      # pipe to flue
for k in range(3):
    fu.chair(sp, (chx - 0.9 + k * 0.9, Y0 + T + 2.0, FL1), 180, "furn")                             # the stove circle
b.empty("light_store", (0.0, Y1 - 2.5, CEIL1 - 0.3))
b.empty("light_store", (0.0, Y1 - 5.5, CEIL1 - 0.3))
b.empty("light_store", (0.0, Y0 + 1.5, CEIL1 - 0.3))
# board ceiling, open over the stair well (headroom for the flight)
g.floor_with_holes(fl, X0 + T, X1 - T, Y0 + T, Y1 - T, CEIL1 + 0.02, 0.02, [(st_x0, X1 - T, st_y_top, st_y_bot)], "ceiling", "ceiling")
# pressed-tin ceiling would be later; the 1845 store kept a plain board ceiling
# doors: side door (east), rear door (south), door to the addition (west)
g.door(b, "doorframe", fr["E"], walls["E"][2][1]["off"], ft(3, 1), FL1 + 2.05, T, "side", swing_in=False, leaves=1,
       mat="door", threshold_z=FL1, panels=[(0.14, 0.5, 0.86, 0.93), (0.14, 0.07, 0.86, 0.44)])
g.door(b, "doorframe", fr["S"], walls["S"][2][1]["off"], ft(3, 1), FL1 + 2.05, T, "rear", swing_in=True, leaves=1,
       mat="door", threshold_z=FL1, panels=[(0.14, 0.5, 0.86, 0.93), (0.14, 0.07, 0.86, 0.44)])
g.door(b, "doorframe", fr["W"], walls["W"][2][0]["off"], ft(3, 1), FL1 + 2.05, T, "to_feedroom", swing_in=False,
       leaves=1, mat="door", threshold_z=FL1, panels=[(0.14, 0.5, 0.86, 0.93), (0.14, 0.07, 0.86, 0.44)])
# exterior steps at the side and rear doors
st = b.part("steps-col")
sd = walls["E"][2][1]
st.box((X1, Y0 + sd["off"] - 0.1, 0), (X1 + 0.6, Y0 + sd["off"] + sd["w"] + 0.1, FL1 - 0.05), "found")
rd = walls["S"][2][1]
st.box((X0 + rd["off"] - 0.1, Y0 - 0.6, 0), (X0 + rd["off"] + rd["w"] + 0.1, Y0, FL1 - 0.05), "found")

# ------------------------------------------------------------------ 2nd floor flat (2nd floor plan)
p2 = b.part("flat-col")
yp = Y0 + T + ft(14, 7)                  # partition between the rear rooms and the front room
pf = g.wall(p2, (X0 + T, yp), (X1 - T, yp), FL2, CEIL2, 0.1,
            [dict(off=ft(11, 2) + 0.35, w=0.8, sill=FL2, head=FL2 + 2.0)], "plaster", "plaster")
g.door(b, "doorframe", pf, ft(11, 2) + 0.35, 0.8, FL2 + 2.0, 0.1, "flat_front", swing_in=False, leaves=1, mat="door",
       threshold_z=FL2, panels=[(0.15, 0.55, 0.85, 0.92), (0.15, 0.08, 0.85, 0.45)])
xb_ = X0 + T + ft(11, 2)                 # bedroom / stair-hall partition
bfp = g.wall(p2, (xb_, Y0 + T), (xb_, yp), FL2, CEIL2, 0.1, [dict(off=ft(8, 0), w=0.8, sill=FL2, head=FL2 + 2.0)],
             "plaster", "plaster")
g.door(b, "doorframe", bfp, ft(8, 0), 0.8, FL2 + 2.0, 0.1, "flat_bedroom", swing_in=False, leaves=1, mat="door",
       threshold_z=FL2, panels=[(0.15, 0.55, 0.85, 0.92), (0.15, 0.08, 0.85, 0.45)])
fu.bed(p2, (X0 + T + 1.3, Y0 + T + 1.1, FL2), 0, 1.35, 1.95, "furn", "quilt")
fu.dresser(p2, (X0 + T + 0.3, yp - 0.9, FL2), -90, 1.0, 0.5, 0.9, "furn", "brass", mirror_mat="glass")
fu.sofa(p2, (0.0, Y1 - T - 0.55, FL2), 180, 1.9, "upholstery", "furn")
fu.armchair(p2, (X1 - T - 0.8, Y1 - 2.4, FL2), 90, "upholstery", "furn")
fu.radio(p2, (X0 + T + 0.3, Y1 - 2.0, FL2), -90, "furn", "burlap")
fu.table(p2, (0.3, Y1 - 2.6, FL2), 0, 1.2, 0.8, 0.76, "furn")
for (ox, yaw) in ((-0.8, -90), (1.4, 90)):
    fu.chair(p2, (0.3 + ox, Y1 - 2.6, FL2), yaw, "furn")
b.empty("light_flat", (0.0, Y1 - 2.5, CEIL2 - 0.2))
b.empty("light_flat", (X0 + 1.6, Y0 + 1.8, CEIL2 - 0.2))

# ------------------------------------------------------------------ later addition (west): feed & seed / hardware
AW = ft(28, 0)
ay0, ay1 = Y0 + ft(1, 4), Y1 - ft(4, 11)
ax0, ax1 = X0 - AW, X0
A_EAVE = FL1 + 2.95
a_pitch = 28.0
ad = b.part("addition-col")
ad.box((ax0, ay0, -0.2), (ax1, ay1, FL1 - 0.05), "found", sides="xyY")
PX = g.FT / 21.5                          # plan px -> m (1st floor plan, 1/8" scale crop)
axp = lambda px: X0 - (px - 1090) * PX      # plan x px -> +X (west is +px on this plan)
aops = {
    "N": [dict(off=None, px=(1195, 1235), sill=S1, head=S1 + WH), dict(off=None, px=(1360, 1410), sill=FL1, head=FL1 + 2.05),
          dict(off=None, px=(1520, 1560), sill=S1, head=S1 + WH)],
    "S": [dict(off=None, px=(1195, 1235), sill=S1, head=S1 + WH), dict(off=None, px=(1340, 1400), sill=S1, head=S1 + WH),
          dict(off=None, px=(1465, 1525), sill=FL1, head=FL1 + 2.05)],
    "W": [dict(off=0.0, w=WW, sill=S1, head=S1 + WH)],
}
# north wall runs east->west from (ax1, ay1) to (ax0, ay1): offset = distance west of the block wall
nops_a = [dict(off=(X0 - axp(o["px"][0])), w=(o["px"][1] - o["px"][0]) * PX, sill=o["sill"], head=o["head"]) for o in aops["N"]]
sops_a = [dict(off=(axp(o["px"][1]) - ax0), w=(o["px"][1] - o["px"][0]) * PX, sill=o["sill"], head=o["head"]) for o in aops["S"]]
wops_a = [dict(off=(ay1 - ay0) / 2 - WW / 2, w=WW, sill=S1, head=S1 + WH)]
afr = {
    "N": g.wall(ad, (ax1, ay1), (ax0, ay1), FL1 - 0.05, A_EAVE, T, nops_a, "siding_w", "plaster"),
    "S": g.wall(ad, (ax0, ay0), (ax1, ay0), FL1 - 0.05, A_EAVE, T, sops_a, "siding_w", "plaster"),
    "W": g.wall_profile(ad, (ax0, ay1), (ax0, ay0), FL1 - 0.05, g.gable_top(ay1 - ay0, A_EAVE,
                        A_EAVE + (ay1 - ay0) / 2 * math.tan(math.radians(a_pitch)) - 0.08), T, wops_a, "siding_w", "plaster"),
}
for k, ops in (("N", nops_a), ("S", sops_a), ("W", wops_a)):
    for op in ops:
        if op["sill"] > FL1 + 0.1:
            g.window(b, "windows", afr[k], op["off"], op["w"], op["sill"], op["head"], T, sash_rows=2, sash_cols=2,
                     glass_name="glass")
g.door(b, "doorframe", afr["N"], nops_a[1]["off"], nops_a[1]["w"], FL1 + 2.05, T, "feed_front", swing_in=True, leaves=1,
       mat="door", threshold_z=FL1, panels=[(0.14, 0.5, 0.86, 0.93), (0.14, 0.07, 0.86, 0.44)])
g.door(b, "doorframe", afr["S"], sops_a[2]["off"], sops_a[2]["w"], FL1 + 2.05, T, "feed_rear", swing_in=False, leaves=1,
       mat="door", threshold_z=FL1, panels=[(0.14, 0.07, 0.86, 0.93)])
ar = b.part("addition_roof-col")
g.gable_roof_x(ar, ax0, ax1, ay0, ay1, A_EAVE, a_pitch, overhang_eave=0.3, overhang_rake=0.25, thick=0.12,
               mat_top="roof", mat_under="trim", fascia="trim")
ad.box((ax0 + T, ay0 + T, FL1 - 0.05), (ax1 - 0.01, ay1 - T, FL1), "floor", sides="Z")
ad.box((ax0 + T, ay0 + T, A_EAVE - 0.12), (ax1 - 0.01, ay1 - T, A_EAVE - 0.1), "ceiling", sides="z")
# partitions (plan): rear row A (office) | B (stock room) | C (washroom); front row D (feed & seed) | E (hardware)
yr = ay0 + (440 - 265) * PX
xAB, xBC, xDE = axp(1290), axp(1570), axp(1430)
pa = b.part("addition_partitions-col")
# D -> B door kept inside D (east of the D/E partition) and inside B (west of the A/B partition)
off_stock = (ax1 - 0.01) - (xDE + 0.9)
assert xDE + 0.9 < xAB - 0.1 and xDE + 0.1 > xBC + 0.1, "stockroom door must open from D into B"
fr_r = g.wall(pa, (ax1 - 0.01, yr), (ax0 + T, yr), FL1, A_EAVE - 0.1, 0.1,
              [dict(off=X0 - axp(1275), w=0.8, sill=FL1, head=FL1 + 2.0),                  # D -> A office
               dict(off=off_stock, w=0.8, sill=FL1, head=FL1 + 2.0)], "plaster", "plaster")   # D -> B stock
g.door(b, "doorframe", fr_r, X0 - axp(1275), 0.8, FL1 + 2.0, 0.1, "office", swing_in=False, leaves=1, mat="door",
       threshold_z=FL1)
g.door(b, "doorframe", fr_r, off_stock, 0.8, FL1 + 2.0, 0.1, "stockroom", swing_in=True, leaves=1, mat="door",
       threshold_z=FL1)
g.wall(pa, (xAB, ay0 + T), (xAB, yr), FL1, A_EAVE - 0.1, 0.1, [], "plaster", "plaster")
bc = g.wall(pa, (xBC, yr), (xBC, ay0 + T), FL1, A_EAVE - 0.1, 0.1, [dict(off=0.4, w=0.75, sill=FL1, head=FL1 + 2.0)],
            "plaster", "plaster")
g.door(b, "doorframe", bc, 0.4, 0.75, FL1 + 2.0, 0.1, "washroom", swing_in=True, leaves=1, mat="door", threshold_z=FL1)
de = g.wall(pa, (xDE, yr), (xDE, ay1 - T), FL1, A_EAVE - 0.1, 0.1, [dict(off=(ay1 - T - yr) - 1.3, w=0.9, sill=FL1,
            head=FL1 + 2.0)], "plaster", "plaster")
g.door(b, "doorframe", de, (ay1 - T - yr) - 1.3, 0.9, FL1 + 2.0, 0.1, "hardware_room", swing_in=True, leaves=1,
       mat="door", threshold_z=FL1)
af = b.part("addition_fittings-col")
fu.sack_stack(af, ((ax1 + xDE) / 2, (yr + ay1) / 2 - 0.6, FL1), 0, 3, 2, 5, "burlap")       # feed & seed
fu.sack_stack(af, ((ax1 + xDE) / 2 + 0.8, ay1 - T - 0.6, FL1), 0, 2, 2, 3, "burlap")
fu.platform_scale(af, (xDE + 0.6, yr + 0.6, FL1), 180, "counter", "steel")
fu.bin_row(af, ((xDE + ax0) / 2, yr + 0.45, FL1), 180, 5, "counter", ["nails", "steel", "iron", "nails", "steel"])
fu.stocked_shelves(af, (ax0 + T + 0.2, (yr + ay1) / 2 + 0.5, FL1), -90, 2.2, 0.4, 2.2, 5, "counter", GOODS, seed=13)
fu.stocked_shelves(af, ((xDE + ax0) / 2, ay1 - T - 0.2, FL1), 180, 2.6, 0.4, 2.2, 5, "counter", GOODS, seed=14)
fu.desk(af, ((ax1 + xAB) / 2, ay0 + T + 0.5, FL1), 180, "furn", "brass")
fu.chair(af, ((ax1 + xAB) / 2, ay0 + T + 1.2, FL1), 180, "furn")
fu.safe(af, (ax1 - 0.45, yr - 0.5, FL1), 90, "iron", "brass")
fu.stocked_shelves(af, ((xAB + xBC) / 2, ay0 + T + 0.2, FL1), 0, 3.4, 0.45, 2.2, 5, "counter", GOODS, seed=15)
fu.toilet(af, ((xBC + ax0) / 2, ay0 + T + 0.3, FL1), 0, "china", "furn")
fu.sink_counter(af, ((xBC + ax0) / 2, yr - 0.4, FL1), 180, 0.7, "china", "china", "steel")
for (lx, ly) in (((ax1 + xDE) / 2, (yr + ay1) / 2), ((xDE + ax0) / 2, (yr + ay1) / 2), ((ax1 + xAB) / 2, (ay0 + yr) / 2),
                 ((xAB + xBC) / 2, (ay0 + yr) / 2)):
    b.empty("light_addition", (lx, ly, A_EAVE - 0.4))
# bracketed porch along the addition front (north elevation / plan)
po = b.part("porch-col")
py1 = ay1 + ft(4, 5)
po.box((ax0, ay1, FL1 - 0.2), (ax1, py1, FL1 - 0.05), "porch", mats={"z": "porch"})
pz = A_EAVE - 0.35
for px in (1092, 1285, 1480, 1665):
    x = axp(px)
    po.box((x - 0.07, py1 - 0.2, FL1 - 0.05), (x + 0.07, py1 - 0.06, pz), "trim")
    po.box((x - 0.2, py1 - 0.2, pz - 0.35), (x + 0.2, py1 - 0.06, pz - 0.3), "trim")          # scroll brackets (flat)
po.box((ax0, py1 - 0.22, pz), (ax1, py1 - 0.04, pz + 0.18), "trim")
pr = [(ax0 - 0.1, ay1, A_EAVE - 0.05), (ax1, ay1, A_EAVE - 0.05), (ax1, py1 + 0.2, pz + 0.12), (ax0 - 0.1, py1 + 0.2, pz + 0.12)]
b.part("porch_roof-col").face(pr[::-1], "roof")
b.part("porch_roof-col").face(pr, "trim")
for k in range(2):
    po.box((axp(1350), py1 + k * 0.28, 0), (axp(1420), py1 + (k + 1) * 0.28, FL1 - 0.05 - k * (FL1 / 2)), "porch")

# ------------------------------------------------------------------ signs + site pieces
sg = b.part("signs-col")
# main sign board on the cornice frieze (between shop cornice and the upper windows)
sg.box((X0 + 0.4, Y1 + 0.02, SHOP_TOP + 0.12), (X1 - 0.4, Y1 + 0.06, SHOP_TOP + 0.62), "signboard")
g.text_mesh(b, "sign_mercantile", "PRUETT MERCANTILE", 0.3, (0, Y1 + 0.065, SHOP_TOP + 0.37), math.pi, "gold",
            extrude=0.01)
g.text_mesh(b, "sign_window_left1", "GROCERIES", 0.16, (X0 + bay_w / 2, Y1 + CANT - 0.02, FL1 + BASE + 1.3), math.pi,
            "gold", extrude=0.002)
g.text_mesh(b, "sign_window_left2", "DRY GOODS", 0.12, (X0 + bay_w / 2, Y1 + CANT - 0.02, FL1 + BASE + 1.05), math.pi,
            "gold", extrude=0.002)
g.text_mesh(b, "sign_window_right1", "HARDWARE", 0.16, (X1 - bay_w / 2, Y1 + CANT - 0.02, FL1 + BASE + 1.3), math.pi,
            "gold", extrude=0.002)
g.text_mesh(b, "sign_window_right2", "NOTIONS", 0.12, (X1 - bay_w / 2, Y1 + CANT - 0.02, FL1 + BASE + 1.05), math.pi,
            "gold", extrude=0.002)
g.text_mesh(b, "sign_hours", "OPEN  Mon-Sat  7 to 6", 0.045, (dx0 + door_w / 2 + 0.95, Y1 + 0.005, FL1 + 1.5), math.pi,
            "sign_white", extrude=0.002, font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
# FEED & SEED board on the addition porch fascia
sg.box((axp(1150), py1 - 0.03, pz + 0.18), (axp(1600), py1 + 0.01, pz + 0.55), "sign_white")
g.text_mesh(b, "sign_feed", "FEED & SEED", 0.24, ((axp(1150) + axp(1600)) / 2, py1 + 0.015, pz + 0.365), math.pi, "red",
            extrude=0.008)
g.text_mesh(b, "sign_est", "EST. 1868", 0.09, (0, Y1 + 0.065, SHOP_TOP + 0.72), math.pi, "gold", extrude=0.004)
# inside: counter card + price board
g.text_mesh(b, "sign_counter", "PAY HERE", 0.07, (X0 + T + 1.0, Y1 - 4.6, FL1 + 1.35), -math.pi / 2, "red",
            extrude=0.003)
# period gas pump at the curb (fictional brand) + a porch bench and hitching rail
fu.gas_pump(b.part("gas_pump-col"), (X1 + 1.2, Y1 + 3.2, 0), 180, "pump", "globe", "steel", "hose")
g.text_mesh(b, "sign_gas_globe", "PRAIRIE", 0.07, (X1 + 1.2, Y1 + 3.2 + 0.21, 2.12), math.pi, "red", extrude=0.003,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
g.text_mesh(b, "sign_gas_globe_b", "PRAIRIE", 0.07, (X1 + 1.2, Y1 + 3.2 - 0.21, 2.12), 0.0, "red", extrude=0.003,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
fu.bench(b.part("porch_bench-col"), ((axp(1150) + axp(1300)) / 2, ay1 + 0.4, FL1 - 0.05), 180, 1.6, "furn")
hr = b.part("hitching_rail-col")
for x in (X0 + 0.5, X0 + 2.6):
    hr.box((x - 0.06, Y1 + 5.2, 0), (x + 0.06, Y1 + 5.32, 1.0), "furn")
hr.box((X0 + 0.44, Y1 + 5.2, 0.9), (X0 + 2.66, Y1 + 5.32, 1.0), "furn")

b.finish(OUT)
