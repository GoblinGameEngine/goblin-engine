"""
Park/Recreation Equipment (B4, 10), Cemetery-Specific Props (B6, 7), and
Downtown-Scale Seasonal Decoration (B7, 5) from
research/scenery_asset_checklist_expansion.md -- 22 items total. Simple
box/cylinder-primitive props.

Real-world meters. Run headless:
    blender --background --python build_park_cemetery_decor.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")


def build_box_prop(prop_id, size, z_center, tex):
	obj = make_box(prop_id, size, (0.0, 0.0, z_center))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_cylinder_prop(prop_id, radius, height, tex, z_offset=0.0, vertices=12):
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
		location=(0.0, 0.0, z_offset + height / 2.0), vertices=vertices)
	obj = bpy.context.active_object
	obj.name = prop_id + "-col"
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_gazebo(prop_id, tex):
	mat = load_material(prop_id, tex)
	objs = []
	floor = make_box(prop_id + "_floor", (3.0, 3.0, 0.15), (0.0, 0.0, 0.5))
	objs.append(floor)
	import math
	for i in range(6):
		ang = i * math.pi / 3.0
		post = make_box(prop_id + "_post_%d" % i, (0.1, 0.1, 2.4), (1.3 * math.cos(ang), 1.3 * math.sin(ang), 0.5 + 1.2))
		objs.append(post)
	bpy.ops.mesh.primitive_cone_add(radius1=1.8, radius2=0.1, depth=1.2, location=(0.0, 0.0, 0.5 + 2.4 + 0.6), vertices=6)
	roof = bpy.context.active_object
	objs.append(roof)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_headstone(prop_id, width, height, tex, rounded_top=True):
	obj = make_box(prop_id, (width, 0.15, height), (0.0, 0.0, height / 2.0))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {}
	manifest.setdefault("park_cemetery_decor", [])
	items = manifest["park_cemetery_decor"]

	# --- B4: Park/recreation equipment ---
	clear_scene(); items.append(build_box_prop("playground_slide", (1.0, 3.0, 1.8), 0.9, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("jungle_gym_climbing_structure", (2.5, 2.5, 2.0), 1.0, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("swing_set_park_multibay", (4.0, 1.8, 2.4), 1.2, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("baseball_backstop_bleachers", (6.0, 1.0, 4.0), 2.0, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("basketball_court_outdoor", (15.0, 28.0, 0.05), 0.025, tex="road_tinted.png"))
	clear_scene(); items.append(build_gazebo("gazebo_bandstand", tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("war_memorial_monument", (1.2, 0.8, 2.2), 1.1, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_cylinder_prop("park_civic_flagpole", radius=0.08, height=7.0, tex="wall_tinted_9.png", vertices=8))
	clear_scene(); items.append(build_box_prop("picnic_shelter_pavilion", (5.0, 5.0, 2.6), 1.3, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_cylinder_prop("park_drinking_fountain", radius=0.2, height=0.9, tex="wall_tinted_0.png"))

	# --- B6: Cemetery-specific props ---
	clear_scene(); items.append(build_headstone("headstone_upright_slab", width=0.6, height=0.9, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_headstone("headstone_obelisk_monument", width=0.5, height=2.0, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("headstone_flat_flush", (0.5, 0.7, 0.05), 0.025, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("mausoleum_family_scale", (2.5, 3.0, 2.8), 1.4, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("cemetery_gate_entrance_arch", (3.5, 0.3, 2.8), 1.4, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("cemetery_access_lane", (3.0, 10.0, 0.03), 0.015, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("cemetery_memorial_bench", (1.5, 0.45, 0.45), 0.225, tex="wall_tinted_0.png"))

	# --- B7: Downtown-scale seasonal decoration ---
	clear_scene(); items.append(build_box_prop("string_lights_main_street", (10.0, 0.05, 0.05), 5.0, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("banner_pole_seasonal", (0.5, 0.05, 1.2), 3.5, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("town_christmas_tree", (2.5, 2.5, 5.0), 2.5, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_cylinder_prop("wreath_lamppost", radius=0.3, height=0.15, tex="wall_tinted_2.png", z_offset=2.5))
	clear_scene(); items.append(build_box_prop("holiday_parade_bunting_set", (2.0, 0.05, 0.4), 3.5, tex="wall_tinted_3.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_park_cemetery_decor: wrote %d items to %s" % (len(items), OUT_DIR))


if __name__ == "__main__":
	main()
