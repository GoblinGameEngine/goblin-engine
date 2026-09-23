"""
Small Props/Decor (30 listed items, 29 actual models -- item 5,
"plastic furniture slipcover," is explicitly a material/render-state
variant applied to the existing sofa/armchair meshes per
interior_props_master_list.md's own note, not a separate mesh) from
section 13. The final category in the 265-item master list -- completes
it entirely. Small box/cylinder-primitive props.

Real-world meters. Run headless:
    blender --background --python build_decor.py
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


def build_potted_plant(prop_id, tex):
	bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.3, location=(0.0, 0.0, 0.15), vertices=10)
	pot = bpy.context.active_object
	bpy.ops.mesh.primitive_cone_add(radius1=0.25, radius2=0.02, depth=0.6, location=(0.0, 0.0, 0.3 + 0.3), vertices=8)
	foliage = bpy.context.active_object
	mat = load_material(prop_id, tex)
	for o in (pot, foliage):
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects([pot, foliage])
	combined.name = prop_id + "-col"
	export_glb(combined, OUT_DIR, prop_id + ".glb")
	return {"id": prop_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	with open(manifest_path) as f:
		manifest = json.load(f)
	items = manifest["interior_props"]

	clear_scene(); items.append(build_box_prop("area_rug", (2.0, 1.4, 0.02), 0.01, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("books_shelf_fill", (0.6, 0.2, 0.25), 0.125, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("family_photos_wall_decor", (0.3, 0.03, 0.25), 1.5, tex="wall_tinted_7.png"))
	clear_scene(); items.append(build_box_prop("religious_cultural_iconography", (0.25, 0.05, 0.3), 1.4, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_potted_plant("potted_plant", tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("rag_rug", (1.2, 0.8, 0.02), 0.01, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_cylinder_prop("wall_clock_thermometer", radius=0.15, height=0.05, tex="wall_tinted_0.png", vertices=16))
	clear_scene(); items.append(build_box_prop("magazine_newspaper_rack", (0.4, 0.3, 0.8), 0.4, tex="wall_tinted_5.png"))
	clear_scene(); items.append(build_box_prop("decorative_wall_mirror", (0.5, 0.03, 0.7), 1.3, tex="wall_tinted_8.png"))
	clear_scene(); items.append(build_box_prop("taxidermy_wall_mount", (0.4, 0.3, 0.35), 1.6, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("wall_art_framed", (0.5, 0.03, 0.4), 1.4, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_box_prop("historical_portrait_plaque", (0.45, 0.04, 0.55), 1.6, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("wall_menu_board_chalkboard", (0.9, 0.04, 0.6), 1.5, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("servants_call_bell_box", (0.25, 0.1, 0.3), 1.3, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("canned_goods_pantry_stock", (0.5, 0.25, 0.3), 0.15, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("flour_grain_bin_small", (0.35, 0.35, 0.5), 0.25, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("root_vegetable_basket", (0.35, 0.3, 0.25), 0.125, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("boot_tray", (0.5, 0.3, 0.06), 0.03, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("coat_hook_row", (0.8, 0.06, 0.15), 1.5, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_box_prop("storage_boxes_trunks", (0.6, 0.4, 0.4), 0.2, tex="wall_tinted_4.png"))
	clear_scene(); items.append(build_box_prop("dress_form", (0.4, 0.3, 0.9), 0.45, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("home_gym_equipment", (0.6, 1.5, 1.2), 0.6, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("hobbyist_workshop_buildout", (1.0, 0.5, 0.9), 0.45, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("sewing_machine", (0.5, 0.3, 0.4), 0.75, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_box_prop("garment_steamer", (0.3, 0.3, 0.9), 0.45, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_box_prop("pin_cushion_notions_shelf", (0.5, 0.2, 0.3), 0.9, tex="wall_tinted_2.png"))
	clear_scene(); items.append(build_box_prop("small_desk_flag", (0.15, 0.15, 0.4), 0.9, tex="wall_tinted_3.png"))
	clear_scene(); items.append(build_cylinder_prop("belfry_bell", radius=0.3, height=0.4, tex="wall_tinted_9.png", z_offset=0.2, vertices=12))
	clear_scene(); items.append(build_box_prop("barn_cat_pigeon_roost", (0.4, 0.3, 0.2), 0.1, tex="wall_tinted_2.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_decor: manifest now has %d total interior props" % len(items))


if __name__ == "__main__":
	main()
