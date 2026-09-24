"""
P-HOUSE1 -- Haugen house, 214 Main St, Pruett.

Real example: Horace Paine House, Walker & Illinois Streets, Grand Detour, Ogle County, IL
(1850s Greek Revival, 1 1/2 storeys) -- HABS ILL-175 (remake/reference/P-HOUSE1/).
Sheet 1: first + second floor plans (1/16"), front (north) elevation (1/4") with the vertical
dimension string (1'-2" grade->floor, 2'-8" sill, 5'-2" window, 8'-0" ceiling, 10" floor,
3'-10" knee to plate, 7'-7 1/2" roof rise), 44'-0" x 28'-4" main block, 51'-2" overall with
the rear kitchen wing, 9'-0" side porch.  Photos: five-bay front (two 6/6 shuttered windows,
sidelit door with entablature, three 2/2 windows), frieze windows under the eave, rear wing
with a lattice-screened porch (photo 3), wallpapered interiors (photos 7-9).
The plan is simplified to its room sequence: bedrooms W, front stair hall, living room,
parlour E, back hall, bath (modern), dining + kitchen in the wing.  Occupied today: modern
furnishing in period rooms.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbhouse as gh  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-house1")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-HOUSE1.glb")

b = g.Building("P-HOUSE1", TEX)
for k, t, tile in (("siding", "siding", 1.0), ("roof", "roof", 1.0), ("found", "foundation", 1.2), ("trim", "trim", 1.0),
                   ("shutter", "shutter", 1.0), ("floor", "floor", 2.0), ("plaster", "plaster", 2.0),
                   ("wallpaper_a", "wallpaper_a", 0.9144), ("lino", "lino", 0.9144), ("hextile", "hextile", 0.3048),
                   ("porch", "porch", 2.0), ("door", "door", 1.0), ("furniture", "furniture", 1.0), ("chimney", "chimney", 1.0),
                   ("iron", "iron", 0.5)):
    b.mat(k, tex=t, tile_m=tile)
for k, c, r in (("brass", (0.75, 0.6, 0.28), 0.3), ("threshold", (0.5, 0.48, 0.44), 0.8), ("enamel", (0.93, 0.93, 0.9), 0.3),
                ("steel", (0.7, 0.72, 0.74), 0.35), ("china", (0.96, 0.96, 0.94), 0.2), ("counter_top", (0.78, 0.74, 0.66), 0.4),
                ("upholstery", (0.35, 0.42, 0.33), 0.9), ("quilt", (0.6, 0.25, 0.22), 0.9), ("rug", (0.45, 0.2, 0.18), 0.95),
                ("tv", (0.05, 0.05, 0.06), 0.2), ("burlap", (0.6, 0.5, 0.35), 0.95), ("mail_black", (0.08, 0.08, 0.08), 0.4),
                ("white_text", (0.95, 0.95, 0.95), 0.5)):
    b.mat(k, color=c, rough=r, metal=0.9 if k in ("brass", "steel") else 0.0)
b.mat("glass", color=(0.72, 0.8, 0.84), rough=0.05, alpha=0.2)
b.mat("glassblock", color=(0.75, 0.82, 0.85), rough=0.2, alpha=0.6)

FT = g.FT
FL1 = g.ft(1, 2)
CEIL1 = FL1 + g.ft(8, 0)
FL2 = CEIL1 + g.ft(0, 10)
PLATE = FL2 + g.ft(3, 10)
CEIL2 = FL2 + g.ft(7, 6)
HX, HY = g.ft(44, 0) / 2, g.ft(28, 4) / 2          # main block half-sizes
WX0 = HX - g.ft(14, 0)                             # wing west face (wing is 14' wide, flush east)
WY0 = -HY - g.ft(23, 0)                            # wing south face (51'-2" overall)
SILL, WH = g.ft(2, 8), g.ft(5, 2)

spec = dict(
    t_ext=0.15, t_int=0.1, era="modern",
    mats=dict(ext="siding", int="plaster", roof="roof", roof_under="trim", found="found", floor="floor", ceiling="plaster",
              trim="trim", door="door", fascia="trim", porch="porch", post="trim", furn="furniture"),
    blocks=[
        dict(name="main", rect=(-HX, -HY, HX, HY), floors=[(FL1, CEIL1), (FL2, CEIL2)], wall_top=PLATE, found_top=FL1 - 0.05,
             roof=dict(type="gable", ridge="x", pitch=28.2, eave_oh=0.35, rake_oh=0.2, thick=0.16), habitable_attic=True),
        dict(name="wing", rect=(WX0, WY0, HX, -HY), floors=[(FL1, FL1 + 2.44)], wall_top=FL1 + 2.62, found_top=FL1 - 0.05,
             roof=dict(type="gable", ridge="y", pitch=30, eave_oh=0.3, rake_oh=0.2, thick=0.14)),
    ],
    rooms=[
        dict(name="BR1", rect=(-HX, -0.3, -2.36, HY), type="bed"),
        dict(name="BR2", rect=(-HX, -HY, -2.36, -0.3), type="bed"),
        dict(name="HALLF", rect=(-2.36, -1.2, -0.6, HY), type="hall"),
        dict(name="LR", rect=(-0.6, -1.2, 3.6, HY), type="living"),
        dict(name="PARLOR", rect=(3.6, -1.2, HX, HY), type="sitting"),
        dict(name="BACKHALL", rect=(-2.36, -HY, 4.7, -1.2), type="hall"),
        dict(name="BATH", rect=(4.7, -HY, HX, -1.2), type="bath", floor_mat="hextile"),
        dict(name="DR", rect=(WX0, -7.8, HX, -HY), type="dining"),
        dict(name="KIT", rect=(WX0, WY0, HX, -7.8), type="kitchen", floor_mat="lino"),
        dict(name="BR3", floor=1, rect=(-HX, -HY, -2.4, HY), type="bed"),
        dict(name="HALL2", floor=1, rect=(-2.4, -2.4, 0.4, 3.4), type=None),
        dict(name="CLN", floor=1, rect=(-2.4, 3.4, 0.4, HY), type="closet"),
        dict(name="CLS", floor=1, rect=(-2.4, -HY, 0.4, -2.4), type="closet"),
        dict(name="BR4", floor=1, rect=(0.4, -0.2, HX, HY), type="bed"),
        dict(name="BR6", floor=1, rect=(0.4, -HY, HX, -0.2), type="bed"),
    ],
    doors=[
        dict(name="front", at=(-1.48, HY), w=0.9, h=2.1, ext=True, sidelights=0.28, panels=[(0.18, 0.08, 0.82, 0.92)]),
        dict(name="back", at=(1.2, -HY), w=0.85, ext=True, glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="kitchen_porch", at=(WX0, -10.0), w=0.85, ext=True, glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="hall_br1", at=(-2.36, 2.2), w=0.8, swing_into="BR1"),
        dict(name="hall_lr", at=(-0.6, 3.8), w=0.9, swing_into="LR"),
        dict(name="hall_back", at=(-1.7, -1.2), w=0.8, swing_into="BACKHALL"),
        dict(name="lr_parlor", at=(3.6, -0.3), w=0.9, swing_into="PARLOR"),
        dict(name="lr_back", at=(1.8, -1.2), w=0.8, swing_into="BACKHALL"),
        dict(name="br2", at=(-2.36, -2.6), w=0.8, swing_into="BR2"),
        dict(name="bath", at=(4.7, -2.6), w=0.75, swing_into="BATH"),
        dict(name="dining", at=(3.3, -HY), w=0.9, swing_into="DR"),
        dict(name="kitchen", at=(4.6, -7.8), w=0.9, swing_into="KIT"),
        dict(name="br3", floor=1, at=(-2.4, -1.0), w=0.75, h=1.95, swing_into="BR3"),
        dict(name="br4", floor=1, at=(0.4, 1.4), w=0.75, h=1.95, swing_into="BR4"),
        dict(name="br6", floor=1, at=(0.4, -1.3), w=0.75, h=1.95, swing_into="BR6"),
        dict(name="closet_n", floor=1, at=(0.0, 3.4), w=0.6, h=1.3, swing_into="HALL2"),
        dict(name="closet_s", floor=1, at=(-1.0, -2.4), w=0.6, h=1.5, swing_into="HALL2"),
    ],
    windows=[
        *[dict(at=(x, HY), w=0.9, sill=SILL, h=WH, cols=3, shutters=True, head_cap=True) for x in (-5.28, -3.44)],
        *[dict(at=(x, HY), w=0.95, sill=SILL, h=WH, cols=1, shutters=True, head_cap=True) for x in (1.17, 3.15, 5.16)],
        dict(at=(-HX, 2.2), w=0.9, sill=SILL, h=WH, cols=3, shutters=True), dict(at=(-HX, -2.3), w=0.9, sill=SILL, h=WH, cols=3, shutters=True),
        dict(at=(HX, 2.5), w=0.9, sill=SILL, h=WH, cols=1, shutters=True), dict(at=(HX, 0.2), w=0.9, sill=SILL, h=WH, cols=1, shutters=True),
        dict(at=(HX, -2.7), w=0.6, sill=1.2, h=0.9, cols=1),
        dict(at=(HX, -6.0), w=0.9, sill=SILL, h=WH, cols=1), dict(at=(HX, -9.6), w=0.9, sill=SILL, h=WH, cols=1),
        dict(at=(4.6, WY0), w=0.9, sill=1.05, h=1.2, cols=1), dict(at=(WX0, -6.0), w=0.9, sill=SILL, h=WH, cols=1),
        dict(at=(-4.5, -HY), w=0.9, sill=SILL, h=WH, cols=3), dict(at=(-0.4, -HY), w=0.9, sill=SILL, h=WH, cols=3),
        # frieze ("lie-on-your-stomach") windows under the eaves, front + rear (elevation)
        *[dict(at=(x, HY), floor=1, w=0.9, sill=0.1, h=0.42, kind="fixed", cols=4, casing=0.05) for x in (-5.31, -3.47, -1.26, 1.16, 3.15, 5.16)],
        *[dict(at=(x, -HY), floor=1, w=0.9, sill=0.1, h=0.42, kind="fixed", cols=4, casing=0.05) for x in (-5.31, -3.47, -1.26, 1.16)],
        # gable-end windows lighting the upstairs bedrooms
        dict(at=(-HX, 1.3), floor=1, w=0.8, sill=0.55, h=1.2, cols=2), dict(at=(-HX, -1.3), floor=1, w=0.8, sill=0.55, h=1.2, cols=2),
        dict(at=(HX, 1.3), floor=1, w=0.8, sill=0.55, h=1.2, cols=2), dict(at=(HX, -1.3), floor=1, w=0.8, sill=0.55, h=1.2, cols=2),
    ],
    stairs=[dict(start=(-1.55, 3.2), dir=(0, -1), width=0.9, n=13, run=0.23, floor=0, to_floor=1, rail_side="right")],
    rails=[dict(floor=1, pts=[(-0.62, 3.2), (-0.62, 0.35)])],
    porches=[
        dict(rect=(WX0 - g.ft(9, 0), WY0, WX0, -HY), z=FL1 - 0.03, post_top=FL1 + 2.3,
             posts=[(WX0 - g.ft(9, 0) + 0.12, y) for y in (WY0 + 0.15, -9.0, -6.7, -HY - 0.15)],
             rails=[[(WX0 - g.ft(9, 0) + 0.12, -9.0), (WX0 - g.ft(9, 0) + 0.12, -HY - 0.15)]], rail_style="lattice",
             steps=dict(at=(WX0 - g.ft(9, 0), -10.1), dir=(-1, 0), width=1.2),
             roof=dict(type="shed", high="E", high_z=FL1 + 2.62, low_z=FL1 + 2.35, oh=0.2), ceiling_light=True),
        dict(rect=(-2.2, HY, -0.76, HY + 0.7), z=FL1 - 0.03, post_top=FL1, posts=[], beam=False, skirt_mat="found",
             steps=dict(at=(-1.48, HY + 0.7), dir=(0, 1), width=1.2, mat="found")),
    ],
    chimneys=[dict(at=(-4.5, -0.3), z0=FL1, top=7.35), dict(at=(3.6, 1.5), z0=FL1, top=7.1)],
    fireplaces=[dict(room="BR1", at=(-4.5, -0.25), facing=(0, 1)), dict(room="LR", at=(3.55, 1.5), facing=(-1, 0))],
)

house = gh.House(b, spec)
house.build()

# door entablature over the front entrance (elevation: flat cornice on pilasters)
tp = b.part("trim")
tp.box((-2.45, HY, FL1 + 2.25), (-0.51, HY + 0.12, FL1 + 2.5), "trim")
for x in (-2.35, -0.71):
    tp.box((x - 0.08, HY, FL1), (x + 0.08, HY + 0.06, FL1 + 2.25), "trim")
# frieze band + eave cornice across the front and rear (elevation)
for yy, s in ((HY, 1), (-HY, -1)):
    tp.box((-HX - 0.03, min(yy, yy + s * 0.04), FL2 - 0.12), (HX + 0.03, max(yy, yy + s * 0.04), FL2 - 0.04), "trim")
# picket fence along the front lot line with a working gate on the walk; mailbox at the curb
gh.picket_fence(b, [(-11.0, HY + 6.0), (11.0, HY + 6.0)], 1.05, "trim", name="front_fence", gate=(0, 11.0 - 1.48 - 0.55, 1.1))
gh.mailbox(b, (1.5, HY + 7.2, 0.0), 0.0, "HAUGEN", "214", "mail_black", "trim", "white_text")
walk = b.part("walk-col")
walk.box((-2.0, HY + 1.1, -0.02), (-0.96, HY + 6.0, 0.03), "found", sides="Z")

b.finish(OUT)
