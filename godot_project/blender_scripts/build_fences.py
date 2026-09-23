"""
Fence models per research/scenery_asset_checklist.txt section 7 and
research/lot_contents/expanded_trees_and_fences.md Part 2. Each fence is
a repeatable straight SEGMENT (a fixed run length, e.g. 3m) meant to be
placed end-to-end by the generator along a lot line or field edge, not
one long fence per lot -- matches how the existing fence_chain_short/
tall/picket/privacy assets already work (confirmed via
editor_assets/manifest.json's "fences" category). Post-and-rail/picket
geometry via repeated small boxes; woven/mesh-style fences (chain-link,
field fence, deer fencing, high-tensile) approximated as a single thin
alpha-cutout-ready panel (a flat quad) rather than modeling individual
wires, consistent with this project's established "chroma-key-to-alpha
hard cutout" convention for thin see-through geometry (fence_chain_*,
door/window glass, porch railings -- see toon.gdshader's own comments).

Real-world meters. Run headless:
    blender --background --python build_fences.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")
SEGMENT_LEN = 3.0


def build_post_rail_fence(fence_id, height, post_spacing, rail_count, post_size, rail_thickness, tex):
	"""Wood-style fence: posts at fixed spacing + horizontal rails --
	covers split-rail (rail_count=2-3, no verticals between) and farm
	field-fence-post-line (posts only, mesh panel added separately for
	woven-wire styles, see build_mesh_panel_fence)."""
	objs = []
	mat = load_material(fence_id, tex)
	n_posts = max(2, int(SEGMENT_LEN / post_spacing) + 1)
	for i in range(n_posts):
		x = -SEGMENT_LEN / 2.0 + i * (SEGMENT_LEN / (n_posts - 1))
		post = make_box(fence_id + "_post_%d" % i, (post_size, post_size, height), (x, 0.0, height / 2.0))
		post.data.materials.append(mat)
		cube_uv(post)
		objs.append(post)
	for r in range(rail_count):
		rz = height * (r + 1) / (rail_count + 1)
		rail = make_box(fence_id + "_rail_%d" % r, (SEGMENT_LEN, rail_thickness, rail_thickness * 1.5), (0.0, 0.0, rz))
		rail.data.materials.append(mat)
		cube_uv(rail)
		objs.append(rail)
	combined = join_objects(objs)
	combined.name = fence_id + "-col"
	export_glb(combined, OUT_DIR, fence_id + ".glb")
	return {"id": fence_id, "segment_length": SEGMENT_LEN, "height": height}


def build_mesh_panel_fence(fence_id, height, post_size, tex):
	"""Woven/mesh-style fence (chain-link+razor-wire industrial, field
	fence, deer fencing, high-tensile electric, snow fence): 2 end posts
	+ a single thin panel quad meant to carry an alpha-cutout mesh/wire
	texture, per this project's established hard-cutout convention
	(discard fully-transparent texels, no blending -- see
	toon.gdshader's own comment on why blend_mix was wrong for exactly
	this kind of geometry)."""
	mat = load_material(fence_id, tex)
	post_a = make_box(fence_id + "_post_a", (post_size, post_size, height), (-SEGMENT_LEN / 2.0, 0.0, height / 2.0))
	post_a.data.materials.append(mat)
	cube_uv(post_a)
	post_b = make_box(fence_id + "_post_b", (post_size, post_size, height), (SEGMENT_LEN / 2.0, 0.0, height / 2.0))
	post_b.data.materials.append(mat)
	cube_uv(post_b)

	bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, height / 2.0))
	panel = bpy.context.active_object
	panel.scale = (SEGMENT_LEN, height, 1.0)
	bpy.context.view_layer.objects.active = panel
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	panel.rotation_euler = (1.5707963, 0.0, 0.0)
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
	panel.name = fence_id + "_panel"
	panel.data.materials.append(mat)
	cube_uv(panel)

	combined = join_objects([post_a, post_b, panel])
	combined.name = fence_id + "-col"
	export_glb(combined, OUT_DIR, fence_id + ".glb")
	return {"id": fence_id, "segment_length": SEGMENT_LEN, "height": height, "cutout_texture": True}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {}
	manifest.setdefault("fences", [])

	clear_scene()
	manifest["fences"].append(build_post_rail_fence(
		"fence_split_rail", height=1.1, post_spacing=1.5, rail_count=2,
		post_size=0.15, rail_thickness=0.08, tex="wall_tinted_6.png"))

	clear_scene()
	manifest["fences"].append(build_post_rail_fence(
		"fence_farm_field_post_line", height=1.2, post_spacing=1.0, rail_count=1,
		post_size=0.12, rail_thickness=0.06, tex="wall_tinted_4.png"))

	clear_scene()
	manifest["fences"].append(build_mesh_panel_fence(
		"fence_field_woven_wire", height=1.3, post_size=0.1, tex="wall_tinted_5.png"))

	clear_scene()
	manifest["fences"].append(build_mesh_panel_fence(
		"fence_corral_livestock", height=1.5, post_size=0.18, tex="wall_tinted_8.png"))

	clear_scene()
	manifest["fences"].append(build_mesh_panel_fence(
		"fence_industrial_chainlink_razor", height=2.4, post_size=0.1, tex="wall_tinted_9.png"))

	clear_scene()
	manifest["fences"].append(build_mesh_panel_fence(
		"fence_deer", height=2.2, post_size=0.08, tex="wall_tinted_0.png"))

	clear_scene()
	manifest["fences"].append(build_mesh_panel_fence(
		"fence_high_tensile_electric", height=1.1, post_size=0.06, tex="wall_tinted_2.png"))

	clear_scene()
	manifest["fences"].append(build_mesh_panel_fence(
		"fence_snow_plastic", height=1.2, post_size=0.06, tex="wall_tinted_1.png"))

	clear_scene()
	manifest["fences"].append(build_post_rail_fence(
		"fence_ornamental_aluminum", height=1.0, post_spacing=1.2, rail_count=2,
		post_size=0.08, rail_thickness=0.05, tex="wall_tinted_10.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_fences: wrote %d fence segments to %s" % (len(manifest["fences"]), OUT_DIR))


if __name__ == "__main__":
	main()
