"""
P-HOUSE3 -- Brandt house (American foursquare), 118 Elevator St, Pruett.

Real example: John H. Donahue House, 98 Southern Ave, Dubuque, Dubuque County, IA (1917) --
HABS IA-159-R (remake/reference/P-HOUSE3/).  Data: main block 22' x 24', 2 storeys,
pyramidal (hipped) roof with a hipped dormer centred on the front (3-light fixed window),
offset interior brick chimney near the ridge, full-width one-storey front porch on 3 battered
frame columns set on stone-pattern concrete-block pedestals with a concrete balustrade,
enclosed back porch 22' x 8' (hipped, banks of 1/1 windows, 3-step open wooden stair to its
door), stone-pattern concrete-block foundation, 1/1 windows singly or paired, living-room
cottage window (fixed centre + flanking 1/1), wide boxed eaves.  Garage: 20' x 20', hipped roof
with broad overhangs, centred front dormer with a round-arched window, one triple-leaf garage
door and one conventional door.  Plan: the classic foursquare four-room layout (living room,
stair hall, dining room, kitchen; four rooms + bath upstairs off a small hall).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import math  # noqa: E402

import gbhouse as gh  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-house3")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-HOUSE3.glb")

b = g.Building("P-HOUSE3", TEX)
gh.std_house_materials(b, ["siding", "roof", "found", "trim", "floor", "plaster", "lino", "hextile", "porch", "door",
                           "furniture", "chimney", "iron"])

HX, HY = g.ft(22) / 2, g.ft(24) / 2
FL1 = 0.95
CEIL1 = FL1 + 2.75
FL2 = CEIL1 + 0.28
CEIL2 = FL2 + 2.6
PLATE = FL2 + 2.75
RP = -HY - g.ft(8)                      # rear enclosed porch south face
SILL = 0.72
GX0, GX1, GY0, GY1 = -HX - 3.8, -HX - 3.8 + g.ft(20), RP - 2.2 - g.ft(20), RP - 2.2

spec = dict(
    t_ext=0.15, t_int=0.1, era="modern",
    mats=dict(ext="siding", int="plaster", roof="roof", found="found", floor="floor", ceiling="plaster", trim="trim", door="door",
              fascia="trim", porch="porch", post="trim", furn="furniture"),
    blocks=[
        dict(name="main", rect=(-HX, -HY, HX, HY), floors=[(FL1, CEIL1), (FL2, CEIL2)], wall_top=PLATE, found_top=FL1 - 0.05,
             roof=dict(type="hip", pitch=30, eave_oh=0.6, thick=0.16)),
        dict(name="backporch", rect=(-HX, RP, HX, -HY), floors=[(FL1 - 0.2, FL1 + 2.2)], wall_top=FL1 + 2.3, found_top=FL1 - 0.25,
             roof=dict(type="hip", pitch=22, eave_oh=0.4, thick=0.12)),
        dict(name="garage", rect=(GX0, GY0, GX1, GY1), floors=[(0.1, 2.75)], wall_top=2.9, found_top=0.05,
             roof=dict(type="hip", pitch=30, eave_oh=0.7, thick=0.14)),
    ],
    rooms=[
        dict(name="LR", rect=(-HX, 0.3, 0.9, HY), type="living"),
        dict(name="ENTRY", rect=(0.9, 0.3, HX, HY), type="hall"),
        dict(name="DR", rect=(-HX, -HY, 0.3, 0.3), type="dining"),
        dict(name="KIT", rect=(0.3, -HY, HX, 0.3), type="kitchen", floor_mat="lino"),
        dict(name="BPORCH", rect=(-HX, RP, HX, -HY), type="laundry"),
        dict(name="HALL2", floor=1, rect=(-1.2, -0.6, HX, 0.6), type=None),
        dict(name="WELL", floor=1, rect=(2.2, 0.6, HX, HY), type=None, open_plan_to="HALL2"),   # stair arrives in the hall
        dict(name="BR1", floor=1, rect=(-HX, 0.6, 0.0, HY), type="bed"),
        dict(name="SEW", floor=1, rect=(0.0, 0.6, 2.2, HY), type="sitting"),
        dict(name="CL", floor=1, rect=(-HX, -0.6, -1.2, 0.6), type="closet"),
        dict(name="BR2", floor=1, rect=(-HX, -HY, 0.0, -0.6), type="bed"),
        dict(name="BATH", floor=1, rect=(0.0, -HY, 1.2, -0.6), type="bath", floor_mat="hextile"),
        dict(name="BR3", floor=1, rect=(1.2, -HY, HX, -1.2), type="bed"),
        # stair-head landing: the upstairs hall widens past the top riser (0.9 m clear)
        dict(name="HALL2B", floor=1, rect=(1.2, -1.2, HX, -0.6), type=None, no_light=True, open_plan_to="HALL2"),
        dict(name="GAR", rect=(GX0, GY0, GX1, GY1), type=None),
    ],
    doors=[
        dict(name="front", at=(1.6, HY), w=0.9, ext=True, glazed=(0.2, 0.55, 0.8, 0.88)),
        dict(name="entry_lr", at=(0.9, 1.6), w=1.3, cased=True),
        dict(name="lr_dr", at=(-1.7, 0.3), w=1.5, cased=True),
        dict(name="entry_kit", at=(1.6, 0.3), w=0.85, swing_into="KIT"),
        dict(name="dr_kit", at=(0.3, -1.8), w=0.85, swing_into="KIT"),
        dict(name="kit_porch", at=(1.8, -HY), w=0.85, swing_into="BPORCH", glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="porch_out", at=(2.3, RP), w=0.85, ext=True, glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="br1", floor=1, at=(-0.6, 0.6), w=0.8, swing_into="BR1"),
        dict(name="br2", floor=1, at=(-0.6, -0.6), w=0.8, swing_into="BR2"),
        dict(name="bath", floor=1, at=(0.6, -0.6), w=0.7, swing_into="BATH"),
        dict(name="br3", floor=1, at=(2.3, -1.2), w=0.8, swing_into="BR3"),
        dict(name="sew", floor=1, at=(1.1, 0.6), w=0.75, swing_into="SEW"),
        dict(name="closet", floor=1, at=(-2.3, 0.6), w=0.7, swing_into="BR1"),
        dict(name="garage_main", at=((GX0 + GX1) / 2 - 0.6, GY1), w=2.7, h=2.1, ext=True, leaves=2, out=True,
             panels=[(0.1, 0.55, 0.9, 0.9), (0.1, 0.1, 0.9, 0.5)]),
        dict(name="garage_man", at=(GX1 - 0.8, GY1), w=0.8, ext=True),
    ],
    windows=[
        # front: living-room cottage window (fixed centre + two 1/1) and the stair-hall window
        dict(at=(-1.3, HY), w=1.4, sill=SILL, h=1.5, kind="picture"),
        dict(at=(-2.45, HY), w=0.6, sill=SILL, h=1.5), dict(at=(-0.15, HY), w=0.6, sill=SILL, h=1.5),
        dict(at=(-1.6, HY), floor=1, w=0.8, sill=0.75, h=1.4), dict(at=(-0.6, HY), floor=1, w=0.8, sill=0.75, h=1.4),
        dict(at=(1.6, HY), floor=1, w=0.8, sill=0.75, h=1.4),
        dict(at=(-HX, 2.2), w=0.8, sill=SILL, h=1.5), dict(at=(-HX, -1.8), w=0.8, sill=SILL, h=1.5),
        dict(at=(-HX, -2.7), w=0.8, sill=SILL, h=1.5),
        dict(at=(HX, 2.0), w=0.8, sill=SILL + 0.6, h=1.0), dict(at=(HX, -1.8), w=0.8, sill=1.05, h=1.1),
        dict(at=(-HX, 2.2), floor=1, w=0.8, sill=0.75, h=1.4), dict(at=(-HX, -2.2), floor=1, w=0.8, sill=0.75, h=1.4),
        dict(at=(HX, 2.3), floor=1, w=0.8, sill=0.75, h=1.4), dict(at=(HX, -2.2), floor=1, w=0.8, sill=0.75, h=1.4),
        dict(at=(0.6, -HY), floor=1, w=0.6, sill=1.1, h=0.9), dict(at=(-1.8, -HY), floor=1, w=0.8, sill=0.75, h=1.4),
        # back porch: banks of 1/1 windows (data form)
        *[dict(at=(x, RP), w=0.7, sill=0.8, h=1.2) for x in (-2.6, -1.8, -1.0, -0.2)],
        dict(at=(-HX, -4.8), w=0.7, sill=0.8, h=1.2), dict(at=(HX, -4.8), w=0.7, sill=0.8, h=1.2),
        dict(at=(GX0, (GY0 + GY1) / 2), w=0.8, sill=1.1, h=0.8, cols=2),
    ],
    # straight flight up from a 0.9 m landing inside the front door (you step onto the first tread
    # from the landing, not from the railed side); its top lands in the upstairs hall
    stairs=[dict(start=(2.3, HY - 0.15 - 0.9), dir=(0, -1), width=0.95, n=15, run=0.19, floor=0, to_floor=1, rail_side="right")],
    rails=[dict(floor=1, pts=[(2.25, 0.65), (2.25, HY - 0.15 - 0.9)])],
    porches=[
        dict(rect=(-HX, HY, HX, HY + g.ft(8)), z=FL1 - 0.05, post_top=FL1 + 2.55,
             posts=[(-HX + 0.3, HY + g.ft(8) - 0.3), (0.35, HY + g.ft(8) - 0.3), (HX - 0.3, HY + g.ft(8) - 0.3)],
             post_style="battered", pedestal=0.95, pedestal_mat="found", rail_style="balustrade", rail_mat="found",
             rails=[[(-HX + 0.3, HY + g.ft(8) - 0.3), (0.35, HY + g.ft(8) - 0.3)], [(-HX + 0.3, HY + 0.1), (-HX + 0.3, HY + g.ft(8) - 0.3)],
                    [(2.25, HY + g.ft(8) - 0.3), (HX - 0.3, HY + g.ft(8) - 0.3)], [(HX - 0.3, HY + 0.1), (HX - 0.3, HY + g.ft(8) - 0.3)]],
             steps=dict(at=(1.3, HY + g.ft(8)), dir=(0, 1), width=1.6, mat="found"),
             roof=dict(type="hip", z=FL1 + 2.75, pitch=20, oh=0.45), ceiling_light=True, skirt_mat="found"),
        dict(rect=(1.8, RP - 0.9, 2.8, RP), z=FL1 - 0.25, post_top=FL1, posts=[], beam=False, skirt=False,
             steps=dict(at=(2.3, RP - 0.9), dir=(0, -1), width=1.0)),
    ],
    chimneys=[dict(at=(-1.3, -0.9), w=0.5, d=0.5, z0=CEIL2, top=PLATE + 2.6)],
)
house = gh.House(b, spec)
house.build()

# hipped dormer centred on the front (3-light fixed window) and the garage's arched-window dormer
dm = b.part("dormers-col")
tn = math.tan(math.radians(30))
for (cx, face_y, base_z, w, tag) in ((0.0, HY - 0.25, PLATE + 0.15, 1.6, "house"), ((GX0 + GX1) / 2, GY1 + 0.1, 3.05, 1.3, "garage")):
    depth = 1.4
    dm.box((cx - w / 2, face_y - depth, base_z), (cx - w / 2 + 0.1, face_y, base_z + 0.95), "siding")
    dm.box((cx + w / 2 - 0.1, face_y - depth, base_z), (cx + w / 2, face_y, base_z + 0.95), "siding")
    fr = g.wall(dm, (cx + w / 2, face_y), (cx - w / 2, face_y), base_z, base_z + 0.95, 0.08,
                [dict(off=0.18, w=w - 0.36, sill=base_z + 0.2, head=base_z + 0.75)], "siding", "plaster")
    g.window(b, "windows", fr, 0.18, w - 0.36, base_z + 0.2, base_z + 0.75, 0.08, sash_rows=1, sash_cols=3 if tag == "house" else 2,
             glass_name="glass", casing=0.05)
    gh.hip_roof(dm, cx - w / 2, cx + w / 2, face_y - depth, face_y, base_z + 0.95, 25, 0.2, 0.08, "roof", "trim", "trim")
# keystone + arch hint over the garage dormer window
dm.box(((GX0 + GX1) / 2 - 0.06, GY1 + 0.02, 3.05 + 0.72), ((GX0 + GX1) / 2 + 0.06, GY1 + 0.12, 3.05 + 0.88), "trim")
gh.car(b, ((GX0 + GX1) / 2 - 0.6, (GY0 + GY1) / 2, 0.1), 0.0)
drv = b.part("driveway-col")
drv.box((-HX - 3.4, GY1, -0.02), (-HX - 0.6, HY + 7.0, 0.03), "found", sides="Z")      # to the garage doors
gh.mailbox(b, (-HX - 3.9, HY + 7.3, 0.0), 0.0, "BRANDT", "118", "mail_black", "trim", "white_text")
walk = b.part("walk-col")
walk.box((0.6, HY + g.ft(8) + 0.9, -0.02), (2.0, HY + 7.0, 0.03), "found", sides="Z")

b.finish(OUT)
