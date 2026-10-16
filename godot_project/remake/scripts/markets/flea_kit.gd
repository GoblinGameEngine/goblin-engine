extends RefCounted
class_name FleaKit

## The flea-market kit (MARKETS-KIT stream: remake/markets/kit.glb, kit_mid.glb, pieces.json; research/flea_markets/
## requests.md K1): each piece's surfaces by SLOT, recoloured from the palettes and merged into chunk meshes by GROUP.
##
##   FleaKit.load_all()                     main thread, once: the glbs' meshes into arrays
##   FleaKit.ok()                           the kit is there
##   FleaKit.has(piece) / info(piece)       its pieces.json record
##   FleaKit.put(acc, piece, xf, variant, over := {}, mid := false, yscale := 1.0, ypivot := 0.0)
##                                          append the piece (piece frame -> chunk frame `xf`) to `acc` {group: arrays}
##   FleaKit.anchor(piece, name)            Transform3D of an anchor in the piece frame (identity if none)
##   FleaKit.material(group)                the shared material of a group (night: set_night)
##   FleaKit.commit(acc)                    {group: ArrayMesh-ready arrays}
##
## Colour: COLOR_0 is a grey shade (baked AO); the vertex colour is shade x the palette's sRGB colour of the slot
## (palettes[key][variant][slot]; `over` replaces slots). Night (pieces.json "night"): emissive 2.0 x night, glow
## <= 0.9, canvas a 0.35 lobe, textured: the atlas's _emit mask x albedo x 2.0 x night.

const PIECES := "res://remake/markets/pieces.json"
static var _loaded := false
static var _ok := false
static var pieces := {}
static var palettes := {}
static var slot_group := {}
static var textures := {}
static var _mesh := {}                  # "glb|mesh" -> [[slot, PackedVector3Array v, n, PackedColorArray c, PackedVector2Array uv, PackedInt32Array idx]]
static var _mats := {}
static var _night := 0.0


static func ok() -> bool:
	return _ok


static func has(p: String) -> bool:
	return _ok and pieces.has(p)


static func info(p: String) -> Dictionary:
	return pieces.get(p, {})


static func load_all() -> void:
	if _loaded:
		return
	_loaded = true
	var d = DataFile.json(PIECES)
	if not (d is Dictionary):
		return
	pieces = d.get("pieces", {})
	palettes = d.get("palettes", {})
	slot_group = d.get("slot_group", {})
	textures = d.get("textures", {})
	var glbs := {}
	for k in pieces:
		var e: Dictionary = pieces[k]
		glbs[str(e.get("glb", ""))] = true
		var m = e.get("mid")
		if m is Dictionary:
			glbs[str(m.get("glb", ""))] = true
	for g in glbs:
		if g == "" or not ResourceLoader.exists(g):
			continue
		var ps = load(g)
		if not (ps is PackedScene):
			continue
		var root: Node = (ps as PackedScene).instantiate()
		for mi in root.find_children("*", "MeshInstance3D", true, false):
			var mesh: Mesh = (mi as MeshInstance3D).mesh
			if mesh == null:
				continue
			var surfs: Array = []
			for si in mesh.get_surface_count():
				var mat := mesh.surface_get_material(si)
				var slot := str(mat.resource_name).trim_prefix("mk_") if mat else "wall"
				var a := mesh.surface_get_arrays(si)
				var v: PackedVector3Array = a[Mesh.ARRAY_VERTEX]
				var n: PackedVector3Array = a[Mesh.ARRAY_NORMAL] if a[Mesh.ARRAY_NORMAL] != null else PackedVector3Array()
				var c: PackedColorArray = a[Mesh.ARRAY_COLOR] if a[Mesh.ARRAY_COLOR] != null else PackedColorArray()
				var uv: PackedVector2Array = a[Mesh.ARRAY_TEX_UV] if a[Mesh.ARRAY_TEX_UV] != null else PackedVector2Array()
				var idx: PackedInt32Array = a[Mesh.ARRAY_INDEX] if a[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
				# (the node's own transform inside the glb, baked in)
				var xf := (mi as MeshInstance3D).transform
				if xf != Transform3D.IDENTITY:
					for i in v.size():
						v[i] = xf * v[i]
					for i in n.size():
						n[i] = (xf.basis * n[i]).normalized()
				surfs.append([slot, v, n, c, uv, idx])
			_mesh["%s|%s" % [g, str(mi.name)]] = surfs
		root.free()
	_ok = not _mesh.is_empty()


static func _surfaces(p: String, mid: bool) -> Array:
	var e: Dictionary = pieces.get(p, {})
	if e.is_empty():
		return []
	if mid:
		var m = e.get("mid")
		if m is Dictionary:
			return _mesh.get("%s|%s" % [m.glb, m.mesh], [])
	return _mesh.get("%s|%s" % [e.glb, e.mesh], [])


static func anchor(p: String, name: String) -> Transform3D:
	var a = (pieces.get(p, {}) as Dictionary).get("anchors", {}).get(name)
	if not (a is Array) or a.size() < 4:
		return Transform3D.IDENTITY
	return Transform3D(Basis(Vector3.UP, deg_to_rad(float(a[3]))), Vector3(float(a[0]), float(a[1]), float(a[2])))


static func variants(key: String) -> int:
	return maxi(1, (palettes.get(key, []) as Array).size())


static func _pal(key: String, variant: int) -> Dictionary:
	var vs: Array = palettes.get(key, [])
	if vs.is_empty():
		return {}
	return vs[posmod(variant, vs.size())]


static func put(acc: Dictionary, p: String, xf: Transform3D, variant := 0, over := {}, mid := false, yscale := 1.0, ypivot := 0.0) -> int:
	var e: Dictionary = pieces.get(p, {})
	var pal := _pal(str(e.get("palette", "stall")), variant)
	var n_ := 0
	for s in _surfaces(p, mid):
		var slot: String = s[0]
		var grp := str(slot_group.get(slot, "solid"))
		if not acc.has(grp):
			acc[grp] = [PackedVector3Array(), PackedVector3Array(), PackedColorArray(), PackedVector2Array(), PackedInt32Array()]
		var A: Array = acc[grp]
		var base := (A[0] as PackedVector3Array).size()
		var col := Color(str(over.get(slot, pal.get(slot, "#bbbbbb"))))
		var v: PackedVector3Array = s[1]
		var nn: PackedVector3Array = s[2]
		var cc: PackedColorArray = s[3]
		var uv: PackedVector2Array = s[4]
		var idx: PackedInt32Array = s[5]
		var vs: PackedVector3Array = A[0]
		var ns: PackedVector3Array = A[1]
		var cs: PackedColorArray = A[2]
		var us: PackedVector2Array = A[3]
		var ix: PackedInt32Array = A[4]
		for i in v.size():
			var q := v[i]
			if yscale != 1.0:
				q.y = ypivot + (q.y - ypivot) * yscale
			vs.append(xf * q)
			ns.append((xf.basis * (nn[i] if i < nn.size() else Vector3.UP)).normalized())
			var sh := cc[i].r if i < cc.size() else 1.0
			cs.append(Color(col.r * sh, col.g * sh, col.b * sh, 1.0))
			us.append(uv[i] if i < uv.size() else Vector2.ZERO)
		if idx.is_empty():
			for i in v.size():
				ix.append(base + i)
		else:
			for i in idx:
				ix.append(base + i)
		A[0] = vs
		A[1] = ns
		A[2] = cs
		A[3] = us
		A[4] = ix
		n_ += v.size()
	return n_


static func commit(acc: Dictionary) -> Dictionary:
	var out := {}
	for g in acc:
		var A: Array = acc[g]
		if (A[0] as PackedVector3Array).is_empty():
			continue
		var arr := []
		arr.resize(Mesh.ARRAY_MAX)
		arr[Mesh.ARRAY_VERTEX] = A[0]
		arr[Mesh.ARRAY_NORMAL] = A[1]
		arr[Mesh.ARRAY_COLOR] = A[2]
		arr[Mesh.ARRAY_TEX_UV] = A[3]
		arr[Mesh.ARRAY_INDEX] = A[4]
		out[g] = arr
	return out


const SHADER := """shader_type spatial;
render_mode cull_back;
uniform sampler2D atlas : source_color, filter_linear_mipmap;
uniform sampler2D emit_mask : hint_default_black, filter_linear_mipmap;
uniform bool textured = false;
uniform float metal = 0.0;
uniform float rough = 0.85;
uniform float emit_k = 0.0;      // x albedo x night (emissive 2.0, glow 0.9, canvas 0.35)
uniform float tex_emit = 0.0;    // textured: mask x albedo x this x night
uniform float night = 0.0;
varying vec3 vcol;
vec3 lin(vec3 c) { return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c)); }
void vertex() { vcol = lin(COLOR.rgb); }
void fragment() {
	vec3 a = vcol;
	if (textured) {
		vec4 t = texture(atlas, UV);
		if (t.a < 0.5) { discard; }
		a *= t.rgb;
		EMISSION = a * texture(emit_mask, UV).r * tex_emit * night;
	} else {
		EMISSION = a * emit_k * night;
	}
	ALBEDO = a;
	METALLIC = metal;
	ROUGHNESS = rough;
}"""


static func material(g: String) -> Material:
	if _mats.has(g):
		return _mats[g]
	var sh := Shader.new()
	sh.code = SHADER
	var m := ShaderMaterial.new()
	m.shader = sh
	match g:
		"metal":
			m.set_shader_parameter("metal", 0.55)
			m.set_shader_parameter("rough", 0.45)
		"glass":
			m.set_shader_parameter("metal", 0.2)
			m.set_shader_parameter("rough", 0.12)
		"emissive":
			m.set_shader_parameter("emit_k", 2.0)
		"glow":
			m.set_shader_parameter("emit_k", 0.9)
		"canvas":
			m.set_shader_parameter("emit_k", 0.35)
			m.set_shader_parameter("rough", 0.95)
	if g.begins_with("tex_"):
		var p := str(textures.get(g, ""))
		if p != "" and ResourceLoader.exists(p):
			m.set_shader_parameter("textured", true)
			m.set_shader_parameter("atlas", load(p))
			var em := p.get_basename() + "_emit.png"
			if ResourceLoader.exists(em):
				m.set_shader_parameter("emit_mask", load(em))
			m.set_shader_parameter("tex_emit", 2.0)
	_mats[g] = m
	return m


static func set_night(n: float) -> void:
	if absf(n - _night) < 0.01:
		return
	_night = n
	for g in _mats:
		(_mats[g] as ShaderMaterial).set_shader_parameter("night", n)
