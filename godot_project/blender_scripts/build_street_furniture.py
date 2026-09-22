"""
Builds fire_hydrant.glb and lamp_post.glb -- small street-furniture props
for StreetFurniture.gd to place along downtown/residential streets. Unlike
building_helpers.py's buildings, these are solid small props: no interior,
no door openings, no manifest entry needed (StreetFurniture.gd just
instances the .glb directly). Flat solid-color materials (no texture
image) rather than generating new _detail/_tinted texture files for two
tiny single-color props -- ToonShading.gd's material conversion already
handles a textureless BaseMaterial3D fine (falls back to albedo_color).

Run: blender --background --python blender_scripts/build_street_furniture.py
Writes: assets/street_furniture/fire_hydrant.glb, lamp_post.glb
"""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import FT, REPO, clear_scene, cube_uv, join_objects, export_glb

OUT_DIR = os.path.join(REPO, "assets", "street_furniture")


def solid_material(name, color):
	mat = bpy.data.materials.new(name)
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes.get("Principled BSDF")
	bsdf.inputs["Base Color"].default_value = (*color, 1.0)
	bsdf.inputs["Roughness"].default_value = 0.55
	return mat


def make_cylinder(name, radius, depth, location, material, vertices=12):
	bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices, location=location)
	obj = bpy.context.active_object
	obj.name = name
	obj.data.materials.append(material)
	return obj


def make_cone(name, radius1, radius2, depth, location, material, vertices=12):
	bpy.ops.mesh.primitive_cone_add(radius1=radius1, radius2=radius2, depth=depth, vertices=vertices, location=location)
	obj = bpy.context.active_object
	obj.name = name
	obj.data.materials.append(material)
	return obj


def build_fire_hydrant():
	"""~0.75m tall, classic red hydrant silhouette: flanged base, main
	body, domed cap with a top nozzle, two side nozzle caps."""
	clear_scene()
	red = solid_material("hydrant_red", (0.62, 0.05, 0.04))
	dark = solid_material("hydrant_dark", (0.12, 0.1, 0.09))

	parts = []
	parts.append(make_cylinder("base_flange", 0.18, 0.12, (0, 0, 0.06), red))
	parts.append(make_cylinder("body", 0.13, 0.42, (0, 0, 0.12 + 0.21), red))
	parts.append(make_cone("dome", 0.13, 0.07, 0.16, (0, 0, 0.12 + 0.42 + 0.08), red))
	parts.append(make_cylinder("top_nozzle", 0.045, 0.09, (0, 0, 0.12 + 0.42 + 0.16 + 0.045), dark))
	# Two side nozzle caps, sticking out perpendicular to the body.
	for side in (-1, 1):
		cap = make_cylinder("side_nozzle", 0.06, 0.1, (side * (0.13 + 0.05), 0, 0.12 + 0.42 * 0.55), dark)
		cap.rotation_euler[1] = math_pi_half()
		bpy.context.view_layer.objects.active = cap
		bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
		parts.append(cap)

	combined = join_objects(parts)
	combined.name = "fire_hydrant"
	cube_uv(combined)
	os.makedirs(OUT_DIR, exist_ok=True)
	export_glb(combined, OUT_DIR, "fire_hydrant.glb")
	print(f"wrote {OUT_DIR}/fire_hydrant.glb")


def math_pi_half():
	import math
	return math.pi / 2.0


def build_lamp_post():
	"""~4.3m tall straight pole with a flared base and a lantern-style
	head -- generic enough to read correctly on both downtown's wide
	streets and residential's local ones."""
	clear_scene()
	metal = solid_material("lamp_metal", (0.09, 0.09, 0.1))
	glass = solid_material("lamp_glass", (0.95, 0.85, 0.55))
	glass.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 1.5
	glass.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value = (0.95, 0.85, 0.55, 1.0)

	parts = []
	parts.append(make_cone("base_flare", 0.16, 0.08, 0.25, (0, 0, 0.125), metal))
	pole_h = 3.6
	parts.append(make_cylinder("pole", 0.055, pole_h, (0, 0, 0.25 + pole_h / 2.0), metal))
	head_z = 0.25 + pole_h
	parts.append(make_cylinder("head_base", 0.1, 0.08, (0, 0, head_z + 0.04), metal))
	parts.append(make_cylinder("lantern", 0.14, 0.32, (0, 0, head_z + 0.08 + 0.16), glass, vertices=8))
	parts.append(make_cone("head_cap", 0.16, 0.02, 0.18, (0, 0, head_z + 0.08 + 0.32 + 0.09), metal))

	combined = join_objects(parts)
	combined.name = "lamp_post"
	cube_uv(combined)
	os.makedirs(OUT_DIR, exist_ok=True)
	export_glb(combined, OUT_DIR, "lamp_post.glb")
	print(f"wrote {OUT_DIR}/lamp_post.glb")


if __name__ == "__main__":
	build_fire_hydrant()
	build_lamp_post()
