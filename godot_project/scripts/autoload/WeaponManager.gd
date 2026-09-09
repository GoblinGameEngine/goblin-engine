extends Node

# Owns the player's weapon loadout and handles equip/unequip. The actual
# view-model + use-logic lives in scenes/weapons/*.tscn (WeaponBase
# subclasses); this just instances/frees them under the registered mount.

signal weapon_equipped(weapon_id: String)
signal loadout_changed()

const DATA_PATH := "res://data/weapons.json"

var definitions: Dictionary = {}      # weapon_id -> data dict (includes "scene")
var owned: Array[String] = []         # weapon ids the player currently has
var equipped_index: int = -1

var _mount: Node3D = null
var _user: Node = null
var _camera: Camera3D = null
var _muzzle_ray: RayCast3D = null
var _current_weapon: WeaponBase = null
var _hit_marker: MeshInstance3D = null

func _ready() -> void:
	var text := _read_file(DATA_PATH)
	if text.is_empty():
		push_error("WeaponManager: failed to read %s" % DATA_PATH)
		return
	var data = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		push_error("WeaponManager: malformed JSON in %s" % DATA_PATH)
		return
	for w in data.get("weapons", []):
		definitions[w.id] = w

func _read_file(path: String) -> String:
	if not FileAccess.file_exists(path):
		return ""
	var f := FileAccess.open(path, FileAccess.READ)
	var text := f.get_as_text()
	f.close()
	return text

## Called once by Player.gd on _ready() so the manager knows where to attach
## view-models and route raycasts/damage.
func register_player(user: Node, mount: Node3D, camera: Camera3D, muzzle_ray: RayCast3D) -> void:
	_user = user
	_mount = mount
	_camera = camera
	_muzzle_ray = muzzle_ray
	_build_hit_marker()

func add_weapon(weapon_id: String) -> bool:
	if not definitions.has(weapon_id) or owned.has(weapon_id):
		return false
	owned.append(weapon_id)
	loadout_changed.emit()
	if equipped_index == -1:
		equip(weapon_id)
	return true

func remove_weapon(weapon_id: String) -> bool:
	if not owned.has(weapon_id):
		return false
	var was_equipped := is_equipped(weapon_id)
	owned.erase(weapon_id)
	loadout_changed.emit()
	if was_equipped:
		if owned.is_empty():
			unequip()
		else:
			equip(owned[0])
	return true

func is_equipped(weapon_id: String) -> bool:
	return equipped_index >= 0 and equipped_index < owned.size() and owned[equipped_index] == weapon_id

func get_equipped_id() -> String:
	return owned[equipped_index] if equipped_index >= 0 and equipped_index < owned.size() else ""

func equip(weapon_id: String) -> bool:
	if not owned.has(weapon_id) or _mount == null:
		return false
	for child in _mount.get_children():
		child.queue_free()
	var def: Dictionary = definitions[weapon_id]
	var scene: PackedScene = load(def.scene)
	var instance: WeaponBase = scene.instantiate()
	_mount.add_child(instance)
	instance.setup(def, _user, _camera, _muzzle_ray)
	_current_weapon = instance
	equipped_index = owned.find(weapon_id)
	weapon_equipped.emit(weapon_id)
	return true

func unequip() -> void:
	if _mount:
		for child in _mount.get_children():
			child.queue_free()
	_current_weapon = null
	equipped_index = -1
	weapon_equipped.emit("")

func cycle(direction: int) -> void:
	if owned.is_empty():
		return
	var next := (equipped_index + direction + owned.size()) % owned.size()
	equip(owned[next])

func try_use_equipped() -> void:
	if _current_weapon:
		_current_weapon.try_use()

func _build_hit_marker() -> void:
	_hit_marker = MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.05
	sphere.height = 0.1
	_hit_marker.mesh = sphere
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = Color(1.0, 0.9, 0.3)
	_hit_marker.material_override = mat
	_hit_marker.visible = false
	get_tree().current_scene.add_child.call_deferred(_hit_marker)

func show_hit_marker(at: Vector3) -> void:
	if _hit_marker == null:
		return
	_hit_marker.global_position = at
	_hit_marker.visible = true
	get_tree().create_timer(0.12).timeout.connect(func():
		if is_instance_valid(_hit_marker):
			_hit_marker.visible = false
	)
