#!/usr/bin/env python3
"""Upscales the two reference wallpapers you provided (reference/fluffy
clouds wallpaper.jpeg, reference/cosmic sky wallpaper.jpeg) and saves them
as this project's sky_day.png/sky_night.png -- replacing the earlier
GIMP-drawn versions entirely, per your direct request ("just upscale
these and use them") rather than generating new art.

Center-cropped to square before upscaling: the ceiling/wall shaders tile
the same texture equally in both directions (StationRingBuilder.
TILE_CEILING), so a square source tiles far more predictably than the
photos' native ~3:2 aspect ratio would.

Run: python3 blender_scripts/upscale_sky_wallpapers.py
Writes: assets/textures/sky_day.png, assets/textures/sky_night.png
"""

import os

from PIL import Image

REF_DIR = "/home/nelahi/goblin-engine/reference"
OUT_DIR = "assets/textures"
TARGET_SIZE = 2048


def upscale_square(src_path: str, dst_path: str) -> None:
	img = Image.open(src_path).convert("RGB")
	w, h = img.size
	side = min(w, h)
	left = (w - side) // 2
	top = (h - side) // 2
	img = img.crop((left, top, left + side, top + side))
	img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
	img.save(dst_path)
	print(f"wrote {dst_path} ({TARGET_SIZE}x{TARGET_SIZE}, upscaled from {side}x{side} crop of {w}x{h})")


if __name__ == "__main__":
	os.makedirs(OUT_DIR, exist_ok=True)
	upscale_square(f"{REF_DIR}/fluffy clouds wallpaper.jpeg", f"{OUT_DIR}/sky_day.png")
	upscale_square(f"{REF_DIR}/cosmic sky wallpaper.jpeg", f"{OUT_DIR}/sky_night.png")
