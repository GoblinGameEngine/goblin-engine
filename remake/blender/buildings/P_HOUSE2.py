"""
P-HOUSE2 -- Lindqvist house (bungalow), 305 Depot St, Pruett.

Real example: "Representative Bungalow", 1506 Thompson Ave, Des Moines, Polk County, IA
(c.1920) -- HABS IA-91 (remake/reference/P-HOUSE2/).  Data form: 1 1/2-storey, rectangular,
large simple gable with the gable end to the street, projecting enclosed entrance porch with
its own gable, wide eaves on straight brackets, very narrow clapboard with corner boards,
brick foundation; photo: detached single-car garage at the end of the drive.
The data form records no plan ("interior: unknown"), so the plan follows the research
template research/building_catalog/residential/bungalow_craftsman.md (living room across the
front, dining + kitchen on one side, two bedrooms + bath on the other, attic bedroom reached by
an enclosed stair).  Width/depth scaled from the photo (28' x 42').
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import gbhouse as gh  # noqa: E402
import gblib as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TEX = os.path.join(ROOT, "remake", "textures", "p-house2")
OUT = os.path.join(ROOT, "godot_project", "remake", "buildings", "P-HOUSE2.glb")

b = g.Building("P-HOUSE2", TEX)
gh.std_house_materials(b, ["siding", "roof", "found", "trim", "floor", "plaster", "lino", "hextile", "porch", "door",
                           "furniture", "chimney", "iron"])

FL1 = 0.75                               # brick foundation, several steps up (photo)
CEIL1 = FL1 + 2.6
FL2 = CEIL1 + 0.25
PLATE = FL1 + 3.3
HX, HY = 4.25, 6.4                       # 28' x 42'
PX0, PX1, PY1 = -3.0, 1.0, HY + 2.5      # enclosed entrance porch (projects 8')
SILL = 0.8

spec = dict(
    t_ext=0.15, t_int=0.1, era="modern",
    mats=dict(ext="siding", int="plaster", roof="roof", found="found", floor="floor", ceiling="plaster", trim="trim", door="door",
              fascia="trim", porch="porch", post="trim", furn="furniture"),
    blocks=[
        dict(name="main", rect=(-HX, -HY, HX, HY), floors=[(FL1, CEIL1), (FL2, FL2 + 2.3)], wall_top=PLATE, found_top=FL1 - 0.05,
             roof=dict(type="gable", ridge="y", pitch=42, eave_oh=0.7, rake_oh=0.6, thick=0.16), habitable_attic=True),
        dict(name="porch", rect=(PX0, HY, PX1, PY1), floors=[(FL1, FL1 + 2.4)], wall_top=FL1 + 2.55, found_top=FL1 - 0.05,
             roof=dict(type="gable", ridge="y", pitch=42, eave_oh=0.6, rake_oh=0.55, thick=0.14)),
        dict(name="garage", rect=(-7.45, -HY - 9.0, -3.75, -HY - 3.2), floors=[(0.1, 2.4)], wall_top=2.45, found_top=0.05,
             roof=dict(type="gable", ridge="y", pitch=35, eave_oh=0.4, rake_oh=0.3, thick=0.12)),
    ],
    rooms=[
        dict(name="ENC", rect=(PX0, HY, PX1, PY1), type="sitting"),
        dict(name="LR", rect=(-HX, 2.6, HX, HY), type="living"),
        dict(name="DR", rect=(-HX, -1.8, -0.3, 2.6), type="dining"),
        dict(name="STAIR", rect=(-0.3, -1.8, 0.9, 2.6), type=None, no_light=False),
        dict(name="BR1", rect=(0.9, 0.2, HX, 2.6), type="bed"),
        dict(name="BATH", rect=(0.9, -1.8, 2.6, 0.2), type="bath", floor_mat="hextile"),
        dict(name="CL1", rect=(2.6, -1.8, HX, 0.2), type="closet"),
        dict(name="KIT", rect=(-HX, -HY, -0.3, -1.8), type="kitchen", floor_mat="lino"),
        dict(name="BR2", rect=(-0.3, -HY, HX, -1.8), type="bed"),
        dict(name="ATTIC", floor=1, rect=(-HX, -HY, HX, HY), type="bed"),
        dict(name="GAR", rect=(-7.45, -HY - 9.0, -3.75, -HY - 3.2), type=None),
    ],
    # the stair-foot landing (0.7 m) is shared by 3 doors: DR and bath leaves swing away from it,
    # both kept south of the first riser
    doors=[
        dict(name="front", at=(-1.0, PY1), w=0.9, ext=True, glazed=(0.15, 0.45, 0.85, 0.9)),
        dict(name="enc_lr", at=(-1.0, HY), w=0.9, swing_into="LR", glazed=(0.15, 0.35, 0.85, 0.9)),
        dict(name="lr_dr", at=(-2.3, 2.6), w=1.5, cased=True),
        dict(name="br1", at=(2.6, 2.6), w=0.8, swing_into="BR1"),
        dict(name="dr_stair", at=(-0.3, -1.36), w=0.7, swing_into="DR"),
        dict(name="bath", at=(0.9, -1.36), w=0.7, swing_into="BATH"),
        dict(name="cl1", at=(3.4, 0.2), w=0.7, swing_into="BR1"),
        dict(name="dr_kit", at=(-2.0, -1.8), w=0.85, swing_into="KIT"),
        dict(name="br2", at=(0.3, -1.8), w=0.8, swing_into="BR2"),
        dict(name="back", at=(-2.5, -HY), w=0.85, ext=True, glazed=(0.15, 0.5, 0.85, 0.9)),
        dict(name="garage_side", at=(-3.75, -HY - 5.0), w=0.8, ext=True),
        dict(name="garage_main", at=(-5.6, -HY - 3.2), w=2.6, h=2.1, ext=True, leaves=2, out=True,
             panels=[(0.1, 0.55, 0.9, 0.9), (0.1, 0.1, 0.9, 0.5)]),
    ],
    windows=[
        *[dict(at=(x, PY1), w=0.75, sill=0.9, h=1.2, cols=1) for x in (-2.4, 0.4)],
        *[dict(at=(x, y), w=0.75, sill=0.9, h=1.2, cols=1) for (x, y) in ((PX0, 7.5), (PX1, 7.5))],
        *[dict(at=(x, HY), w=0.9, sill=SILL, h=1.4, cols=1) for x in (2.0, 3.1)],
        dict(at=(-HX, 4.5), w=0.9, sill=SILL, h=1.4, cols=1), dict(at=(HX, 4.5), w=0.9, sill=SILL, h=1.4, cols=1),
        dict(at=(-HX, 0.4), w=0.9, sill=SILL, h=1.4, cols=1), dict(at=(-HX, -4.0), w=0.9, sill=1.1, h=1.1, cols=1),
        dict(at=(HX, 1.4), w=0.9, sill=SILL, h=1.4, cols=1), dict(at=(HX, -0.8), w=0.6, sill=1.3, h=0.8, kind="glassblock"),
        dict(at=(HX, -4.0), w=0.9, sill=SILL, h=1.4, cols=1), dict(at=(2.0, -HY), w=0.9, sill=SILL, h=1.4, cols=1),
        dict(at=(-1.2, -HY), w=0.9, sill=1.1, h=1.1, cols=1),
        # attic gable windows front + back (pair)
        *[dict(at=(x, y), floor=1, w=0.7, sill=0.6, h=1.1, cols=1) for x in (-0.55, 0.55) for y in (HY, -HY)],
        dict(at=(-5.6, -HY - 9.0), w=0.8, sill=1.1, h=0.8, cols=2),
    ],
    stairs=[dict(start=(0.85, -1.1), dir=(0, 1), width=1.05, n=14, run=0.21, floor=0, to_floor=1, rail=False)],   # boxed between walls
    rails=[dict(floor=1, pts=[(-0.25, -1.1), (-0.25, 1.85)])],
    porches=[dict(rect=(PX0 + 1.2, PY1, PX0 + 2.8, PY1 + 1.3), z=FL1 - 0.03, post_top=FL1, posts=[], beam=False, skirt_mat="found",
                  steps=dict(at=(-1.0, PY1 + 1.3), dir=(0, 1), width=1.4, mat="found")),
             dict(rect=(-3.2, -HY - 1.0, -1.8, -HY), z=FL1 - 0.03, post_top=FL1, posts=[], beam=False, skirt_mat="found",
                  steps=dict(at=(-2.5, -HY - 1.0), dir=(0, -1), width=1.1, mat="found"))],
    chimneys=[dict(at=(-HX - 0.3, 4.5), w=0.6, d=0.9, z0=0.0, top=PLATE + 3.0)],
    fireplaces=[dict(room="LR", at=(-HX + 0.15, 4.5), facing=(1, 0))],
)
house = gh.House(b, spec)
house.build()

# straight eave brackets under the wide overhangs (data form) -- knee braces along both eaves
br = b.part("brackets")
import math  # noqa: E402
tn42 = math.tan(math.radians(42))
for y in (-5.8, -3.0, -0.2, 2.6, 5.4):
    for sx in (-1, 1):
        x = sx * HX
        # horizontal arm out to 0.55 m under the soffit + a diagonal-ish strut down to the wall
        z_arm = PLATE - 0.55 * tn42 - 0.16 / math.cos(math.radians(42)) - 0.02
        br.box((min(x, x + sx * 0.55), y - 0.05, z_arm - 0.1), (max(x, x + sx * 0.55), y + 0.05, z_arm), "trim")
        br.box((min(x, x + sx * 0.12), y - 0.05, z_arm - 0.55), (max(x, x + sx * 0.12), y + 0.05, z_arm), "trim")
# car in the garage, driveway, mailbox
gh.car(b, (-5.6, -HY - 6.1, 0.1), 0.0)
drv = b.part("driveway-col")
drv.box((-7.0, -HY - 3.2, -0.02), (-5.0, HY + 6.0, 0.03), "found", sides="Z")          # concrete ribbon drive
gh.mailbox(b, (-7.6, HY + 6.3, 0.0), 0.0, "LINDQVIST", "305", "mail_black", "trim", "white_text")
walk = b.part("walk-col")
walk.box((-1.7, PY1 + 1.3, -0.02), (-0.3, HY + 6.0, 0.03), "found", sides="Z")

b.finish(OUT)
