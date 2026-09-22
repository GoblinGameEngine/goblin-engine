#!/usr/bin/env python3
"""Generates corn_sprite.png / soy_sprite.png -- alpha-cutout billboard
art for CropFieldGenerator.gd's corn/soy fields, same asset category as
assets/textures/door_sprite.png (a flat RGBA cutout meant for a single
QuadMesh, not a tileable _detail/_tinted texture -- see
building_helpers.py's comment on that separate convention). Pure PIL/
numpy, no Blender needed (there's no 3D geometry here, just 2D art).

Run: python3 blender_scripts/gen_crop_sprites.py
Writes: assets/textures/corn_sprite.png, assets/textures/soy_sprite.png
"""

import math
import random

from PIL import Image, ImageDraw

random.seed(1234)

OUT_DIR = "assets/textures"


def _leaf_polygon(base, tip, width):
    """A tapered blade shape from `base` to `tip`, `width` px at the base."""
    bx, by = base
    tx, ty = tip
    dx, dy = tx - bx, ty - by
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length  # perpendicular unit vector
    hw = width * 0.5
    # A simple 4-point diamond-ish blade: wide near the base, tapering to a
    # point at the tip, with one control point bulging outward at ~40% up
    # the blade for a slightly curved leaf silhouette instead of a straight
    # wedge.
    mid = (bx + dx * 0.42 + nx * hw * 1.15, by + dy * 0.42 + ny * hw * 1.15)
    return [
        (bx - nx * hw * 0.3, by - ny * hw * 0.3),
        (bx + nx * hw * 0.3, by + ny * hw * 0.3),
        mid,
        (tx, ty),
    ]


def _draw_leaf(draw, base, tip, width, color):
    draw.polygon(_leaf_polygon(base, tip, width), fill=color)


def gen_corn(w=768, h=1536):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    ground_y = h - 8
    top_y = int(h * 0.10)
    stem_x = w * 0.5

    stem_base = (140, 90, 26, 255)
    leaf_colors = [
        (77, 140, 31, 255),
        (92, 158, 41, 255),
        (66, 122, 26, 255),
    ]

    # Main stalk -- a slightly tapered vertical blade, not a straight line,
    # so it reads as a real stem rather than a ruler.
    stalk_w_base = w * 0.045
    stalk_w_top = w * 0.02
    draw.polygon(
        [
            (stem_x - stalk_w_base * 0.5, ground_y),
            (stem_x + stalk_w_base * 0.5, ground_y),
            (stem_x + stalk_w_top * 0.5, top_y),
            (stem_x - stalk_w_top * 0.5, top_y),
        ],
        fill=stem_base,
    )

    # Alternating drooping leaves up the stalk.
    n_leaves = 7
    for i in range(n_leaves):
        t = i / (n_leaves - 1)
        y = ground_y - (ground_y - top_y) * (0.12 + 0.80 * t)
        side = 1 if i % 2 == 0 else -1
        leaf_len = w * (0.55 - 0.18 * t) * random.uniform(0.9, 1.08)
        droop = h * (0.10 + 0.05 * t)
        base = (stem_x, y)
        tip = (stem_x + side * leaf_len, y - h * 0.03 + droop * 0.4)
        width = w * (0.09 - 0.02 * t)
        color = leaf_colors[i % len(leaf_colors)]
        _draw_leaf(draw, base, tip, width, color)

    # Tassel at the very top -- a small cluster of thin diverging lines.
    tassel_color = (158, 140, 56, 255)
    for i in range(9):
        ang = math.radians(-70 + i * 17)
        length = h * 0.05 * random.uniform(0.7, 1.0)
        ex = stem_x + math.sin(ang) * length
        ey = top_y - math.cos(ang) * length
        draw.line([(stem_x, top_y), (ex, ey)], fill=tassel_color, width=max(2, int(w * 0.006)))

    # One or two ears partway up, wrapped in husk (a rounded elongated
    # shape) with a few strands of golden silk poking out the top.
    husk_color = (140, 148, 56, 255)
    silk_color = (191, 140, 46, 255)
    for ear_i, ear_t in enumerate([0.42, 0.58]):
        y = ground_y - (ground_y - top_y) * ear_t
        side = 1 if ear_i == 0 else -1
        ex = stem_x + side * w * 0.05
        ear_w = w * 0.07
        ear_h = h * 0.14
        draw.ellipse([ex - ear_w * 0.5, y - ear_h * 0.5, ex + ear_w * 0.5, y + ear_h * 0.5], fill=husk_color)
        for s in range(4):
            sx = ex + random.uniform(-ear_w * 0.3, ear_w * 0.3)
            draw.line([(sx, y - ear_h * 0.5), (sx + random.uniform(-8, 8), y - ear_h * 0.7)], fill=silk_color, width=2)

    img.save(f"{OUT_DIR}/corn_sprite.png")
    print(f"wrote {OUT_DIR}/corn_sprite.png {img.size}")


def gen_soy(w=768, h=1024):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    ground_y = h - 8
    top_y = int(h * 0.22)
    stem_x = w * 0.5

    stem_color = (82, 115, 36, 255)
    leaf_colors = [
        (71, 133, 36, 255),
        (87, 148, 46, 255),
        (61, 112, 31, 255),
    ]

    # Several branching stems fanning slightly outward from a common base
    # -- soybeans grow as a bushy clump, not one tall stalk.
    n_stems = 5
    stem_tops = []
    for i in range(n_stems):
        t = i / (n_stems - 1)
        spread = (t - 0.5) * w * 0.5
        sx = stem_x + spread
        sy_top = top_y + abs(t - 0.5) * h * 0.25
        draw.line([(stem_x, ground_y), (sx, sy_top)], fill=stem_color, width=max(3, int(w * 0.018)))
        stem_tops.append((sx, sy_top))

    # Trifoliate leaf clusters (3 rounded leaflets) scattered along each
    # stem, denser near the top -- the actual bushy canopy silhouette.
    leaflet_r = w * 0.055
    for sx, sy_top in stem_tops:
        n_clusters = random.randint(3, 5)
        for c in range(n_clusters):
            ct = c / max(1, n_clusters - 1)
            cx = stem_x + (sx - stem_x) * (0.3 + 0.7 * ct) + random.uniform(-10, 10)
            cy = ground_y + (sy_top - ground_y) * (0.25 + 0.75 * ct) + random.uniform(-10, 10)
            color = random.choice(leaf_colors)
            for leaflet_i in range(3):
                ang = math.radians(-90 + leaflet_i * 120 + random.uniform(-15, 15))
                lx = cx + math.cos(ang) * leaflet_r * 0.8
                ly = cy + math.sin(ang) * leaflet_r * 0.8
                draw.ellipse(
                    [lx - leaflet_r * 0.5, ly - leaflet_r * 0.7, lx + leaflet_r * 0.5, ly + leaflet_r * 0.7],
                    fill=color,
                )

    # A few pale pod clusters low on the plant.
    pod_color = (158, 148, 82, 255)
    for _ in range(6):
        px = stem_x + random.uniform(-w * 0.28, w * 0.28)
        py = ground_y - random.uniform(h * 0.15, h * 0.45)
        draw.ellipse([px - 6, py - 10, px + 6, py + 10], fill=pod_color)

    img.save(f"{OUT_DIR}/soy_sprite.png")
    print(f"wrote {OUT_DIR}/soy_sprite.png {img.size}")


if __name__ == "__main__":
    import os

    os.makedirs(OUT_DIR, exist_ok=True)
    gen_corn()
    gen_soy()
