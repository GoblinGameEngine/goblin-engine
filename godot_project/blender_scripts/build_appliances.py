"""
Appliances category from research/interior_props_master_list.md section
5 (22 items; refrigerator + stove_range already built in
build_interior_props.py as [UNIVERSAL] items -- the remaining 20 here,
including washer/dryer/small-kitchen-appliance-cluster which the master
list ALSO flags [UNIVERSAL] but were missed in the first pass). Simple
box-based geometry, same convention as build_interior_props.py.

Real-world meters. Run headless:
    blender --background --python build_appliances.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "interior_props_assets")


def build_box_prop(prop_id, size, z_center, tex):
	obj = make_box(prop_id, size, (0.0, 0.0, z_center))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id, "size": list(size)}


def build_two_part(prop_id, size_a, z_a, size_b, offset_b, z_b, tex):
	a = make_box(prop_id + "_a", size_a, (0.0, 0.0, z_a))
	b = make_box(prop_id + "_b", size_b, offset_b + (z_b,))
	mat = load_material(prop_id, tex)
	for o in (a, b):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([a, b])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	clear_scene(); items.append(build_box_prop("icebox", (0.55, 0.5, 1.1), 0.55, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("dishwasher_residential", (0.6, 0.6, 0.85), 0.425, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("microwave", (0.5, 0.35, 0.3), 1.2, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_box_prop("washer", (0.65, 0.65, 0.9), 0.45, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("dryer", (0.65, 0.65, 0.9), 0.45, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("chest_freezer", (1.4, 0.7, 0.85), 0.425, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("small_kitchen_appliance_cluster", (0.8, 0.35, 0.35), 1.0, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("stand_mixer_airfryer_winefridge", (0.9, 0.4, 0.5), 1.0, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("institutional_range_oven", (1.8, 0.9, 1.0), 0.5, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("steam_table", (1.5, 0.7, 0.9), 0.45, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("griddle_flattop", (1.0, 0.6, 0.35), 0.9, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("deep_fryer", (0.5, 0.6, 0.9), 0.45, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("large_coffee_urn", (0.35, 0.35, 0.6), 1.0, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("standard_coffee_machine", (0.3, 0.25, 0.4), 0.9, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("malt_mixer_syrup_dispenser", (0.4, 0.3, 0.5), 1.0, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("popcorn_machine", (0.5, 0.45, 0.8), 0.9, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("vending_machine", (0.9, 0.8, 1.8), 0.9, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("commercial_dishwasher", (0.9, 0.8, 1.5), 0.75, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("boiler_unit", (1.0, 0.8, 1.6), 0.8, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("walkin_cooler_freezer", (2.4, 2.0, 2.2), 1.1, tex="wall_tinted_1.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_appliances: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()
