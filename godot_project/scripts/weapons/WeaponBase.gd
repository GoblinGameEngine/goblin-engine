extends Node3D
class_name WeaponBase

# Base for every equippable weapon view-model. WeaponManager instances one
# of these under the player's WeaponMount on equip, calls setup(), and
# forwards "attack" input to try_use(). Subclasses override _perform().

var data: Dictionary = {}
var user: Node = null
var camera: Camera3D = null
var muzzle_ray: RayCast3D = null

var _cooldown_left := 0.0

func setup(weapon_data: Dictionary, weapon_user: Node, weapon_camera: Camera3D, weapon_muzzle_ray: RayCast3D) -> void:
	data = weapon_data
	user = weapon_user
	camera = weapon_camera
	muzzle_ray = weapon_muzzle_ray

func _process(delta: float) -> void:
	if _cooldown_left > 0.0:
		_cooldown_left -= delta

func can_use() -> bool:
	return _cooldown_left <= 0.0

func try_use() -> void:
	if not can_use():
		return
	_cooldown_left = float(data.get("cooldown", 0.5))
	_perform()

func _perform() -> void:
	pass  # override in subclasses

## Small punchy feedback shared by melee and ranged weapons: nudge the
## view-model back then spring it home.
func recoil(distance: float = 0.06, out_time: float = 0.03, back_time: float = 0.09) -> void:
	var tw := create_tween()
	var start_pos := position
	tw.tween_property(self, "position", start_pos + Vector3(0, 0, distance), out_time)
	tw.tween_property(self, "position", start_pos, back_time)
