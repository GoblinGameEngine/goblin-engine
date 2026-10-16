extends Node
class_name LightField

## The night air's own light (the user, 2026-10-16: "At night there needs to be pools of light from the light sources
## that spill over carried by the air to provide ambient illumination. This illumination will cumulatively fade as
## the player gains distance from the light sources").  Cheap, for the Deck: no per-source lights.
##   * the floor: every street lamp, festoon string and walk lamp (StreetLights' data) splatted into a 64 m grid over
##     the whole map (s, x) and blurred twice (~200 m reach), once, on a worker; sampled at the camera
##   * the sky islands: the warren's own lights (its twin json "lights") within REACH of the camera, every half second
##   -> `glow` (0..1, eased): how lit the air is where the view is.  DaySkySystem lifts the night ambient by it and warms
##      it, and tints the fog toward lamplight, so a town's streets and walls are lit softly by the air and it all fades
##      away as you walk out into the dark.  The lamps' own pools stay as they are.

const CELL := 64.0
const DENSE := 9.0                   # blurred lamps a cell for glow ~0.63 (a lit town street)
const REACH := 70.0                  # m: island lights counted round the camera
const ISLAND_DENSE := 40.0           # ... this many for ~0.63
const BLUR := 2                      # box-blur passes of radius 2 cells

static var glow := 0.0               # (read by DaySkySystem)
static var enabled := true           # (dev: false for a before/after)
var station: Node
var _grid := PackedFloat32Array()
var _ns := 0
var _nx := 0
var _task := -1
var _t := 0.0
var _isl := 0.0
var _floor := 0.0


func _ready() -> void:
	name = "LightField"


var _lights: Node


func build(lights: Node) -> void:
	## the floor's grid, on a worker, once StreetLights has its data
	_lights = lights


func _build(lights: Node) -> void:
	_ns = ceili(StationGeo.CIRC / CELL)
	_nx = ceili(StationGeo.LENGTH / CELL)
	var g := PackedFloat32Array()
	g.resize(_ns * _nx)
	for pair in [[lights.get("_lamps"), 4, 1.0], [lights.get("_strings"), 7, 1.5], [lights.get("_walk"), 3, 0.6]]:
		var a = pair[0]
		if a == null:
			continue
		var st: int = pair[1]
		for i in range(0, (a as Array).size() - 1, st):
			var s := fposmod(float(a[i]), StationGeo.CIRC)
			var x := float(a[i + 1]) + StationGeo.HALF_LEN
			var ci := clampi(int(s / CELL), 0, _ns - 1)
			var cj := clampi(int(x / CELL), 0, _nx - 1)
			g[cj * _ns + ci] += float(pair[2])
	for p in BLUR:
		g = _blur(g, true)
		g = _blur(g, false)
	_grid = g


func _blur(g: PackedFloat32Array, along_s: bool) -> PackedFloat32Array:
	## a box blur of radius 2 cells, along s (wrapping) or x
	var o := PackedFloat32Array()
	o.resize(g.size())
	for j in _nx:
		for i in _ns:
			var acc := 0.0
			for d in range(-2, 3):
				if along_s:
					acc += g[j * _ns + posmod(i + d, _ns)]
				else:
					acc += g[clampi(j + d, 0, _nx - 1) * _ns + i]
			o[j * _ns + i] = acc / 5.0
	return o


func _sample(s: float, x: float) -> float:
	var fs := fposmod(s, StationGeo.CIRC) / CELL - 0.5
	var fx := (x + StationGeo.HALF_LEN) / CELL - 0.5
	var i0 := floori(fs)
	var j0 := clampi(floori(fx), 0, _nx - 2)
	var ts := fs - i0
	var tx := clampf(fx - j0, 0.0, 1.0)
	var a := _grid[j0 * _ns + posmod(i0, _ns)]
	var b := _grid[j0 * _ns + posmod(i0 + 1, _ns)]
	var c := _grid[(j0 + 1) * _ns + posmod(i0, _ns)]
	var d := _grid[(j0 + 1) * _ns + posmod(i0 + 1, _ns)]
	return lerpf(lerpf(a, b, ts), lerpf(c, d, ts), tx)


func _process(delta: float) -> void:
	if _lights and _grid.is_empty() and _task < 0 and bool(_lights.get("ready_")):
		_task = WorkerThreadPool.add_task(_build.bind(_lights), false, "light field")
	if _task >= 0:
		if not WorkerThreadPool.is_task_completed(_task):
			return
		WorkerThreadPool.wait_for_task_completion(_task)
		_task = -1
	var cam := get_viewport().get_camera_3d()
	if cam == null:
		return
	var p := cam.global_position
	_t -= delta
	if _t <= 0.0:
		_t = 0.5
		# the floor: lamps round here, fading with the height over the ground (the air's glow is low and local)
		_floor = 0.0
		if not _grid.is_empty():
			var s := StationGeo.s_of(p)
			var above := StationGeo.h_of(p) - maxf(MapTerrain.elevation(s, p.x), 0.0)
			_floor = (1.0 - exp(-_sample(s, p.x) / DENSE)) * clampf(1.0 - above / 250.0, 0.0, 1.0)
		_isl = 0.0                     # (islands: their lamp field lights each surface by distance -- SkyWarren._field)
	var want := clampf(maxf(_floor, _isl), 0.0, 1.0) if enabled else 0.0
	glow = lerpf(glow, want, clampf(delta * 1.5, 0.0, 1.0))     # (eased: walking out of town, it fades)


func _island_glow(p: Vector3) -> float:
	var sk: Node = station.get_node_or_null("SkyIslands") if station else null
	if sk == null:
		return 0.0
	var best := 0.0
	for isl in sk.islands:
		if isl.tier < 2 or isl.warren == null:
			continue
		var lp: Vector3 = isl.global_transform.affine_inverse() * p
		var n := 0.0
		for l in (isl.warren.side as Dictionary).get("lights", []):
			var d := Vector3(float(l[0]), float(l[1]), float(l[2])).distance_to(lp)
			if d < REACH:
				n += 1.0 - d / REACH
		best = maxf(best, 1.0 - exp(-n / ISLAND_DENSE))
	return best
