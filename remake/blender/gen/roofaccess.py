"""
roofaccess.py -- roof access for a flat-roofed building (the sky islands, research/sky_islands/00_plan.md: "the
buildings on the islands will all have roof access").  Built only for records with traits.roof_access, so no other
building changes.

fire_escape(): an iron switchback stair up an outside wall, from the ground to a landing at every upper floor and on
to a platform over the parapet, with a short stair down onto the roof.  Two lanes (even flights against the wall,
odd ones outside them) so every flight has a whole storey of headroom; landings span both lanes at the ends.
Walkable: each flight is gblib.stairs (an invisible ramp collides), landings and the platform are -col boxes, the
rails collide as thin boxes (spindle_rail into a -col part).

The wall is given in its own frame: `o` metres out from the wall's outer face, `a` along it.  axis "x": the wall is
the plane x = w (a side wall), o runs along sign*x, a is y; axis "y": the plane y = w (a front or rear wall), o runs
along sign*y, a is x.
"""
import math

import gblib as g

LANE = 1.0            # flight width
GAP = 0.1             # between the lanes
LAND = 1.2            # landing length along the wall
RISE = 0.19
RUN = 0.25


def _iron(b):
    return b.mat("fire_iron", color=(0.13, 0.14, 0.15), rough=0.55, metal=0.5)


class _Frame:
    def __init__(self, axis, w, sign):
        self.axis, self.w, self.sign = axis, w, sign

    def p(self, o, a, z=None):
        q = (self.w + self.sign * o, a) if self.axis == "x" else (a, self.w + self.sign * o)
        return q if z is None else (q[0], q[1], z)

    def d(self, do, da):
        return (self.sign * do, da) if self.axis == "x" else (da, self.sign * do)

    def box(self, part, o0, o1, a0, a1, z0, z1, mat):
        p0, p1 = self.p(o0, a0), self.p(o1, a1)
        part.box((p0[0], p0[1], z0), (p1[0], p1[1], z1), mat)

    def stairs(self, b, name, o_lo, o_hi, a_start, along, z, rise, n, run, mat):
        """A flight across o_lo..o_hi climbing along a (along=+1) or against it (-1) from a_start."""
        d = self.d(0, along)
        # gblib.stairs' width runs to the left of the climb: side = (-d.y, d.x); start on the edge that keeps it
        # inside o_lo..o_hi
        for o_s in (o_lo, o_hi):
            sx, sy = self.p(o_s, a_start)
            ox, oy = self.p((o_lo + o_hi) / 2, a_start)
            side = (-d[1], d[0])
            if (ox - sx) * side[0] + (oy - sy) * side[1] > 0:
                g.stairs(b, name, (sx, sy, z), d, o_hi - o_lo, rise, n, run, mat)
                return

    def stairs_out(self, b, name, o_start, a_lo, a_hi, z, rise, n, run, mat):
        """A flight across a_lo..a_hi climbing outward (+o) from o_start."""
        d = self.d(1, 0)
        side = (-d[1], d[0])
        for a_s in (a_lo, a_hi):
            sx, sy = self.p(o_start, a_s)
            ox, oy = self.p(o_start, (a_lo + a_hi) / 2)
            if (ox - sx) * side[0] + (oy - sy) * side[1] > 0:
                g.stairs(b, name, (sx, sy, z), d, a_hi - a_lo, rise, n, run, mat)
                return


def fire_escape(b, axis, w, sign, a0, a1, levels, wall_top, parapet, te, name="fire_escape"):
    """w: the wall's outer face; sign: +1 if outside is +axis; a0..a1: the wall's usable stretch; levels: the upper
    floors' floor heights, ascending; wall_top: the roof's top surface; parapet: its height; te: the parapet's
    thickness.  Returns the escape's (o, a) extent: (0, depth, a_lo, a_hi)."""
    F = _Frame(axis, w, sign)
    mat = _iron(b)
    z_top = wall_top + parapet + 0.12                     # the platform, over the coping
    zs = [0.0] + [z for z in levels if z > 0.5] + [z_top]
    rises = [zs[k + 1] - zs[k] for k in range(len(zs) - 1)]
    ns = [max(2, math.ceil(r / RISE)) for r in rises]
    Lf = max(ns) * RUN
    if a1 - a0 < 2 * LAND + Lf:
        Lf = max(a1 - a0 - 2 * LAND, max(ns) * 0.2)
    ac = (a0 + a1) / 2
    aA = ac - (Lf / 2 + LAND)                             # landing A [aA, aA + LAND], the flights, landing B
    aB = aA + LAND + Lf
    lanes = [(0.05 + li * (LANE + GAP), 0.05 + li * (LANE + GAP) + LANE) for li in range(2)]
    o_out = lanes[1][1]
    deck = b.part(name + "-col")
    rails = b.part(name + "_rail-col")
    end = "A"
    for k, (rise, n) in enumerate(zip(rises, ns)):
        lo, hi = lanes[k % 2]
        run = Lf / n
        z0, z1 = zs[k], zs[k + 1]
        if end == "A":
            F.stairs(b, f"{name}_f{k}", lo, hi, aA + LAND, +1, z0, rise, n, run, mat)
            end = "B"
        else:
            F.stairs(b, f"{name}_f{k}", lo, hi, aB, -1, z0, rise, n, run, mat)
            end = "A"
        if k % 2 == 1:                                    # the outer rail beside an outer-lane flight
            s0, s1 = (aA + LAND, aB) if end == "B" else (aB, aA + LAND)
            g.raking_rail(rails, F.p(o_out, s0, z0 + 0.95), F.p(o_out, s1, z1 + 0.95), mat)
        la = (aB, aB + LAND) if end == "B" else (aA, aA + LAND)
        if k == len(rises) - 1:
            # the platform runs in over the parapet; a stair down onto the roof, climbing outward to its inner edge
            o_in = -(te + 0.1)
            F.box(deck, o_in, o_out, la[0], la[1], z1 - 0.08, z1, mat)
            ni = max(2, math.ceil((z1 - wall_top) / RISE))
            F.stairs_out(b, f"{name}_roof", o_in - ni * RUN, la[0] + 0.1, la[0] + 0.1 + LANE, wall_top, z1 - wall_top, ni, RUN,
                         mat)
        else:
            F.box(deck, 0.0, o_out, la[0], la[1], z1 - 0.08, z1, mat)
        a_end = la[0] if end == "A" else la[1]
        g.spindle_rail(rails, [F.p(o_out, la[0]), F.p(o_out, la[1])], z1, 1.0, 0.6, mat)
        g.spindle_rail(rails, [F.p(0.0, a_end), F.p(o_out, a_end)], z1, 1.0, 0.6, mat)
    # posts under the landings' outer corners
    for aa in (aA + 0.05, aA + LAND - 0.05, aB + 0.05, aB + LAND - 0.05):
        F.box(deck, o_out - 0.1, o_out - 0.04, aa - 0.03, aa + 0.03, 0.0, zs[-1], mat)
    return 0.0, o_out, aA, aB + LAND
