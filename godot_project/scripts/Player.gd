extends CharacterBody3D

# Firewatch-speed FPS/RPG controller: WASD move, mouse look, jump, and
# weapon use forwarded to WeaponManager (see scripts/autoload/WeaponManager.gd)
# so weapons can be swapped without touching this script.

const WALK_SPEED := 4.2
const JUMP_VELOCITY := 4.5
const MOUSE_SENSITIVITY := 0.0025
const PITCH_LIMIT := deg_to_rad(85)
# CharacterBody3D doesn't climb any vertical ledge on its own, no matter how
# small -- curbs (0.12m) and driveway/sidewalk seams read as full walls
# without this. 0.3m comfortably clears those with margin while staying
# well under a stair riser, so normal walking still feels normal.
const STEP_HEIGHT := 0.3

@export var faction_id: String = "player"

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")
var spawn_transform: Transform3D

@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var muzzle_ray: RayCast3D = $Head/Camera3D/MuzzleRay
@onready var weapon_mount: Node3D = $Head/Camera3D/WeaponMount
@onready var health: Health = $Health

var _skip_next_mouse_delta := true

func get_faction() -> String:
	return faction_id

## Called by GameMenu/DialogBox when they hand control back to gameplay.
## Re-capturing the mouse after it's been visible causes the same
## OS-warp-generates-a-huge-synthetic-delta issue as the very first capture
## on launch, so route it through here rather than setting
## Input.mouse_mode directly.
func recapture_mouse() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	_skip_next_mouse_delta = true

func _ready() -> void:
	spawn_transform = global_transform
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	WeaponManager.register_player(self, weapon_mount, camera, muzzle_ray)

	# Starting loadout for framework testing -- fists always on you, plus
	# whatever else the player has found/been given.
	WeaponManager.add_weapon("fists")
	WeaponManager.add_weapon("bat")
	WeaponManager.add_weapon("pistol")
	WeaponManager.equip("pistol")

	health.died.connect(_on_died)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		# The very first motion event after the OS warps the cursor into the
		# window on capture reports a huge synthetic relative delta -- skip
		# it once so the camera doesn't snap on launch/focus.
		if _skip_next_mouse_delta:
			_skip_next_mouse_delta = false
		else:
			var sens := MOUSE_SENSITIVITY * Settings.mouse_sensitivity_mult
			rotate_y(-event.relative.x * sens)
			head.rotate_x(-event.relative.y * sens)
			head.rotation.x = clamp(head.rotation.x, -PITCH_LIMIT, PITCH_LIMIT)

	# The map editor reuses left-click (place) and mouse wheel (rotate)
	# for its own purposes while active -- without this guard, opening
	# the editor and clicking to place an asset would ALSO fire whatever
	# weapon is equipped / cycle weapons underneath it.
	if MapEditorUI.active:
		return

	if event.is_action_pressed("shoot"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			WeaponManager.try_use_equipped()
		else:
			recapture_mouse()

	if event.is_action_pressed("next_weapon"):
		WeaponManager.cycle(1)
	if event.is_action_pressed("prev_weapon"):
		WeaponManager.cycle(-1)
	for i in range(1, 4):
		if event.is_action_pressed("weapon_slot_%d" % i) and i - 1 < WeaponManager.owned.size():
			WeaponManager.equip(WeaponManager.owned[i - 1])

	if event.is_action_pressed("interact"):
		_try_interact()

const INTERACT_RANGE := 3.5

## Single button (E) for everything: talk, loot corpses, pick up items,
## open doors, flip switches. Any object in the world becomes usable by E
## just by implementing `interact(by: Node) -> void` -- NPCBase's
## implementation (talk/loot) below is the template future Pickup/Door/
## Switch scenes should follow.
func _try_interact() -> void:
	if DialogBox.is_open():
		return
	muzzle_ray.force_raycast_update()
	if not muzzle_ray.is_colliding():
		return
	var target := muzzle_ray.get_collider()
	if target == null or not target.has_method("interact"):
		return
	if target is Node3D and global_position.distance_to(target.global_position) > INTERACT_RANGE:
		return
	target.interact(self)

## Curbs/small ledges block CharacterBody3D outright unless something nudges
## the player up onto them -- this probes for "blocked at foot height, clear
## at step height" and, if found, snaps up to the exact top-of-step height
## (not a flat +STEP_HEIGHT pop) so it reads as stepping over a curb rather
## than hopping a fixed amount for every tiny seam.
func _try_step_up(move_dir: Vector3) -> void:
	if move_dir.length_squared() < 0.0001 or not is_on_floor():
		return
	var space_state := get_world_3d().direct_space_state
	var probe := move_dir.normalized() * 0.4
	var origin := global_position

	var foot_from := origin + Vector3(0, 0.1, 0)
	var foot_query := PhysicsRayQueryParameters3D.create(foot_from, foot_from + probe)
	foot_query.exclude = [self]
	if not space_state.intersect_ray(foot_query):
		return  # nothing in the way -- no step needed

	var head_from := origin + Vector3(0, STEP_HEIGHT + 0.02, 0)
	var head_query := PhysicsRayQueryParameters3D.create(head_from, head_from + probe)
	head_query.exclude = [self]
	if space_state.intersect_ray(head_query):
		return  # still blocked above step height -- a real wall, not a curb

	var down_from := origin + probe + Vector3(0, STEP_HEIGHT + 0.05, 0)
	var down_query := PhysicsRayQueryParameters3D.create(down_from, down_from + Vector3(0, -(STEP_HEIGHT + 0.15), 0))
	down_query.exclude = [self]
	var hit := space_state.intersect_ray(down_query)
	if hit:
		var new_y: float = hit.position.y + 0.02
		if new_y > global_position.y:
			global_position.y = new_y

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= gravity * delta

	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = JUMP_VELOCITY

	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var move_dir := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	velocity.x = move_dir.x * WALK_SPEED
	velocity.z = move_dir.z * WALK_SPEED

	_try_step_up(move_dir)
	move_and_slide()

func _on_died(_attacker: Node) -> void:
	# No fail state defined yet -- just patch up and reset position so
	# framework testing (and future NPC combat) isn't a dead end.
	print("Player died -- respawning.")
	global_transform = spawn_transform
	velocity = Vector3.ZERO
	health.heal(health.max_health)
