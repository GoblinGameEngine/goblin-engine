"""
Part A (already-flagged-but-unresolved gaps, 23 items) from
research/scenery_asset_checklist_expansion.md: hospital, harbor/marina
infrastructure, rail depot + founder's mansion + rail corridor, chain
ferry, cemetery grounds, fairground, and downtown building-condition
props. Mix of full buildings (shell+parapet/gable) and simple
prop-scale geometry.

Buildings go to downtown_assets (civic/commercial scale) or
farm_assets (fairground, rural-adjacent) as appropriate; simple props
go to infrastructure_assets, matching the convention established for
every other non-building prop this session.

Real-world feet-derived meters. Run headless:
    blender --background --python build_part_a_gaps.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import (
	FT, REPO, clear_scene, load_material, cube_uv, join_objects, make_box,
	build_shell, cut_front_door, register_front_door,
	build_parapet, build_gable_roof, export_glb, DOOR_HEIGHT,
)

DOWNTOWN_DIR = os.path.join(REPO, "assets", "downtown_assets")
INFRA_DIR = os.path.join(REPO, "assets", "infrastructure_assets")

PARAPET_HEIGHT = 0.6
PARAPET_THICKNESS = 0.15
STORY_H = 3.66


def build_flat_building(building_id, width, depth, wall_h, wall_tex, roof_tex, out_dir=DOWNTOWN_DIR, door_x_frac=0.5):
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
	export_glb(combined, out_dir, building_id + ".glb")
	return {"id": building_id, "archetype": building_id, "stories": max(1, round(wall_h / 3.5)),
		"wall_h": wall_h, "width": width, "depth": depth, "openings": openings}


def build_gable_building(building_id, width, depth, wall_h, pitch, overhang, wall_tex, roof_tex, out_dir=DOWNTOWN_DIR):
	openings = []
	shell = build_shell(width, depth, wall_h)
	cut_front_door(shell, 0.0, depth, DOOR_HEIGHT / 2.0)
	register_front_door(openings, 0.0, depth)
	wall_mat = load_material(building_id + "_wall", wall_tex)
	shell.data.materials.append(wall_mat)
	cube_uv(shell)
	roof_mat = load_material(building_id + "_roof", roof_tex)
	roof = build_gable_roof(width, depth, wall_h, pitch_deg=pitch, overhang=overhang, material=roof_mat)
	combined = join_objects([shell, roof])
	combined.name = building_id + "-col"
	export_glb(combined, out_dir, building_id + ".glb")
	return {"id": building_id, "archetype": building_id, "stories": 1,
		"wall_h": wall_h, "width": width, "depth": depth, "openings": openings}


def build_box_prop(prop_id, size, z_center, tex):
	obj = make_box(prop_id, size, (0.0, 0.0, z_center))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, INFRA_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_lighthouse(prop_id, tex):
	bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=10.0, location=(0.0, 0.0, 5.0), vertices=14)
	tower = bpy.context.active_object
	bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=1.0, location=(0.0, 0.0, 10.5), vertices=14)
	lantern = bpy.context.active_object
	mat = load_material(prop_id, tex)
	for o in (tower, lantern):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([tower, lantern])
	combined.name = prop_id + "-col"
	export_glb(combined, INFRA_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(DOWNTOWN_DIR, exist_ok=True)
	os.makedirs(INFRA_DIR, exist_ok=True)
	downtown_manifest_path = os.path.join(DOWNTOWN_DIR, "manifest.json")
	with open(downtown_manifest_path) as f:
		downtown_manifest = json.load(f)
	infra_manifest_path = os.path.join(INFRA_DIR, "manifest.json")
	with open(infra_manifest_path) as f:
		infra_manifest = json.load(f)
	infra_manifest.setdefault("part_a_gaps", [])
	infra_items = infra_manifest["part_a_gaps"]

	# --- A1: Hospital ---
	clear_scene()
	downtown_manifest["downtown_buildings"].append(build_flat_building(
		"rural_hospital", width=30.0, depth=40.0, wall_h=STORY_H * 2.0,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_1.png"))

	# --- A2: Harbor/marina infrastructure ---
	clear_scene()
	infra_items.append(build_box_prop("industrial_harbor_freight_dock", (4.0, 20.0, 3.0), 1.5, tex="wall_tinted_9.png"))
	clear_scene()
	downtown_manifest["downtown_buildings"].append(build_flat_building(
		"marina_harbormaster_office", width=6.0, depth=8.0, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_2.png"))
	clear_scene()
	infra_items.append(build_box_prop("fuel_dock", (2.0, 4.0, 1.0), 0.5, tex="wall_tinted_9.png"))
	clear_scene()
	infra_items.append(build_box_prop("boat_slip_dock_pier", (2.0, 15.0, 0.3), 0.15, tex="wall_tinted_6.png"))
	clear_scene()
	downtown_manifest["downtown_buildings"].append(build_flat_building(
		"chandlery_marine_supply_store", width=8.0, depth=14.0, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_0.png"))
	clear_scene()
	infra_items.append(build_lighthouse("pierhead_lighthouse", tex="wall_tinted_0.png"))
	clear_scene()
	infra_items.append(build_box_prop("lift_drawbridge", (12.0, 6.0, 1.5), 0.75, tex="wall_tinted_9.png"))

	# --- A3: Rail depot, founder's mansion, rail corridor ---
	clear_scene()
	downtown_manifest["downtown_buildings"].append(build_gable_building(
		"rail_depot", width=8.0, depth=25.0, wall_h=3.5, pitch=20.0, overhang=1.2,
		wall_tex="wall_tinted_6.png", roof_tex="roof_tinted_2.png"))
	clear_scene()
	downtown_manifest["downtown_buildings"].append(build_gable_building(
		"founders_mansion", width=16.0, depth=15.0, wall_h=6.5, pitch=32.0, overhang=0.6,
		wall_tex="wall_tinted_9.png", roof_tex="roof_tinted_3.png"))
	clear_scene()
	infra_items.append(build_box_prop("rail_corridor_track_segment", (1.5, 10.0, 0.15), 0.075, tex="wall_tinted_9.png"))
	clear_scene()
	infra_items.append(build_box_prop("railroad_grade_crossing_signal", (0.8, 0.3, 3.5), 1.75, tex="wall_tinted_3.png"))

	# --- A4: Chain ferry ---
	clear_scene()
	infra_items.append(build_box_prop("hand_cranked_chain_ferry", (3.0, 5.0, 0.8), 0.4, tex="wall_tinted_2.png"))
	clear_scene()
	infra_items.append(build_box_prop("ferry_landing_dock", (2.5, 3.0, 0.3), 0.15, tex="wall_tinted_6.png"))

	# --- A5: Cemetery grounds ---
	clear_scene()
	downtown_manifest["downtown_buildings"].append(build_flat_building(
		"cemetery_grounds_chapel", width=8.0, depth=10.0, wall_h=STORY_H,
		wall_tex="wall_tinted_0.png", roof_tex="roof_tinted_2.png"))

	# --- A6: Fairground ---
	clear_scene()
	downtown_manifest["downtown_buildings"].append(build_gable_building(
		"fairground_exhibition_hall_4h", width=20.0, depth=35.0, wall_h=STORY_H * 1.3, pitch=18.0, overhang=0.6,
		wall_tex="wall_tinted_2.png", roof_tex="roof_tinted_3.png"))
	clear_scene()
	infra_items.append(build_box_prop("fairground_livestock_judging_barn", (15.0, 25.0, 4.0), 2.0, tex="wall_tinted_6.png"))
	clear_scene()
	infra_items.append(build_box_prop("fairground_grandstand", (20.0, 6.0, 5.0), 2.5, tex="wall_tinted_0.png"))
	clear_scene()
	infra_items.append(build_box_prop("fairground_midway_ride_ferris_wheel", (10.0, 10.0, 12.0), 6.0, tex="wall_tinted_3.png"))
	clear_scene()
	infra_items.append(build_box_prop("fair_judging_tent_pavilion", (6.0, 6.0, 3.0), 1.5, tex="wall_tinted_0.png"))

	# --- A7: Downtown building-condition props ---
	clear_scene()
	infra_items.append(build_box_prop("plywood_boarded_storefront_panel", (1.0, 0.05, 2.1), 1.05, tex="wall_tinted_6.png"))
	clear_scene()
	infra_items.append(build_box_prop("for_lease_closed_signage_decal", (0.6, 0.03, 0.4), 1.4, tex="wall_tinted_0.png"))
	clear_scene()
	infra_items.append(build_box_prop("modernized_storefront_awning_set", (2.0, 0.6, 0.3), 2.4, tex="wall_tinted_3.png"))

	with open(downtown_manifest_path, "w") as f:
		json.dump(downtown_manifest, f, indent=2)
	with open(infra_manifest_path, "w") as f:
		json.dump(infra_manifest, f, indent=2)
	print("build_part_a_gaps: downtown_buildings now %d, part_a_gaps props now %d" % (
		len(downtown_manifest["downtown_buildings"]), len(infra_items)))


if __name__ == "__main__":
	main()
