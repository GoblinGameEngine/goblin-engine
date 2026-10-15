"""lattice.py -- the warren's 3D cell lattice over a sky island's site (FORMAT.md: 3 m x 3 m x 3.2 m cells).

The plan (2D, one value per column) says what the ground is: outside, rim walk, free land, water, green, street...;
the volume (3D) says which cells are rooms, and who built them when.  Deterministic: everything from the island seed.
"""
import base64
import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.prepared import prep

CELL = 3.0
STOREY = 3.2
LEVELS = 16

# plan classes (2D)
OUT, RIM, FREE, WATER, BANK, GREEN, PASTURE, MAIN, PLAZA, GATE, LANE, COURT, RESERVED, LOT, ARTERY = range(15)
PLAN_NAMES = ["out", "rim", "free", "water", "bank", "green", "pasture", "main", "plaza", "gate", "lane", "court",
              "reserved", "lot", "artery"]
WALKABLE = {RIM, BANK, GREEN, MAIN, PLAZA, GATE, LANE, COURT, RESERVED, ARTERY}
PUBLIC = {RIM, BANK, GREEN, MAIN, PLAZA, GATE, LANE, RESERVED, ARTERY}       # (courts are the house's own)
STREETS = {MAIN, PLAZA, GATE, LANE, ARTERY}

# uses (FORMAT.md)
HOME, SHOP, WORK, CIVIC, STAIR, PASSAGE = range(6)


class Lattice:
    def __init__(self, isl, seed):
        self.isl = isl
        self.seed = seed
        f = isl["faces"]
        self.x0 = math.floor(float(f["N"]) / CELL) * CELL
        self.z0 = math.floor(float(f["E"]) / CELL) * CELL
        self.nx = int(math.ceil((float(f["S"]) - self.x0) / CELL))
        self.nz = int(math.ceil((float(f["W"]) - self.z0) / CELL))
        self.L = LEVELS
        self.plan = np.full((self.nx, self.nz), OUT, np.uint8)
        self.ground = np.zeros((self.nx, self.nz), np.float32)    # deck height at the column centre
        self.gk = np.zeros((self.nx, self.nz), np.int16)          # the column's ground level
        self.occ = np.zeros((self.nx, self.nz, self.L), np.uint8)       # 1 a room
        self.epoch = np.zeros((self.nx, self.nz, self.L), np.uint8)
        self.unit = np.full((self.nx, self.nz, self.L), -1, np.int32)
        self.lift = np.zeros((self.nx, self.nz), np.int16)       # storeys a column stands on stilts
        self.block = np.zeros((self.nx, self.nz, self.L), bool)          # kept empty (tether corridors)
        self.lot = np.full((self.nx, self.nz), -1, np.int32)              # the founding lot of a column
        self.units = []          # [{use, lot, cells, homes, floors}]
        self.lots = []           # [{cells: [(i, j)], court: [(i, j)], use, kind, door: (i, j, rot)}]
        self.notes = []
        self._height()
        self._site()

    # ------------------------------------------------------------------ geometry
    def centre(self, i, j, k=0):
        return (self.x0 + CELL * i + CELL / 2, STOREY * k, self.z0 + CELL * j + CELL / 2)

    def cell_of(self, x, z):
        return int((x - self.x0) // CELL), int((z - self.z0) // CELL)

    def inb(self, i, j):
        return 0 <= i < self.nx and 0 <= j < self.nz

    def _height(self):
        hg = self.isl["height"]
        a = np.frombuffer(base64.b64decode(hg["data"]), "<i2").astype(np.float32) / 100.0
        self._hgrid = a.reshape(int(hg["nz"]), int(hg["nx"]))
        self._hg = hg

    def deck_y(self, x, z):
        hg = self._hg
        fx = (x - float(hg["x0"])) / float(hg["step"])
        fz = (z - float(hg["z0"])) / float(hg["step"])
        nx, nz = int(hg["nx"]), int(hg["nz"])
        ix = min(max(int(math.floor(fx)), 0), nx - 2)
        iz = min(max(int(math.floor(fz)), 0), nz - 2)
        tx = min(max(fx - ix, 0.0), 1.0)
        tz = min(max(fz - iz, 0.0), 1.0)
        H = self._hgrid
        a = H[iz, ix] * (1 - tx) + H[iz, ix + 1] * tx
        b = H[iz + 1, ix] * (1 - tx) + H[iz + 1, ix + 1] * tx
        return float(a * (1 - tz) + b * tz)

    # ------------------------------------------------------------------ the site
    def _site(self):
        isl = self.isl
        outline = Polygon([(p[0], p[1]) for p in isl["outline"]]).buffer(0)
        self.outline = outline
        inner = prep(outline.buffer(-4.5))              # the fence band and a rim walk kept free
        edge = prep(outline.buffer(-1.0))
        water = [Polygon([(p[0], p[1]) for p in w["outline"]]).buffer(0) for w in isl.get("water", [])]
        self.water_polys = water
        wp = [prep(w.buffer(0.8)) for w in water]
        bank = [prep(w.buffer(5.5)) for w in water]
        past = [(prep(Polygon([(p[0], p[1]) for p in pa["outline"]]).buffer(0)), pa["kind"]) for pa in isl.get("pastures", [])]
        for i in range(self.nx):
            for j in range(self.nz):
                x, _, z = self.centre(i, j)
                pt = Point(x, z)
                g = self.deck_y(x, z)
                self.ground[i, j] = g
                self.gk[i, j] = max(0, int(math.ceil((g - 0.4) / STOREY)))
                if not edge.contains(pt):
                    continue
                if not inner.contains(pt):
                    self.plan[i, j] = RIM
                    continue
                if any(w.contains(pt) for w in wp):
                    self.plan[i, j] = WATER
                elif any(b.contains(pt) for b in bank):
                    self.plan[i, j] = BANK
                elif any(p.contains(pt) for p, kind in past):
                    self.plan[i, j] = PASTURE if any(p.contains(pt) and kind != "wild" for p, kind in past) else GREEN
                else:
                    self.plan[i, j] = FREE
        # reserved ground: pads (12 m discs), hoists, launchers -- open and walkable, never built
        for p in isl.get("pads", []):
            self._disc(float(p["x"]), float(p["z"]), 7.5, RESERVED)
        for h in isl.get("hoists", []) + isl.get("launchers", []):
            self._disc(float(h["x"]), float(h["z"]), 4.5, RESERVED)
        # the bridges' landings and working room: a gate strip in from the face
        f = isl["faces"]
        self.gates = []
        for bi, b in enumerate(isl.get("bridges", [])):
            side, al, w = b["side"], float(b["along"]), float(b.get("width", 3.6))
            depth = float(b.get("clear", 6.0)) + 7.0
            half = w / 2 + 2.5
            if side == "N":
                x0, x1, z0, z1 = float(f["N"]), float(f["N"]) + depth, al - half, al + half
            elif side == "S":
                x0, x1, z0, z1 = float(f["S"]) - depth, float(f["S"]), al - half, al + half
            elif side == "E":
                x0, x1, z0, z1 = al - half, al + half, float(f["E"]), float(f["E"]) + depth
            else:
                x0, x1, z0, z1 = al - half, al + half, float(f["W"]) - depth, float(f["W"])
            cells = self._rect(x0, x1, z0, z1, GATE)
            inner_end = {"N": (float(f["N"]) + depth, al), "S": (float(f["S"]) - depth, al),
                         "E": (al, float(f["E"]) + depth), "W": (al, float(f["W"]) - depth)}[side]
            self.gates.append({"bridge": bi, "side": side, "along": al, "width": w, "cells": cells,
                               "end": self.cell_of(*inner_end)})
        # tether corridors: the lines from each balloon's hub (60 m up) to its anchor, kept clear at every level
        for bl in isl.get("balloons", []):
            a = bl["anchor"]
            seg = LineString([(float(a[0]), float(a[1]), float(a[2])), (float(bl["x"]), 60.0, float(bl["z"]))])
            for k in range(self.L):
                y = STOREY * k + 1.6
                t = (y - float(a[1])) / max(60.0 - float(a[1]), 1e-3)
                if t < -0.05 or t > 1.0:
                    continue
                t = max(t, 0.0)
                cx = float(a[0]) + (float(bl["x"]) - float(a[0])) * t
                cz = float(a[2]) + (float(bl["z"]) - float(a[2])) * t
                for i, j in self._disc_cells(cx, cz, 5.0):
                    self.block[i, j, k] = True
            # the anchor's foot is open ground
            self._disc(float(a[0]), float(a[2]), 4.0, RESERVED)

    def _disc_cells(self, x, z, r):
        out = []
        i0, j0 = self.cell_of(x - r - CELL, z - r - CELL)
        i1, j1 = self.cell_of(x + r + CELL, z + r + CELL)
        for i in range(max(i0, 0), min(i1 + 1, self.nx)):
            for j in range(max(j0, 0), min(j1 + 1, self.nz)):
                cx, _, cz = self.centre(i, j)
                if math.hypot(cx - x, cz - z) <= r + CELL * 0.71:
                    out.append((i, j))
        return out

    def _disc(self, x, z, r, cls):
        for i, j in self._disc_cells(x, z, r):
            if self.plan[i, j] not in (OUT, WATER):
                self.plan[i, j] = cls

    def _rect(self, x0, x1, z0, z1, cls):
        cells = []
        i0, j0 = self.cell_of(min(x0, x1), min(z0, z1))
        i1, j1 = self.cell_of(max(x0, x1) - 0.01, max(z0, z1) - 0.01)
        for i in range(max(i0, 0), min(i1 + 1, self.nx)):
            for j in range(max(j0, 0), min(j1 + 1, self.nz)):
                if self.plan[i, j] != OUT:
                    if self.plan[i, j] != WATER:
                        self.plan[i, j] = cls
                    cells.append((i, j))
        return cells

    # ------------------------------------------------------------------ volume helpers
    def is_room(self, i, j, k):
        return self.inb(i, j) and 0 <= k < self.L and self.occ[i, j, k] == 1

    def set_room(self, i, j, k, unit, epoch):
        self.occ[i, j, k] = 1
        self.unit[i, j, k] = unit
        self.epoch[i, j, k] = epoch

    def clear(self, i, j, k):
        self.occ[i, j, k] = 0
        self.unit[i, j, k] = -1

    def top(self, i, j):
        """the highest room level in a column, or -1"""
        ks = np.nonzero(self.occ[i, j])[0]
        return int(ks[-1]) if len(ks) else -1

    def free_at(self, i, j, k):
        return self.inb(i, j) and 0 <= k < self.L and self.occ[i, j, k] == 0 and not self.block[i, j, k]

    def supported(self, i, j, k):
        """a room needs a room (or its ground) under it, or to cantilever <= 1 cell off a supported room, or to span
        <= 3 cells between supported rooms (r4 §2 structure)"""
        if k <= self.gk[i, j] + self.lift[i, j]:
            return True                                     # (its ground, or its stilts)
        if self.occ[i, j, k - 1]:
            return True
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if self.is_room(a, b, k) and (k <= self.gk[a, b] or self.occ[a, b, k - 1]):
                return True
        for di, dj in ((1, 0), (0, 1)):
            # spans along the axis: both ends within 3 cells, with every cell between them a room at k
            for back in range(0, 3):
                for fwd in range(0, 3 - back):
                    a0 = (i - di * (back + 1), j - dj * (back + 1))
                    a1 = (i + di * (fwd + 1), j + dj * (fwd + 1))
                    if not (self.is_room(*a0, k) and self.is_room(*a1, k)):
                        continue
                    ok = all(self.is_room(i - di * b, j - dj * b, k) for b in range(1, back + 1)) and \
                        all(self.is_room(i + di * f, j + dj * f, k) for f in range(1, fwd + 1))
                    s0 = k <= self.gk[a0] or self.occ[a0[0], a0[1], k - 1]
                    s1 = k <= self.gk[a1] or self.occ[a1[0], a1[1], k - 1]
                    if ok and s0 and s1:
                        return True
        return False

    def settle(self):
        """drop unsupported rooms until everything stands (bottom up, repeated)"""
        removed = 0
        for _ in range(4):
            changed = False
            for k in range(1, self.L):
                ii, jj = np.nonzero(self.occ[:, :, k])
                for i, j in zip(ii, jj):
                    if not self.supported(int(i), int(j), k):
                        self.clear(i, j, k)
                        removed += 1
                        changed = True
            if not changed:
                break
        return removed

    def new_unit(self, use, lot=-1):
        self.units.append({"use": use, "lot": lot, "cells": 0, "homes": 0, "floors": 0})
        return len(self.units) - 1
