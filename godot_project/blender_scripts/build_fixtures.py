"""
Remaining Fixtures -- Kitchen/Bath (5 of 11; the other 6 -- kitchen
sink, toilet, bathroom sink/vanity, tub/shower, mirror, towel rack --
are [UNIVERSAL] items already built in build_interior_props.py) and all
7 Fixtures -- Lighting items from research/interior_props_master_list.md
sections 6-7. Simple primitive geometry, same convention as the other
interior-prop scripts.

Real-world meters. Run headless:
    blender --background --python build_fixtures.py
"""

import sys
import os
import json
import bpy

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
	return {"id": prop_id}


def build_cylinder_prop(prop_id, radius, height, tex, z_offset=0.0, vertices=16):
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height,
		location=(0.0, 0.0, z_offset + height / 2.0), vertices=vertices)
	obj = bpy.context.active_object
	obj.name = prop_id + "-col"
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_lamp(prop_id, base_radius, pole_height, shade_radius, shade_height, tex):
	bpy.ops.mesh.primitive_cylinder_add(radius=base_radius, depth=0.05, location=(0.0, 0.0, 0.025), vertices=12)
	base = bpy.context.active_object
	bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=pole_height, location=(0.0, 0.0, pole_height / 2.0), vertices=8)
	pole = bpy.context.active_object
	bpy.ops.mesh.primitive_cone_add(radius1=shade_radius, radius2=shade_radius * 0.7, depth=shade_height,
		location=(0.0, 0.0, pole_height + shade_height / 2.0), vertices=12)
	shade = bpy.context.active_object
	mat = load_material(prop_id, tex)
	for o in (base, pole, shade):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([base, pole, shade])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_ceiling_fixture(prop_id, radius, drop, tex, arm_count=0):
	bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=drop, location=(0.0, 0.0, -drop / 2.0), vertices=6)
	chain = bpy.context.active_object
	bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=radius * 0.3, depth=radius,
		location=(0.0, 0.0, -drop - radius / 2.0), vertices=16)
	shade = bpy.context.active_object
	mat = load_material(prop_id, tex)
	objs = [chain, shade]
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def build_wall_sign(prop_id, width, height, tex):
	obj = make_box(prop_id, (width, 0.1, height), (0.0, 0.0, 0.0))
	mat = load_material(prop_id, tex)
	obj.data.materials.append(mat)
	cube_uv(obj)
	obj.name = prop_id + "-col"
	export_glb(obj, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	# --- Kitchen/Bath remainder ---
	clear_scene(); items.append(build_box_prop("pedestal_sink", (0.45, 0.4, 0.85), 0.425, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("clawfoot_tub", (0.75, 1.5, 0.55), 0.275, tex="wall_tinted_1.png"))
	clear_scene(); items.append(build_box_prop("standalone_shower_stall", (0.9, 0.9, 2.0), 1.0, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("medicine_cabinet", (0.5, 0.15, 0.6), 1.4, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("utility_sink", (0.55, 0.5, 0.85), 0.425, tex="wall_tinted_9.png"))

	# --- Lighting ---
	clear_scene(); items.append(build_lamp("floor_lamp", base_radius=0.18, pole_height=1.3, shade_radius=0.2, shade_height=0.25, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_lamp("table_lamp", base_radius=0.12, pole_height=0.35, shade_radius=0.15, shade_height=0.2, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_ceiling_fixture("pendant_chandelier_dining", radius=0.35, drop=0.4, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("wall_sconce", (0.15, 0.1, 0.25), 0.0, tex="wall_tinted_10.png"))
	clear_scene(); items.append(build_ceiling_fixture("decorative_grand_chandelier", radius=0.6, drop=0.6, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_wall_sign("marquee_blade_sign", width=1.5, height=0.8, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_wall_sign("neon_signage", width=1.2, height=0.5, tex="wall_tinted_3.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_fixtures: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()
