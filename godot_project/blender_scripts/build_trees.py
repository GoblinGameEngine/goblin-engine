"""
New tree species/variants from research/lot_contents/
expanded_trees_and_fences.md Part 1 (21 items across downtown street
trees, residential yard trees, farm zone, riparian, and seasonal/
condition variants) -- simple trunk+canopy geometry, consistent with
the existing 7 tree assets in editor_assets/ (tree_autumn, tree_conifer,
etc.), NOT the flat-sprite billboard technique used for crop fields
(gen_crop_sprites.py) since these are individually-placed yard/street/
farm trees, not a dense MultiMesh-batched field crop.

Real-world meters. Run headless:
    blender --background --python build_trees.py
"""

import sys
import os
import json
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, export_glb

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")


def build_tree(tree_id, trunk_h, trunk_r, canopy_type, canopy_size, trunk_tex, canopy_tex):
	bpy.ops.mesh.primitive_cylinder_add(radius=trunk_r, depth=trunk_h,
		location=(0.0, 0.0, trunk_h / 2.0), vertices=8)
	trunk = bpy.context.active_object
	trunk_mat = load_material(tree_id + "_trunk", trunk_tex)
	trunk.data.materials.append(trunk_mat)
	cube_uv(trunk)
	objs = [trunk]

	if canopy_type != "none":
		canopy_mat = load_material(tree_id + "_canopy", canopy_tex)
		if canopy_type == "round":
			bpy.ops.mesh.primitive_uv_sphere_add(radius=canopy_size, location=(0.0, 0.0, trunk_h + canopy_size * 0.8), segments=10, ring_count=6)
		elif canopy_type == "cone":
			bpy.ops.mesh.primitive_cone_add(radius1=canopy_size, radius2=0.05, depth=canopy_size * 2.2,
				location=(0.0, 0.0, trunk_h + canopy_size * 1.1), vertices=10)
		elif canopy_type == "oval":
			bpy.ops.mesh.primitive_uv_sphere_add(radius=canopy_size, location=(0.0, 0.0, trunk_h + canopy_size), segments=10, ring_count=6)
			bpy.context.active_object.scale = (1.0, 1.0, 1.4)
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		canopy = bpy.context.active_object
		canopy.data.materials.append(canopy_mat)
		cube_uv(canopy)
		objs.append(canopy)

	combined = join_objects(objs)
	combined.name = tree_id + "-col"
	export_glb(combined, OUT_DIR, tree_id + ".glb")
	return {"id": tree_id, "canopy_type": canopy_type}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {}
	manifest.setdefault("trees", [])
	items = manifest["trees"]

	# Downtown street trees.
	clear_scene(); items.append(build_tree("tree_honeylocust", trunk_h=3.5, trunk_r=0.18, canopy_type="round", canopy_size=2.0, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_littleleaf_linden", trunk_h=3.0, trunk_r=0.2, canopy_type="cone", canopy_size=1.8, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_london_planetree", trunk_h=4.0, trunk_r=0.25, canopy_type="round", canopy_size=2.3, trunk_tex="wall_tinted_0.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_red_maple", trunk_h=3.2, trunk_r=0.18, canopy_type="round", canopy_size=1.9, trunk_tex="wall_tinted_6.png", canopy_tex="roof_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_kentucky_coffeetree", trunk_h=3.8, trunk_r=0.2, canopy_type="oval", canopy_size=1.7, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))

	# Residential yard trees.
	clear_scene(); items.append(build_tree("tree_american_elm_legacy", trunk_h=4.5, trunk_r=0.3, canopy_type="round", canopy_size=2.8, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_oak_mature", trunk_h=4.0, trunk_r=0.35, canopy_type="round", canopy_size=2.6, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_sugar_norway_maple", trunk_h=3.5, trunk_r=0.22, canopy_type="round", canopy_size=2.1, trunk_tex="wall_tinted_6.png", canopy_tex="roof_tinted_1.png"))
	clear_scene(); items.append(build_tree("tree_dead_ash_stump", trunk_h=1.2, trunk_r=0.28, canopy_type="none", canopy_size=0.0, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_tree("tree_white_pine_blue_spruce", trunk_h=3.0, trunk_r=0.2, canopy_type="cone", canopy_size=1.6, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_8.png"))

	# Farm zone.
	clear_scene(); items.append(build_tree("tree_eastern_redcedar", trunk_h=3.5, trunk_r=0.15, canopy_type="cone", canopy_size=1.3, trunk_tex="wall_tinted_6.png", canopy_tex="roof_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_norway_white_spruce", trunk_h=4.0, trunk_r=0.18, canopy_type="cone", canopy_size=1.7, trunk_tex="wall_tinted_6.png", canopy_tex="roof_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_osage_orange_relic", trunk_h=2.5, trunk_r=0.3, canopy_type="round", canopy_size=1.8, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_apple_orchard", trunk_h=2.0, trunk_r=0.15, canopy_type="round", canopy_size=1.3, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_cherry_orchard", trunk_h=2.0, trunk_r=0.14, canopy_type="round", canopy_size=1.2, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_tree("tree_black_walnut", trunk_h=4.5, trunk_r=0.3, canopy_type="oval", canopy_size=2.2, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))

	# Riparian/waterside.
	clear_scene(); items.append(build_tree("tree_black_willow", trunk_h=3.0, trunk_r=0.22, canopy_type="oval", canopy_size=2.0, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_eastern_cottonwood", trunk_h=4.5, trunk_r=0.35, canopy_type="round", canopy_size=2.7, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_tree("tree_american_sycamore", trunk_h=4.2, trunk_r=0.32, canopy_type="round", canopy_size=2.5, trunk_tex="wall_tinted_0.png", canopy_tex="wall_tinted_2.png"))

	# Seasonal/condition variants.
	clear_scene(); items.append(build_tree("tree_storm_damaged", trunk_h=2.8, trunk_r=0.25, canopy_type="oval", canopy_size=1.2, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_tree("tree_young_replacement_sapling", trunk_h=1.5, trunk_r=0.06, canopy_type="round", canopy_size=0.5, trunk_tex="wall_tinted_6.png", canopy_tex="wall_tinted_2.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_trees: wrote %d trees to %s" % (len(items), OUT_DIR))


if __name__ == "__main__":
	main()
