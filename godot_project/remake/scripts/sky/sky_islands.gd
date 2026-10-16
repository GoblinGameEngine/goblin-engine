extends Node3D
class_name SkyIslands

## The hundred sky islands of the Skein (research/sky_islands/; canon remake/bible/sky_islands.json, layouts
## remake/sky/islands.json).  SkyDrift moves them -- with the wind, up and down, docking into rafts of up to ten for
## three days -- and this places them, every physics tick (before the player moves: process_physics_priority), and
## draws what belongs to them all:
##   * the balloons: two MultiMeshes over every island (the full envelope near, a lighter one far), 100 m x 1 km each,
##     BALLOON_BASE m over the deck;
##   * the line rockets and the lines they tow between docking islands (SkyDrift.lines), sagging;
##   * each island's tier (SkyIsland: far / mid / near) by distance;
##   * the bridges: down when an edge is lashed, up when it's cast off;
##   * snow: an island in a cloud gathers it (SNOW_IN), and loses it very slowly after (SNOW_MELT by day);
##     falling flakes round the camera whenever it's in a cloud aloft;
##   * carrying the player: standing aboard, StationPlayer.carrier_velocity is the deck's motion there and its
##     gravity is the Aloft's (ABOARD_G of the floor's: 0.925 g at 750 m, lighter still riding west -- the canon).
## Containers lowered to the floor are left there for the ground crews (drop_cargo), cleared after a while.

const BALLOON_BASE := 60.0            # m over the deck (the plan)
const SNOW_IN := 1.0 / 420.0          # per s at a cloud's heart: a cloud's passing (2-4 min) whitens the roofs ...
const SNOW_MELT := 1.0 / 7200.0       # ... per s in daylight: it takes two hours of sun to clear (none at night)
const ABOARD_G := 0.89
const LINE_RANGE := 9000.0
const CARGO_LIFE := 600.0

var player: StationPlayer
var clouds: RemakeClouds
var sky: DaySkySystem
var drift: SkyDrift
var islands: Array[SkyIsland] = []
var layouts: Array = []
var ready_ := false
var _task := -1
var banners: SkyBanners              # every island's banners, dock flags and pennants (three MultiMeshes in all)
var _mm_near: MultiMeshInstance3D
var _mm_far: MultiMeshInstance3D
var _lines: MeshInstance3D
var _rockets: MultiMeshInstance3D
var _tier_t := 0.0
var _snow_t := 0.0
var _aboard := -1
var _flakes: GPUParticles3D
var _cargo: Array = []               # [node, seconds left]
var _cloud_i := 0
var _plumb_t := 90.0
var _flights: Array = []            # larks out on a descent: {lark, island, pad (local Transform3D), state, t}
const PLUMB_EVERY := Vector2(240.0, 600.0)   # s between descents seen near the player
const PLUMB_STAY := 60.0                     # s on the floor (the trading)
var _snow_last := PackedFloat64Array()


func setup(p_player: StationPlayer, p_clouds: RemakeClouds, p_sky: DaySkySystem) -> void:
	player = p_player
	clouds = p_clouds
	sky = p_sky
	process_physics_priority = -10
	var lay: Dictionary = JSON.parse_string(DataFile.text("res://remake/sky/islands.json"))
	var can: Dictionary = JSON.parse_string(DataFile.text("res://remake/bible/sky_islands.json"))
	var by_id := {}
	for c in can.islands:
		by_id[c.id] = c
	layouts = lay.islands
	models = lay.get("models", {})
	var defs := []
	for L in layouts:
		defs.append({"id": L.id, "faces": L.faces, "bridges": L.bridges})
	drift = SkyDrift.new()
	drift.setup(defs)
	# a day and a half of sky before the player sees it (rafts formed, some under way): on a worker
	_task = WorkerThreadPool.add_task(drift.warm_up.bind(36.0, 30.0), false, "sky islands warm-up")
	for i in layouts.size():
		var isl := SkyIsland.new()
		isl.setup(self, i, layouts[i], by_id.get(layouts[i].id, {}))
		isl.visible = false
		add_child(isl)
		islands.append(isl)
	_make_balloons()
	banners = SkyBanners.new()
	add_child(banners)
	banners.setup(self)
	_balloon_looks(by_id)
	_lines = MeshInstance3D.new()
	_lines.name = "Lines"
	_lines.mesh = ImmediateMesh.new()
	_lines.material_override = SkyIsland._mat("sky_tether", Color(0.2, 0.18, 0.15))
	_lines.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_lines)
	_rockets = _mm("Rockets", SkyIsland.part_mesh("rocket"))
	_make_flakes()
	var tg := Time.get_ticks_msec()
	SkySigns.warm_glyphs()                          # (the signs' letters, once, while loading)
	print("SkyIslands: sign glyphs %d ms" % (Time.get_ticks_msec() - tg))
	RemakeAirVehicle.frame_source = frame_at
	var folk := SkyFolk.new()
	folk.name = "SkyFolk"
	folk.sys = self
	add_child(folk)


func _mm(n: String, mesh: Mesh) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.mesh = mesh
	var mmi := MultiMeshInstance3D.new()
	mmi.name = n
	mmi.multimesh = mm
	mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mmi)
	return mmi


func _make_balloons() -> void:
	_mm_near = _mm("BalloonsNear", SkyIsland.part_mesh("balloon"))
	_mm_far = _mm("BalloonsFar", SkyIsland.part_mesh("balloon_far"))
	# (the envelopes are a kilometre tall: never culled for being off-centre, always drawn)
	for m in [_mm_near, _mm_far]:
		(m as MultiMeshInstance3D).multimesh.use_custom_data = true     # (the clan's colour and its ad: sky_balloon)
		(m as MultiMeshInstance3D).custom_aabb = AABB(Vector3.ONE * -StationGeo.R * 1.2, Vector3.ONE * StationGeo.R * 2.4)


func is_ready() -> bool:
	return ready_


# ------------------------------------------------------------------ every tick
func _physics_process(delta: float) -> void:
	if not ready_:
		if _task >= 0 and WorkerThreadPool.is_task_completed(_task):
			WorkerThreadPool.wait_for_task_completion(_task)
			_task = -1
			ready_ = true
			for i in islands.size():
				islands[i].visible = true
			print("SkyIslands: %d islands aloft (%s)" % [islands.size(), drift.summary()])
			var t0 := Time.get_ticks_msec()
			SkyIsland.lark_bake(self)                 # (the parked larks' impostor, once, while still loading: ~0.8 s)
			print("SkyIslands: lark impostor baked in %d ms" % (Time.get_ticks_msec() - t0))
		return
	Prof.begin("sky.step")
	_sim_step(delta)
	Prof.end("sky.step")
	Prof.begin("sky.place")
	_place_islands(delta)
	Prof.end("sky.place")
	_events()
	Prof.begin("sky.travel")
	_travel_step(delta)
	Prof.end("sky.travel")
	Prof.begin("sky.carry")
	_carry(delta)
	Prof.end("sky.carry")


# Where SkyDrift's frame for an island jumps (lashed into a raft's shared frame, cast off back onto its own), the
# island doesn't: the jump goes into its correction (_corr: its actual = SkyDrift's * _corr), which then eases out at
# CORR_MOVE / CORR_TURN -- slowly enough to stand on.  _prev: last tick's actual transforms (what moved the deck under a
# point: the player's carry, an aircraft's frame).
const CORR_MOVE := 0.4               # m/s
const CORR_TURN := 0.004             # rad/s
var _corr: Array[Transform3D] = []
var _prev: Array[Transform3D] = []
var _target_prev: Array[Transform3D] = []
var _last: Array[Transform3D] = []      # each island's transform as last set (its node's, without asking the node)
var _dt := 1.0 / 60.0


# The drift is stepped at SIM_HZ (its rafts and meetings change slowly), and each island's transform is interpolated
# between its last two sim states every tick -- smooth to stand on, and the sim (~0.5 ms a step) runs a sixth as often.
# Far islands (tier 0: a few hundred triangles 3.6 km off) are placed every FAR_EVERY ticks, staggered; mid ones
# (tier 1: the LOD1 model, hundreds of metres off) every MID_EVERY.
const SIM_HZ := 10.0
const FAR_EVERY := 6
const MID_EVERY := 2
var _sim_acc := 0.0
var _sim_a: Array[Transform3D] = []     # each island's sim transform a step ago ...
var _sim_b: Array[Transform3D] = []     # ... and now
var _tick := 0
var _moved_dt := PackedFloat32Array()   # seconds since each island was last placed


func _sim_step(delta: float) -> void:
	var n := islands.size()
	if _sim_b.size() != n:
		_sim_a.resize(n)
		_sim_b.resize(n)
		for i in n:
			_sim_b[i] = drift.transform(i)
			_sim_a[i] = _sim_b[i]
	_sim_acc += delta
	var h := 1.0 / SIM_HZ
	while _sim_acc >= h:
		_sim_acc -= h
		drift.step(h)
		for i in n:
			_sim_a[i] = _sim_b[i]
			_sim_b[i] = drift.transform(i)


func _sim_transform(i: int) -> Transform3D:
	var f := clampf(_sim_acc * SIM_HZ, 0.0, 1.0)
	var a := _sim_a[i]
	var b := _sim_b[i]
	if a.origin.distance_to(b.origin) > 40.0:
		return b                                   # (a jump in the frame: the correction below takes it up)
	return Transform3D(Basis(a.basis.get_rotation_quaternion().slerp(b.basis.get_rotation_quaternion(), f)), a.origin.lerp(b.origin, f))


func _place_islands(delta: float) -> void:
	_dt = maxf(delta, 1e-4)
	_tick += 1
	var n := islands.size()
	if _corr.size() != n:
		_corr.resize(n)
		_corr.fill(Transform3D.IDENTITY)
		_prev.resize(n)
		_target_prev.resize(n)
		_last.resize(n)
		_moved_dt.resize(n)
		_moved_dt.fill(delta)
		for i in n:
			_target_prev[i] = _sim_transform(i)
			_prev[i] = _target_prev[i]
			_last[i] = islands[i].global_transform if islands[i].is_inside_tree() else _target_prev[i]
	for i in n:
		_moved_dt[i] += delta
		var every := FAR_EVERY if islands[i].tier <= 0 else (MID_EVERY if islands[i].tier == 1 else 1)
		if every > 1 and i != _aboard and (_tick + i) % every != 0:
			continue                                  # (far: placed every few ticks)
		var dtm: float = _moved_dt[i]
		_moved_dt[i] = 0.0
		_place_one(i, dtm)


func _place_one(i: int, delta: float) -> void:
	var jump := 18.0 * delta + 0.25                  # m: more than any drift or winch moves it in a tick
	if true:
		var t := _sim_transform(i)
		var tp := _target_prev[i]
		# (a turn of more than ~0.002 rad moves the basis' columns by about that: compared without quaternions)
		if t.origin.distance_squared_to(tp.origin) > jump * jump or (t.basis.x - tp.basis.x).length_squared() \
				+ (t.basis.z - tp.basis.z).length_squared() > 8e-6:
			# the frame jumped: keep the island where it was (its actual transform last tick), and ease from there
			_corr[i] = t.affine_inverse() * _last[i]
		_target_prev[i] = t
		var c := _corr[i]
		if c != Transform3D.IDENTITY:
			var q := c.basis.get_rotation_quaternion()
			var ang := q.get_angle()
			if ang > 1e-6:
				q = q.slerp(Quaternion.IDENTITY, minf(1.0, CORR_TURN * delta / ang))
			var o := c.origin.move_toward(Vector3.ZERO, CORR_MOVE * delta)
			c = Transform3D(Basis(q), o)
			if o.length() < 1e-4 and q.get_angle() < 1e-6:
				c = Transform3D.IDENTITY
			_corr[i] = c
		var actual := t * c
		_prev[i] = _last[i]
		_last[i] = actual
		islands[i].global_transform = actual
		islands[i].moved()


func deck_velocity(i: int, p: Vector3) -> Vector3:
	## m/s the island's deck (and everything on it: buildings, bridges) moved at the point p over the last tick --
	## its drift, climb, the raft frame's turn and any easing correction, all at once
	var lp := _prev[i].affine_inverse() * p
	return (islands[i].global_transform * lp - p) / _dt     # (near islands are placed every tick: _dt is theirs)


func _events() -> void:
	## an edge lashed: its two bridges come down; cast off: they go up
	for ev in drift.events:
		if ev[0] == "lash" or ev[0] == "cast_off":
			var e: Dictionary = ev[1]
			var down: bool = ev[0] == "lash"
			islands[e.a].set_bridge(e.side, e.along_a, down, islands[e.b].bridge_style())
			islands[e.b].set_bridge(SkyDrift._opp(e.side), e.along_b, down, islands[e.a].bridge_style())
	drift.events.clear()


const CARRY_MARGIN := 16.0             # m past a deck's faces still aboard: the bridges (13 m) and their noses


func _carry(_delta: float) -> void:
	## the player aboard -- on the deck, a roof, or out on a bridge: carried by the island (its actual motion where
	## they stand), and lighter
	if player == null or player.is_seated():
		if _aboard >= 0 and player:
			player.gravity_k = 1.0
		_aboard = -1
		return
	var p := player.global_position
	var on := -1
	for i in islands.size():
		var isl := islands[i]
		if isl.tier < 2:
			continue
		var lp := isl.global_transform.affine_inverse() * p
		if isl.inside(lp, CARRY_MARGIN) and lp.y > -4.0 and lp.y < 120.0:
			on = i
			break
	if on >= 0:
		player.carrier_velocity = deck_velocity(on, p)
		player.gravity_k = ABOARD_G
	elif _aboard >= 0:
		player.carrier_velocity = Vector3.ZERO
		player.gravity_k = 1.0
	if (on >= 0) != (_aboard >= 0):
		_sun_soft(on >= 0)
	_aboard = on


## Aboard, the camera always moves (the island drifts ~5 m/s): the sun's shadow cascades re-snap to their texels every
## frame or two and every shadow edge on the island crawls -- a flicker (frame diffs: 0.06 % of the pixels changing a
## frame with shadows, 0.001 % without, 0.001 % with the shadow blurred).  So aboard the sun's shadows are softened.
const SUN_BLUR_ABOARD := 2.5
var _sun: DirectionalLight3D
var _sun_blur := 1.0


func _sun_soft(on: bool) -> void:
	if _sun == null or not is_instance_valid(_sun):
		var ls := get_tree().current_scene.find_children("*", "DirectionalLight3D", true, false)
		if ls.is_empty():
			return
		_sun = ls[0]
		_sun_blur = _sun.shadow_blur
	_sun.shadow_blur = SUN_BLUR_ABOARD if on else _sun_blur


const FRAME_OVER := 500.0             # m over a deck a flier takes on the island's motion (RemakeAirVehicle)
const FRAME_MARGIN := 30.0            # m round the deck's edges


func frame_at(p: Vector3) -> Vector3:
	## the moving air over an island (to land on it, an aircraft flies relative to this): the island's velocity
	## anywhere over its deck up to FRAME_OVER m above it, else Vector3.INF
	if not ready_ or StationGeo.h_of(p) < SkyDrift.DECK_H - SkyDrift.H_SWING - 20.0:
		return Vector3.INF                    # (down by the floor: nowhere near an island -- most callers, at once)
	for i in islands.size():
		var isl := islands[i]
		if isl.global_position.distance_squared_to(p) > 640000.0:          # (800 m)
			continue
		var lp := isl.global_transform.affine_inverse() * p
		var f: Dictionary = layouts[i].faces
		if lp.y > -10.0 and lp.y < FRAME_OVER and lp.x > float(f.N) - FRAME_MARGIN and lp.x < float(f.S) + FRAME_MARGIN \
				and lp.z > float(f.E) - FRAME_MARGIN and lp.z < float(f.W) + FRAME_MARGIN:
			return deck_velocity(i, p)
	return Vector3.INF


func _exit_tree() -> void:
	if RemakeAirVehicle.frame_source == frame_at:
		RemakeAirVehicle.frame_source = Callable()


# ------------------------------------------------------------------ fast travel (GameMenu's Navigator, "Floating Cities")
var _travel_to := -1
var _travel_t := 0.0


func travel_names() -> Array:
	## [[index, name], ...] for the Navigator
	var out := []
	for i in islands.size():
		out.append([i, str(islands[i].canon.get("name", layouts[i].id))])
	return out


var _travel_side := {}               # island index -> its warren side file's travel point (read once)


func travel_local(i: int) -> Vector3:
	## where one arrives on island i (its own frame): the layout's "travel" point if it has one (the city's main square or
	## landing), else the walkway node nearest the island's middle
	var L: Dictionary = layouts[i]
	var wv: SkyWarren = islands[i].warren
	if wv and wv.travel().size() >= 3:
		var tw: Array = wv.travel()
		return Vector3(float(tw[0]), float(tw[1]), float(tw[2]))
	if SkyWarren.has_file(str(L.id)):
		# (the city not built yet: its side file says where -- a megabyte of json: parsed once, not every frame of the
		# fast travel's hold)
		if not _travel_side.has(i):
			_travel_side[i] = []
			var sp := SkyWarren.DIR + str(L.id) + ".json"
			if DataFile.exists(sp):
				# (just its "travel": [x, y, z, yaw], found in the text: parsing the whole file took ~50 ms)
				var txt := DataFile.text(sp)
				var at := txt.find("\"travel\":")
				if at >= 0:
					var tr = JSON.parse_string(txt.substr(txt.find("[", at), txt.find("]", at) - txt.find("[", at) + 1))
					if tr is Array and tr.size() >= 3:
						_travel_side[i] = tr
		var tj: Array = _travel_side[i]
		if tj.size() >= 3:
			return Vector3(float(tj[0]), float(tj[1]), float(tj[2]))
	if L.has("travel"):
		var t: Array = L.travel
		return Vector3(float(t[0]), islands[i].deck_y(float(t[0]), float(t[1])), float(t[1]))
	var best := Vector2.ZERO
	var bd := INF
	for n in L.get("graph", {}).get("nodes", []):
		var v := Vector2(float(n[0]), float(n[1]))
		if v.length() < bd:
			bd = v.length()
			best = v
	return Vector3(best.x, islands[i].deck_y(best.x, best.y), best.y)


func travel_point_sx(i: int) -> Vector2:
	var p := islands[i].global_transform * travel_local(i)
	return Vector2(StationGeo.s_of(p), p.x)


func fast_travel(i: int) -> void:
	## held over the city (no gravity) until its deck has loaded, then set down on it
	if i < 0 or i >= islands.size() or player == null:
		return
	_travel_to = i
	_travel_t = 0.0
	player.set_physics_process(false)
	_hold_traveller()


func _hold_traveller() -> void:
	var isl := islands[_travel_to]
	var lp := travel_local(_travel_to) + Vector3(0, 1.5, 0)
	player.global_transform = Transform3D(isl.global_transform.basis, isl.global_transform * lp)
	player.velocity = Vector3.ZERO


func _travel_step(delta: float) -> void:
	if _travel_to < 0:
		return
	_travel_t += delta
	_hold_traveller()
	var isl := islands[_travel_to]
	if (isl.has_node("Near/Rock") and (isl.warren == null or isl.warren.near_ready())) or _travel_t > 25.0:
		player.set_physics_process(true)
		_travel_to = -1


func aboard() -> int:
	return _aboard


# ------------------------------------------------------------------ every frame
func _process(delta: float) -> void:
	if not ready_:
		return
	var cam := player.camera.global_position if player else Vector3.ZERO
	_tier_t -= delta
	if _tier_t <= 0.0:
		_tier_t = 0.4
		Prof.begin("sky.tier")
		for isl in islands:
			var d := isl.global_position.distance_to(cam)
			isl.set_tier(2 if d < SkyIsland.NEAR else (1 if d < SkyIsland.MID else 0))
			isl.set_physics_active(d < PHYS_R + isl.radius())
		Prof.end("sky.tier")
	Prof.begin("sky.balloons")
	_balloons()
	Prof.end("sky.balloons")
	Prof.begin("sky.banners")
	if banners:
		banners.step(delta)
	Prof.end("sky.banners")
	Prof.begin("sky.night")
	_night_step(delta)
	Prof.end("sky.night")
	Prof.begin("sky.lines")
	_draw_lines(cam)
	Prof.end("sky.lines")
	Prof.begin("sky.steer")
	_steer_clouds()                               # (a few clouds a frame)
	Prof.end("sky.steer")
	Prof.begin("sky.snow")
	_snow_step(delta)
	_flakes_step(cam)
	Prof.end("sky.snow")
	_plumb_step(delta)
	for c in _cargo.duplicate():
		c[1] -= delta
		if c[1] <= 0.0:
			(c[0] as Node).queue_free()
			_cargo.erase(c)


const PHYS_R := 120.0                 # m past an island's edge within which its collision is live


var _bal_frame := 0
var _buf_near := PackedFloat32Array()
var _buf_far := PackedFloat32Array()


func _balloons() -> void:
	## both envelope MultiMeshes from flat buffers (one call each, not two per balloon); the far set -- islands 3.6 km
	## and more away, moving a few metres a second -- only every fourth frame
	_bal_frame += 1
	var do_far := _bal_frame % 4 == 0 or _buf_far.is_empty()
	var nn := 0
	var nf := 0
	for i in islands.size():
		var c: int = layouts[i].balloons.size()
		if islands[i].tier >= 1:
			nn += c
		else:
			nf += c
	_buf_near.resize(nn * 16)
	if do_far:
		_buf_far.resize(nf * 16)
	var kn := 0
	var kf := 0
	for i in islands.size():
		var isl := islands[i]
		var near := isl.tier >= 1
		if not near and not do_far:
			continue
		var xf := isl.global_transform
		var bs := xf.basis
		var bl: Array = layouts[i].balloons
		var looks: Array = _bal_look[i] if i < _bal_look.size() else []
		for k in bl.size():
			var b: Dictionary = bl[k]
			var o: Vector3 = xf * Vector3(b.x, BALLOON_BASE, b.z)
			var c: Color = looks[k] if k < looks.size() else Color(1, 1, 1, 0)
			# (packed arrays copy on assignment: each buffer is written in place)
			if near:
				var j := kn * 16
				_buf_near[j] = bs.x.x; _buf_near[j + 1] = bs.y.x; _buf_near[j + 2] = bs.z.x; _buf_near[j + 3] = o.x
				_buf_near[j + 4] = bs.x.y; _buf_near[j + 5] = bs.y.y; _buf_near[j + 6] = bs.z.y; _buf_near[j + 7] = o.y
				_buf_near[j + 8] = bs.x.z; _buf_near[j + 9] = bs.y.z; _buf_near[j + 10] = bs.z.z; _buf_near[j + 11] = o.z
				_buf_near[j + 12] = c.r; _buf_near[j + 13] = c.g; _buf_near[j + 14] = c.b; _buf_near[j + 15] = c.a
				kn += 1
			else:
				var j := kf * 16
				_buf_far[j] = bs.x.x; _buf_far[j + 1] = bs.y.x; _buf_far[j + 2] = bs.z.x; _buf_far[j + 3] = o.x
				_buf_far[j + 4] = bs.x.y; _buf_far[j + 5] = bs.y.y; _buf_far[j + 6] = bs.z.y; _buf_far[j + 7] = o.y
				_buf_far[j + 8] = bs.x.z; _buf_far[j + 9] = bs.y.z; _buf_far[j + 10] = bs.z.z; _buf_far[j + 11] = o.z
				_buf_far[j + 12] = c.r; _buf_far[j + 13] = c.g; _buf_far[j + 14] = c.b; _buf_far[j + 15] = c.a
				kf += 1
	_set_buf(_mm_near.multimesh, _buf_near, nn)
	if do_far:
		_set_buf(_mm_far.multimesh, _buf_far, nf)


static func _set_buf(mm: MultiMesh, buf: PackedFloat32Array, n: int) -> void:
	if mm.instance_count != n:
		mm.instance_count = n
	if n > 0:
		mm.buffer = buf


static func _fill(mm: MultiMesh, xf: Array[Transform3D], custom: Array[Color] = []) -> void:
	if mm.instance_count != xf.size():
		mm.instance_count = xf.size()
	for k in xf.size():
		mm.set_instance_transform(k, xf[k])
		if k < custom.size():
			mm.set_instance_custom_data(k, custom[k])


func _launcher(i: int, side: String) -> Vector3:
	for l in layouts[i].get("launchers", []):
		if l.side == side:
			return islands[i].global_transform * Vector3(l.x, 3.0, l.z)
	var f: Dictionary = layouts[i].faces
	var lp: Vector3 = {"N": Vector3(f.N, 3, 0), "S": Vector3(f.S, 3, 0), "E": Vector3(0, 3, f.E), "W": Vector3(0, 3, f.W)}[side]
	return islands[i].global_transform * lp


func _draw_lines(cam: Vector3) -> void:
	## line rockets in flight and the lines they've carried over: from a launcher on the host's facing side to one
	## on the guest's, sagging (more the longer and slacker), the rocket at the head while it flies
	var im := _lines.mesh as ImmediateMesh
	im.clear_surfaces()
	var heads: Array[Transform3D] = []
	var any := false
	for ln in drift.lines:
		var a := _launcher(ln.a, ln.side)
		var b := _launcher(ln.b, SkyDrift._opp(ln.side))
		if a.distance_to(cam) > LINE_RANGE and b.distance_to(cam) > LINE_RANGE:
			continue
		var head := a.lerp(b, ln.fly)
		var down := -StationGeo.up(StationGeo.s_of(a))
		var L := a.distance_to(head)
		if not any:
			im.surface_begin(Mesh.PRIMITIVE_LINES)
			any = true
		var prev := a
		for k in range(1, 17):
			var f := k / 16.0
			var q := a.lerp(head, f) + down * (4.0 * f * (1.0 - f)) * L * (0.06 if ln.fly < 1.0 else 0.03)
			im.surface_add_vertex(prev)
			im.surface_add_vertex(q)
			prev = q
		if ln.fly < 1.0:
			heads.append(Transform3D(Basis.looking_at((b - a).normalized(), -down), head))
	if any:
		im.surface_end()
	_fill(_rockets.multimesh, heads)


var _steer_t := 0.0
var _steer_i := 0
const STEER_SHARE := 0.65             # of the island layer's clouds: the rest wander as before
const STEER_AHEAD := 6000.0           # m ahead (west) a cloud looks for an island to pass through


func _steer_clouds() -> void:
	## The clouds at the islands' height run west faster than the islands drift, so they overtake them from the east;
	## most of them (STEER_SHARE) also edge north or south onto the line of the nearest island ahead and settle to its
	## height -- so the islands float through clouds now and then, and it snows on them (the user, 2026-10-14)
	if clouds == null or clouds._low.is_empty():
		return
	for step in 3:
		_steer_i = (_steer_i + 1) % clouds._low.size()
		var c: Dictionary = clouds._low[_steer_i]
		if c.layer != RemakeClouds.ISLAND_LAYER or c.state != "free" or c.kind != 0:
			continue
		if float(absi(hash(c.uid)) % 1000) / 1000.0 >= STEER_SHARE:
			continue
		var best := -1
		var bd := INF
		for i in islands.size():
			var p := drift.pos(i)
			var ahead := -StationGeo.wrap_ds(p.x - float(c.s))          # (> 0: the island is west of the cloud)
			if ahead < 0.0 or ahead > STEER_AHEAD:
				continue
			var d := ahead + absf(p.y - float(c.x)) * 2.0
			if d < bd:
				bd = d
				best = i
		if best < 0:
			continue
		var dx: float = drift.pos(best).y - float(c.x)
		c.vx = clampf(dx / 120.0, -RemakeClouds.DRIFT_NS, RemakeClouds.DRIFT_NS)
		c.h0 = drift.altitude(best) - 30.0                               # (its base just under the deck: the town's in it)


func _snow_step(_delta: float) -> void:
	## Two islands a frame (every island about once a second).  Snow builds while an island is in a cloud (sampled over
	## its deck and up past its roofs) -- and, lighter, under a storm cell or a front's drizzle: whatever falls past
	## 750 m falls as snow (it melts lower down: the floor gets rain).  Out of it, it melts very slowly, by day.
	var now := Time.get_ticks_msec() * 0.001
	if _snow_last.size() != islands.size():
		_snow_last.resize(islands.size())
		_snow_last.fill(now)
	var day := sky.daylight() if sky else 1.0
	var storms: Array = clouds.storms() if clouds else []
	for k in 2:
		var i := (_cloud_i + k) % islands.size()
		var isl := islands[i]
		var dt := now - _snow_last[i]
		_snow_last[i] = now
		var fall := _snowfall(i, storms)
		isl.snowing = fall
		var v := isl.snow
		if fall > 0.0:
			v = minf(1.0, v + SNOW_IN * fall * dt)
		else:
			v = maxf(0.0, v - SNOW_MELT * day * dt)
		isl.set_snow(v)
	_cloud_i = (_cloud_i + 2) % islands.size()


func _snowfall(i: int, storms: Array) -> float:
	## how hard it snows on island i now (0 none, ~1 in a cloud's heart)
	if clouds == null:
		return 0.0
	var isl := islands[i]
	var xf := isl.global_transform
	var f: Dictionary = layouts[i].faces
	var depth := 0.0
	# (a cheap first look: any cloud whose reach touches the island at all? the full test below samples ten points
	# against every cloud -- ~1.7 ms a frame when every island got it)
	var near := false
	var c0 := isl.global_position
	var rad := isl.radius() + 100.0
	for c in clouds._low:
		if c.state != "hidden" and (c.node as Node3D).global_position.distance_to(c0) < float(c.reach) + rad + 60.0:
			near = true
			break
	for p in ([Vector2.ZERO, Vector2(f.N, 0) * 0.7, Vector2(f.S, 0) * 0.7, Vector2(0, f.E) * 0.7, Vector2(0, f.W) * 0.7] if near else []):
		for y in [25.0, 90.0]:
			depth = maxf(depth, clouds.inside(xf * Vector3(p.x, y, p.y)))
		if depth > 0.0:
			break
	if depth > 0.0:
		return 0.4 + depth
	var g := isl.global_position
	var s := StationGeo.s_of(g)
	for st in storms:
		if float(st.base) > StationGeo.h_of(g) and absf(StationGeo.wrap_ds(s - float(st.s))) < float(st.fa) and absf(g.x - float(st.x)) < float(st.fb):
			return 0.5 * float(st.intensity) + 0.2
	return clouds.drizzle_at(s, g.x) * 0.3


# ------------------------------------------------------------------ snowfall
func _make_flakes() -> void:
	_flakes = GPUParticles3D.new()
	_flakes.name = "Snowfall"
	_flakes.amount = 2500
	_flakes.lifetime = 6.0
	_flakes.local_coords = false
	_flakes.emitting = false
	_flakes.visibility_aabb = AABB(Vector3(-40, -40, -40), Vector3(80, 80, 80))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = Vector3(30, 2, 30)
	pm.direction = Vector3.DOWN
	pm.spread = 15.0
	pm.initial_velocity_min = 0.6
	pm.initial_velocity_max = 1.4
	pm.gravity = Vector3(0, -0.9, 0)
	pm.turbulence_enabled = true
	pm.turbulence_noise_strength = 0.6
	pm.turbulence_noise_scale = 4.0
	pm.scale_min = 0.6
	pm.scale_max = 1.4
	_flakes.process_material = pm
	var q := QuadMesh.new()
	q.size = Vector2(0.06, 0.06)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = Color(1, 1, 1, 0.9)
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	q.material = m
	_flakes.draw_pass_1 = q
	add_child(_flakes)


func _flakes_step(cam: Vector3) -> void:
	## it snows wherever the camera is in a cloud aloft (the islands make the snow; the floor gets rain)
	var aloft := StationGeo.h_of(cam) > 450.0
	var depth := clouds.inside(cam) if clouds and aloft else 0.0
	var on := depth > 0.0 or (_aboard >= 0 and islands[_aboard].snowing > 0.0)
	_flakes.emitting = on
	if on:
		var s := StationGeo.s_of(cam)
		_flakes.global_transform = Transform3D(StationGeo.basis(s), cam + StationGeo.up(s) * 20.0)


func _in_cloud(i: int) -> bool:
	return clouds != null and clouds.inside(islands[i].global_transform * Vector3(0, 20, 0)) > 0.0


func _plumb_step(delta: float) -> void:
	## The plumb goes down: a near island's lark lifts off its cradle, flies down to the floor (the canon: one
	## representative per clan does the trading in person), waits, and comes back to the same cradle -- the pad
	## followed as the island drifts; landed, it's the island's again.
	_plumb_t -= delta
	for f in _flights.duplicate():
		var k: Node3D = f.lark
		if not is_instance_valid(k):
			_flights.erase(f)
			continue
		if f.state == "floor":
			f.t -= delta
			if f.t <= 0.0:
				f.state = "up"
				var isl: SkyIsland = f.island
				var pad: Transform3D = f.pad
				var p := VehiclePilot.fly_to(k as RemakeAirVehicle, isl, pad.origin, 60.0)
				p.arrived.connect(func() -> void: _landed(f))
	if _plumb_t > 0.0 or _flights.size() >= 2:
		return
	_plumb_t = randf_range(PLUMB_EVERY.x, PLUMB_EVERY.y)
	for isl in islands:
		if isl.tier == 2 and isl.global_position.distance_to(player.global_position) < 2500.0:
			var k: Node3D = isl.take_lark()
			if k == null or not is_instance_valid(k):
				continue
			var pad := k.transform
			k.reparent(self, true)
			k.remove_meta("riding")
			SkyIsland._ranges(k, 0.0, 4000.0)            # (seen going down and coming back)
			# down to the floor some way off under the island's drift (a trade yard; the floor's towns come later)
			var g := isl.global_position
			var s := fposmod(StationGeo.s_of(g) - 900.0, StationGeo.CIRC)
			var x := clampf(g.x + randf_range(-600.0, 600.0), -9000.0, 9000.0)
			var f := {"lark": k, "island": isl, "pad": pad, "state": "down", "t": PLUMB_STAY}
			_flights.append(f)
			var p := VehiclePilot.drive(k as RemakeAirVehicle, StationGeo.point(s, x, maxf(MapTerrain.elevation(s, x), 0.0)), 60.0)
			p.arrived.connect(func() -> void:
				f.state = "floor"
				f.t = PLUMB_STAY)
			return


func _landed(f: Dictionary) -> void:
	var k: Node3D = f.lark
	var isl: SkyIsland = f.island
	_flights.erase(f)
	if not is_instance_valid(k):
		return
	if isl.tier < 2 or not isl.has_node("Near"):
		k.queue_free()
		return
	k.reparent(isl.get_node("Near"), false)
	k.transform = f.pad
	k.set_meta("riding", true)
	SkyIsland._ranges(k, 0.0, 350.0)
	isl.return_lark(k, f.pad)


func drop_cargo(c: Node3D, at: Vector3) -> void:
	## a container let go at the floor: stands where it landed for the ground crew
	add_child(c)
	var s := StationGeo.s_of(at)
	var x := at.x
	c.global_transform = Transform3D(StationGeo.basis(s), StationGeo.point(s, x, maxf(MapTerrain.elevation(s, x), 0.0)))
	c.visible = true
	_cargo.append([c, CARGO_LIFE])


func debug_snow(v: float) -> void:
	for isl in islands:
		isl.set_snow(v)


# ------------------------------------------------------------------ the balloons' looks, and the night
var models := {}                      # the layout's shared building models (SkySigns reads their sizes / anchors)
var _bal_look: Array = []             # per island, per balloon: Color(clan rgb, (ad row + 1) / 128)
var _night_t := 0.0
const BALLOON_ADS := ["LIGHT HANDS LONG LINES", "BERRY WINE", "SNOW HONEY", "SKYCLOTH", "ROPE THAT HOLDS",
	"NO FLAME NO FALL", "LASHING SALE", "WARM GANSEYS", "HOT TEA", "THE SKEIN", "LARK REPAIRS", "DOWN QUILTS",
	"FRESH SKYBOXES", "GOGGLES", "MEAD", "CLOUD PORRIDGE", "NOODLES", "BELLS", "TRADE HERE", "WEIGH IT"]


func _balloon_looks(by_id: Dictionary) -> void:
	## every balloon: its clan's colour, and on about a third of them an advert -- the island's own wares or a slogan
	var ads: Array = BALLOON_ADS.duplicate()
	for i in layouts.size():
		var c: Dictionary = by_id.get(layouts[i].id, {})
		ads.append(("%s %s" % [str(c.get("name", "")), str(c.get("specialty", ""))]).to_upper().left(22))
	var tex := SkyDotFont.strip_texture(ads, 22 * SkyDotFont.ADVANCE)
	var mat := ShaderMaterial.new()
	mat.shader = load("res://remake/shaders/sky_balloon.gdshader")
	mat.set_shader_parameter("ads", tex)
	for m in [_mm_near, _mm_far]:
		(m as MultiMeshInstance3D).material_override = mat
	var r := RandomNumberGenerator.new()
	for i in layouts.size():
		var c: Dictionary = by_id.get(layouts[i].id, {})
		var cols: Array = c.get("colors", ["#c08040"])
		var clan := Color(str(cols[0]))
		var own := BALLOON_ADS.size() + i            # (this island's own advert's row)
		r.seed = hash(str(layouts[i].id) + ":balloons")
		var row: Array = []
		for k in (layouts[i].balloons as Array).size():
			var ad := -1
			if r.randf() < 0.36:
				ad = own if r.randf() < 0.5 else r.randi() % BALLOON_ADS.size()
			var tint := clan.lerp(Color(str(cols[k % cols.size()])), 0.5) if k % 3 == 2 else clan
			row.append(Color(tint.r, tint.g, tint.b, float(ad + 1) / 128.0))
		_bal_look.append(row)


func _night_step(delta: float) -> void:
	## once a second: every island's far glitter on or off
	_night_t -= delta
	if _night_t > 0.0:
		return
	_night_t = 1.0
	var n := 1.0 - (sky.daylight() if sky else 1.0)
	for isl in islands:
		isl.set_night(n)

