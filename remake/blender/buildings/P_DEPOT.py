"""
P-DEPOT -- Pruett Depot Museum (former C&NW combination passenger depot).

Real example: Rock Island Railroad, Seneca Passenger Depot, Main & Cash Streets, Seneca,
La Salle Co., IL (1911-12) -- HAER IL-44 (remake/reference/P-DEPOT/).  Report: wood frame,
50' x 17', asbestos-shingle siding; photos (HAER 1-2 + Commons): single-storey, hipped roof
with deep bracketed eaves over a trackside platform, operator's bay window facing the track,
double-hung windows, doors on both long sides, freight end with a wide door.  The HAER record
has no plan, so the room layout is the standard combination-depot arrangement (waiting room,
ticket/telegraph office with the trackside bay between, baggage/freight room at the far end).
Pruett use: the village museum -- waiting-room benches kept, exhibit cases, the ticket window
and telegraph desk preserved; baggage cart and train-order signal outside.
Origin: centre of footprint at grade; TRACK SIDE = SOUTH (-Y), street side = north.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbfurn as fu  # noqa: E402
import gbhouse as gh  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-depot")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-DEPOT.glb")

b = g.Building("P-DEPOT", TEX)
gh.std_house_materials(b, ["siding", "roof", "platform", "found", "trim", "rr_red", "floor", "freight_floor", "beadboard",
                           "plaster", "door", "furniture", "iron"])
for k, c in (("board_white", (0.93, 0.92, 0.88)), ("letters_black", (0.05, 0.05, 0.05)), ("signal_red", (0.75, 0.1, 0.08)),
             ("signal_yellow", (0.9, 0.72, 0.1)), ("paper", (0.95, 0.93, 0.85))):
    b.mat(k, color=c, rough=0.55)

L, Wd = g.ft(50), g.ft(17)
X0, X1, Y0, Y1 = -L / 2, L / 2, -Wd / 2, Wd / 2
FL = 0.45                      # platform-height floor
CEIL = FL + 3.2
PLATE = FL + 3.35
BAY = 0.9                      # operator's bay projection toward the track

xw0, xw1 = X0, X0 + 6.2         # waiting room (west)
xo0, xo1 = xw1, xw1 + 3.4       # office (with the bay)
xf0, xf1 = xo1, X1              # baggage / freight room (east)

spec = dict(
    t_ext=0.15, t_int=0.1, era="old",
    mats=dict(ext="siding", int="plaster", roof="roof", roof_under="trim", found="found", floor="floor", ceiling="beadboard",
              trim="trim", door="door", fascia="rr_red", porch="platform", post="trim", furn="furniture"),
    blocks=[
        dict(name="depot", rect=(X0, Y0, X1, Y1), floors=[(FL, CEIL)], wall_top=PLATE, found_top=FL - 0.05,
             roof=dict(type="hip", pitch=30, eave_oh=1.6, thick=0.14)),
        dict(name="bay", rect=(xo0 + 0.6, Y0 - BAY, xo1 - 0.6, Y0), floors=[(FL, CEIL)], wall_top=PLATE - 0.2, found_top=FL - 0.05,
             roof=dict(type="hip", pitch=30, eave_oh=0.2, thick=0.1)),
    ],
    rooms=[
        dict(name="WAIT", rect=(xw0, Y0, xw1, Y1), type=None),
        dict(name="OFFICE", rect=(xo0, Y0, xo1, Y1), type=None),
        dict(name="BAYR", rect=(xo0 + 0.6, Y0 - BAY, xo1 - 0.6, Y0), type=None, no_light=True, open_plan_to="OFFICE"),
        dict(name="FREIGHT", rect=(xf0, Y0, xf1, Y1), type=None, floor_mat="freight_floor"),
    ],
    doors=[
        dict(name="wait_track", at=(xw0 + 3.0, Y0), w=0.95, ext=True, transom=0.4, glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="wait_street", at=(xw0 + 3.0, Y1), w=0.95, ext=True, transom=0.4, glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="office", at=(xo1 - 0.8, Y1), w=0.85, ext=True, transom=0.4),
        dict(name="wait_office", at=(xw1, Y1 - 1.2), w=0.8, swing_into="OFFICE", locked=False),
        dict(name="office_freight", at=(xo1, Y1 - 1.2), w=0.8, swing_into="OFFICE"),
        dict(name="freight_track", at=(xf0 + 3.0, Y0), w=2.2, h=2.5, ext=True, leaves=2, out=True, panels=[(0.1, 0.08, 0.9, 0.92)]),
        dict(name="freight_street", at=(xf0 + 3.0, Y1), w=2.2, h=2.5, ext=True, leaves=2, out=True, panels=[(0.1, 0.08, 0.9, 0.92)]),
    ],
    windows=[
        *[dict(at=(x, Y0), w=0.9, sill=0.85, h=1.7, cols=1) for x in (xw0 + 1.3, xw0 + 4.9)],
        *[dict(at=(x, Y1), w=0.9, sill=0.85, h=1.7, cols=1) for x in (xw0 + 1.3, xw0 + 4.9)],
        dict(at=(X0, 0.0), w=0.9, sill=0.85, h=1.7, cols=1), dict(at=(xo0 + 1.2, Y1), w=0.9, sill=0.85, h=1.7, cols=1),
        # operator's bay: three windows so the agent can see up and down the line
        dict(at=((xo0 + xo1) / 2, Y0 - BAY), w=1.0, sill=0.8, h=1.6, cols=1),
        dict(at=(xo0 + 0.6, Y0 - BAY / 2), w=0.5, sill=0.8, h=1.6, cols=1), dict(at=(xo1 - 0.6, Y0 - BAY / 2), w=0.5, sill=0.8, h=1.6, cols=1),
        dict(at=(X1, -1.5), w=0.7, sill=1.3, h=0.9, cols=2), dict(at=(X1, 1.5), w=0.7, sill=1.3, h=0.9, cols=2),
    ],
    porches=[dict(rect=(X0 - 6.0, Y0 - 4.2, X1 + 6.0, Y0), z=FL - 0.02, post_top=FL, posts=[], beam=False, skirt_mat="found",
                  steps=dict(at=(X0 - 6.0, Y0 - 2.0), dir=(-1, 0), width=2.0, mat="platform")),
             dict(rect=(xw0 + 2.2, Y1, xw0 + 3.8, Y1 + 1.0), z=FL - 0.02, post_top=FL, posts=[], beam=False, skirt_mat="found",
                  steps=dict(at=(xw0 + 3.0, Y1 + 1.0), dir=(0, 1), width=1.4, mat="found"))],
    chimneys=[dict(at=(xo0 + 1.7, 0.6), w=0.4, d=0.4, z0=CEIL, top=PLATE + 2.6, mat="platform")],
)
gh.House(b, spec).build()

# deep-eave brackets (knee braces) all round, depot red
br = b.part("brackets")
tn = math.tan(math.radians(30))
for x in [X0 + 0.3 + k * 2.4 for k in range(7)] + [X1 - 0.3]:
    for (y, s) in ((Y0, -1), (Y1, 1)):
        zt = PLATE - 1.2 * tn - 0.2
        br.box((x - 0.06, min(y, y + s * 1.3), zt - 0.12), (x + 0.06, max(y, y + s * 1.3), zt), "rr_red")
        br.box((x - 0.06, min(y, y + s * 0.2), zt - 1.0), (x + 0.06, max(y, y + s * 0.2), zt), "rr_red")
# waiting room: original slat benches along the walls + museum exhibit cases
wp = b.part("waiting-col")
for (x, y, yaw, ln) in ((xw0 + 0.35, 0.0, -90, 3.2), (xw0 + 1.35, Y1 - 0.5, 180, 1.4), (xw0 + 1.1, Y0 + 0.45, 0, 1.2)):
    fu.bench(wp, (x, y, FL), yaw, ln, "furniture")
for k, (x, y) in enumerate(((xw0 + 2.3, -0.3), (xw0 + 4.1, -0.3))):
    fu.display_case(wp, (x, y, FL), 0, 1.4, "furniture", "glass")
    for j in range(3):
        wp.box((x - 0.5 + j * 0.35, y - 0.15, FL + 0.62), (x - 0.3 + j * 0.35, y + 0.1, FL + 0.66 + 0.04 * j), "paper")
wp.box((xw0 + 5.9, -1.9, FL + 1.1), (xw0 + 6.03, 0.7, FL + 2.3), "board_white")         # exhibit panel on the partition
g.text_mesh(b, "sign_exhibit", "PRUETT & THE C&NW  1886-1971", 0.07, (xw0 + 5.88, -0.6, FL + 2.1), -math.pi / 2, "letters_black",
            extrude=0.002)
b.empty("light_wait", (xw0 + 3.0, 0.0, CEIL - 0.3))
# office: ticket window in the partition, telegraph/operator's desk in the bay
op = b.part("office-col")
op.box((xw1 - 0.05, -0.6, FL + 1.0), (xw1 + 0.05, 0.6, FL + 1.05), "furniture")          # ticket window counter (in the wall face)
fu.desk(op, ((xo0 + xo1) / 2, Y0 - BAY + 0.45, FL), 180, "furniture", "brass", w=1.6, d=0.6)
op.box(((xo0 + xo1) / 2 - 0.2, Y0 - BAY + 0.35, FL + 0.76), ((xo0 + xo1) / 2 + 0.2, Y0 - BAY + 0.6, FL + 0.9), "iron")  # telegraph key/sounder
fu.chair(op, ((xo0 + xo1) / 2, Y0 + 0.3, FL), 180, "furniture")
fu.safe(op, (xo1 - 0.45, -0.6, FL), -90, "iron", "brass")
fu.potbelly_stove(op, (xo0 + 1.7, 0.6, FL), "iron")
b.empty("light_office", ((xo0 + xo1) / 2, 0.0, CEIL - 0.3))
# freight room: baggage + crates, scale
fp = b.part("freight-col")
fu.platform_scale(fp, (xf0 + 1.0, 0.0, FL), 90, "furniture", "steel")
for k in range(5):
    fp.box((X1 - 1.8 + (k % 3) * 0.5, Y1 - 1.2 + (k // 3) * 0.5, FL), (X1 - 1.35 + (k % 3) * 0.5, Y1 - 0.75 + (k // 3) * 0.5, FL + 0.45), "furniture")
b.empty("light_freight", ((xf0 + xf1) / 2, 0.0, CEIL - 0.3))

# ------------------------------------------------------------------ platform furniture + signs
sg = b.part("signs-col")
for (x, rot, s_) in ((X0 - 0.02, -math.pi / 2, -1), (X1 + 0.02, math.pi / 2, 1)):
    sg.box((min(x, x + s_ * 0.06), -1.0, PLATE - 0.6), (max(x, x + s_ * 0.06), 1.0, PLATE - 0.15), "board_white")
    g.text_mesh(b, f"sign_station_{'W' if s_ < 0 else 'E'}", "PRUETT", 0.3, (x + s_ * 0.065, 0.0, PLATE - 0.38), rot, "letters_black",
                extrude=0.01)
# museum sign on posts by the street door
mx, my = xw0 + 5.5, Y1 + 3.0
for px in (mx - 0.8, mx + 0.8):
    sg.box((px - 0.05, my - 0.05, 0.0), (px + 0.05, my + 0.05, 1.8), "rr_red")
sg.box((mx - 0.95, my - 0.04, 0.9), (mx + 0.95, my + 0.04, 1.75), "board_white")
for i, (t, sz, z) in enumerate((("PRUETT DEPOT MUSEUM", 0.13, 1.56), ("C&NW  1912", 0.09, 1.34), ("Open Sat - Sun  1 - 4", 0.08, 1.12))):
    g.text_mesh(b, f"sign_museum_{i}", t, sz, (mx, my + 0.045, z), math.pi, "letters_black", extrude=0.003)
    g.text_mesh(b, f"sign_museum_b{i}", t, sz, (mx, my - 0.045, z), 0.0, "letters_black", extrude=0.003)
# train-order signal mast on the bay (two blades)
tm = b.part("train_order-col")
cx = (xo0 + xo1) / 2
tm.box((cx - 0.06, Y0 - BAY - 0.5, 0.0), (cx + 0.06, Y0 - BAY - 0.38, 7.0), "iron")
for (s_, m) in ((-1, "signal_red"), (1, "signal_yellow")):
    tm.box((cx + s_ * 0.05, Y0 - BAY - 0.47, 6.2), (cx + s_ * 1.0, Y0 - BAY - 0.41, 6.45), m)
# baggage cart on the platform
bc = b.part("baggage_cart-col")
bc.box((X1 + 2.0, Y0 - 2.6, 0.55), (X1 + 4.4, Y0 - 1.5, 0.63), "furniture")
for (x, y) in ((X1 + 2.3, Y0 - 2.6), (X1 + 4.1, Y0 - 2.6), (X1 + 2.3, Y0 - 1.5), (X1 + 4.1, Y0 - 1.5)):
    bc.box((x - 0.04, y - 0.22, FL - 0.02), (x + 0.04, y + 0.22, FL + 0.42), "iron")
for k in range(2):
    bc.box((X1 + 2.2 + k * 0.9, Y0 - 2.4, 0.63), (X1 + 3.0 + k * 0.9, Y0 - 1.7, 1.05), "furniture")   # trunks

b.finish(OUT)
