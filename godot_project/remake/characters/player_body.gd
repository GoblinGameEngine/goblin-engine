extends Node3D
class_name PlayerBody

## The player's own body: a true first-person body (research/player/01_first_person_body.md).
## The SAME generated person the bicycle seats (NpcTraits.person(seed, "player", ...)), built with
## split_head -- the head, neck, hair and hat live on NpcCharacter.HEAD_LAYER, which the player's
## camera culls while every light still shadow-maps it: looking down you see your chest, arms and
## legs; your shadow (and any other camera) shows a whole person; you never see the inside of your
## own head.
##
## The controller (StationPlayer) stays authoritative: this node is glued under the capsule (feet
## at the capsule's bottom, yaw = the body's yaw) and NpcAnimator poses it -- the walk from the
## capsule's speed, the camera pitch curled down the spine, the crouch factor, and the slide, hang
## and mantle poses (NpcRide.slide/hang/mantle -- the same set every NPC human can use).

const EYE_STAND := 1.43          # the capsule's eye height (StationPlayer: origin at the eyes)

## The equipped weapon is held by the body: NpcWeaponPose keys the weapon in the camera's frame
## (the boxer's guard, the bat over the shoulder, the two-handed pistol) and both hands reach it by
## arm IK with their facing set, so it shows in first person, third person and the shadow alike
## (research/player/04_weapon_holds.md).  The attack animates the same pose.
var npc: NpcCharacter
var animator: NpcAnimator
var _player: StationPlayer
var _task := -1
var _prepared: Dictionary = {}
var _pose_w := 0.0               # the movement pose's blend weight (eases in and out)
var _pose_mode := ""
var _hold_w := 0.0               # the weapon hold pose's blend weight
var _atk_t := -1.0               # time into the current attack (-1: none)
var _atk_id := ""
var _punch_side := 1             # the fist that punches next (+1 right, -1 left)
var _fight_until := 0
var _sway := Vector3.ZERO        # the weapon lagging the look a touch
var _last_basis := Basis.IDENTITY
var _lock := Mutex.new()


func _ready() -> void:
	_player = get_parent() as StationPlayer
	if _player:
		_player.camera.cull_mask &= ~NpcCharacter.HEAD_LAYER
		_player.camera.near = 0.03
	# the same person as RemakeBicycle.take_seat builds, so the bike, the mirror and the shadow agree
	var seed := 1
	if DataFile.exists(NpcLife.PATH):
		seed = NpcLife.shared().seed
	var v := NpcTraits.shared().person(seed, "player", ["L0", "L1"], "", {"age": 30})
	_task = WorkerThreadPool.add_task(func() -> void:
		var d := NpcCharacter.prepare(v, "player", seed, "work", true)
		_lock.lock()
		_prepared = d
		_lock.unlock())


func _assemble_if_ready() -> void:
	if npc or _task < 0 or not WorkerThreadPool.is_task_completed(_task):
		return
	WorkerThreadPool.wait_for_task_completion(_task)
	_task = -1
	_lock.lock()
	var d := _prepared
	_prepared = {}
	_lock.unlock()
	npc = NpcCharacter.from_prepared(d)
	npc.name = "Me"
	add_child(npc)
	animator = NpcAnimator.attach(npc)
	animator.process_priority = process_priority + 1   # pose after this sets the hold, same frame
	animator.ambient = false                 # no watch-checking from inside your own body
	# the generated person's eyes to the capsule's: one uniform scale, so the hands, the stride and
	# the shadow all match the collision the player actually has
	var J: Dictionary = npc.built.joints
	var eye_y := float((J.Head as Vector3).y) + 0.10
	if eye_y > 0.5:
		npc.scale = Vector3.ONE * (EYE_STAND / eye_y)


func _process(_dt: float) -> void:
	_assemble_if_ready()
	if npc == null or _player == null:
		return
	if _player.is_seated():
		visible = false                      # the vehicle seats its own rider body
		return
	visible = true
	var st := _player.body_state()
	# glue: feet at the capsule's bottom (the controller's origin is at the eyes and comes down as
	# the crouch does), plus the look-down pull-back that keeps the chest behind the near plane
	var pitch := float(st.pitch)
	var back := 0.30 * smoothstep(-0.45, -1.3, pitch)
	position = Vector3(0, -float(st.eye), 0.02 + back)
	rotation = Vector3.ZERO
	animator.speed = float(st.speed)
	animator.aim_pitch = pitch
	animator.crouch = float(st.crouch)
	animator.air = move_toward(animator.air, float(st.get("air", 0.0)), get_process_delta_time() / 0.12)
	animator.air_v = float(st.get("vspeed", 0.0))
	_hold_weapon()
	_apply_pose(st)


func landed(fall_speed: float) -> void:
	## Touchdown (StationPlayer calls it): the knees take the landing, scaled by the fall.
	if animator:
		animator.land(clampf((fall_speed - 3.0) / 7.0, 0.15, 1.0))


func weapon_used(id: String) -> void:
	## The attack: NpcWeaponPose animates the hold (any NPC can play the same one).
	_atk_id = id
	_atk_t = 0.0
	if id == "fists":
		_punch_side = -_punch_side


func reach(_at: Vector3) -> void:
	## Using something in the world (a door): the arm goes out to it and back.
	if animator and animator.clip_playing() == "":
		animator.play("door_reach")


func _hold_weapon() -> void:
	## The equipped weapon's visual is the body's: out of the camera's mount, placed by the hold pose.
	var w: Node3D = WeaponManager._current_weapon
	if w == null or not is_instance_valid(w):
		return
	if w.get_parent() != self:
		if w.get_parent():
			w.get_parent().remove_child(w)
		add_child(w)
		w.set("held_by_body", true)


func _apply_pose(st: Dictionary) -> void:
	## The slide / hang / mantle poses as NpcAnimator.ride overrides, blended in and out; with no
	## movement pose, the weapon hold pose (right hand raised with the pistol, the bat carried),
	## which a playing action clip suppresses so attacks read fully.
	var mode := str(st.get("mode", ""))
	var target_w := 1.0 if mode != "" else 0.0
	if mode != _pose_mode and mode != "":
		_pose_mode = mode
	_pose_w = move_toward(_pose_w, target_w, get_process_delta_time() / 0.16)
	if _pose_w <= 0.001:
		_pose_mode = ""
		animator.ride = _weapon_hold(float(st.pitch))
		return
	var edge_local := Vector3.ZERO
	if st.has("edge"):
		edge_local = npc.to_local(st.edge as Vector3)
	match _pose_mode:
		"slide":
			animator.ride = NpcRide.slide(npc, _pose_w)
		"hang":
			animator.ride = NpcRide.hang(npc, edge_local, float(st.get("shimmy", 0.0)), _pose_w)
		"mantle":
			animator.ride = NpcRide.mantle(npc, edge_local, float(st.get("k", 0.0)), _pose_w)
		_:
			animator.ride = {}


func _weapon_hold(_pitch: float) -> Dictionary:
	## The hold (and attack) pose for the equipped weapon, from NpcWeaponPose in the camera's frame.
	## Fists come up as a guard only while fighting (a few seconds after a punch); otherwise the
	## arms are the walk's.
	var dt := get_process_delta_time()
	var id := WeaponManager.get_equipped_id()
	if has_meta("freeze"):                     # a fixed attack moment, for screenshots (DevBridge)
		_atk_t = float(get_meta("freeze"))
	elif _atk_t >= 0.0:
		_atk_t += dt
		if _atk_id != id or _atk_t > float(NpcWeaponPose.LEN.get(_atk_id, 0.5)):
			_atk_t = -1.0
	var guard := id == "fists" and (_atk_t >= 0.0 or _fight_until > Time.get_ticks_msec())
	if _atk_t >= 0.0 and id == "fists":
		_fight_until = Time.get_ticks_msec() + 4000
	var want := id != "" and (id != "fists" or guard) and not _player.is_seated()
	_hold_w = move_toward(_hold_w, 1.0 if want else 0.0, dt / 0.18)
	var w: Node3D = WeaponManager._current_weapon
	if w and is_instance_valid(w) and w.get_parent() == self:
		w.visible = id != "fists" and _hold_w > 0.5
	if _hold_w <= 0.001 or id == "":
		return {}
	var cam: Camera3D = _player.camera
	# sway: the weapon trails a fast turn a little and springs back
	var turn := (_last_basis.inverse() * cam.global_transform.basis).get_euler()
	_last_basis = cam.global_transform.basis
	_sway = _sway.lerp(Vector3(clampf(turn.y, -0.05, 0.05) * 0.25, clampf(-turn.x, -0.05, 0.05) * 0.25, 0), 0.25)
	_sway = _sway.lerp(Vector3.ZERO, minf(1.0, dt * 8.0))
	var aim_to_skel := npc.skeleton.global_transform.affine_inverse() * cam.global_transform
	var p: Dictionary = NpcWeaponPose.pose(id, _atk_t if _atk_id == id else -1.0, _punch_side, aim_to_skel, _sway)
	if w and is_instance_valid(w) and w.get_parent() == self:
		w.global_transform = cam.global_transform * (p.weapon as Transform3D)
	var r: Dictionary = p.ride
	r.w = _hold_w
	return r
