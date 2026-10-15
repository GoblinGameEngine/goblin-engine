#!/usr/bin/env python3
"""vignette.py -- assemble small test scenes from the warren kit (checks the frames fit: walls on faces, corners,
slabs, crowns) and write palette-baked glbs for rendering:

  * medina: a bending lane between blank zellige walls, a studded portal, a sabat (a room over the lane), a riad
    court with galleries and a fountain, a square minaret, lanterns, a cane awning, a shoring beam;
  * kowloon: an alley between 8-storey towers -- grilles, cages, cantilevered storeys, a covered stretch with the
    alley ceiling, blade signs and sign arms, AC units and pipes, a rooftop village of shacks, tanks, aerials and a
    playground, cables across.

  ~/.venvs/ssc-assets/bin/python remake/blender/sky/warren_kit/vignette.py
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geom  # noqa: E402
from build import PREV, hex_rgb  # noqa: E402
from pieces import PALETTES, PIECES  # noqa: E402

FACE = {"+z": 0, "+x": 90, "-z": 180, "-x": 270}
DIR = {"+z": (0, 1), "+x": (1, 0), "-z": (0, -1), "-x": (-1, 0)}
_cache = {}


def piece(pid):
    if pid not in _cache:
        _cache[pid] = PIECES[pid]["build"]()
    return _cache[pid]


class Scene:
    def __init__(self, civ):
        self.civ = civ
        self.by_pal = {}                       # palette index -> Mesh

    def _put(self, pid, xf, pal=0):
        m = self.by_pal.setdefault(pal, geom.Mesh())
        m.add(piece(pid), xf)

    @staticmethod
    def centre(i, j, k):
        return 3.0 * i + 1.5, 3.2 * k, 3.0 * j + 1.5

    def cell(self, pid, i, j, k, rot=0, pal=0, dy=0.0):
        cx, cy, cz = self.centre(i, j, k)
        r = geom.rot_y(rot)
        self._put(pid, lambda p: _add(r(p), (cx, cy + dy, cz)), pal)

    def wall(self, pid, i, j, k, face, pal=0, dy=0.0):
        cx, cy, cz = self.centre(i, j, k)
        dx, dz = DIR[face]
        r = geom.rot_y(FACE[face])
        self._put(pid, lambda p: _add(r(p), (cx + 1.5 * dx, cy + dy, cz + 1.5 * dz)), pal)

    def corner(self, pid, i, j, k, quad, pal=0):
        """quad: which corner of cell (i, j): (+1/-1, +1/-1) toward +X/+Z"""
        cx, cy, cz = self.centre(i, j, k)
        sx, sz = quad
        rot = {(1, 1): 0, (1, -1): 90, (-1, -1): 180, (-1, 1): 270}[(sx, sz)]
        r = geom.rot_y(rot)
        self._put(pid, lambda p: _add(r(p), (cx + 1.5 * sx, cy, cz + 1.5 * sz)), pal)

    def export(self, path):
        pals = PALETTES[self.civ]
        nodes = []
        out = geom.Mesh()
        for pal, m in self.by_pal.items():
            cols = {k: hex_rgb(v) for k, v in pals[pal % len(pals)].items()}
            # bake each palette's colours by exporting separately
            nodes.append((f"{self.civ}_p{pal}", m, cols))
        size = 0
        # one glb per palette set, merged by writing all nodes (export_glb bakes one palette per call: do it per node)
        parts = []
        for name, m, cols in nodes:
            tmp = path.replace(".glb", f"_{name}.glb")
            size += geom.export_glb(tmp, [(name, m)], colours=cols)
            parts.append(tmp)
        return parts, sum(m.count() for _, m, _ in nodes)


def _add(p, o):
    return (p[0] + o[0], p[1] + o[1], p[2] + o[2])


# ------------------------------------------------------------------ medina
def medina():
    s = Scene("maghrebi_medina")
    rnd = random.Random(3)
    # a lane along X at j = 2 (i 0..7), bending: from i 4 on it steps to j 3
    lane = {(i, 2) for i in range(0, 5)} | {(i, 3) for i in range(4, 9)}
    court = {(i, j) for i in range(1, 4) for j in range(5, 8)}           # the riad's court (open to the sky)
    occupied = {}
    for i in range(-1, 10):
        for j in range(0, 10):
            if (i, j) in lane or (i, j) in court:
                continue
            occupied[(i, j)] = 3 if (i + j) % 3 else 2
    occupied[(6, 0)] = 0                                                  # (a gap for the minaret's plot)
    # paving
    for (i, j) in lane:
        s.cell("pave_lane", i, j, 0)
    for (i, j) in court:
        s.cell("pave_court", i, j, 0)
    s.cell("fountain_riad", 2, 6, 0)
    # the mass: per cell, storeys; faces onto the lane / court / outside get walls
    for (i, j), h in occupied.items():
        if h <= 0:
            continue
        pal = (i * 7 + j * 3) % 2 if (i + j) % 5 else 3
        for k in range(h):
            for face, (dx, dz) in DIR.items():
                n = (i + dx, j + dz)
                if n in occupied and occupied[n] > k:
                    continue
                on_lane = n in lane
                on_court = n in court
                if on_lane:
                    if k == 0:
                        pid = "wall_door_portal_k" if (i, j) == (2, 1) else ("wall_zellij_k" if (i + j) % 2 else "wall_plain_k")
                        if (i, j) == (3, 4):
                            pid = "wall_fountain_k"
                    elif k == 1:
                        pid = "wall_window_s_k" if (i * 3 + k) % 3 == 0 else "wall_plain_k"
                    else:
                        pid = "wall_bay_box_k" if (i + j) % 4 == 0 else ("wall_screen_k" if (i + j) % 3 == 0 else "wall_window_s_k")
                elif on_court:
                    pid = "wall_arch_horseshoe_k" if k == 0 else ("wall_balcony_timber_k" if k == 1 else "wall_screen_k")
                else:
                    pid = "wall_plain_k" if k == 0 else ("wall_window_s_k" if rnd.random() < 0.4 else "wall_plain_k")
                s.wall(pid, i, j, k, face, pal)
        # the roof: a terrace with a parapet on the exposed edges
        s.cell("roof_terrace", i, j, h, pal=pal, dy=0.0)
        for face, (dx, dz) in DIR.items():
            n = (i + dx, j + dz)
            if n in occupied and occupied[n] >= h:
                continue
            s.wall("edge_parapet_plain_k" if (i + j) % 3 else "edge_parapet_crenel_k", i, j, h, face, pal)
        for (sx, sz) in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
            nx, nz = (i + sx, j), (i, j + sz)
            if (nx not in occupied or occupied[nx] < 1) and (nz not in occupied or occupied[nz] < 1) and (i + j) % 2 == 0:
                s.corner("corner_round_k", i, j, 0, (sx, sz), pal)
    # the sabat: a room over the lane at (1, 2), level 1, its floor on cedar beams; the lane passes under
    s.cell("sabat_beams", 1, 2, 1)
    for face in ("+x", "-x"):
        s.wall("wall_screen_k" if face == "+x" else "wall_window_s_k", 1, 2, 1, face, 1)
    s.cell("roof_terrace", 1, 2, 2, pal=1)
    s.wall("edge_parapet_plain_k", 1, 2, 2, "+x", 1)
    s.wall("edge_parapet_plain_k", 1, 2, 2, "-x", 1)
    # lane life: lanterns, a cane awning, a shoring beam, festoon
    s.wall("ov_lantern", 2, 1, 0, "+z", dy=2.4)
    s.wall("ov_lantern", 5, 2, 0, "+z", dy=2.4)
    s.cell("ov_awning_cane", 3, 2, 0)
    s.cell("ov_awning_cane", 5, 3, 0, rot=90)
    s.cell("shoring_beam", 6, 3, 0, rot=90)
    s.cell("ov_festoon", 7, 3, 0, rot=90)
    s.cell("ov_stall", 8, 3, 0, rot=90)
    s.cell("ov_dish", 4, 1, 3)
    # the minaret on (6, 0): base, three shafts, top; a green hip mosque roof beside it
    s.cell("minaret_base", 6, 0, 0)
    for k in range(1, 4):
        s.cell("minaret_shaft", 6, 0, k)
    s.cell("minaret_top", 6, 0, 4)
    s.cell("green_hip", 7, 0, 2)
    return s


# ------------------------------------------------------------------ kowloon
def kowloon():
    s = Scene("kowloon_walled")
    rnd = random.Random(5)
    alley = {(i, 2) for i in range(0, 9)}
    occupied = {}
    for i in range(0, 9):
        for j in range(0, 5):
            if (i, j) in alley:
                continue
            occupied[(i, j)] = 6 + ((i * 5 + j * 3) % 4)
    covered = {(i, 2) for i in range(3, 6)}                               # the mass closes over the alley here, from level 3
    for (i, j) in alley:
        s.cell("pave_lane", i, j, 0, pal=0)
    for (i, j), h in occupied.items():
        pal = (i * 3 + j) % 4
        for k in range(h):
            for face, (dx, dz) in DIR.items():
                n = (i + dx, j + dz)
                if n in occupied and occupied[n] > k:
                    continue
                if n in covered and k >= 3:
                    continue
                if n in alley and k == 0:
                    pid = "wall_shopfront_a_t" if (i % 2) else "wall_shopfront_b_t"
                elif k < 4:
                    pid = "wall_window_grille_t" if rnd.random() < 0.6 else "wall_window_m_t"
                else:
                    r = rnd.random()
                    pid = "wall_balcony_cage_t" if r < 0.35 else ("wall_cantilever_step_t" if r < 0.55 and n in alley else
                                                                  ("wall_window_grille_t" if r < 0.8 else "wall_tower_seam_t"))
                s.wall(pid, i, j, k, face, pal)
                if k > 0 and rnd.random() < 0.3:
                    s.wall("ov_ac", i, j, k, face, dy=0.4 + rnd.random() * 0.8)
                if k == 1 and n in alley:
                    s.wall("ov_sign_blade" if i % 2 else "ov_sign_box", i, j, k, face, dy=0.3)
                if k == 2 and n in alley and i % 3 == 0:
                    s.wall("ov_sign_arm", i, j, k, face)
                if face in ("+x",) and k == 0 and rnd.random() < 0.3:
                    s.wall("ov_pipe_run", i, j, k, face)
        s.cell("roof_tin" if (i + j) % 2 else "roof_terrace", i, j, h, pal=pal)
        for face, (dx, dz) in DIR.items():
            n = (i + dx, j + dz)
            if n in occupied and occupied[n] >= h:
                continue
            s.wall("edge_rail_t", i, j, h, face, pal)
        roll = rnd.random()
        if roll < 0.3:
            s.cell(rnd.choice(["ov_shack_a", "ov_shack_b", "ov_shack_c"]), i, j, h, rot=rnd.choice([0, 90, 180, 270]), pal=pal)
        elif roll < 0.5:
            s.cell("ov_tank", i, j, h)
        elif roll < 0.7:
            s.cell("ov_antennas", i, j, h)
        elif roll < 0.78:
            s.cell("ov_playground", i, j, h)
    # the covered stretch: the mass over the alley from level 3, its ceiling under it
    for (i, j) in covered:
        s.cell("alley_ceiling", i, j, 3)
        s.cell("floor_slab", i, j, 3)
        for k in range(3, 7):
            for face in ("+x", "-x"):
                n = (i + DIR[face][0], j)
                if n in covered:
                    continue
                s.wall("wall_window_grille_t", i, j, k, face, 1)
        s.cell("roof_terrace", i, j, 7, pal=1)
    for i in (1, 2, 6, 7):
        s.cell("ov_cables", i, 2, 0, rot=90)
        s.cell("alley_ceiling", i, 2, 1) if i == 6 else None
    s.wall("ov_fluoro", 2, 1, 0, "+z", dy=2.6)
    s.wall("ov_laundry", 1, 1, 4, "+z")
    s.wall("ov_laundry", 7, 3, 5, "-z")
    return s


if __name__ == "__main__":
    os.makedirs(PREV, exist_ok=True)
    for name, sc in (("medina", medina()), ("kowloon", kowloon())):
        parts, tris = sc.export(os.path.join(PREV, f"vig_{name}.glb"))
        print(name, tris, "tris", len(parts), "glbs")
        with open(os.path.join(PREV, f"vig_{name}.list"), "w") as f:
            f.write("\n".join(parts))
