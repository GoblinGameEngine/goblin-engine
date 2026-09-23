"""
The 4 NEW vehicle-category items from
research/interior_props_master_list.md section 12 -- "generic parked
car" and "patrol car" are already covered by the existing
editor_assets/car.glb and police_car.glb, so only the genuinely new
items are built here: a derelict/non-running car (low-income exterior
signal), a fire truck/pumper, a boat/camper/ATV trailer (upper-income
exterior signal), and a generic car-on-a-lift for repair-bay scenes.
Simple low-poly box-based vehicle silhouettes, consistent with this
project's existing low-poly vehicle style.

Real-world meters. Run headless:
    blender --background --python build_vehicles_2.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "interior_props_assets")


def build_car_silhouette(prop_id, tex, cabin_tex=None, wheel_tex=None):
	body = make_box(prop_id + "_body", (1.8, 4.2, 0.5), (0.0, 0.0, 0.55))
	cabin = make_box(prop_id + "_cabin", (1.6, 2.2, 0.5), (0.0, -0.3, 1.05))
	mat = load_material(prop_id + "_body", tex)
	cabin_mat = load_material(prop_id + "_cabin", cabin_tex or tex)
	body.data.materials.append(mat)
	cube_uv(body)
	cabin.data.materials.append(cabin_mat)
	cube_uv(cabin)
	objs = [body, cabin]
	wmat = load_material(prop_id + "_wheel", wheel_tex or tex)
	for sx in (-1, 1):
		for sy in (-1, 1):
			wheel = make_box(prop_id + "_wheel_%d_%d" % (sx, sy), (0.15, 0.5, 0.5),
				(sx * 0.9, sy * 1.5, 0.25))
			wheel.data.materials.append(wmat)
			cube_uv(wheel)
			objs.append(wheel)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_fire_truck(prop_id, tex):
	body = make_box(prop_id + "_body", (2.4, 7.0, 1.3), (0.0, 0.5, 1.1))
	cabin = make_box(prop_id + "_cabin", (2.3, 1.8, 1.2), (0.0, -2.8, 1.35))
	mat = load_material(prop_id, tex)
	objs = [body, cabin]
	for sx in (-1, 1):
		for sy in (-2.8, -0.5, 2.0):
			wheel = make_box(prop_id + "_wheel_%.1f_%d" % (sy, sx), (0.2, 0.6, 0.6), (sx * 1.15, sy, 0.3))
			objs.append(wheel)
	ladder = make_box(prop_id + "_ladder", (0.5, 5.5, 0.3), (0.0, 0.8, 2.0))
	objs.append(ladder)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_trailer(prop_id, width, length, height, tex):
	body = make_box(prop_id + "_body", (width, length, height), (0.0, 0.0, height / 2.0 + 0.4))
	mat = load_material(prop_id, tex)
	objs = [body]
	for sx in (-1, 1):
		wheel = make_box(prop_id + "_wheel_%d" % sx, (0.15, 0.5, 0.4), (sx * (width / 2.0 - 0.1), -length * 0.3, 0.2))
		objs.append(wheel)
	hitch = make_box(prop_id + "_hitch", (0.1, 0.8, 0.15), (0.0, length / 2.0 + 0.4, 0.3))
	objs.append(hitch)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_car_on_lift(prop_id, tex):
	car = build_car_silhouette(prop_id + "_car", tex=tex)
	import bpy
	car_obj = bpy.data.objects[prop_id + "_car-col"]
	car_obj.location.z += 1.2
	bpy.context.view_layer.objects.active = car_obj
	bpy.ops.object.select_all(action="DESELECT")
	car_obj.select_set(True)
	bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
	mat = load_material(prop_id + "_lift", "wall_tinted_9.png")
	objs = [car_obj]
	for sx in (-1, 1):
		post = make_box(prop_id + "_post_%d" % sx, (0.15, 0.15, 2.0), (sx * 1.0, 0.0, 1.0))
		post.data.materials.append(mat)
		cube_uv(post)
		objs.append(post)
	arm = make_box(prop_id + "_arm", (2.2, 0.15, 0.1), (0.0, 0.0, 1.15))
	arm.data.materials.append(mat)
	cube_uv(arm)
	objs.append(arm)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	clear_scene(); items.append(build_car_silhouette("derelict_car", tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_fire_truck("fire_truck_pumper", tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_trailer("boat_camper_atv_trailer", width=1.8, length=4.5, height=0.9, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_car_on_lift("vehicle_in_repair", tex="wall_tinted_3.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_vehicles_2: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()
