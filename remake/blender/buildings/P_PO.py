"""
P-PO -- U.S. Post Office, Pruett.

Real example (primary): Harvel, Illinois post office (Commons photo, CC BY-SA 4.0) --
1960s one-storey brick box, low-pitch front-gabled roof, a second gabled canopy with white
vinyl soffit over the lettering + entrance, aluminium 2x2 storefront window, glass door with
transom, glass-block side window, blue collection box at the curb.  Secondary: Elliott, IL
post office (same era: gable front, rear side windows, flag pole).  No drawings exist, so
dimensions are scaled from the Harvel photo (door = 3'-0" leaf, brick courses 2 2/3") and the
interior follows research/building_catalog/commercial_civic_farm/post_office.md (lobby with PO
boxes + service window, workroom, postmaster's office, restroom, rear loading door).

Origin: centre of footprint at grade.  +X east, +Y north.  FRONT = NORTH.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from mathutils import Vector  # noqa: E402

import gbfurn as fu  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-po")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-PO.glb")

b = g.Building("P-PO", TEX)
for k, t, tile in (("brick", "brick", 1.0), ("vinyl", "vinyl", 1.0), ("roof", "roof", 1.0), ("ceiling", "ceiling", 1.2192),
                   ("vct_l", "vct_lobby", 1.2192), ("vct_w", "vct_work", 1.2192), ("concrete", "concrete", 2.0),
                   ("drywall", "drywall", 2.0), ("alu", "aluminum", 1.0), ("trim", "trim", 1.0), ("counter", "counter", 1.0),
                   ("steel_door", "steel_door", 1.0)):
    b.mat(k, tex=t, tile_m=tile)
b.mat("glass", color=(0.6, 0.68, 0.72), rough=0.05, alpha=0.25)
b.mat("glassblock", color=(0.75, 0.82, 0.85), rough=0.2, alpha=0.6)
b.mat("brass", color=(0.78, 0.62, 0.3), rough=0.3, metal=1.0)
b.mat("threshold", color=(0.6, 0.6, 0.6), rough=0.5, metal=0.8)
b.mat("door", color=(0.72, 0.74, 0.76), rough=0.3, metal=0.9)        # aluminium storefront door frame
b.mat("letters", color=(0.93, 0.93, 0.9), rough=0.4, metal=0.3)
b.mat("usps_blue", color=(0.05, 0.16, 0.42), rough=0.45)
b.mat("red", color=(0.72, 0.1, 0.12), rough=0.5)
b.mat("white", color=(0.95, 0.95, 0.95), rough=0.5)
b.mat("navy", color=(0.1, 0.13, 0.35), rough=0.5)
b.mat("pole", color=(0.85, 0.85, 0.85), rough=0.3, metal=0.9)
b.mat("canvas", color=(0.72, 0.66, 0.52), rough=0.95)
b.mat("steel", color=(0.55, 0.57, 0.6), rough=0.4, metal=0.9)
b.mat("paper", color=(0.95, 0.93, 0.85), rough=0.8)
b.mat("cork", color=(0.66, 0.5, 0.33), rough=0.95)
b.mat("china", color=(0.95, 0.95, 0.93), rough=0.2)
b.mat("mulch", color=(0.3, 0.2, 0.13), rough=1.0)
b.mat("sign_black", color=(0.05, 0.05, 0.05), rough=0.6)

MPX = 7.3 / 570.0                     # Harvel photo: facade 570 px = 24'-0"
W, D = 7.3, 12.2                      # depth ASSUMED from the side-wall foreshortening (~40')
X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
T = 0.3                               # brick veneer on block
FL = 0.15                             # slab on grade
EAVE = FL + 2.9
PITCH = 18.4                          # 4/12
CEIL = FL + 2.6

shell = b.part("shell-col")
shell.box((X0 - 0.01, Y0 - 0.01, -g.FOUND_DEPTH), (X1 + 0.01, Y1 + 0.01, FL), "concrete", sides="xXyY")
wx = lambda px: X0 + (px - 190) * MPX          # Harvel photo x (px) -> +X
front_ops = [dict(off=X1 - wx(380), w=(380 - 215) * MPX, sill=FL + 0.42, head=FL + 2.55),        # storefront window
             dict(off=T + 0.15, w=0.95, sill=FL, head=FL + 2.55)]                         # door + transom
walls = {
    "N": ((X1, Y1), (X0, Y1), front_ops),
    "E": ((X1, Y0), (X1, Y1), [dict(off=D - 1.6 - 0.45, w=0.45, sill=FL + 1.1, head=FL + 2.1),      # glass block
                               dict(off=2.2, w=0.9, sill=FL + 1.0, head=FL + 2.2)]),
    "S": ((X0, Y0), (X1, Y0), [dict(off=1.0, w=0.92, sill=FL, head=FL + 2.1),                        # loading door
                               dict(off=W - 1.6, w=0.7, sill=FL + 1.5, head=FL + 2.2)]),
    "W": ((X0, Y1), (X0, Y0), [dict(off=5.0, w=0.9, sill=FL + 1.0, head=FL + 2.2),
                               dict(off=8.3, w=0.9, sill=FL + 1.0, head=FL + 2.2)]),
}
fr = {}
for k in ("E", "W"):
    fr[k] = g.wall(shell, *walls[k][:2], FL, EAVE, T, walls[k][2], "brick", "drywall")
for k in ("N", "S"):
    fr[k] = g.wall(shell, *walls[k][:2], FL, EAVE, T, walls[k][2], "brick", "drywall")
    g.gable_infill(shell, walls[k][0], walls[k][1], EAVE, EAVE + W / 2 * math.tan(math.radians(PITCH)) - 0.08, T,
                   "vinyl", "drywall")
roof = b.part("roof-col")
RIDGE = g.gable_roof(roof, X0, X1, Y0, Y1, EAVE, PITCH, overhang_eave=0.35, overhang_rake=0.25, thick=0.2,
                     mat_top="roof", mat_under="vinyl", ridge_axis="y", fascia="alu")
roof.box((-0.1, Y0 - 0.25, RIDGE + 0.02), (0.1, Y1 + 0.25, RIDGE + 0.07), "roof")
roof.cylinder((1.2, -2.0), 0.05, RIDGE - 1.2 * math.tan(math.radians(PITCH)), RIDGE + 0.2, "alu", n=8)      # vent stack

# second gabled canopy over lettering + entrance (Harvel photo)
cx0, cx1 = wx(330), X1
can = b.part("canopy-col")
# the canopy's ridge runs N-S like the main roof; its vinyl gable face looks north
c_eave = EAVE - 0.25
c_ridge = c_eave + (cx1 - cx0) / 2 * math.tan(math.radians(26))
ymid = Y1 + 1.0
xm = (cx0 + cx1) / 2
for side in (-1, 1):
    xe = (cx0 if side < 0 else cx1) + side * 0.12
    q = [(xe, Y1 - 0.05, c_eave - 0.05), (xm, Y1 - 0.05, c_ridge), (xm, ymid + 0.12, c_ridge), (xe, ymid + 0.12, c_eave - 0.05)]
    can.face(q if side < 0 else q[::-1], "roof")
    under = [(p_[0], p_[1], p_[2] - 0.12) for p_ in q]
    can.face(under[::-1] if side < 0 else under, "vinyl")
can.face([(cx0, ymid, c_eave), (cx1, ymid, c_eave), ((cx0 + cx1) / 2, ymid, c_ridge - 0.05)], "vinyl")          # gable face
can.face([(cx1, ymid - 0.02, c_eave), (cx0, ymid - 0.02, c_eave), ((cx0 + cx1) / 2, ymid - 0.02, c_ridge - 0.05)], "vinyl")
can.box((cx0, Y1, c_eave - 0.12), (cx1, ymid + 0.02, c_eave), "vinyl")                                    # flat soffit + fascia
can.box((cx0 - 0.03, ymid, c_eave - 0.2), (cx1 + 0.03, ymid + 0.04, c_eave), "alu")
b.empty("light_canopy", (wx(715), Y1 + 0.5, c_eave - 0.2))

# storefront window: aluminium 2x2, and the glazed entrance door with transom
g.window(b, "windows", fr["N"], front_ops[0]["off"], front_ops[0]["w"], front_ops[0]["sill"], front_ops[0]["head"], T,
         sash_rows=1, sash_cols=2, mats={"trim": "alu"}, casing=0.04, glass_name="glass")
op = front_ops[1]
g.door(b, "doorframe", fr["N"], op["off"], op["w"], FL + 2.13, T, "lobby", swing_in=False, leaves=1, mat="door",
       threshold_z=FL, casing=0.05, trim="alu", panels=[], glazed=(0.12, 0.08, 0.88, 0.93))
g.transom(b, fr["N"], op["off"], op["w"], FL + 2.13, op["head"], T, trim="alu", lights=1)
# door leaf glazing (storefront door is mostly glass): add a glass pane inside the leaf's frame
# (the leaf itself is an aluminium frame slab; see panels) -- glass sheet in the door object below
for k in ("E", "W", "S"):
    for o in walls[k][2]:
        if o["sill"] > FL + 0.1 and not (k == "E" and o["w"] < 0.5):
            g.window(b, "windows", fr[k], o["off"], o["w"], o["sill"], o["head"], T, sash_rows=1, sash_cols=1,
                     mats={"trim": "alu"}, casing=0.04, glass_name="glass")
gb = walls["E"][2][0]                                                              # glass block panel
b.part("glassblock").obox(fr["E"], (gb["off"], T * 0.3, gb["sill"]), (gb["off"] + gb["w"], T * 0.7, gb["head"]), "glassblock")
g.door(b, "doorframe", fr["S"], 1.0, 0.92, FL + 2.1, T, "loading", swing_in=False, leaves=1, mat="steel_door",
       threshold_z=FL, panels=[(0.1, 0.1, 0.9, 0.9)], locked=True)
# planter bed under the front window (photo) + front walk + rear stoop
site = b.part("site-col")
site.box((wx(145), Y1, 0), (wx(480), Y1 + 0.45, 0.22), "concrete")
site.box((wx(150), Y1 + 0.03, 0.22), (wx(475), Y1 + 0.42, 0.25), "mulch")
site.box((X0 - 1.5, Y1, -0.02), (X1 + 1.5, Y1 + 2.0, FL - 0.01), "concrete", sides="Z")
site.box((X0 + 0.7, Y0 - 1.3, 0), (X0 + 2.2, Y0, FL - 0.01), "concrete")

# ------------------------------------------------------------------ interior
fl = b.part("floor-col")
LOBBY_D = 3.6
yp = Y1 - T - LOBBY_D
fl.box((X0 + T, yp, FL - 0.01), (X1 - T, Y1 - T, FL), "vct_l", sides="Z")
fl.box((X0 + T, Y0 + T, FL - 0.01), (X1 - T, yp, FL), "vct_w", sides="Z")
fl.box((X0 + T, Y0 + T, CEIL), (X1 - T, Y1 - T, CEIL + 0.02), "ceiling", sides="z")
# lobby / workroom partition: PO box wall + service window + staff door (locked: staff only)
pp = b.part("partition-col")
box_off, box_w = 0.25, 2.5
win_off, win_w = box_off + box_w + 0.25, 1.3
door_off = W - 2 * T - 1.25
pf = g.wall(pp, (X1 - T, yp), (X0 + T, yp), FL, CEIL, 0.3,
            [dict(off=box_off, w=box_w, sill=FL + 0.45, head=FL + 2.0),
             dict(off=win_off, w=win_w, sill=FL + 1.05, head=FL + 2.05),
             dict(off=door_off, w=0.9, sill=FL, head=FL + 2.1)], "drywall", "drywall")
# the partition runs east->west, so its left (w_in) side is the WORKROOM (south); lobby face is v0
o, u, w_in, up = pf
F = pf
pb = b.part("po_boxes")
pb.obox(F, (box_off, 0.0, FL + 0.45), (box_off + box_w, 0.3, FL + 2.0), "brass")                  # box bank body
cols, rows = 16, 9
for c in range(cols):
    for r in range(rows):
        x = box_off + 0.04 + c * (box_w - 0.08) / cols
        z = FL + 0.5 + r * 1.45 / rows
        wdt = (box_w - 0.08) / cols - 0.012
        hgt = 1.45 / rows - 0.012
        pb.obox(F, (x, -0.01, z), (x + wdt, 0.0, z + hgt), "brass")
        pb.obox(F, (x + wdt * 0.35, -0.018, z + hgt * 0.35), (x + wdt * 0.65, -0.01, z + hgt * 0.65), "steel")  # dial
# service window: counter + roll-down grille housing
pp.obox(F, (win_off - 0.05, -0.35, FL + 1.0), (win_off + win_w + 0.05, 0.35, FL + 1.05), "counter")
pp.obox(F, (win_off, -0.05, FL + 2.05), (win_off + win_w, 0.05, FL + 2.2), "alu")
g.door(b, "doorframe", pf, door_off, 0.9, FL + 2.1, 0.3, "staff", swing_in=True, leaves=1, mat="steel_door",
       threshold_z=FL, panels=[(0.1, 0.1, 0.9, 0.9)], locked=True)
lp = b.part("lobby-col")
# writing counter (west wall), bulletin board, stamp machine, flag-bearing wanted-poster board
fu.table(lp, (X0 + T + 0.35, Y1 - T - 1.8, FL), -90, 1.4, 0.5, 1.07, "counter")
lp.box((X0 + T, Y1 - T - 2.6, FL + 1.3), (X0 + T + 0.03, Y1 - T - 1.0, FL + 2.1), "cork")
for i in range(5):
    lp.box((X0 + T + 0.03, Y1 - T - 2.5 + i * 0.3, FL + 1.45 + (i % 2) * 0.25), (X0 + T + 0.035, Y1 - T - 2.3 + i * 0.3,
           FL + 1.75 + (i % 2) * 0.25), "paper")
b.empty("light_lobby", (0, Y1 - T - 1.8, CEIL - 0.05))
# workroom: sorting case, work tables, hampers, scale; postmaster's office + restroom partitions
wp = b.part("workroom-col")
for k in range(2):                                           # pigeonhole sorting cases along the east wall
    ys = yp - 0.9 - k * 1.4
    fu.shelves(wp, (X1 - T - 0.2, ys, FL), 90, 1.3, 0.35, 1.9, 9, "counter")
    for c in range(1, 6):
        wp.box((X1 - T - 0.37, ys - 0.65 + c * 0.26 - 0.008, FL + 0.08), (X1 - T - 0.03, ys - 0.65 + c * 0.26 + 0.008, FL + 1.9), "counter")
fu.table(wp, (0.2, yp - 2.0, FL), 0, 2.0, 0.9, 0.9, "counter")
for (hx, hy) in ((-0.4, yp - 3.3), (0.3, yp - 3.3), (1.0, yp - 3.3)):
    wp.box((hx - 0.3, hy - 0.25, FL + 0.1), (hx + 0.3, hy + 0.25, FL + 0.75), "canvas")        # canvas mail hampers
    for sx in (-1, 1):
        for sy in (-1, 1):
            wp.box((hx + sx * 0.27 - 0.02, hy + sy * 0.22 - 0.02, FL), (hx + sx * 0.27 + 0.02, hy + sy * 0.22 + 0.02, FL + 0.1), "steel")
fu.platform_scale(wp, (0.9, yp - 0.6, FL), 180, "steel", "steel")
ox1 = X0 + T + 2.5
oy1 = Y0 + T + 3.0
of = g.wall(wp, (ox1, Y0 + T), (ox1, oy1), FL, CEIL, 0.1, [dict(off=1.9, w=0.8, sill=FL, head=FL + 2.05)], "drywall", "drywall")
g.door(b, "doorframe", of, 1.9, 0.8, FL + 2.05, 0.1, "postmaster", swing_in=False, leaves=1, mat="counter", threshold_z=FL)
g.wall(wp, (ox1, oy1), (X0 + T, oy1), FL, CEIL, 0.1, [], "drywall", "drywall")
fu.desk(wp, (X0 + T + 1.2, Y0 + T + 0.5, FL), 180, "counter", "steel")
fu.chair(wp, (X0 + T + 1.2, Y0 + T + 1.2, FL), 180, "counter")
fu.safe(wp, (X0 + T + 0.45, oy1 - 0.5, FL), -90, "steel", "brass")
rx0 = X1 - T - 1.6
rf = g.wall(wp, (rx0, oy1 - 0.9), (rx0, Y0 + T), FL, CEIL, 0.1, [dict(off=0.15, w=0.75, sill=FL, head=FL + 2.05)],
            "drywall", "drywall")
g.door(b, "doorframe", rf, 0.15, 0.75, FL + 2.05, 0.1, "restroom", swing_in=True, leaves=1, mat="counter", threshold_z=FL)
g.wall(wp, (X1 - T, oy1 - 0.9), (rx0, oy1 - 0.9), FL, CEIL, 0.1, [], "drywall", "drywall")
fu.toilet(wp, (X1 - T - 0.4, Y0 + T + 0.35, FL), 0, "china", "china")
fu.sink_counter(wp, (X1 - T - 0.3, oy1 - 1.5, FL), 90, 0.55, "china", "china", "steel")
b.empty("light_work", (0.3, yp - 1.8, CEIL - 0.05))
b.empty("light_work", (0.3, Y0 + 2.0, CEIL - 0.05))
b.empty("light_office", (X0 + 1.5, Y0 + 1.5, CEIL - 0.05))

# ------------------------------------------------------------------ signs, flag, collection box
g.text_mesh(b, "sign_us_post_office", "U.S. POST OFFICE", 0.24, ((wx(405) + wx(640)) / 2, Y1 + 0.005, FL + 2.02), math.pi,
            "letters", extrude=0.02, font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
g.text_mesh(b, "sign_pruett", "PRUETT", 0.2, ((wx(405) + wx(640)) / 2, Y1 + 0.005, FL + 1.66), math.pi, "letters",
            extrude=0.02, font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
# hours plaque on the brick beside the entrance
b.part("shell-col").box((1.22, Y1, FL + 1.49), (2.2, Y1 + 0.004, FL + 1.63), "white")
g.text_mesh(b, "sign_hours", "LOBBY 7-6 · WINDOW 8-12, 1-4 · SAT 8-11", 0.04, (1.71, Y1 + 0.005, FL + 1.55), math.pi,
            "sign_black", extrude=0.002, font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
g.text_mesh(b, "sign_staff", "EMPLOYEES ONLY", 0.06, (X1 - T - door_off - 0.45, yp + 0.01, FL + 2.25), math.pi, "sign_black",
            extrude=0.002)
# flag pole + flag (13 stripes, blue canton)
fx, fy = X0 - 1.6, Y1 + 1.4
fp = b.part("flagpole-col")
fp.cylinder((fx, fy), 0.06, 0, 7.5, "pole", n=10, r1=0.035)
fp.cylinder((fx, fy), 0.09, 7.5, 7.62, "brass", n=10)
fp.cylinder((fx, fy), 0.25, 0, 0.3, "concrete", n=12)
flag = b.part("flag")
FW, FH = 1.5, 0.95
for s in range(13):
    z1 = 7.35 - s * FH / 13
    flag.box((fx + 0.07, fy - 0.003, z1 - FH / 13), (fx + 0.07 + FW, fy + 0.003, z1), "red" if s % 2 == 0 else "white")
flag.box((fx + 0.07, fy - 0.005, 7.35 - FH * 7 / 13), (fx + 0.07 + FW * 0.4, fy + 0.005, 7.35), "navy")
# blue collection box at the curb (photo)
cb = b.part("collection_box-col")
bx, by = wx(990), Y1 + 2.8
cb.box((bx - 0.28, by - 0.23, 0.15), (bx + 0.28, by + 0.23, 1.15), "usps_blue")
cb.cylinder((bx, by), 0.23, 1.15, 1.2, "usps_blue", n=14)
for sx in (-1, 1):
    for sy in (-1, 1):
        cb.box((bx + sx * 0.24 - 0.025, by + sy * 0.19 - 0.025, 0), (bx + sx * 0.24 + 0.025, by + sy * 0.19 + 0.025, 0.15), "usps_blue")
cb.box((bx - 0.2, by + 0.23, 0.95), (bx + 0.2, by + 0.26, 1.05), "steel")                  # pull-down slot
g.text_mesh(b, "sign_us_mail", "U.S. MAIL", 0.08, (bx, by + 0.235, 0.72), math.pi, "white", extrude=0.002,
            font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
# curb sign
cs = b.part("curb_sign-col")
cs.box((X1 + 1.0, Y1 + 3.2, 0), (X1 + 1.05, Y1 + 3.25, 2.2), "steel")
cs.box((X1 + 0.8, Y1 + 3.26, 1.6), (X1 + 1.25, Y1 + 3.28, 2.15), "white")
for i, t_ in enumerate(("NO", "PARKING", "MAIL", "VEHICLES", "ONLY")):
    g.text_mesh(b, f"sign_noparking_{i}", t_, 0.055, (X1 + 1.025, Y1 + 3.285, 2.07 - i * 0.1), math.pi,
                "red" if i < 2 else "sign_black", extrude=0.002, font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")

b.finish(OUT)
