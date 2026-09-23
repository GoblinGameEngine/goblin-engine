"""
Industrial/utility-adjacent buildings: warehouse, small factory/mill,
auto repair shop, gas station (flat-roofed parapet boxes, same
convention as downtown storefronts), two grain elevators (small/large --
simplified as tall narrow concrete-tower boxes, a reasonably accurate
read for this structure type even without silo-cluster detail), and a
water tower (a genuinely new shape: cylindrical tank on a single support
column -- the "standpipe" water tower style, chosen over the spider-leg
style for build simplicity; landmark/non-walkable per
research/scenery_asset_checklist.txt, so no door/interior). Researched
in research/building_catalog/commercial_civic_farm/. Geometry helpers
live in building_helpers.py.

Real-world feet-derived meters (1ft = 0.3048m), matching this project's
established scale convention.

Run headless:
    blender --background --python build_industrial_buildings.py
"""

import sys
import os
import json
import math
import bpy

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


def build_flat_industrial(building_id, width, depth, wall_h, wall_tex, roof_tex, door_x_frac=0.5):
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


def build_grain_elevator(building_id, footprint, tower_h, wall_tex, roof_tex):
	"""Simplified as a single tall narrow concrete-tower box -- real
	grain elevators are visually dominated by exactly this silhouette
	(very tall, narrow footprint, flat/minimal roofline) even before
	adding a silo cluster or headhouse detail, so this is a reasonably
	accurate first pass, not a rough stand-in."""
	openings = []
	shell = build_shell(footprint, footprint, tower_h)
	cut_front_door(shell, 0.0, footprint, DOOR_HEIGHT / 2.0)
	register_front_door(openings, 0.0, footprint)

	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)

	roof_mat = load_material(building_id + "_roof", roof_tex)
	parapet = build_parapet(footprint, footprint, tower_h, PARAPET_HEIGHT, PARAPET_THICKNESS, roof_mat)

	combined = join_objects([shell, parapet])
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id, "archetype": building_id,
		"stories": max(1, round(tower_h / 3.5)), "wall_h": tower_h,
		"width": footprint, "depth": footprint, "openings": openings,
	}


def build_water_tower(building_id, tank_radius, tank_height, column_radius, column_height, wall_tex):
	"""Standpipe-style water tower: a squat cylindrical tank on a single
	thick cylindrical support column. Landmark/non-walkable structure
	per research/scenery_asset_checklist.txt section 2 -- no door, no
	interior, no manifest opening entries."""
	bpy.ops.mesh.primitive_cylinder_add(radius=column_radius, depth=column_height,
		location=(0.0, 0.0, column_height / 2.0), vertices=16)
	column = bpy.context.active_object
	column.name = building_id + "_column"

	bpy.ops.mesh.primitive_cylinder_add(radius=tank_radius, depth=tank_height,
		location=(0.0, 0.0, column_height + tank_height / 2.0), vertices=24)
	tank = bpy.context.active_object
	tank.name = building_id + "_tank"

	mat = load_material(building_id + "_wall", wall_tex)
	for obj in (column, tank):
		obj.data.materials.append(mat)
		cube_uv(obj)

	combined = join_objects([column, tank])
	combined.name = building_id + "-col"

	export_glb(combined, OUT_DIR, building_id + ".glb")
	return {
		"id": building_id, "archetype": building_id,
		"stories": 0, "wall_h": column_height + tank_height,
		"width": tank_radius * 2.0, "depth": tank_radius * 2.0,
		"openings": [], "landmark_no_interior": True,
	}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {"downtown_buildings": []}

	# Researched 15-25m x 30-60m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_industrial(
		"warehouse", width=18.0, depth=40.0, wall_h=STORY_H * 1.4,
		wall_tex="wall_tinted_3.png", roof_tex="roof_tinted_2.png"))

	# Researched 15-45m x 25-80m range, toward the smaller end.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_industrial(
		"small_factory_mill", width=22.0, depth=45.0, wall_h=STORY_H * 1.6,
		wall_tex="wall_tinted_5.png", roof_tex="roof_tinted_3.png"))

	# Researched 12-20m x 15-25m range.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_industrial(
		"auto_repair_shop", width=15.0, depth=20.0, wall_h=STORY_H * 1.2,
		wall_tex="wall_tinted_7.png", roof_tex="roof_tinted_0.png"))

	# Researched 8-14m x 10-16m (+forecourt) range -- forecourt/canopy/
	# pump islands not modeled at this pass, just the small service
	# building itself.
	clear_scene()
	manifest["downtown_buildings"].append(build_flat_industrial(
		"gas_station", width=9.0, depth=12.0, wall_h=STORY_H,
		wall_tex="wall_tinted_8.png", roof_tex="roof_tinted_1.png"))

	# Small grain elevator: researched ~26x26 ft class, 32-40 ft tall at
	# the smallest per the village-tier research.
	clear_scene()
	manifest["downtown_buildings"].append(build_grain_elevator(
		"grain_elevator_small", footprint=26.0 * FT, tower_h=36.0 * FT,
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_0.png"))

	# Large grain elevator: researched 70-125 ft tall, town/city scale.
	clear_scene()
	manifest["downtown_buildings"].append(build_grain_elevator(
		"grain_elevator_large", footprint=9.0, tower_h=95.0 * FT,
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_0.png"))

	# Water tower: researched 8-15m tank diameter, 25-45m total height.
	# Landmark structure, no interior.
	clear_scene()
	manifest["downtown_buildings"].append(build_water_tower(
		"water_tower", tank_radius=5.0, tank_height=7.0,
		column_radius=1.2, column_height=25.0,
		wall_tex="wall_tinted_9.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_industrial_buildings: manifest now has %d total downtown buildings" % len(manifest["downtown_buildings"]))


if __name__ == "__main__":
	main()
