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
const INTERIOR_DOOR_SCENE_PATH := "res://scenes/InteriorDoor.tscn"
const WINDOW_SCENE_PATH := "res://scenes/Window.tscn"

static func setup(root: Node3D, openings: Array) -> Dictionary:
	var door_scene: PackedScene = load(DOOR_SCENE_PATH)
	var interior_door_scene: PackedScene = load(INTERIOR_DOOR_SCENE_PATH)
	var window_scene: PackedScene = load(WINDOW_SCENE_PATH)
	var doors := 0
	var windows := 0
	for o in openings:
		var kind: String = o.get("kind", "")
		var width: float = o["width"]
		var height: float = o["height"]
		var plane_rot: float = o["plane_rot"]
		if kind == "door" or kind == "door_int":
			# door_int = a bedroom/bathroom doorway (see build_neighborhood.py's
			# register_opening_generic()) -- same placement math as an
			# exterior door, just a narrower, plainer InteriorDoor.tscn
			# instead of Door.tscn.
			var inst: Door = (interior_door_scene if kind == "door_int" else door_scene).instantiate()
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

## Same opening data (a building's manifest-shaped "openings" list, in
## that building's own local unrotated space -- see the flat setup()
## above and MapEditorUI.gd's _spawn_house_openings() for that local
## space's exact axis convention: x/hinge_x along width, y/hinge_y along
## depth with Blender's +y -> Godot's -z, z vertical), but parented
## under `building_root` -- a node the CALLER has already placed with
## its own correct world transform (e.g. via RingCoords.place_on_ring())
## -- and given a LOCAL transform, instead of the flat setup()'s
## global_position + a scalar world-Y rotation. Needed for anything on
## the station ring's curved floor: RingCoords' Basis isn't a pure
## Y-rotation ("up" itself varies with position), and critically, Door.gd
## animates its swing as a LOCAL rotation around its own Y axis -- that
## only swings a door correctly (on its actual vertical hinge) if local Y
## inherits the BUILDING's own up through the scene graph, which requires
## parenting under the placed building and setting a local transform, not
## baking the building's placement into each opening's global_transform
## directly (confirmed by reasoning through Door.gd's _base_rot_y /
## rotation:y tween -- baking global would swing doors around world-Y
## instead, wrong everywhere except exactly atop the ring's spin axis).
## Additive, not a replacement -- setup() above is untouched and still
## what Main.gd's flat neighborhood map uses.
static func setup_transformed(building_root: Node3D, openings: Array) -> Dictionary:
	var door_scene: PackedScene = load(DOOR_SCENE_PATH)
	var interior_door_scene: PackedScene = load(INTERIOR_DOOR_SCENE_PATH)
	var window_scene: PackedScene = load(WINDOW_SCENE_PATH)
	var doors := 0
	var windows := 0
	for o in openings:
		var kind: String = o.get("kind", "")
		var width: float = o["width"]
		var height: float = o["height"]
		var plane_rot: float = o["plane_rot"]
		var local_basis := Basis(Vector3.UP, plane_rot)
		if kind == "door" or kind == "door_int":
			var local_pos := Vector3(o["hinge_x"], o["z"], -o["hinge_y"])
			var inst: Door = (interior_door_scene if kind == "door_int" else door_scene).instantiate()
			building_root.add_child(inst)
			inst.transform = Transform3D(local_basis, local_pos)
			doors += 1
		elif kind == "window":
			var local_pos := Vector3(o["x"], o["z"] + height / 2.0, -o["y"])
			var inst2: Node3D = window_scene.instantiate()
			building_root.add_child(inst2)
			inst2.transform = Transform3D(local_basis, local_pos)
			inst2.scale = Vector3(width, height, 1.0)
			windows += 1
	return {"doors": doors, "windows": windows}
