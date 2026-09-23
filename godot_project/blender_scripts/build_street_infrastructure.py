"""
Street/Park Furniture and Public Infrastructure (15 items) from
research/scenery_asset_checklist_expansion.md Part B3 -- the single
largest completely-unaddressed gap found in the completeness audit
(generic municipal street furniture: traffic control, utilities,
public seating/trash), despite extensive road/intersection/bridge
coverage elsewhere. Simple box/cylinder-primitive props, plus a couple
of flat ground-decal patches (crosswalk, manhole, storm drain).

Real-world meters. Run headless:
    blender --background --python build_street_infrastructure.py
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


def build_ground_decal(prop_id, width, depth, tex):
	obj = make_box(prop_id, (width, depth, 0.01), (0.0, 0.0, 0.005))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_sign_on_post(prop_id, sign_w, sign_h, post_h, tex):
	post = make_box(prop_id + "_post", (0.06, 0.06, post_h), (0.0, 0.0, post_h / 2.0))
	sign = make_box(prop_id + "_sign", (sign_w, 0.03, sign_h), (0.0, 0.0, post_h))
	mat = load_material(prop_id, tex)
	for o in (post, sign):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([post, sign])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {}
	manifest.setdefault("street_infrastructure", [])
	items = manifest["street_infrastructure"]

	clear_scene(); items.append(build_box_prop("public_street_bench", (1.8, 0.5, 0.85), 0.425, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_cylinder_prop("public_trash_can", radius=0.28, height=0.85, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("bike_rack_public", (2.0, 0.1, 0.7), 0.35, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_box_prop("newspaper_vending_box", (0.4, 0.4, 1.0), 0.5, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_cylinder_prop("parking_meter", radius=0.08, height=1.2, tex="wall_tinted_9.png", vertices=8))
	clear_scene(); items.append(build_cylinder_prop("utility_power_pole", radius=0.15, height=9.0, tex="wall_tinted_6.png", vertices=8))
	clear_scene(); items.append(build_box_prop("pad_mounted_transformer", (0.9, 0.7, 1.0), 0.5, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_ground_decal("manhole_cover", width=0.6, depth=0.6, tex="road_tinted.png"))
	clear_scene(); items.append(build_ground_decal("storm_drain_grate", width=0.9, depth=0.4, tex="road_tinted.png"))
	clear_scene(); items.append(build_sign_on_post("traffic_light_signal", sign_w=0.35, sign_h=1.0, post_h=3.5, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_sign_on_post("stop_sign", sign_w=0.6, sign_h=0.6, post_h=2.1, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_sign_on_post("street_name_sign", sign_w=0.7, sign_h=0.15, post_h=2.4, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_ground_decal("crosswalk_marking", width=3.0, depth=1.5, tex="road_tinted.png"))
	clear_scene(); items.append(build_sign_on_post("rural_route_speed_limit_sign", sign_w=0.5, sign_h=0.7, post_h=2.0, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_sign_on_post("yield_sign", sign_w=0.6, sign_h=0.55, post_h=1.9, tex="wall_tinted_0.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_street_infrastructure: wrote %d items to %s" % (len(items), OUT_DIR))


if __name__ == "__main__":
	main()
