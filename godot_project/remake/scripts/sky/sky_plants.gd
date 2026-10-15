extends RefCounted
class_name SkyPlants

## The warrens' plants (research/sky_islands/warrens/r4_design.md §6): every species a low-poly toon mesh (<= 250
## triangles) built here in code, once, and drawn as one MultiMesh per species per island quadrant (SkyWarren._plants:
## RenderingServer instances, not nodes).  The generator (tools/sky/warren, each civ's foliage()) writes the instances:
## [species, x, y, z, rot, scale] in the island frame.
##
## A species mesh: COLOR the part's colour (albedo); UV2.x the bend weight (0 at the root, 1 at the crown's top: the
## sway), UV2.y the flutter weight (leaves).  warren_foliage.gdshader sways it in its own frame (the wind turned by the
## instance's yaw, INSTANCE_CUSTOM.g), phased by INSTANCE_CUSTOM.r (hashed from the instance's place on the island) and
## tinted by the instance colour.
##
## Frames: a tree stands on y 0 at its origin.  A climber on a wall (WALL_HUNG) has the wall on its z 0 plane and grows
## toward +Z; a pergola spans its cell (x, z -1.5..1.5) at 2.7 m.

const MAX_TRIS := 250
## species hung on a wall face: the generator gives their house cell and face (rot 0..3 as radians); SkyWarren moves
## them out onto the face
const WALL_HUNG := ["bougainvillea", "jasmine", "banyan_wall", "ivy", "ivy_moss", "wisteria", "rose_climber"]
## species that cast shadows (the rest are low or flat)
const SHADOWS := ["date_palm", "fan_palm", "bitter_orange", "lemon", "fig", "olive", "cypress", "pine", "maple",
	"plane_tree", "willow", "banyan_tree", "bamboo", "banana", "grapevine_pergola"]

static var _arrays := {}             # species -> mesh arrays (built on a worker: SkyWarren._prepare)
static var _meshes := {}             # species -> ArrayMesh (made on the main thread from the arrays)
static var _mat: ShaderMaterial
static var _mutex := Mutex.new()


static func arrays(species: String) -> Array:
	## (any thread) the species' mesh arrays, built once
	_mutex.lock()
	var a = _arrays.get(species)
	_mutex.unlock()
	if a == null:
		a = _build(species).arrays()
		_mutex.lock()
		_arrays[species] = a
		_mutex.unlock()
	return a


static func mesh(species: String) -> ArrayMesh:
	## (main thread) the species' mesh, its material on
	var m: ArrayMesh = _meshes.get(species)
	if m == null:
		m = ArrayMesh.new()
		m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays(species))
		m.surface_set_material(0, material())
		_meshes[species] = m
	return m


static func material() -> ShaderMaterial:
	if _mat == null:
		_mat = ShaderMaterial.new()
		_mat.shader = preload("res://remake/shaders/warren_foliage.gdshader")
	return _mat


# ------------------------------------------------------------------ the builder
class MB:
	var v := PackedVector3Array()
	var n := PackedVector3Array()
	var c := PackedColorArray()
	var w := PackedVector2Array()        # bend, flutter
	var seed := 1

	func rnd() -> float:
		seed = (seed * 1103515245 + 12345) & 0x7fffffff
		return float(seed % 10000) / 10000.0

	func tri(a: Vector3, b: Vector3, cc: Vector3, na: Vector3, nb: Vector3, nc: Vector3, col: Color, wa: Vector2,
			wb: Vector2, wc: Vector2) -> void:
		## one triangle, wound so that its front faces the given normals (Godot: front faces clockwise)
		var face := (cc - a).cross(b - a)
		if face.dot(na + nb + nc) < 0.0:
			var t := b
			b = cc
			cc = t
			var tn := nb
			nb = nc
			nc = tn
			var tw := wb
			wb = wc
			wc = tw
		v.append_array([a, b, cc])
		n.append_array([na, nb, nc])
		c.append_array([col, col, col])
		w.append_array([wa, wb, wc])

	func flat(a: Vector3, b: Vector3, cc: Vector3, nrm: Vector3, col: Color, wa: Vector2, wb: Vector2, wc: Vector2) -> void:
		tri(a, b, cc, nrm, nrm, nrm, col, wa, wb, wc)

	func quad(a: Vector3, b: Vector3, cc: Vector3, d: Vector3, nrm: Vector3, col: Color, wa: Vector2, wb: Vector2,
			wc: Vector2, wd: Vector2) -> void:
		flat(a, b, cc, nrm, col, wa, wb, wc)
		flat(a, cc, d, nrm, col, wa, wc, wd)

	func cyl(a: Vector3, b: Vector3, r0: float, r1: float, sides: int, col: Color, w0: float, w1: float) -> void:
		## a tapered tube from a to b (no caps); r1 0: a cone
		var ax := (b - a).normalized()
		var u := ax.cross(Vector3.FORWARD if absf(ax.z) < 0.9 else Vector3.RIGHT).normalized()
		var vv := ax.cross(u)
		var top := col.lightened(0.08)
		for s in sides:
			var t0 := TAU * s / sides
			var t1 := TAU * (s + 1) / sides
			var d0 := u * cos(t0) + vv * sin(t0)
			var d1 := u * cos(t1) + vv * sin(t1)
			var p0 := a + d0 * r0
			var p1 := a + d1 * r0
			if r1 <= 0.0:
				tri(p0, p1, b, d0, d1, (d0 + d1).normalized(), col, Vector2(w0, 0), Vector2(w0, 0), Vector2(w1, 0))
			else:
				var q0 := b + d0 * r1
				var q1 := b + d1 * r1
				tri(p0, p1, q1, d0, d1, d1, col, Vector2(w0, 0), Vector2(w0, 0), Vector2(w1, 0))
				tri(p0, q1, q0, d0, d1, d0, top, Vector2(w0, 0), Vector2(w1, 0), Vector2(w1, 0))

	func blob(cen: Vector3, rad: Vector3, col: Color, wb: float, flutter := 0.6, sub := true) -> void:
		## a lumpy ellipsoid: an octahedron, split once (32 triangles; 8 unsplit), its corners jittered
		var o := [Vector3.RIGHT, Vector3.LEFT, Vector3.UP, Vector3.DOWN, Vector3.BACK, Vector3.FORWARD]
		var faces := [[0, 2, 4], [4, 2, 1], [1, 2, 5], [5, 2, 0], [0, 4, 3], [4, 1, 3], [1, 5, 3], [5, 0, 3]]
		var jit := {}
		var shade := col.darkened(0.18)
		for f in faces:
			var a: Vector3 = o[f[0]]
			var b: Vector3 = o[f[1]]
			var cc: Vector3 = o[f[2]]
			var tris := [[a, b, cc]]
			if sub:
				var ab := (a + b).normalized()
				var bc := (b + cc).normalized()
				var ca := (cc + a).normalized()
				tris = [[a, ab, ca], [ab, b, bc], [ca, bc, cc], [ab, bc, ca]]
			for t in tris:
				var ps := []
				var ns := []
				var ws := []
				for k in 3:
					var d: Vector3 = t[k]
					var key := Vector3i(roundi(d.x * 100), roundi(d.y * 100), roundi(d.z * 100))
					if not jit.has(key):
						jit[key] = 0.82 + rnd() * 0.3
					var p := cen + d * rad * float(jit[key])
					ps.append(p)
					ns.append((d / rad).normalized())
					ws.append(Vector2(wb * (0.85 + 0.15 * d.y), flutter))
				# (the underside a shade darker: the toon light alone reads flat)
				var under: bool = (t[0].y + t[1].y + t[2].y) < -0.5
				tri(ps[0], ps[1], ps[2], ns[0], ns[1], ns[2], shade if under else col, ws[0], ws[1], ws[2])

	func dot(cen: Vector3, r: float, col: Color, wb: float) -> void:
		## a fruit, a flower: an unsplit octahedron (8 triangles)
		blob(cen, Vector3(r, r, r), col, wb, 0.5, false)

	func frond(base: Vector3, dir: Vector3, length: float, width: float, droop: float, col: Color, wb: float,
			segs := 3) -> void:
		## a drooping leaf strip (palm frond, banana leaf): segs quads along a curve, widest in the middle
		dir = Vector3(dir.x, 0.0, dir.z).normalized() if Vector2(dir.x, dir.z).length() > 1e-3 else Vector3.RIGHT
		var side := dir.cross(Vector3.UP).normalized()
		var pts := []
		for k in segs + 1:
			var t := float(k) / segs
			pts.append([base + dir * length * t + Vector3.UP * (droop * 0.35 * t - droop * t * t), width * sin(PI * (0.12 + 0.76 * t)) * 0.5, t])
		for k in segs:
			var p0: Vector3 = pts[k][0]
			var p1: Vector3 = pts[k + 1][0]
			var h0: float = pts[k][1]
			var h1: float = pts[k + 1][1]
			var t0: float = pts[k][2]
			var t1: float = pts[k + 1][2]
			var nrm := (p1 - p0).cross(side).normalized()
			if nrm.y < 0.0:
				nrm = -nrm
			var c0 := col.lightened(0.06 * t0)
			quad(p0 - side * h0, p0 + side * h0, p1 + side * h1, p1 - side * h1, nrm, c0,
				Vector2(wb, t0), Vector2(wb, t0), Vector2(wb, t1), Vector2(wb, t1))

	func card(cen: Vector3, right: Vector3, up: Vector3, col: Color, w_bot: float, w_top: float, flutter := 0.8) -> void:
		## an upright card (reed, willow strand, leaf spray): cen at its middle, right and up its half extents
		var nrm := right.cross(up).normalized()
		quad(cen - right - up, cen + right - up, cen + right + up, cen - right + up, nrm, col,
			Vector2(w_bot, 0.0), Vector2(w_bot, 0.0), Vector2(w_top, flutter), Vector2(w_top, flutter))

	func box(lo: Vector3, hi: Vector3, col: Color, wb := 0.0) -> void:
		var c8 := []
		for k in 8:
			c8.append(Vector3(hi.x if k & 1 else lo.x, hi.y if k & 2 else lo.y, hi.z if k & 4 else lo.z))
		var faces := [[[0, 2, 6, 4], Vector3.LEFT], [[1, 5, 7, 3], Vector3.RIGHT], [[0, 4, 5, 1], Vector3.DOWN],
			[[2, 3, 7, 6], Vector3.UP], [[0, 1, 3, 2], Vector3.FORWARD], [[4, 6, 7, 5], Vector3.BACK]]
		for f in faces:
			var q: Array = f[0]
			var cl := col.darkened(0.12) if f[1] != Vector3.UP else col
			quad(c8[q[0]], c8[q[1]], c8[q[2]], c8[q[3]], f[1], cl, Vector2(wb, 0), Vector2(wb, 0), Vector2(wb, 0), Vector2(wb, 0))

	func tris() -> int:
		return v.size() / 3

	func arrays() -> Array:
		var a := []
		a.resize(Mesh.ARRAY_MAX)
		a[Mesh.ARRAY_VERTEX] = v
		a[Mesh.ARRAY_NORMAL] = n
		a[Mesh.ARRAY_COLOR] = c
		a[Mesh.ARRAY_TEX_UV2] = w
		return a


# ------------------------------------------------------------------ the species
const BARK := Color(0.42, 0.32, 0.24)
const BARK_GREY := Color(0.55, 0.52, 0.47)
const LEAF := Color(0.3, 0.5, 0.22)
const LEAF_DARK := Color(0.16, 0.34, 0.16)
const LEAF_GREY := Color(0.48, 0.56, 0.4)
const PALM := Color(0.36, 0.52, 0.22)


## the generator's other species (its civ modules' SPEC foliage lists), each as one of the shapes above with its own
## colours and size: [shape, {params}]
const C_GREEN := Color(0.3, 0.5, 0.22)
const KIN := {
	"acacia": ["umbrella", {"leaf": Color(0.42, 0.52, 0.24), "h": 3.2}],
	"kikar_acacia": ["umbrella", {"leaf": Color(0.4, 0.5, 0.22), "h": 2.8}],
	"ghaf": ["umbrella", {"leaf": Color(0.45, 0.55, 0.3), "h": 2.6}],
	"khejri": ["umbrella", {"leaf": Color(0.45, 0.55, 0.3), "h": 2.6}],
	"umbrella_pine": ["umbrella", {"leaf": Color(0.2, 0.36, 0.18), "h": 5.0}],
	"aleppo_pine": ["umbrella", {"leaf": Color(0.28, 0.42, 0.22), "h": 4.0}],
	"spruce": ["conifer", {"leaf": Color(0.14, 0.3, 0.2), "h": 7.0}],
	"pine_pruned": ["conifer", {"leaf": Color(0.2, 0.36, 0.2), "h": 3.0}],
	"italian_cypress": ["column", {"leaf": Color(0.13, 0.3, 0.15), "h": 8.0, "r": 0.6}],
	"poplar": ["column", {"leaf": Color(0.38, 0.55, 0.26), "h": 9.0, "r": 1.0}],
	"conocarpus": ["column", {"leaf": Color(0.3, 0.48, 0.24), "h": 4.5, "r": 0.9}],
	"almond": ["broad", {"leaf": Color(0.4, 0.55, 0.28), "bloom": Color(0.98, 0.85, 0.9), "h": 1.6}],
	"apricot": ["broad", {"leaf": Color(0.36, 0.52, 0.24), "fruit": Color(0.98, 0.6, 0.2), "h": 1.6}],
	"pear": ["broad", {"leaf": Color(0.34, 0.5, 0.22), "fruit": Color(0.8, 0.8, 0.3), "h": 1.8}],
	"pomegranate": ["broad", {"leaf": Color(0.3, 0.48, 0.2), "fruit": Color(0.78, 0.12, 0.12), "h": 1.2, "s": 0.7}],
	"mandarin": ["fruit", {"fruit": Color(0.98, 0.55, 0.1)}],
	"orange": ["fruit", {"fruit": Color(0.98, 0.52, 0.08)}],
	"lime_tree": ["fruit", {"fruit": Color(0.55, 0.78, 0.2)}],
	"mango": ["broad", {"leaf": Color(0.18, 0.38, 0.16), "h": 2.4, "s": 1.3}],
	"mulberry": ["broad", {"leaf": Color(0.3, 0.5, 0.2), "h": 2.0}],
	"walnut": ["broad", {"leaf": Color(0.3, 0.48, 0.22), "h": 2.6, "s": 1.3}],
	"chestnut": ["broad", {"leaf": Color(0.26, 0.44, 0.18), "h": 2.6, "s": 1.3}],
	"pistachio": ["broad", {"leaf": Color(0.4, 0.5, 0.26), "h": 1.4, "s": 0.8}],
	"elm": ["broad", {"leaf": Color(0.3, 0.48, 0.2), "h": 3.2, "s": 1.3}],
	"karagach_elm": ["broad", {"leaf": Color(0.32, 0.5, 0.22), "h": 3.0, "s": 1.2}],
	"zelkova": ["broad", {"leaf": Color(0.32, 0.5, 0.22), "h": 3.0, "s": 1.2}],
	"linden": ["broad", {"leaf": Color(0.36, 0.54, 0.24), "h": 3.0, "s": 1.25}],
	"chenar_plane": ["broad", {"leaf": Color(0.38, 0.52, 0.24), "h": 3.4, "s": 1.5, "bark": Color(0.66, 0.62, 0.5)}],
	"sycamore_fig": ["broad", {"leaf": Color(0.28, 0.46, 0.2), "h": 2.4, "s": 1.4}],
	"ficus": ["broad", {"leaf": Color(0.16, 0.36, 0.16), "h": 2.2, "s": 1.2, "bark": Color(0.55, 0.52, 0.47)}],
	"camphor": ["broad", {"leaf": Color(0.3, 0.5, 0.22), "h": 2.6, "s": 1.3}],
	"ginkgo": ["broad", {"leaf": Color(0.85, 0.72, 0.2), "h": 3.0, "s": 1.0}],
	"eucalyptus": ["broad", {"leaf": Color(0.5, 0.6, 0.48), "h": 4.0, "s": 1.0, "bark": Color(0.8, 0.76, 0.68)}],
	"neem": ["broad", {"leaf": Color(0.3, 0.5, 0.2), "h": 2.6, "s": 1.3}],
	"peepal": ["broad", {"leaf": Color(0.3, 0.52, 0.2), "h": 2.6, "s": 1.4, "bark": Color(0.55, 0.52, 0.47)}],
	"banyan": ["banyan", {}],
	"ashoka": ["column", {"leaf": Color(0.16, 0.36, 0.14), "h": 6.0, "r": 1.0}],
	"bel": ["broad", {"leaf": Color(0.34, 0.52, 0.22), "fruit": Color(0.7, 0.66, 0.3), "h": 2.0}],
	"sidr_ziziphus": ["broad", {"leaf": Color(0.4, 0.5, 0.28), "h": 1.8}],
	"molle": ["willowish", {"leaf": Color(0.38, 0.54, 0.26)}],
	"pepper_tree": ["willowish", {"leaf": Color(0.38, 0.54, 0.26)}],
	"queuna": ["broad", {"leaf": Color(0.3, 0.44, 0.24), "h": 1.6, "s": 0.8, "bark": Color(0.6, 0.35, 0.25)}],
	"tamarisk": ["shrub", {"leaf": Color(0.5, 0.58, 0.42), "bloom": Color(0.9, 0.7, 0.8), "r": 1.3}],
	"ceiba": ["broad", {"leaf": Color(0.3, 0.5, 0.22), "h": 4.5, "s": 1.6, "bark": Color(0.55, 0.6, 0.5)}],
	"jacaranda": ["broad", {"leaf": Color(0.52, 0.42, 0.78), "bloom": Color(0.6, 0.48, 0.86), "h": 2.6, "s": 1.3}],
	"flamboyant": ["broad", {"leaf": Color(0.82, 0.22, 0.12), "bloom": Color(0.95, 0.35, 0.1), "h": 2.6, "s": 1.4}],
	"gulmohar": ["broad", {"leaf": Color(0.85, 0.28, 0.12), "bloom": Color(0.98, 0.45, 0.12), "h": 2.6, "s": 1.4}],
	"bauhinia": ["broad", {"leaf": Color(0.32, 0.5, 0.22), "bloom": Color(0.9, 0.5, 0.75), "h": 2.0}],
	"sakura": ["broad", {"leaf": Color(0.96, 0.78, 0.84), "bloom": Color(1.0, 0.88, 0.92), "h": 2.0, "s": 1.1}],
	"japanese_maple": ["broad", {"leaf": Color(0.78, 0.18, 0.12), "h": 1.4, "s": 0.8}],
	"wisteria": ["climber", {"leaf": Color(0.3, 0.48, 0.2), "bloom": Color(0.6, 0.5, 0.86)}],
	"ivy": ["climber", {"leaf": Color(0.18, 0.36, 0.16), "bloom": Color(0.2, 0.4, 0.18)}],
	"ivy_moss": ["climber", {"leaf": Color(0.22, 0.4, 0.18), "bloom": Color(0.36, 0.5, 0.22)}],
	"rose_climber": ["climber", {"leaf": Color(0.26, 0.44, 0.2), "bloom": Color(0.86, 0.2, 0.3)}],
	"caper_plant": ["shrub", {"leaf": Color(0.36, 0.5, 0.28), "bloom": Color(0.96, 0.92, 0.95), "r": 0.6}],
	"oleander": ["shrub", {"leaf": Color(0.26, 0.42, 0.2), "bloom": Color(0.95, 0.5, 0.65), "r": 1.0}],
	"hibiscus": ["shrub", {"leaf": Color(0.22, 0.42, 0.18), "bloom": Color(0.9, 0.12, 0.2), "r": 0.8}],
	"henna": ["shrub", {"leaf": Color(0.34, 0.48, 0.24), "r": 0.8}],
	"qat_shrub": ["shrub", {"leaf": Color(0.3, 0.46, 0.22), "r": 0.9}],
	"lilac": ["shrub", {"leaf": Color(0.3, 0.46, 0.22), "bloom": Color(0.72, 0.58, 0.86), "r": 1.0}],
	"rhododendron": ["shrub", {"leaf": Color(0.2, 0.36, 0.18), "bloom": Color(0.86, 0.3, 0.55), "r": 1.0}],
	"lavender": ["spikes", {"leaf": Color(0.45, 0.52, 0.4), "bloom": Color(0.55, 0.45, 0.8)}],
	"hollyhock": ["spikes", {"leaf": Color(0.3, 0.48, 0.22), "bloom": Color(0.9, 0.4, 0.6), "h": 1.8}],
	"marigold": ["beds", {"leaf": Color(0.3, 0.48, 0.2), "bloom": Color(0.98, 0.6, 0.1)}],
	"rose_beds": ["beds", {"leaf": Color(0.26, 0.42, 0.18), "bloom": Color(0.86, 0.2, 0.3)}],
	"alfalfa_beds": ["beds", {"leaf": Color(0.42, 0.6, 0.26)}],
	"maqshama_vegetable_beds": ["beds", {"leaf": Color(0.36, 0.56, 0.24), "bloom": Color(0.85, 0.25, 0.15)}],
	"roof_moss_ferns": ["moss", {"leaf": Color(0.3, 0.46, 0.2)}],
	"totora_reeds": ["reeds", {}],
	"betel_palm": ["palm", {"kind": "betel"}],
	"royal_palm": ["palm", {"kind": "coconut_palm"}],
	"doum_palm": ["palm", {"kind": "fan_palm"}],
	"palm_fan": ["palm", {"kind": "fan_palm"}],
	"papaya": ["banana", {"fruit": Color(0.6, 0.7, 0.2)}],
	"basil_pots": ["pots", {"kind": "pot_mint_geranium"}],
	"herb_pots": ["pots", {"kind": "pot_mint_geranium"}],
	"pot_herbs": ["pots", {"kind": "pot_mint_geranium"}],
	"tulsi_pots": ["pots", {"kind": "pot_mint_geranium"}],
	"pot_geranium": ["pots", {"kind": "pot_mint_geranium"}],
	"geranium_pot": ["pots", {"kind": "pot_mint_geranium"}],
	"geranium_tins": ["pots", {"kind": "potted_plants"}],
	"marigold_pots": ["pots", {"kind": "pot_mint_geranium"}],
	"fern_pot": ["pots", {"kind": "roof_garden"}],
	"monstera_pot": ["pots", {"kind": "roof_garden"}],
	"lemon_tub": ["pots", {"kind": "pot_mint_geranium"}],
	"bougainvillea_pot": ["pots", {"kind": "pot_mint_geranium"}],
	"tulsi_stand": ["pots", {"kind": "roof_garden"}],
	"drying_chilli_corn": ["rack", {}],
}


static func _build(sp: String) -> MB:
	var b := MB.new()
	b.seed = absi(sp.hash()) % 100000 + 7
	if KIN.has(sp):
		_kin(b, KIN[sp][0], KIN[sp][1], sp)
		if b.tris() > MAX_TRIS:
			push_warning("SkyPlants: %s has %d triangles (> %d)" % [sp, b.tris(), MAX_TRIS])
		return b
	match sp:
		"date_palm", "fan_palm", "coconut_palm":
			_palm(b, sp)
		"bitter_orange", "lemon", "citrus", "orange":
			_citrus(b, Color(0.95, 0.5, 0.08) if sp != "lemon" else Color(0.98, 0.86, 0.2))
		"fig":
			_broadleaf(b, BARK_GREY, Color(0.26, 0.44, 0.18), 2.0, 3, Vector3(1.9, 1.2, 1.9))
		"olive":
			_broadleaf(b, BARK_GREY.darkened(0.15), LEAF_GREY, 1.4, 3, Vector3(1.4, 1.0, 1.4), 0.45)
		"maple":
			_broadleaf(b, BARK, Color(0.78, 0.3, 0.12), 2.4, 3, Vector3(1.8, 1.5, 1.8))
		"plane_tree":
			_broadleaf(b, Color(0.66, 0.62, 0.5), Color(0.38, 0.52, 0.24), 3.2, 3, Vector3(2.4, 1.9, 2.4))
		"cypress":
			b.cyl(Vector3.ZERO, Vector3(0, 0.8, 0), 0.16, 0.12, 5, BARK, 0.0, 0.05)
			b.blob(Vector3(0, 3.6, 0), Vector3(0.75, 3.2, 0.75), LEAF_DARK, 0.6, 0.3)
			b.blob(Vector3(0, 6.4, 0), Vector3(0.4, 1.2, 0.4), LEAF_DARK.lightened(0.05), 1.0, 0.3)
		"pine":
			b.cyl(Vector3.ZERO, Vector3(0, 6.0, 0), 0.22, 0.08, 5, BARK, 0.0, 0.6)
			for k in 4:
				var y := 2.2 + k * 1.3
				var r := 2.0 - k * 0.42
				b.cyl(Vector3(0, y, 0), Vector3(0, y + 2.0, 0), r, 0.0, 7, LEAF_DARK.lightened(0.04 * k), 0.3 + 0.2 * k, 0.5 + 0.2 * k)
		"willow":
			b.cyl(Vector3.ZERO, Vector3(0.3, 2.6, 0), 0.28, 0.18, 5, BARK, 0.0, 0.3)
			b.blob(Vector3(0.3, 4.2, 0), Vector3(2.4, 1.6, 2.4), Color(0.48, 0.62, 0.26), 0.7)
			for k in 18:
				var a := TAU * k / 18 + b.rnd() * 0.3
				var r := 2.1 + b.rnd() * 0.4
				var cen := Vector3(0.3 + cos(a) * r, 2.6 + b.rnd() * 0.5, sin(a) * r)
				var right := Vector3(-sin(a), 0, cos(a)) * 0.35
				b.card(cen, right, Vector3(0, 1.5, 0), Color(0.5, 0.66, 0.28).darkened(b.rnd() * 0.15), 0.9, 0.6, 1.0)
		"banyan_tree":
			b.cyl(Vector3.ZERO, Vector3(0, 3.0, 0), 0.75, 0.5, 6, BARK_GREY, 0.0, 0.1)
			for k in 6:
				var a := TAU * k / 6 + b.rnd() * 0.5
				var r := 1.6 + b.rnd() * 1.6
				b.cyl(Vector3(cos(a) * r, 0, sin(a) * r), Vector3(cos(a) * r * 0.8, 4.0, sin(a) * r * 0.8), 0.12, 0.08, 4, BARK_GREY.lightened(0.05), 0.0, 0.2)
			b.blob(Vector3(0, 4.8, 0), Vector3(3.6, 1.5, 3.6), LEAF_DARK, 0.4)
			b.blob(Vector3(1.6, 5.6, 0.8), Vector3(2.4, 1.2, 2.2), LEAF_DARK.lightened(0.08), 0.5)
			b.blob(Vector3(-1.4, 5.4, -1.2), Vector3(2.2, 1.2, 2.4), LEAF.darkened(0.1), 0.5)
		"banyan_wall":
			for k in 7:
				var x := -1.2 + k * 0.4 + b.rnd() * 0.2
				var top := Vector3(x * 0.6, 3.0, 0.15)
				b.cyl(Vector3(x, 0.0, 0.08), Vector3(x + (b.rnd() - 0.5) * 0.4, 1.5, 0.1), 0.05, 0.06, 4, BARK_GREY, 0.0, 0.05)
				b.cyl(Vector3(x + (b.rnd() - 0.5) * 0.4, 1.5, 0.1), top, 0.06, 0.09, 4, BARK_GREY, 0.05, 0.1)
			b.blob(Vector3(0, 3.3, 0.6), Vector3(1.6, 0.9, 0.7), LEAF_DARK, 0.4)
			b.blob(Vector3(0.9, 2.6, 0.45), Vector3(0.8, 0.6, 0.5), LEAF, 0.4)
		"bougainvillea", "jasmine", "ivy":
			var leaf := Color(0.24, 0.44, 0.18)
			var bloom := Color(0.86, 0.16, 0.52) if sp == "bougainvillea" else Color(0.96, 0.95, 0.9)
			# (flat against the wall: a climber, not a tree)
			b.cyl(Vector3(0, 0, 0.06), Vector3(0.2, 1.3, 0.08), 0.045, 0.035, 4, BARK, 0.0, 0.05)
			b.blob(Vector3(0.1, 2.2, 0.2), Vector3(1.4, 0.9, 0.2), bloom if sp == "bougainvillea" else leaf, 0.3)
			b.blob(Vector3(-0.6, 1.4, 0.16), Vector3(0.8, 0.7, 0.17), leaf, 0.25)
			b.blob(Vector3(0.9, 2.9, 0.16), Vector3(0.9, 0.5, 0.17), bloom.lerp(leaf, 0.35) if sp == "bougainvillea" else leaf.lightened(0.06), 0.35)
			if sp == "jasmine":
				for k in 12:
					b.dot(Vector3(-1.0 + b.rnd() * 2.2, 1.1 + b.rnd() * 2.0, 0.36 + b.rnd() * 0.06), 0.06, bloom, 0.3)
		"grapevine_pergola":
			var wood := Color(0.45, 0.33, 0.22)
			for x in [-1.3, 1.3]:
				for z in [-1.3, 1.3]:
					b.box(Vector3(x - 0.06, 0, z - 0.06), Vector3(x + 0.06, 2.75, z + 0.06), wood)
			for z in [-1.3, 1.3]:
				b.box(Vector3(-1.45, 2.75, z - 0.06), Vector3(1.45, 2.87, z + 0.06), wood)
			b.cyl(Vector3(1.3, 0, 1.3), Vector3(0.6, 2.9, 0.6), 0.07, 0.05, 4, BARK, 0.0, 0.1)
			b.blob(Vector3(0, 3.0, 0), Vector3(1.6, 0.28, 1.6), Color(0.32, 0.5, 0.2), 0.15)
			b.blob(Vector3(0.7, 2.95, 0.6), Vector3(0.9, 0.3, 0.8), Color(0.38, 0.56, 0.22), 0.15)
			for k in 6:
				var cen := Vector3(-1.1 + b.rnd() * 2.2, 2.6, -1.1 + b.rnd() * 2.2)
				b.dot(cen, 0.12, Color(0.36, 0.16, 0.36), 0.3)
		"pot_mint_geranium", "potted_plants", "roof_garden":
			_pots(b, sp)
		"reeds":
			for k in 22:
				var a := b.rnd() * TAU
				var r := b.rnd() * 0.9
				var h := 0.4 + b.rnd() * 0.35
				var cen := Vector3(cos(a) * r, h, sin(a) * r)
				var yaw := b.rnd() * PI
				var lean := Vector3(cos(a), 0, sin(a)) * 0.15 * b.rnd()
				b.card(cen + lean, Vector3(cos(yaw), 0, sin(yaw)) * 0.035, Vector3(0, h, 0) + lean, Color(0.5, 0.6, 0.28).darkened(b.rnd() * 0.25), 0.0, 0.8, 1.0)
				if k % 3 == 0:
					b.dot(cen + Vector3(0, h * 0.9, 0), 0.06, Color(0.4, 0.26, 0.14), 0.8)
		"bamboo":
			for k in 7:
				var a := b.rnd() * TAU
				var r := b.rnd() * 0.6
				var base := Vector3(cos(a) * r, 0, sin(a) * r)
				var lean := Vector3(cos(a), 0, sin(a)) * (0.4 + b.rnd() * 0.8)
				var h := 5.0 + b.rnd() * 2.0
				var col := Color(0.45, 0.58, 0.26).lerp(Color(0.62, 0.62, 0.32), b.rnd() * 0.5)
				var p := base
				for s in 3:
					var q := base + lean * (s + 1) / 3.0 * ((s + 1) / 3.0) + Vector3(0, h * (s + 1) / 3.0, 0)
					b.cyl(p, q, 0.06, 0.055, 4, col, 0.3 * s, 0.3 * (s + 1))
					p = q
				for s in 2:
					var yaw := b.rnd() * TAU
					b.card(p - Vector3(0, 0.8 + s * 1.2, 0), Vector3(cos(yaw), 0, sin(yaw)) * 0.7, Vector3(0, 0.5, 0), LEAF.lightened(0.05), 0.8, 1.0, 1.0)
		"banana":
			b.cyl(Vector3.ZERO, Vector3(0, 2.2, 0), 0.16, 0.12, 6, Color(0.46, 0.5, 0.26), 0.0, 0.3)
			for k in 7:
				var a := TAU * k / 7 + b.rnd() * 0.4
				b.frond(Vector3(0, 2.1 + b.rnd() * 0.3, 0), Vector3(cos(a), 0, sin(a)), 2.0, 0.8, 0.9, Color(0.4, 0.62, 0.22), 0.5, 3)
		"lotus", "water_plants":
			for k in 7:
				var a := b.rnd() * TAU
				var r := 0.3 + b.rnd() * 1.0
				var cen := Vector3(cos(a) * r, 0.02, sin(a) * r)
				var pr := 0.25 + b.rnd() * 0.15
				for s in 5:
					var t0 := TAU * s / 5
					var t1 := TAU * (s + 1) / 5
					b.flat(cen, cen + Vector3(cos(t0), 0, sin(t0)) * pr, cen + Vector3(cos(t1), 0, sin(t1)) * pr, Vector3.UP,
						Color(0.3, 0.52, 0.26), Vector2(0.1, 0.2), Vector2(0.1, 0.2), Vector2(0.1, 0.2))
			for k in 2:
				var cen := Vector3(b.rnd() - 0.5, 0.0, b.rnd() - 0.5)
				b.cyl(cen, cen + Vector3(0, 0.35, 0), 0.0001, 0.14, 5, Color(0.96, 0.62, 0.74), 0.0, 0.3)
		_:
			# an unknown species: a plain shrub (and say so once)
			push_warning("SkyPlants: no mesh for species '%s' (a shrub stands in)" % sp)
			b.blob(Vector3(0, 0.7, 0), Vector3(0.8, 0.7, 0.8), LEAF, 0.4)
	if b.tris() > MAX_TRIS:
		push_warning("SkyPlants: %s has %d triangles (> %d)" % [sp, b.tris(), MAX_TRIS])
	return b


static func _kin(b: MB, shape: String, p: Dictionary, sp: String) -> void:
	var leaf: Color = p.get("leaf", C_GREEN)
	var bloom = p.get("bloom")
	var h: float = p.get("h", 2.0)
	var sc: float = p.get("s", 1.0)
	match shape:
		"broad":
			_broadleaf(b, p.get("bark", BARK), leaf, h, 3, Vector3(1.6, 1.2, 1.6) * sc)
			var dots = bloom if bloom != null else p.get("fruit")
			if dots != null:
				for k in 12:
					var a := b.rnd() * TAU
					var r := 1.3 * sc * (0.6 + b.rnd() * 0.4)
					b.dot(Vector3(cos(a) * r, h + 1.0 * sc + b.rnd() * 1.4 * sc, sin(a) * r), 0.1 if bloom == null else 0.16, dots, 0.6)
		"fruit":
			_citrus(b, p.get("fruit", Color(0.95, 0.5, 0.08)))
		"umbrella":
			b.cyl(Vector3.ZERO, Vector3(0.3, h, 0.1), 0.2, 0.14, 5, BARK, 0.0, 0.3)
			b.cyl(Vector3(0.3, h, 0.1), Vector3(-0.6, h + 0.6, 0.4), 0.1, 0.07, 4, BARK, 0.3, 0.5)
			b.blob(Vector3(0.1, h + 0.9, 0.1), Vector3(2.6, 0.6, 2.4), leaf, 0.5)
			b.blob(Vector3(-0.8, h + 1.1, 0.5), Vector3(1.4, 0.45, 1.3), leaf.lightened(0.06), 0.6)
		"conifer":
			b.cyl(Vector3.ZERO, Vector3(0, h, 0), 0.2, 0.06, 5, BARK, 0.0, 0.6)
			for k in 4:
				var y := h * (0.25 + 0.17 * k)
				var r := h * (0.24 - 0.045 * k)
				b.cyl(Vector3(0, y, 0), Vector3(0, y + h * 0.32, 0), r, 0.0, 7, leaf.lightened(0.04 * k), 0.3 + 0.2 * k, 0.5 + 0.2 * k)
		"column":
			var r: float = p.get("r", 0.7)
			b.cyl(Vector3.ZERO, Vector3(0, 0.8, 0), 0.15, 0.12, 5, BARK, 0.0, 0.05)
			b.blob(Vector3(0, h * 0.5, 0), Vector3(r, h * 0.45, r), leaf, 0.6, 0.3)
			b.blob(Vector3(0, h * 0.85, 0), Vector3(r * 0.55, h * 0.18, r * 0.55), leaf.lightened(0.05), 1.0, 0.3)
		"willowish":
			b.cyl(Vector3.ZERO, Vector3(0.2, 2.2, 0), 0.22, 0.15, 5, BARK, 0.0, 0.3)
			b.blob(Vector3(0.2, 3.4, 0), Vector3(2.0, 1.2, 2.0), leaf, 0.7)
			for k in 14:
				var a := TAU * k / 14 + b.rnd() * 0.3
				var cen := Vector3(0.2 + cos(a) * 1.8, 2.4, sin(a) * 1.8)
				b.card(cen, Vector3(-sin(a), 0, cos(a)) * 0.3, Vector3(0, 1.0, 0), leaf.darkened(b.rnd() * 0.15), 0.9, 0.6, 1.0)
		"banyan":
			_build_into(b, "banyan_tree")
		"shrub":
			var r: float = p.get("r", 0.9)
			b.blob(Vector3(0, r * 0.8, 0), Vector3(r, r * 0.8, r), leaf, 0.3)
			b.blob(Vector3(r * 0.5, r * 1.2, r * 0.2), Vector3(r * 0.6, r * 0.5, r * 0.6), leaf.lightened(0.05), 0.4)
			if bloom != null:
				for k in 14:
					var a := b.rnd() * TAU
					var e := b.rnd() * 1.2
					b.dot(Vector3(cos(a) * r * cos(e) * 0.95, r * 0.8 + sin(e) * r * 0.8, sin(a) * r * cos(e) * 0.95), 0.08, bloom, 0.4)
		"climber":
			b.cyl(Vector3(0, 0, 0.06), Vector3(0.2, 1.3, 0.08), 0.045, 0.035, 4, BARK, 0.0, 0.05)
			b.blob(Vector3(0.1, 2.2, 0.2), Vector3(1.4, 0.9, 0.2), leaf, 0.3)
			b.blob(Vector3(-0.6, 1.4, 0.16), Vector3(0.8, 0.7, 0.17), leaf.darkened(0.08), 0.25)
			if bloom != null:
				for k in 14:
					b.dot(Vector3(-1.1 + b.rnd() * 2.4, 1.2 + b.rnd() * 1.8, 0.34 + b.rnd() * 0.06), 0.08, bloom, 0.3)
		"spikes":
			for k in 7:
				var cen := Vector3((b.rnd() - 0.5) * 1.2, 0, (b.rnd() - 0.5) * 1.2)
				var hh := h * (0.5 + b.rnd() * 0.5)
				b.cyl(cen, cen + Vector3(0, hh, 0), 0.03, 0.02, 3, leaf, 0.0, 0.8)
				if bloom != null:
					b.dot(cen + Vector3(0, hh * 0.85, 0), 0.08, bloom, 0.8)
					b.dot(cen + Vector3(0, hh * 0.65, 0), 0.07, bloom, 0.6)
		"beds":
			b.box(Vector3(-1.3, 0, -0.5), Vector3(1.3, 0.25, 0.5), Color(0.5, 0.38, 0.26))
			for k in 3:
				b.blob(Vector3(-0.85 + k * 0.85, 0.36, 0), Vector3(0.42, 0.18, 0.4), leaf.lightened(0.04 * k), 0.2, 0.6, false)
			if bloom != null:
				for k in 10:
					b.dot(Vector3(-1.2 + b.rnd() * 2.4, 0.5, -0.35 + b.rnd() * 0.7), 0.06, bloom, 0.3)
		"moss":
			for k in 3:
				b.blob(Vector3((b.rnd() - 0.5) * 1.6, 0.05, (b.rnd() - 0.5) * 1.6), Vector3(0.7, 0.12, 0.6), leaf.lightened(0.05 * k), 0.1, 0.4)
		"reeds":
			_build_into(b, "reeds")
		"palm":
			if str(p.kind) == "betel":
				_palm(b, "fan_palm")
			else:
				_palm(b, str(p.kind))
		"banana":
			_build_into(b, "banana")
			for k in 4:
				var a := TAU * k / 4
				b.dot(Vector3(cos(a) * 0.2, 1.8, sin(a) * 0.2), 0.1, p.get("fruit", C_GREEN), 0.4)
		"pots":
			_pots(b, str(p.kind))
		"rack":
			var wood := Color(0.45, 0.33, 0.22)
			b.box(Vector3(-1.0, 0, -0.05), Vector3(-0.92, 2.0, 0.05), wood)
			b.box(Vector3(0.92, 0, -0.05), Vector3(1.0, 2.0, 0.05), wood)
			b.box(Vector3(-1.0, 1.9, -0.04), Vector3(1.0, 1.96, 0.04), wood)
			for k in 16:
				b.dot(Vector3(-0.85 + k * 0.11, 1.65 - (k % 3) * 0.15, 0.0), 0.07,
					Color(0.85, 0.12, 0.08) if k % 2 == 0 else Color(0.95, 0.75, 0.2), 0.5)


static func _build_into(b: MB, sp: String) -> void:
	## (a KIN shape that is one of the plain species) built into b
	var o := _build(sp)
	b.v.append_array(o.v)
	b.n.append_array(o.n)
	b.c.append_array(o.c)
	b.w.append_array(o.w)


static func _palm(b: MB, sp: String) -> void:
	var h := 7.0 if sp == "date_palm" else (9.0 if sp == "fan_palm" else 8.0)
	var lean := Vector3(0.9, 0, 0.3) if sp != "fan_palm" else Vector3(0.2, 0, 0.1)
	var p := Vector3.ZERO
	var r := 0.3 if sp == "date_palm" else 0.24
	for s in 4:
		var t := (s + 1) / 4.0
		var q := lean * t * t + Vector3(0, h * t, 0)
		b.cyl(p, q, r, r * 0.92, 5, Color(0.5, 0.4, 0.3).darkened(0.05 * (s % 2)), 0.25 * s, 0.25 * (s + 1))
		p = q
		r *= 0.92
	var nf := 12 if sp != "fan_palm" else 11
	for k in nf:
		var a := TAU * k / nf + b.rnd() * 0.25
		var up := 0.6 if k % 2 == 0 else 0.0
		if sp == "fan_palm":
			b.frond(p + Vector3(0, 0.1, 0), Vector3(cos(a), 0, sin(a)), 1.6, 1.3, 0.4 + up * 0.3, PALM.darkened(0.1), 1.0, 2)
		else:
			b.frond(p + Vector3(0, 0.2, 0), Vector3(cos(a), 0, sin(a)), 3.0, 0.75, 1.5 - up, PALM.lerp(LEAF_GREY, 0.3 * (k % 3) / 2.0), 1.0, 3)
	if sp == "fan_palm":
		b.cyl(p - Vector3(0, 1.4, 0), p, 0.6, 0.35, 6, Color(0.55, 0.47, 0.33), 0.9, 1.0)     # (the dead skirt)
	else:
		for k in 3:
			var a := TAU * k / 3 + 0.4
			b.dot(p + Vector3(cos(a) * 0.45, -0.5, sin(a) * 0.45), 0.22, Color(0.84, 0.5, 0.12), 1.0)


static func _citrus(b: MB, fruit: Color) -> void:
	b.cyl(Vector3.ZERO, Vector3(0.05, 1.3, 0), 0.12, 0.09, 5, BARK, 0.0, 0.2)
	b.cyl(Vector3(0.05, 1.3, 0), Vector3(0.0, 2.0, 0.05), 0.09, 0.06, 4, BARK, 0.2, 0.4)
	b.blob(Vector3(0, 2.3, 0), Vector3(1.35, 1.1, 1.35), Color(0.2, 0.42, 0.18), 0.5)
	b.blob(Vector3(0.5, 2.9, 0.3), Vector3(0.8, 0.7, 0.8), Color(0.26, 0.48, 0.2), 0.7)
	b.blob(Vector3(-0.5, 2.7, -0.4), Vector3(0.7, 0.6, 0.7), Color(0.22, 0.44, 0.18), 0.65)
	for k in 10:
		var a := b.rnd() * TAU
		var y := 1.7 + b.rnd() * 1.2
		var r := 1.15 * sqrt(maxf(0.0, 1.0 - pow((y - 2.3) / 1.1, 2.0))) + 0.06
		b.dot(Vector3(cos(a) * r, y, sin(a) * r), 0.09, fruit, 0.6)


static func _broadleaf(b: MB, bark: Color, leaf: Color, trunk_h: float, n: int, crown: Vector3, twist := 0.15) -> void:
	var top := Vector3(twist, trunk_h, 0.0)
	b.cyl(Vector3.ZERO, top, 0.24, 0.17, 5, bark, 0.0, 0.25)
	for k in n:
		var a := TAU * k / n + b.rnd() * 0.6
		var d := Vector3(cos(a), 0, sin(a))
		var tip := top + d * crown.x * 0.55 + Vector3(0, crown.y * 0.7, 0)
		b.cyl(top, tip, 0.12, 0.06, 4, bark, 0.25, 0.5)
		b.blob(tip + Vector3(0, crown.y * 0.2, 0), crown * (0.62 + b.rnd() * 0.15), leaf.lightened(0.05 * k) if k % 2 else leaf, 0.6)


static func _pots(b: MB, sp: String) -> void:
	var kow := sp == "potted_plants"
	var n := 4 if kow else 3
	for k in n:
		var a := TAU * k / n + b.rnd() * 0.5
		var r := 0.45 + b.rnd() * 0.3
		var cen := Vector3(cos(a) * r, 0, sin(a) * r)
		var pr := 0.18 + b.rnd() * 0.08
		var ph := 0.3 + b.rnd() * 0.15
		if kow and k % 2 == 1:
			# a polystyrene box or a paint bucket
			b.box(cen - Vector3(0.25, 0, 0.18), cen + Vector3(0.25, ph, 0.18), Color(0.9, 0.9, 0.86))
		else:
			b.cyl(cen, cen + Vector3(0, ph, 0), pr * 0.8, pr, 6, Color(0.72, 0.38, 0.22) if not kow else Color(0.3, 0.42, 0.62), 0.0, 0.0)
		var lc := LEAF.lightened(b.rnd() * 0.1)
		if sp == "roof_garden":
			lc = Color(0.36, 0.56, 0.22)
		b.blob(cen + Vector3(0, ph + 0.18, 0), Vector3(pr * 1.4, 0.22, pr * 1.4), lc, 0.3, 0.8)
		if sp == "pot_mint_geranium" and k != 1:
			for s in 3:
				b.dot(cen + Vector3((b.rnd() - 0.5) * 0.3, ph + 0.36, (b.rnd() - 0.5) * 0.3), 0.06, Color(0.9, 0.16, 0.2), 0.4)
