"""
Additional small-town business archetypes (Part B1, 11 buildings) from
research/scenery_asset_checklist_expansion.md -- dollar store, feed
store, veterinary clinic, newspaper office, local radio station,
funeral home, law office, insurance agency, real estate office,
laundromat, medical/dental clinic. Same flat-roofed parapet convention
as the other downtown buildings.

Real-world feet-derived meters. Run headless:
    blender --background --python build_downtown_buildings_3.py
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
STORY_H = 3.66


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
		"id": building_id, "archetype": building_id,
		"stories": max(1, round(wall_h / 3.5)), "wall_h": wall_h,
		"width": width, "depth": depth, "openings": openings,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"dollar_store", width=14.0, depth=22.0, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_1.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"feed_store", width=16.0, depth=28.0, wall_h=STORY_H * 1.2,
		wall_tex="wall_tinted_4.png", roof_tex="roof_tinted_3.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"veterinary_clinic", width=12.0, depth=18.0, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_2.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"newspaper_office", width=9.0, depth=16.0, wall_h=STORY_H,
		wall_tex="wall_tinted_6.png", roof_tex="roof_tinted_0.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"local_radio_station", width=10.0, depth=14.0, wall_h=STORY_H,
		wall_tex="wall_tinted_5.png", roof_tex="roof_tinted_1.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"funeral_home", width=15.0, depth=20.0, wall_h=STORY_H * 1.3,
		wall_tex="wall_tinted_9.png", roof_tex="roof_tinted_2.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"law_office", width=8.0, depth=14.0, wall_h=STORY_H,
		wall_tex="wall_tinted_9.png", roof_tex="roof_tinted_1.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"insurance_agency", width=7.0, depth=12.0, wall_h=STORY_H,
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_0.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"real_estate_office", width=7.0, depth=12.0, wall_h=STORY_H,
		wall_tex="wall_tinted_3.png", roof_tex="roof_tinted_0.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"laundromat", width=9.0, depth=16.0, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_1.png"))

	clear_scene()
	manifest["downtown_buildings"].append(build_building(
		"medical_dental_clinic", width=11.0, depth=17.0, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_2.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_downtown_buildings_3: manifest now has %d total downtown buildings" % len(manifest["downtown_buildings"]))


if __name__ == "__main__":
	main()
