"""preview.py -- debug pictures (PIL): the plan with heights, and the level slices."""
import numpy as np
from PIL import Image, ImageDraw

from lattice import (ARTERY, BANK, COURT, FREE, GATE, GREEN, LANE, LOT, MAIN, OUT, PASTURE, PLAZA, RESERVED, RIM,
                     WATER)

PLAN_COL = {OUT: (34, 36, 44), RIM: (150, 146, 136), FREE: (200, 190, 160), WATER: (60, 110, 150), BANK: (120, 160, 90),
            GREEN: (96, 150, 76), PASTURE: (150, 170, 90), MAIN: (226, 206, 150), PLAZA: (240, 222, 170),
            GATE: (240, 200, 120), LANE: (186, 170, 136), COURT: (130, 170, 100), RESERVED: (210, 200, 180),
            LOT: (120, 100, 80), ARTERY: (220, 190, 130)}


def plan_image(L, scale=6, foliage=None, title=""):
    w, h = L.nz * scale, L.nx * scale
    img = Image.new("RGB", (w, h + 22), (20, 20, 26))
    d = ImageDraw.Draw(img)
    top = np.full((L.nx, L.nz), -1)
    for k in range(L.L):
        top[L.occ[:, :, k] > 0] = k
    kmax = max(1, int(top.max()))
    for i in range(L.nx):
        for j in range(L.nz):
            c = PLAN_COL.get(int(L.plan[i, j]), (255, 0, 255))
            if top[i, j] >= 0:
                t = top[i, j] / kmax
                c = (int(90 + 150 * t), int(70 + 120 * t), int(60 + 90 * t))
                if L.plan[i, j] in (LANE, ARTERY):            # (a room over a lane: a sabat / tunnel)
                    c = (int(170 + 60 * t), int(90 + 60 * t), 60)
            d.rectangle([j * scale, i * scale + 22, (j + 1) * scale - 1, (i + 1) * scale + 21], fill=c)
    if foliage:
        for f in foliage:
            x, z = f[1], f[3]
            j = (z - L.z0) / 3.0 * scale
            i = (x - L.x0) / 3.0 * scale + 22
            d.ellipse([j - 2, i - 2, j + 2, i + 2], fill=(40, 120, 40))
    t = L.travel
    j = (t[2] - L.z0) / 3.0 * scale
    i = (t[0] - L.x0) / 3.0 * scale + 22
    d.ellipse([j - 5, i - 5, j + 5, i + 5], outline=(255, 60, 60), width=2)
    d.text((4, 4), title, fill=(230, 230, 230))
    return img


def slices_image(L, scale=4, title=""):
    levels = [k for k in range(L.L) if L.occ[:, :, k].any()]
    cols = 4
    rows = (len(levels) + cols - 1) // cols
    W, H = L.nz * scale + 8, L.nx * scale + 20
    img = Image.new("RGB", (cols * W, rows * H + 22), (20, 20, 26))
    d = ImageDraw.Draw(img)
    d.text((4, 4), title, fill=(230, 230, 230))
    for n, k in enumerate(levels):
        ox, oy = (n % cols) * W, (n // cols) * H + 22
        d.text((ox + 2, oy + 2), "level %d" % k, fill=(200, 200, 200))
        for i in range(L.nx):
            for j in range(L.nz):
                if L.occ[i, j, k]:
                    e = int(L.epoch[i, j, k])
                    c = [(140, 100, 70), (170, 120, 80), (190, 150, 100), (200, 175, 130), (210, 200, 160),
                         (90, 160, 200)][min(e, 5)]
                elif L.plan[i, j] in (OUT,):
                    continue
                else:
                    c = (60, 60, 66) if k > L.gk[i, j] else PLAN_COL.get(int(L.plan[i, j]), (80, 80, 80))
                d.rectangle([ox + j * scale, oy + 14 + i * scale, ox + (j + 1) * scale - 1, oy + 14 + (i + 1) * scale - 1],
                            fill=c)
    return img
