"""
P-CHURCH -- St. Olaf Evangelical Lutheran Church, Pruett.

Real example: First Evangelical (Norwegian) Lutheran Church, Sheldahl, Iowa -- HABS IA-62
(remake/reference/P-CHURCH/).  Every dimension below is read off the HABS measured drawings
(sheet 1: floor plan + south elevation, sheet 2: west/east elevations, sheet 3: pulpit, pew,
spindle details) unless marked ASSUMED; interior finishes follow the three HABS interior photos.

Plan coordinates: origin = centre of the footprint at grade, +X east, +Y north (front = south).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from mathutils import Vector  # noqa: E402

import gblib as g  # noqa: E402
from gblib import ft  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-church")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-CHURCH.glb")

b = g.Building("P-CHURCH", TEX)
b.mat("siding", tex="siding", tile_m=1.0)
b.mat("roof", tex="roof", tile_m=1.0)
b.mat("found", tex="foundation", tile_m=1.2)
b.mat("chimney", tex="chimney", tile_m=1.0)
b.mat("floor", tex="floor", tile_m=2.0)
b.mat("plaster", tex="wall", tile_m=2.0)
b.mat("wainscot", tex="wainscot", tile_m=1.0)
b.mat("trim", tex="trim", tile_m=1.0)
b.mat("pew", tex="pew", tile_m=1.0)
b.mat("door", tex="door", tile_m=1.0)
b.mat("iron", tex="iron", tile_m=0.5, metal=0.6)
b.mat("ceiling", tex="ceiling", tile_m=2.0)
b.mat("glass", color=(0.75, 0.82, 0.85), rough=0.05, alpha=0.18)
b.mat("brass", color=(0.72, 0.56, 0.25), rough=0.3, metal=1.0)
b.mat("bronze", color=(0.55, 0.40, 0.22), rough=0.35, metal=1.0)
b.mat("threshold", color=(0.42, 0.40, 0.37), rough=0.9)
b.mat("signboard", color=(0.93, 0.92, 0.88), rough=0.6)
b.mat("letters", color=(0.08, 0.10, 0.20), rough=0.5)
b.mat("sign_black", color=(0.05, 0.05, 0.05), rough=0.6)
b.mat("organ", tex="door", tile_m=0.6)
b.mat("carpet", color=(0.42, 0.13, 0.12), rough=0.95)
b.mat("paper", color=(0.95, 0.93, 0.85), rough=0.8)

# --- dimensions (drawings) -------------------------------------------------
W = ft(28, 5)                 # east-west, sheet 1 plan
D = ft(30, 7.25)              # north-south, sheet 1 plan
X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
T = 0.15                      # frame wall incl. siding + plaster  ASSUMED (2x4 + lath)
FLOOR = ft(0, 10)             # finished floor above grade (door sill, sheet 1 south elev.)
DATUM = ft(1, 11)             # datum line above grade (sheet 2)
EAVE = DATUM + ft(12, 11)     # eave above grade (scaled off sheet 1, 25'-0" ridge dim. as scale)
RIDGE = DATUM + ft(25, 0)     # ridge above datum (sheet 1 dimension)
PITCH = math.degrees(math.atan((RIDGE - EAVE) / (W / 2)))
CEIL = FLOOR + ft(12, 8)      # flat board ceiling  ASSUMED from interior photo 4 (door = 8.1')
WIN_SILL = DATUM + ft(1, 10.75)   # sheet 2
WIN_H = ft(7, 6)                  # sheet 2
WIN_W = ft(2, 9)                  # sheet 1
DOOR_W, DOOR_HEAD = ft(4, 0), FLOOR + ft(7, 10)

shell = b.part("shell-col")
# fieldstone foundation (visible band grade -> floor), slightly proud of the siding
shell.box((X0 - 0.03, Y0 - 0.03, -g.FOUND_DEPTH), (X1 + 0.03, Y1 + 0.03, FLOOR), "found", sides="xXyY")

# --- walls: counter-clockwise so the interior is always on the left --------
west_w = [ft(5, 8), ft(5, 8) + WIN_W + ft(5, 6), ft(5, 8) + 2 * WIN_W + ft(5, 6) + ft(5, 6.375)]   # from N corner
east_w = [ft(5, 7.5), ft(5, 7.5) + ft(2, 9.125) + ft(5, 6.75),
          ft(5, 7.5) + 2 * ft(2, 9.125) + ft(5, 6.75) + ft(5, 5.75)]                                # from S corner
door_off = ft(12, 2.25)

walls = {
    "S": ((X0, Y0), (X1, Y0), [dict(off=door_off, w=DOOR_W, sill=FLOOR, head=DOOR_HEAD)]),
    "E": ((X1, Y0), (X1, Y1), [dict(off=o, w=WIN_W, sill=WIN_SILL, head=WIN_SILL + WIN_H) for o in east_w]),
    "N": ((X1, Y1), (X0, Y1), []),
    "W": ((X0, Y1), (X0, Y0), [dict(off=o, w=WIN_W, sill=WIN_SILL, head=WIN_SILL + WIN_H) for o in west_w]),
}
frames = {}
for k, (a, c, ops) in walls.items():
    frames[k] = g.wall(shell, a, c, FLOOR, EAVE, T, ops, "siding", "plaster")
# corner boards + frieze board (white trim, sheet 1/2 elevations)
for (cx, cy) in ((X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)):
    sx, sy = (1 if cx > 0 else -1), (1 if cy > 0 else -1)
    shell.box((min(cx, cx + sx * 0.03) - (0.12 if sx < 0 else 0), min(cy, cy + sy * 0.03) - (0.12 if sy < 0 else 0), FLOOR),
              (max(cx, cx + sx * 0.03) + (0.12 if sx > 0 else 0), max(cy, cy + sy * 0.03) + (0.12 if sy > 0 else 0), EAVE), "trim")
for (a, c) in (((X0, Y0), (X1, Y0)), ((X1, Y1), (X0, Y1))):
    pass
shell.box((X0 - 0.03, Y0 - 0.03, EAVE - 0.22), (X0, Y1 + 0.03, EAVE), "trim")
shell.box((X1, Y0 - 0.03, EAVE - 0.22), (X1 + 0.03, Y1 + 0.03, EAVE), "trim")

# gable ends (N and S) above the eave, sided outside, plaster inside the (unseen) attic
g.gable_infill(shell, (X0, Y0), (X1, Y0), EAVE, RIDGE - 0.05, T, "siding", "plaster")
g.gable_infill(shell, (X1, Y1), (X0, Y1), EAVE, RIDGE - 0.05, T, "siding", "plaster")

# --- roof: gable, ridge N-S, cedar shingles (sheet 1/2) ----------------------
roof = b.part("roof-col")
g.gable_roof(roof, X0, X1, Y0, Y1, EAVE, PITCH, overhang_eave=0.25, overhang_rake=0.12, thick=0.12,
             mat_top="roof", mat_under="trim", ridge_axis="y", fascia="trim")
# ridge cap
roof.box((-0.09, Y0 - 0.12, RIDGE + 0.02), (0.09, Y1 + 0.12, RIDGE + 0.1), "roof")

# --- windows (6x 4/4 double-hung, sheet 2) + double front door (sheet 1) ----
for k in ("E", "W"):
    for i, op in enumerate(walls[k][2]):
        g.window(b, f"windows", frames[k], op["off"], op["w"], op["sill"], op["head"], T, sash_rows=2, sash_cols=2,
                 glass_name="glass")
g.door(b, "doorframe", frames["S"], door_off, DOOR_W, DOOR_HEAD, T, "front", swing_in=True, leaves=2,
       panels=[(0.18, 0.38, 0.82, 0.93), (0.18, 0.06, 0.82, 0.3)], mat="door", threshold_z=FLOOR)
# door head cornice (sheet 1)
dx0 = X0 + door_off - 0.18
shell.box((dx0, Y0 - 0.1, DOOR_HEAD + 0.1), (dx0 + DOOR_W + 0.36, Y0, DOOR_HEAD + 0.2), "trim")
# stone step (sheet 1 elev.: one stone below the sill)
shell.box((X0 + door_off - 0.35, Y0 - 0.65, -g.FOUND_DEPTH), (X0 + door_off + DOOR_W + 0.35, Y0, FLOOR - 0.02), "found")

# --- belfry (sheet 1: 7'-11" above ridge; sheet 2: 3'-8" in from the S gable) -----
bel = b.part("belfry-col")
bc_y = Y0 + ft(3, 8)
half = ft(2, 2)
post_top = RIDGE + ft(4, 2)
for sx in (-1, 1):
    for sy in (-1, 1):
        cx, cy = sx * (half - 0.07), bc_y + sy * (half - 0.07)
        zb = EAVE + (W / 2 - abs(cx)) * math.tan(math.radians(PITCH)) - 0.05
        bel.box((cx - 0.07, cy - 0.07, zb), (cx + 0.07, cy + 0.07, post_top), "trim")
bel.box((-half, bc_y - half, post_top - 0.12), (half, bc_y + half, post_top), "trim")
g.pyramid_roof(bel, 0.0, bc_y, half, post_top, RIDGE + ft(7, 11), 0.12, "roof", "trim")
# bell on a yoke (sheet 1 shows the open belfry; bell ASSUMED 24" dia.)
bell = b.part("bell")
bell.box((-half + 0.07, bc_y - 0.05, post_top - 0.3), (half - 0.07, bc_y + 0.05, post_top - 0.2), "door")
bell.cylinder((0, bc_y), 0.13, post_top - 0.72, post_top - 0.3, "bronze", n=18, r1=0.08)
bell.cylinder((0, bc_y), 0.31, post_top - 0.8, post_top - 0.72, "bronze", n=18, r1=0.13)

# --- chimney at the north end (sheet 1 "chimney above", sheet 2) -----------------
ch = b.part("chimney-col")
cy_ = Y1 - 0.55
ch.box((-0.24, cy_ - 0.24, CEIL), (0.24, cy_ + 0.24, RIDGE + 0.9), "chimney")
ch.box((-0.28, cy_ - 0.28, RIDGE + 0.9), (0.28, cy_ + 0.28, RIDGE + 1.0), "chimney")

# --- interior: floor, ceiling, wainscot --------------------------------------
fl = b.part("floor-col")
fl.box((X0 + T, Y0 + T, FLOOR - 0.05), (X1 - T, Y1 - T, FLOOR), "floor", sides="Z")
fl.box((X0 + T, Y0 + T, CEIL), (X1 - T, Y1 - T, CEIL + 0.05), "ceiling", sides="z")
# carpet runner up the centre aisle (photo 4)
fl.box((-0.55, Y0 + T + 0.3, FLOOR), (0.55, Y1 - 3.6, FLOOR + 0.006), "carpet", sides="Z")
WS = FLOOR + ft(3, 0)   # wainscot height -- photos 2-4 (ASSUMED 3'-0" to cap)
ws = b.part("wainscot")
for k, (a, c, ops) in walls.items():
    o, u, w_in, length = g.wall_frame(a, c)
    F = (o, u, w_in, Vector((0, 0, 1)))
    x = T
    spans = []
    cur = T
    for op in sorted(ops, key=lambda d: d["off"]):
        if op["sill"] < WS:
            spans.append((cur, op["off"] - 0.08))
            cur = op["off"] + op["w"] + 0.08
    spans.append((cur, length - T))
    for (s0, s1) in spans:
        if s1 - s0 > 0.02:
            ws.obox(F, (s0, T, FLOOR), (s1, T + 0.012, WS), "wainscot")
            ws.obox(F, (s0, T, WS), (s1, T + 0.035, WS + 0.04), "pew")       # cap rail
            ws.obox(F, (s0, T, FLOOR), (s1, T + 0.02, FLOOR + 0.14), "pew")  # baseboard

# --- chancel: raised semicircular platform + spindle rail (sheet 3) ---------------
PX = 1.0 / 31.1 * g.FT        # plan pixels -> metres (plan scale: 28'-5" = 885 px on sheet 1 crop)
def plan(px, py):
    return ((px - 842.5) * PX, -(py - 816.5) * PX)

ch_c = plan(845, 520)
R_ch = 4.8 * g.FT
CH_Z = FLOOR + 0.2
chan = b.part("chancel-col")
pts = [(ch_c[0] + R_ch * math.cos(math.pi + math.pi * k / 24), ch_c[1] + R_ch * math.sin(math.pi + math.pi * k / 24))
       for k in range(25)]
outline = [(ch_c[0] - R_ch, Y1 - T)] + pts + [(ch_c[0] + R_ch, Y1 - T)]
chan.prism(outline, FLOOR, CH_Z, "floor")
rail = b.part("chancel_rail-col")
gap = 0.45      # opening at the front for communion (sheet 3 shows a gap in the rail at centre front)
left = [p for p in pts if p[0] < ch_c[0] - gap]
right = [p for p in pts if p[0] > ch_c[0] + gap]
g.spindle_rail(rail, [(ch_c[0] - R_ch, ch_c[1] + 0.9)] + left, CH_Z, 0.72, 0.16, "pew")
g.spindle_rail(rail, right + [(ch_c[0] + R_ch, ch_c[1] + 0.9)], CH_Z, 0.72, 0.16, "pew")
# kneeling step outside the rail
for side_pts in (left, right):
    for a_, c_ in zip(side_pts, side_pts[1:]):
        m = ((a_[0] + c_[0]) / 2, (a_[1] + c_[1]) / 2)
        dirv = Vector((m[0] - ch_c[0], m[1] - ch_c[1], 0)).normalized() * 0.2
        rail.box((min(a_[0], c_[0]) + dirv.x - 0.08, min(a_[1], c_[1]) + dirv.y - 0.08, FLOOR),
                 (max(a_[0], c_[0]) + dirv.x + 0.08, max(a_[1], c_[1]) + dirv.y + 0.08, FLOOR + 0.12), "carpet")

# pulpit: panelled box on a dais against the north wall, steps both sides (sheet 3 plan/elev.)
pul = b.part("pulpit-col")
DAIS = FLOOR + 1.05
pul.box((-0.95, Y1 - T - 1.25, CH_Z), (0.95, Y1 - T, DAIS), "pew")
pul.box((-0.72, Y1 - T - 1.25 - 0.62, CH_Z), (0.72, Y1 - T - 1.25, DAIS + 1.12), "pew")      # pulpit body
pul.box((-0.78, Y1 - T - 1.25 - 0.75, DAIS + 1.08), (0.78, Y1 - T - 1.25 + 0.05, DAIS + 1.16), "pew")  # bookboard
for i, (x0p, x1p) in enumerate(((-0.66, -0.36), (-0.3, -0.02), (0.02, 0.3), (0.36, 0.66))):
    yf = Y1 - T - 1.25 - 0.62
    pul.box((x0p, yf - 0.012, CH_Z + 0.15), (x1p, yf, CH_Z + 0.95), "door")
    pul.box((x0p, yf - 0.012, CH_Z + 1.05), (x1p, yf, DAIS + 0.95), "door")
for sx in (-1, 1):
    # 4 risers climbing inward (toward the dais) from the chancel floor, one flight each side
    y_start = Y1 - T - 0.2 if sx > 0 else Y1 - T - 1.1
    g.stairs(b, f"pulpit_steps_{'W' if sx < 0 else 'E'}", (sx * (0.95 + 4 * 0.24), y_start, CH_Z),
             (-sx, 0), 0.9, DAIS - CH_Z, 4, 0.24, "pew")
# hymn board on the north wall
hb = (ch_c[0] + 1.9, Y1 - T - 0.03)
pul.box((hb[0] - 0.3, hb[1] - 0.04, FLOOR + 1.6), (hb[0] + 0.3, hb[1], FLOOR + 2.4), "pew")
for i, num in enumerate(("212", "45", "397")):
    g.text_mesh(b, f"sign_hymn_{i}", num, 0.16, (hb[0], hb[1] - 0.045, FLOOR + 2.22 - i * 0.24), math.pi, "paper",
                extrude=0.002)

# organ platform, NW corner, with the reed organ + stool from photo 2
op0, op1 = plan(415, 360), plan(625, 595)
org = b.part("organ-col")
org.box((op0[0], op1[1], FLOOR), (op1[0], Y1 - T, FLOOR + 0.2), "floor")
ox, oy = (op0[0] + op1[0]) / 2, Y1 - T - 0.35
org.box((ox - 0.62, oy - 0.3, FLOOR + 0.2), (ox + 0.62, oy + 0.3, FLOOR + 1.02), "organ")
org.box((ox - 0.62, oy - 0.02, FLOOR + 1.02), (ox + 0.62, oy + 0.3, FLOOR + 1.9), "organ")
org.box((ox - 0.55, oy - 0.45, FLOOR + 0.95), (ox + 0.55, oy - 0.3, FLOOR + 0.99), "paper")   # keyboard
org.cylinder((ox, oy - 0.85), 0.18, FLOOR + 0.2, FLOOR + 0.62, "organ", n=12)

# --- pews: two banks facing north + 3 side pews in the NE corner (sheet 1), profile sheet 3 --------
pews = b.part("pews-col")
SEAT, BACK, DEPTH = 0.43, ft(0, 29.25) + 0.17, 0.42


def pew(xa, xb, y_back, facing=(0, 1)):
    """A pew between xa..xb (plan), back edge at y_back, occupant faces +Y (north)."""
    f = Vector((facing[0], facing[1], 0))
    s = Vector((f.y, -f.x, 0))
    o = Vector(((xa + xb) / 2, y_back, FLOOR)) if facing[1] else Vector((y_back, (xa + xb) / 2, FLOOR))
    L = abs(xb - xa)
    F = (o, s, f, Vector((0, 0, 1)))
    pews.obox(F, (-L / 2, 0.0, SEAT - 0.04), (L / 2, DEPTH, SEAT), "pew")            # seat
    pews.obox(F, (-L / 2, 0.0, SEAT), (L / 2, 0.035, BACK), "pew")                   # back
    for e in (-L / 2, L / 2 - 0.035):                                               # ends
        pews.obox(F, (e, 0.0, 0), (e + 0.035, DEPTH + 0.03, BACK - 0.05), "pew")
    pews.obox(F, (-L / 2, 0.035, 0.05), (L / 2, 0.06, SEAT - 0.06), "pew")          # rear apron


west_rows = [(695, 665), (768, 730), (848, 730), (928, 640), (1003, 640), (1083, 730), (1162, 730), (1238, 730)]
east_rows = [768, 848, 928, 1003, 1083, 1162, 1238]
for py, pend in west_rows:
    xa, _ = plan(418, 0)
    xb, _ = plan(pend, 0)
    _, yb = plan(0, py + 35)
    pew(xa, xb, yb)
for py in east_rows:
    xa, _ = plan(955, 0)
    xb, _ = plan(1265, 0)
    _, yb = plan(0, py + 35)
    pew(xa, xb, yb)
for px in (1088, 1158, 1225):          # NE side pews, running N-S, facing west toward the pulpit
    x_back, _ = plan(px + 32, 0)
    _, ya = plan(0, 735)
    _, yb_ = plan(0, 362)
    pew(ya, yb_, x_back, facing=(-1, 0))

# --- stove + stovepipe to the chimney (sheet 1 "STOVE", photo 4) -------------------
st = b.part("stove-col")
sc = plan(785, 965)
st.cylinder(sc, 0.28, FLOOR + 0.12, FLOOR + 1.1, "iron", n=16)
st.cylinder(sc, 0.33, FLOOR + 0.35, FLOOR + 0.5, "iron", n=16)
st.cylinder(sc, 0.2, FLOOR + 1.1, FLOOR + 1.3, "iron", n=16, r1=0.08)
for a in range(4):
    ang = math.pi / 4 + a * math.pi / 2
    st.box((sc[0] + 0.22 * math.cos(ang) - 0.03, sc[1] + 0.22 * math.sin(ang) - 0.03, FLOOR),
           (sc[0] + 0.22 * math.cos(ang) + 0.03, sc[1] + 0.22 * math.sin(ang) + 0.03, FLOOR + 0.14), "iron")
pipe_z = CEIL - 0.45
st.cylinder(sc, 0.075, FLOOR + 1.3, pipe_z, "iron", n=10)
pipe = b.part("stovepipe")
pipe.box((sc[0] - 0.075, sc[1] - 0.075, pipe_z - 0.075), (sc[0] + 0.075, cy_ - 0.24, pipe_z + 0.075), "iron")
pipe.box((sc[0] - 0.075, cy_ - 0.3, pipe_z - 0.075), (0.075, cy_ - 0.24, pipe_z + 0.075), "iron")

# --- lights: 4 pendant fixtures on the ceiling (photo 2 shows a pendant cord) -------------
for (lx, ly) in ((-2.2, -2.5), (2.2, -2.5), (-2.2, 1.6), (2.2, 1.6)):
    lp = b.part("pendants")
    lp.box((lx - 0.006, ly - 0.006, CEIL - 0.6), (lx + 0.006, ly + 0.006, CEIL), "sign_black")
    lp.cylinder((lx, ly), 0.16, CEIL - 0.7, CEIL - 0.6, "paper", n=12, r1=0.04)
    b.empty("light_pendant", (lx, ly, CEIL - 0.72))

# --- coat pegs + a framed notice by the door (photo 4) -----------------------------------
cp = b.part("coatpegs")
cp.box((X0 + T, Y0 + T + 0.6, FLOOR + 1.7), (X0 + T + 0.03, Y0 + T + 2.2, FLOOR + 1.8), "pew")
for k in range(6):
    yy = Y0 + T + 0.7 + k * 0.27
    cp.box((X0 + T + 0.03, yy - 0.012, FLOOR + 1.73), (X0 + T + 0.12, yy + 0.012, FLOOR + 1.76), "brass")

# --- exterior: notice board sign on posts, cornerstone, hitching post ---------------------
sg = b.part("sign_board-col")
sx0, sy0 = -3.6, Y0 - 3.2
for px in (sx0 - 0.75, sx0 + 0.75):
    sg.box((px - 0.05, sy0 - 0.05, -0.4), (px + 0.05, sy0 + 0.05, 1.75), "trim")
sg.box((sx0 - 0.85, sy0 - 0.04, 0.85), (sx0 + 0.85, sy0 + 0.04, 1.75), "signboard")
sg.box((sx0 - 0.9, sy0 - 0.09, 1.75), (sx0 + 0.9, sy0 + 0.09, 1.82), "trim")
lines = [("ST. OLAF", 0.2, 1.54), ("EV. LUTHERAN CHURCH", 0.1, 1.36), ("Est. 1874", 0.08, 1.2),
         ("Worship Sunday 9:30 A.M.", 0.075, 1.05), ("All Are Welcome", 0.075, 0.93)]
for i, (txt, size, z) in enumerate(lines):
    g.text_mesh(b, f"sign_notice_{i}", txt, size, (sx0, sy0 - 0.045, z), 0.0, "letters")
    g.text_mesh(b, f"sign_notice_back_{i}", txt, size, (sx0, sy0 + 0.045, z), math.pi, "letters")
g.text_mesh(b, "sign_cornerstone", "1874", 0.14, (X0 + 0.45, Y0 - 0.035, 0.12), 0.0, "sign_black")
hp = b.part("hitching_post-col")
hp.cylinder((X1 + 1.6, Y0 - 1.8), 0.06, 0.0, 1.05, "iron", n=10)
hp.cylinder((X1 + 1.6, Y0 - 1.8), 0.09, 1.05, 1.12, "iron", n=10)

b.finish(OUT)
