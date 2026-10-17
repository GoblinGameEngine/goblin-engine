extends CharacterBody3D
class_name StationPlayer

# Space-station variant of Player.gd -- same FPS controller shape
# (WASD, mouse look, jump, weapons via WeaponManager) but with radial
# gravity instead of fixed world-down, since the floor here is the
# inside of a ring (see scripts/world/StationGeo.gd and
# scripts/world/StationRingBuilder.gd). Forked from Player.gd rather
# than adding a gravity-mode flag to it -- the gravity/up-direction
# change touches nearly every line of the physics step, so branching it
# inline would be more confusing than a dedicated copy. No step-up/curb
# logic here (Player.gd's _try_step_up) -- this map's floor has no
# curbs or stairs, just ~3.75-degree seams between straight segments,
# comfortably inside CharacterBody3D's default floor_max_angle.
#
# NOT a spinning station -- RingBody never moves (see the file-level
# comment in StationGeo.gd for why: rotating it, and simulating
# centrifugal force from that rotation, went through several rounds of
# hard-to-fix bugs before this settled on a stationary ring with an
# artificial radial gravity gradient, StationGeo.gravity_at(),
# instead). "Down" is still radial, toward the ring wall -- that part
# is pure geometry, unrelated to whether anything is spinning -- but
# nothing here is being carried by a moving platform any more.
#
# Physics: each physics frame, "down" is computed fresh as the radial
# direction from the station's central axis through the player (the
# floor is further out along that direction; the ceiling/axis is the
# other way). up_direction is set to match every frame, and the body's
# whole basis is turned by the shortest rotation from its own current up
# to that true up (Quaternion(basis.y, up) * basis) -- not reconstructed
# from a fixed forward vector via Basis.looking_at(). That keeps forward (and any yaw/pitch already
# applied via mouse look) correctly glued to the floor as you WALK
# along its curve, the same "align to a changing surface normal, keep
# facing" technique used for walking on curved/spherical ground
# elsewhere -- looking_at(old_forward, up) alone let forward and up
# drift apart frame to frame instead. Velocity is decomposed into an
# "along up" component (gravity/jump accumulate here, exactly like
# Player.gd's velocity.y) and a fresh per-frame tangential component
# from WASD input, instead of Player.gd's world-axis velocity.x/.z.

# LIVE TUNING: `static var`, not `const` -- read fresh every physics/
# input frame, so these can be changed from a running game with no
# restart, e.g. `python3 tools/gcmd.py run "StationPlayer.WALK_SPEED = 6.0"`.
# See the matching comment in StationGeo.gd for the geometry/gravity
# side of tuning (radius, ceiling height, etc.), which needs a
# rebuild_ring() call instead since those are baked into the built mesh.
static var WALK_SPEED := 4.2
static var SPRINT_SPEED := 7.5  # held (not toggled) via the "sprint" action -- left shift, project.godot's [input]
static var JUMP_VELOCITY := 4.5
static var MOUSE_SENSITIVITY := 0.0025
static var PITCH_LIMIT := deg_to_rad(85)

# Swimming: neutrally buoyant, no current/flow force -- see WaterVolume.gd
# and this file's _physics_process() swim branch. "jump"/"swim_down" (Ctrl,
# project.godot's [input]) give vertical control in place of land's
# gravity+jump; letting go decays toward hovering in place rather than
# sinking or drifting.
static var SWIM_SPEED := 3.2
static var SWIM_VERTICAL_SPEED := 2.6

@export var faction_id: String = "player"

var spawn_transform: Transform3D
var _station: Node3D

@onready var head: Node3D = $Head
@onready var camera: Camera3D = $Head/Camera3D
@onready var muzzle_ray: RayCast3D = $Head/Camera3D/MuzzleRay
@onready var weapon_mount: Node3D = $Head/Camera3D/WeaponMount
@onready var health: Health = $Health

var _skip_next_mouse_delta := true
# a controller's right stick: turn / look speeds at full deflection (radians a second), scaled by
# Settings.stick_look_mult; L3 sprint stays on until the stick comes back (Controls.gd)
const STICK_YAW_SPEED := 3.2
const STICK_PITCH_SPEED := 2.3
var _sprint_latched := false

# Which WaterVolume(s) the player is currently overlapping -- an Array,
# not a bool, so two overlapping volumes (e.g. a future river/lake
# junction) don't prematurely end swim state when only one is exited.
var _water_volumes: Array[Area3D] = []

# Vehicles (remake/scripts/vehicles/air_vehicle.gd). Seated: the vehicle
# places the body each tick, the mouse turns only the head, E stands up.
# Standing in a cabin: the vehicle sets carrier_velocity (its own motion at
# this point) every tick, added on top of walking, and sheltered (a cabin
# keeps a cloud's "water" out).
var carrier_velocity := Vector3.ZERO
var sheltered := false
# Gravity's share where we stand (SkyIslands: aboard a sky island the Aloft's lighter deck, ~0.89; 1 elsewhere)
var gravity_k := 1.0
var _vehicle: Node = null
var _last_carrier := Vector3.ZERO
const SEATED_YAW_LIMIT := 1.9

func sit_in(vehicle: Node) -> void:
	_vehicle = vehicle
	$CollisionShape3D.disabled = true
	weapon_mount.visible = false            # hands on the controls
	velocity = Vector3.ZERO
	carrier_velocity = Vector3.ZERO
	head.rotation.y = 0.0
	_clear_moves()

func stand_up(at: Vector3, basis_: Basis) -> void:
	## Off a seat: on our feet on whatever floor is under `at` (the ground, a deck, a cabin floor),
	## found with a ray -- our origin is at the eyes, the feet are _feet_depth() below it. (Callers
	## passed ground points, or guesses at the eye height; a ground point put the body underground.)
	_vehicle = null
	var up := StationGeo.up(StationGeo.s_of(at))
	var q := PhysicsRayQueryParameters3D.create(at + up * 0.6, at - up * 2.5, collision_mask)   # (from just above: not onto a cabin roof)
	q.exclude = [get_rid()]
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	var feet: Vector3 = hit.position if not hit.is_empty() else at
	if hit.is_empty():
		var s := StationGeo.s_of(at)
		var g := StationGeo.point(s, at.x, MapTerrain.elevation(s, at.x))
		if (at - g).dot(up) < 0.0:
			feet = g                                 # never under the ground
	global_transform = Transform3D(basis_, feet + up * (_feet_depth() + 0.03))
	$CollisionShape3D.disabled = false
	weapon_mount.visible = true
	head.rotation.y = 0.0
	velocity = Vector3.ZERO

func _feet_depth() -> float:
	## From our origin down to the bottom of the capsule.
	var cs := $CollisionShape3D as CollisionShape3D
	var h := 1.8
	if cs.shape is CapsuleShape3D:
		h = (cs.shape as CapsuleShape3D).height
	return -cs.position.y + h * 0.5

func is_seated() -> bool:
	return _vehicle != null

func is_swimming() -> bool:
	if sheltered or _vehicle != null:
		return false
	# in a volume that really holds this spot (a cloud only above its flat base: its spheres reach far
	# below what's drawn)
	for v in _water_volumes:
		if is_instance_valid(v) and (not v.has_method("holds") or v.holds(global_position)):
			return true
	return _in_map_water()


## The map's own water -- rivers, the lake, the seas (MapTerrain.water_at). None of it is a WaterVolume: those were
## only ever the clouds, so swimming never started in real water (the user, 2026-10-09: "The swimming mechanic never
## worked in the water"). In once it is over the chest; out again once it is down to the waist (wading ashore).
const SWIM_IN := 1.05                # m of water over the feet: swimming from here
const SWIM_OUT := 0.85               # and walking again below this
const FLOAT_EYE := 0.12              # m: afloat and still, the eyes this far above the surface
var _water_level := -9999.0          # the surface here last tick (-9999: none)
var _in_water := false


func _in_map_water() -> bool:
	var p := global_position
	var s := StationGeo.s_of(p)
	var wa := MapTerrain.water_at(s, p.x)
	_water_level = wa.x
	if wa.x < -9000.0:
		_in_water = false
		return false
	var depth := wa.x - (StationGeo.h_of(p) - _feet_depth())
	_in_water = depth > (SWIM_OUT if _in_water else SWIM_IN)
	return _in_water

## WaterVolume.gd's own contract -- called via has_method(), not a typed
## signal connection, so any body (not just this class) can opt in.
func enter_water(volume: Area3D) -> void:
	if not _water_volumes.has(volume):
		_water_volumes.append(volume)

func exit_water(volume: Area3D) -> void:
	_water_volumes.erase(volume)

func get_faction() -> String:
	return faction_id


func on_weapon_used(weapon_id: String) -> void:
	## WeaponManager fired/swung the equipped weapon: the body plays the matching action clip.
	var b := get_node_or_null("Body")
	if b and b.has_method("weapon_used"):
		b.weapon_used(weapon_id)

func recapture_mouse() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	_skip_next_mouse_delta = true

const FLOOR_MAX_DEG := 55.0
const FLOOR_SNAP := 0.5


func _ready() -> void:
	_station = get_tree().get_first_node_in_group("space_station")
	spawn_transform = global_transform
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	WeaponManager.register_player(self, weapon_mount, camera, muzzle_ray)

	WeaponManager.add_weapon("fists")
	WeaponManager.add_weapon("bat")
	WeaponManager.add_weapon("pistol")
	WeaponManager.equip("pistol")

	health.died.connect(_on_died)
	# the player's own body: a true first-person body, same person as the bicycle seats
	# (remake/characters/player_body.gd; research/player/00_plan.md)
	var body: Node3D = preload("res://remake/characters/player_body.gd").new()
	body.name = "Body"
	add_child(body)
	# hillsides: walkable up to FLOOR_MAX_DEG (the terrain's 2 m triangles vary round a hill's
	# average slope, and at the default 45 degrees the steeper ones read as wall -- the player
	# dropped off them every few frames and bobbed); held to the ground over crests and dips;
	# the same speed up a hill as down it
	floor_max_angle = deg_to_rad(FLOOR_MAX_DEG)
	floor_snap_length = FLOOR_SNAP
	floor_constant_speed = true

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		if _skip_next_mouse_delta:
			_skip_next_mouse_delta = false
		else:
			var sens := MOUSE_SENSITIVITY * Settings.mouse_sensitivity_mult
			# NOT rotate_y() -- confirmed live that Node3D.rotate_y() turns
			# around the PARENT's Y axis, not this node's own current local
			# Y (easy to miss in Player.gd, where those are always the same
			# axis since that body never reorients -- not true here, where
			# local "up" constantly changes to track the ring's curve).
			# Rotating around the wrong axis was corrupting yaw AND bleeding
			# into the "up" component WASD reads from transform.basis,
			# which is what made forward input read as a jump instead of a
			# walk. Rotating explicitly around the body's own current up
			# (already expressed in the same space as global_transform)
			# fixes both.
			if _vehicle:
				# seated: look round the cabin without turning the body in the seat
				head.rotation.y = clamp(head.rotation.y - event.relative.x * sens, -SEATED_YAW_LIMIT, SEATED_YAW_LIMIT)
				head.rotation.x = clamp(head.rotation.x - event.relative.y * sens, -PITCH_LIMIT, PITCH_LIMIT)
			else:
				global_transform.basis = global_transform.basis.rotated(global_transform.basis.y, -event.relative.x * sens)
				head.rotate_x(-event.relative.y * sens)
				head.rotation.x = clamp(head.rotation.x, -PITCH_LIMIT, PITCH_LIMIT)

	if event.is_action_pressed("shoot") and _vehicle == null:
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
		if _vehicle:
			_vehicle.leave_seat()
		else:
			_try_interact()

	if event.is_action_pressed("crouch") and _vehicle == null and not is_swimming():
		_crouch_pressed()

const INTERACT_RANGE := 3.5

func _try_interact() -> void:
	if DialogBox.is_open():
		return
	# along the aim: solid things, and the use-only zones (RemakeInteractZone: a vehicle's doorway,
	# its steering wheel); areas that aren't for using (water, cloud) are looked through
	var from := camera.global_position
	var to := from - camera.global_transform.basis.z * (INTERACT_RANGE + 0.5)
	var q := PhysicsRayQueryParameters3D.create(from, to, muzzle_ray.collision_mask | RemakeInteractZone.LAYER)
	q.collide_with_areas = true               # (not from inside: standing in a doorway, you use what you look at past it)
	# a doorway gives way to anything usable seen through it (the steering wheel, the far door)
	var ex: Array[RID] = [get_rid()]
	var fallback: Object = null
	for attempt in 8:
		q.exclude = ex
		var hit := get_world_3d().direct_space_state.intersect_ray(q)
		if hit.is_empty():
			break
		var target: Object = hit.collider
		if target is Area3D and not target.has_method("interact"):
			ex.append((target as Area3D).get_rid())
			continue
		if target == null or not target.has_method("interact") or from.distance_to(hit.position) > INTERACT_RANGE:
			break
		if target is RemakeInteractZone and (target as RemakeInteractZone).gives_way:
			if fallback == null:
				fallback = target
			ex.append((target as Area3D).get_rid())
			continue
		if target is RemakeDoor:
			var b := get_node_or_null("Body")
			if b and b.has_method("reach"):
				b.reach(hit.position)           # the hand goes out to the handle
		target.interact(self)
		return
	if fallback:
		fallback.interact(self)

## Radial vector from the station's central axis to the player, with
## the axis-direction component projected out (so this is purely the
## "how far out, which way" part). Returns Vector3.ZERO if we somehow
## have no station reference (e.g. running this scene standalone).
func _radial_vector() -> Vector3:
	if _station == null:
		return Vector3.ZERO
	var rel := global_position - _station.global_position
	var axis: Vector3 = StationGeo.AXIS
	return rel - axis * rel.dot(axis)

func _process(delta: float) -> void:
	# the eyes: transient offsets (step-up lift, landing dip) smoothed out, and the lean (Q/R)
	_eye_off = lerpf(_eye_off, 0.0, clampf(delta * 10.0, 0.0, 1.0))
	var lt := (1.0 if Input.is_action_pressed("lean_right") else 0.0) \
		- (1.0 if Input.is_action_pressed("lean_left") else 0.0)
	if _vehicle or not _hang.is_empty() or not _mantle.is_empty():
		lt = 0.0
	_lean = lerpf(_lean, lt, clampf(delta * 8.0, 0.0, 1.0))
	var off := _lean * LEAN_OFF
	if absf(off) > 0.01:
		# the peek shortens against walls: never put the camera inside one
		var q := PhysicsRayQueryParameters3D.create(global_position,
			global_position + global_transform.basis.x * (off + signf(off) * 0.12), collision_mask)
		q.exclude = [get_rid()]
		var hit := get_world_3d().direct_space_state.intersect_ray(q)
		if not hit.is_empty():
			off = signf(off) * maxf(0.0, global_position.distance_to(hit.position) - 0.12)
	head.position = Vector3(off, _eye_off, 0.0)
	head.rotation.z = -_lean * LEAN_ROLL

	# looking round with a controller's right stick (the mouse's equivalent is in _unhandled_input)
	var v := Controls.look_vector()
	if v == Vector2.ZERO:
		return
	var k := Settings.stick_look_mult * delta
	if _vehicle:
		head.rotation.y = clamp(head.rotation.y - v.x * STICK_YAW_SPEED * k, -SEATED_YAW_LIMIT, SEATED_YAW_LIMIT)
	else:
		global_transform.basis = global_transform.basis.rotated(global_transform.basis.y.normalized(), -v.x * STICK_YAW_SPEED * k)
	head.rotation.x = clamp(head.rotation.x - v.y * STICK_PITCH_SPEED * k, -PITCH_LIMIT, PITCH_LIMIT)


# -- modern movement: crouch, slide, step-up, mantle/vault, ledge hang, lean -----------------------
# (research/player/00_plan.md B and 02_movement_reference.md; the body poses that go with these are
# NpcAnimator.crouch and NpcRide.slide/hang/mantle, driven through body_state() -> PlayerBody.)
const STAND_H := 1.45                # the capsule, standing (scene: r 0.18)
const STAND_EYE := 1.43              # origin-at-the-eyes height over the feet
const CROUCH_H := 0.95
const CROUCH_EYE := 0.92
const STEP := 0.36                   # tallest step climbed without a ramp
static var CROUCH_SPEED := 2.1
static var SLIDE_BOOST := 1.2        # entry speed multiplier, capped at SLIDE_MAX
static var SLIDE_MAX := 9.0
static var SLIDE_DECEL := 4.0        # m/s^2 on the flat (slopes add/subtract real gravity)
static var SLIDE_END := 2.2
static var MANTLE_UP := 1.35         # highest ledge mantled from the ground (feet to ledge top)
static var MANTLE_UP_AIR := 1.0      # ... and mid-air
static var VAULT_UP := 0.55          # this low it's a vault: quick, speed kept
static var LEAN_OFF := 0.30          # m sideways at full lean
static var LEAN_ROLL := deg_to_rad(10.0)

var _crouch_k := 0.0                 # 0 standing .. 1 crouched (smoothed; the capsule follows)
var _crouch_toggle := false          # C (pad B) toggles: press to crouch, press again to stand
var _sliding := false
var _slide_dir := Vector3.ZERO
var _slide_speed := 0.0
var _slide_air := 0.0
var _hang := {}                      # {edge: Vector3, n: Vector3 (out of the wall), dir: Vector3 (edge axis)}
var _shimmy := 0.0
var _mantle := {}                    # {from: Vector3, to: Vector3, t: float, dur: float, edge: Vector3,
									 #  keep: Vector3 (velocity after), land_crouch: bool}
var _lean := 0.0                     # smoothed -1..1
var _eye_off := 0.0                  # transient eye smoothing (step-up lift, landing dip)
var _was_floor := true
var _probe_cap := CapsuleShape3D.new()


func eye_height() -> float:
	return lerpf(STAND_EYE, CROUCH_EYE, _crouch_k)


func body_state() -> Dictionary:
	## What the visible body needs this frame (PlayerBody reads it in _process).
	var up := global_transform.basis.y
	var vh := velocity - up * velocity.dot(up) - carrier_velocity
	var st := {"eye": eye_height(), "crouch": _crouch_k, "pitch": head.rotation.x,
		"speed": vh.length(), "mode": "",
		"air": 0.0 if is_on_floor() or is_swimming() or not _hang.is_empty() or not _mantle.is_empty() else 1.0,
		"vspeed": clampf(velocity.dot(up) / 5.0, -1.0, 1.0)}
	if not _mantle.is_empty():
		st.mode = "mantle"
		st.edge = _mantle.edge
		st.k = clampf(float(_mantle.t) / float(_mantle.dur), 0.0, 1.0)
	elif not _hang.is_empty():
		st.mode = "hang"
		st.edge = _hang.edge
		st.shimmy = _shimmy
	elif _sliding:
		st.mode = "slide"
	return st


func _set_capsule(k: float) -> void:
	var cs := $CollisionShape3D as CollisionShape3D
	var cap := cs.shape as CapsuleShape3D
	cap.height = lerpf(STAND_H, CROUCH_H, k)
	cs.position.y = -(lerpf(STAND_EYE, CROUCH_EYE, k) - cap.height * 0.5)


func _stand_blocked() -> bool:
	## Anything over us inside the standing capsule?  (Tried with the full-size capsule from the
	## standing origin; the current capsule is put back untouched.)
	var cs := $CollisionShape3D as CollisionShape3D
	var cap := cs.shape as CapsuleShape3D
	var old_h := cap.height
	var old_y := cs.position.y
	var up := global_transform.basis.y
	cap.height = STAND_H
	cs.position.y = -(STAND_EYE - STAND_H * 0.5)
	var hit := test_move(global_transform.translated(up * (STAND_EYE - eye_height())), up * 0.02)
	cap.height = old_h
	cs.position.y = old_y
	return hit


func _update_crouch(dt: float, up: Vector3, swimming: bool) -> void:
	var want := (_crouch_toggle or _sliding) and not swimming
	var target := 1.0 if want else 0.0
	if target < _crouch_k and _stand_blocked():
		target = _crouch_k                   # no headroom: stay down (re-checked every frame)
	if target == _crouch_k:
		return
	var k := move_toward(_crouch_k, target, dt / 0.22)
	var d_eye := lerpf(STAND_EYE, CROUCH_EYE, k) - lerpf(STAND_EYE, CROUCH_EYE, _crouch_k)
	_crouch_k = k
	_set_capsule(k)
	global_position += up * d_eye            # the feet stay planted; the eyes come down


func _crouch_pressed() -> void:
	## C (pad B) is a toggle: press to crouch, press again to stand (the user, 2026-10-16).
	## Sprinting on the ground it starts a slide instead; hanging, the drop handles it.
	if not _hang.is_empty():
		return
	var up := global_transform.basis.y
	var vh := velocity - up * velocity.dot(up) - carrier_velocity
	if is_on_floor() and not _sliding and vh.length() > 0.88 * SPRINT_SPEED:
		_sliding = true
		_slide_dir = vh.normalized()
		_slide_speed = minf(vh.length() * SLIDE_BOOST, SLIDE_MAX)
		_slide_air = 0.0
		_crouch_toggle = false
		return
	_crouch_toggle = not _crouch_toggle


func _slide_step(dt: float, up: Vector3) -> void:
	if not is_on_floor():
		_slide_air += dt
		if _slide_air > 0.3:
			_sliding = false
		return
	_slide_air = 0.0
	# steering: weak authority, like a real slide
	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var want := (transform.basis * Vector3(input_dir.x, 0, input_dir.y))
	want = want - up * want.dot(up)
	if want.length_squared() > 0.01:
		_slide_dir = _slide_dir.slerp(want.normalized(), clampf(dt * 1.5, 0.0, 0.2)).normalized()
	# the flat's friction, and the slope's true gravity along our line (downhill slides run on)
	var n := get_floor_normal()
	var g := StationGeo.gravity_at(_radial_vector().length()) * gravity_k
	var g_t := (-up * g) - n * n.dot(-up * g)
	_slide_speed = maxf(0.0, _slide_speed - SLIDE_DECEL * dt + g_t.dot(_slide_dir) * dt)
	if _slide_speed < SLIDE_END:
		_sliding = false              # run out: _update_crouch stands us up unless C toggled us down


# -- mantle / vault / ledge hang -------------------------------------------------------------------

func _fwd_flat(up: Vector3) -> Vector3:
	var f := -global_transform.basis.z
	return (f - up * f.dot(up)).normalized()


func _clearance(feet: Vector3, up: Vector3) -> int:
	## Room for the body stood at feet: 2 standing, 1 crouched, 0 none.
	var space := get_world_3d().direct_space_state
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = _probe_cap
	q.collision_mask = collision_mask
	q.exclude = [get_rid()]
	for probe in [[STAND_H, 2], [CROUCH_H, 1]]:
		_probe_cap.radius = 0.17
		_probe_cap.height = float(probe[0]) - 0.04
		q.transform = Transform3D(global_transform.basis, feet + up * (float(probe[0]) * 0.5 + 0.03))
		if space.intersect_shape(q, 1).is_empty():
			return probe[1]
	return 0


func _ledge_probe(up: Vector3, lo: float, hi: float, reach: float) -> Dictionary:
	## A grabbable edge ahead: a wall face between heights lo..hi over the feet (relative to the
	## eyes for hangs), its top a near-level surface.  {} or {edge, n, top, h}.
	var space := get_world_3d().direct_space_state
	var fwd := _fwd_flat(up)
	var feet := global_position - up * eye_height()
	var wall := {}
	for hh in [0.5 * (lo + hi), lo + 0.15, hi - 0.1]:
		var from := feet + up * clampf(hh, 0.1, hi)
		var q := PhysicsRayQueryParameters3D.create(from, from + fwd * reach, collision_mask)
		q.exclude = [get_rid()]
		wall = space.intersect_ray(q)
		if not wall.is_empty():
			break
	if wall.is_empty():
		return {}
	var n: Vector3 = wall.normal
	n = (n - up * n.dot(up))
	if n.length() < 0.5:
		return {}
	n = n.normalized()
	if fwd.dot(-n) < 0.45:
		return {}                                        # not facing the wall
	# the top: straight down from above, a hand's width past the lip
	var inside: Vector3 = (wall.position as Vector3) - n * 0.18
	var start := inside + up * ((feet + up * (hi + 0.5) - inside).dot(up))
	var q2 := PhysicsRayQueryParameters3D.create(start, start - up * (hi + 0.6 - lo), collision_mask)
	q2.exclude = [get_rid()]
	var top := space.intersect_ray(q2)
	if top.is_empty():
		return {}
	if (top.normal as Vector3).dot(up) < 0.75:
		return {}                                        # not a standable top
	var h := ((top.position as Vector3) - feet).dot(up)
	if h < lo or h > hi:
		return {}
	var edge: Vector3 = (top.position as Vector3) + n * 0.18   # back out to the lip
	return {"edge": edge, "n": n, "top": top.position, "h": h}


func _try_mantle(up: Vector3) -> bool:
	var hi := MANTLE_UP if is_on_floor() else MANTLE_UP_AIR
	var l := _ledge_probe(up, 0.3, hi, 0.85)
	if l.is_empty():
		return false
	var feet_to: Vector3 = (l.top as Vector3) - (l.n as Vector3) * 0.24 + up * 0.02
	var room := _clearance(feet_to, up)
	if room == 0:
		return false
	var vault: bool = float(l.h) <= VAULT_UP and is_on_floor()
	var vh := velocity - up * velocity.dot(up) - carrier_velocity
	_mantle = {"from": global_position, "t": 0.0, "dur": 0.45 if vault else 0.8,
		"edge": l.edge, "land_crouch": room == 1,
		"to": feet_to + up * (CROUCH_EYE if room == 1 else STAND_EYE),
		"keep": (vh if vault else vh.limit_length(1.0))}
	velocity = Vector3.ZERO
	($CollisionShape3D as CollisionShape3D).disabled = true
	return true


func _mantle_step(dt: float, up: Vector3) -> void:
	_mantle.t = float(_mantle.t) + dt
	var k := clampf(float(_mantle.t) / float(_mantle.dur), 0.0, 1.0)
	var d: Vector3 = (_mantle.to as Vector3) - (_mantle.from as Vector3)
	var d_up := up * d.dot(up)
	var d_h := d - d_up
	# weight up first, then over the lip (each eased)
	global_position = (_mantle.from as Vector3) + d_up * smoothstep(0.0, 0.7, k) + d_h * smoothstep(0.3, 1.0, k)
	if k >= 1.0:
		var land_crouch: bool = _mantle.land_crouch
		velocity = _mantle.keep
		_mantle = {}
		($CollisionShape3D as CollisionShape3D).disabled = false
		if land_crouch:
			_crouch_toggle = true
			_crouch_k = 1.0
			_set_capsule(1.0)


func _try_swim_mantle(up: Vector3) -> bool:
	## Jump while swimming beside something climbable -- a boat's gunwale, a dock, a river bank:
	## the gunwale haul (research/player/03_action_animations.md 4).  The edge may sit from chest
	## height below the eyes to half a metre above them; the pull is slower than a dry mantle.
	var eye := eye_height()
	var l := _ledge_probe(up, eye - 0.9, eye + 0.5, 0.9)
	if l.is_empty():
		return false
	var feet_to: Vector3 = (l.top as Vector3) - (l.n as Vector3) * 0.24 + up * 0.02
	var room := _clearance(feet_to, up)
	if room == 0:
		return false
	_mantle = {"from": global_position, "t": 0.0, "dur": 1.0, "edge": l.edge,
		"land_crouch": room == 1,
		"to": feet_to + up * (CROUCH_EYE if room == 1 else STAND_EYE), "keep": Vector3.ZERO}
	velocity = Vector3.ZERO
	($CollisionShape3D as CollisionShape3D).disabled = true
	return true


func _try_hang(up: Vector3) -> bool:
	## Falling past a ledge with hands free: catch it.  Hands are at the capsule's top (the eyes).
	if velocity.dot(up) > 0.5:
		return false
	var eye := eye_height()
	var l := _ledge_probe(up, eye - 0.12, eye + 0.38, 0.55)
	if l.is_empty():
		return false
	var edge: Vector3 = l.edge
	var n: Vector3 = l.n
	# room for the hanging body against the wall (hands at arm's reach to the lip)
	var org := edge + n * 0.28 - up * 0.30
	if _clearance(org - up * (eye - 0.02) + up * 0.02, up) == 0:
		return false
	_hang = {"edge": edge, "n": n, "dir": up.cross(n).normalized()}
	_shimmy = 0.0
	global_position = org
	# face the wall: forward (-z) into it, up kept
	global_transform.basis = Basis(up.cross(n).normalized(), up, n).orthonormalized()
	velocity = Vector3.ZERO
	return true


func _hang_step(dt: float, up: Vector3) -> void:
	velocity = Vector3.ZERO
	var edge: Vector3 = _hang.edge
	var n: Vector3 = _hang.n
	var dir: Vector3 = _hang.dir
	# drop: crouch or back away
	if Input.is_action_just_pressed("crouch") or Input.get_axis("move_forward", "move_back") > 0.5:
		_hang = {}
		velocity = n * 1.0
		return
	# climb: jump or forward
	if Input.is_action_just_pressed("jump") or Input.get_axis("move_back", "move_forward") > 0.5:
		var feet_to := edge - n * 0.24 + up * 0.02
		var room := _clearance(feet_to, up)
		if room > 0:
			_hang = {}
			_mantle = {"from": global_position, "t": 0.0, "dur": 0.9, "edge": edge,
				"land_crouch": room == 1,
				"to": feet_to + up * (CROUCH_EYE if room == 1 else STAND_EYE), "keep": Vector3.ZERO}
			($CollisionShape3D as CollisionShape3D).disabled = true
		return
	# shimmy along the edge while it carries on
	var side := Input.get_axis("move_left", "move_right")
	_shimmy = move_toward(_shimmy, side, dt * 6.0)
	if absf(side) > 0.2:
		var step := dir * side * 0.7 * dt
		var probe_from := global_position + step
		var save := global_position
		global_position = probe_from
		var l := _ledge_probe(up, eye_height() - 0.12, eye_height() + 0.38, 0.55)
		if l.is_empty() or absf(((l.edge as Vector3) - edge).dot(up)) > 0.15:
			global_position = save                      # the edge ends (or jumps): stay
		else:
			_hang.edge = (l.edge as Vector3)
			_hang.n = l.n
			_hang.dir = up.cross(l.n as Vector3).normalized()


func _step_up(dt: float, up: Vector3) -> void:
	## Climb a single step: the horizontal move is blocked, the same move from STEP higher is clear
	## -> lift onto it (floor snap settles the feet; the eyes smooth the lift out via _eye_off).
	var h := (velocity - up * velocity.dot(up)) * dt
	if h.length() < 0.0005 or not is_on_floor():
		return
	var t := global_transform
	if not test_move(t, h):
		return
	var lift := up * STEP
	if test_move(t, lift):
		return
	var raised := t.translated(lift)
	if test_move(raised, h):
		return
	var col := KinematicCollision3D.new()
	var moved := raised.translated(h)
	if test_move(moved, -lift, col):
		var dy := STEP - col.get_travel().length()
		global_position += up * dy
		_eye_off -= dy                                   # the camera glides up, not jumps


func _physics_process(delta: float) -> void:
	if _vehicle:
		return                      # the vehicle places us on the seat
	var radial := _radial_vector()
	var radial_len := radial.length()
	var degenerate := radial_len < 0.001
	if degenerate:
		# Degenerate (on/near the axis) -- fall back to ordinary world-down
		# rather than dividing by ~zero; shouldn't happen once spawned on
		# the floor, but keeps this from producing NaNs if it ever does.
		radial = Vector3.DOWN
		radial_len = 1.0
	var radial_dir := radial / radial_len
	var up := -radial_dir
	up_direction = up

	# Stand along the true up every tick: turn the body from wherever its own up now points, not by
	# the change since last tick -- that way nothing can leave it tilted (the old incremental turn
	# skipped changes below Vector3's epsilon yet still recorded them as done, so a slow drift --
	# floating in a cloud -- piled up an unrecoverable lean).
	var body_up := global_transform.basis.y.normalized()
	if body_up.angle_to(up) > 1e-6:
		global_transform.basis = Basis(Quaternion(body_up, up)) * global_transform.basis
	global_transform.basis = global_transform.basis.orthonormalized()

	# parkour states own the body: the mantle curve carries it, the hang pins it
	if not _mantle.is_empty():
		_mantle_step(delta, up)
		return
	if not _hang.is_empty():
		_hang_step(delta, up)
		return

	var up_speed := (velocity - _last_carrier).dot(up)
	var swimming := is_swimming()
	_update_crouch(delta, up, swimming)
	if swimming:
		# Neutrally buoyant -- no gravity pull, and explicitly no current/
		# flow force applied here or anywhere in WaterVolume.gd ("I don't
		# want the water to flow, just make it so the play character can
		# swim in it"). Vertical control replaces jump/gravity: hold jump
		# to rise, swim_down to sink, let go to coast toward a hover
		# instead of falling.
		# in the map's water a body floats: let go, it comes up till the head is out, and it can't swim up out of the
		# surface (a cloud's water has no surface to float at: there, letting go hovers)
		var eye_over := StationGeo.h_of(global_position) - _water_level if _in_water else NAN
		if Input.is_action_just_pressed("jump") and _try_swim_mantle(up):
			return                   # out of the water onto a gunwale, a dock, a bank
		if Input.is_action_pressed("jump"):
			up_speed = move_toward(up_speed, SWIM_VERTICAL_SPEED, SWIM_VERTICAL_SPEED * 6.0 * delta)
		elif Input.is_action_pressed("swim_down"):
			up_speed = move_toward(up_speed, -SWIM_VERTICAL_SPEED, SWIM_VERTICAL_SPEED * 6.0 * delta)
		elif _in_water:
			up_speed = move_toward(up_speed, clampf((FLOAT_EYE - eye_over) * 2.0, -1.0, 1.2), SWIM_VERTICAL_SPEED * 3.0 * delta)
		else:
			up_speed = move_toward(up_speed, 0.0, SWIM_VERTICAL_SPEED * 3.0 * delta)
		if _in_water and eye_over > FLOAT_EYE + 0.25 and not is_on_floor():
			up_speed = minf(up_speed, -0.5)        # (out of the water's top: back down onto it)
	else:
		if not is_on_floor():
			# Stepped radial gradient (0G at the axis, TARGET_G at the wall)
			# instead of a flat pull or omega^2*radial_len -- see
			# StationGeo.gravity_at(). Using radial_len here (not just
			# whatever gravity_at() was for the floor you took off from)
			# means a jump/fall that drifts toward the axis genuinely gets
			# lighter as it goes, same as it would get lighter walking
			# inward through the bands on foot.
			up_speed -= StationGeo.gravity_at(radial_len) * gravity_k * delta
		else:
			up_speed = minf(up_speed, 0.0)       # grounded: no speed left over from the slope to carry off a crest

		if Input.is_action_just_pressed("jump"):
			# a ledge ahead takes the jump as a mantle/vault (grounded or in the air)
			if _try_mantle(up):
				return
			if is_on_floor():
				if _sliding:
					_sliding = false             # slide hop
					up_speed = JUMP_VELOCITY * 0.85
				else:
					up_speed = JUMP_VELOCITY
		elif not is_on_floor() and up_speed < 0.5 \
				and (Input.is_action_pressed("jump") or Input.is_action_pressed("move_forward")):
			# falling past a ledge with jump or forward held: catch it
			if _try_hang(up):
				return

	if _sliding:
		_slide_step(delta, up)
	if _sliding:
		velocity = up * up_speed + _slide_dir * _slide_speed + carrier_velocity
		platform_floor_layers = 0 if carrier_velocity != Vector3.ZERO else 0xFFFFFFFF
		_last_carrier = carrier_velocity
		var fell := -up_speed
		move_and_slide()
		_land_dip(fell)
		return

	var input_dir := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var move_dir := (transform.basis * Vector3(input_dir.x, 0, input_dir.y))
	if move_dir.length_squared() > 0.0001:
		# full speed on the keys; a stick walks as far over as it's pushed
		move_dir = move_dir.normalized() * minf(input_dir.length(), 1.0)

	# sprint: held (Shift), or clicked in on a stick (L3) until the player stops
	if Controls.using_pad and Input.is_action_just_pressed("sprint"):
		_sprint_latched = not _sprint_latched
	if input_dir.length() < 0.2:
		_sprint_latched = false
	var sprinting := _sprint_latched or (Input.is_action_pressed("sprint") and not Controls.using_pad)
	var speed := SWIM_SPEED if swimming else (SPRINT_SPEED if sprinting else WALK_SPEED)
	if not swimming:
		speed = lerpf(speed, CROUCH_SPEED, _crouch_k)     # crouched we go carefully
	velocity = up * up_speed + move_dir * speed + carrier_velocity
	# a cabin carries us itself (carrier_velocity); the engine's own platform velocity would double it
	platform_floor_layers = 0 if carrier_velocity != Vector3.ZERO else 0xFFFFFFFF
	_last_carrier = carrier_velocity
	if not swimming:
		_step_up(delta, up)
	var fell := -up_speed
	move_and_slide()
	_land_dip(fell)


func _land_dip(fall_speed: float) -> void:
	## A hard landing dips the eyes a touch (smoothed back out in _process) and bends the body's
	## knees (the shared landing animation, NpcAnimator.land).
	var grounded := is_on_floor()
	if grounded and not _was_floor:
		if fall_speed > 5.0:
			_eye_off -= clampf((fall_speed - 5.0) * 0.02, 0.0, 0.12)
		if fall_speed > 2.0:
			var b := get_node_or_null("Body")
			if b and b.has_method("landed"):
				b.landed(fall_speed)
	_was_floor = grounded

func _on_died(_attacker: Node) -> void:
	print("StationPlayer died -- respawning.")
	respawn()


func respawn() -> void:
	## Back to where you started (the Communicator's System > Respawn, or a death), out of any vehicle, healed.
	if _vehicle:
		_vehicle.leave_seat()
	carrier_velocity = Vector3.ZERO
	sheltered = false
	global_transform = spawn_transform
	velocity = Vector3.ZERO
	_water_volumes.clear()  # a mid-swim death would otherwise respawn the player still "swimming" on dry land
	_in_water = false
	_clear_moves()
	health.heal(health.max_health)


func _clear_moves() -> void:
	## Out of every movement state (a seat, a respawn): standing, nothing held.
	_sliding = false
	_hang = {}
	if not _mantle.is_empty():
		_mantle = {}
		($CollisionShape3D as CollisionShape3D).disabled = _vehicle != null
	_crouch_toggle = false
	_crouch_k = 0.0
	_set_capsule(0.0)
	_lean = 0.0
	_eye_off = 0.0
	head.position = Vector3.ZERO
	head.rotation.z = 0.0
