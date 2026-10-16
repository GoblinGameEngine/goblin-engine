extends RefCounted
## (no class_name: the users preload it as CitySigns, so a new global class needs no --import)

## Bitmap shop signs (tools/signs/make_signs.py -> remake/signs/city_signs.json + remake/signs/city/<Settlement>.png).
## Every storefront sign board store.py built gets a textured quad with the shop's actual name (it replaces the board's
## 3D lettering: merge_kit drops those kit "T" rows, drop_rows()).  One MeshInstance3D per building (all its signs,
## one surface: one draw), one material per settlement atlas (shared by every building there); the glow is the atlas's
## emit texture (albedo x night mask), driven by set_night() from RemakeBuilding.set_night (DaySkySystem).

const INDEX := "res://remake/signs/city_signs.json"
const SHOW_TO := 240.0               # m: a sign's own mesh draws to here (LOD0 and LOD1 both carry it)
const LIFT := 0.006                  # m off the board's lettering plane

static var _mx := Mutex.new()
static var _data = null              # the parsed index (Dictionary), loaded once
static var _drop := {}               # model -> {row index: true}
static var _mats := {}               # settlement -> StandardMaterial3D
static var _night := 0.0
static var enabled := true


static func _load() -> void:
	_mx.lock()
	if _data == null:
		var d = DataFile.json(INDEX)
		_data = d if d is Dictionary else {}
		# (not imported yet -- a new atlas without its .import -- or no index: no signs, and keep the 3D lettering)
		var sts: Dictionary = _data.get("settlements", {})
		if sts.is_empty() or not ResourceLoader.exists(String(sts[sts.keys()[0]].get("png", ""))):
			enabled = false
			_data = {}
		var dr: Dictionary = _data.get("models_drop_rows", {})
		for m in dr:
			var s := {}
			for ri in dr[m]:
				s[int(ri)] = true
			_drop[m] = s
	_mx.unlock()


static func drop_rows(model: String) -> Dictionary:
	## the kit T rows (indices) of a model that the bitmap signs replace (safe on a worker thread)
	if _data == null:
		_load()
	if not enabled:
		return {}
	return _drop.get(model, {})


static func _material(st: String) -> StandardMaterial3D:
	if _mats.has(st):
		return _mats[st]
	var info: Dictionary = (_data.get("settlements", {}) as Dictionary).get(st, {})
	var m := StandardMaterial3D.new()
	m.resource_name = "CITY_SIGNS_" + st
	var alb = load(String(info.get("png", ""))) if info.has("png") else null
	var emi = load(String(info.get("emit", ""))) if info.has("emit") else null
	m.albedo_texture = alb
	m.roughness = 0.75
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	m.alpha_scissor_threshold = 0.5
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	if emi:
		m.emission_enabled = true
		m.emission = Color.WHITE
		# MULTIPLY: emission = colour x texture (the default ADD made it colour + texture: every quad glowed solid white
		# at night whatever its mask said -- the user's "washed out", 2026-10-16)
		m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
		m.emission_texture = emi
		m.emission_energy_multiplier = _energy(_night)
	_mats[st] = m
	return m


## Night glow (the user, 2026-10-16: "washed out at night"): only the lit parts emit.  The emit atlas is albedo x mask
## (make_signs.py): neon, bulbs and letters 255, lightbox faces 115, board grounds and backings 0; the material's
## emission is that x EMIT_SCALE x night (MULTIPLY operator).  The shared night scale with the island signs
## (2026-10-16): letters and neon 2.0 HDR, lit faces <= 0.9, backings dark, against DaySkySystem's glow (threshold 1.5,
## intensity 0.7, no bloom).
const EMIT_SCALE := 2.0               # (the shared night scale with the island signs: letters and neon 2.0 HDR)


static func _energy(n: float) -> float:
	return n * EMIT_SCALE


static func set_night(n: float) -> void:
	_night = n
	for st in _mats:
		(_mats[st] as StandardMaterial3D).emission_energy_multiplier = _energy(n)


static func attach(root: Node3D, building_id: String) -> void:
	## the building's signs as one mesh under its root (the placement frame: the quads are in it)
	if _data == null:
		_load()
	if not enabled:
		return
	var b = (_data.get("buildings", {}) as Dictionary).get(building_id)
	if b == null or root.has_node("city_signs"):
		return
	var verts := PackedVector3Array()
	var norms := PackedVector3Array()
	var uvs := PackedVector2Array()
	var idx := PackedInt32Array()
	for q in b.quads:
		var c := Vector3(q.c[0], q.c[1], q.c[2])
		var r := Vector3(q.r[0], q.r[1], q.r[2])
		var u := Vector3(q.u[0], q.u[1], q.u[2])
		var n := r.cross(u).normalized()       # (the lettering's own +z: outward, toward the reader)
		c += n * LIFT
		var hw: float = float(q.w) * 0.5
		var hh: float = float(q.h) * 0.5
		var uv: Array = q.uv
		var base := verts.size()
		# reading from outside: left = c - r*hw (r is the reading direction)
		verts.append_array([c - r * hw + u * hh, c + r * hw + u * hh, c + r * hw - u * hh, c - r * hw - u * hh])
		for _k in 4:
			norms.append(n)
		uvs.append_array([Vector2(uv[0], uv[1]), Vector2(uv[0] + uv[2], uv[1]), Vector2(uv[0] + uv[2], uv[1] + uv[3]),
			Vector2(uv[0], uv[1] + uv[3])])
		idx.append_array([base, base + 1, base + 2, base, base + 2, base + 3])
	if verts.is_empty():
		return
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_NORMAL] = norms
	arr[Mesh.ARRAY_TEX_UV] = uvs
	arr[Mesh.ARRAY_INDEX] = idx
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	mesh.surface_set_material(0, _material(String(b.settlement)))
	var mi := MeshInstance3D.new()
	mi.name = "city_signs"
	mi.mesh = mesh
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.visibility_range_end = SHOW_TO
	mi.visibility_range_end_margin = 20.0
	mi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	root.add_child(mi)


static func signs_of(building_id: String) -> Array:
	## [{uid, type, name, style, ...}] (for the PDA, WorldQuery, the story engine)
	if _data == null:
		_load()
	var b = (_data.get("buildings", {}) as Dictionary).get(building_id)
	return b.quads if b != null else []
