"""ramps.py -- the walking surfaces of the kit's stairs, explicit (pieces.json "collide": "ramp" + "ramp").

The player has no step-up: a stair collides as smooth inclined quads laid over its treads' nosings. Each entry is a
list of quads in the piece's own frame, each quad four points [x, y, z] in order round its edge (winding is not
meaningful: collide both faces): a straight flight is one quad (more with landings), a spiral a run of quads round
its helix. The runtime
builds one collider from them (backface_collision on, so winding never matters) and none from the stair's triangles.
"""
import math

HB, ST = 1.5, 3.2


def _flight(x0, x1, z0, z1, y0, y1):
    """one inclined quad from (z0, y0) to (z1, y1) between x0 and x1"""
    return [[x0, y0, z0], [x0, y1, z1], [x1, y1, z1], [x1, y0, z0]]


def _flight_x(z0, z1, xa, xb, ya, yb):
    """an inclined quad climbing along +X (stairs up a face)"""
    return [[xa, ya, z0], [xb, yb, z0], [xb, yb, z1], [xa, ya, z1]]


def _helix(r0, r1, a0, a1, y0, y1, n, cx=0.0, cz=0.0, zs=1.0):
    """n quads round a helix between radii r0, r1 from angle a0 (height y0) to a1 (y1); z = cz + zs * r sin(a)"""
    out = []
    for k in range(n):
        ta, tb = a0 + (a1 - a0) * k / n, a0 + (a1 - a0) * (k + 1) / n
        ya, yb = y0 + (y1 - y0) * k / n, y0 + (y1 - y0) * (k + 1) / n

        def p(r, t, y):
            return [round(cx + r * math.cos(t), 4), round(y, 4), round(cz + zs * r * math.sin(t), 4)]
        out.append([p(r0, ta, ya), p(r1, ta, ya), p(r1, tb, yb), p(r0, tb, yb)])
    return out


RAMPS = {
    "step_low_1": [_flight(-HB, HB, -HB, HB, 0.0, 0.2)],
    "step_low_4": [_flight(-HB, HB, -HB, HB, 0.0, 0.8)],
    "steps_up": [_flight(-1.4, 1.4, -HB, HB, 0.0, 1.6)],
    "stair_run": [_flight(-0.65, 0.65, -HB, 4.5, 0.0, ST)],
    "stair_street_long": [_flight(-HB, HB, -HB, 1.2, 0.0, 1.6), _flight(-HB, HB, 1.2, 2.4, 1.6, 1.6), _flight(-HB, HB, 2.4, 5.1, 1.6, ST)],
    "stair_painted": [_flight(-1.3, 1.3, -HB, HB, 0.0, 1.6)],
    "stair_knight": [_flight(-HB, HB, -HB, 4.5, 0.0, 1.6)],
    "ghat_steps_wide": [_flight(-HB, HB, -HB, 0.9, 0.0, -1.4), _flight(-HB, HB, 0.9, 2.1, -1.6, -1.6), _flight(-HB, HB, 2.1, 4.5, -1.6, -3.2)],
    "water_steps_private": [_flight(-HB + 0.02, -0.28, -HB, 1.4, 0.0, -1.4), _flight(-HB + 0.02, -0.28, 1.4, HB, -1.55, -1.55)],
    "pier_steps_khlong": [_flight(-0.8, 0.8, -HB, -0.4, 0.0, 0.0), _flight(-0.7, 0.7, -0.4, 1.58, 0.0, -1.98)],
    "stair_steel_external": [_flight_x(0.05, 0.9, -1.45, 0.85, 0.0, ST), _flight_x(0.05, 0.9, 0.85, 1.5, ST, ST)],
    "stair_external_white": [_flight_x(0.004, 0.85, -HB, HB, 0.0, ST)],
    "stair_spiral": _helix(0.1, 1.3, 0.0, math.tau, ST / 16, ST, 8, zs=-1.0),
    "stair_plex_outdoor": _helix(0.15, 1.25, math.pi / 2, math.pi / 2 + 1.5 * math.pi, ST * 0.9 / 16, ST * 0.9, 8, cz=0.1)
                          + [_flight(-1.4, 1.4, -HB, -0.6, ST, ST)],
    "stair_spiral_courtyard": _helix(0.1, 1.0, -math.pi / 2, 1.5 * math.pi, ST * 0.92 / 14, ST * 0.92, 8) + [_flight(-1.0, 1.0, -HB, -0.9, ST, ST)],
}
