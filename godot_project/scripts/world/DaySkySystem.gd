extends Node
class_name DaySkySystem

# Drives the station's circadian sky cycle -- requested directly: a
# ceiling sky (shaders/ceiling_sky.gdshader) and wall cliff-to-sky blend
# (shaders/wall_cliff_sky.gdshader) sharing one time_of_day, plus a real
# shadow-casting DirectionalLight3D whose angle sweeps to match the
# visible sun band. One band across the WHOLE ceiling (not per-zone, not
# tied to arc position) so "the entire station is on the same time of
# day" -- see ceiling_sky.gdshader's own header for why the band is
# computed from world-space X rather than baked into the tiled sky
# texture.
#
# time_of_day: 0=midnight, 0.25=dawn ends/full day begins, 0.75=day ends/
# dusk begins, wraps at 1.0. The whole color/band arc is defined as a
# short list of (t, ...) keyframes linearly interpolated between --
# matches "blue during the day -> red at dusk -> night -> red at dawn ->
# blue" exactly by construction (day and night keyframes are pure
# white/night-texture; the ONLY place red shows up is the dawn/dusk
# keyframes in between).

static var DAY_LENGTH_SECONDS := 600.0  # live-tunable, e.g. gcmd.py run "DaySkySystem.DAY_LENGTH_SECONDS = 120.0"

const SKY_DAY_TEX := preload("res://assets/textures/sky_day.png")
const SKY_NIGHT_TEX := preload("res://assets/textures/sky_night.png")
const CLIFF_TEX := preload("res://assets/textures/cliff_rock.png")

const CEILING_SKY_SHADER := preload("res://shaders/ceiling_sky.gdshader")
const WALL_CLIFF_SKY_SHADER := preload("res://shaders/wall_cliff_sky.gdshader")

# Keyframes: [t, night_mix, tint_r, tint_g, tint_b, band_intensity, band_pos]
# band_pos only matters while band_intensity > 0; outside dawn/dusk/day
# it's held at its nearest defined value (unused since intensity is 0).
const KEYFRAMES := [
	[0.0,  1.0, 1.0, 1.0, 1.0, 0.0, 0.0],
	[0.15, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0],
	[0.20, 0.5, 1.6, 0.6, 0.4, 0.3, 0.15],
	[0.25, 0.0, 1.0, 1.0, 1.0, 1.0, 0.25],
	[0.75, 0.0, 1.0, 1.0, 1.0, 1.0, 0.75],
	[0.80, 0.5, 1.6, 0.6, 0.4, 0.3, 0.85],
	[0.85, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
	[1.0,  1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
]

var time_of_day: float = 0.27  # start mid-morning, already light out
var ceiling_material: ShaderMaterial
var wall_material: ShaderMaterial
var sun: DirectionalLight3D
var station: Node3D
var env: Environment

## `ring_mesh` is StationRingBuilder's single "RingMesh" node -- floor/
## ceiling/wall are surfaces 0/1/2 of ONE ArrayMesh (see that file's own
## build() for the exact commit order this depends on), not separate
## nodes, so this sets per-SURFACE overrides rather than a whole-instance
## material_override. Must run AFTER ToonShading.apply_to_world(ring_mesh)
## -- that call overwrites every surface's material uniformly with its
## own toon.gdshader instance; these two custom shaders (already their
## own self-contained cel-banded/unshaded logic, not meant to go through
## that conversion at all) need to land last, or ToonShading clobbers them.
## `p_env` (optional) is the WorldEnvironment's Environment resource --
## when given, ambient light gently dims at night (still well above the
## old near-black default that caused "the shadow problem" -- this is a
## mood shift, not a regression of that fix).
func setup(p_station: Node3D, p_sun: DirectionalLight3D, ring_mesh: MeshInstance3D,
		ceiling_height: float, wall_tile: float, p_env: Environment = null) -> void:
	station = p_station
	sun = p_sun
	env = p_env

	ceiling_material = ShaderMaterial.new()
	ceiling_material.shader = CEILING_SKY_SHADER
	ceiling_material.set_shader_parameter("sky_day_texture", SKY_DAY_TEX)
	ceiling_material.set_shader_parameter("sky_night_texture", SKY_NIGHT_TEX)
	ring_mesh.set_surface_override_material(1, ceiling_material)

	wall_material = ShaderMaterial.new()
	wall_material.shader = WALL_CLIFF_SKY_SHADER
	wall_material.set_shader_parameter("cliff_texture", CLIFF_TEX)
	wall_material.set_shader_parameter("sky_day_texture", SKY_DAY_TEX)
	wall_material.set_shader_parameter("sky_night_texture", SKY_NIGHT_TEX)
	wall_material.set_shader_parameter("wall_v_max", ceiling_height / wall_tile)
	ring_mesh.set_surface_override_material(2, wall_material)

	_apply(0.0)  # first frame's worth, before _process() runs

static func _lerp_keyframes(t: float) -> Array:
	for i in range(KEYFRAMES.size() - 1):
		var a: Array = KEYFRAMES[i]
		var b: Array = KEYFRAMES[i + 1]
		if t >= a[0] and t <= b[0]:
			var span: float = b[0] - a[0]
			var f: float = (t - a[0]) / span if span > 0.0001 else 0.0
			var out := []
			for k in range(1, a.size()):
				out.append(lerp(float(a[k]), float(b[k]), f))
			return out
	var last: Array = KEYFRAMES[KEYFRAMES.size() - 1]
	return last.slice(1)

func _process(delta: float) -> void:
	time_of_day = fposmod(time_of_day + delta / DAY_LENGTH_SECONDS, 1.0)
	_apply(delta)

func _apply(_delta: float) -> void:
	if ceiling_material == null:
		return
	var v := _lerp_keyframes(time_of_day)
	var night_mix: float = v[0]
	var tint := Color(v[1], v[2], v[3])
	var band_intensity: float = v[4]
	var band_pos: float = v[5]

	var width: float = SpaceStation.WIDTH
	var band_center: float = lerp(-width * 0.5, width * 0.5, band_pos)
	var band_half_width: float = width * 0.025  # 5% of the ceiling's width, requested directly
	# Band color rides the same tint arc -- warm/orange low on the horizon
	# (dawn/dusk), bright and closer to white overhead.
	var band_color := Color(tint.r, tint.g * 0.95, tint.b * 0.85)

	ceiling_material.set_shader_parameter("night_mix", night_mix)
	ceiling_material.set_shader_parameter("day_tint", tint)
	ceiling_material.set_shader_parameter("band_color", band_color)
	ceiling_material.set_shader_parameter("band_center", band_center)
	ceiling_material.set_shader_parameter("band_half_width", band_half_width)
	ceiling_material.set_shader_parameter("band_intensity", band_intensity)

	wall_material.set_shader_parameter("night_mix", night_mix)
	wall_material.set_shader_parameter("day_tint", tint)

	if sun:
		# The light's own direction sweeps the same west->east arc the
		# visible band does, so shadows fall consistently with what's
		# painted on the ceiling -- "cast shadows... a natural way to
		# tell direction and time of day" only works if the two agree.
		# -35/40 (pitch/base yaw) matches this project's original static
		# "noon" sun; the sweep just adds/subtracts yaw around that.
		var sweep_deg: float = lerp(-55.0, 55.0, band_pos)
		sun.rotation_degrees = Vector3(-35.0, 40.0 + sweep_deg, 0.0)
		sun.light_color = Color(tint.r, tint.g * 0.97, tint.b * 0.9)
		sun.light_energy = 0.15 + band_intensity * 1.15
		sun.shadow_enabled = band_intensity > 0.05

	if env:
		# 1.2 (this project's established "no pitch-black areas" fix) by
		# day, dimmed but still well clear of that old broken floor by
		# night -- a mood shift, not a return of the original bug.
		env.ambient_light_energy = lerp(0.65, 1.2, 1.0 - night_mix)
