extends Node3D
class_name SkyBanners

## The islands' banners (the user, 2026-10-15: "Each island should be trailing large colorful banners that stretch
## 300m below the islands advertising its name and its wares. Each Island will need its own ethno/political flag"):
##   banners   2-4 long hanging banners an island, 10-20 m wide (by the island's size), hung from its rim on its outer
##             faces, facing out, ~300 m long: mostly flat with a gentle billow and a slow sway, weighted at the foot by
##             a batten, so the name on them reads from the ground and the neighbouring islands (sky_banner.gdshader,
##             phased per banner in the island's frame; lit at night).  Every island's in ONE MultiMesh near (40-segment ribbons) and one far (6
##             segments, updated every fourth frame) -- two draws for the whole sky, filled from flat buffers like
##             the balloons (SkyIslands._balloons).
##   flags     the island's flag on a mast at each dock face (near islands; one MultiMesh of masts, one of flags)
##   pennants  on the rooftops: the warren's tallest columns (near islands)
## Furled -- shortened -- where an island rides low over the ground or over another island below it, so a banner never
## reaches the floor or another deck.  (Lashed islands lie side by side: a raft doesn't furl them.)
##
## The artwork: the SIGNS agent's atlas (remake/signs/signs.json "flags" / "banners": {island id: {atlas, cell}}),
## sampled by cell when it is there; until then the clan's colours in bands with a woven motif.

const LEN := 300.0                   # m a banner at full length
const WIDTH := 1.0                   # (the mesh is 1 m wide: each banner's instance is scaled to its island's width)
const NAME_COLS := 32                # the name atlas: 32 x 4 cells of 64 x 512 px, each island's name down a cell
const NAME_ROWS := 4
const SEG_NEAR := 40
const SEG_FAR := 6
const FLAG_W := 6.0
const FLAG_H := 4.0
const MAST_H := 14.0
const FURL_PER := 1                  # islands' clearances checked a round (~50 us each: the terrain under it) ...
const FURL_EVERY := 4                # ... one round every 4th frame (all 100 in ~7 s: they drift slowly)
const FURL_R := 400.0                # m: the grid's cells (only islands in neighbouring cells can be below)
const SH := preload("res://remake/shaders/sky_banner.gdshader")

var sys: Node                        # SkyIslands
var _near: MultiMeshInstance3D
var _far: MultiMeshInstance3D
var _flags: MultiMeshInstance3D
var _masts: MultiMeshInstance3D
var _pennants: MultiMeshInstance3D
var _anch: Array = []                # per island: [[local point, yaw]] banner tops
var _docks: Array = []               # per island: [[local point, yaw]] masts
var _roofs: Array = []               # per island: [local point] (filled when its warren is in)
var _look: Array = []                # per island: [colour A, colour B packed, atlas cell, phase]
var _len: PackedFloat32Array = PackedFloat32Array()   # per island: length factor 0..1 (furl)
var _buf_n := PackedFloat32Array()
var _buf_f := PackedFloat32Array()
var _frame := 0
var _grid := {}
var draws_ms := 0.0                  # (stats: the last update's main-thread time)


func setup(p_sys: Node) -> void:
	sys = p_sys
	name = "SkyBanners"
	var atlas := _atlas_cells()
	for i in sys.islands.size():
		var L: Dictionary = sys.layouts[i]
		var id := str(L.id)
		var h := absi(id.hash())
		# banner tops on the rim: evenly round the outline, 2-4 of them
		var ol: Array = L.get("outline", [])
		var nb := 2 + h % 3
		var an: Array = []
		for k in nb:
			if ol.is_empty():
				break
			var p: Array = ol[int(float(k + 0.5) / nb * ol.size()) % ol.size()]
			var lp := Vector3(float(p[0]), -1.5, float(p[1]))
			an.append([Vector3(lp.x * 0.97, lp.y, lp.z * 0.97), atan2(lp.x, lp.z)])
		_anch.append(an)
		# masts at the dock faces: the launchers (else the face centres)
		var dk: Array = []
		for l in L.get("launchers", []):
			dk.append([Vector3(float(l.x), 0.0, float(l.z)), float(l.yaw)])
		_docks.append(dk)
		_roofs.append([])
		var cols: Array = sys.islands[i].canon.get("colors", [])
		var ca := Color(str(cols[0])) if cols.size() > 0 else Color.from_hsv(float(h % 360) / 360.0, 0.7, 0.85)
		var cb := Color(str(cols[1])) if cols.size() > 1 else Color.from_hsv(float((h / 7) % 360) / 360.0, 0.6, 0.95)
		var packed := float((cb.r8 << 16) | (cb.g8 << 8) | cb.b8)
		var f: Dictionary = L.get("faces", {})
		var rad := maxf(maxf(absf(float(f.get("N", 80))), absf(float(f.get("S", 80)))), maxf(absf(float(f.get("E", 80))), absf(float(f.get("W", 80)))))
		_look.append([ca, packed, float(atlas.get(id, -1)), float(h % 1000) / 1000.0, clampf(rad * 0.16, 12.0, 20.0), float(i % (NAME_COLS * NAME_ROWS))])
	_len.resize(sys.islands.size())
	_len.fill(1.0)
	var mat := ShaderMaterial.new()
	mat.shader = SH
	mat.set_shader_parameter("len_m", LEN)
	_near = _mmi("BannersNear", _ribbon(SEG_NEAR, WIDTH, LEN), mat)
	_far = _mmi("BannersFar", _ribbon(SEG_FAR, WIDTH, LEN), mat)
	var fm := ShaderMaterial.new()
	fm.shader = SH
	fm.set_shader_parameter("len_m", FLAG_W)
	fm.set_shader_parameter("flag", true)
	_flags = _mmi("Flags", _ribbon(8, FLAG_H, FLAG_W), fm)
	_pennants = _mmi("Pennants", _ribbon(5, 0.9, 3.5), fm)
	var pole := CylinderMesh.new()
	pole.top_radius = 0.08
	pole.bottom_radius = 0.12
	pole.height = MAST_H
	pole.radial_segments = 5
	pole.rings = 1
	var pm := StandardMaterial3D.new()
	pm.albedo_color = Color(0.32, 0.3, 0.28)
	pole.material = pm
	_masts = _mmi("Masts", pole, null)
	if not _banner_atlas.is_empty() and _banner_atlas.has("png_a"):
		# the SIGNS agent's banners (name and wares, in the warren's lettering and the people's colours): cells 2i, 2i+1
		mat.set_shader_parameter("atlas", load(str(_banner_atlas.png_a)))
		if _banner_atlas.has("emit_a"):
			mat.set_shader_parameter("atlas_emit", load(str(_banner_atlas.emit_a)))
		var g: Array = _banner_atlas.get("grid", [32, 7])
		mat.set_shader_parameter("atlas_grid", Vector2(float(g[0]), float(g[1])))
		mat.set_shader_parameter("has_atlas", true)
		if _banner_atlas.has("png_b") and ResourceLoader.exists(str(_banner_atlas.png_b)):
			mat.set_shader_parameter("atlas_b", load(str(_banner_atlas.png_b)))
			if _banner_atlas.has("emit_b"):
				mat.set_shader_parameter("atlas_b_emit", load(str(_banner_atlas.emit_b)))
			mat.set_shader_parameter("has_atlas_b", true)
	else:
		_bake_names.call_deferred(mat)
	for m in [_near, _far]:
		# (300 m ribbons on islands kilometres off: never culled for being off-centre)
		m.custom_aabb = AABB(Vector3.ONE * -StationGeo.R * 1.2, Vector3.ONE * StationGeo.R * 2.4)
	_near.visibility_range_end = 0.0


func _bake_names(mat: ShaderMaterial) -> void:
	## (once) every island's name, set down a 64 x 512 cell of one luminance texture (a SubViewport of Labels drawn a
	## single time): the banners' lettering until the SIGNS atlas has their name-and-wares strips
	var vp := SubViewport.new()
	vp.size = Vector2i(64 * NAME_COLS, 512 * NAME_ROWS)
	vp.transparent_bg = false
	vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	var bg := ColorRect.new()
	bg.color = Color.BLACK
	bg.size = Vector2(vp.size)
	vp.add_child(bg)
	for i in mini(sys.layouts.size(), NAME_COLS * NAME_ROWS):
		var nm := str(sys.layouts[i].get("name", sys.layouts[i].id)).to_upper()
		var lb := Label.new()
		lb.text = nm
		lb.add_theme_font_size_override("font_size", int(clampf(470.0 / maxf(nm.length(), 1) * 1.55, 18.0, 54.0)))
		lb.add_theme_color_override("font_color", Color.WHITE)
		lb.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lb.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		lb.size = Vector2(500, 60)
		lb.pivot_offset = Vector2(0, 0)
		# (turned a quarter: read top to bottom down the cell)
		lb.rotation = PI * 0.5
		var cx := (i % NAME_COLS) * 64
		var cy := (i / NAME_COLS) * 512
		lb.position = Vector2(cx + 62, cy + 6)
		vp.add_child(lb)
	add_child(vp)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img := vp.get_texture().get_image()
	img.convert(Image.FORMAT_L8)
	img.generate_mipmaps()
	mat.set_shader_parameter("names", ImageTexture.create_from_image(img))
	mat.set_shader_parameter("name_grid", Vector2(NAME_COLS, NAME_ROWS))
	mat.set_shader_parameter("has_names", true)
	vp.queue_free()


static var _banner_atlas := {}


static func _atlas_cells() -> Dictionary:
	## (SIGNS, signs.json "banner_atlas") island id -> its name banner's cell in banners_a (its wares banner: the next)
	var p := "res://remake/signs/signs.json"
	if not DataFile.exists(p):
		return {}
	var d = JSON.parse_string(DataFile.text(p))
	if not (d is Dictionary) or not d.has("banner_atlas"):
		return {}
	_banner_atlas = d.banner_atlas
	var out := {}
	for id in (d.banner_atlas.get("islands", {}) as Dictionary):
		out[id] = int(d.banner_atlas.islands[id].get("name", -1))
	return out


func _mmi(n: String, mesh: Mesh, mat: Material) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.use_custom_data = true
	mm.mesh = mesh
	var mi := MultiMeshInstance3D.new()
	mi.name = n
	mi.multimesh = mm
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	if mat:
		mi.material_override = mat
	add_child(mi)
	return mi


static func _ribbon(segs: int, w: float, l: float) -> ArrayMesh:
	## a strip hanging from y 0 down to -l (or out along +x for a flag: the shader turns it), w wide in x; UV.y 0 at the
	## top .. 1 at the end, UV.x across; double-sided (the shader turns the normal)
	var v := PackedVector3Array()
	var n := PackedVector3Array()
	var u := PackedVector2Array()
	var ix := PackedInt32Array()
	for k in segs + 1:
		var t := float(k) / segs
		for s in 2:
			v.append(Vector3((s - 0.5) * w, -t * l, 0.0))
			n.append(Vector3(0, 0, 1))
			u.append(Vector2(s, t))
	for k in segs:
		var a := k * 2
		ix.append_array([a, a + 2, a + 1, a + 1, a + 2, a + 3])
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = v
	arr[Mesh.ARRAY_NORMAL] = n
	arr[Mesh.ARRAY_TEX_UV] = u
	arr[Mesh.ARRAY_INDEX] = ix
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return m


# ------------------------------------------------------------------ every frame (SkyIslands._process)
var _slot0 := PackedInt32Array()     # per island: its first slot in the banner buffers (fixed: no resizing a frame)
var _anch_xf: Array = []             # per island: its banners' local transforms (turned, scaled to its width)
var _tier_prev := PackedInt32Array()
var _nb := 0
const FAR_EVERY := 16                # far islands' banners: a sixteenth of them a frame (km off: a lag of 1/4 s is nothing)


func _slots() -> void:
	## (once) every banner a fixed slot in both buffers; a banner shown in one is a zero transform in the other
	_slot0.resize(sys.islands.size())
	_tier_prev.resize(sys.islands.size())
	_tier_prev.fill(-1)
	_nb = 0
	for i in sys.islands.size():
		_slot0[i] = _nb
		var lk: Array = _look[i]
		var xs: Array = []
		for a in _anch[i]:
			xs.append(Transform3D(Basis(Vector3.UP, float(a[1])) * Basis.from_scale(Vector3(float(lk[4]), 1.0, 1.0)), a[0]))
		_anch_xf.append(xs)
		_nb += xs.size()
	_buf_n.resize(_nb * 20)
	_buf_n.fill(0.0)
	_buf_f.resize(_nb * 20)
	_buf_f.fill(0.0)


func step(delta: float) -> void:
	var t0 := Time.get_ticks_usec()
	if _slot0.is_empty():
		_slots()
	_frame += 1
	if _frame % FURL_EVERY == 0:
		_furl()
	for i in sys.islands.size():
		var tier: int = sys.islands[i].tier
		var near := tier >= 1
		var moved_tier := tier != _tier_prev[i]
		# (the island you're on or by every frame; the mid ones every other; the far a sixteenth a frame)
		var due: bool = tier >= 2 or (tier == 1 and (i + _frame) % 2 == 0) or i % FAR_EVERY == _frame % FAR_EVERY
		if due or moved_tier:
			var xf: Transform3D = sys.islands[i].global_transform
			var lk: Array = _look[i]
			var ln := _len[i]
			var k := _slot0[i]
			for lx in _anch_xf[i]:
				var bx: Transform3D = xf * (lx as Transform3D)
				# (explicit branches: each packed buffer written in place, no copies)
				if near:
					_put(_buf_n, k, bx, lk, ln, 0.0, _cell_add(k - _slot0[i]))
					if moved_tier:
						_hide(_buf_f, k)
				else:
					_put(_buf_f, k, bx, lk, ln, 0.0, _cell_add(k - _slot0[i]))
					if moved_tier:
						_hide(_buf_n, k)
				k += 1
			_tier_prev[i] = tier
		if tier >= 2:
			if (_roofs[i] as Array).is_empty():
				_roof_points(i)
			if not _deco.has(i) or int(_deco[i][3]) != (_roofs[i] as Array).size():
				_deco_build(i)
		elif _deco.has(i):
			for m in (_deco[i] as Array).slice(0, 3):
				(m as Node).queue_free()
			_deco.erase(i)
	SkyIslands._set_buf(_near.multimesh, _buf_n, _nb)
	SkyIslands._set_buf(_far.multimesh, _buf_f, _nb)
	draws_ms = (Time.get_ticks_usec() - t0) / 1000.0


## per island at tier 2: its masts, flags and roof pennants as MultiMeshes in the island's own frame (children of it),
## built once -- they ride the island with no work a frame (rewritten in world space every frame they cost ~0.1 ms)
var _deco := {}                      # island -> [flags, masts, pennants, roof count]


func _deco_build(i: int) -> void:
	if _deco.has(i):
		for m in (_deco[i] as Array).slice(0, 3):
			(m as Node).queue_free()
	var lk: Array = _look[i]
	var docks: Array = _docks[i]
	var roofs: Array = _roofs[i]
	var bf := PackedFloat32Array()
	var bm := PackedFloat32Array()
	var bp := PackedFloat32Array()
	bf.resize(docks.size() * 20)
	bm.resize(docks.size() * 20)
	bp.resize(roofs.size() * 20)
	var kg := 0
	for d in docks:
		_put(bm, kg, Transform3D(Basis(Vector3.UP, float(d[1])), (d[0] as Vector3) + Vector3(0, MAST_H * 0.5, 0)), lk, 1.0, 0.0)
		kg = _put(bf, kg, Transform3D(Basis(Vector3.UP, float(d[1])), (d[0] as Vector3) + Vector3(0.1, MAST_H - 0.3, 0)), lk, 1.0, 1.0)
	var kp := 0
	for r in roofs:
		kp = _put(bp, kp, Transform3D(Basis(), r), lk, 1.0, 2.0)
	var out: Array = []
	for e in [[_flags, bf, kg], [_masts, bm, kg], [_pennants, bp, kp]]:
		var src: MultiMeshInstance3D = e[0]
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.use_custom_data = true
		mm.mesh = src.multimesh.mesh
		SkyIslands._set_buf(mm, e[1], int(e[2]))
		var mi := MultiMeshInstance3D.new()
		mi.name = "Banner" + str(src.name)
		mi.multimesh = mm
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.material_override = src.material_override
		sys.islands[i].add_child(mi)
		out.append(mi)
	out.append(roofs.size())
	_deco[i] = out


static func _cell_add(j: int) -> int:
	## an island's j-th banner: name (2i), wares (2i + 1), then banners_b's streamer (500 + 2i) and clan (500 + 2i + 1)
	return j % 2 + (500 if j % 4 >= 2 else 0)


static func _hide(buf: PackedFloat32Array, k: int) -> void:
	## a slot drawn as nothing (a zero basis: every triangle collapses to a point)
	var j := k * 20
	for m in 12:
		buf[j + m] = 0.0


static func _put(buf: PackedFloat32Array, k: int, t: Transform3D, lk: Array, ln: float, kind: float, cell_add := 0) -> int:
	## one instance: transform (12), colour A (4), custom: r the phase, g the length, b colour B packed, a the atlas cell
	## (+ 1000 x kind: 0 banner, 1 flag, 2 pennant)
	var j := k * 20
	var b := t.basis
	var o := t.origin
	var c: Color = lk[0]
	buf[j] = b.x.x; buf[j + 1] = b.y.x; buf[j + 2] = b.z.x; buf[j + 3] = o.x
	buf[j + 4] = b.x.y; buf[j + 5] = b.y.y; buf[j + 6] = b.z.y; buf[j + 7] = o.y
	buf[j + 8] = b.x.z; buf[j + 9] = b.y.z; buf[j + 10] = b.z.z; buf[j + 11] = o.z
	buf[j + 12] = c.r; buf[j + 13] = c.g; buf[j + 14] = c.b
	buf[j + 15] = (float(lk[5]) + 0.5) / 255.0 if lk.size() > 5 else 0.0    # (alpha: the island's name cell)
	buf[j + 16] = fmod(float(lk[3]) + float(k) * 0.137, 1.0); buf[j + 17] = ln; buf[j + 18] = lk[1]
	buf[j + 19] = (float(lk[2]) + float(cell_add) + 1.0 if float(lk[2]) >= 0.0 else 0.0) + 1000.0 * kind   # (cell + 1: 0 none)
	return k + 1


func _roof_points(i: int) -> void:
	## pennants on the warren's 6 tallest columns (once its side file is in)
	var w = sys.islands[i].get("warren")
	if w == null or (w.side as Dictionary).is_empty() or (w.head as Dictionary).is_empty():
		return
	var top := {}
	for lv in w.side.get("levels", []):
		var k := int(lv.level)
		var rows: Array = lv.rows
		for a in rows.size():
			var row := str(rows[a])
			for b in row.length():
				if row[b] == "#":
					top[Vector2i(a, b)] = k
	var best: Array = []
	for c: Vector2i in top:
		best.append([int(top[c]), c])
	best.sort_custom(func(p, q): return p[0] > q[0])
	var out: Array = []
	for e in best.slice(0, 6):
		var c: Vector2i = e[1]
		out.append(Vector3(float(w.head.x0) + 3.0 * c.x + 1.5, 3.2 * (int(e[0]) + 1) + 0.6, float(w.head.z0) + 3.0 * c.y + 1.5))
	_roofs[i] = out


var _furl_i := 0


func _furl() -> void:
	## a few islands a frame (FURL_PER): each one's banner length -- what clears the ground below and any island below it
	## within reach, less a margin.  Only the islands within FURL_R of it are compared (a grid of their positions is
	## rebuilt each round), not every pair: the pairwise check cost ~0.7 ms a frame.
	var n: int = sys.islands.size()
	if n == 0:
		return
	if _furl_i == 0:
		_grid.clear()
		for j in n:
			var q: Vector3 = sys.islands[j].global_position
			var key := Vector3i(floori(q.x / FURL_R), floori(q.y / FURL_R), floori(q.z / FURL_R))
			if not _grid.has(key):
				_grid[key] = []
			_grid[key].append(j)
	for step_ in FURL_PER:
		var i := _furl_i
		_furl_i = (_furl_i + 1) % n
		var isl: Node3D = sys.islands[i]
		var p := isl.global_position
		if sys.drift and sys.drift.mooring and sys.drift.mooring.is_moored(i):
			_len[i] = 0.08                       # (moored over a market, or coming down to one: furled)
			if _furl_i == 0:
				break
			continue
		var clear := StationGeo.h_of(p) - maxf(MapTerrain.elevation(StationGeo.s_of(p), p.x), 0.0)
		var up := StationGeo.up(StationGeo.s_of(p))
		var k0 := Vector3i(floori(p.x / FURL_R), floori(p.y / FURL_R), floori(p.z / FURL_R))
		for dx in range(-1, 2):
			for dy in range(-1, 2):
				for dz in range(-1, 2):
					for j in _grid.get(k0 + Vector3i(dx, dy, dz), []):
						if j == i:
							continue
						var dv: Vector3 = sys.islands[j].global_position - p
						var below := -dv.dot(up)
						if below > 20.0 and (dv + up * below).length() < 260.0:
							clear = minf(clear, below - 60.0)    # (its deck and rock: the banner stays above them)
		_len[i] = clampf((clear - 40.0) / LEN, 0.08, 1.0)
		if _furl_i == 0:
			break
