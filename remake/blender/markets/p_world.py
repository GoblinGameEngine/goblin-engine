"""p_world.py -- MARKETS-WORLD's pieces, built to the kit's conventions (mk.py; requests.md W2): the food truck (two
variants), the market office, the gate house, the restrooms, a bike rack, and the floating pier market (Victory Bay's
Regatta Swap: the coordinator, 2026-10-16) -- deck modules on pontoons, a rail, a shore gangway with ramp collision and
the pier head.

Frame (every piece): +Y up, metres, origin at the footprint centre on the ground (a pier piece: on its DECK surface,
the pontoons below y 0, in the water); the FRONT faces +Z. Every builder is b(q): q=1 the full piece, q=0 its MID."""
import math

from mk import B, Mesh, piece, place, prism_zy, rot_y, sweep  # noqa: F401

# ------------------------------------------------------------------ the food truck (on a 4 x 8 m pad, hatch to +Z)
TRUCK_W, TRUCK_L = 2.3, 6.4


def _band(m, hw, ya, yb, za, zb, slot):
    """a livery band painted on the body's two sides, 1 cm proud (quads: no box through the walls)"""
    for sx in (-1, 1):
        x = sx * (hw + 0.01)
        m.quad_facing((x, ya, za), (x, ya, zb), (x, yb, zb), (x, yb, za), (sx, 0, 0), slot)


def food_truck(variant):
    def b(q):
        m = Mesh()
        hw = TRUCK_W / 2
        z0, z1 = -TRUCK_L / 2, TRUCK_L / 2
        cab = 1.7                                               # the cab at the back (-Z), the kitchen box to the front
        m.box((-hw + 0.1, 0.3, z0 + 0.2), (hw - 0.1, 0.84, z1 - 0.2), "dark")          # the chassis (under the body)
        for zc in (z0 + 1.0, z1 - 1.2):                         # wheels (outboard of the chassis)
            for sx in (-1, 1):
                m.tube((sx * (hw - 0.08), 0.42, zc), (sx * (hw + 0.02), 0.42, zc), 0.42, "dark", n=8 if q else 6)
        m.box((-hw + 0.02, 0.86, z0), (hw - 0.02, 2.25, z0 + cab + 0.06), "wall")      # the cab (its front into the box)
        m.quad_facing((-hw + 0.06, 1.45, z0 - 0.01), (hw - 0.06, 1.45, z0 - 0.01), (hw - 0.06, 2.1, z0 - 0.01),
                      (-hw + 0.06, 2.1, z0 - 0.01), (0, 0, -1), "glass")                   # the windscreen
        for sx in (-1, 1):                                                             # the cab's side windows
            x = sx * (hw + 0.01)
            m.quad_facing((x, 1.45, z0 + 0.25), (x, 1.45, z0 + cab - 0.25), (x, 2.05, z0 + cab - 0.25), (x, 2.05, z0 + 0.25), (sx, 0, 0), "glass")
        h = 2.95 if variant == 0 else 2.75
        if variant == 0:                                        # a: the square kitchen box
            m.box((-hw, 0.86, z0 + cab), (hw, h, z1), "wall")
            _band(m, hw, h - 0.25, h - 0.05, z0 + cab + 0.05, z1 - 0.05, "accent")
        else:                                                   # b: a round-roofed vintage van
            sec = []
            for k in range(9):
                a = math.pi * k / 8
                sec.append((-hw * math.cos(a), h - 0.55 + 0.55 * math.sin(a)))
            sec = [(-hw, 0.86)] + sec + [(hw, 0.86)]
            m.prism_xy(sec, [], z0 + cab, z1, "wall")
            _band(m, hw, 1.0, 1.25, z0 + cab + 0.05, z1 - 0.05, "accent")
        # the serving end (+Z): a hatch (a dark panel 1 cm proud), the counter, the awning, the menu board
        m.quad_facing((-hw + 0.25, 1.15, z1 + 0.01), (hw - 0.25, 1.15, z1 + 0.01), (hw - 0.25, 2.2, z1 + 0.01),
                      (-hw + 0.25, 2.2, z1 + 0.01), (0, 0, 1), "dark")
        m.box((-hw + 0.2, 1.05, z1 + 0.02), (hw - 0.2, 1.12, z1 + 0.35), "trim")
        aw = [(-hw - 0.1, 2.3, z1 + 0.02), (hw + 0.1, 2.3, z1 + 0.02), (hw + 0.1, 2.05, z1 + 0.6), (-hw - 0.1, 2.05, z1 + 0.6)]
        m.quad(*aw, "fabric")
        m.quad(aw[3], aw[2], aw[1], aw[0], "fabric", 0.8)
        if q:
            m.quad_facing((-0.6, 0.65, z1 + 0.012), (0.6, 0.65, z1 + 0.012), (0.6, 1.0, z1 + 0.012), (-0.6, 1.0, z1 + 0.012), (0, 0, 1), "cream")
            m.box((-0.35, h, -0.4), (0.35, h + 0.25, 0.4), "metal")                    # the roof vent
            m.box((-0.12, 2.32, z1 + 0.05), (0.12, 2.4, z1 + 0.2), "lamp")              # the hatch light
        return m
    return b


for v, tag in ((0, "a"), (1, "b")):
    piece("fm_food_truck_" + tag, "stall", food_truck(v), kind="vehicle", foot=[TRUCK_W + 0.2, TRUCK_L + 1.2], lod1="keep",
          frame=[B(-TRUCK_W / 2, 0.0, -TRUCK_L / 2, TRUCK_W / 2, 2.8, TRUCK_L / 2)],
          anchors={"vendor_0": [0.0, 0.62, TRUCK_L / 2 - 0.9, 180], "customer": [0.0, 0.0, TRUCK_L / 2 + 1.4, 180]},
          budget=900, palette="stall",
          notes="a food truck on its 4 x 8 m pad, the serving hatch, counter and awning at +Z (the court); "
                "variant %s %s" % (tag, "square box" if v == 0 else "round-roofed vintage van"))


# ------------------------------------------------------------------ small buildings
def hut(w, d, h, doors, windows, counter=False, vents=False):
    """a flat-roofed block: walls, a roof slab with an overhang, doors and windows on the +Z face, a sign board"""
    def b(q):
        m = Mesh()
        m.box((-w / 2, 0.0, -d / 2), (w / 2, h, d / 2), "wall")
        m.box((-w / 2 - 0.3, h, -d / 2 - 0.3), (w / 2 + 0.3, h + 0.22, d / 2 + 0.3), "roof")
        m.box((-w / 2 - 0.05, 0.0, -d / 2 - 0.05), (w / 2 + 0.05, 0.25, d / 2 + 0.05), "concrete")       # the plinth
        for x in doors:
            m.box((x - 0.5, 0.25, d / 2 - 0.01), (x + 0.5, 2.3, d / 2 + 0.03), "dark")
            if q:
                m.box((x - 0.6, 2.3, d / 2), (x + 0.6, 2.38, d / 2 + 0.06), "trim")
        for x in windows:
            m.box((x - 0.7, 1.12 if counter else 1.0, d / 2 - 0.01), (x + 0.7, 2.0, d / 2 + 0.03), "glass")
            if q and not counter:
                m.box((x - 0.78, 0.92, d / 2), (x + 0.78, 1.0, d / 2 + 0.12), "trim")
        if counter:
            m.box((-w / 2 + 0.3, 0.95, d / 2), (w / 2 - 0.3, 1.05, d / 2 + 0.3), "trim")
        m.box((-w / 2 + 0.4, h - 0.55, d / 2), (w / 2 - 0.4, h - 0.1, d / 2 + 0.06), "cream")      # the board
        if q and vents:
            for x in (-w / 4, w / 4):
                m.box((x - 0.3, h + 0.22, -0.3), (x + 0.3, h + 0.5, 0.3), "metal")
        if q:
            m.box((-0.15, h - 0.95, d / 2 + 0.05), (0.15, h - 0.75, d / 2 + 0.25), "lamp")           # the door light
        return m
    return b


for pid, w, d, h, doors, wins, ctr, vents, note in (
        ("fm_office", 8.0, 6.0, 3.2, [-2.2], [0.6, 2.6], False, True, "the market office: the manager, the warden, the clerk"),
        ("fm_gatehouse", 4.0, 3.0, 2.8, [], [0.0], True, False, "the gate house: tickets, information, lost and found"),
        ("fm_restroom", 6.0, 8.0, 3.0, [-1.6, 1.6], [], False, True, "the restrooms: two doors to the front")):
    piece(pid, "building", hut(w, d, h, doors, wins, ctr, vents), kind="building", foot=[w, d], lod1="keep",
          frame=[B(-w / 2, 0.0, -d / 2, w / 2, h, d / 2)], budget=500, palette="shed", notes=note)


def bike_rack(q):
    m = Mesh()
    n = 6 if q else 4
    for k in range(5):
        x = -1.2 + 0.6 * k
        pts = [(x, 0.0, -0.35)] + [(x, 0.6 + 0.25 * math.sin(math.pi * j / n), -0.35 + 0.7 * j / n) for j in range(n + 1)] + [(x, 0.0, 0.35)]
        sweep(m, pts, 0.025, "steel", n=5 if q else 4)
    return m


piece("fm_bike_rack", "lot", bike_rack, kind="decor", foot=[3.0, 0.8], lod1="drop", frame=[B(-1.25, 0.0, -0.4, 1.25, 0.9, 0.4)],
      budget=500, palette="lot", notes="five hoop stands for bicycles (the pier market's shore end: Victory Bay is car-light)")


# ------------------------------------------------------------------ the floating pier (Victory Bay's Regatta Swap)
DECK_T = 0.25            # the deck's thickness (boards and stringers)
PONT_H = 0.7             # the pontoons' depth under the deck


def pier_deck(n):
    """an n x n m deck module: boards across x, stringers along z, a pontoon each side, fender strips"""
    def b(q):
        m = Mesh()
        h = n / 2
        m.box((-h, -DECK_T, -h), (h, -0.05, h), "frame")                                # the stringer bed
        nb = int(n / 0.3) if q else int(n / 1.0)
        bw = n / nb
        for k in range(nb):                                                            # the deck boards
            z = -h + k * bw
            m.box((-h, -0.05, z + 0.006), (h, 0.0, z + bw - 0.006), "wood", 1.0 - 0.06 * (k % 3))
        for sx in (-1, 1):                                                             # the pontoons
            x0, x1 = sorted((sx * (h - 0.25), sx * (h - 1.35)))
            m.box((x0, -DECK_T - PONT_H, -h + 0.2), (x1, -DECK_T, h - 0.2), "concrete")
            m.box((min(sx * h, sx * (h + 0.06)), -0.22, -h), (max(sx * h, sx * (h + 0.06)), -0.02, h), "dark")   # fenders
        return m
    return b


for n in (3, 6):
    piece("fm_pier_deck_%d" % n, "pier", pier_deck(n), kind="floor", foot=[float(n), float(n)], lod1="keep",
          frame=[B(-n / 2, -DECK_T, -n / 2, n / 2, 0.0, n / 2)], walk=[[-n / 2, -n / 2, n / 2, n / 2, 0.0]],
          budget=600 if n == 6 else 300, palette="pier", ground=False,
          notes="a %d x %d m floating deck module (boards, stringers, two pontoons, fenders); the deck's top at y 0 "
                "(the water %.2f m below), tile it edge to edge" % (n, n, DECK_T + 0.3))


def pier_rail(q):
    m = Mesh()
    for k in range(4):
        x = -3.0 + 2.0 * k
        m.box((x - 0.05, 0.0, -0.05), (x + 0.05, 1.05, 0.05), "wood")
    m.box((-3.0, 1.0, -0.06), (3.0, 1.08, 0.06), "wood")
    if q:
        m.box((-3.0, 0.5, -0.03), (3.0, 0.56, 0.03), "wood", 0.9)
        m.tube((-3.0, 0.78, 0.0), (3.0, 0.78, 0.0), 0.018, "rope", n=4)
    return m


piece("fm_pier_rail_6", "pier", pier_rail, kind="rail", foot=[6.0, 0.12], lod1="keep", frame=[B(-3.0, 0.0, -0.06, 3.0, 1.08, 0.06)],
      budget=200, palette="pier", ground=False, notes="6 m of the pier's edge rail: posts every 2 m, a top rail, a mid rail and a rope")

RAMP_L, RAMP_W, RAMP_RISE = 12.0, 2.6, 1.0


def pier_ramp(q):
    """the gangway: from the shore landing (z -6, y +RAMP_RISE) down to the deck (z +6, y 0), stringers and handrails"""
    m = Mesh()
    hw = RAMP_W / 2
    hl = RAMP_L / 2
    y0, y1 = RAMP_RISE, 0.0
    t = 0.12
    prism_zy(m, [(-hl, y0 - t), (hl, y1 - t), (hl, y1), (-hl, y0)], -hw, hw, "wood")             # the deck slab
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (hw + 0.005), sx * (hw + 0.09)))
        prism_zy(m, [(-hl, y0 - 0.25), (hl, y1 - 0.25), (hl, y1 + 0.12), (-hl, y0 + 0.12)], x0, x1, "frame")   # stringers
        xr = sx * (hw + 0.05)
        sweep(m, [(xr, y0 + 1.0, -hl), (xr, y1 + 1.0, hl)], 0.03, "steel", n=5 if q else 4)               # the handrail
        for k in range(4):
            z = -hl + 0.1 + (RAMP_L - 0.2) * k / 3
            y = y0 + (y1 - y0) * (z + hl) / RAMP_L + 0.12
            m.box((xr - 0.03, y, z - 0.03), (xr + 0.03, y0 + (y1 - y0) * (z + hl) / RAMP_L + 0.97, z + 0.03), "steel")
    return m


piece("fm_pier_ramp", "pier", pier_ramp, kind="floor", foot=[RAMP_W + 0.16, RAMP_L], lod1="keep", collide="frame",
      frame=[B(-RAMP_W / 2 - 0.09, -0.25, -RAMP_L / 2, -RAMP_W / 2, RAMP_RISE + 1.03, RAMP_L / 2),
             B(RAMP_W / 2, -0.25, -RAMP_L / 2, RAMP_W / 2 + 0.09, RAMP_RISE + 1.03, RAMP_L / 2)],
      ramps=[[[-RAMP_W / 2, RAMP_RISE, -RAMP_L / 2], [RAMP_W / 2, RAMP_RISE, -RAMP_L / 2], [RAMP_W / 2, 0.0, RAMP_L / 2], [-RAMP_W / 2, 0.0, RAMP_L / 2]]],
      budget=400, palette="pier", ground=False,
      notes="the shore gangway: %.0f m long, %.1f m wide, %.1f m from the landing (z -%.0f) down to the deck (z +%.0f); "
            "walk it on its `ramps` quad, the side frames are the rails" % (RAMP_L, RAMP_W, RAMP_RISE, RAMP_L / 2, RAMP_L / 2))


def pier_bollard(q):
    m = Mesh()
    m.cyl(0.0, 0.0, 0.16, 0.0, 0.55, "dark", n=8 if q else 6)
    m.cyl(0.0, 0.0, 0.22, 0.55, 0.62, "dark", n=8 if q else 6)
    if q:
        m.tube((-0.25, 0.4, 0.0), (0.25, 0.4, 0.0), 0.05, "dark", n=4)
    return m


piece("fm_pier_bollard", "pier", pier_bollard, kind="decor", foot=[0.5, 0.44], lod1="drop", frame=[B(-0.16, 0.0, -0.16, 0.16, 0.62, 0.16)],
      budget=120, palette="pier", ground=False, notes="a mooring bollard on the deck (the pier head's anchor points: the islands' hawsers make fast here)")
