"""
Second batch of downtown-zone commercial buildings: small grocery,
pharmacy/drugstore, clothing store, barber shop/salon, bar/tavern, movie
theater, small hotel/inn, restaurant -- 8 of the 12 downtown retail
archetypes researched in research/building_catalog/commercial_civic_farm/
(the other 4 -- general store, bank, hardware, diner -- already exist as
storefront_general/bank/hardware/diner.glb, built by the original
build_downtown_buildings.py). Same flat-roofed-box-with-parapet
convention as that script (real Midwestern main-street look, not a
pitched roof), same hollow wall shell + one front door pattern. Kept in
a separate file rather than extending the original script, so the
already-shipped 5 buildings never need to be regenerated/re-verified as
a side effect of adding these.

Real-world feet-derived meters (1ft = 0.3048m), matching
DowntownGenerator.gd's own scale convention.

Run headless:
    blender --background --python build_downtown_buildings_2.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	FT, REPO, clear_scene, load_material, cube_uv, join_objects,
	build_shell, cut_front_door, register_front_door,
	build_parapet, export_glb, DOOR_HEIGHT,
)

OUT_DIR = os.path.join(REPO, "assets", "downtown_assets")

PARAPET_HEIGHT = 0.6
PARAPET_THICKNESS = 0.15
STORY_H = 3.66  # matches build_downtown_buildings.py's own storefront-ceiling convention


def build_building(building_id, width, depth, wall_h, wall_tex, roof_tex, door_x_frac=0.5):
	openings = []
	shell = build_shell(width, depth, wall_h)
	door_x = (door_x_frac - 0.5) * width
	cut_front_door(shell, door_x, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, door_x, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	parapet = build_parapet(width, depth, wall_h, PARAPET_HEIGHT, PARAPET_THICKNESS, roof_mat)

	combined = join_objects([shell, parapet])
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id,
		"archetype": building_id,
		"stories": max(1, round(wall_h / 3.5)),
		"wall_h": wall_h,
		"width": width,
		"depth": depth,
		"openings": openings,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	# Merge into the existing downtown_assets/manifest.json (from the
	# original build_downtown_buildings.py) rather than overwriting it --
	# both scripts share one output directory and one manifest.
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {"downtown_buildings": []}

	# Researched 12-20m x 20-35m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"small_grocery", width=15.0, depth=25.0, wall_h=STORY_H,
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_1.png"))

	# Researched 8-13m x 15-22m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"pharmacy_drugstore", width=10.0, depth=18.0, wall_h=STORY_H,
		wall_tex="wall_tinted_5.png", roof_tex="roof_tinted_2.png"))

	# Researched 7-12m x 15-25m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"clothing_store", width=9.0, depth=18.0, wall_h=STORY_H,
		wall_tex="wall_tinted_6.png", roof_tex="roof_tinted_3.png"))

	# Researched 4-7m x 8-14m range -- narrowest storefront in the batch.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"barber_salon", width=5.5, depth=10.0, wall_h=STORY_H,
		wall_tex="wall_tinted_7.png", roof_tex="roof_tinted_0.png"))

	# Researched 6-10m x 12-20m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"bar_tavern", width=8.0, depth=15.0, wall_h=STORY_H,
		wall_tex="wall_tinted_8.png", roof_tex="roof_tinted_1.png"))

	# Researched 10-22m x 25-50m range, taller front facade (cinemas read
	# taller than an ordinary 1-story storefront).
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"movie_theater", width=16.0, depth=35.0, wall_h=STORY_H * 1.5,
		wall_tex="wall_tinted_3.png", roof_tex="roof_tinted_2.png"))

	# Researched 12-20m x 20-30m range, 2.5 stories (hotels read taller
	# than ordinary retail).
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"hotel_inn_small", width=15.0, depth=24.0, wall_h=STORY_H * 2.5,
		wall_tex="wall_tinted_9.png", roof_tex="roof_tinted_3.png"))

	# Researched 8-14m x 15-25m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"restaurant", width=11.0, depth=20.0, wall_h=STORY_H,
		wall_tex="wall_tinted_10.png", roof_tex="roof_tinted_0.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_downtown_buildings_2: manifest now has %d total downtown buildings" % len(manifest["downtown_buildings"]))


if __name__ == "__main__":
	main()
