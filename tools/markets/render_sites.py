#!/usr/bin/env python3
"""
render_sites.py -- a plan view of every sited flea market on the game data (roads, structures, areas, the market's
areas, stalls, lot rows, poles, tents, anchor blocks): research/flea_markets/img/sites.jpg (a contact sheet), and
img/site_<ID>.png per market with --each.

    ~/.venvs/ssc-assets/bin/python tools/markets/render_sites.py [--each] [--only FM-C,FM-SOL]
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GD = os.path.join(ROOT, "godot_project", "remake")
OUT = os.path.join(ROOT, "research", "flea_markets", "img")
PX = 1.5                    # px per m
HALF = 260.0                # m round the site's centre


def main():
    each = "--each" in sys.argv
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
    fm = [m for m in json.load(open(os.path.join(GD, "markets", "flea_markets.json")))["markets"] if m.get("sited")]
    if only:
        fm = [m for m in fm if m["id"] in only]
    ter = json.load(open(os.path.join(GD, "terrain.json")))
    C = 2 * math.pi * ter["R"]
    wrap = lambda d: (d + C / 2) % C - C / 2
    structs = json.load(open(os.path.join(GD, "placement.json")))["structures"]
    tiles = []
    for m in fm:
        cs, cx = m["centre_sx"]
        S = int(2 * HALF * PX)
        im = Image.new("RGB", (S, S), (214, 222, 196))
        d = ImageDraw.Draw(im)
        T = lambda p: ((wrap(p[0] - cs) + HALF) * PX, (p[1] - cx + HALF) * PX)
        col = {"parking": (80, 80, 80), "market_floor": (120, 112, 104), "market_apron": (150, 200, 110), "mooring_field": (110, 175, 95),
               "lawn": (170, 210, 140), "lot": (190, 180, 160), "schoolground": (200, 190, 150)}
        for a in ter["areas"]:
            p0 = a["poly"][0]
            if abs(wrap(p0[0] - cs)) > HALF + 300 or abs(p0[1] - cx) > HALF + 300:
                continue
            d.polygon([T(p) for p in a["poly"]], fill=col.get(a["kind"], (200, 200, 190)))
        for r in ter["roads"]:
            pts = r["pts"]
            if not any(abs(wrap(p[0] - cs)) < HALF + 100 and abs(p[1] - cx) < HALF + 100 for p in pts[::3] + [pts[-1]]):
                continue
            w = 2 * max(r.get("hl", r["w"] / 2), r.get("hr", r["w"] / 2))
            d.line([T(p) for p in pts], fill=(250, 240, 120) if r.get("market") else (60, 60, 66), width=max(1, int(w * PX)))
        for e in structs:
            if abs(wrap(e["s"] - cs)) > HALF + 60 or abs(e["x"] - cx) > HALF + 60:
                continue
            c_, s_ = math.cos(e["yaw"]), math.sin(e["yaw"])
            poly = [(e["s"] + lx * s_ - lz * c_, e["x"] + lx * c_ + lz * s_) for lx, lz in
                    ((e["fmin"][0], e["fmin"][1]), (e["fmax"][0], e["fmin"][1]), (e["fmax"][0], e["fmax"][1]), (e["fmin"][0], e["fmax"][1]))]
            d.polygon([T(p) for p in poly], fill=(170, 90, 70), outline=(90, 40, 30))
        f = m["frame"]
        a_ = f["yaw"]
        W_ = lambda u, v: ((f["s"] + u * math.cos(a_) - v * math.sin(a_)), f["x"] + u * math.sin(a_) + v * math.cos(a_))
        if m.get("pier"):
            for dk in m["pier"]["decks"] + [[-1.3, 0.0, 1.3, 12.0]]:
                q = [W_(dk[0], dk[1]), W_(dk[2], dk[1]), W_(dk[2], dk[3]), W_(dk[0], dk[3])]
                d.polygon([T(p) for p in q], fill=(170, 130, 90), outline=(90, 60, 40))
        for s in m["stalls"]:
            w, h = {0: (3, 3), 1: (3, 3), 2: (6, 3), 3: (4, 8)}[int(s[3])]
            q = [W_(s[0] + du, s[1] + dv) for du, dv in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
            d.polygon([T(p) for p in q], fill={0: (200, 50, 50), 1: (60, 110, 220), 2: (60, 190, 210), 3: (240, 150, 40)}[int(s[3])])
        for t in m["tent_slots"]:
            hh = t[3] / 2
            q = [W_(t[0] + du, t[1] + dv) for du, dv in ((-hh, -hh), (hh, -hh), (hh, hh), (-hh, hh))]
            d.polygon([T(p) for p in q], outline=(220, 0, 200))
        for p in m["poles"]:
            c = T(W_(p[0], p[1]))
            d.ellipse([c[0] - 2, c[1] - 2, c[0] + 2, c[1] + 2], fill=(255, 230, 0))
        for p in m["deadmen"]:
            c = T(W_(p[0], p[1]))
            d.ellipse([c[0] - 2, c[1] - 2, c[0] + 2, c[1] + 2], fill=(20, 20, 20))
        for p in m["masts"]:
            c = T(W_(p[0], p[1]))
            d.ellipse([c[0] - 4, c[1] - 4, c[0] + 4, c[1] + 4], outline=(0, 0, 0), width=2)
        c = T(W_(m["pylon"][0], m["pylon"][1]))
        d.rectangle([c[0] - 4, c[1] - 4, c[0] + 4, c[1] + 4], fill=(255, 0, 0))
        try:
            font = ImageFont.load_default(size=22)
        except TypeError:
            font = ImageFont.load_default()
        d.text((8, 6), "%s  %s (%s)  r %.2f" % (m["id"], m["name"], m["town"], m["limits_r"]), fill=(0, 0, 0), font=font)
        if each:
            im.save(os.path.join(OUT, "site_%s.png" % m["id"]))
        tiles.append(im.resize((390, 390)))
    if not tiles:
        return
    cols = 6
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 390, rows * 390), (255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * 390, (k // cols) * 390))
    sheet.save(os.path.join(OUT, "sites.jpg"), quality=85)
    print("wrote", os.path.join(OUT, "sites.jpg"), len(tiles))


if __name__ == "__main__":
    main()
