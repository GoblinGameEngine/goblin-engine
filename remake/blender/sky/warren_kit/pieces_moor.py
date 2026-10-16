"""pieces_moor.py -- the island side of the market moorings (research/flea_markets/00_plan.md section 8.2, requested by
the flea-market streams; the market kit's twin pieces are remake/blender/markets): the winch house at the rim, the
gondola top stations (passengers and cargo), the drop-cage davit and the signal mast.

Frame: CELL pieces spanning [nx, nz] cells along +X / +Z from the first cell (origin at the first cell's centre,
y 0 = the deck).  THE RIM IS -Z: the first row's outer face (z -1.5) stands on the deck edge, and what reaches over
the void (fairleads, the davit's jib, the stations' cantilevered berth decks) lies at z < -1.5.  The generator turns a
piece so its -Z faces out of the island.  Shared by every family (civs "shared"): the families dress them with their
palette (wall / trim / roof / accent / accent2) and their own overlays (ov_festoon, ov_lantern, ov_chochin_string,
ov_awning_cane, ov_suq_canopy) on the faces.

Collision is "frame" (explicit boxes: SPECIAL below, merged into build.py's SPECIAL); walk-through volumes in "pass".
The gondola geometry matches the market kit: cabin floor = platform top, the carriage pivot 5.2 m over it, the track
ropes 0.9 m over the pivot, the haul rope 0.37 m over it, berths 6.5 m apart (the bull wheel's diameter).
"""
import math

from geom import Mesh, rot_y
from pieces import PIECES, _w
from pieces_marks import _place

SH = ["shared"]
PIVOT, ROPE_DY, HAUL_DY, ROPE_DZ = 5.2, 0.9, 0.37, 0.3


def B(x0, y0, z0, x1, y1, z1):
    return [[round(x0, 4), round(y0, 4), round(z0, 4)], [round(x1, 4), round(y1, 4), round(z1, 4)]]


def _wall_x(m, z0, z1, x0, x1, y0, y1, slot, holes=()):
    """a wall slab lying along z (its faces +-x) from z0 to z1, x0..x1 thick, with holes [(za, zb, ya, yb)]"""
    sub = Mesh()
    z0, z1, x0, x1 = z0 + 0.002, z1 - 0.002, x0 + 0.002, x1 - 0.002          # (no edge shared with a neighbour slab)
    outer = [(-z1, y0), (-z0, y0), (-z0, y1), (-z1, y1)]
    hs = [[(-zb, ya), (-za, ya), (-za, yb), (-zb, yb)] for za, zb, ya, yb in holes]
    if hs:
        sub.wall_cut(outer, hs, x0, x1, slot, reveal_slot="trim")
    else:
        sub.prism_xy(outer, [], x0, x1, slot)
    m.add(sub, rot_y(90))


def _wall_z(m, x0, x1, z0, z1, y0, y1, slot, holes=()):
    """a wall slab lying along x (its faces +-z) from x0 to x1, z0..z1 thick, with holes [(xa, xb, ya, yb)]"""
    x0, x1, z0, z1 = x0 + 0.002, x1 - 0.002, z0 + 0.002, z1 - 0.002
    outer = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    hs = [[(xa, ya), (xb, ya), (xb, yb), (xa, yb)] for xa, xb, ya, yb in holes]
    if hs:
        m.wall_cut(outer, hs, z0, z1, slot, reveal_slot="trim")
    else:
        m.prism_xy(outer, [], z0, z1, slot)


def _panes_z(m, xs, ya, yb, z, sgn):
    """glass panes on a face at z facing sgn * z, between the xs pairs"""
    for xa, xb in xs:
        if sgn > 0:
            m.pane(xa, ya, xb, yb, z)
        else:
            m.quad((xb, ya, z), (xa, ya, z), (xa, yb, z), (xb, yb, z), "glass", 1.0, uv=[(0, 1), (1, 1), (1, 0), (0, 0)])


def _panes_x(m, zs, ya, yb, x, sgn):
    for za, zb in zs:
        if sgn > 0:
            m.quad((x, ya, zb), (x, ya, za), (x, yb, za), (x, yb, zb), "glass", 1.0, uv=[(0, 1), (1, 1), (1, 0), (0, 0)])
        else:
            m.quad((x, ya, za), (x, ya, zb), (x, yb, zb), (x, yb, za), "glass", 1.0, uv=[(0, 1), (1, 1), (1, 0), (0, 0)])


def _bulb(m, p, r, slot="emissive"):
    x, y, z = p
    pts = [(x + r, y, z), (x, y, z - r), (x - r, y, z), (x, y, z + r)]
    for k in range(4):
        a, b = pts[k], pts[(k + 1) % 4]
        m.tri(a, b, (x, y + r, z), slot)
        m.tri(b, a, (x, y - r * 1.25, z), slot)


def _rope(m, pts, r=0.03, slot="metal"):
    for a, b in zip(pts, pts[1:]):
        m.tube(a, b, r, slot, n=5)


# ------------------------------------------------------------------ the line house (3 x 3 cells, 2 storeys)
def moor_line_house(q=1):
    """the winch house at the rim: a hawser drum behind a wide rim-side gate, the fairlead cantilevered over the edge,
    a glazed control cab upstairs looking out over the rim, a signal mast seat on its roof (q 0: its MID)"""
    def b():
        m = Mesh()
        x0, x1, z0, z1 = -1.4, 7.4, -1.4, 7.4
        T = 0.25
        _wall_z(m, x0, x1, z0, z0 + T, 0.0, 3.2, "wall", holes=[(1.0, 5.0, 0.0, 2.8)])          # the rim face: the hawser gate
        _wall_z(m, x0, x1, z1 - T, z1, 0.0, 3.2, "wall", holes=[(2.4, 3.6, 0.0, 2.3)])          # the back: a door
        _wall_x(m, z0 + T, z1 - T, x0, x0 + T, 0.0, 3.2, "wall", holes=[(2.0, 3.4, 1.0, 2.2)])
        _wall_x(m, z0 + T, z1 - T, x1 - T, x1, 0.0, 3.2, "wall", holes=[(2.0, 3.4, 1.0, 2.2)])
        if q:
            _panes_x(m, [(2.0, 3.4)], 1.0, 2.2, x0 + 0.12, -1)
            _panes_x(m, [(2.0, 3.4)], 1.0, 2.2, x1 - 0.12, 1)
        m.box((x0 - 0.1, 3.2, z0 - 0.1), (x1 + 0.1, 3.45, z1 + 0.1), "roof")                    # the first roof (the cab's floor)
        m.box((2.4, 0.05, z1 - 0.2), (3.6, 2.25, z1 - 0.15), "frame")                          # the back door leaf
        # the drum: along x inside the gate, flanged, three wraps of hawser, on two frames
        drum = Mesh()
        nd = 12 if q else 8
        drum.cyl(0.0, 0.0, 0.9, -1.8, 1.8, "metal", n=nd)
        for y in (-1.8, 1.8):
            drum.cyl(0.0, 0.0, 1.25, y - (0.08 if y < 0 else 0.0), y + (0.0 if y < 0 else 0.08), "accent", n=nd)
        m.add(drum, lambda p: (p[1] + 3.0, 1.5 - p[0], 1.6 + p[2]))                            # (axis y -> x: a proper turn)
        for x in (1.0, 5.0):
            m.box((x - 0.12, 0.0, 1.0), (x + 0.12, 1.5, 2.2), "metal")
        # the fairlead: two arms over the rim, a roller at the tip; the hawser from the drum's top over the roller
        for x in (2.4, 3.6):
            m.box((x - 0.08, 0.5, -3.4), (x + 0.08, 0.8, z0), "metal")
            if q:
                m.tube((x, 0.5, -3.2), (x, -1.4, z0 - 0.02), 0.06, "metal", n=4)
        roll = Mesh()
        roll.cyl(0.0, 0.0, 0.18, -0.5, 0.5, "accent2", n=10)
        m.add(roll, lambda p: (p[1] + 3.0, 0.98 - p[0], -3.3 + p[2]))
        m.tube((3.0, 2.46, 1.6), (3.0, 1.21, -3.3), 0.05, "fabric", n=5)                       # the hawser out
        m.tube((3.0, 0.8, -3.48), (3.0, -2.5, -3.48), 0.05, "fabric", n=5)                      # (down over the edge)
        # the control cab upstairs
        cx0, cx1, cz0, cz1 = 0.6, 5.4, -1.2, 3.4
        m.box((cx0, 3.45, cz0), (cx1, 4.35, cz1), "wall")
        m.box((cx0, 5.95, cz0), (cx1, 6.15, cz1), "wall")
        for x in ((cx0, cx0 + 1.6, cx1 - 1.6, cx1) if q else (cx0, cx1)):
            xa = min(max(x - 0.08, cx0), cx1 - 0.16)
            m.box((xa + 0.002, 4.352, cz0 + 0.002), (xa + 0.158, 5.948, cz0 + 0.158), "frame")
            m.box((xa + 0.002, 4.352, cz1 - 0.158), (xa + 0.158, 5.948, cz1 - 0.002), "frame")
        _panes_z(m, [(cx0 + 0.16, cx0 + 1.52), (cx0 + 1.68, cx1 - 1.68), (cx1 - 1.52, cx1 - 0.16)], 4.35, 5.95, cz0 + 0.08, -1)
        _panes_z(m, [(cx0 + 0.16, cx0 + 1.52), (cx1 - 1.52, cx1 - 0.16)], 4.35, 5.95, cz1 - 0.08, 1)
        m.box((cx0 + 0.002, 4.352, cz0 + 0.162), (cx0 + 0.158, 5.948, cz1 - 0.162), "wall")
        m.box((cx1 - 0.158, 4.352, cz0 + 0.162), (cx1 - 0.002, 5.948, cz1 - 0.162), "wall")
        m.box((cx0 - 0.4, 6.15, cz0 - 0.5), (cx1 + 0.4, 6.4, cz1 + 0.4), "roof")
        m.box((2.7, 6.4, 0.8), (3.3, 6.5, 1.4), "metal")                                        # the signal mast seat
        _bulb(m, (cx0 - 0.25, 6.55, cz0 - 0.35), 0.1)
        _bulb(m, (cx1 + 0.25, 6.55, cz0 - 0.35), 0.1)
        for x in ((1.6, 4.4) if q else ()):                                                    # the gate's lamps
            m.box((x - 0.1, 2.95, z0 - 0.12), (x + 0.1, 3.1, z0), "metal")
            m.box((x - 0.07, 2.88, z0 - 0.1), (x + 0.07, 2.95, z0 - 0.02), "emissive")
        return m
    return b


# ------------------------------------------------------------------ the drop-cage davit (2 x 2 cells)
DAVIT_TIP = (1.5, 8.2, -3.6)


def moor_drop_cage_davit():
    """the davit for the first, free-hanging gondola (the crew's drop cage): a slewing post on a plinth, a jib over
    the rim with a sheave at its tip, the winch at its foot, the hoist line down over the edge"""
    def b():
        m = Mesh()
        m.box((0.2, 0.0, -1.2), (2.8, 0.6, 1.4), "trim")                                       # the plinth
        m.cyl(1.5, 0.1, 0.42, 0.6, 7.6, "accent", n=12, r1=0.3)                                 # the post
        m.cyl(1.5, 0.1, 0.5, 7.6, 8.0, "metal", n=12)                                           # the slewing ring
        tx, ty, tz = DAVIT_TIP
        jib = Mesh()                                                                           # the jib (two plates) and its strut
        jib.prism_xy([(-0.6, 7.75), (4.1, 8.05), (4.1, 8.45), (-0.6, 8.6)], [], -0.07, 0.07, "accent")
        for dx in (-0.22, 0.22):
            _place(m, jib, 90, dx=1.5 + dx, dz=0.1)
        m.tube((1.5, 6.4, 0.38), (1.5, 7.85, -2.2), 0.08, "metal", n=6)
        sh = Mesh()
        sh.cyl(0.0, 0.0, 0.32, -0.12, 0.12, "metal", n=10)
        m.add(sh, lambda p: (p[1] + tx, ty - p[0], p[2] + tz))
        # the winch at the foot and the hoist line: up the jib, over the sheave, down over the edge
        dr = Mesh()                                                                            # (axis along z, beside the post)
        dr.cyl(0.0, 0.0, 0.33, -0.35, 0.35, "frame", n=10)
        m.add(dr, lambda p: (p[0] + 2.32, 0.97 - p[2], p[1] + 1.0))
        m.box((2.0, 0.6, 0.55), (2.64, 1.35, 0.63), "metal")
        m.box((2.0, 0.6, 1.37), (2.64, 1.35, 1.45), "metal")
        m.tube((2.32, 1.3, 1.0), (1.5, ty + 0.2, tz + 0.3), 0.022, "fabric", n=4)               # (to the sheave's back tangent)
        m.tube((1.5, ty, tz - 0.32), (1.5, ty - 6.0, tz - 0.32), 0.022, "fabric", n=4)
        m.box((1.38, ty - 6.25, tz - 0.44), (1.62, ty - 6.0, tz - 0.2), "metal")                # the hook block
        _bulb(m, (1.5, ty + 0.62, tz + 0.2), 0.1)
        return m
    return b


# ------------------------------------------------------------------ the signal mast (1 x 1 cell, 4 storeys; tops a line house)
def moor_signal_mast():
    """signal lights for the ground crews (a column of coloured lamps), the bell for bell-speech in its frame, a small
    look-out platform; y 0 = the roof it stands on"""
    def b():
        m = Mesh()
        H = 12.6
        m.box((-0.5, 0.0, -0.5), (0.5, 0.15, 0.5), "metal")
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.tube((sx * 0.42, 0.15, sz * 0.42), (sx * 0.2, H, sz * 0.2), 0.04, "accent", n=4)
        for k in range(1, 8):
            y = 0.15 + (H - 0.15) * k / 8
            hw = 0.42 - 0.22 * y / H
            for yaw in (0, 90, 180, 270):
                t = Mesh()
                t.tube((-hw + 0.04, y, hw), (hw - 0.04, y, hw), 0.02, "accent", n=3)
                _place(m, t, yaw)
        m.box((-0.75, 9.6, -0.75), (0.75, 9.72, 0.75), "metal")                                 # the look-out
        for yaw in (0, 90, 180, 270):
            t = Mesh()
            t.box((-0.73, 10.7, 0.71), (0.69, 10.75, 0.75), "metal")
            t.box((-0.73, 9.72, 0.71), (-0.69, 10.698, 0.75), "metal")
            _place(m, t, yaw)
        for k, sl in enumerate(("emissive", "accent2", "emissive", "accent2", "emissive")):      # the lamp column, -z (rim) face
            y = 2.0 + 1.4 * k
            m.box((-0.16, y - 0.16, -0.62), (0.16, y + 0.16, -0.36), "metal")
            m.box((-0.12, y - 0.12, -0.64), (0.12, y + 0.12, -0.62), sl)
        m.box((-0.3, H, -0.3), (0.3, H + 0.12, 0.3), "metal")
        for x in (-0.28, 0.28):
            m.box((x - 0.03, H + 0.12, -0.03), (x + 0.03, H + 0.95, 0.03), "metal")
        m.box((-0.31, H + 0.95, -0.05), (0.31, H + 1.02, 0.05), "metal")
        m.lathe([(0.24, H + 0.35), (0.2, H + 0.5), (0.14, H + 0.8), (0.04, H + 0.94), (0.0, H + 0.95)], "accent2", n=10)   # the bell
        _bulb(m, (0.0, H + 1.16, 0.0), 0.1)
        return m
    return b


# ------------------------------------------------------------------ the gondola top stations (4 x 6 pax, 4 x 5 cargo)
BERTH_X = (1.25, 7.75)
DECKS = [(-1.4, -0.37), (2.87, 6.13), (9.37, 10.4)]
TIP_Z, DECK_Z0, CAB_Z = -9.0, -8.6, -5.0
ROPE_Y, HAUL_Y = PIVOT + ROPE_DY, PIVOT + HAUL_DY
WHEEL = (4.5, HAUL_Y, 3.0)


def _rail_z(m, x, za, zb, y0=0.0, slot="accent2"):
    """a railing along z at x from za to zb: end posts, a top rail and a knee rail"""
    for z in (za, zb):
        m.box((x - 0.03, y0, z - 0.03), (x + 0.03, y0 + 1.1, z + 0.03), slot)
    m.box((x - 0.035, y0 + 1.1, za - 0.03), (x + 0.035, y0 + 1.16, zb + 0.03), slot)
    m.box((x - 0.015, y0 + 0.55, za + 0.03), (x + 0.015, y0 + 0.59, zb - 0.03), slot)


def _rail_x(m, z, xa, xb, y0=0.0, slot="accent2"):
    for x in (xa, xb):
        m.box((x - 0.03, y0, z - 0.03), (x + 0.03, y0 + 1.1, z + 0.03), slot)
    m.box((xa - 0.03, y0 + 1.1, z - 0.035), (xb + 0.03, y0 + 1.16, z + 0.035), slot)
    m.box((xa + 0.03, y0 + 0.55, z - 0.015), (xb - 0.03, y0 + 0.59, z + 0.015), slot)


def station(cargo):
    zb = 13.4 if cargo else 16.4

    def b():
        m = Mesh()
        # the cantilevered berth decks over the void, their girders and struts into the rim below
        for xa, xb in DECKS:
            m.box((xa, -0.15, DECK_Z0), (xb, 0.0, -1.5), "metal")
            xc = (xa + xb) / 2
            m.box((xc - 0.2, -0.75, DECK_Z0 + 0.1), (xc + 0.2, -0.15, -1.5), "frame")
            for x in (xa + 0.15, xb - 0.15):
                m.tube((x, -0.75, DECK_Z0 + 0.5), (x, -6.0, -1.55), 0.12, "frame", n=6)
        for k, (xa, xb) in enumerate(DECKS):                                     # railings: berth edges (door gaps), outer edges, tips
            for x, inner in ((xa + 0.06, k > 0), (xb - 0.06, k < 2)):
                if inner:
                    _rail_z(m, x, DECK_Z0 + 0.1, CAB_Z - 0.85)
                    _rail_z(m, x, CAB_Z + 0.85, -1.62)
                else:
                    _rail_z(m, x, DECK_Z0 + 0.1, -1.62)
            _rail_x(m, DECK_Z0 + 0.06, xa + 0.16, xb - 0.16)
        # the berth gantry: two portals on the decks, a canopy roof, the head saddles at the tip
        for zp in (TIP_Z + 0.7, -1.9):
            for xc in (-0.885, 4.5, 9.885):
                m.box((xc - 0.15, 0.0, zp - 0.15), (xc + 0.15, 7.2, zp + 0.15), "accent")
            m.box((-1.42, 7.2, zp - 0.17), (10.42, 7.6, zp + 0.17), "accent")
        m.box((-1.5, 7.6, TIP_Z - 0.4), (10.5, 7.75, -1.62), "roof")
        for bx in BERTH_X:
            m.box((bx - 0.5, ROPE_Y - 0.15, TIP_Z - 0.7), (bx + 0.5, ROPE_Y - 0.032, TIP_Z + 0.2), "metal")    # the saddle shoe
            m.box((bx - 0.1, ROPE_Y - 0.15, TIP_Z + 0.2), (bx + 0.1, 7.2, TIP_Z + 0.53), "metal")              # its hanger
            for dx in (-ROPE_DZ, ROPE_DZ):
                m.tube((bx + dx, ROPE_Y, TIP_Z - 0.7), (bx + dx, ROPE_Y, 5.15), 0.03, "metal", n=5)           # the track ropes
            m.tube((bx, HAUL_Y, TIP_Z - 0.7), (bx, HAUL_Y, WHEEL[2]), 0.023, "metal", n=4)                  # the haul rope
        # the drive house (z -1.5 .. 7.5): an open passage below, the machine floor above with the bull wheel
        m.box((-1.4, 3.2, -1.5), (10.4, 3.45, 7.5), "trim")
        for xc in (-1.25, 10.25):
            for zc in (-1.35, 3.0, 7.35):
                m.box((xc - 0.15, 0.0, zc - 0.15), (xc + 0.15, 3.2, zc + 0.15), "wall")
        _wall_z(m, -1.4, 10.4, -1.5, -1.25, 3.45, 7.6, "wall", holes=[(-0.2, 9.2, 4.6, 7.0)])
        _wall_z(m, -1.4, 10.4, 7.25, 7.5, 3.45, 7.6, "wall", holes=[(1.0, 3.0, 4.4, 5.8), (6.0, 8.0, 4.4, 5.8)])
        _wall_x(m, -1.25, 7.25, -1.4, -1.15, 3.45, 7.6, "wall", holes=[(0.5, 2.5, 4.4, 5.8), (4.0, 6.0, 4.4, 5.8)])
        _wall_x(m, -1.25, 7.25, 10.15, 10.4, 3.45, 7.6, "wall", holes=[(0.5, 2.5, 4.4, 5.8), (4.0, 6.0, 4.4, 5.8)])
        _panes_x(m, [(0.5, 2.5), (4.0, 6.0)], 4.4, 5.8, -1.27, -1)
        _panes_x(m, [(0.5, 2.5), (4.0, 6.0)], 4.4, 5.8, 10.27, 1)
        _panes_z(m, [(1.0, 3.0), (6.0, 8.0)], 4.4, 5.8, 7.37, 1)
        m.box((-1.5, 7.6, -1.6), (10.5, 7.9, 7.65), "roof")
        wx, wy, wz = WHEEL                                                     # the bull wheel and its drive
        m.cyl(wx, wz, 0.4, 3.45, wy - 0.12, "metal", n=10)
        n = 28
        for k in range(n):
            a0, a1 = math.tau * k / n, math.tau * (k + 1) / n
            m.tube((wx + 3.25 * math.cos(a0), wy, wz + 3.25 * math.sin(a0)), (wx + 3.25 * math.cos(a1), wy, wz + 3.25 * math.sin(a1)), 0.1, "frame", n=4)
        for k in range(8):
            a = math.tau * k / 8
            m.tube((wx + 0.42 * math.cos(a), wy, wz + 0.42 * math.sin(a)), (wx + 3.1 * math.cos(a), wy, wz + 3.1 * math.sin(a)), 0.05, "metal", n=4)
        m.cyl(wx, wz, 0.5, wy - 0.12, wy + 0.12, "metal", n=10)
        m.box((wx + 3.6, 3.45, wz - 0.9), (wx + 5.4, 4.9, wz + 0.9), "accent")    # the motor
        for bx in BERTH_X:                                                     # the track ropes' anchor drums
            dr = Mesh()
            dr.cyl(0.0, 0.0, 0.45, -0.55, 0.55, "frame", n=10)
            m.add(dr, lambda p, bx=bx: (p[1] + bx, ROPE_Y - p[0], p[2] + 5.6))                  # (axis along x)
            m.box((bx - 0.7, 3.45, 5.3), (bx + 0.7, ROPE_Y - 0.45, 5.9), "metal")
        # the gates at the rim (y 0, z -1.2): posts, a lit header
        for xa, xb in DECKS:
            for x in (xa + 0.1, xb - 0.1):
                m.box((x - 0.06, 0.0, -1.26), (x + 0.06, 2.45, -1.14), "metal")
            m.box((xa + 0.04, 2.45, -1.27), (xb - 0.04, 2.75, -1.13), "metal")
            m.box((xa + 0.2, 2.5, -1.3), (xb - 0.2, 2.7, -1.27), "emissive")
        if not cargo:
            # the waiting hall: an open arcade below (columns), offices above with windows, a fare booth, benches
            for xc in (3.0, 7.0):
                for zc in (11.0, zb - 0.15):
                    m.box((xc - 0.15, 0.0, zc - 0.15), (xc + 0.15, 3.2, zc + 0.15), "wall")
            m.box((-1.4, 3.2, 7.502), (10.4, 3.45, zb), "trim")
            _wall_x(m, 7.5, zb, -1.4, -1.15, 0.0, 3.2, "wall", holes=[(8.5, 10.0, 0.9, 2.3), (12.0, 14.5, 0.9, 2.3)])
            _wall_x(m, 7.5, zb, 10.15, 10.4, 0.0, 3.2, "wall", holes=[(8.5, 10.0, 0.9, 2.3), (12.0, 14.5, 0.9, 2.3)])
            _panes_x(m, [(8.5, 10.0), (12.0, 14.5)], 0.9, 2.3, -1.27, -1)
            _panes_x(m, [(8.5, 10.0), (12.0, 14.5)], 0.9, 2.3, 10.27, 1)
            _wall_z(m, -1.4, 10.4, 7.5, 7.75, 3.45, 6.4, "wall")
            _wall_z(m, -1.4, 10.4, zb - 0.25, zb, 3.45, 6.4, "wall", holes=[(0.0, 2.0, 4.3, 5.7), (3.5, 5.5, 4.3, 5.7), (7.0, 9.0, 4.3, 5.7)])
            _panes_z(m, [(0.0, 2.0), (3.5, 5.5), (7.0, 9.0)], 4.3, 5.7, zb - 0.12, 1)
            _wall_x(m, 7.75, zb - 0.25, -1.4, -1.15, 3.45, 6.4, "wall", holes=[(9.0, 11.0, 4.3, 5.7), (12.5, 14.5, 4.3, 5.7)])
            _wall_x(m, 7.75, zb - 0.25, 10.15, 10.4, 3.45, 6.4, "wall", holes=[(9.0, 11.0, 4.3, 5.7), (12.5, 14.5, 4.3, 5.7)])
            m.box((-1.5, 6.4, 7.4), (10.5, 6.7, zb + 0.1), "roof")
            m.box((0.0, 0.0, 9.0), (1.8, 2.5, 10.4), "trim")                                    # the fare booth
            m.box((-0.1, 2.5, 8.9), (1.9, 2.62, 10.5), "accent")
            m.quad((1.8 + 0.027, 1.0, 10.2), (1.8 + 0.027, 1.0, 9.2), (1.8 + 0.027, 2.1, 9.2), (1.8 + 0.027, 2.1, 10.2), "glass", 1.0, uv=[(0, 1), (1, 1), (1, 0), (0, 0)])
            for z in (12.0, 13.6):                                                             # benches
                m.box((5.0, 0.0, z - 0.2), (8.6, 0.42, z + 0.2), "frame")
                m.box((5.0, 0.42, z + 0.16), (8.6, 0.9, z + 0.22), "frame")
            for x in (0.6, 4.0, 7.6):                                                          # the arcade's lamps
                m.box((x - 0.3, 3.12, 14.0), (x + 0.3, 3.2, 14.6), "emissive")
        else:
            # the cargo shed: an open-fronted shed, the weigh scale and the skybox cradle on the centre deck, a gantry crane
            for xc in (-1.25, 10.25):
                for zc in (10.0, zb - 0.15):
                    m.box((xc - 0.15, 0.0, zc - 0.15), (xc + 0.15, 4.6, zc + 0.15), "wall")
            _wall_z(m, -1.4, 10.4, zb - 0.25, zb, 0.0, 4.6, "wall", holes=[(2.5, 6.5, 0.0, 3.6)])
            m.box((-1.5, 4.6, 7.4), (10.5, 4.9, zb + 0.1), "roof")
            m.box(((DECKS[1][0] + 0.1), 0.0, -7.6), ((DECKS[1][1] - 0.1), 0.05, -4.6), "metal")      # the weigh scale
            m.box((DECKS[1][1] - 0.6, 0.05, -4.3), (DECKS[1][1] - 0.2, 1.5, -4.1), "metal")
            m.box((DECKS[1][1] - 0.58, 1.1, -4.33), (DECKS[1][1] - 0.22, 1.45, -4.31), "emissive")
            for x in (DECKS[1][0] + 0.3, DECKS[1][1] - 0.3):                                   # the cradle's chocks
                m.box((x - 0.15, 0.05, -7.4), (x + 0.15, 0.3, -4.8), "accent2")
            for x in (DECKS[1][0] + 0.25, DECKS[1][1] - 0.25):                                 # the gantry over the centre deck
                m.box((x - 0.12, 7.0, TIP_Z + 0.5), (x + 0.12, 7.2, -2.1), "accent2")
            m.box((DECKS[1][0] + 0.13, 6.75, -6.3), (DECKS[1][1] - 0.13, 7.0, -5.7), "accent2")
            m.box((4.3, 6.2, -6.2), (4.7, 6.75, -5.8), "metal")
            m.tube((4.5, 6.2, -6.0), (4.5, 3.4, -6.0), 0.015, "metal", n=3)
        return m
    return b


# ------------------------------------------------------------------ register (and the collision frames for build.py)
PIECES["moor_line_house"] = _w("cell", moor_line_house(), SH, lod1="keep", kind="tower", span=(3, 3),
                               notes="MOORING: the winch house at the rim (3 x 3 cells, 2 storeys): hawser drum behind the rim gate, the fairlead over the edge (-z), a glazed control cab; moor_signal_mast sits on its roof seat (x 3.0, y 6.5, z 1.1)")
PIECES["moor_station_pax"] = _w("cell", station(False), SH, lod1="keep", kind="tower", span=(4, 6),
                                notes="MOORING: the gondola top station (4 x 6 cells): two berths on decks cantilevered 7.5 m over the rim (-z), the gantry and head saddles, the drive house with the bull wheel over an open passage, the waiting hall with its fare booth")
PIECES["moor_station_cargo"] = _w("cell", station(True), SH, lod1="keep", kind="tower", span=(4, 5),
                                  notes="MOORING: the cargo top station (4 x 5 cells): the same berths and drive house, a weigh scale and the skybox cradle on the centre deck under a gantry crane, an open cargo shed")
PIECES["moor_drop_cage_davit"] = _w("cell", moor_drop_cage_davit(), SH, lod1="keep", kind="tower", span=(2, 2),
                                    notes="MOORING: the davit for the crew's drop cage (2 x 2 cells): slewing post, jib over the rim (-z) with its sheave, the winch, the hoist line and hook")
PIECES["moor_signal_mast"] = _w("cell", moor_signal_mast(), SH, lod1="keep", kind="tower", collide=True,
                                notes="MOORING: the signal mast (1 x 1, 4 storeys; y 0 = the line house roof): a lamp column for the ground crews, the bell for bell-speech")

_DECK_FR = [B(xa, -0.15, DECK_Z0, xb, 0.0, -1.5) for xa, xb in DECKS]
_RAILS = []
for _k, (_xa, _xb) in enumerate(DECKS):
    for _x, _inner in ((_xa + 0.06, _k > 0), (_xb - 0.06, _k < 2)):
        _spans = [(DECK_Z0 + 0.1, CAB_Z - 0.85), (CAB_Z + 0.85, -1.62)] if _inner else [(DECK_Z0 + 0.1, -1.62)]
        _RAILS += [B(_x - 0.035, 0.0, za - 0.03, _x + 0.035, 1.16, zb + 0.03) for za, zb in _spans]
    _RAILS.append(B(_xa + 0.13, 0.0, DECK_Z0 + 0.025, _xb - 0.13, 1.16, DECK_Z0 + 0.095))
_GANTRY = [B(xc - 0.15, 0.0, zp - 0.15, xc + 0.15, 7.2, zp + 0.15) for zp in (TIP_Z + 0.7, -1.9) for xc in (-0.885, 4.5, 9.885)]
_GATES = [B(x - 0.06, 0.0, -1.26, x + 0.06, 2.45, -1.14) for xa, xb in DECKS for x in (xa + 0.1, xb - 0.1)]
_DRIVE = ([B(xc - 0.15, 0.0, zc - 0.15, xc + 0.15, 3.2, zc + 0.15) for xc in (-1.25, 10.25) for zc in (-1.35, 3.0, 7.35)]
          + [B(-1.4, 3.2, -1.5, 10.4, 7.9, 7.5)])
SPECIAL = {
    "moor_line_house": dict(frame=[B(-1.4, 0.0, -1.4, 1.0, 3.45, -1.15), B(5.0, 0.0, -1.4, 7.4, 3.45, -1.15), B(-1.4, 2.8, -1.4, 7.4, 3.45, -1.15),
                                   B(-1.4, 0.0, -1.15, -1.15, 3.45, 7.4), B(7.15, 0.0, -1.15, 7.4, 3.45, 7.4), B(-1.4, 0.0, 7.15, 7.4, 3.45, 7.4),
                                   B(0.88, 0.0, 0.35, 5.12, 2.75, 2.85), B(-1.5, 3.2, -1.7, 7.5, 6.5, 7.5)],
                            ),
    "moor_station_pax": dict(frame=_DECK_FR + _RAILS + _GANTRY + _GATES + _DRIVE
                             + [B(-1.4, 0.0, 7.5, -1.15, 6.7, 16.4), B(10.15, 0.0, 7.5, 10.4, 6.7, 16.4), B(-1.4, 3.2, 7.5, 10.4, 6.7, 16.4),
                                B(0.0, 0.0, 9.0, 1.8, 2.62, 10.4), B(5.0, 0.0, 11.8, 8.6, 0.9, 11.8 + 0.42), B(5.0, 0.0, 13.4, 8.6, 0.9, 13.82)]
                             + [B(xc - 0.15, 0.0, zc - 0.15, xc + 0.15, 3.2, zc + 0.15) for xc in (3.0, 7.0) for zc in (11.0, 16.25)],
                             **{"pass": B(-0.3, 0.0, -1.1, 9.3, 3.1, 7.4), "pass_kind": "open", "clear": [9.6, 3.1], "foot": 0.0}),
    "moor_station_cargo": dict(frame=_DECK_FR + _RAILS + _GANTRY + _GATES + _DRIVE
                               + [B(xc - 0.15, 0.0, zc - 0.15, xc + 0.15, 4.6, zc + 0.15) for xc in (-1.25, 10.25) for zc in (10.0, 13.25)]
                               + [B(-1.4, 0.0, 13.15, 2.5, 4.9, 13.4), B(6.5, 0.0, 13.15, 10.4, 4.9, 13.4), B(-1.5, 4.6, 7.4, 10.5, 4.9, 13.5)],
                               **{"pass": B(-0.3, 0.0, -1.1, 9.3, 3.1, 7.4), "pass_kind": "open", "clear": [9.6, 3.1], "foot": 0.0}),
    "moor_drop_cage_davit": dict(frame=[B(0.2, 0.0, -1.2, 2.8, 0.6, 1.4), B(1.08, 0.6, -0.32, 1.92, 8.0, 0.52)]),
}
for _pid in ("moor_line_house", "moor_station_pax", "moor_station_cargo", "moor_drop_cage_davit"):
    PIECES[_pid]["collide"] = True
MIDS = {"moor_line_house": moor_line_house(0)}   # (hand-made MIDs: the decimated one left non-manifold edges)
ANCHORS = {   # (pieces.json "anchors": [x, y, z, yaw]; read by the generator / SkyMooring)
    "moor_line_house": {"hawser": [3.0, 0.98, -3.48, 0], "signal_mast": [3.0, 6.5, 1.1, 0], "door": [3.0, 0.0, 7.4, 0]},
    "moor_station_pax": {**{f"berth_{i}": [bx, 0.0, CAB_Z, 90] for i, bx in enumerate(BERTH_X)},
                         **{f"pivot_{i}": [bx, PIVOT, CAB_Z, 90] for i, bx in enumerate(BERTH_X)},
                         **{f"rope_exit_{i}": [bx, ROPE_Y, TIP_Z - 0.7, 0] for i, bx in enumerate(BERTH_X)},
                         **{f"haul_exit_{i}": [bx, HAUL_Y, TIP_Z - 0.7, 0] for i, bx in enumerate(BERTH_X)},
                         "bull_wheel": [WHEEL[0], WHEEL[1], WHEEL[2], 0], "booth": [0.9, 0.0, 10.6, 0], "street": [4.5, 0.0, 16.4, 0]},
    "moor_station_cargo": {**{f"berth_{i}": [bx, 0.0, CAB_Z, 90] for i, bx in enumerate(BERTH_X)},
                           **{f"rope_exit_{i}": [bx, ROPE_Y, TIP_Z - 0.7, 0] for i, bx in enumerate(BERTH_X)},
                           "scale": [4.5, 0.05, -6.1, 0], "crane_hook": [4.5, 3.4, -6.0, 0], "bull_wheel": [WHEEL[0], WHEEL[1], WHEEL[2], 0]},
    "moor_drop_cage_davit": {"hook": [DAVIT_TIP[0], DAVIT_TIP[1] - 6.25, DAVIT_TIP[2] - 0.32, 0], "sheave": list(DAVIT_TIP) + [0]},
    "moor_signal_mast": {"bell": [0.0, 13.1, 0.0, 0]},
}
