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

## The equipped weapon's visual moves from the camera's WeaponMount into the right hand (PropR
## bone: the handle runs along +z through the fist, NpcProps' convention), so it shows in first
## person, third person and the shadow alike (research/player/03_action_animations.md 3).
## The transform seats each weapon's own model in the fist.
const WEAPON_GRIP := {
	"pistol": [Vector3(0, 0.02, 0.0), Vector3(-35.4, 180.0, 149.1), 0.5],   # barrel level along the aim (solved live against the hold pose's prop frame, 2026-10-16)
	"bat": [Vector3(0, 0, 0.05), Vector3(-67.2, -73.0, -0.4), 0.9],  # carried at the side, fat end down-forward (solved live against the carry pose, 2026-10-16)
	"fists": [Vector3.ZERO, Vector3.ZERO, 0.0],                      # the body HAS fists: no extra mesh
}
## The attack clip per weapon (npc_clips.json, group "action" -- NPCs share them).
const WEAPON_CLIP := {"fists": "punch", "bat": "bat_swing", "pistol": "pistol_fire"}

var npc: NpcCharacter
var animator: NpcAnimator
var _player: StationPlayer
var _task := -1
var _prepared: Dictionary = {}
var _pose_w := 0.0               # the movement pose's blend weight (eases in and out)
var _pose_mode := ""
var _hold_w := 0.0               # the weapon hold pose's blend weight
var _hand_mount: BoneAttachment3D
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
	## The attack: the shared action clip for this weapon (any NPC can play the same one).
	if animator:
		animator.play(WEAPON_CLIP.get(id, "punch"))


func reach(_at: Vector3) -> void:
	## Using something in the world (a door): the arm goes out to it and back.
	if animator and animator.clip_playing() == "":
		animator.play("door_reach")


func _hold_weapon() -> void:
	## Keep the equipped weapon's visual in the right hand.
	var w: Node3D = WeaponManager._current_weapon
	if w == null:
		return
	if _hand_mount == null:
		_hand_mount = BoneAttachment3D.new()
		_hand_mount.name = "HandRMount"
		npc.skeleton.add_child(_hand_mount)
		_hand_mount.bone_name = "PropR"
	if w.get_parent() != _hand_mount:
		if w.get_parent():
			w.get_parent().remove_child(w)
		_hand_mount.add_child(w)
		var g: Array = WEAPON_GRIP.get(WeaponManager.get_equipped_id(), WEAPON_GRIP.fists)
		w.position = g[0]
		w.rotation_degrees = g[1]
		w.scale = Vector3.ONE * maxf(float(g[2]), 0.001)
		w.visible = float(g[2]) > 0.0


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


func _weapon_hold(pitch: float) -> Dictionary:
	## The carry pose for the equipped weapon, following the aim pitch.  Only the needed channels,
	## so the walk keeps the other arm swinging.
	var want := WeaponManager.get_equipped_id() != "" and WeaponManager.get_equipped_id() != "fists" \
		and animator.clip_playing() == "" and not _player.is_seated()
	_hold_w = move_toward(_hold_w, 1.0 if want else 0.0, get_process_delta_time() / 0.2)
	if _hold_w <= 0.001:
		return {}
	match WeaponManager.get_equipped_id():
		"pistol":
			# half-raised ahead of the chest, the muzzle following the pitch (the arm mostly
			# extended, so the barrel -- along the forearm -- points where the eyes do)
			var J: Dictionary = npc.built.joints
			var sh: Vector3 = J.UpperArmR
			var hand := sh + Vector3(-0.01, -0.03 + 0.30 * sin(pitch), -0.34 * cos(pitch))
			return {"w": _hold_w, "grip": 0.85, "pole": Vector3(0.35, -0.85, 0.15), "handR": hand}
		"bat":
			# carried low at the side, a firm grip
			var J2: Dictionary = npc.built.joints
			var hip: Vector3 = J2.Hips
			return {"w": _hold_w, "grip": 0.9, "pole": Vector3(0.8, -0.3, 0.2),
				"handR": Vector3(hip.x + 0.24, hip.y - 0.12, hip.z - 0.05)}
	return {}
