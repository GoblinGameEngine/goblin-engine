extends Node
class_name OpeningsSetup

# Instantiates the door/window sprite scenes recorded in map_layout.json's
# "openings" list (see build_neighborhood.py's ALL_OPENINGS/
# register_opening()) -- doors and windows are no longer Blender geometry
# at all (the wall openings themselves are still real holes, built there),
# just lightweight Godot scenes placed at runtime, same pattern Main.gd
# already uses for the 3 vehicle models. Windows are purely decorative
# (no collision -- see reference/memory.txt for why walkable window holes
# were an accepted, deliberate scope trim, not an oversight) and cheap in
# bulk; doors are real interactive StaticBody3D instances (see Door.gd)
# since each needs its own open/closed state.

const DOOR_SCENE_PATH := "res://scenes/Door.tscn"
const WINDOW_SCENE_PATH := "res://scenes/Window.tscn"

static func setup(root: Node3D, openings: Array) -> Dictionary:
	var door_scene: PackedScene = load(DOOR_SCENE_PATH)
	var window_scene: PackedScene = load(WINDOW_SCENE_PATH)
	var doors := 0
	var windows := 0
	for o in openings:
		var kind: String = o.get("kind", "")
		var width: float = o["width"]
		var height: float = o["height"]
		var plane_rot: float = o["plane_rot"]
		if kind == "door":
			var inst: Door = door_scene.instantiate()
			root.add_child(inst)
			inst.global_position = Vector3(o["hinge_x"], o["z"], -o["hinge_y"])
			inst.rotation.y = plane_rot
			doors += 1
		elif kind == "window":
			var inst2: Node3D = window_scene.instantiate()
			root.add_child(inst2)
			inst2.global_position = Vector3(o["x"], o["z"] + height / 2.0, -o["y"])
			inst2.rotation.y = plane_rot
			inst2.scale = Vector3(width, height, 1.0)
			windows += 1
	return {"doors": doors, "windows": windows}
