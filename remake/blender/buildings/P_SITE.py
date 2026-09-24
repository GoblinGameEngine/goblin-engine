"""
P-SITE -- Pruett village site: ground, streets, sidewalks, the C&NW track and grade crossing,
street/route/village signs, streetlights, trees.  The ten Pruett structures and the three
crossings are separate .glbs placed on this plan (remake/godot pruett_test.gd uses the same
numbers, see LOTS below).  Coordinates: metres, +X east, +Y north; Main St = US 30 along X.

Layout rules followed (research/generator_rules.md): village tier -- Main St core of 1-2
blocks with zero-setback-style frontage, church and depot within a block of Main (§9), grain
elevator on a side street by the rail corridor, never on Main (§6/§9), rail corridor parallel
to Main one block back (rail-spine village, §6), 20 m Main St right-of-way, gravel side streets.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbbridge as gbr  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
b = g.Building("P-SITE", os.path.join(ROOT, "remake", "textures", "p-site"))
b.sink_ground = False               # the site is ground itself (and a flat stand-in for map terrain)
for n, t in (("grass", 4.0), ("asphalt", 3.0), ("gravel_road", 3.0), ("sidewalk", 2.0), ("ballast", 2.0), ("ties", 2.6),
             ("bark", 1.0), ("leaves", 1.5)):
    b.mat(n, tex=n, tile_m=t)
for k, c, r, m in (("rail", (0.35, 0.3, 0.27), 0.4, 0.9), ("paint_yellow", (0.9, 0.72, 0.12), 0.6, 0.0),
                   ("paint_white", (0.92, 0.92, 0.9), 0.6, 0.0), ("sign_green", (0.05, 0.35, 0.18), 0.4, 0.0),
                   ("sign_white", (0.95, 0.95, 0.93), 0.4, 0.0), ("sign_black", (0.04, 0.04, 0.04), 0.5, 0.0),
                   ("post_steel", (0.6, 0.62, 0.64), 0.4, 0.9), ("curb", (0.7, 0.69, 0.66), 0.8, 0.0),
                   ("lamp", (0.95, 0.92, 0.8), 0.3, 0.0), ("pole_wood", (0.35, 0.27, 0.2), 0.9, 0.0),
                   ("crossbuck", (0.96, 0.96, 0.96), 0.5, 0.0)):
    b.mat(k, color=c, rough=r, metal=m)

X0, X1, Y0, Y1 = -270.0, 270.0, -150.0, 130.0
HOLES = [(-260.0, -200.0, -20.0, 20.0),        # US 30 bridge patch
         (190.0, 230.0, -20.0, 20.0),          # US 30 culvert patch
         (-260.0, -200.0, -150.0, -110.0)]     # C&NW arch patch (shown standalone in the slice)
TRACK_Y = -70.0
DEPOT_ST_X, ELEV_ST_X = -15.0, 42.0

# below-grade spaces the ground must not cap (world rects x0, x1, y0, y1): the tavern's dirt
# cellar under its whole main block (P_TAVERN: 37'-1" x 26'-10", lot at (-30, 17) turned 180),
# and the elevator's dump/boot pit under the driveway grate (P_ELEV: 1.4 x 2.0 m, lot at (58, -45))
TAV_W, TAV_D = g.ft(37, 1), g.ft(26, 10)
CUTS = [(-30.0 - TAV_W / 2, -30.0 + TAV_W / 2, 17.0 - TAV_D / 2, 17.0 + TAV_D / 2),
        (58.0 - 0.7, 58.0 + 0.7, -45.0 - 1.0, -45.0 + 1.0)]

# ground: 10 m grid with holes where the crossings bring their own creek terrain; cells that a
# cut overlaps are split on the cut's edges and only the pieces outside it are kept
gp = b.part("ground-col")
x = X0
while x < X1:
    y = Y0
    while y < Y1:
        cx, cy = x + 5, y + 5
        if not any(h[0] <= cx <= h[1] and h[2] <= cy <= h[3] for h in HOLES):
            cuts = [c for c in CUTS if c[0] < x + 10 and x < c[1] and c[2] < y + 10 and y < c[3]]
            xs = sorted({x, x + 10} | {v for c in cuts for v in c[:2] if x < v < x + 10})
            ys = sorted({y, y + 10} | {v for c in cuts for v in c[2:] if y < v < y + 10})
            for xa, xb in zip(xs, xs[1:]):
                for ya, yb in zip(ys, ys[1:]):
                    mx, my = (xa + xb) / 2, (ya + yb) / 2
                    if any(c[0] < mx < c[1] and c[2] < my < c[3] for c in cuts):
                        continue
                    gp.face([(xa, ya, 0.0), (xb, ya, 0.0), (xb, yb, 0.0), (xa, yb, 0.0)], "grass")
        y += 10
    x += 10

# Main St / US 30: asphalt lanes, parking lanes + curbs + sidewalks through the core
rd = b.part("streets-col")
for (xa, xb) in ((-200.0, 190.0), (230.0, 270.0)):
    rd.box((xa, -3.65, -0.2), (xb, 3.65, 0.02), "asphalt", mats={"z": "asphalt"})
rd.box((-60.0, 3.65, -0.2), (95.0, 6.15, 0.02), "asphalt", mats={"z": "asphalt"})
rd.box((-60.0, -6.15, -0.2), (95.0, -3.65, 0.02), "asphalt", mats={"z": "asphalt"})
for s in (-1, 1):
    y_curb = s * 6.15
    rd.box((-60.0, min(y_curb, y_curb + s * 0.15), 0.0), (95.0, max(y_curb, y_curb + s * 0.15), 0.15), "curb")
    rd.box((-60.0, min(y_curb + s * 0.15, s * 9.0), 0.0), (95.0, max(y_curb + s * 0.15, s * 9.0), 0.14), "sidewalk")
mk = b.part("road_marks")
xx = -198.0
while xx < 268:
    if not (190 <= xx <= 230):
        mk.box((xx, -0.06, 0.021), (xx + 3.0, 0.06, 0.023), "paint_yellow")
    xx += 9.0
for xs in range(-58, 94, 7):                                  # parking stall lines in the core
    for s in (-1, 1):
        mk.box((xs - 0.05, min(s * 3.7, s * 6.1), 0.021), (xs + 0.05, max(s * 3.7, s * 6.1), 0.023), "paint_white")
# side streets (gravel): Depot St across the track, Elevator St to the elevator
rd.box((DEPOT_ST_X - 3.0, -85.0, -0.2), (DEPOT_ST_X + 3.0, -9.0, 0.02), "gravel_road", mats={"z": "gravel_road"})
rd.box((DEPOT_ST_X - 3.0, 9.0, -0.2), (DEPOT_ST_X + 3.0, 95.0, 0.02), "gravel_road", mats={"z": "gravel_road"})
rd.box((ELEV_ST_X - 3.0, -66.0, -0.2), (ELEV_ST_X + 3.0, -9.0, 0.02), "gravel_road", mats={"z": "gravel_road"})

# C&NW track through the village at grade, timber grade crossing at Depot St
tp = b.part("track-col")
tp.box((-200.0, TRACK_Y - 1.8, -0.15), (270.0, TRACK_Y + 1.8, 0.2), "ballast")
tt = b.part("track_ties")
xx = -199.75
while xx < 270:
    tt.box((xx - 0.11, TRACK_Y - 1.3, 0.2), (xx + 0.11, TRACK_Y + 1.3, 0.37), "ties")
    xx += 0.5
for sy in (-0.72, 0.72):
    tt.box((-200.0, TRACK_Y + sy - 0.035, 0.37), (270.0, TRACK_Y + sy + 0.035, 0.52), "rail")
    tt.box((-200.0, TRACK_Y + sy - 0.07, 0.37), (270.0, TRACK_Y + sy + 0.07, 0.39), "rail")
tp.box((DEPOT_ST_X - 3.0, TRACK_Y - 1.4, 0.2), (DEPOT_ST_X + 3.0, TRACK_Y + 1.4, 0.52), "ties")   # crossing planks
# ramps up to the crossing
for s in (-1, 1):
    y0 = TRACK_Y + s * 1.4
    q = [(DEPOT_ST_X - 3.0, y0, 0.52), (DEPOT_ST_X + 3.0, y0, 0.52), (DEPOT_ST_X + 3.0, y0 + s * 5.0, 0.02), (DEPOT_ST_X - 3.0, y0 + s * 5.0, 0.02)]
    tp.face(q if s < 0 else q[::-1], "gravel_road")


def crossbuck(x, y, facing):
    p = b.part("crossbucks-col")
    p.box((x - 0.06, y - 0.06, 0.0), (x + 0.06, y + 0.06, 3.9), "crossbuck")
    ca, sa = math.cos(facing), math.sin(facing)
    for sgn in (1, -1):
        ang = sgn * math.radians(45)
        # two boards crossed at 90 deg, drawn as thin rotated slabs in the facing plane
        for k in range(12):
            t = -0.6 + k * 0.1
            px, pz = t * math.cos(ang), 3.4 + t * math.sin(ang)
            p.box((x + ca * px - 0.07, y + sa * px - 0.07, pz - 0.1), (x + ca * px + 0.07, y + sa * px + 0.07, pz + 0.1), "crossbuck")
    g.text_mesh(b, f"sign_rrx_{x:.0f}_{y:.0f}", "RAILROAD  CROSSING", 0.07, (x - sa * 0.09, y + ca * 0.09, 3.4), facing,
                "sign_black", extrude=0.002, font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")


crossbuck(DEPOT_ST_X + 4.0, TRACK_Y + 4.5, math.pi)
crossbuck(DEPOT_ST_X - 4.0, TRACK_Y - 4.5, 0.0)

# street name signs at the corners, route + village signs on US 30
for (x, y, a_txt, b_txt) in ((DEPOT_ST_X - 3.8, 9.6, "MAIN ST", "DEPOT ST"), (ELEV_ST_X + 3.8, -9.6, "MAIN ST", "ELEVATOR ST")):
    p = b.part("street_signs-col")
    p.box((x - 0.04, y - 0.04, 0.0), (x + 0.04, y + 0.04, 2.9), "post_steel")
    p.box((x - 0.55, y - 0.02, 2.55), (x + 0.55, y + 0.02, 2.75), "sign_green")
    p.box((x - 0.02, y - 0.55, 2.8), (x + 0.02, y + 0.55, 3.0), "sign_green")
    g.text_mesh(b, f"sign_st_{a_txt}_{x:.0f}", a_txt, 0.11, (x, y - 0.025, 2.65), 0.0, "sign_white", extrude=0.002,
                font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
    g.text_mesh(b, f"sign_st_{b_txt}_{x:.0f}", b_txt, 0.11, (x - 0.025, y, 2.9), -math.pi / 2, "sign_white", extrude=0.002,
                font="/run/host/usr/share/fonts/noto/NotoSans-Bold.ttf")
for (x, face) in ((-165.0, -math.pi / 2), (165.0, math.pi / 2)):
    yy = -6.0 if x < 0 else 6.0
    gbr.post_sign(b, f"welcome_{'W' if x < 0 else 'E'}", x, yy, face, [("PRUETT", 0.28), ("Pop. 820", 0.14),
                  ("Home of the Pruett Co-op", 0.1)], board=(2.2, 1.1), board_mat="sign_green", text_mat="sign_white", height=1.6)
    gbr.post_sign(b, f"us30_{'W' if x < 0 else 'E'}", x + (15 if x < 0 else -15), -yy, face + math.pi,
                  [("US", 0.14), ("30", 0.28)], board=(0.65, 0.7))
    gbr.post_sign(b, f"speed_{'W' if x < 0 else 'E'}", x + (25 if x < 0 else -25), yy, face, [("SPEED", 0.11), ("LIMIT", 0.11),
                  ("30", 0.3)], board=(0.6, 0.8))

# streetlights (cobra heads on wood poles) along Main St through the core
lp = b.part("streetlights-col")
for (i, x) in enumerate(range(-50, 100, 30)):
    y = 9.3 if i % 2 == 0 else -9.3
    s = -1 if y > 0 else 1
    lp.cylinder((x, y), 0.13, 0.0, 8.5, "pole_wood", n=10, r1=0.1)
    lp.box((x - 0.05, min(y, y + s * 2.2), 7.9), (x + 0.05, max(y, y + s * 2.2), 8.0), "post_steel")
    lp.box((x - 0.18, y + s * 2.2 - 0.3, 7.75), (x + 0.18, y + s * 2.2 + 0.3, 7.95), "lamp")
    b.empty("light_street", (x, y + s * 2.2, 7.6))

# trees: big maples along the residential lots + a few by the church/depot
tr = b.part("trees-col")
for (tx, ty, h) in ((-90, 40, 11), (-60, 45, 13), (5, 42, 12), (48, 48, 10), (90, 40, 12), (-50, 75, 11), (-5, 80, 12),
                    (15, -30, 10), (-40, -40, 12), (80, -25, 11), (-70, -12, 9), (100, 18, 10)):
    tr.cylinder((tx, ty), 0.25, 0.0, h * 0.45, "bark", n=10, r1=0.18)
    crown = b.part("tree_crowns")
    for k, (dx, dy, dz, r) in enumerate(((0, 0, 0.7, 0.38), (1.2, 0.5, 0.6, 0.28), (-1.0, -0.8, 0.62, 0.3), (0.3, 1.1, 0.8, 0.26))):
        cz = h * dz
        rr = h * r
        crown.cylinder((tx + dx, ty + dy), rr, cz - rr * 0.8, cz, "leaves", n=10, r1=rr * 0.95)
        crown.cylinder((tx + dx, ty + dy), rr * 0.95, cz, cz + rr * 0.7, "leaves", n=10, r1=rr * 0.2)

b.finish(os.path.join(ROOT, "godot_project", "remake", "buildings", "P-SITE.glb"))

# lot plan shared with Godot (pruett_test.gd): name -> (x east, y north, yaw deg CCW from above)
LOTS = {
    "P-TAVERN": (-30.0, 17.0, 180), "P-CHURCH": (-2.0, 18.6, 0), "P-STORE": (22.0, 18.0, 180),
    "P-PO": (-40.0, -19.3, 0), "P-DEPOT": (8.0, -59.2, 0), "P-ELEV": (58.0, -45.0, 0),
    "P-HOUSE1": (72.0, 26.0, 180), "P-HOUSE4": (-80.0, 22.0, 180), "P-HOUSE2": (-35.2, 55.0, -90),
    "P-HOUSE3": (28.0, -35.0, -90), "P-BR-US30": (-230.0, 0.0, -90), "P-CULVERT": (210.0, 0.0, -90),
    "P-BR-RAIL": (-230.0, -130.0, -90), "P-SITE": (0.0, 0.0, 0),
}
