"""
Remaining farm structures beyond the existing barn/pole_building:
chicken coop, corn crib, farm equipment shed (simple shells, same
gable-roof convention as build_farm_buildings.py), and a grain silo
(landmark/non-walkable cylinder, same construction technique as
build_industrial_buildings.py's water tower). Researched in
research/building_catalog/commercial_civic_farm/. Geometry helpers live
in building_helpers.py.

Real-world feet-derived meters (1ft = 0.3048m), matching this project's
established scale convention.

Run headless:
    blender --background --python build_farm_structures_2.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	FT, REPO, clear_scene, load_material, cube_uv, join_objects,
	build_shell, cut_front_door, register_front_door,
	build_gable_roof, export_glb, DOOR_HEIGHT,
)

OUT_DIR = os.path.join(REPO, "assets", "farm_assets")


def build_building(building_id, width, depth, wall_h, roof_pitch_deg, roof_overhang, wall_tex, roof_tex):
	openings = []
	shell = build_shell(width, depth, wall_h)
	cut_front_door(shell, 0.0, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, 0.0, depth)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	roof = build_gable_roof(width, depth, wall_h, pitch_deg=roof_pitch_deg, overhang=roof_overhang, material=roof_mat)

	combined = join_objects([shell, roof])
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id, "archetype": building_id,
		"stories": 1, "wall_h": wall_h,
		"width": width, "depth": depth, "openings": openings,
	}


def build_grain_silo(building_id, radius, height, wall_tex):
	"""Landmark/non-walkable per research/scenery_asset_checklist.txt --
	same construction technique as build_industrial_buildings.py's water
	tower (a single bpy cylinder primitive), just without the tank-on-
	column composition since a farm silo is one continuous cylinder."""
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
		location=(0.0, 0.0, height / 2.0), vertices=20)
	silo = bpy.context.active_object
	silo.name = building_id + "-col"
	mat = load_material(building_id + "_wall", wall_tex)
	silo.data.materials.append(mat)
	cube_uv(silo)

	export_glb(silo, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id, "archetype": building_id,
		"stories": 0, "wall_h": height,
		"width": radius * 2.0, "depth": radius * 2.0,
		"openings": [], "landmark_no_interior": True,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {"farm_buildings": []}

	# Researched 3-6m x 4-8m range.
	clear_scene()
	manifest["farm_buildings"].append(build_building(
		"chicken_coop", width=4.0, depth=5.5, wall_h=2.0,
		roof_pitch_deg=20.0, roof_overhang=0.3,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_2.png"))

	# Researched 8-9m x 8-12m (double-crib) range.
	clear_scene()
	manifest["farm_buildings"].append(build_building(
		"corn_crib", width=8.5, depth=10.0, wall_h=3.0,
		roof_pitch_deg=22.0, roof_overhang=0.4,
		wall_tex="wall_tinted_4.png", roof_tex="roof_tinted_1.png"))

	# Researched 6-9m x 9-15m range (often open-sided -- approximated
	# here as a fully-walled shed; an open-sided visual variant is a
	# later refinement, not required for the placement/interior spec).
	clear_scene()
	manifest["farm_buildings"].append(build_building(
		"farm_equipment_shed", width=7.5, depth=12.0, wall_h=3.5,
		roof_pitch_deg=15.0, roof_overhang=0.4,
		wall_tex="wall_tinted_6.png", roof_tex="roof_tinted_3.png"))

	# Grain silo: researched 4-9m diameter, 8-20m height, landmark/
	# non-walkable.
	clear_scene()
	manifest["farm_buildings"].append(build_grain_silo(
		"grain_silo", radius=3.0, height=16.0, wall_tex="wall_tinted_2.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_farm_structures_2: manifest now has %d total farm buildings" % len(manifest["farm_buildings"]))


if __name__ == "__main__":
	main()
