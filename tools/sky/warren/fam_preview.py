#!/usr/bin/env python3
"""fam_preview.py -- one picture per warren family: an overview and a street view (from the travel point toward the
landmark / the island's middle) of one of its islands, assembled from the real kit (assemble.py + Blender
render_warren.py), side by side in research/sky_islands/img/fam_<family>.png.

  ~/.venvs/ssc-assets/bin/python tools/sky/warren/fam_preview.py FAMILY [ISLAND_ID]
"""
import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
WR = os.path.join(ROOT, "godot_project", "remake", "sky", "warrens")
IMG = os.path.join(ROOT, "research", "sky_islands", "img")
TMP = os.environ.get("WARREN_TMP", "/tmp")
PY = sys.executable


def main():
    fam = sys.argv[1]
    asg = json.load(open(os.path.join(WR, "assign.json")))["assign"]
    isls = {i["id"]: i for i in json.load(open(os.path.join(ROOT, "godot_project", "remake", "sky", "islands.json")))["islands"]}
    ids = [k for k, v in sorted(asg.items()) if v == fam]
    iid = sys.argv[2] if len(sys.argv) > 2 else max(ids, key=lambda k: (min(int(isls[k]["blocks"]), 5), k))
    doc = json.load(open(os.path.join(WR, iid + ".json")))
    npz = os.path.join(TMP, "fam_%s.npz" % iid)
    subprocess.run([PY, os.path.join(HERE, "assemble.py"), iid, npz], check=True)
    isl = isls[iid]
    f = isl["faces"]
    size = max(f["S"] - f["N"], f["W"] - f["E"])
    tx, ty, tz, _ = doc["travel"]
    lm = doc.get("landmark") or []
    fr = doc["frame"]
    if lm:
        gx, gz = fr["x0"] + 3 * lm[0] + 1.5, fr["z0"] + 3 * lm[1] + 1.5
    else:
        gx, gz = (f["N"] + f["S"]) / 2, (f["E"] + f["W"]) / 2
    d = math.hypot(gx - tx, gz - tz)
    a0 = math.atan2(gz - tz, gx - tx)
    # a clear line of sight: no room and no tree in the first 16 m (turn from the landmark's bearing until clear)
    import numpy as np
    fol = np.load(npz)["foliage"]
    lv = {x["level"]: x["rows"] for x in doc["levels"]}
    k0 = int(round(ty / 3.2))

    def blocked(x, z):
        i, j = int((x - fr["x0"]) // 3), int((z - fr["z0"]) // 3)
        if not (0 <= i < fr["nx"] and 0 <= j < fr["nz"]):
            return False
        for k in (k0, k0 + 1):
            if k in lv and lv[k][i][j] == "#":
                return True
        return len(fol) and bool((np.hypot(fol[:, 0] - x, fol[:, 2] - z) < 3.2).any())

    # stand in the city: a main-street cell 10-45 m in from the travel point, looking down the longest open run of
    # street (no tree in the first cells)
    plan = doc["plan"]
    walkc = set("MPGAL")
    nodes = np.array([n[:3] for n in doc["walk"]["nodes"]], np.float32)
    best_s = None
    for i in range(fr["nx"]):
        for j in range(fr["nz"]):
            if plan[i][j] not in "MA":
                continue
            x, z = fr["x0"] + 3 * i + 1.5, fr["z0"] + 3 * j + 1.5
            dd = math.hypot(x - tx, z - tz)
            if not 10 <= dd <= 45:
                continue
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                run = 0
                while run < 16:
                    a_, b_ = i + di * (run + 1), j + dj * (run + 1)
                    if not (0 <= a_ < fr["nx"] and 0 <= b_ < fr["nz"]) or plan[a_][b_] not in walkc:
                        break
                    run += 1
                if any(len(fol) and (np.hypot(fol[:, 0] - (x + 3 * di * s_), fol[:, 2] - (z + 3 * dj * s_)) < 3.0).any()
                       for s_ in (0, 1, 2)):
                    continue
                sc = run - abs(math.remainder(math.atan2(dj, di) - a0, math.tau)) * 0.5
                if best_s is None or sc > best_s[0]:
                    best_s = (sc, x, z, math.atan2(dj, di))
    if best_s:
        _, tx, tz, best = best_s
        if len(nodes):
            k_ = int(np.argmin(np.hypot(nodes[:, 0] - tx, nodes[:, 2] - tz)))
            ty = float(nodes[k_, 1])
    else:
        best = a0
    ux, uz = math.cos(best), math.sin(best)
    T = (tx + ux * 30, ty + 4.5, tz + uz * 30)
    C = (tx, ty + 1.8, tz)
    # Blender: (x, -z, y)
    dx, dy, dz = C[0] - T[0], -(C[2] - T[2]), C[1] - T[1]
    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
    street = "%.1f:%.2f:%.1f:%.1f:%.1f:%.1f@20" % (math.degrees(math.atan2(dy, dx)), math.degrees(math.asin(dz / dist)),
                                                  dist, T[0], T[1], T[2])
    over = "210:34:%.0f" % (size * 1.25 + 60)
    pre = os.path.join(TMP, "fam_%s" % fam)
    subprocess.run(["flatpak", "run", "org.blender.Blender", "-b", "--factory-startup", "--python",
                    os.path.join(ROOT, "remake", "blender", "sky", "render_warren.py"), "--", pre, iid, npz, "--",
                    over, street], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    a = Image.open(pre + "_0.png").convert("RGB").resize((1200, 750))
    b = Image.open(pre + "_1.png").convert("RGB").resize((1200, 750))
    out = Image.new("RGB", (2400, 790), (20, 20, 24))
    out.paste(a, (0, 40))
    out.paste(b, (1200, 40))
    dr = ImageDraw.Draw(out)
    dr.text((12, 12), "%s -- %s %s (%d blocks): overview | street view from the travel point" %
            (fam, iid, isl.get("name"), int(isl["blocks"])), fill=(235, 235, 235))
    os.makedirs(IMG, exist_ok=True)
    out.save(os.path.join(IMG, "fam_%s.png" % fam))
    print("fam_%s.png" % fam, iid)


if __name__ == "__main__":
    main()
