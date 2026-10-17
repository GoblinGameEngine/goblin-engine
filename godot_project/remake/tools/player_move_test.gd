extends SceneTree

## Headless selftest for the player's body and modern movement (research/player/00_plan.md D):
## builds a test site on the ring at s=0 (floor, step, crouch tunnel, vault box, mantle wall, hang
## pillar), spawns the real StationPlayer scene, drives it with synthesized input events, and
## asserts each mechanic: the split head, walk, sprint, step-up, crouch (and blocked stand-up),
## slide, vault, mantle, ledge hang + climb, lean.
##   ../godot/godot4 --headless --path . --script res://remake/tools/player_move_test.gd
## Exit code 1 on any failure.

const FLOOR_Y := 10000.0          # s = 0: the floor at radius R, up = (0,-1,0), forward (+s) = +z
var fails: Array[String] = []
var player: CharacterBody3D


func _ok(name: String, cond: bool, detail := "") -> void:
	if cond:
		print("PASS  %s" % name)
	else:
		print("FAIL  %s  %s" % [name, detail])
		fails.append(name)


func _box(parent: Node, center: Vector3, size: Vector3) -> void:
	var b := StaticBody3D.new()
	b.collision_layer = 1
	var cs := CollisionShape3D.new()
	var sh := BoxShape3D.new()
	sh.size = size
	cs.shape = sh
	b.add_child(cs)
	parent.add_child(b)
	b.global_position = center


func _press(action: String) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	Input.parse_input_event(e)


func _release(action: String) -> void:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = false
	Input.parse_input_event(e)


func _release_all() -> void:
	for a in ["move_forward", "move_back", "move_left", "move_right", "jump", "sprint", "crouch",
			"lean_left", "lean_right"]:
		_release(a)


func feet_h() -> float:
	## Feet height over the floor (up is -y here).
	return FLOOR_Y - (player.global_position.y + player.eye_height())


func _spawn(x: float, z: float) -> void:
	player.global_transform = Transform3D(StationGeo.basis(0.0), Vector3(x, FLOOR_Y - 1.43, z))
	player.velocity = Vector3.ZERO
	player._clear_moves()


func _wait(frames: int) -> void:
	for i in frames:
		await physics_frame


func _init() -> void:
	_boot()


func _boot() -> void:
	await process_frame            # autoloads (WeaponManager, Settings...) come up after _init
	var site := Node3D.new()
	root.add_child(site)
	var station := Node3D.new()
	station.add_to_group("space_station")
	site.add_child(station)
	var ring := Node3D.new()
	ring.name = "RingBody"         # the HUD's compass looks for it
	station.add_child(ring)
	# the floor, and each lane's obstacle (up here is -y: "0.3 above the floor" = y 9999.7)
	_box(site, Vector3(10, FLOOR_Y + 0.5, 10), Vector3(60, 1, 64))
	_box(site, Vector3(5, FLOOR_Y - 0.15, 4), Vector3(4, 0.3, 2))                 # B: a 0.3 step
	_box(site, Vector3(10, FLOOR_Y - 1.6, 5), Vector3(4, 1.0, 4))                 # C: tunnel roof, clear height 1.1
	_box(site, Vector3(15, FLOOR_Y - 0.25, 4.5), Vector3(4, 0.5, 1.5))            # D: a 0.5 vault box
	_box(site, Vector3(20, FLOOR_Y - 0.6, 5), Vector3(4, 1.2, 2))                 # E: a 1.2 mantle wall
	_box(site, Vector3(25, FLOOR_Y - 1.1, 5), Vector3(4, 2.2, 2))                 # F: a 2.2 hang pillar
	_box(site, Vector3(50, FLOOR_Y - 0.25, 2.8), Vector3(4, 1.5, 3))              # G: a boat deck in open water (top 1.0 over the swimmer's feet)
	var ps: PackedScene = load("res://scenes/StationPlayer.tscn")
	player = ps.instantiate()
	site.add_child(player)
	player.sheltered = true                 # no MapTerrain water checks on the test site
	player.process_mode = Node.PROCESS_MODE_ALWAYS
	_run()


func _run() -> void:
	await physics_frame
	await physics_frame

	# -- the split head (M1): a split build loses no geometry, and the head meshes sit on HEAD_LAYER
	var seed := 1
	var v: Dictionary = NpcTraits.shared().person(seed, "player", ["L0", "L1"], "", {"age": 30})
	var plain: Dictionary = NpcCharacter.prepare(v, "player", seed, "work")
	var split: Dictionary = NpcCharacter.prepare(v, "player", seed, "work", true)
	var n_plain: int = (plain.body[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
	var n_body: int = (split.body[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
	var n_head: int = (split.head[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
	var n_collar: int = (split.collar[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
	# the split torso trades its neck cap for the dark collar plug, so the sum differs a little
	_ok("split: no geometry lost", n_head > 100 and n_collar > 10
		and absf(float(n_body + n_head - n_plain)) < 80,
		"plain %d vs body %d + head %d (+collar %d)" % [n_plain, n_body, n_head, n_collar])
	var me := NpcCharacter.from_prepared(split)
	root.add_child(me)
	_ok("split: layers", me.head_mesh.layers == NpcCharacter.HEAD_LAYER
		and me.headwear_mesh.layers == NpcCharacter.HEAD_LAYER
		and me.body_mesh.layers != NpcCharacter.HEAD_LAYER, "head %d wear %d" % [me.head_mesh.layers, me.headwear_mesh.layers])
	_ok("split: face material shared", me.head_mesh.mesh.surface_get_material(0) == me.body_mesh.mesh.surface_get_material(0))
	me.queue_free()

	# -- the player's own body node arrives (built on a worker) with the camera culling the head
	_spawn(0, -4)
	var body: Node3D = player.get_node("Body")
	for i in 300:
		if body.npc != null:
			break
		await physics_frame
	_ok("body: built", body.npc != null)
	_ok("body: camera culls HEAD_LAYER", (player.camera.cull_mask & NpcCharacter.HEAD_LAYER) == 0)
	if body.npc:
		_ok("body: scaled to the eyes", absf(body.npc.scale.x * (float((body.npc.built.joints.Head as Vector3).y) + 0.10) - 1.43) < 0.03,
			"scale %.3f" % body.npc.scale.x)

	# -- walk + sprint (lane A)
	_spawn(0, -4)
	_press("move_forward")
	await _wait(90)
	var walked := player.global_position.z - (-4.0)
	_ok("walk: moves", walked > 4.0 and walked < 8.0, "%.1f m in 1.5 s" % walked)
	_press("sprint")
	var z0 := player.global_position.z
	await _wait(60)
	var ran := player.global_position.z - z0
	_ok("sprint: faster", ran > 6.0, "%.1f m in 1 s" % ran)
	_release_all()

	# -- step-up (lane B): over the 0.3 step without jumping
	_spawn(5, 1)
	_press("move_forward")
	var topped := false
	for i in 120:
		await physics_frame
		if feet_h() > 0.25 and player.is_on_floor():
			topped = true
			break
	_ok("step-up: climbs 0.3", topped, "feet %.2f z %.1f" % [feet_h(), player.global_position.z])
	_release_all()

	# -- crouch (lane C): toggle, go under the 1.1 tunnel, blocked stand-up inside, stand after
	_spawn(10, 1)
	_press("crouch")
	_release("crouch")        # a tap: toggle on
	await _wait(30)
	var cap := (player.get_node("CollisionShape3D") as CollisionShape3D).shape as CapsuleShape3D
	_ok("crouch: capsule", absf(cap.height - 0.95) < 0.02, "h %.2f" % cap.height)
	_press("move_forward")
	var under := false
	for i in 240:
		await physics_frame
		if player.global_position.z > 4.4 and player.global_position.z < 5.6:
			under = true
			_press("crouch")   # try to stand under the roof
			_release("crouch")
			break
	await _wait(25)
	_ok("crouch: reaches the tunnel", under, "z %.1f" % player.global_position.z)
	_ok("crouch: stand blocked under the roof", cap.height < 1.1, "h %.2f" % cap.height)
	for i in 240:
		await physics_frame
		if player.global_position.z > 7.5:
			break
	await _wait(40)
	_ok("crouch: stands when clear", absf(cap.height - 1.45) < 0.02, "h %.2f z %.1f" % [cap.height, player.global_position.z])
	_release_all()

	# -- slide (lane A): sprint, then crouch
	_spawn(0, -6)
	_press("move_forward")
	_press("sprint")
	await _wait(75)
	_press("crouch")
	await _wait(5)
	_ok("slide: starts", player._sliding, "speed in %.1f" % player.velocity.length())
	var vmax := 0.0
	var slid := 0
	for i in 300:
		await physics_frame
		vmax = maxf(vmax, player.velocity.length())
		if not player._sliding:
			slid = i
			break
	_release("crouch")
	_ok("slide: boosts then ends", vmax > 7.8 and slid > 20, "vmax %.1f ended at %d" % [vmax, slid])
	_release_all()

	# -- vault (lane D): sprint at the 0.5 box, jump
	_spawn(15, 1)
	_press("move_forward")
	await _wait(40)
	_press("jump")
	await _wait(3)
	_release("jump")
	var on_box := false
	for i in 90:
		await physics_frame
		if feet_h() > 0.45 and player.is_on_floor():
			on_box = true
			break
	_ok("vault: onto 0.5", on_box, "feet %.2f z %.1f" % [feet_h(), player.global_position.z])
	_release_all()

	# -- mantle (lane E): the 1.2 wall
	_spawn(20, 2)
	_press("move_forward")
	await _wait(30)
	_press("jump")
	await _wait(3)
	_release("jump")
	var on_wall := false
	for i in 150:
		await physics_frame
		if feet_h() > 1.15 and player.is_on_floor():
			on_wall = true
			break
	_ok("mantle: onto 1.2", on_wall, "feet %.2f z %.1f" % [feet_h(), player.global_position.z])
	_release_all()

	# -- ledge hang + climb (lane F): the 2.2 pillar is past mantle reach; jumping at it, falling
	# with jump held, the hands catch the edge; holding forward then climbs it
	_spawn(25, 2.2)
	_press("move_forward")
	await _wait(20)
	_press("jump")
	var hung := false
	var up_top := false
	for i in 420:
		await physics_frame
		if not player._hang.is_empty():
			hung = true
		if feet_h() > 2.1 and player.is_on_floor():
			up_top = true
			break
	_ok("hang: catches the edge", hung)
	_ok("hang: climbs to the top (2.2)", up_top, "feet %.2f" % feet_h())
	_release_all()

	# -- hang drop: catch again (forward let go before the catch, so no auto-climb), crouch drops
	_spawn(25, 2.2)
	_press("move_forward")
	await _wait(20)
	_press("jump")
	await _wait(4)
	_release("move_forward")       # drift on; only jump stays held for the grab
	for i in 90:
		await physics_frame
		if not player._hang.is_empty():
			break
	_release_all()
	if not player._hang.is_empty():
		await _wait(10)
		_press("crouch")
		await _wait(3)
		_release("crouch")
		await _wait(50)
		_ok("hang: crouch drops", player._hang.is_empty() and feet_h() < 1.0, "feet %.2f" % feet_h())
	else:
		_ok("hang: crouch drops", false, "never caught")
	player._clear_moves()
	_release_all()

	# -- the action clips exist (shared with every NPC; npc_clip_test checks their bones)
	var have := true
	for c in ["punch", "bat_swing", "pistol_fire", "door_reach"]:
		have = have and float(NpcClips.clip(c).get("length", 0.0)) > 0.0
	_ok("clips: punch/bat/fire/door authored", have)

	# -- the jump animation drives the body (air rises past the tuck threshold, lands with a pulse)
	_spawn(0, -4)
	var an = player.get_node("Body").animator
	_press("jump")
	await _wait(3)
	_release("jump")
	var air_max := 0.0
	var land_seen := false
	for i in 120:
		await physics_frame
		air_max = maxf(air_max, an.air)
		if an._land_t >= 0.0:
			land_seen = true
			break
	_ok("jump: airborne pose + landing pulse", air_max > 0.7 and land_seen, "air %.2f land %s" % [air_max, land_seen])

	# -- water-to-boat: swimming beside a gunwale, jump hauls out onto the deck
	_spawn(50, 0.55)
	player.sheltered = false
	var water := Area3D.new()
	root.add_child(water)
	player.enter_water(water)
	await _wait(20)
	_ok("swim: swimming in the test water", player.is_swimming())
	_press("jump")
	await _wait(3)
	_release("jump")
	var on_deck := false
	for i in 180:
		await physics_frame
		# (the mock water has no bounds, so the swim flag stays on over the deck: feet height alone)
		if feet_h() > 0.9 and player._mantle.is_empty():
			on_deck = true
			break
	_ok("swim: climbs onto the boat deck", on_deck, "feet %.2f z %.1f" % [feet_h(), player.global_position.z])
	player.exit_water(water)
	player.sheltered = true
	_release_all()

	# -- lean (lane A, in the open)
	_spawn(0, -4)
	_press("lean_right")
	await _wait(50)
	var hx: float = (player.get_node("Head") as Node3D).position.x
	_release("lean_right")
	await _wait(50)
	var hx2: float = (player.get_node("Head") as Node3D).position.x
	_ok("lean: offsets and returns", hx > 0.2 and absf(hx2) < 0.05, "%.2f -> %.2f" % [hx, hx2])

	print("")
	if fails.is_empty():
		print("ALL PASS")
		quit(0)
	else:
		print("%d FAILURES: %s" % [fails.size(), ", ".join(fails)])
		quit(1)
