"""
farm.py -- farmstead buildings (records FARM-NN-barn / -silo / -shed; farmhouses use house.py).

  barn   bank_barn | gambrel_dairy | english_three_bay | round_barn | pole_barn | tobacco | crib_barn:
         a ground floor of stalls / stanchions / a threshing floor behind big hinged doors, a hay
         loft reached by a climbable ladder, the farm name painted on the gable end.
  silo   concrete_stave | brick | tile | harvestore_blue | wood_stave: a cylinder with a dome or cone
         roof, a walk-in door at the base and a climbable chute ladder up the side.
  shed   pole_shed | quonset | frame_machine_shed | corn_crib: an implement shed with a tractor and a
         wagon in it, doors you can open.
Each building sits at its own lot origin (the farmstead layout places them on the map).
"""
import math

from common import (dget, Palette, WALL_TEX, clamp, hexcol, lib_building, rng, std_materials, darken, g, FONT_SANS, ft)
import gbhouse as gh
import gbfurn as fu
import shopfit


def materials(b, tr):
    pal = Palette(b)
    col = tr.get("colors", {}) or {}
    cond = tr.get("condition", "kept")
    wear = {"kept": 1.0, "worn": 0.85, "shabby": 0.72, "boarded": 0.68}.get(cond, 1.0)
    body = col.get("body") or "#8a2a1e"
    std_materials(pal, trim=col.get("trim") or "#e8e2d4", door=col.get("accent") or body)
    shopfit.shop_materials(pal)
    walls = tr.get("walls") or tr.get("upper_walls") or "board_and_batten"
    if walls in ("board_and_batten", "drop_siding", "clapboard", "vertical_board"):
        pal.surf("ext", "barn_board", darken(hexcol(body), wear), rough=0.85)
    elif walls in ("metal", "stone_and_metal"):
        pal.surf("ext", "corrugated_rusty" if cond in ("shabby",) else "corrugated", rough=0.5, metal=0.6)
    elif walls == "stone":
        pal.surf("ext", "fieldstone", rough=0.9)
    elif walls == "brick":
        pal.surf("ext", "brick_red", rough=0.9)
    else:
        pal.surf("ext", WALL_TEX.get(walls, "barn_board"), darken(hexcol(body), wear), rough=0.85)
    lower = tr.get("lower_walls")
    if lower == "brick":
        pal.surf("lower", "brick_red", rough=0.9)
    elif lower in ("stone", "fieldstone"):
        pal.surf("lower", "fieldstone", rough=0.9)
    else:
        pal.surf("lower", "concrete", rough=0.9)
    rmat = dget(tr, "roof").get("material", "metal")
    pal.surf("roof", "metal_roof" if rmat == "metal" else ("roof_wood" if rmat == "wood_shingle" else "roof_asphalt"),
             darken(hexcol(col.get("roof") or "#7a7470"), wear), rough=0.6, metal=0.3 if rmat == "metal" else 0.0)
    pal.surf("floor", "concrete", rough=0.9)
    pal.surf("wood", "weathered_board", rough=0.9)
    pal.surf("plaster", "weathered_board", rough=0.9)
    pal.surf("found", "concrete", rough=0.9)
    pal.solid("roof_under", (0.35, 0.3, 0.25), rough=0.9)
    pal.solid("hay", (0.82, 0.7, 0.38), rough=0.95)
    pal.solid("tractor", (0.75, 0.12, 0.08) if tr.get("tractor") != "green" else (0.15, 0.4, 0.15), rough=0.5)
    pal.solid("silo_glass", (0.12, 0.2, 0.42), rough=0.2, metal=0.5)
    pal.solid("letters_white", (0.95, 0.94, 0.9), rough=0.6)
    return pal


def ladder(b, name, x, y, z0, z1, axis="x", face=1.0):
    """A climbable ladder (a 'ladder_*' mesh becomes a climb zone in Godot)."""
    lad = b.part(f"ladder_{name}")
    for s in (-0.22, 0.22):
        if axis == "x":
            lad.box((x + s - 0.025, y - 0.03, z0), (x + s + 0.025, y + 0.03, z1), "iron")
        else:
            lad.box((x - 0.03, y + s - 0.025, z0), (x + 0.03, y + s + 0.025, z1), "iron")
    z = z0 + 0.3
    while z < z1 - 0.1:
        if axis == "x":
            lad.box((x - 0.22, y - 0.015, z), (x + 0.22, y + 0.015, z + 0.03), "iron")
        else:
            lad.box((x - 0.015, y - 0.22, z), (x + 0.015, y + 0.22, z + 0.03), "iron")
        z += 0.3


def tractor(p, pos, yaw):
    f = fu.F(pos, yaw)
    p.obox(f, (-0.5, -1.2, 0.6), (0.5, 0.8, 1.3), "tractor")
    p.obox(f, (-0.35, 0.8, 0.7), (0.35, 1.7, 1.2), "tractor")
    p.obox(f, (-0.3, -1.3, 1.3), (0.3, -0.8, 2.1), "iron")
    for (x, y, r) in ((-0.85, -0.9, 0.75), (0.85, -0.9, 0.75), (-0.6, 1.3, 0.4), (0.6, 1.3, 0.4)):
        p.obox(f, (x - 0.18, y - r, 0.0), (x + 0.18, y + r, r * 2), "tire")


def wagon(p, pos, yaw):
    f = fu.F(pos, yaw)
    p.obox(f, (-1.0, -2.0, 0.7), (1.0, 2.0, 0.8), "wood")
    for s in (-1, 1):
        p.obox(f, (s * 1.0 - 0.04, -2.0, 0.8), (s * 1.0 + 0.04, 2.0, 1.4), "wood")
    for (x, y) in ((-0.9, -1.4), (0.9, -1.4), (-0.9, 1.4), (0.9, 1.4)):
        p.obox(f, (x - 0.08, y - 0.4, 0.0), (x + 0.08, y + 0.4, 0.8), "tire")


def stall_row(p, x0, x1, y, fz, depth=2.4, pitch=1.6, mat="wood"):
    """Stall partitions along x at y (stalls open toward +y), a feed trough at the back."""
    x = x0
    while x <= x1 + 0.01:
        p.box((x - 0.04, y, fz), (x + 0.04, y + depth, fz + 1.4), mat)
        x += pitch
    p.box((x0, y - 0.1, fz), (x1, y + 0.4, fz + 0.6), mat)


def cupola(b, cx, cy, z, s=1.3, name="cupola"):
    """A louvred ventilator cupola with a pyramid cap, standing on the ridge at z."""
    p = b.part(name)
    p.box((cx - s / 2, cy - s / 2, z - 0.3), (cx + s / 2, cy + s / 2, z + s), "trim")
    for k in range(4):                                                     # louvre shadow bands
        zz = z + 0.2 + k * 0.22
        p.box((cx - s / 2 - 0.01, cy - s / 2 - 0.01, zz), (cx + s / 2 + 0.01, cy + s / 2 + 0.01, zz + 0.06), "roof_under")
    g.pyramid_roof(p, cx, cy, s / 2 + 0.15, z + s, z + s + 0.9, 0.0, "roof", "roof_under")


def ridge_height(half, pitch, gambrel):
    """Rise of the roof above the wall top for a gable (pitch) or gambrel (60 deg lower slope over
    45% of the half-span, 25 deg above) roof."""
    if gambrel:
        return 0.45 * half * math.tan(math.radians(60)) + 0.55 * half * math.tan(math.radians(25))
    return half * math.tan(math.radians(pitch))


def lean_to(b, side, span, x0, x1, y0, y1, depth=3.6, h_in=3.0, h_out=2.4):
    """An open-fronted shed-roof lean-to on posts along one side of the barn (side '+x', '-x' or
    '-y'), between span = (a, b) along that wall; its back is the barn wall."""
    a, c = span
    if c - a < 2.5:
        return
    p = b.part("lean_to-col")
    v = b.part("lean_to_roof")
    n = max(1, int((c - a) / 3.0))
    for k in range(n + 1):
        u = a + (c - a) * k / n
        if side == "+x":
            p.box((x1 + depth - 0.25, u - 0.1, 0.0), (x1 + depth - 0.05, u + 0.1, h_out), "wood")
        elif side == "-x":
            p.box((x0 - depth + 0.05, u - 0.1, 0.0), (x0 - depth + 0.25, u + 0.1, h_out), "wood")
        else:
            p.box((u - 0.1, y0 - depth + 0.05, 0.0), (u + 0.1, y0 - depth + 0.25, h_out), "wood")
    if side == "+x":
        top = [(x1, a, h_in), (x1, c, h_in), (x1 + depth + 0.3, c, h_out - 0.1), (x1 + depth + 0.3, a, h_out - 0.1)]
    elif side == "-x":
        top = [(x0 - depth - 0.3, a, h_out - 0.1), (x0 - depth - 0.3, c, h_out - 0.1), (x0, c, h_in), (x0, a, h_in)]
    else:
        top = [(a, y0, h_in), (a, y0 - depth - 0.3, h_out - 0.1), (c, y0 - depth - 0.3, h_out - 0.1), (c, y0, h_in)]
    v.face(top, "roof")
    v.face([(q[0], q[1], q[2] - 0.08) for q in reversed(top)], "roof_under")


LEAN_SIDE = {"east": "+x", "right": "+x", "west": "-x", "left": "-x", "south": "-y", "north": "-y", "rear": "-y", "back": "-y"}


def build_round_barn(rec, tr, rnd):
    """A true round barn: a low cylindrical wall, a bowed (two-pitch) conical roof to a ventilator
    cupola at the peak, a ring of small windows and a big doorway on the front with its X-braced
    leaves swung open."""
    b = lib_building(rec["id"])
    pal = materials(b, tr)
    r = clamp(ft(tr.get("w_ft") or 60) / 2, 6.0, 12.0)
    conical = dget(tr, "roof").get("type") in ("pyramid", "conical", "cone")
    # a low drum under a tall bowed roof; cone-roofed barns put most of their height in the drum
    wall_h = clamp(ft(tr.get("height_ft") or 30) * 0.5, 5.0, 9.0) if conical else 5.0
    n = 24
    door_w, door_h = 3.6, 3.4
    p = b.part("round_barn-col")
    P = lambda a, rr, z: (rr * math.cos(a), rr * math.sin(a), z)
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        gap = abs(math.atan2(math.sin(am - math.pi / 2), math.cos(am - math.pi / 2))) < (door_w / 2) / r
        zb = door_h if gap else 0.0
        p.face([P(a0, r, zb), P(a1, r, zb), P(a1, r, wall_h), P(a0, r, wall_h)], "ext")
        p.face([P(a1, r - 0.2, zb), P(a0, r - 0.2, zb), P(a0, r - 0.2, wall_h), P(a1, r - 0.2, wall_h)], "wood")
        if gap:
            p.face([P(a1, r, zb), P(a0, r, zb), P(a0, r - 0.2, zb), P(a1, r - 0.2, zb)], "wood")
        elif i % 2 == 0:                                                   # ring(s) of small square windows
            w = b.part("round_windows")
            wx, wy, _ = P(am, r + 0.02, 0.0)
            tx, ty = -math.sin(am), math.cos(am)
            for zw in ((2.3, wall_h - 2.2) if wall_h > 6.5 else (2.3,)):
                w.face([(wx - tx * 0.35, wy - ty * 0.35, zw), (wx + tx * 0.35, wy + ty * 0.35, zw),
                        (wx + tx * 0.35, wy + ty * 0.35, zw + 0.7), (wx - tx * 0.35, wy - ty * 0.35, zw + 0.7)], "silo_glass")
    p.cylinder((0.0, 0.0), r - 0.1, -0.05, 0.1, "floor", n=n)
    # the roof: a bowed two-pitch dome (the default), or a straight cone at the record's pitch
    # (roof type pyramid / conical); very large barns (80 ft+) carry a clerestory drum on the
    # cone with a band of windows, then a smaller cone to the lantern
    rf = b.part("round_roof-col")
    ra = 1.0
    rings = []
    if conical:
        tp = math.tan(math.radians(clamp(dget(tr, "roof").get("pitch_deg") or 30, 15, 50)))
        z0 = wall_h - 0.2
        if ft(tr.get("w_ft") or 60) >= ft(80):
            rc = r * 0.38
            z1 = z0 + (r + 0.5 - rc) * tp
            rings.append((r + 0.5, z0, rc, z1))
            drum = b.part("round_clerestory-col")
            drum.cylinder((0.0, 0.0), rc, z1 - 0.1, z1 + 2.2, "trim", n=n, caps=False)
            for i in range(0, n, 2):                                        # band of small windows
                a0, a1 = 2 * math.pi * (i + 0.25) / n, 2 * math.pi * (i + 0.75) / n
                drum.face([P(a0, rc + 0.02, z1 + 0.7), P(a1, rc + 0.02, z1 + 0.7), P(a1, rc + 0.02, z1 + 1.5), P(a0, rc + 0.02, z1 + 1.5)],
                          "silo_glass")
            z2 = z1 + 2.2
            za = z2 + (rc + 0.3 - ra) * tp
            rings.append((rc + 0.3, z2, ra, za))
        else:
            za = z0 + (r + 0.5 - ra) * tp
            rings.append((r + 0.5, z0, ra, za))
    else:
        rk = r * 0.6
        zk = wall_h + (r + 0.5 - rk) * math.tan(math.radians(60)) * 0.7
        za = zk + (rk - ra) * math.tan(math.radians(25))
        rings = [(r + 0.5, wall_h - 0.2, rk, zk), (rk, zk, ra, za)]
    for (ro0, z0, ro1, z1) in rings:
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            rf.face([P(a0, ro0, z0), P(a1, ro0, z0), P(a1, ro1, z1), P(a0, ro1, z1)], "roof")
            rf.face([P(a1, ro0 - 0.15, z0 - 0.12), P(a0, ro0 - 0.15, z0 - 0.12), P(a0, ro1 - 0.15, z1 - 0.12), P(a1, ro1 - 0.15, z1 - 0.12)],
                    "roof_under")
    # a ring of small gabled dormers on the lower roof (the records carry these only in the brief)
    if tr.get("dormers") or "dormer" in (rec.get("brief") or "").lower():
        ro0, z0, ro1, z1 = rings[0]
        dm = b.part("round_dormers")
        for k in range(8):
            am = math.pi / 2 + math.pi / 8 + k * math.pi / 4                  # clear of the door (+y)
            rr = ro0 - (ro0 - ro1) * 0.35
            zr = z0 + (z1 - z0) * 0.35
            cx, cy = rr * math.cos(am), rr * math.sin(am)
            tx, ty = -math.sin(am), math.cos(am)
            nx, ny = math.cos(am), math.sin(am)
            fb = [(cx + nx * 0.35 + tx * s * 0.5, cy + ny * 0.35 + ty * s * 0.5) for s in (-1, 1)]
            dm.face([(fb[0][0], fb[0][1], zr - 0.2), (fb[1][0], fb[1][1], zr - 0.2), (fb[1][0], fb[1][1], zr + 0.6), (fb[0][0], fb[0][1], zr + 0.6)], "trim")
            dm.face([(fb[1][0], fb[1][1], zr + 0.6), (fb[0][0], fb[0][1], zr + 0.6), (cx + nx * 0.35, cy + ny * 0.35, zr + 1.0)], "trim")
            dm.face([(cx + nx * 0.36 + tx * 0.2, cy + ny * 0.36 + ty * 0.2, zr), (cx + nx * 0.36 - tx * 0.2, cy + ny * 0.36 - ty * 0.2, zr),
                     (cx + nx * 0.36 - tx * 0.2, cy + ny * 0.36 - ty * 0.2, zr + 0.45), (cx + nx * 0.36 + tx * 0.2, cy + ny * 0.36 + ty * 0.2, zr + 0.45)],
                    "roof_under")                                          # louvred vent
            for s in (-1, 1):                                              # little gable roof
                e = (cx + nx * 0.4 + tx * s * 0.6, cy + ny * 0.4 + ty * s * 0.6)
                dm.face([(cx + nx * 0.4, cy + ny * 0.4, zr + 1.05), (e[0], e[1], zr + 0.55), (e[0] - nx * 1.0, e[1] - ny * 1.0, zr + 0.85),
                         (cx - nx * 0.6, cy - ny * 0.6, zr + 1.1)][::s], "roof")
    # round ventilator cupola / lantern at the peak
    cp = b.part("round_cupola")
    cp.cylinder((0.0, 0.0), ra + 0.05, za - 0.1, za + 0.9, "trim", n=16)
    cp.cylinder((0.0, 0.0), ra + 0.25, za + 0.9, za + 1.6, "roof", n=16, r1=0.05)
    # the pair of X-braced leaves, swung open against the wall either side of the doorway
    lv = b.part("round_doors")
    for s in (-1, 1):
        x_in = s * door_w / 2
        x_out = s * (door_w / 2 + door_w / 2)
        yy = math.sqrt(max(0.0, r * r - x_out * x_out)) + 0.15
        lv.box((min(x_in, x_out), yy, 0.05), (max(x_in, x_out), yy + 0.06, door_h - 0.05), "trim")
        for (za_, zb_) in ((0.2, door_h - 0.2),):
            lv.face([(x_in, yy + 0.07, za_), (x_out, yy + 0.07, zb_), (x_out, yy + 0.07, zb_ - 0.12), (x_in, yy + 0.07, za_ + 0.12)], "roof_under")
            lv.face([(x_out, yy + 0.07, za_), (x_in, yy + 0.07, zb_), (x_in, yy + 0.07, zb_ - 0.12), (x_out, yy + 0.07, za_ + 0.12)], "roof_under")
    b.empty("light_barn", (0.0, 0.0, 3.0))
    return b


# ------------------------------------------------------------------ barn
def build_barn(rec, tr, rnd):
    b = lib_building(rec["id"])
    materials(b, tr)
    names = rec.get("names") or {}
    typ = tr.get("type", "english_three_bay")
    if typ == "round_barn":
        return build_round_barn(rec, tr, rnd)
    W = clamp(ft(tr.get("w_ft") or 40), 8.0, 24.0)
    D = clamp(ft(tr.get("d_ft") or 30), 7.0, 26.0)
    H = clamp(ft(tr.get("height_ft") or 30), 7.0, 14.0)
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    FL = 0.1
    loft = 3.2
    gambrel = typ in ("gambrel_dairy",) or dget(tr, "roof").get("type") == "gambrel"
    # English / bank barns take their big doors on the long (eave) side; dairy and pole barns on a
    # gable end.  The front (+y) is where the doors are, so the ridge runs along x or y to match.
    ridge = "x" if typ in ("english_three_bay", "bank_barn", "crib_barn", "tobacco") else "y"
    wall_top = loft + 2.2 if not gambrel else loft + 0.9
    if typ == "bank_barn" and not gambrel:
        wall_top = loft + 4.2        # the upper (threshing) floor is a full storey: its ramp doors need the height
    pitch = dget(tr, "roof").get("pitch_deg") or 42
    if typ == "pole_barn":
        wall_top, pitch = 4.2, 18
    roof = dict(type="gambrel" if gambrel else "gable", ridge=ridge, pitch=25 if gambrel else pitch, pitch_lower=60, knee_frac=0.45,
                eave_oh=0.4, rake_oh=0.3, thick=0.15)
    floors = [(FL, loft - 0.25)] if typ == "pole_barn" else [(FL, loft - 0.25), (loft, wall_top + 3.0)]
    # doors: big pair centred on the front (the drive / threshing floor), man doors on the sides
    cx = 0.0
    doors = [dict(name="big_front", at=(cx, y1), w=min(3.6, W * 0.35), h=min(3.4, loft - 0.4), ext=True, leaves=2, out=True,
                  panels=[(0.08, 0.08, 0.92, 0.92)]),
             dict(name="big_back", at=(cx, y0), w=min(3.2, W * 0.3), h=min(3.0, loft - 0.5), ext=True, leaves=2, out=True,
                  panels=[(0.08, 0.08, 0.92, 0.92)]),
             dict(name="side_e", at=(x1, y0 + D * 0.3), w=0.95, ext=True, out=True),
             dict(name="side_w", at=(x0, y1 - D * 0.3), w=0.95, ext=True, out=True)]
    if typ == "bank_barn":
        # the earth bank buries the back of the ground floor: the rear big doors open onto the
        # ramp top at loft level instead (a ground-level door there opened into a dead end under the ramp,
        # and the ramp top met a blank wall)
        doors[1].update(floor=1, h=min(3.4, wall_top - loft - 0.3))
    rooms = [dict(name="FLOOR", rect=(x0, y0, x1, y1), type=None, no_furnish=True)]
    if typ != "pole_barn":
        rooms.append(dict(name="LOFT", floor=1, rect=(x0, y0, x1, y1), type=None, no_furnish=True))
    windows = [dict(at=(x, y0), w=0.7, sill=1.2, h=0.7, kind="dh", cols=2) for x in (x0 + 1.5, x1 - 1.5)]
    windows += [dict(at=(x0, y), w=0.7, sill=1.2, h=0.7, kind="dh", cols=2) for y in (y0 + 1.5,)]
    spec = dict(t_ext=0.1, t_int=0.1, era="old",
                mats=dict(ext="ext", int="wood", roof="roof", roof_under="roof_under", found="lower", floor="floor",
                          ceiling="wood", trim="trim", door="ext", fascia="trim", porch="concrete", post="wood", furn="wood"),
                blocks=[dict(name="barn", rect=(x0, y0, x1, y1), floors=floors, wall_top=wall_top, found_top=FL,
                             roof=roof, habitable_attic=True)],
                rooms=rooms, doors=doors, windows=windows, stairs=[], rails=[], porches=[], chimneys=[], fireplaces=[])
    gh.House(b, spec).build()
    p = b.part("barn_fittings-col")
    # ground floor: stalls down one side (or stanchion rows for dairy), open drive in the middle
    if typ in ("gambrel_dairy",):
        for yy in (y0 + 1.2, y1 - 3.8):
            stall_row(p, x0 + 1.0, x1 - 1.0, yy, FL, depth=1.8, pitch=1.1)
    elif typ != "pole_barn":
        stall_row(p, x0 + 0.6, -2.4, y0 + 0.4, FL)
        stall_row(p, 2.4, x1 - 0.6, y0 + 0.4, FL)
    # loft floor opening + ladder to it; hay bales stacked in the loft
    if typ != "pole_barn":
        lx, ly = x0 + 1.2, 0.0
        ladder(b, "loft", lx, ly, FL, loft + 1.1, axis="y")
        for k in range(12):
            bx = x0 + 2.5 + (k % 6) * 1.1
            by = y0 + 1.0 + (k // 6) * 0.6
            if bx < x1 - 1.0:
                p.box((bx, by, loft), (bx + 1.0, by + 0.5, loft + 0.45), "hay")
        # hay door + hay-hood (track beam) on the front gable
        p.box((-1.0, y1 + 0.01, loft + 0.5), (1.0, y1 + 0.05, loft + 2.3), "ext")
        p.box((-0.1, y1, wall_top + 1.2), (0.1, y1 + 1.2, wall_top + 1.4), "wood")
    b.empty("light_barn", (0.0, 0.0, loft - 0.4))
    if typ != "pole_barn":
        b.empty("light_loft", (x1 - 2.5, 0.0, loft + 2.0))
    # bank barn: an earth ramp up to the loft doors on the back side
    if typ == "bank_barn":
        ramp = b.part("bank_ramp-col")
        q = [(-2.0, y0 - 6.0, 0.0), (2.0, y0 - 6.0, 0.0), (2.0, y0, loft), (-2.0, y0, loft)]
        ramp.face(q, "gravel")
        for s in (-2.0, 2.0):
            ramp.face([(s, y0 - 6.0, 0.0), (s, y0, 0.0), (s, y0, loft)] if s > 0 else [(s, y0, loft), (s, y0, 0.0), (s, y0 - 6.0, 0.0)], "lower")
    # ventilator cupolas along the ridge
    ncup = int(tr.get("cupolas") or (1 if tr.get("cupola") else 0))
    if ncup and typ != "pole_barn":
        half = (D if ridge == "x" else W) / 2
        rz = wall_top + ridge_height(half, 25 if gambrel else pitch, gambrel) - 0.1
        L_r = W if ridge == "x" else D
        for k in range(min(ncup, 4)):
            u = -L_r / 2 + L_r * (k + 1) / (ncup + 1)
            cupola(b, u if ridge == "x" else 0.0, 0.0 if ridge == "x" else u, rz, name=f"cupola{k}")
    # an open lean-to shed along one side (clear of the side doors and the bank ramp)
    lt = tr.get("lean_to")
    if lt:
        sides = ["+x", "-x"] if "both" in str(lt).lower() else [LEAN_SIDE.get(str(lt).lower(), "+x")]
        for side in sides:
            if side == "-y" and typ == "bank_barn":
                side = "+x"
            if side == "+x":
                span = (y0 + D * 0.3 + 1.0, y1 - 0.3)
            elif side == "-x":
                span = (y0 + 0.3, y1 - D * 0.3 - 1.0)
            else:
                span = (min(3.2, W * 0.3) / 2 + 0.6, x1 - 0.3)
            lean_to(b, side, span, x0, x1, y0, y1, h_in=min(3.0, wall_top - 0.3))
    # a grain-elevator tower rising through the roof near one end (built from the wall top up, so
    # the barn's floors and the lean-tos below stay clear)
    if tr.get("elevator_tower") and typ != "pole_barn":
        half = (D if ridge == "x" else W) / 2
        rz = wall_top + ridge_height(half, 25 if gambrel else pitch, gambrel)
        ts = 3.4
        ex, ey = (x1 - ts / 2 - 1.0, 0.0) if ridge == "x" else (0.0, y0 + ts / 2 + 1.0)
        et = b.part("elevator_tower")
        et.box((ex - ts / 2, ey - ts / 2, wall_top - 0.5), (ex + ts / 2, ey + ts / 2, rz + 4.0), "ext")
        et.box((ex - 0.5, ey + ts / 2 + 0.01, rz + 1.2), (ex + 0.5, ey + ts / 2 + 0.05, rz + 3.2), "wood")      # hinged plank door
        gh.hip_roof(et, ex - ts / 2 - 0.25, ex + ts / 2 + 0.25, ey - ts / 2 - 0.25, ey + ts / 2 + 0.25, rz + 4.0, 45, 0.25, 0.1,
                    "roof", "trim", "trim")
    # the farm name on the front gable
    sign = (names.get("sign") or names.get("family") or "").upper()
    if sign:
        g.text_mesh(b, "sign_barn", sign[:28], clamp((W - 1.0) / max(8, len(sign[:28])) * 1.3, 0.25, 0.6),
                    (0.0, y1 + 0.06, wall_top + 0.5), math.pi, "letters_white", extrude=0.01, font=FONT_SANS)
    return b


# ------------------------------------------------------------------ silo
def build_silo(rec, tr, rnd):
    b = lib_building(rec["id"])
    materials(b, tr)
    pal = Palette(b)
    typ = tr.get("type", "concrete_stave")
    r = clamp(ft(tr.get("diameter_ft") or 14) / 2, 1.8, 4.0)
    h = clamp(ft(tr.get("height_ft") or 40), 6.0, 22.0)
    tex = {"concrete_stave": "concrete", "brick": "brick_red", "tile": "brick_buff", "wood_stave": "weathered_board"}.get(typ)
    if typ == "harvestore_blue":
        pal.solid("silo_wall", (0.12, 0.2, 0.42), rough=0.2, metal=0.5)
    else:
        pal.surf("silo_wall", tex or "concrete", rough=0.85)
    p = b.part("silo-col")
    n = 28
    # wall as a ring of panels with a doorway gap facing +y at the base
    door_w, door_h = 0.9, 2.1
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        gap = abs(math.atan2(math.sin(am - math.pi / 2), math.cos(am - math.pi / 2))) < (door_w / 2) / r
        for (ro, ri) in ((r, r - 0.2),):
            P = lambda a, rr, z: (rr * math.cos(a), rr * math.sin(a), z)
            zb = door_h if gap else 0.0
            p.face([P(a0, ro, zb), P(a1, ro, zb), P(a1, ro, h), P(a0, ro, h)], "silo_wall")
            p.face([P(a1, ri, zb), P(a0, ri, zb), P(a0, ri, h), P(a1, ri, h)], "silo_wall")
            if gap:
                p.face([P(a1, ro, zb), P(a0, ro, zb), P(a0, ri, zb), P(a1, ri, zb)], "silo_wall")
    # hoops (stave silos): open bands on a visual-only part.  Capped, each one was a solid disc
    # across the silo in the collision mesh (the lowest ~0.3 m above the floor), sealing it off.
    if typ in ("concrete_stave", "wood_stave"):
        hp = b.part("silo_hoops")
        for k in range(int(h / 0.8)):
            hp.cylinder((0.0, 0.0), r + 0.03, k * 0.8 + 0.4, k * 0.8 + 0.45, "steel", n=n, caps=False)
    # domed / conical roof; a painted checkerboard dome (and/or band) when the record has one
    checked_top = tr.get("checkered_top") or tr.get("checkered")
    checked_band = tr.get("checkered_band") or (tr.get("checkered") and not tr.get("checkered_top"))
    if checked_top or checked_band:
        pal.solid("check_red", (0.72, 0.1, 0.08), rough=0.6)
        pal.solid("check_white", (0.93, 0.91, 0.87), rough=0.6)
    for k in range(6):
        rr0 = r * math.cos(k / 6 * math.pi / 2)
        rr1 = r * math.cos((k + 1) / 6 * math.pi / 2)
        z0 = h + r * 0.8 * math.sin(k / 6 * math.pi / 2)
        z1 = h + r * 0.8 * math.sin((k + 1) / 6 * math.pi / 2)
        if checked_top:
            Q = lambda a, rr, z: ((rr + 0.05) * math.cos(a), (rr + 0.05) * math.sin(a), z)
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                p.face([Q(a0, rr0, z0), Q(a1, rr0, z0), Q(a1, rr1, z1), Q(a0, rr1, z1)],
                       "check_red" if (i // 2 + k) % 2 == 0 else "check_white")
        else:
            p.cylinder((0.0, 0.0), max(rr0, rr1) + 0.05, z0, z1, "silo_wall" if typ == "harvestore_blue" else "roof", n=n, r1=rr1 + 0.05)
    if checked_band:
        bnd = b.part("silo_band")
        for row in range(2):
            zz = h - 1.6 + row * 0.6
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                if abs(math.atan2(math.sin((a0 + a1) / 2), math.cos((a0 + a1) / 2))) < 0.35:
                    continue                                                # behind the chute (+x) stays plain
                Q = lambda a, z: ((r + 0.04) * math.cos(a), (r + 0.04) * math.sin(a), z)
                bnd.face([Q(a0, zz), Q(a1, zz), Q(a1, zz + 0.6), Q(a0, zz + 0.6)], "check_red" if (i + row) % 2 == 0 else "check_white")
    p.cylinder((0.0, 0.0), r - 0.05, -0.05, 0.1, "concrete", n=n)
    # a feed room against the base (as on real silos): an ordinary hinged door to the yard, and a
    # cased opening through its back wall into the silo's doorway gap
    fr = (-1.3, r - 0.35, 1.3, r + 2.2)
    spec = dict(t_ext=0.12, t_int=0.1, era="old",
                mats=dict(ext="ext", int="wood", roof="roof", roof_under="roof_under", found="found", floor="floor", ceiling="wood",
                          trim="trim", door="wood", fascia="trim", porch="concrete", post="wood", furn="wood"),
                blocks=[dict(name="feed", rect=fr, floors=[(0.1, 2.5)], wall_top=2.7, found_top=0.05,
                             roof=dict(type="shed", high="S", pitch=18, eave_oh=0.25, thick=0.1))],
                rooms=[dict(name="FEED", rect=fr, type=None, no_furnish=True)],
                doors=[dict(name="feed", at=(0.0, fr[3]), w=0.9, ext=True),
                       dict(name="silo_way", at=(0.0, fr[1]), w=0.85, h=door_h - 0.05, ext=True, cased=True)],
                windows=[dict(at=(fr[2], (fr[1] + fr[3]) / 2), w=0.6, sill=1.2, h=0.6, kind="dh", cols=2)],
                stairs=[], rails=[], porches=[], chimneys=[], fireplaces=[])
    gh.House(b, spec).build()
    # chute on the +x side (the door faces +y), the ladder on the chute's outer face
    ch = b.part("silo_chute-col")
    ch.box((r - 0.05, -0.45, 0.0), (r + 0.8, 0.45, h + 0.3), "silo_wall" if typ != "harvestore_blue" else "steel")
    ladder(b, "silo", r + 0.9, 0.0, 0.0, h + 0.5, axis="y")
    b.empty("light_silo", (0.0, 0.0, 2.2))
    return b


# ------------------------------------------------------------------ shed
def build_shed(rec, tr, rnd):
    b = lib_building(rec["id"])
    materials(b, tr)
    typ = tr.get("type", "pole_shed")
    W = clamp(ft(tr.get("w_ft") or 40), 6.0, 24.0)
    D = clamp(ft(tr.get("d_ft") or 30), 6.0, 24.0)
    H = clamp(ft(tr.get("height_ft") or 16), 3.2, 7.0)
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    FL = 0.05
    drive = False
    if typ == "quonset":
        p = b.part("quonset-col")
        r = W / 2
        n = 16
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            P = lambda a, y, dr=0.0: ((r + dr) * math.cos(a), y, (r + dr) * math.sin(a) * H / r)
            p.face([P(a0, y0), P(a1, y0), P(a1, y1), P(a0, y1)], "ext")
            p.face([P(a1, y0, -0.05), P(a0, y0, -0.05), P(a0, y1, -0.05), P(a1, y1, -0.05)], "ext")
        # end walls: the back closed, the front with a big door opening (two leaves) + a man door
        for yy, front in ((y0, False), (y1, True)):
            pts = [(r * math.cos(math.pi * i / n), r * math.sin(math.pi * i / n) * H / r) for i in range(n + 1)]
            for (xa, za), (xb, zb) in zip(pts, pts[1:]):
                xm = (xa + xb) / 2
                zlo = 3.0 if front and abs(xm) < 1.9 else 0.0
                if max(za, zb) <= zlo:
                    continue
                q = [(xa, yy, max(zlo, 0.0)), (xb, yy, max(zlo, 0.0)), (xb, yy, zb), (xa, yy, za)]
                p.face(q if front else q[::-1], "ext")
                p.face([(v[0], v[1] - 0.05 if front else v[1] + 0.05, v[2]) for v in (q[::-1] if front else q)], "ext")
        p.box((x0, y0, -0.02), (x1, y1, FL), "floor", sides="Z")
        for s in (-1, 1):
            hinge = g.Vector((s * 1.9, y1 + 0.02, FL))
            leaf = b.part(f"door_quonset_{'L' if s < 0 else 'R'}__{'p' if s < 0 else 'n'}")
            Fl = (g.Vector((0, 0, 0)), g.Vector((1, 0, 0)), g.Vector((0, 1, 0)), g.Vector((0, 0, 1)))
            leaf.obox(Fl, (0.0, 0.0, 0.0), (1.85, 0.05, 2.95), "ext")
            leaf.origin = hinge
            leaf.rot_z = 0.0 if s < 0 else math.pi
        fz = FL
    else:
        open_front = typ == "pole_shed" or bool(tr.get("open_front"))
        drive = bool(tr.get("drive_through")) and not open_front
        doors = []
        if not open_front:
            nb = max(1, int(W / 5.0))
            for i in range(nb):
                doors.append(dict(name=f"bay{i}", at=(x0 + W * (i + 0.5) / nb, y1), w=min(3.6, W / nb - 0.6), h=min(3.4, H - 0.4),
                                  ext=True, leaves=2, out=True, panels=[(0.08, 0.08, 0.92, 0.92)]))
        doors.append(dict(name="man", at=(x1, y0 + 1.2), w=0.9, ext=True, out=True))
        spec = dict(t_ext=0.1, t_int=0.1, era="old",
                    mats=dict(ext="ext", int="wood", roof="roof", roof_under="roof_under", found="found", floor="floor", ceiling="wood",
                              trim="trim", door="ext", fascia="trim", porch="concrete", post="wood", furn="wood"),
                    blocks=[dict(name="shed", rect=(x0, y0, x1, y1), floors=[(FL, H - 0.2)], wall_top=H, found_top=FL,
                                 roof=dict(type="gable", ridge="x", pitch=20 if typ != "corn_crib" else 35, eave_oh=0.4, rake_oh=0.3,
                                           thick=0.12))],
                    rooms=[dict(name="SHED", rect=(x0, y0, x1, y1), type=None, no_furnish=True)], doors=doors,
                    windows=[dict(at=(x0, 0.0), w=0.8, sill=1.3, h=0.6, kind="dh", cols=2)] if typ != "corn_crib" else [],
                    stairs=[], rails=[], porches=[], chimneys=[], fireplaces=[])
        if drive:
            # a drive-through crib / granary: an open wagon alley straight through, front to back
            dw = min(3.6, W * 0.4)
            spec["doors"] = [dict(name="drive_f", at=(0.0, y1), w=dw, h=min(3.6, H - 0.3), ext=True, cased=True),
                             dict(name="drive_b", at=(0.0, y0), w=dw, h=min(3.6, H - 0.3), ext=True, cased=True),
                             spec["doors"][-1]]
        if open_front:
            # an open-fronted pole shed: wide cased bays across the front, posts between them
            nb = max(2, int(W / 4.0))
            spec["doors"] = [dict(name=f"bay{i}", at=(x0 + W * (i + 0.5) / nb, y1), w=W / nb - 0.35, h=H - 0.4, ext=True, cased=True)
                             for i in range(nb)] + [spec["doors"][-1]]
        gh.House(b, spec).build()
        fz = FL
    p = b.part("shed_fittings-col")
    if typ != "quonset" and drive:
        tractor(p, (x0 + min(1.3, W * 0.15), 0.0, fz), 90)             # parked beside the alley, which stays clear
    else:
        tractor(p, (x0 + W * 0.3, 0.0, fz), 180)
        wagon(p, (x0 + W * 0.72, -0.5, fz), 180)
    b.empty("light_shed", (0.0, 0.0, H - 0.6))
    return b


def build(rec):
    rid = rec["id"]
    tr = rec.get("traits") or {}
    rnd = rng(rid)
    part = rid.rsplit("-", 1)[-1]
    if part == "barn":
        return build_barn(rec, tr, rnd)
    if part == "silo":
        return build_silo(rec, tr, rnd)
    return build_shed(rec, tr, rnd)
