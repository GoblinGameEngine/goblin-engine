"""
The 4 genuinely static junction-shape models from
research/scenery_asset_checklist.txt section 4: T-intersection, 4-way
intersection, cul-de-sac turnaround, and the courthouse-square special
intersection. Built as flat paved PATCHES (a shaped quad carrying the
existing road texture) meant to be dropped at a junction point,
complementing -- not replacing -- StreetBuilder.gd's existing
segment-by-segment straight-road generation.

The rest of section 4's list (river-following road segment, curvilinear
residential segment, rail-corridor-parallel segment, narrow no-curb
segment, farm access lane, minor drainage-spur segment) are NOT static
models -- they're path-following/curve-generation logic that belongs in
StreetBuilder.gd itself (extending its existing per-ring-segment
approach), same as how the currently-EXISTING straight street types are
implemented as generator code, not discrete assets. Deliberately not
modeled here; flagged in generated_models_registry.md as a future
GDScript task instead.

Real-world meters. Run headless:
    blender --background --python build_intersections.py
"""

import sys
import os
import json
import bpy
import bmesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, export_glb, make_box

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")


def build_flat_patch(prop_id, verts_2d, tex):
	bm = bmesh.new()
	bverts = [bm.verts.new((x, y, 0.02)) for x, y in verts_2d]
	bm.faces.new(bverts)
	bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
	mesh = bpy.data.meshes.new(prop_id + "_mesh")
	bm.to_mesh(mesh)
	bm.free()
	obj = bpy.data.objects.new(prop_id, mesh)
	bpy.context.collection.objects.link(obj)
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
	manifest.setdefault("intersections", [])
	items = manifest["intersections"]

	# T-intersection: a wide cross-shaped patch, one arm capped (the "T").
	clear_scene()
	items.append(build_flat_patch("intersection_t", [
		(-10, -6), (10, -6), (10, 6), (3, 6), (3, 20), (-3, 20), (-3, 6), (-10, 6),
	], tex="road_tinted.png"))

	# 4-way intersection: a plus-shaped patch, all 4 arms open.
	clear_scene()
	items.append(build_flat_patch("intersection_4way", [
		(-6, -20), (6, -20), (6, -6), (20, -6), (20, 6), (6, 6),
		(6, 20), (-6, 20), (-6, 6), (-20, 6), (-20, -6), (-6, -6),
	], tex="road_tinted.png"))

	# Cul-de-sac turnaround: a circular pad fed by one straight arm.
	clear_scene()
	import math
	circle_pts = [(9.1 * math.cos(a), 9.1 * math.sin(a) + 9.1) for a in
		[i * math.pi / 12.0 for i in range(24)]]
	items.append(build_flat_patch("cul_de_sac_turnaround", [(-5, -8), (5, -8), (5, 0)] + circle_pts + [(-5, 0)], tex="road_tinted.png"))

	# Courthouse-square intersection: a large open plaza patch (wider
	# than a standard 4-way) framing where the civic block sits.
	clear_scene()
	items.append(build_flat_patch("intersection_courthouse_square", [
		(-8, -30), (8, -30), (8, -8), (30, -8), (30, 8), (8, 8),
		(8, 30), (-8, 30), (-8, 8), (-30, 8), (-30, -8), (-8, -8),
	], tex="road_tinted.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_intersections: wrote %d intersection patches to %s" % (len(items), OUT_DIR))


if __name__ == "__main__":
	main()
