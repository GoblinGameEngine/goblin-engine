"""
P-HOUSE4 -- Kowalski house (workers' cottage), 402 Main St, Pruett.

Real example: 2019 Woodland Avenue (Cottage), Des Moines, Polk County, IA (c.1897) --
HABS IA-194 (remake/reference/P-HOUSE4/).  Report: one-storey frame cottage, main house with
rear wing ~28' x 32', cross-gable roof over the main house, hip roof over the rear wing, shed
roofs over the enclosed front porch and the enclosed rear porch (~20' x 5'), asbestos-cement
cover-up siding, brick foundation (exposed where the lot falls away), medium eaves, interior
brick chimney on the front-gable ridge ~14' from the south wall; 5 rooms (living room with
fireplace, dining room through an archway, 2 bedrooms, kitchen) + bath + entry hall; straight
stair kitchen -> full basement (not modelled: basement omitted in this slice, noted);
3-part living-room window (large centre pane flanked by 1/1); wood panel front door with a
6-pane window; back door with one glass panel over 3 horizontal panels; poured concrete steps
and walk; chain-link fence along the east property line.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbhouse as gh  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-house4")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-HOUSE4.glb")

b = g.Building("P-HOUSE4", TEX)
gh.std_house_materials(b, ["siding", "roof", "found", "trim", "floor", "plaster", "lino", "hextile", "porch", "door",
                           "furniture", "chimney", "iron"])

FL1 = 0.7
CEIL1 = FL1 + 2.75
PLATE = FL1 + 2.9
HX = g.ft(24) / 2
Y0, Y1 = 0.0, g.ft(22)                     # front-gable main block
WY0 = -g.ft(10)                            # rear hip wing
RPY0 = WY0 - g.ft(5)                       # enclosed rear porch
FPY1 = Y1 + g.ft(6)                        # enclosed front porch

spec = dict(
    t_ext=0.15, t_int=0.1, era="modern",
    mats=dict(ext="siding", int="plaster", roof="roof", found="found", floor="floor", ceiling="plaster", trim="trim", door="door",
              fascia="trim", porch="porch", post="trim", furn="furniture"),
    blocks=[
        dict(name="main", rect=(-HX, Y0, HX, Y1), floors=[(FL1, CEIL1)], wall_top=PLATE, found_top=FL1 - 0.05,
             roof=dict(type="gable", ridge="y", pitch=40, eave_oh=0.4, rake_oh=0.3, thick=0.15)),
        dict(name="bay", rect=(HX, 1.6, HX + 1.4, 5.2), floors=[(FL1, CEIL1)], wall_top=PLATE, found_top=FL1 - 0.05,
             roof=dict(type="gable", ridge="x", pitch=40, eave_oh=0.35, rake_oh=0.3, thick=0.14)),
        dict(name="wing", rect=(-HX, WY0, HX - 1.3, Y0), floors=[(FL1, CEIL1)], wall_top=PLATE, found_top=FL1 - 0.05,
             roof=dict(type="hip", pitch=30, eave_oh=0.4, thick=0.14)),
        dict(name="rporch", rect=(-HX, RPY0, -HX + g.ft(20), WY0), floors=[(FL1 - 0.1, FL1 + 2.2)], wall_top=FL1 + 2.3,
             found_top=FL1 - 0.15, roof=dict(type="shed", high="N", pitch=12, eave_oh=0.3, thick=0.1)),
        dict(name="fporch", rect=(-3.1, Y1, 1.1, FPY1), floors=[(FL1 - 0.1, FL1 + 2.2)], wall_top=FL1 + 2.3,
             found_top=FL1 - 0.15, roof=dict(type="shed", high="S", pitch=12, eave_oh=0.3, thick=0.1)),
    ],
    rooms=[
        dict(name="FP", rect=(-3.1, Y1, 1.1, FPY1), type="sitting"),
        dict(name="LR", rect=(-HX, 3.4, 0.8, Y1), type="living"),
        dict(name="ENTRY", rect=(0.8, 5.2, HX, Y1), type="hall"),
        dict(name="DR", rect=(-HX, Y0, 0.8, 3.4), type="dining"),
        dict(name="BR1", rect=(0.8, 1.6, HX, 5.2), type="bed"),
        dict(name="BAY", rect=(HX, 1.6, HX + 1.4, 5.2), type=None, no_light=True),
        dict(name="CL", rect=(0.8, Y0, HX, 1.6), type="closet"),
        dict(name="KIT", rect=(-HX, WY0, -0.4, Y0), type="kitchen", floor_mat="lino"),
        dict(name="BR2", rect=(-0.4, WY0, HX - 1.3, Y0), type="bed"),
        dict(name="RP", rect=(-HX, RPY0, -HX + g.ft(20), WY0), type="laundry"),
    ],
    doors=[
        dict(name="porch_front", at=(-1.0, FPY1), w=0.9, ext=True, glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="front", at=(-1.0, Y1), w=0.9, swing_into="LR", glazed=(0.2, 0.62, 0.8, 0.9)),
        dict(name="lr_entry", at=(0.8, 6.0), w=0.9, cased=True),
        dict(name="arch", at=(-1.5, 3.4), w=1.8, cased=True),
        dict(name="entry_br1", at=(2.2, 5.2), w=0.8, swing_into="BR1"),
        dict(name="br1_bay", at=(HX, 3.4), w=1.6, cased=True),
        dict(name="dr_cl", at=(0.8, 0.8), w=0.7, swing_into="DR"),
        dict(name="dr_kit", at=(-2.5, Y0), w=0.85, swing_into="KIT"),
        dict(name="kit_br2", at=(-0.4, -1.8), w=0.8, swing_into="BR2"),
        dict(name="kit_rp", at=(-2.5, WY0), w=0.85, swing_into="RP", glazed=(0.15, 0.55, 0.85, 0.9),
             panels=[(0.15, 0.07, 0.85, 0.16), (0.15, 0.2, 0.85, 0.3), (0.15, 0.34, 0.85, 0.44)]),
        dict(name="back", at=(-0.4, RPY0), w=0.85, ext=True, glazed=(0.15, 0.55, 0.85, 0.9),
             panels=[(0.15, 0.07, 0.85, 0.16), (0.15, 0.2, 0.85, 0.3), (0.15, 0.34, 0.85, 0.44)]),
    ],
    windows=[
        dict(at=(2.3, Y1), w=1.2, sill=0.75, h=1.45, kind="picture"), dict(at=(1.35, Y1), w=0.55, sill=0.75, h=1.45),
        dict(at=(3.25, Y1), w=0.55, sill=0.75, h=1.45),
        dict(at=(-HX, 5.6), w=0.8, sill=0.8, h=1.4), dict(at=(-HX, 1.7), w=0.8, sill=0.8, h=1.4),
        dict(at=(HX + 1.4, 3.4), w=1.0, sill=0.8, h=1.4), dict(at=(HX, 0.8), w=0.6, sill=1.0, h=1.1),
        dict(at=(-HX, -2.8), w=0.8, sill=1.05, h=1.1), dict(at=(HX - 1.3, -1.8), w=0.8, sill=0.8, h=1.4),
        *[dict(at=(x, FPY1), w=0.7, sill=0.8, h=1.1) for x in (-2.4, 0.4)],
        dict(at=(-3.1, Y1 + 0.9), w=0.6, sill=0.8, h=1.1), dict(at=(1.1, Y1 + 0.9), w=0.6, sill=0.8, h=1.1),
        *[dict(at=(x, RPY0), w=0.6, sill=0.8, h=1.0) for x in (-2.8, -1.8)],
    ],
    porches=[dict(rect=(-1.7, FPY1, -0.3, FPY1 + 1.0), z=FL1 - 0.13, post_top=FL1, posts=[], beam=False, skirt_mat="porch",
                  steps=dict(at=(-1.0, FPY1 + 1.0), dir=(0, 1), width=1.4, mat="porch")),
             dict(rect=(-1.1, RPY0 - 1.0, 0.3, RPY0), z=FL1 - 0.13, post_top=FL1, posts=[], beam=False, skirt_mat="porch",
                  steps=dict(at=(-0.4, RPY0 - 1.0), dir=(0, -1), width=1.2, mat="porch"))],
    # report: interior chimney on the front-gable ridge ~14' back; the living-room fireplace sits under it
    chimneys=[dict(at=(0.55, 4.3), w=0.5, d=0.6, z0=CEIL1, top=PLATE + 3.1)],
    fireplaces=[dict(room="LR", at=(0.75, 4.3), facing=(-1, 0))],
)
house = gh.House(b, spec)
house.build()

# chain-link fence along the east property line (report) with a walk gate; concrete walk + mailbox
gh.chainlink_fence(b, [(HX + 3.5, FPY1 + 5.0), (HX + 3.5, RPY0 - 4.0)], 1.2, gate=(0, 3.0, 1.0))
walk = b.part("walk-col")
walk.box((-1.7, FPY1 + 1.9, -0.02), (-0.3, FPY1 + 5.0, 0.03), "porch", sides="Z")
gh.mailbox(b, (-0.3 + 1.6, FPY1 + 5.3, 0.0), 0.0, "KOWALSKI", "402", "mail_black", "trim", "white_text")

b.finish(OUT)
