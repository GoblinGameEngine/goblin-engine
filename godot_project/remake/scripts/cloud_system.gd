extends Node3D
class_name RemakeClouds

## The station's weather: two sparse cloud layers drifting west to east -- round the axis, the way
## the air turns with the station (north is the Marlowe end cap, -x; east is +s, see
## RemakeStation.compass_bearing).  Each layer is one node turned about the axis, so the clouds
## simply come round again.
##
##   Low cumulus, LOW_BASE..LOW_TOP m up: a few puffs blended into one smooth cartoon skin (a
##   smooth-union distance field, shrink-wrapped by a sphere of rays -- no facets, no seams
##   where puffs meet) with a flat base, opaque and cel-shaded (cumulus.gdshader) so the outline
##   pass inks only the silhouette.  The skins are generated on a worker thread at startup.  Each is also a WaterVolume --
##   the same trigger the lake uses -- so whatever flies or falls into one gets enter_water() /
##   exit_water() and treats it as water; the camera inside one whites out (fog by depth).
##
##   High cirrus, CIRRUS_H m up (50 m off the central shaft): a sparse shell of flat translucent
##   ribbons wrapped round the axis, the way the spinning air carries them (cirrus.gdshader),
##   drifting very slowly -- one jittered ribbon per slot of a band x slot grid, so they spread
##   evenly without clumping, merged into one mesh per band.
##
## Positions are a fixed-seed hash, so the same sky comes back every launch.

const LOW_COUNT := 34
const LOW_BASE := 200.0
const LOW_TOP := 300.0
const LOW_WIND := 4.0                # m/s east, at the layer's middle
const CIRRUS_ROWS := 10              # the cirrus shell: bands along the axis ...
const CIRRUS_COLS := 6               # ... by slots round it, one jittered ribbon each
const CIRRUS_H := 400.0              # 100 m from the axis, 50 m off the shaft
const CIRRUS_WIND := 0.6
const END_CLEAR := 40.0              # m kept between a cloud and an end cap
const SEED := 20260924

var target: Node3D                   # the camera the inside-a-cloud whiteout follows
var env: Environment
var _low: Array = []                 # {node, reach, puffs: [[Vector3 local, r]]}
var _low_layer: Node3D               # turned about the axis: the low clouds' drift
var _high_layer: Node3D
var _cumulus_mat: ShaderMaterial
var _cirrus_mat: ShaderMaterial
var _rng := RandomNumberGenerator.new()
var _fogged := false
var _skin_task := -1
var _skins: Array = []               # the worker's output: one mesh arrays per low cloud


func setup(p_target: Node3D, p_env: Environment) -> void:
	target = p_target
	env = p_env
	_rng.seed = SEED
	_cumulus_mat = ShaderMaterial.new()
	_cumulus_mat.shader = load("res://remake/shaders/cumulus.gdshader")
	_cirrus_mat = ShaderMaterial.new()
	_cirrus_mat.shader = load("res://remake/shaders/cirrus.gdshader")
	_low_layer = Node3D.new()
	_low_layer.name = "Cumulus"
	add_child(_low_layer)
	_high_layer = Node3D.new()
	_high_layer.name = "Cirrus"
	add_child(_high_layer)
	for i in LOW_COUNT:
		_low.append(_make_cumulus(i))
	for row in CIRRUS_ROWS:
		_make_cirrus_band(row)
	var all_puffs := []
	for c in _low:
		all_puffs.append(c.puffs)
	_skin_task = WorkerThreadPool.add_task(_make_skins.bind(all_puffs), false, "cloud skins")
	set_process(true)


# ------------------------------------------------------------------ low cumulus
func _make_cumulus(i: int) -> Dictionary:
	# simple on purpose: a row of 2-4 big puffs along its length (local x, turned to run with the
	# wind round the ring) and a few smaller heads on top, all pressed flat underneath
	var length := _rng.randf_range(45.0, 110.0)
	var puffs := []
	var n_base := clampi(roundi(length / 30.0), 2, 4)
	var r0 := length / (n_base + 1.0)
	for k in n_base:
		var r := r0 * _rng.randf_range(0.85, 1.15)
		var px := (k - (n_base - 1) * 0.5) * r0 * 1.1
		puffs.append([Vector3(px, r * 0.3, 0.0), r])
	# the crown: a few rounder heads of mixed size heaped along the top
	for k in _rng.randi_range(2, 4):
		var r := r0 * _rng.randf_range(0.45, 0.8)
		puffs.append([Vector3(_rng.randf_range(-0.45, 0.45) * length * 0.5, r0 * _rng.randf_range(0.7, 1.0), _rng.randf_range(-0.25, 0.25) * r0), r])
	var width := r0 * 2.0
	var node := Node3D.new()
	node.name = "cumulus_%d" % i
	_low_layer.add_child(node)
	var mi := MeshInstance3D.new()                         # its mesh comes from the worker (_make_skins)
	mi.material_override = _cumulus_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	node.add_child(mi)
	var area := WaterVolume.new()
	area.name = "volume"
	for p in puffs:
		var cs := CollisionShape3D.new()
		var sph := SphereShape3D.new()
		sph.radius = p[1]
		cs.shape = sph
		cs.position = p[0]
		area.add_child(cs)
	node.add_child(area)
	var top := 0.0
	for p in puffs:
		top = maxf(top, p[0].y + p[1])
	var half_w := width * 0.5 + 20.0                          # its extent along the axis
	var sp := _rng.randf() * StationGeo.CIRC
	var h := _rng.randf_range(LOW_BASE, maxf(LOW_BASE, LOW_TOP - top))
	var lim := StationGeo.HALF_LEN - END_CLEAR - half_w
	node.transform = Transform3D(StationGeo.basis(sp, PI * 0.5), StationGeo.point(sp, _rng.randf_range(-lim, lim), h))
	return {"node": node, "mesh": mi, "puffs": puffs, "reach": maxf(length * 0.5, width * 0.5) + 25.0}


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


static func _skin(puffs: Array) -> Array:
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
	var rings := 22
	var segs := 40
	var grid := []
	for a in rings + 1:
		var row := []
		var th := PI * a / rings
		for b in segs + 1:
			var ph := TAU * b / segs
			var dir := Vector3(sin(th) * cos(ph), cos(th), sin(th) * sin(ph))
			var t := reach
			for it in 40:
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


# ------------------------------------------------------------------ high cirrus
func _make_cirrus_band(row: int) -> void:
	## One band of the shell along the axis: CIRRUS_COLS ribbons round it, each on the cylinder
	## CIRRUS_H up -- its span round the axis, its width along it -- in one mesh (UV2.x: the
	## ribbon's seed for the shader's wisps).
	var r := StationGeo.R - CIRRUS_H
	var band := (StationGeo.LENGTH - 2.0 * END_CLEAR) / CIRRUS_ROWS
	var x0 := -StationGeo.HALF_LEN + END_CLEAR + band * row
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var n := 24
	for col in CIRRUS_COLS:
		var span := _rng.randf_range(0.45, 1.2)             # radians: 45-120 m of arc
		var th0 := TAU * (col + _rng.randf_range(0.15, 0.85)) / CIRRUS_COLS + row * 0.37
		var width := _rng.randf_range(25.0, 60.0)
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
	mi.name = "cirrus_%d" % row
	mi.mesh = st.commit()
	mi.material_override = _cirrus_mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_high_layer.add_child(mi)


func _process(delta: float) -> void:
	if _skin_task >= 0 and WorkerThreadPool.is_task_completed(_skin_task):
		WorkerThreadPool.wait_for_task_completion(_skin_task)
		_skin_task = -1
		for i in _low.size():
			var mesh := ArrayMesh.new()
			mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, _skins[i])
			(_low[i].mesh as MeshInstance3D).mesh = mesh
		_skins = []
	# east is +s: a turn about +x (y toward z) at each layer's wind over its radius
	var dt := minf(delta, 0.1)
	_low_layer.rotation.x = fposmod(_low_layer.rotation.x + LOW_WIND / (StationGeo.R - (LOW_BASE + LOW_TOP) * 0.5) * dt, TAU)
	_high_layer.rotation.x = fposmod(_high_layer.rotation.x + CIRRUS_WIND / (StationGeo.R - CIRRUS_H) * dt, TAU)
	_whiteout()


func inside(p: Vector3) -> float:
	## How deep p is inside a low cloud: 0 outside, 1 at a puff's centre.
	var best := 0.0
	for c in _low:
		var node: Node3D = c.node
		var t := node.global_transform
		if absf(p.x - t.origin.x) > c.reach or p.distance_to(t.origin) > c.reach + 60.0:
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
		env.fog_light_energy = 1.0
		env.fog_sky_affect = 1.0
		env.fog_density = 0.03 + 0.25 * d
		_fogged = true
	elif _fogged:
		env.fog_enabled = false
		_fogged = false


func _exit_tree() -> void:
	if _skin_task >= 0:
		WorkerThreadPool.wait_for_task_completion(_skin_task)
