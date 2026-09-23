"""
Animals/Wildlife (10 items) from
research/scenery_asset_checklist_expansion.md Part B5 -- completely
absent category despite barns/coops/farms/lake implying livestock and
wildlife throughout. Simple low-poly box-based creature silhouettes
(body+head+4 legs for quadrupeds, body+head+2 legs for birds),
consistent with this project's low-poly aesthetic.

Real-world meters. Run headless:
    blender --background --python build_animals.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_helpers import REPO, clear_scene, load_material, cube_uv, join_objects, make_box, export_glb

OUT_DIR = os.path.join(REPO, "assets", "infrastructure_assets")


def build_quadruped(animal_id, body_size, body_h, leg_h, head_size, tex):
	body = make_box(animal_id + "_body", body_size, (0.0, 0.0, leg_h + body_h / 2.0))
	head = make_box(animal_id + "_head", head_size, (0.0, -body_size[1] / 2.0 - head_size[1] / 2.0 + 0.05, leg_h + body_h * 0.8))
	mat = load_material(animal_id, tex)
	objs = [body, head]
	for sx in (-1, 1):
		for sy in (-1, 1):
			leg = make_box(animal_id + "_leg_%d_%d" % (sx, sy), (body_size[0] * 0.15, body_size[0] * 0.15, leg_h),
				(sx * body_size[0] * 0.35, sy * body_size[1] * 0.35, leg_h / 2.0))
			objs.append(leg)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = animal_id + "-col"
	export_glb(combined, OUT_DIR, animal_id + ".glb")
	return {"id": animal_id}


def build_small_pet(animal_id, body_size, leg_h, tex):
	return build_quadruped(animal_id, body_size, body_size[2], leg_h, (body_size[0]*0.6, body_size[0]*0.6, body_size[2]*0.7), tex)


def build_bird(animal_id, body_size, leg_h, tex):
	body = make_box(animal_id + "_body", body_size, (0.0, 0.0, leg_h + body_size[2] / 2.0))
	head = make_box(animal_id + "_head", (body_size[0]*0.5, body_size[0]*0.5, body_size[0]*0.5),
		(0.0, -body_size[1]/2.0, leg_h + body_size[2]*0.9))
	mat = load_material(animal_id, tex)
	objs = [body, head]
	for sx in (-1, 1):
		leg = make_box(animal_id + "_leg_%d" % sx, (0.02, 0.02, leg_h), (sx * body_size[0] * 0.2, 0.0, leg_h / 2.0))
		objs.append(leg)
	for o in objs:
		o.data.materials.append(mat)
		cube_uv(o)
	combined = join_objects(objs)
	combined.name = animal_id + "-col"
	export_glb(combined, OUT_DIR, animal_id + ".glb")
	return {"id": animal_id}


def main():
	os.makedirs(OUT_DIR, exist_ok=True)
	manifest_path = os.path.join(OUT_DIR, "manifest.json")
	if os.path.exists(manifest_path):
		with open(manifest_path) as f:
			manifest = json.load(f)
	else:
		manifest = {}
	manifest.setdefault("animals", [])
	items = manifest["animals"]

	clear_scene(); items.append(build_quadruped("animal_cow", (0.7, 1.5, 1.0), 1.0, 0.9, (0.5, 0.5, 0.6), tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_bird("animal_chicken", (0.25, 0.35, 0.3), 0.2, tex="wall_tinted_0.png"))
	clear_scene(); items.append(build_quadruped("animal_pig", (0.5, 1.0, 0.6), 0.55, 0.35, (0.35, 0.35, 0.35), tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_quadruped("animal_horse", (0.7, 1.8, 1.3), 1.3, 1.1, (0.5, 0.55, 0.6), tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_small_pet("animal_dog", (0.3, 0.6, 0.4), 0.3, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_small_pet("animal_cat", (0.2, 0.4, 0.25), 0.2, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_bird("animal_bird_flock", (0.1, 0.15, 0.12), 0.06, tex="wall_tinted_9.png"))
	clear_scene(); items.append(build_quadruped("animal_deer", (0.4, 1.1, 0.9), 0.85, 0.8, (0.3, 0.4, 0.4), tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_small_pet("animal_squirrel", (0.12, 0.25, 0.15), 0.12, tex="wall_tinted_6.png"))
	clear_scene(); items.append(build_bird("animal_canada_goose", (0.25, 0.5, 0.35), 0.25, tex="wall_tinted_9.png"))

	with open(manifest_path, "w") as f:
		json.dump(manifest, f, indent=2)
	print("build_animals: wrote %d animals to %s" % (len(items), OUT_DIR))


if __name__ == "__main__":
	main()
