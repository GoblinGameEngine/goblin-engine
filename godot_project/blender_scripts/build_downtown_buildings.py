"""
Downtown zone buildings: 4 storefront types (general store, bank, hardware,
diner) and a post office -- flat-roofed rectangular boxes with a low
parapet lip (not a pitched roof, per the researched Midwestern main-street
look), each a real hollow wall shell with one front door. Geometry
helpers live in building_helpers.py, shared with build_farm_buildings.py.

The bank is built taller (3 stories) to serve as the "occasional 3-story
anchor near the main crossroads" the research called for; everything
else is 1-2 stories, matching the researched dominant pattern. The post
office is a double-wide lot with a centered (symmetrical) door -- civic
buildings get a grander, more formal facade than an ordinary storefront.

Real-world feet-derived meters (1ft = 0.3048m), matching
DowntownGenerator.gd's own scale convention.

Run headless:
    blender --background --python build_downtown_buildings.py
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
	# "-col" is Godot's glTF-import node-name-suffix convention for real
	# collision -- see building_helpers.py's module docstring for why
	# RingCoords.add_trimesh_collision() is what actually provides it at
	# runtime regardless.
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id,
		"stories": max(1, round(wall_h / 3.5)),
		"wall_h": wall_h,
		"width": width,
		"depth": depth,
		"openings": openings,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest = {"downtown_buildings": []}

	# Standard 25ft storefront lot, ~80ft deep -- ground-floor storefront
	# ceiling height read as taller than a house's (~12ft/3.66m per
	# story here vs. a house's 2.75m), matching the researched ~10ft
	# glass-zone-plus-header proportion.
	STOREFRONT_W = 25.0 * FT
	STOREFRONT_D = 80.0 * FT
	STORY_H = 3.66

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"storefront_general", width=STOREFRONT_W, depth=STOREFRONT_D, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_0.png"))

	# The 3-story anchor near the main crossroads (placed by
	# DowntownGenerator.gd, not decided here) -- banks were the
	# researched example of the most ornate, tallest building on a
	# small-town main street.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"storefront_bank", width=STOREFRONT_W, depth=STOREFRONT_D, wall_h=STORY_H * 3.0,
		wall_tex="wall_tinted_9.png", roof_tex="roof_tinted_1.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"storefront_hardware", width=STOREFRONT_W, depth=STOREFRONT_D, wall_h=STORY_H,
		wall_tex="wall_tinted_4.png", roof_tex="roof_tinted_2.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"storefront_diner", width=STOREFRONT_W, depth=STOREFRONT_D, wall_h=STORY_H * 0.9,
		wall_tex="wall_tinted_1.png", roof_tex="roof_tinted_3.png"))

	# Post office: double-wide civic lot, centered (symmetrical) door --
	# build_building()'s default door_x_frac=0.5 already centers it.
	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"post_office", width=STOREFRONT_W * 2.0, depth=90.0 * FT, wall_h=STORY_H * 2.0,
		wall_tex="wall_tinted_10.png", roof_tex="roof_tinted_0.png"))

	with open(os.path.join(OUT_DIR, "manifest.json"), "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_downtown_buildings: wrote %d buildings to %s" % (len(manifest["downtown_buildings"]), OUT_DIR))


if __name__ == "__main__":
	main()
