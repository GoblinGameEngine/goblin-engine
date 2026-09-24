extends Node3D
class_name RemakeBuilding

## Instances one remake building .glb and wires up what the Blender side encoded in node
## names (see remake/blender/gblib.py header):
##   door_*    -> hinged RemakeDoor bodies with box collision that swings with the leaf
##   light_*   -> OmniLight3D
## "-col"/"-colonly" collision is handled by Godot's own glTF import hints.

@export var scene: PackedScene
@export var light_energy := 1.2

var doors: Array[RemakeDoor] = []


func _ready() -> void:
	if scene:
		load_building(scene)


func load_building(ps: PackedScene) -> void:
	var inst := ps.instantiate()
	add_child(inst)
	var door_nodes: Array[Node3D] = []
	var light_nodes: Array[Node3D] = []
	var ladder_nodes: Array[Node3D] = []
	_collect(inst, door_nodes, light_nodes, ladder_nodes)
	for n in ladder_nodes:
		_make_ladder(n)
	for n in door_nodes:
		_make_door(n)
	for l in light_nodes:
		var lamp := OmniLight3D.new()
		lamp.omni_range = 7.0
		lamp.light_energy = light_energy
		lamp.light_color = Color(1.0, 0.9, 0.75)
		lamp.shadow_enabled = false
		l.add_child(lamp)
	# pair up the leaves of double doors (same id before the _L/_R suffix)
	var by_id := {}
	for d in doors:
		var base := d.door_id.trim_suffix("_L").trim_suffix("_R")
		by_id[base] = by_id.get(base, []) + [d]
	for base in by_id:
		var leaves: Array = by_id[base]
		for d in leaves:
			for other in leaves:
				if other != d:
					d.partners.append(other)


func _collect(n: Node, door_nodes: Array[Node3D], light_nodes: Array[Node3D], ladder_nodes: Array[Node3D]) -> void:
	for c in n.get_children():
		if c is Node3D and String(c.name).begins_with("door_"):
			door_nodes.append(c)
			continue
		if c is Node3D and String(c.name).begins_with("light_"):
			light_nodes.append(c)
		if c is MeshInstance3D and String(c.name).begins_with("ladder_"):
			ladder_nodes.append(c)
		_collect(c, door_nodes, light_nodes, ladder_nodes)


## ladder_* meshes become climb zones: an Area3D slightly larger than the ladder that tells
## any body with set_ladder() when it is on it (the player then climbs instead of falling).
func _make_ladder(n: Node3D) -> void:
	var mi := n as MeshInstance3D
	var aabb := mi.get_aabb()
	var area := Area3D.new()
	area.name = "LadderZone"
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = aabb.size + Vector3(0.7, 0.4, 0.7)
	cs.shape = box
	cs.position = aabb.get_center()
	area.add_child(cs)
	area.add_to_group("ladder")
	n.add_child(area)
	area.body_entered.connect(func(b): if b.has_method("set_ladder"): b.set_ladder(1, cs))
	area.body_exited.connect(func(b): if b.has_method("set_ladder"): b.set_ladder(-1, cs))


func _make_door(n: Node3D) -> void:
	var parts := String(n.name).split("__")
	var id := parts[0].trim_prefix("door_")
	var sign := -1.0 if parts.size() > 1 and parts[1] == "n" else 1.0
	var is_locked := parts.has("locked")
	var body := RemakeDoor.new()
	body.name = "DoorBody_" + id
	# transform must be set before entering the tree and physics sync left off: with
	# sync_to_physics on, the body snaps back to wherever the physics server first saw it
	body.sync_to_physics = false
	body.transform = n.transform
	var parent := n.get_parent()
	parent.add_child(body)
	parent.remove_child(n)
	body.add_child(n)
	n.transform = Transform3D.IDENTITY
	# collision box = the leaf mesh's local AABB
	var mi := n as MeshInstance3D
	if mi == null:
		for c in n.get_children():
			if c is MeshInstance3D:
				mi = c
				break
	if mi:
		var aabb := mi.get_aabb()
		var cs := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = aabb.size
		cs.shape = box
		cs.position = aabb.get_center()
		body.add_child(cs)
	body.setup(id, sign, is_locked)
	doors.append(body)
