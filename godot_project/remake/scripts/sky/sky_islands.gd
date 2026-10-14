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
	_lines = MeshInstance3D.new()
	_lines.name = "Lines"
	_lines.mesh = ImmediateMesh.new()
	_lines.material_override = SkyIsland._mat("sky_tether", Color(0.2, 0.18, 0.15))
	_lines.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_lines)
	_rockets = _mm("Rockets", SkyIsland.part_mesh("rocket"))
	_make_flakes()
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
		return
	drift.step(delta)
	for i in islands.size():
		islands[i].global_transform = drift.transform(i)
	_events()
	_carry()


func _events() -> void:
	## an edge lashed: its two bridges come down; cast off: they go up
	for ev in drift.events:
		if ev[0] == "lash" or ev[0] == "cast_off":
			var e: Dictionary = ev[1]
			var down: bool = ev[0] == "lash"
			islands[e.a].set_bridge(e.side, e.along_a, down)
			islands[e.b].set_bridge(SkyDrift._opp(e.side), e.along_b, down)
	drift.events.clear()


func _carry() -> void:
	## the player aboard: carried by the deck, and lighter
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
		if isl.inside(lp) and lp.y > -4.0 and lp.y < 120.0:
			on = i
			break
	if on >= 0:
		player.carrier_velocity = drift.velocity(on, p)
		player.gravity_k = ABOARD_G
	elif _aboard >= 0:
		player.carrier_velocity = Vector3.ZERO
		player.gravity_k = 1.0
	_aboard = on


const FRAME_OVER := 500.0             # m over a deck a flier takes on the island's motion (RemakeAirVehicle)
const FRAME_MARGIN := 30.0            # m round the deck's edges


func frame_at(p: Vector3) -> Vector3:
	## the moving air over an island (to land on it, an aircraft flies relative to this): the island's velocity
	## anywhere over its deck up to FRAME_OVER m above it, else Vector3.INF
	if not ready_:
		return Vector3.INF
	for i in islands.size():
		var isl := islands[i]
		if isl.global_position.distance_squared_to(p) > 640000.0:          # (800 m)
			continue
		var lp := isl.global_transform.affine_inverse() * p
		var f: Dictionary = layouts[i].faces
		if lp.y > -10.0 and lp.y < FRAME_OVER and lp.x > float(f.N) - FRAME_MARGIN and lp.x < float(f.S) + FRAME_MARGIN \
				and lp.z > float(f.E) - FRAME_MARGIN and lp.z < float(f.W) + FRAME_MARGIN:
			return drift.velocity(i, p)
	return Vector3.INF


func _exit_tree() -> void:
	if RemakeAirVehicle.frame_source == frame_at:
		RemakeAirVehicle.frame_source = Callable()


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
		for isl in islands:
			var d := isl.global_position.distance_to(cam)
			isl.set_tier(2 if d < SkyIsland.NEAR else (1 if d < SkyIsland.MID else 0))
	_balloons()
	_draw_lines(cam)
	_snow_step(delta)
	_flakes_step(cam)
	_plumb_step(delta)
	for c in _cargo.duplicate():
		c[1] -= delta
		if c[1] <= 0.0:
			(c[0] as Node).queue_free()
			_cargo.erase(c)


func _balloons() -> void:
	var near: Array[Transform3D] = []
	var far: Array[Transform3D] = []
	for i in islands.size():
		var isl := islands[i]
		var xf := isl.global_transform
		for b in layouts[i].balloons:
			var t := xf * Transform3D(Basis(), Vector3(b.x, BALLOON_BASE, b.z))
			if isl.tier >= 1:
				near.append(t)
			else:
				far.append(t)
	_fill(_mm_near.multimesh, near)
	_fill(_mm_far.multimesh, far)


static func _fill(mm: MultiMesh, xf: Array[Transform3D]) -> void:
	if mm.instance_count != xf.size():
		mm.instance_count = xf.size()
	for k in xf.size():
		mm.set_instance_transform(k, xf[k])


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
	for p in [Vector2.ZERO, Vector2(f.N, 0) * 0.7, Vector2(f.S, 0) * 0.7, Vector2(0, f.E) * 0.7, Vector2(0, f.W) * 0.7]:
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
		if isl.tier == 2 and isl.larks_parked.size() > 0 and isl.global_position.distance_to(player.global_position) < 2500.0:
			var k: Node3D = isl.larks_parked.pop_back()
			if not is_instance_valid(k):
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
	isl.larks_parked.append(k)


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
