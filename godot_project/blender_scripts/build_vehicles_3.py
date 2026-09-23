"""
Vehicles (B2, 13 items) from research/scenery_asset_checklist_expansion.md
-- patrol car and fire truck/pumper already exist (interior_props_assets),
not duplicated here. Low-poly box-based vehicle silhouettes, same
convention as build_vehicles_2.py.

Real-world meters. Run headless:
    blender --background --python build_vehicles_3.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")


def build_car_silhouette(prop_id, tex, width=1.8, length=4.2, cabin_h=0.5, body_h=0.5):
	body = make_box(prop_id + "_body", (width, length, body_h), (0.0, 0.0, 0.3 + body_h / 2.0))
	cabin = make_box(prop_id + "_cabin", (width * 0.9, length * 0.5, cabin_h), (0.0, -length * 0.07, 0.3 + body_h + cabin_h / 2.0))
	mat = load_material(prop_id, tex)
	objs = [body, cabin]
	for sx in (-1, 1):
		for sy in (-1, 1):
			wheel = make_box(prop_id + "_wheel_%d_%d" % (sx, sy), (0.15, 0.5, 0.5),
				(sx * width * 0.5, sy * length * 0.35, 0.25))
			objs.append(wheel)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_truck(prop_id, tex, width=2.2, length=6.5, box_h=2.4):
	cab = make_box(prop_id + "_cab", (2.1, 1.8, 1.6), (0.0, -length / 2.0 + 0.9, 0.9))
	box = make_box(prop_id + "_box", (width, length - 2.0, box_h), (0.0, 1.0, box_h / 2.0 + 0.5))
	mat = load_material(prop_id, tex)
	objs = [cab, box]
	for sx in (-1, 1):
		for sy in (-2.0, 0.0, 2.0):
			wheel = make_box(prop_id + "_wheel_%.1f_%d" % (sy, sx), (0.2, 0.6, 0.6), (sx * width * 0.5, sy, 0.3))
			objs.append(wheel)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_two_wheeler(prop_id, tex, length, height, thin=True):
	body = make_box(prop_id + "_body", (0.4 if thin else 0.6, length, height), (0.0, 0.0, height / 2.0))
	mat = load_material(prop_id, tex)
	objs = [body]
	for sy in (-1, 1):
		wheel = make_box(prop_id + "_wheel_%d" % sy, (0.1, 0.5, 0.5), (0.0, sy * length * 0.4, 0.25))
		objs.append(wheel)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_recreational_vehicle(prop_id, tex, radius, height, z_offset=0.0, vertices=10):
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
		location=(0.0, 0.0, z_offset + height / 2.0), vertices=vertices, rotation=(1.5707963, 0.0, 0.0))
	obj = bpy.context.active_object
	obj.name = prop_id + "-col"
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
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
	manifest.setdefault("vehicles", [])
	items = manifest["vehicles"]

	clear_scene(); items.append(build_truck("vehicle_school_bus", tex="wall_tinted_3.png", width=2.4, length=8.0, box_h=2.2))
	clear_scene(); items.append(build_truck("vehicle_delivery_van_box_truck", tex="wall_tinted_0.png", width=2.0, length=5.5, box_h=2.0))
	clear_scene(); items.append(build_car_silhouette("vehicle_ambulance", tex="wall_tinted_0.png", width=2.0, length=5.5, cabin_h=1.2, body_h=0.5))
	clear_scene(); items.append(build_truck("vehicle_tow_truck", tex="wall_tinted_9.png", width=2.0, length=6.0, box_h=1.2))
	clear_scene(); items.append(build_two_wheeler("vehicle_motorcycle", tex="wall_tinted_6.png", length=1.8, height=0.8))
	clear_scene(); items.append(build_two_wheeler("vehicle_bicycle", tex="wall_tinted_9.png", length=1.5, height=0.9, thin=True))
	clear_scene(); items.append(build_truck("vehicle_semi_tractor_trailer", tex="wall_tinted_10.png", width=2.4, length=14.0, box_h=2.6))
	clear_scene(); items.append(build_box_prop_local("vehicle_combine_harvester", (3.0, 6.0, 3.0), 1.5, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_truck("vehicle_grain_truck", tex="wall_tinted_1.png", width=2.3, length=7.0, box_h=2.0))
	clear_scene(); items.append(build_recreational_vehicle("vehicle_snowmobile", tex="wall_tinted_3.png", radius=0.4, height=2.0, z_offset=0.2))
	clear_scene(); items.append(build_box_prop_local("vehicle_atv", (1.0, 1.8, 0.9), 0.45, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_recreational_vehicle("vehicle_boat_pontoon", tex="wall_tinted_0.png", radius=1.0, height=5.0, z_offset=0.3))
	clear_scene(); items.append(build_truck("vehicle_municipal_snowplow_dump_truck", tex="wall_tinted_9.png", width=2.4, length=7.0, box_h=1.8))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_vehicles_3: wrote %d vehicles to %s" % (len(items), OUT_DIR))


def build_box_prop_local(prop_id, size, z_center, tex):
	obj = make_box(prop_id, size, (0.0, 0.0, z_center))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


if __name__ == "__main__":
	main()
