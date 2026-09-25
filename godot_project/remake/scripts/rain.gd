extends Node3D
class_name RemakeRain

## The rain and thunder under RemakeClouds' storms -- only under the storm cells, nowhere else.
##
## How games do it, and how this does (Godot 4):
##   * Near the camera: a GPUParticles3D box of streaks carried with the camera (the "camera-attached
##     rain volume" of most FPS games), turned so its down is the floor's down at the camera (the
##     ring's gravity points away from the axis).  Its thinning (amount_ratio) is the storm's
##     intensity, fading out at the storm's edge -- so it only rains under the cloud.
##   * Rain doesn't come indoors or through roofs: a GPUParticlesCollisionHeightField3D rides with
##     the camera and renders the geometry below it from above each frame (the "rain occlusion /
##     rain shadow map" of Infamous, Watch Dogs etc.); drops that hit a roof, a wall top or the
##     ground die there, and each spawns a splash (a sub-emitter at collision).
##   * From a distance: each storm is a tall translucent column of falling streaks from its cloud
##     base to the floor (rain_shaft.gdshader) that moves with the cloud.
##   * Sound: each storm's rain is heard only near it -- a 3D rain loop at the nearest point of its
##     footprint to the camera (at the camera when it's under the storm), muffled under a roof.
##     Thunder alone carries across the station.
##   * Thunderstorms: lightning bolts from the cell's base to the floor at random under it, a flash
##     of light, and thunder that arrives distance / 343 m/s later.

const NEAR_BOX := 36.0               # m: half-size of the particle box round the camera
const DROP_SPEED := 26.0
const THUNDER_EVERY := Vector2(4.0, 12.0)

var camera: Camera3D
var clouds: RemakeClouds
var _rain: GPUParticles3D
var _splash: GPUParticles3D
var _rig: Node3D
var _hf: GPUParticlesCollisionHeightField3D
var _pm: ParticleProcessMaterial
var _spm: ParticleProcessMaterial
var _shafts := {}                    # storm id -> MeshInstance3D
var _shaft_shader: Shader
var _rain_snd: AudioStreamWAV
var _sounds := {}                    # storm id -> AudioStreamPlayer3D
var _thunder_snd: AudioStreamWAV
var _next_bolt := {}                 # storm id -> seconds to its next bolt
var _pending_thunder: Array = []     # [seconds left, volume db]
var _bolts: Array = []               # [node, light, seconds left]
var _bolt_mat: StandardMaterial3D
var _rng := RandomNumberGenerator.new()


func setup(p_camera: Camera3D, p_clouds: RemakeClouds) -> void:
	camera = p_camera
	clouds = p_clouds
	_rng.seed = 424242
	_shaft_shader = load("res://remake/shaders/rain_shaft.gdshader")
	_rig = Node3D.new()
	_rig.name = "RainRig"
	add_child(_rig)
	# the splashes: a tiny burst where each drop dies
	_splash = GPUParticles3D.new()
	_splash.name = "Splash"
	_splash.amount = 3000
	_splash.lifetime = 0.3
	_splash.emitting = false
	_splash.local_coords = false
	_spm = ParticleProcessMaterial.new()
	_spm.direction = Vector3.UP
	_spm.spread = 70.0
	_spm.initial_velocity_min = 1.0
	_spm.initial_velocity_max = 2.2
	_spm.gravity = Vector3(0, -9.8, 0)
	_spm.scale_min = 0.6
	_spm.scale_max = 1.2
	_splash.process_material = _spm
	var sq := QuadMesh.new()
	sq.size = Vector2(0.035, 0.035)
	var sm := StandardMaterial3D.new()
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	sm.albedo_color = Color(0.85, 0.88, 0.92, 0.55)
	sm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	sq.material = sm
	_splash.draw_pass_1 = sq
	_splash.visibility_aabb = AABB(Vector3(-60, -60, -60), Vector3(120, 120, 120))
	add_child(_splash)
	# the drops
	_rain = GPUParticles3D.new()
	_rain.name = "Rain"
	_rain.amount = 14000
	_rain.lifetime = 1.8
	_rain.preprocess = 1.0
	_rain.local_coords = false
	_rain.emitting = false
	_rain.visibility_aabb = AABB(Vector3(-60, -80, -60), Vector3(120, 120, 120))
	_pm = ParticleProcessMaterial.new()
	_pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	_pm.emission_box_extents = Vector3(NEAR_BOX, 1.0, NEAR_BOX)
	_pm.direction = Vector3(0, -1, 0)
	_pm.spread = 1.5
	_pm.initial_velocity_min = DROP_SPEED * 0.9
	_pm.initial_velocity_max = DROP_SPEED * 1.1
	_pm.gravity = Vector3(0, -9.8, 0)
	_pm.particle_flag_align_y = true
	_pm.collision_mode = ParticleProcessMaterial.COLLISION_HIDE_ON_CONTACT
	_pm.sub_emitter_mode = ParticleProcessMaterial.SUB_EMITTER_AT_COLLISION
	_pm.sub_emitter_amount_at_collision = 1
	_rain.process_material = _pm
	_rain.collision_base_size = 0.02
	var q := QuadMesh.new()
	q.size = Vector2(0.012, 0.55)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = Color(0.78, 0.81, 0.86, 0.28)
	m.billboard_mode = BaseMaterial3D.BILLBOARD_FIXED_Y
	m.billboard_keep_scale = true
	q.material = m
	_rain.draw_pass_1 = q
	_rig.add_child(_rain)
	_rain.sub_emitter = _rain.get_path_to(_splash)
	# the rain shadow: what's under the camera (roofs, walls, the ground), from above
	_hf = GPUParticlesCollisionHeightField3D.new()
	_hf.name = "RainShadow"
	_hf.size = Vector3(NEAR_BOX * 2.2, 90.0, NEAR_BOX * 2.2)
	_hf.resolution = GPUParticlesCollisionHeightField3D.RESOLUTION_256
	_hf.update_mode = GPUParticlesCollisionHeightField3D.UPDATE_MODE_ALWAYS
	_hf.follow_camera_enabled = false
	add_child(_hf)
	# sound
	_rain_snd = load("res://remake/audio/rain_loop.wav")
	_rain_snd.loop_mode = AudioStreamWAV.LOOP_FORWARD
	_rain_snd.loop_begin = 0
	_rain_snd.loop_end = _rain_snd.data.size() / 2
	_thunder_snd = load("res://remake/audio/thunder.wav")
	_bolt_mat = StandardMaterial3D.new()
	_bolt_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_bolt_mat.albedo_color = Color(0.9, 0.93, 1.0)
	_bolt_mat.emission_enabled = true
	_bolt_mat.emission = Color(0.85, 0.9, 1.0)
	_bolt_mat.emission_energy_multiplier = 6.0
	set_process(true)


func _process(delta: float) -> void:
	if camera == null or clouds == null:
		return
	var storms: Array = clouds.storms()
	var cp := camera.global_position
	var cs := StationGeo.s_of(cp)
	var ch := StationGeo.h_of(cp)
	var up := StationGeo.up(cs)
	# ---- how hard it rains where the camera is, and how near a storm is (for the sound)
	var here := 0.0
	var live := {}
	var roofed := _roofed(cp, up)
	for st in storms:
		var d := Vector2(StationGeo.wrap_ds(st.s - cs), st.x - cp.x).length()
		if ch < st.base:
			here = maxf(here, st.intensity * (1.0 - smoothstep(0.85, 1.0, _foot_r(st, cs, cp.x))))
		live[st.id] = true
		_shaft(st)
		_sound(st, cs, cp, ch, roofed)
		if st.thunder:
			_thunder_step(st, delta, d)
	for id in _shafts.keys():
		if not live.has(id):
			(_shafts[id] as Node).queue_free()
			_shafts.erase(id)
			if _sounds.has(id):
				(_sounds[id] as Node).queue_free()
				_sounds.erase(id)
			_next_bolt.erase(id)
	# ---- the particles: the box above the camera, down = the floor's down there
	var basis := StationGeo.basis(cs)
	_rig.global_transform = Transform3D(basis, cp + up * 28.0)
	_hf.global_transform = Transform3D(basis, cp)
	_pm.gravity = -up * 9.8
	_pm.direction = basis.inverse() * -up
	_spm.gravity = -up * 9.8
	_spm.direction = up
	_rain.amount_ratio = clampf(here, 0.0, 1.0)
	_rain.emitting = here > 0.01
	# ---- lightning and thunder in flight
	for b in _bolts.duplicate():
		b[2] -= delta
		(b[1] as OmniLight3D).light_energy = maxf(0.0, (b[1] as OmniLight3D).light_energy - delta * 60.0)
		(b[0] as Node3D).visible = fmod(b[2], 0.08) > 0.03
		if b[2] <= 0.0:
			(b[0] as Node).queue_free()
			(b[1] as Node).queue_free()
			_bolts.erase(b)
	for t in _pending_thunder.duplicate():
		t[0] -= delta
		if t[0] <= 0.0:
			var p := AudioStreamPlayer.new()
			p.stream = _thunder_snd
			p.volume_db = t[1]
			add_child(p)
			p.play()
			p.finished.connect(p.queue_free)
			_pending_thunder.erase(t)


static func _foot_r(st: Dictionary, s: float, x: float) -> float:
	## Where (s, x) is in a storm's footprint (the ellipse under its cloud): < 1 inside, 1 on its edge.
	var ds := StationGeo.wrap_ds(s - st.s) / maxf(float(st.fa), 1.0)
	var dx := (x - float(st.x)) / maxf(float(st.fb), 1.0)
	return sqrt(ds * ds + dx * dx)


func _sound(st: Dictionary, cs: float, cp: Vector3, ch: float, roofed: bool) -> void:
	## The storm's rain, heard from the nearest point of its footprint (the camera's own spot when
	## under it); it dies away within about a storm's radius outside it.
	var p: AudioStreamPlayer3D = _sounds.get(st.id)
	if p == null:
		p = AudioStreamPlayer3D.new()
		p.stream = _rain_snd
		p.attenuation_model = AudioStreamPlayer3D.ATTENUATION_LOGARITHMIC
		p.unit_size = 40.0
		p.max_distance = float(st.radius) * 1.5
		add_child(p)
		p.play()
		_sounds[st.id] = p
	var to := Vector2(StationGeo.wrap_ds(cs - st.s), cp.x - st.x)
	var k := _foot_r(st, cs, cp.x)
	var inside := k <= 1.0
	if not inside:
		to /= k                                                 # onto the footprint's edge
	var g := MapTerrain.elevation(st.s + to.x, st.x + to.y)
	p.global_position = StationGeo.point(st.s + to.x, st.x + to.y, minf(ch, st.base - 5.0) if inside else g + 2.0)
	p.volume_db = linear_to_db(maxf(float(st.intensity), 0.0001)) - (10.0 if roofed else 0.0)


func _roofed(cp: Vector3, up: Vector3) -> bool:
	var q := PhysicsRayQueryParameters3D.create(cp + up * 0.5, cp + up * 40.0)
	var hit := get_world_3d().direct_space_state.intersect_ray(q)
	return not hit.is_empty()


func _shaft(st: Dictionary) -> void:
	## The storm's rain seen from afar: a column of streaks from its cloud base to the floor.
	var g := MapTerrain.elevation(st.s, st.x)
	var H: float = maxf(20.0, st.base - g)
	var mi: MeshInstance3D = _shafts.get(st.id)
	if mi == null:
		mi = MeshInstance3D.new()
		mi.name = "shaft_" + str(st.id)
		var cyl := CylinderMesh.new()
		cyl.cap_top = false
		cyl.cap_bottom = false
		cyl.radial_segments = 48
		cyl.rings = 1
		cyl.height = 1.0
		mi.mesh = cyl
		var mat := ShaderMaterial.new()
		mat.shader = _shaft_shader
		mi.material_override = mat
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mi)
		_shafts[st.id] = mi
	var cyl2: CylinderMesh = mi.mesh
	cyl2.top_radius = 1.0
	cyl2.bottom_radius = 0.95
	var mat2: ShaderMaterial = mi.material_override
	mat2.set_shader_parameter("intensity", st.intensity)
	mat2.set_shader_parameter("height", H)
	# the unit cylinder stretched to the footprint's ellipse: fa along the wind (s), fb along the axis (x)
	var fwd := StationGeo.forward(st.s)
	var upv := StationGeo.up(st.s)
	mi.global_transform = Transform3D(Basis(fwd * float(st.fa), upv * H, Vector3(1, 0, 0) * float(st.fb)),
		StationGeo.point(st.s, st.x, g + H * 0.5))


func _thunder_step(st: Dictionary, delta: float, dist: float) -> void:
	var id: String = st.id
	var t: float = _next_bolt.get(id, _rng.randf_range(1.0, 4.0))
	t -= delta
	if t <= 0.0 and st.intensity > 0.3:
		_bolt(st, dist)
		t = _rng.randf_range(THUNDER_EVERY.x, THUNDER_EVERY.y) / maxf(st.intensity, 0.3)
	_next_bolt[id] = t


func _bolt(st: Dictionary, dist: float) -> void:
	## A lightning bolt from the cell's base to the floor, somewhere under it: a jagged line of thin
	## glowing boxes, a flash of light, then thunder delayed by the distance.
	var a := _rng.randf() * TAU
	var rr: float = sqrt(_rng.randf()) * 0.8
	var bs: float = st.s + cos(a) * rr * float(st.fa)
	var bx: float = st.x + sin(a) * rr * float(st.fb)
	var g := MapTerrain.elevation(bs, bx)
	var pts := []
	var n := 10
	var off := Vector2.ZERO
	for i in n + 1:
		var f := i / float(n)
		if i > 0 and i < n:
			off += Vector2(_rng.randf_range(-18.0, 18.0), _rng.randf_range(-18.0, 18.0))
		pts.append(StationGeo.point(bs + off.x, bx + off.y, lerpf(st.base, g, f)))
	var st_ := SurfaceTool.new()
	st_.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in n:
		var p0: Vector3 = pts[i]
		var p1: Vector3 = pts[i + 1]
		var ax := (p1 - p0).normalized()
		var s1 := ax.cross(Vector3.RIGHT if absf(ax.x) < 0.9 else Vector3.UP).normalized() * 1.2
		var s2 := ax.cross(s1).normalized() * 1.2
		var c := [s1, s2, -s1, -s2]
		for k in 4:
			var q := [p0 + c[k], p1 + c[k], p1 + c[(k + 1) % 4], p0 + c[(k + 1) % 4]]
			for j in [0, 1, 2, 0, 2, 3]:
				st_.add_vertex(q[j])
	var mi := MeshInstance3D.new()
	mi.mesh = st_.commit()
	mi.material_override = _bolt_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	var light := OmniLight3D.new()
	light.omni_range = 2500.0
	light.light_energy = 16.0
	light.light_color = Color(0.85, 0.9, 1.0)
	add_child(light)
	light.global_position = pts[n / 2]
	_bolts.append([mi, light, 0.35])
	var delay := clampf(dist / 343.0, 0.05, 10.0)
	var vol := clampf(-6.0 * log(maxf(dist, 150.0) / 150.0) / log(2.0), -40.0, 0.0)
	_pending_thunder.append([delay, vol])
