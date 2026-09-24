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


## Shared material library: the glbs carry no images, each surface's material is named by the hash
## of its definition (<building>.mats.json, written by gblib) and built here once for every building.
static var _mat_cache := {}
const TEX_ROOT := "res://remake/textures/"


func load_building(ps: PackedScene) -> void:
	var inst := ps.instantiate()
	add_child(inst)
	_apply_materials(inst, ps.resource_path.get_basename() + ".mats.json")
	var door_nodes: Array[Node3D] = []
	var light_nodes: Array[Node3D] = []
	var ladder_nodes: Array[Node3D] = []
	_collect(inst, door_nodes, light_nodes, ladder_nodes)
	for n in ladder_nodes:
		_make_ladder(n)
	for n in door_nodes:
		_make_door(n)
	for l in light_nodes:
		if l.name.begins_with("light_locked_"):
			continue            # a closed-up room (vacant store): no power
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


func _apply_materials(inst: Node, sidecar: String) -> void:
	if not FileAccess.file_exists(sidecar):
		return
	var defs: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(sidecar))
	var stack: Array[Node] = [inst]
	while stack.size() > 0:
		var n: Node = stack.pop_back()
		stack.append_array(n.get_children())
		var mi := n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(i)
			if m and defs.has(m.resource_name):
				mi.set_surface_override_material(i, library_material(m.resource_name, defs[m.resource_name]))


static func library_material(key: String, d: Dictionary) -> StandardMaterial3D:
	if _mat_cache.has(key):
		return _mat_cache[key]
	var m := StandardMaterial3D.new()
	m.resource_name = key
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	m.roughness = d.get("rough", 0.6)
	m.metallic = d.get("metal", 0.0)
	var tex = d.get("tex")
	if tex:
		var base: String = TEX_ROOT + tex
		m.albedo_texture = load(base + "_albedo.webp")
		var tint = d.get("tint")
		m.albedo_color = Color(tint[0], tint[1], tint[2]) if tint else Color.WHITE   # tints are stored sRGB
		if ResourceLoader.exists(base + "_rough.webp"):
			m.roughness_texture = load(base + "_rough.webp")
			m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
			m.roughness = 1.0
		if ResourceLoader.exists(base + "_normal.webp"):
			m.normal_enabled = true
			m.normal_texture = load(base + "_normal.webp")
	else:
		var c = d.get("color", [0.8, 0.8, 0.8])
		# Blender colours are linear; albedo_color is sRGB
		m.albedo_color = Color(c[0], c[1], c[2]).linear_to_srgb()
	var a = d.get("alpha")
	if a != null:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.albedo_color.a = a
	var e = d.get("emission")
	if e:
		m.emission_enabled = true
		m.emission = Color(e[0], e[1], e[2])
		m.emission_energy_multiplier = 2.0
	_mat_cache[key] = m
	return m
