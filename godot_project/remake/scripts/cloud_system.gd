extends Node3D
class_name RemakeClouds

## The station's weather.  North is the Marlowe end cap (-x); east is +s (RemakeStation.compass_bearing).
##
##   Cumulus, in LOW_LAYERS (the lowest 200..300 m up, the rest stacked up the air column), LOW_COUNT
##   each: a few puffs blended into one smooth cartoon skin (a smooth-union distance field,
##   shrink-wrapped by a sphere of rays -- no facets, no seams) with a flat base, opaque and
##   cel-shaded (cumulus.gdshader) so the outline pass inks only the silhouette.  Skins are built on
##   worker threads.  Each is also a WaterVolume (the lake's trigger), so whatever flies into one
##   treats it as water, and the camera inside one whites out.
##
##   Every cumulus drifts on its own: the prevailing wind carries it east to west (-s) -- only the
##   lowest layer's clouds may run west to east -- while it wanders north and south.
##
##   Fronts (the 20 km ring's weather systems).  FRONTS bands of weather lie along the axis, end cap to
##   end cap, each a few km wide round the ring with a gentle wave in it, and creep antispinward (west)
##   slower than the wind.  Each lives FRONT_LIFE in-game hours, building and fading, and a new one forms
##   elsewhere after it.  Clouds gather in them -- a cloud out of every front thins away now and then and
##   forms again, mostly on a front's trailing (spinward) side, so the wind carries it through -- and
##   darken there; a grey sheet of altostratus rides over each (front_sheet), and it drizzles under the
##   sheet's core (drizzle_at).  weather_at(s, x) is the front cover anywhere, 0..1.
##
##   Coriolis, for a cylinder spun east (+s: spinward is east -- the air lags the floor, hence the
##   prevailing east wind).  Its spin is ~0.031 rad/s, so at weather scales it is strong, but on a
##   cylinder it acts only in the plane round the axis: a wind along the axis feels nothing, rising air
##   drifts antispinward and falling air (rain) spinward, an antispinward wind is lifted (it weighs less)
##   and a spinward one pressed down, and the spin lines weather up along the axis (Taylor columns).
##   Muted for the game, but there to be seen: the fronts' bands run along the axis; their tops lean
##   antispinward (LEAN_K: the sheet and the upper clouds run ahead of the rain); a storm cell leans the
##   same way (CELL_LEAN); clouds riding the east wind sit higher than ones running spinward
##   (CORIOLIS_LIFT); rain falls slanting spinward (RemakeRain.SLANT).
##
##   Storms (cumulus only).  Two clouds that touch (same layer) or line up one above the other
##   (different layers) reach a merge trigger; an RNG decides whether they merge (much likelier in a
##   front).  Merging, they drift together (the upper one sinking to the lower one's height) and become
##   one cloud: a formed cell, darker, with a rainstorm under it.  Two cells that merge make a
##   supercell: a thunderstorm.  A front's core also starts cells by itself (CELL_RATE): a squall line
##   that moves with the front.  Out of the fronts storms form only by day; at most MAX_STORMS at once.
##   A rainstorm begins to break up after RAIN_HOURS in-game hours, a thunderstorm after THUNDER_HOURS;
##   the break-up takes BREAKUP_HOURS, the rain fading, and the cell splits back into the clouds it was
##   made of, which drift apart.  The rain itself (particles, shafts, lightning, sound) is RemakeRain,
##   reading storms() and drizzle_at().
##
##   High cirrus, CIRRUS_SHELLS: sparse shells of flat translucent ribbons wrapped round the axis,
##   the way the spinning air carries them (cirrus.gdshader), drifting very slowly.
##
## Positions and the weather's dice are fixed-seed RNGs, so the same sky comes back every launch.

const LOW_COUNT := 20                  # per layer (the 20 km ring: fronts gather them; 12 was too thin a sky, 2026-10-14)
## cumulus layers: [base, lowest top, wind m/s, size] -- the clouds grow with height (size scales a
## cloud's length, and its puffs with it)
const LOW_LAYERS := [[200.0, 300.0, 12.0, 8.0], [500.0, 600.0, 15.0, 11.0], [900.0, 1000.0, 18.0, 14.0],
	[1400.0, 1500.0, 21.0, 17.0], [2000.0, 2100.0, 24.0, 20.0]]
const CUMULUS_CEILING := StationGeo.R - StationGeo.SHAFT_R - 300.0   # tops kept under the lower cirrus shell
const CIRRUS_ROWS := 24              # a cirrus shell: bands along the axis ...
const CIRRUS_COLS := 6               # ... by slots round it, one jittered ribbon each
const CIRRUS_H := StationGeo.R - StationGeo.SHAFT_R - 100.0  # 100 m off the central shaft
## cirrus shells: [height, wind m/s east, size] -- 100 m and 250 m off the central shaft
const CIRRUS_SHELLS := [[CIRRUS_H, 1.8, 3.0], [CIRRUS_H - 150.0, 2.4, 2.5]]
const END_CLEAR := 40.0              # m kept between a cloud and an end cap
const SEED := 20260924

# the weather
const MERGE_CHANCE := 0.15           # the RNG at a merge trigger out of the fronts ...
const FRONT_MERGE_CHANCE := 0.7      # ... and in a front's core
const MERGE_SPEED := 20.0            # m/s the two clouds close at
const SINK_SPEED := 12.0             # m/s the upper one sinks at
const MAX_STORMS := 8                # at once, round the whole ring (2 a day was far too few for 1,400 km2, the user 2026-10-14)
const CELL_RATE := 0.12              # per in-game hour: a cloud in a front's core starts a cell (a cell there: a thunderstorm)
const RAIN_HOURS := 2.5
const THUNDER_HOURS := 1.5
const BREAKUP_HOURS := 0.5
# the fronts
const FRONTS := 3                    # at once (one ~20 km of ring apart)
const FRONT_SPEED := Vector2(6.0, 10.0)     # m/s antispinward (west), slower than the wind
const FRONT_HALF := Vector2(1400.0, 2200.0) # m: the core's half-width round the ring
const FRONT_WAVE := Vector2(300.0, 900.0)   # m: the band's wave along the axis (amplitude) ...
const FRONT_WAVELEN := Vector2(9000.0, 18000.0)   # ... and its length
const FRONT_LIFE := Vector2(14.0, 30.0)     # in-game hours
const FRONT_GAP := Vector2(2.0, 6.0)        # in-game hours before the next forms
const FRONT_RAMP := 3.0                     # hours building up ...
const FRONT_FADE := 4.0                     # ... and dying away
const SHEET_H := 2900.0              # m: a front's altostratus sheet, over the top cumulus layer
# Coriolis, muted (see the header)
const LEAN_K := 0.35                 # m antispinward per m up: a front's tops run ahead of its base
const CELL_LEAN := 0.12              # rad a storm cell leans antispinward
const CORIOLIS_LIFT := 4.0           # m up per m/s of antispinward wind
# clouds thinning away and forming again
const FADE_SECONDS := 90.0
const THIN_EVERY := 600.0            # s: a cloud out of every front lasts about this long
const FRONT_RESEED := 0.75           # the share of new clouds that form in a front
const DRIFT_NS := 7.5                # m/s: the north-south wander's range
const CELL_COLOR := Color(0.5, 0.52, 0.58)
const SUPERCELL_COLOR := Color(0.34, 0.35, 0.41)

var target: Node3D                   # the camera the inside-a-cloud whiteout follows
var env: Environment
var sky: DaySkySystem                # the time of day (day / night)
var _low: Array = []                 # every cumulus: see _new_cloud
var _layers: Array = []              # the cumulus layer nodes
var _high_layers: Array = []         # [node, angular speed]
var _cumulus_mat: ShaderMaterial
var _cell_mat: ShaderMaterial
var _super_mat: ShaderMaterial
var _cirrus_mat: ShaderMaterial
var _rng := RandomNumberGenerator.new()
var _wx := RandomNumberGenerator.new()      # the weather's dice
var _fogged := false
var _skin_task := -1
var _skins: Array = []
var _jobs: Array = []                # [task id, cloud] skins being built for merged clouds
var _contacts := {}                  # Vector2i(a id, b id) -> true while two clouds stay at a trigger
var _trig_t := 0.0
var _next_uid := 0                    # each cloud's number (the contact keys)
var _hours := 0.0                    # in-game hours since start
var _next_id := 0
var _fronts: Array = []              # see _new_front
var _front_gap := 0.0                # in-game hours till another front may form
var _check_i := 0                    # the cloud the cover check is at (a few a frame)
var _sheet_mat: ShaderMaterial


func setup(p_target: Node3D, p_env: Environment, p_sky: DaySkySystem = null) -> void:
	target = p_target
	env = p_env
	sky = p_sky
	_rng.seed = SEED
	_wx.seed = SEED + 1
	_cumulus_mat = ShaderMaterial.new()
	_cumulus_mat.shader = load("res://remake/shaders/cumulus.gdshader")
	_cell_mat = _cumulus_mat.duplicate()
	_cell_mat.set_shader_parameter("body_color", CELL_COLOR)
	_super_mat = _cumulus_mat.duplicate()
	_super_mat.set_shader_parameter("body_color", SUPERCELL_COLOR)
	_cirrus_mat = ShaderMaterial.new()
	_cirrus_mat.shader = load("res://remake/shaders/cirrus.gdshader")
	_sheet_mat = _cirrus_mat.duplicate()
	_sheet_mat.set_shader_parameter("color", Color(0.74, 0.76, 0.81))
	for i in FRONTS:
		var f := _new_front(_rng, i * StationGeo.CIRC / FRONTS + _rng.randf_range(-3000.0, 3000.0))
		f.born = -_rng.randf_range(FRONT_RAMP, f.life * 0.6)              # already under way at launch
	for li in LOW_LAYERS.size():
		var lay := Node3D.new()
		lay.name = "Cumulus_%d" % li
		add_child(lay)
		_layers.append(lay)
		for i in LOW_COUNT:
			_low.append(_make_cumulus(li))
	for si in CIRRUS_SHELLS.size():
		var lay := Node3D.new()
		lay.name = "Cirrus_%d" % si
		lay.rotation.x = si * 1.3                              # the shells' gaps don't line up
		add_child(lay)
		var hh: float = CIRRUS_SHELLS[si][0]
		_high_layers.append([lay, CIRRUS_SHELLS[si][1] / (StationGeo.R - hh)])
		for row in CIRRUS_ROWS:
			_make_cirrus_band(row, lay, hh, CIRRUS_SHELLS[si][2])
	var all_puffs := []
	for c in _low:
		all_puffs.append(c.puffs)
	_skin_task = WorkerThreadPool.add_task(_make_skins.bind(all_puffs), false, "cloud skins")
	set_process(true)


# ------------------------------------------------------------------ cumulus
func _new_cloud(li: int, puffs: Array, s: float, x: float, h: float, kind: int) -> Dictionary:
	## A cumulus on layer li: its node (placed each frame from s, x, h), skin mesh, water volume.
	## kind 0 a plain cloud, 1 a cell (rain), 2 a supercell (thunder).
	var node := Node3D.new()
	node.name = "cumulus_%d" % _next_id
	_next_id += 1
	(_layers[li] as Node3D).add_child(node)
	var mi := MeshInstance3D.new()
	mi.material_override = [_cumulus_mat, _cell_mat, _super_mat][kind]
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	node.add_child(mi)
	var area := WaterVolume.new()
	area.name = "volume"
	area.flat_base = true                # drawn cut flat underneath: only what's above that is cloud
	for p in puffs:
		var cs := CollisionShape3D.new()
		var sph := SphereShape3D.new()
		sph.radius = p[1]
		cs.shape = sph
		cs.position = p[0]
		area.add_child(cs)
	node.add_child(area)
	var reach := 0.0
	var foot := 0.0
	var fa := 0.0                    # the footprint under its base: half-length along the wind (s) ...
	var fb := 0.0                    # ... and half-width across it (x)
	for p in puffs:
		reach = maxf(reach, Vector2(p[0].x, p[0].z).length() + p[1])
		foot = maxf(foot, Vector2(p[0].x, p[0].z).length() + p[1] * 0.8)
		var fr: float = sqrt(maxf(p[1] * p[1] - p[0].y * p[0].y, 0.0))   # the puff's circle on the base plane
		fa = maxf(fa, absf(p[0].x) + fr)
		fb = maxf(fb, absf(p[0].z) + fr)
	var wind: float = LOW_LAYERS[li][2]
	var vs: float = -wind * _rng.randf_range(0.7, 1.3)                # east to west ...
	if li == 0 and _rng.randf() < 0.5:
		vs = -vs                                                      # ... the lowest layer either way
	var c := {"node": node, "mesh": mi, "area": area, "puffs": puffs, "reach": reach + 25.0, "foot": foot, "fa": fa, "fb": fb,
		"layer": li, "s": s, "x": x, "h": h, "h0": h, "vs": vs, "vx": _rng.randf_range(-DRIFT_NS, DRIFT_NS),
		"kind": kind, "state": "free", "members": [], "partner": null, "storm": {}, "uid": _next_uid,
		"scale": 1.0, "fade": 0, "shade": 0.0}
	_next_uid += 1
	_place(c)
	return c


func _make_cumulus(li: int) -> Dictionary:
	var base: float = LOW_LAYERS[li][0]
	var size: float = LOW_LAYERS[li][3]
	# simple on purpose: a row of 2-4 big puffs along its length (local x, turned to run with the
	# wind round the ring) and a few smaller heads on top, all pressed flat underneath.  A cloud is
	# straight while the air it rides curves round the axis: kept short enough of its radius that
	# its ends don't droop out of its layer
	var length := minf(_rng.randf_range(45.0, 110.0) * size, 0.8 * (StationGeo.R - base))
	var puffs := []
	var n_base := clampi(roundi(length / 30.0), 2, 4)
	var r0 := length / (n_base + 1.0)
	for k in n_base:
		var r := r0 * _rng.randf_range(0.85, 1.15)
		var px := (k - (n_base - 1) * 0.5) * r0 * 1.1
		puffs.append([Vector3(px, r * 0.3, 0.0), r])
	for k in _rng.randi_range(2, 4):
		var r := r0 * _rng.randf_range(0.45, 0.8)
		puffs.append([Vector3(_rng.randf_range(-0.45, 0.45) * length * 0.5, r0 * _rng.randf_range(0.7, 1.0), _rng.randf_range(-0.25, 0.25) * r0), r])
	var top := 0.0
	for p in puffs:
		top = maxf(top, p[0].y + p[1])
	if base + top > CUMULUS_CEILING:
		var k := (CUMULUS_CEILING - base) / top
		for p in puffs:
			p[0] *= k
			p[1] *= k
		top *= k
		r0 *= k
	var top_h: float = LOW_LAYERS[li][1]
	var h := _rng.randf_range(base, maxf(base, top_h - top))
	var lim := StationGeo.HALF_LEN - END_CLEAR - r0 - 20.0
	var x := _rng.randf_range(-lim, lim)
	var s := _rng.randf() * StationGeo.CIRC
	if _rng.randf() < 0.55:                                  # (the sky at launch: over half of them in the fronts)
		var f: Dictionary = _fronts[_rng.randi() % _fronts.size()]
		s = _front_s(f, x, h) + _rng.randfn(0.0, f.half * 0.6)
	return _new_cloud(li, puffs, fposmod(s, StationGeo.CIRC), x, h, 0)


func _place(c: Dictionary) -> void:
	var b := StationGeo.basis(c.s, PI * 0.5)
	if c.kind > 0:
		b = Basis(Vector3.RIGHT, CELL_LEAN) * b              # (about the axis: its top goes antispinward)
	if c.scale != 1.0:
		b = b.scaled(Vector3.ONE * float(c.scale))
	(c.node as Node3D).transform = Transform3D(b, StationGeo.point(c.s, c.x, c.h))


const BLEND := 3.0                   # m: how softly neighbouring puffs merge (small: the bulges stay)
const BASE_BLEND := 3.0              # m: the rounding where the sides meet the flat base


static func _field(p: Vector3, puffs: Array) -> float:
	## Signed distance (roughly) to the cloud: the puffs' smooth union, cut flat at y = 0.
	var d := 1.0e9
	for pf in puffs:
		var e: float = p.distance_to(pf[0]) - pf[1]
		var h := clampf(0.5 + 0.5 * (e - d) / BLEND, 0.0, 1.0)      # polynomial smooth min
		d = lerpf(e, d, h) - BLEND * h * (1.0 - h)
	var b := -p.y
	var h2 := clampf(0.5 - 0.5 * (b - d) / BASE_BLEND, 0.0, 1.0)     # smooth max with the base
	return lerpf(b, d, h2) + BASE_BLEND * h2 * (1.0 - h2)


static func _skin(puffs: Array, rings := 22, segs := 40) -> Array:
	## The cloud's surface arrays: a sphere of rays from inside the cloud, each sphere-traced in
	## from outside to the field's outermost zero; normals from the field's gradient.
	var c := Vector3.ZERO
	var reach := 0.0
	for pf in puffs:
		c += pf[0]
	c /= puffs.size()
	c.y = 3.0
	for pf in puffs:
		reach = maxf(reach, c.distance_to(pf[0]) + pf[1] + 4.0)
	var grid := []
	for a in rings + 1:
		var row := []
		var th := PI * a / rings
		for b in segs + 1:
			var ph := TAU * b / segs
			var dir := Vector3(sin(th) * cos(ph), cos(th), sin(th) * sin(ph))
			var t := reach
			for it in 60:
				var d := _field(c + dir * t, puffs)
				if d < 0.05:
					break
				t -= maxf(d, 0.2)
				if t <= 0.5:
					t = 0.5
					break
			var v := c + dir * t
			var e := 0.4
			var n := Vector3(_field(v + Vector3(e, 0, 0), puffs) - _field(v - Vector3(e, 0, 0), puffs),
				_field(v + Vector3(0, e, 0), puffs) - _field(v - Vector3(0, e, 0), puffs),
				_field(v + Vector3(0, 0, e), puffs) - _field(v - Vector3(0, 0, e), puffs)).normalized()
			row.append([v, n])
		grid.append(row)
	var verts := PackedVector3Array()
	var norms := PackedVector3Array()
	for a in rings:
		for b in segs:
			var q := [grid[a][b], grid[a + 1][b], grid[a + 1][b + 1], grid[a][b + 1]]
			for k in [0, 2, 1, 0, 3, 2]:
				verts.append(q[k][0])
				norms.append(q[k][1])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = norms
	return arrays


func _make_skins(all_puffs: Array) -> void:
	var out := []
	for puffs in all_puffs:
		out.append(_skin(puffs))
	_skins = out


func _skin_job(job: Dictionary) -> void:
	## (a holder of its own: the worker never touches a cloud the main thread is moving)
	job["skin"] = _skin(job.puffs, 44, 88)          # a storm cell is big: a finer skin


# ------------------------------------------------------------------ high cirrus
func _make_cirrus_band(row: int, layer: Node3D, height: float, size: float) -> void:
	## One band of a shell along the axis: CIRRUS_COLS ribbons round it, each on the cylinder
	## `height` up -- its span round the axis, its width along it -- in one mesh (UV2.x: the
	## ribbon's seed for the shader's wisps).
	var r := StationGeo.R - height
	var band := (StationGeo.LENGTH - 2.0 * END_CLEAR) / CIRRUS_ROWS
	var x0 := -StationGeo.HALF_LEN + END_CLEAR + band * row
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var n := 24
	for col in CIRRUS_COLS:
		var span := minf(_rng.randf_range(0.45, 1.2) * size, 3.0)   # radians round the axis
		var th0 := TAU * (col + _rng.randf_range(0.15, 0.85)) / CIRRUS_COLS + row * 0.37
		var width := minf(_rng.randf_range(25.0, 60.0) * size, band * 0.9)
		var skew := _rng.randf_range(-0.3, 0.3) * width    # wisps lie a little aslant the wind
		var xc := x0 + width * 0.5 + absf(skew) * 0.5 + _rng.randf() * maxf(0.0, band - width - absf(skew))
		var seed := _rng.randf() * 50.0
		for k in n:
			for tri in [[0, 0], [1, 1], [1, 0], [0, 0], [0, 1], [1, 1]]:
				var u: float = (k + tri[0]) / float(n)
				var v: float = tri[1]
				var th: float = th0 + span * (u - 0.5)
				st.set_normal(Vector3(0.0, cos(th), sin(th)))  # toward the floor below it
				st.set_uv(Vector2(u, v))
				st.set_uv2(Vector2(seed, 0.0))
				st.add_vertex(Vector3(xc + (v - 0.5) * width + skew * (u - 0.5), r * cos(th), r * sin(th)))
	var mi := MeshInstance3D.new()
	mi.name = "cirrus_%d_%d" % [roundi(height), row]
	mi.mesh = st.commit()
	mi.material_override = _cirrus_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	layer.add_child(mi)


# ------------------------------------------------------------------ the weather
func is_day() -> bool:
	if sky == null:
		return true
	return sky.time_of_day >= DaySkySystem.DAY_START and sky.time_of_day < DaySkySystem.DAY_END


func storms() -> Array:
	## For RemakeRain: every storm now -- {s, x, base (cloud base height), fa / fb (the footprint under
	## the cloud: half-length along s, half-width along x -- the rain falls only there), radius
	## (the larger), intensity 0..1, thunder, id}.
	var out := []
	for c in _low:
		if c.state == "free" and c.kind > 0 and not c.storm.is_empty():
			out.append({"s": c.s, "x": c.x, "base": c.h, "radius": maxf(c.fa, c.fb), "fa": c.fa, "fb": c.fb,
				"intensity": c.storm.intensity,
				"thunder": c.kind == 2, "id": str(c.node.name)})
	return out


static func _ds(a: float, b: float) -> float:
	return StationGeo.wrap_ds(b - a)


func _hdist(a: Dictionary, b: Dictionary) -> float:
	return Vector2(_ds(a.s, b.s), b.x - a.x).length()


func _drift(c: Dictionary, dt: float) -> void:
	var li: int = c.layer
	# the wander north and south: a slow random walk, turned back at the end caps
	c.vx = clampf(c.vx + _wx.randf_range(-0.9, 0.9) * dt, -DRIFT_NS, DRIFT_NS)
	var lim: float = StationGeo.HALF_LEN - END_CLEAR - c.foot
	if c.x > lim and c.vx > 0.0 or c.x < -lim and c.vx < 0.0:
		c.vx = -c.vx
	# the lowest layer's clouds now and then swing round to run west to east (or back)
	if li == 0 and _wx.randf() < dt / 900.0:
		c.vs = -c.vs
	# Coriolis: riding the east wind (antispinward) it weighs less and sits higher; running spinward, lower
	if c.kind == 0:
		c.h = move_toward(c.h, float(c.h0) - CORIOLIS_LIFT * float(c.vs), 1.5 * dt)
	var k: float = StationGeo.R / (StationGeo.R - c.h)       # m/s at its height -> s units on the floor
	c.s = fposmod(c.s + c.vs * k * dt, StationGeo.CIRC)
	c.x = clampf(c.x + c.vx * dt, -lim, lim)


func _storm_count() -> int:
	var n := 0
	for c in _low:
		if c.kind > 0 and c.state != "hidden" or c.state == "merging" and c.get("merge_kind", 0) == 1:
			n += 1
	return n


func _merge_kind(a: Dictionary, b: Dictionary) -> int:
	## What a merge of a and b would make (1 cell, 2 supercell), or 0 if they can't merge now.
	if a.kind == 0 and b.kind == 0:
		if a.fade != 0 or b.fade != 0 or _storm_count() >= MAX_STORMS:
			return 0
		if not is_day() and weather_at(a.s, a.x, a.h) < 0.4:       # (out of a front, only the sun's heat builds a storm)
			return 0
		return 1
	if a.kind == 1 and b.kind == 1 and not a.storm.get("breaking", false) and not b.storm.get("breaking", false):
		return 2
	return 0


const TRIG_BIN := 3000.0              # m round the ring: no two clouds further apart can touch


func _triggers(dh: float) -> void:
	## Clouds at a merge trigger: touching (same layer) or one above the other (different layers).
	## Each trigger is rolled once, when the two first reach it.  (Binned round the ring: the 20 km
	## ring's 100 clouds pair by pair were ~5,000 checks.)
	var nb := int(StationGeo.CIRC / TRIG_BIN)
	var bins := {}
	for c in _low:
		if c.state == "free":
			var bk := int(c.s / TRIG_BIN) % nb
			if not bins.has(bk):
				bins[bk] = []
			bins[bk].append(c)
	var seen := {}
	for k in bins:
		var here: Array = bins[k]
		var next: Array = bins.get((k + 1) % nb, [])
		for i in here.size():
			for j in range(i + 1, here.size() + next.size()):
				var a: Dictionary = here[i]
				var b: Dictionary = here[j] if j < here.size() else next[j - here.size()]
				var d := _hdist(a, b)
				var hit: bool = d < (a.foot + b.foot) if a.layer == b.layer else d < maxf(a.foot, b.foot) * 0.5
				if not hit:
					continue
				var key := Vector2i(mini(a.uid, b.uid), maxi(a.uid, b.uid))
				seen[key] = true
				if _contacts.has(key):
					continue
				var kind := _merge_kind(a, b)
				var cover := weather_at(a.s, a.x, a.h)
				if kind > 0 and _wx.randf() < lerpf(MERGE_CHANCE, FRONT_MERGE_CHANCE, cover):
					_pair(a, b, kind)
	_contacts = seen
	# a front's core starts cells of its own: a cloud there pulls in its nearest neighbour -- and a cell
	# there grows into a thunderstorm the same way (two cells are seldom near enough along a front)
	for c in _low:
		if c.state != "free" or c.kind > 1 or c.fade != 0 or c.storm.get("breaking", false):
			continue
		var cover := weather_at(c.s, c.x, c.h)
		if cover < 0.55 or _wx.randf() >= CELL_RATE * dh * cover * (1.0 if c.kind == 0 else 2.0):
			continue
		if c.kind == 0 and _storm_count() >= MAX_STORMS:
			continue
		var best: Dictionary = {}
		var bd := 3000.0
		for o in _low:
			if o.uid != c.uid and o.state == "free" and o.kind == 0 and o.fade == 0 \
					and not o.storm.get("breaking", false) and absi(o.layer - c.layer) <= 1:
				var d := _hdist(c, o)
				if d < bd:
					bd = d
					best = o
		if not best.is_empty():
			_pair(c, best, c.kind + 1)


func _pair(a: Dictionary, b: Dictionary, kind: int) -> void:
	a.state = "merging"
	b.state = "merging"
	a.partner = b
	b.partner = a
	a["merge_kind"] = kind
	b["merge_kind"] = kind


func _merging(a: Dictionary, dt: float) -> void:
	## Two merging clouds close on each other (the upper one sinking to the lower one's height);
	## once together they become one.
	var b: Dictionary = a.partner
	var low_h := minf(a.h, b.h)
	for c in [a, b]:
		c.h = move_toward(c.h, low_h, SINK_SPEED * dt)
	var mid_s := fposmod(a.s + _ds(a.s, b.s) * 0.5, StationGeo.CIRC)
	var mid_x: float = (a.x + b.x) * 0.5
	for c in [a, b]:
		var to := Vector2(_ds(c.s, mid_s), mid_x - c.x)
		if to.length() > 0.01:
			var mv := to.normalized() * minf(to.length(), MERGE_SPEED * dt)
			c.s = fposmod(c.s + mv.x, StationGeo.CIRC)
			c.x += mv.y
	if _hdist(a, b) < 20.0 and absf(a.h - b.h) < 1.0:
		_combine(a, b)


func _combine(a: Dictionary, b: Dictionary) -> void:
	## One cloud from two: their puffs side by side along the wind, on the lower one's layer.
	var kind: int = a.merge_kind
	var lower: Dictionary = a if a.layer <= b.layer else b
	var la := 0.0
	var lb := 0.0
	for p in a.puffs:
		la = maxf(la, absf(p[0].x) + p[1])
	for p in b.puffs:
		lb = maxf(lb, absf(p[0].x) + p[1])
	var d := 0.35 * minf(la, lb)
	var puffs := []
	for p in a.puffs:
		puffs.append([p[0] - Vector3(d, 0, 0), p[1]])
	for p in b.puffs:
		puffs.append([p[0] + Vector3(d, 0, 0), p[1]])
	var c := _new_cloud(lower.layer, puffs, lower.s, lower.x, minf(a.h, b.h), kind)
	c.vs = lower.vs * 0.8
	var f := _front_at(c.s, c.x, c.h)
	if not f.is_empty() and weather_at(c.s, c.x, c.h) > 0.3:
		c.vs = -float(f.speed) * (StationGeo.R - c.h) / StationGeo.R      # (a front's cell moves with the front)
	c.members = [a, b]
	for m in [a, b]:
		m.state = "hidden"
		m.partner = null
	c.storm = {"kind": "thunder" if kind == 2 else "rain", "start": _hours, "intensity": 0.0, "breaking": false}
	c.state = "forming"                      # shown once its skin is built
	_low.append(c)
	var holder := {"puffs": puffs.duplicate(true)}
	_jobs.append([WorkerThreadPool.add_task(_skin_job.bind(holder), false, "merged cloud skin"), c, holder])


func _breakup(c: Dictionary) -> void:
	## A storm's end: the cell splits back into the clouds it was made of, which drift apart.
	var parts := []
	for m in c.members:
		if m.kind > 0:                      # a supercell's cells: back to their own clouds
			for mm in m.members:
				parts.append(mm)
			_low.erase(m)
			(m.node as Node3D).queue_free()
		else:
			parts.append(m)
	for i in parts.size():
		var m: Dictionary = parts[i]
		var off: float = (i - (parts.size() - 1) * 0.5) * 2.0 * c.foot / maxf(1.0, parts.size())
		var lim: float = StationGeo.HALF_LEN - END_CLEAR - m.foot
		m.s = c.s
		m.x = clampf(c.x + off, -lim, lim)
		m.h = maxf(m.h, LOW_LAYERS[m.layer][0])
		m.vx = DRIFT_NS * (1.0 if off >= 0.0 else -1.0)
		m.state = "free"
		m.scale = 1.0
		m.fade = 0
		m.storm = {}
		(m.node as Node3D).visible = true
		_place(m)
	_low.erase(c)
	(c.node as Node3D).queue_free()


func _storm_step(c: Dictionary, dh: float) -> void:
	var st: Dictionary = c.storm
	var life := THUNDER_HOURS if st.kind == "thunder" else RAIN_HOURS
	var age: float = _hours - st.start
	if age < life:
		st.intensity = minf(1.0, st.intensity + dh / 0.25)      # the rain builds over a quarter hour
	else:
		st.breaking = true
		st.intensity = clampf(1.0 - (age - life) / BREAKUP_HOURS, 0.0, 1.0)
		if age >= life + BREAKUP_HOURS:
			_breakup(c)


func _process(delta: float) -> void:
	if _skin_task >= 0 and WorkerThreadPool.is_task_completed(_skin_task):
		WorkerThreadPool.wait_for_task_completion(_skin_task)
		_skin_task = -1
		for i in _skins.size():
			var mesh := ArrayMesh.new()
			mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _skins[i])
			(_low[i].mesh as MeshInstance3D).mesh = mesh
		_skins = []
	# merged clouds whose skins are ready replace their parts
	for job in _jobs.duplicate():
		if WorkerThreadPool.is_task_completed(job[0]):
			WorkerThreadPool.wait_for_task_completion(job[0])
			_jobs.erase(job)
			var c: Dictionary = job[1]
			var mesh := ArrayMesh.new()
			mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, job[2].skin)
			(c.mesh as MeshInstance3D).mesh = mesh
			c.state = "free"
			for m in c.members:
				(m.node as Node3D).visible = false
	var dt := minf(delta, 0.1)
	var dh := dt / DaySkySystem.DAY_LENGTH_SECONDS * 24.0          # in-game hours this frame
	_hours += dh
	_fronts_step(dt, dh)
	_life_step(dt)
	for c in _low.duplicate():
		if not _low.has(c):
			continue
		match c.state:
			"free":
				_drift(c, dt)
				if not c.storm.is_empty():
					_storm_step(c, dh)
			"merging":
				if c.partner != null and _low.find(c) < _low.find(c.partner):
					_merging(c, dt)
			"forming":
				_drift(c, dt)
		if _low.has(c) and c.state != "hidden":
			_place(c)
	if _debug_super:
		if _debug_cells.size() == 2 and _debug_cells[0].state == "free" and _debug_cells[1].state == "free":
			_debug_super = false
			_combine_now(_debug_cells[0], _debug_cells[1], 2)
	# (merge triggers 4 times a second: every pair every frame was ~5 ms with the 20 km ring's 60 clouds; they close
	#  at a few m/s, so a trigger is never missed)
	_trig_t -= dt
	if _trig_t <= 0.0:
		_trig_t = 0.25
		_triggers(0.25 / DaySkySystem.DAY_LENGTH_SECONDS * 24.0)
	for L in _high_layers:
		var lay: Node3D = L[0]
		lay.rotation.x = fposmod(lay.rotation.x + float(L[1]) * dt, TAU)
	_whiteout()


# ------------------------------------------------------------------ the fronts
func _new_front(rng: RandomNumberGenerator, s: float) -> Dictionary:
	var f := {"s": fposmod(s, StationGeo.CIRC), "speed": rng.randf_range(FRONT_SPEED.x, FRONT_SPEED.y),
		"half": rng.randf_range(FRONT_HALF.x, FRONT_HALF.y), "amp": rng.randf_range(FRONT_WAVE.x, FRONT_WAVE.y),
		"wl": rng.randf_range(FRONT_WAVELEN.x, FRONT_WAVELEN.y), "ph": rng.randf() * TAU,
		"born": _hours, "life": rng.randf_range(FRONT_LIFE.x, FRONT_LIFE.y), "strength": 0.0}
	f["sheet"] = _front_sheet(f, rng)
	_fronts.append(f)
	return f


func _front_s(f: Dictionary, x: float, h: float) -> float:
	## Where front f's centre is round the ring at x, h up: its wave, its top leaning antispinward.
	return f.s + f.amp * sin(TAU * x / f.wl + f.ph) - LEAN_K * h


func _front_at(s: float, x: float, h: float = 0.0) -> Dictionary:
	## The front that covers (s, x, h) most ({} none).
	var best := {}
	var bv := 0.0
	for f in _fronts:
		var d: float = StationGeo.wrap_ds(s - _front_s(f, x, h)) / f.half
		var v: float = f.strength * exp(-d * d)
		if v > bv:
			bv = v
			best = f
	return best


func weather_at(s: float, x: float, h: float = 0.0) -> float:
	## How deep in a front (s, x) is, h up: 0 fair weather, 1 a full front's core.
	var v := 0.0
	for f in _fronts:
		var d: float = StationGeo.wrap_ds(s - _front_s(f, x, h)) / f.half
		v = maxf(v, f.strength * exp(-d * d))
	return v


func drizzle_at(s: float, x: float) -> float:
	## The drizzle out of a front's sheet at (s, x) on the floor, 0..~0.25 (RemakeRain).
	return 0.25 * smoothstep(0.7, 0.95, weather_at(s, x, SHEET_H))


func fronts() -> Array:
	## For the HUD, the PDA and tests: [{s (its centre on the floor at x 0), speed (m/s west), half, strength}]
	var out := []
	for f in _fronts:
		out.append({"s": fposmod(_front_s(f, 0.0, 0.0), StationGeo.CIRC), "speed": f.speed, "half": f.half,
			"strength": f.strength})
	return out


func _fronts_step(dt: float, dh: float) -> void:
	for f in _fronts.duplicate():
		f.s = fposmod(f.s - float(f.speed) * dt, StationGeo.CIRC)
		var age: float = _hours - f.born
		f.strength = minf(smoothstep(0.0, FRONT_RAMP, age), 1.0 - smoothstep(f.life - FRONT_FADE, f.life, age))
		var sheet: MeshInstance3D = f.sheet
		sheet.rotation.x = (f.s - LEAN_K * SHEET_H) / StationGeo.R
		sheet.set_instance_shader_parameter("fade", f.strength)
		if age >= f.life:
			sheet.queue_free()
			_fronts.erase(f)
			_front_gap = _wx.randf_range(FRONT_GAP.x, FRONT_GAP.y)
	_front_gap -= dh
	if _fronts.size() < FRONTS and _front_gap <= 0.0:
		# a new one where the ring is clearest: the most room from the others
		var best_s := 0.0
		var best_d := -1.0
		for k in 12:
			var s := _wx.randf() * StationGeo.CIRC
			var d := StationGeo.CIRC
			for f in _fronts:
				d = minf(d, absf(StationGeo.wrap_ds(s - float(f.s))))
			if d > best_d:
				best_d = d
				best_s = s
		_new_front(_wx, best_s)
		_front_gap = _wx.randf_range(FRONT_GAP.x, FRONT_GAP.y)


func _front_sheet(f: Dictionary, rng: RandomNumberGenerator) -> MeshInstance3D:
	## The front's altostratus: a grey veil SHEET_H up, end cap to end cap, as wide as the front and
	## waving with it -- turned round the axis to follow it (_fronts_step).  Streaked along the axis
	## (the cirrus shader's fibres run along UV.x).
	var r := StationGeo.R - SHEET_H
	var nx := 48
	var ns := 10
	var w: float = f.half * 1.7
	var seed := rng.randf() * 50.0
	var x0 := -StationGeo.HALF_LEN + END_CLEAR
	var x1 := StationGeo.HALF_LEN - END_CLEAR
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in nx:
		for j in ns:
			for tri in [[0, 0], [1, 1], [1, 0], [0, 0], [0, 1], [1, 1]]:
				var u: float = (i + tri[0]) / float(nx)
				var v: float = (j + tri[1]) / float(ns)
				var x := lerpf(x0, x1, u)
				var th: float = (f.amp * sin(TAU * x / f.wl + f.ph) + (v - 0.5) * 2.0 * w) / StationGeo.R
				st.set_normal(Vector3(0.0, cos(th), sin(th)))
				st.set_uv(Vector2(u, v))
				st.set_uv2(Vector2(seed, 0.0))
				st.add_vertex(Vector3(x, r * cos(th), r * sin(th)))
	var mi := MeshInstance3D.new()
	mi.name = "front_sheet"
	mi.mesh = st.commit()
	mi.material_override = _sheet_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.set_instance_shader_parameter("fade", 0.0)
	add_child(mi)
	return mi


func _life_step(dt: float) -> void:
	## Clouds thinning away out of the fronts and forming again (mostly in one), and shading darker in
	## them: a few clouds a frame looked at, every cloud growing or thinning every frame.
	var n := _low.size()
	for k in mini(4, n):
		_check_i = (_check_i + 1) % n
		var c: Dictionary = _low[_check_i]
		if c.state != "free" or c.kind != 0:
			continue
		var cover := weather_at(c.s, c.x, c.h)
		c.shade = smoothstep(0.15, 0.9, cover) * 0.7
		(c.mesh as MeshInstance3D).set_instance_shader_parameter("shade", c.shade)
		# (n / 4 frames between looks at one cloud: the chance per look keeps THIN_EVERY seconds out of the fronts)
		if c.fade == 0 and _wx.randf() < (1.0 - smoothstep(0.05, 0.4, cover)) * dt * n / 4.0 / THIN_EVERY:
			c.fade = -1
	for c in _low:
		if c.fade == 0 or c.state != "free":
			continue
		c.scale = clampf(c.scale + c.fade * dt / FADE_SECONDS, 0.05, 1.0)
		if c.fade < 0 and c.scale <= 0.05:
			_reform(c)
		elif c.fade > 0 and c.scale >= 1.0:
			c.fade = 0
		var vis: bool = c.scale > 0.06
		if (c.node as Node3D).visible != vis:
			(c.node as Node3D).visible = vis
			(c.area as Area3D).set_deferred("monitoring", vis)


func _reform(c: Dictionary) -> void:
	## A cloud that thinned away forms again: in a front (FRONT_RESEED of the time, on its trailing side
	## -- the wind carries it through), or anywhere.
	var lim: float = StationGeo.HALF_LEN - END_CLEAR - c.foot
	var x := _wx.randf_range(-lim, lim)
	var s := _wx.randf() * StationGeo.CIRC
	var tot := 0.0
	for f in _fronts:
		tot += f.strength
	if tot > 0.2 and _wx.randf() < FRONT_RESEED:
		var pick := _wx.randf() * tot
		for f in _fronts:
			pick -= f.strength
			if pick <= 0.0:
				s = _front_s(f, x, c.h) + f.half * 0.4 + _wx.randfn(0.0, f.half * 0.6)
				break
	c.s = fposmod(s, StationGeo.CIRC)
	c.x = x
	c.fade = 1


func inside(p: Vector3) -> float:
	## How deep p is inside a low cloud: 0 outside, 1 at a puff's centre.
	var best := 0.0
	for c in _low:
		if c.state == "hidden" or c.scale < 0.3:
			continue
		var node: Node3D = c.node
		var t := node.global_transform
		if p.distance_to(t.origin) > c.reach + 60.0:
			continue
		var lp := t.affine_inverse() * p
		if lp.y < 0.0:
			continue
		for pf in c.puffs:
			best = maxf(best, 1.0 - lp.distance_to(pf[0]) / pf[1])
	return best


func _whiteout() -> void:
	if env == null or target == null:
		return
	var d := inside(target.global_position)
	if d > 0.0:
		env.fog_enabled = true
		env.fog_light_color = Color(0.9, 0.92, 0.95)
		env.fog_light_energy = lerpf(0.08, 1.0, sky.daylight()) if sky else 1.0   # (fog doesn't glow white at night)
		env.fog_sky_affect = 1.0
		env.fog_density = 0.03 + 0.25 * d
		_fogged = true
	elif _fogged:
		env.fog_enabled = false
		_fogged = false


func debug_storm(s: float, x: float, thunder := false) -> void:
	## For testing: bring plain clouds over (s, x) and merge them straight away -- two for a
	## rainstorm, four (two cells merged) for a thunderstorm.  Ignores the day / storm limits.
	var picks := []
	for c in _low:
		if c.state == "free" and c.kind == 0 and c.layer <= 1 and c.fade == 0:
			picks.append(c)
		if picks.size() == (4 if thunder else 2):
			break
	if picks.size() < 2:
		return
	for i in picks.size():
		picks[i].s = s + (i % 2) * 30.0
		picks[i].x = x
		picks[i].h = LOW_LAYERS[0][0]
	_combine_now(picks[0], picks[1], 1)
	_debug_cells = [_low[-1]]
	if thunder and picks.size() == 4:
		_combine_now(picks[2], picks[3], 1)
		_debug_cells.append(_low[-1])
		_debug_super = true


var _debug_super := false
var _debug_cells: Array = []


func _combine_now(a: Dictionary, b: Dictionary, kind: int) -> void:
	a.partner = b
	b.partner = a
	a["merge_kind"] = kind
	b["merge_kind"] = kind
	_combine(a, b)


func _exit_tree() -> void:
	if _skin_task >= 0:
		WorkerThreadPool.wait_for_task_completion(_skin_task)
	for job in _jobs:
		WorkerThreadPool.wait_for_task_completion(job[0])
