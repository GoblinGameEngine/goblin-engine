extends Node3D
class_name SkySigns

## An island's lights after dark (research/sky_islands/architecture/00_brief.md; the user, 2026-10-14: "lots and lots of
## lights with billboards and flashing signs ... light up like a christmas tree ... Each store has it's own light up
## stylized sign. Each apartment complex has mood lighting and a stylish motif").  Built with the island's near tier,
## a building or two a frame, into a handful of merged meshes -- so an island lit up is a few draw calls:
##   neon   every glowing tube, letter, lightbox face and LED strip (sky_neon.gdshader: additive, animated per vertex)
##   led    the dot-matrix boards' scrolling messages (sky_led.gdshader, this island's message strip SkyDotFont draws)
##   wash   light thrown on walls: uplights and spotlights (sky_wash.gdshader)
##   solid  sign boards, frames, posts, brass and painted letters (lit, vertex colours)
##   bulbs  string lights, lanterns, chase bulbs, pad lights (one MultiMesh, sky_bulbs.gdshader)
##
## Where: a building's sign and light anchors come from its model (layout "models"[m].anchors: [name, x, y, z, yaw] --
## sign_<kind>_<w>x<h>, glow_<motif>_<n>, lights_<n>, the brief's contract) when the generator has written them;
## otherwise they're derived from the building's lot (the fallback, today's SKY-M models): its front (local -Z, the
## door side) gets a storefront sign per ~7 m on shops and markets (and on many dwellings' ground floors: commerce
## islands), tall buildings get vertical blade signs at the front corners, some a rooftop billboard facing out over
## the rim; every building gets a mood colour and two lighting motifs.  Then string lights between neighbouring
## roofs, along the fence, up the balloon tethers, round the lark pads.
## Names and messages: deterministic, from the island's canon (its trade, specialty, clan, the Skein's slang).

const FONTS := ["res://remake/fonts/NotoSans-Bold.ttf", "res://remake/fonts/NotoSerif-Bold.ttf"]
## the island's people (sky_islands.json "heritage") -> [lettering, accent]: SIGNS' table (tools/signs/make_flags.py
## HERITAGE).  A warren shop sign blends both sides (the user: "it shows how cultures mixed"): the warren family's
## blank is the frame and ground, the name is lettered in the heritage's face, and a share of shops (by hash) glow in
## the heritage accent.  Fonts: remake/fonts/heritage/ (OFL).
const HERITAGE := {"anglo": ["Cinzel", "#1f3a68"], "hispanic": ["Lobster-Regular", "#d9a521"],
	"francophone": ["PlayfairDisplay", "#2b5aa8"], "multi": ["Righteous-Regular", "#8a4fb8"],
	"black_anglo": ["AlfaSlabOne-Regular", "#2f7d3a"], "german": ["OldStandard-Bold", "#303030"],
	"east_asian": ["DelaGothicOne-Regular", "#c8302a"], "irish_scots": ["UncialAntiqua-Regular", "#2f8a5a"],
	"greek": ["Marcellus-Regular", "#3a7cc0"], "polish": ["Oswald", "#c8203a"], "black": ["Shrikhand-Regular", "#d07a1a"],
	"italian": ["PlayfairDisplay", "#3a8a4a"], "arab": ["ArefRuqaa-Bold", "#1a7a6a"], "indigenous": ["CarterOne", "#9a4a2a"],
	"station_coined": ["Bungee-Regular", "#c0c0c8"], "se_asian": ["Chonburi-Regular", "#e0b020"],
	"scandinavian": ["JosefinSlab", "#2a4a8a"], "south_asian": ["YatraOne-Regular", "#e07a1a"],
	"slavic": ["RuslanDisplay-Regular", "#3a5aa8"], "hungarian": ["Arvo-Bold", "#6a8a3a"]}
const ACCENT_SHARE := 0.4            # shops whose name glows in the heritage accent (the rest: the lane's neon)
const SIGN_RANGE := 1400.0
const BULB_RANGE := 900.0
const STOREY := 3.1
const LAMP_EVERY := 16.0

const KINDS := ["neon_script", "lightbox", "dot_matrix", "chochin", "brass", "painted", "neon_frame", "video", "figure"]
const NEON := [Color(1.0, 0.18, 0.45), Color(0.2, 0.85, 1.0), Color(1.0, 0.75, 0.2), Color(0.45, 1.0, 0.35),
	Color(0.75, 0.35, 1.0), Color(1.0, 0.35, 0.15), Color(1.0, 0.95, 0.85), Color(0.3, 0.45, 1.0)]
const MOODS := [Color("#ffb35c"), Color("#ff7aa8"), Color("#3fe0d0"), Color("#9a6bff"), Color("#ffe2b0"), Color("#dfe9ff"),
	Color(1.0, 0.4, 0.3), Color(0.5, 0.9, 0.3)]           # (b_signs_and_light.md: the apartment moods, and two more)
const MOTIFS := ["floor_lines", "corners", "crown", "lanterns", "uplights", "zigzag", "festoons", "window_glow"]
## the research catalogue's names (styles_*.json signage.kinds / night.motifs) -> what's drawn: first matching key wins
const KIND_MAP := [["video", "video"], ["dotmatrix", "dot_matrix"], ["dot_matrix", "dot_matrix"], ["figure", "figure"], ["led", "dot_matrix"], ["blade", "blade"],
	["vertical", "stack"], ["stack", "stack"], ["marquee", "neon_frame"], ["double", "neon_frame"], ["neon", "neon_script"],
	["directory", "lightbox"], ["clock", "lightbox"], ["tile", "lightbox"], ["mosaic", "lightbox"], ["lightbox", "lightbox"],
	["brass", "brass"], ["letters", "brass"], ["lantern", "chochin"], ["chochin", "chochin"], ["fanous", "chochin"],
	["billboard", "billboard"], ["balloon", "billboard"], ["painted", "painted"], ["banner", "painted"],
	["noren", "painted"], ["iron", "painted"], ["mural", "painted"]]
const MOTIF_MAP := [["laundry", "festoons"], ["festoon", "festoons"], ["jhalar", "festoons"], ["canopy", "festoons"],
	["arches", "festoons"], ["party", "crown"], ["garden", "crown"], ["eave", "crown"], ["parapet", "crown"], ["roof", "crown"],
	["strip", "floor_lines"], ["led", "floor_lines"], ["outline", "corners"], ["edges", "corners"], ["canyon", "corners"],
	["minaret", "corners"], ["beacon", "corners"], ["uplight", "uplights"], ["flood", "uplights"], ["wash", "uplights"],
	["mural", "uplights"], ["lantern", "lanterns"], ["balcon", "lanterns"], ["lamp", "lanterns"], ["porthole", "lanterns"],
	["ring", "lanterns"], ["fairy", "lanterns"], ["bulb", "crown"], ["chaser", "zigzag"], ["motif", "zigzag"], ["glow", "window_glow"],
	["lattice", "window_glow"], ["sparkle", "window_glow"]]

const GOODS := ["Rope", "Knots", "Wool", "Down", "Honey", "Tea", "Noodles", "Lamps", "Charts", "Bells", "Gas", "Cloth",
	"Mittens", "Ganseys", "Kites", "Clocks", "Pies", "Snow Honey", "Berry Wine", "Mead", "Brooms", "Tins", "Pickles",
	"Dove Eggs", "Moss Dye", "Cordage", "Skyboxes", "Goggles", "Hats", "Quilts", "Buttons", "Lenses", "Radios", "Boots"]
const ADJ := ["Lucky", "Golden", "Upwind", "High", "Little", "Seventh", "Silver", "Red", "Blue", "Merry", "Last",
	"Thin Air", "Long Line", "Fair", "Bright", "Old", "Northern", "Lashing", "Cold Hands", "Light"]
const NOUN := ["Knot", "Lark", "Gull", "Lantern", "Kettle", "Bell", "Anchor", "Comet", "Cloud", "Swallow", "Spool",
	"Moon", "Star", "Wren", "Hoist", "Rim", "Gale", "Teapot", "Compass", "Heron"]
const SHOP := ["Co.", "& Sons", "& Daughters", "House", "Hall", "Emporium", "Exchange", "Stores", "Supply", "Works",
	"Bar", "Cafe", "Noodle Bar", "Tea Room", "Market", "Depot", "Mart"]
const PUNS := ["Weigh More", "Heavier Than You'd Think", "Ground Floor", "The Lightening Rod", "Knot Bad", "Hitch & Brew",
	"Gust Come In", "Lift & Shift", "The Snow Must Go On", "Mind the Edge", "Bee Line", "Cloud Nine Teas", "Three Days Lashed",
	"The Knives", "Heavies Welcome", "Light Fingers", "Rim Shots", "Up & Away", "The Plumb Line", "Kilo for Kilo",
	"Dove Tales", "Fan Club", "Mitten Kitten", "Weather or Not", "The Honest Kilo", "The Light Kettle", "The Last Snow"]
const KNOTS := ["Bowline", "Hitch", "Sheet Bend", "Clove", "Reef", "Halyard", "Bight", "Splice"]
const THINGS := ["Larks", "Kettles", "Knots", "Bells", "Islands Tea", "Hooks", "Skyboxes", "Gusts", "Doves"]
const LED_MSGS := ["HOIST AT 14:00 - GRAIN 2 BOXES", "SNOW HONEY IN", "WEIGHED FAIR SINCE VY 412", "LARK PARTS - ASK INSIDE",
	"THREE DAYS LASHED - DRINK NOW", "FORECAST: CLOUD 18:00 - SNOW", "SKYBOXES IN AT DAWN", "LASHING SALE - 3 DAYS ONLY", "FRESH SNOW HONEY", "BERRY WINE ON TAP",
	"NO FLAME, NO FALL", "LIGHT HANDS, LONG LINES", "WEIGH IT - BUY IT", "GANSEYS 2 FOR 1", "HOT CLOUD PORRIDGE",
	"ROPE BY THE FATHOM", "GROUND GOODS JUST HOISTED", "OPEN ALL NIGHT", "LARK REPAIRS", "TEA - NOODLES - BUNS",
	"TRADE YOUR LIFT HERE", "WARM HANDS INSIDE", "THE KNOT KEEPS ITS WORD", "DOWN QUILTS - WARMEST ALOFT"]

var isl: Node3D                      # SkyIsland
var _st := {}                        # bucket -> SurfaceTool
var _bulbs: Array = []               # [Transform3D, Color, Color(custom)]
var _leds: Array = []                # the LED boards' messages (rows of the strip texture)
var _todo: Array = []                # Callables, one a frame
var _rng := RandomNumberGenerator.new()
var _accent := 0                     # the island's neon leaning (its palette's start)
var count := {}                      # kind -> how many (for the report)
var _palette: Array = NEON           # the island's style's sign colours ...
var _moods: Array = MOODS            # ... its apartments' moods ...
var _kinds: Array = KINDS            # ... the sign kinds it uses ...
var _motifs: Array = MOTIFS          # ... and its lighting motifs
var _density := 0.6                  # 0..1 signs per storefront and facade (b_signs_and_light.md)
static var _styles := {}
static var STYLES := "res://remake/sky/styles.json"   # the merged style catalogue (research/sky_islands/architecture)

static var _glyphs := {}             # "f:c" -> [PackedVector3Array triangle verts (em units, baseline 0), advance]
static var _fonts: Array = []
static var _mats := {}


func setup(p_isl: Node3D) -> void:
	isl = p_isl
	name = "Signs"
	var data: Dictionary = isl.data
	_rng.seed = hash(str(data.id) + ":signs")
	_accent = _rng.randi() % NEON.size()
	_use_style(str(isl.canon.get("style", data.get("style", ""))))
	for b in ["neon", "led", "wash", "solid", "atlas_sky_a", "atlas_sky_b"]:
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		_st[b] = st
	var wv = isl.get("warren")
	if wv != null:
		# a warren city (SkyWarren): its signs, glows and light strings come from its anchors, in the island's frame
		var anc: Array = wv.anchors()
		for k in range(0, anc.size(), 60):
			var r := RandomNumberGenerator.new()
			r.seed = hash("%s:w%d" % [data.id, k])
			_todo.append(_from_anchors.bind({"id": "%s:w%d" % [data.id, k], "warren": true}, Transform3D.IDENTITY, anc.slice(k, k + 60), r))
		_todo.append(_fence_lights)
		_todo.append(_tether_lights)
		_todo.append(_pad_lights)
		_todo.append(_commit)
		return
	var blds: Array = data.buildings
	for i in blds.size():
		_todo.append(_building.bind(blds[i]))
	_todo.append(_string_lights)
	_todo.append(_link_lights)
	_todo.append(_fence_lights)
	_todo.append(_tether_lights)
	_todo.append(_pad_lights)
	_todo.append(_path_lamps)
	_todo.append(_searchlights)
	_todo.append(_commit)


func _process(_delta: float) -> void:
	if _todo.is_empty():
		set_process(false)
		return
	var t0 := Time.get_ticks_usec()
	while not _todo.is_empty() and Time.get_ticks_usec() - t0 < 2500:
		(_todo.pop_front() as Callable).call()


# ------------------------------------------------------------------ text
static func _font(i: int) -> Font:
	if _fonts.is_empty():
		for p in FONTS:
			_fonts.append(load(p))
	if i >= _fonts.size():
		return _fonts[0]
	return _fonts[i]


static var _hfont := {}              # heritage -> font index (appended to _fonts on first use)


static func _heritage_font(her: String) -> int:
	## the font index of a heritage's lettering (0, Noto Sans, when none)
	if _hfont.has(her):
		return _hfont[her]
	_font(0)
	var fi := 0
	if HERITAGE.has(her):
		var p := "res://remake/fonts/heritage/%s.ttf" % str(HERITAGE[her][0])
		if ResourceLoader.exists(p):
			_fonts.append(load(p))
			fi = _fonts.size() - 1
	_hfont[her] = fi
	return fi


static func _glyph(fi: int, ch: String) -> Array:
	var key := "%d:%s" % [fi, ch]
	if _glyphs.has(key):
		return _glyphs[key]
	var f := _font(fi)
	var adv := f.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, 32).x / 32.0
	var tris := PackedVector3Array()
	if ch != " ":
		var tm := TextMesh.new()
		tm.font = f
		tm.font_size = 32
		tm.pixel_size = 1.0 / 32.0
		tm.depth = 0.0
		tm.curve_step = 1.5
		tm.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		tm.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
		tm.text = ch
		var arr := tm.get_mesh_arrays()
		if not arr.is_empty():
			var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
			var ix = arr[Mesh.ARRAY_INDEX]
			var base := _baseline(fi)
			if ix is PackedInt32Array and (ix as PackedInt32Array).size() > 0:
				for k in (ix as PackedInt32Array):
					var p := v[k]
					tris.append(Vector3(p.x, p.y - base, 0.0))
			else:
				for p in v:
					tris.append(Vector3(p.x, p.y - base, 0.0))
			# only the front faces (a depth-0 TextMesh can still carry its back): Godot's front face winds clockwise,
			# so a +Z-facing triangle's (b - a) x (c - a) points -Z.  (The old test kept n.z >= 0 -- with this TextMesh
			# that is none of them, and no island sign had letters: tools, 2026-10-16, "A" = 33 tris, all n.z < 0.)
			var front := PackedVector3Array()
			for k in range(0, tris.size() - 2, 3):
				var n := (tris[k + 1] - tris[k]).cross(tris[k + 2] - tris[k])
				if n.z < 0.0:
					front.append_array([tris[k], tris[k + 1], tris[k + 2]])
			if not front.is_empty():
				tris = front
	_glyphs[key] = [tris, adv]
	return _glyphs[key]


static var _bases := {}


static func _baseline(fi: int) -> float:
	## the bottom of an "H" (the glyphs sit on it)
	if _bases.has(fi):
		return _bases[fi]
	_bases[fi] = 0.0
	var tm := TextMesh.new()
	tm.font = _font(fi)
	tm.font_size = 32
	tm.pixel_size = 1.0 / 32.0
	tm.depth = 0.0
	tm.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	tm.text = "H"
	var arr := tm.get_mesh_arrays()
	var lo := INF
	for p in (arr[Mesh.ARRAY_VERTEX] as PackedVector3Array):
		lo = minf(lo, p.y)
	_bases[fi] = lo
	return lo


const CAP := 0.72                    # an em's cap height


func _text(bucket: String, xf: Transform3D, text: String, cap_h: float, col: Color, mode := 0.0, phase := 0.0,
		fi := 0, max_w := INF) -> float:
	## text centred on xf's origin (its baseline at the origin, facing +Z), cap_h tall; returns its width
	var w := 0.0
	for c in text:
		w += _glyph(fi, c)[1]
	var s := cap_h / CAP
	if w * s > max_w:
		s = max_w / w
	var W := w * s
	var st: SurfaceTool = _st[bucket]
	var x := -W * 0.5
	for c in text:
		var g := _glyph(fi, c)
		var tris: PackedVector3Array = g[0]
		for p in tris:
			var lp := Vector3(x + p.x * s, p.y * s, 0.0)
			st.set_color(col)
			st.set_normal(xf.basis.z.normalized())
			st.set_uv(Vector2((lp.x + W * 0.5) / maxf(W, 0.01), 0.0))
			st.set_uv2(Vector2(mode, phase))
			st.add_vertex(xf * lp)
		x += float(g[1]) * s
	return W


func _vtext(bucket: String, xf: Transform3D, text: String, cap_h: float, col: Color, mode := 0.0, phase := 0.0, fi := 0) -> void:
	## letters stacked top to bottom (a blade sign), the first at xf's origin
	var y := 0.0
	var n := text.length()
	for i in n:
		var c := text[i]
		if c == " ":
			y -= cap_h * 0.7
			continue
		var g := _glyph(fi, c)
		var s := cap_h / CAP
		var x := -float(g[1]) * s * 0.5
		for p in (g[0] as PackedVector3Array):
			var lp := Vector3(x + p.x * s, y - cap_h + p.y * s, 0.0)
			var st: SurfaceTool = _st[bucket]
			st.set_color(col)
			st.set_normal(xf.basis.z.normalized())
			st.set_uv(Vector2(float(i) / maxf(n, 1.0), 0.0))
			st.set_uv2(Vector2(mode, phase))
			st.add_vertex(xf * lp)
		y -= cap_h * 1.35


# ------------------------------------------------------------------ shapes
func _quad(bucket: String, xf: Transform3D, w: float, h: float, col: Color, uv0 := Vector2.ZERO, uv1 := Vector2.ONE,
		uv2 := Vector2.ZERO) -> void:
	## a w x h quad centred on xf's origin, facing +Z; uv0 at its bottom-left, uv1 its top-right
	var st: SurfaceTool = _st[bucket]
	var c := [Vector3(-w * 0.5, -h * 0.5, 0), Vector3(w * 0.5, -h * 0.5, 0), Vector3(w * 0.5, h * 0.5, 0), Vector3(-w * 0.5, h * 0.5, 0)]
	var uv := [uv0, Vector2(uv1.x, uv0.y), uv1, Vector2(uv0.x, uv1.y)]
	for k in [0, 1, 2, 0, 2, 3]:
		st.set_color(col)
		st.set_normal(xf.basis.z.normalized())
		st.set_uv(uv[k])
		st.set_uv2(uv2)
		st.add_vertex(xf * c[k])


func _box(xf: Transform3D, size: Vector3, col: Color) -> void:
	## a solid box centred on xf's origin (its material draws both sides: winding doesn't matter)
	var st: SurfaceTool = _st["solid"]
	var hs := size * 0.5
	for ax in 3:
		var ua := (ax + 1) % 3
		var va := (ax + 2) % 3
		for sg in [-1.0, 1.0]:
			var n := Vector3.ZERO
			n[ax] = sg
			var u := Vector3.ZERO
			u[ua] = hs[ua]
			var v := Vector3.ZERO
			v[va] = hs[va]
			var cen := n * hs[ax]
			var q := [cen - u - v, cen + u - v, cen + u + v, cen - u + v]
			for k in [0, 1, 2, 0, 2, 3]:
				st.set_color(col)
				st.set_normal((xf.basis * n).normalized())
				st.set_uv(Vector2.ZERO)
				st.set_uv2(Vector2.ZERO)
				st.add_vertex(xf * q[k])


func _tube(a: Vector3, b: Vector3, r: float, col: Color, mode := 0.0, phase := 0.0, u0 := 0.0, u1 := 1.0) -> void:
	## a glowing tube from a to b (a square prism, additive: reads as a round tube once it blooms)
	var d := b - a
	var L := d.length()
	if L < 0.01:
		return
	var z := d / L
	var x := z.cross(Vector3.UP)
	if x.length() < 0.1:
		x = z.cross(Vector3.RIGHT)
	x = x.normalized() * r
	var y := z.cross(x).normalized() * r
	var st: SurfaceTool = _st["neon"]
	for side in [[x, y], [y, -x], [-x, -y], [-y, x]]:
		var e0: Vector3 = side[0]
		var e1: Vector3 = side[1]
		var q := [a + e0, b + e0, b + e1, a + e1]
		var uu := [u0, u1, u1, u0]
		for k in [0, 1, 2, 0, 2, 3]:
			st.set_color(col)
			st.set_normal(z)
			st.set_uv(Vector2(uu[k], 0.0))
			st.set_uv2(Vector2(mode, phase))
			st.add_vertex(q[k])


func _bulb(p: Vector3, col: Color, mode := 0.0, phase := 0.0, scale := 1.0) -> void:
	## scale 1 a festoon bulb (0.35 m of glow), bigger for lanterns
	_bulbs.append([Transform3D(Basis(), p), col, Color(mode, phase, 0.35 * scale, 0)])


func _wash(xf: Transform3D, w: float, h: float, col: Color) -> void:
	## light thrown up a wall from xf's origin (the lamp), w wide at its top, h tall
	_quad("wash", xf * Transform3D(Basis(), Vector3(0, h * 0.5, 0)), w, h, col, Vector2(0, 0), Vector2(1, 1))


# ------------------------------------------------------------------ names
func _name(seed_: String) -> String:
	var r := RandomNumberGenerator.new()
	r.seed = hash(seed_)
	var c: Dictionary = isl.canon
	var goods := GOODS.duplicate()
	for t in c.get("trade", []):
		var w := str(t).split(" ")[0].capitalize()
		if w.length() > 2 and w.length() < 11:
			goods.append(w)
	var g: String = goods[r.randi() % goods.size()]
	var n: String = NOUN[r.randi() % NOUN.size()]
	var a: String = ADJ[r.randi() % ADJ.size()]
	var given: Array = ["Wren", "Lark", "Skye", "Rime", "Brume", "Linnet", "Tamsin", "Juniper", "Ayo", "Fennel", "Isolde", "Halcyon"]
	var who: String = given[r.randi() % given.size()]
	if r.randf() < 0.14:
		return PUNS[r.randi() % PUNS.size()]
	match r.randi() % 10:
		8: return "%s & %s" % [KNOTS[r.randi() % KNOTS.size()], KNOTS[r.randi() % KNOTS.size()]]
		9: return "%s %s" % [["Three", "Seven", "Ten", "Two", "Nine"][r.randi() % 5], THINGS[r.randi() % THINGS.size()]]
		0: return "%s's %s" % [who, g]
		1: return "The %s %s" % [a, n]
		2: return "%s & %s" % [g, goods[r.randi() % goods.size()]]
		3: return "%s %s %s" % [str(c.get("name", "Skein")), g, SHOP[r.randi() % SHOP.size()]]
		4: return "%s %s" % [a, g]
		5: return "%s %s" % [n, SHOP[r.randi() % SHOP.size()]]
		6: return "%s's" % who
		_: return "%s %s" % [g, SHOP[r.randi() % SHOP.size()]]


func _short(s: String) -> String:
	## a blade sign's few letters
	var w := s.to_upper().replace("THE ", "").replace("'S", "").split(" ")
	var out := str(w[0])
	return out.left(6)


func _neon_col(r: RandomNumberGenerator) -> Color:
	if _palette != NEON:
		return _palette[r.randi() % _palette.size()]
	return NEON[(_accent + r.randi() % 4 + (r.randi() % 3) * 2) % NEON.size()]


# ------------------------------------------------------------------ the island's style
static func _style_table() -> Dictionary:
	## styles.json: {"styles": {id: style}} or {"styles": [style]} (or a bare list)
	if _styles.is_empty() and DataFile.exists(STYLES):
		var d = JSON.parse_string(DataFile.text(STYLES))
		var list = d.get("styles", d) if d is Dictionary else d
		if list is Dictionary:
			for k in list:
				if list[k] is Dictionary:
					var st: Dictionary = list[k]
					_styles[str(st.get("id", k))] = st
		elif list is Array:
			for st in list:
				if st is Dictionary and st.has("id"):
					_styles[st.id] = st
	return _styles


func _use_style(id: String) -> void:
	## the island's architecture style (canon "style"): its sign kinds, density, palette, moods and motifs
	var st: Dictionary = _style_table().get(id, {})
	if st.is_empty():
		return
	var sg: Dictionary = st.get("signage", {})
	var nt: Dictionary = st.get("night", {})
	var pal: Array = []
	for h in sg.get("palette", []):
		pal.append(Color(str(h)))
	if pal.size() >= 2:
		_palette = pal
	var moods: Array = []
	for h in nt.get("mood", []):
		moods.append(Color(str(h)))
	if moods.size() >= 1:
		_moods = moods
	var kinds: Array = []
	for k in sg.get("kinds", []):
		var m := _map(str(k), KIND_MAP)
		if m != "" and not kinds.has(m) and m != "blade" and m != "billboard" and m != "stack":
			kinds.append(m)
		elif m in ["blade", "stack", "billboard"]:
			_extra[m] = true
	if not kinds.is_empty():
		_kinds = kinds
	var motifs: Array = []
	for k in nt.get("motifs", []):
		var m := _map(str(k), MOTIF_MAP)
		if m != "" and not motifs.has(m):
			motifs.append(m)
	if not motifs.is_empty():
		_motifs = motifs
	_density = float(sg.get("density", _density))


var _extra := {}                     # the style's blades / stacks / billboards, asked for by name


static func _map(name_: String, table: Array) -> String:
	for kv in table:
		if name_.find(kv[0]) >= 0:
			return kv[1]
	return ""


# ------------------------------------------------------------------ a building
func _building(b: Dictionary) -> void:
	var m: Dictionary = isl.sys.models.get(b.model, {}) if "models" in isl.sys else {}
	var w := float(m.get("w", b.get("w", 14.0)))
	var d := float(m.get("d", b.get("d", 14.0)))
	var h := float(m.get("roof", m.get("h", b.get("h", 15.0))))
	var storeys := int(b.get("storeys", m.get("storeys", maxi(1, roundi(h / STOREY)))))
	var sh := h / maxf(storeys, 1)
	var bx := Transform3D(Basis(Vector3.UP, float(b.yaw)), Vector3(b.x, b.y, b.z))
	var r := RandomNumberGenerator.new()
	r.seed = hash(str(b.id))
	var anchors: Array = m.get("anchors", [])
	if not anchors.is_empty():
		_from_anchors(b, bx, anchors, r)
	else:
		_derived(b, bx, w, d, h, storeys, r)
	_mood(b, bx, w, d, h, storeys, sh, r)


func _front(bx: Transform3D, x: float, y: float, d: float, out := 0.12) -> Transform3D:
	## a sign frame on the front face (the building's local -Z), facing out
	return bx * Transform3D(Basis(Vector3.UP, PI), Vector3(x, y, -d * 0.5 - out))


func _derived(b: Dictionary, bx: Transform3D, w: float, d: float, h: float, storeys: int, r: RandomNumberGenerator) -> void:
	var use := str(b.get("use", "dwelling"))
	match use:
		"infirmary":
			_cross(_front(bx, 0.0, minf(h - 2.0, 6.5), d, 0.3), 2.2, Color(0.25, 1.0, 0.45))
		"gasworks", "gas_works", "gas":
			_sign("neon_frame", _front(bx, 0.0, 4.2, d), 6.0, 1.3, "NO FLAME", Color(1.0, 0.15, 0.1), 1.0, r)
		"school":
			_sign("painted", _front(bx, 0.0, 4.0, d), minf(w * 0.6, 9.0), 1.4, "%s School" % str(isl.canon.get("name", "")), Color.WHITE, 0.0, r)
		"hall":
			_sign("neon_script", _front(bx, 0.0, minf(h - 1.5, 7.5), d), minf(w * 0.8, 14.0), 2.0, "%s Hall" % str(isl.canon.get("name", "")), _neon_col(r), 4.0, r)
			_bulb_frame(_front(bx, 0.0, minf(h - 1.5, 7.5) + 0.6, d, 0.2), minf(w * 0.85, 15.0), 3.0, Color(1.0, 0.85, 0.5))
	var commerce := use in ["market", "shop", "shops", "workshop", "hall", "envelope_loft"] or (use == "dwelling" and r.randf() < 0.3 + 0.5 * _density)
	if commerce:
		var n := maxi(1, roundi(w / 7.0)) if use in ["market", "shop", "shops"] else 1
		var shops: Array = b.get("shops", [])
		if not shops.is_empty():
			n = shops.size()
		for i in n:
			var x := -w * 0.5 + (i + 0.5) * w / n
			var kind: String = _kinds[(r.randi() + _accent) % _kinds.size()]
			var nm := _name("%s:%d" % [b.id, i])
			if i < shops.size():
				var sh_ = shops[i]
				if sh_ is Dictionary:
					nm = str(sh_.get("name", sh_.get("shop_name", nm)))
					var k2 := _map(str(sh_.get("kind", sh_.get("sign", ""))), KIND_MAP)
					if k2 != "" and k2 != "blade" and k2 != "billboard" and k2 != "stack":
						kind = k2
				elif sh_ is String:
					nm = sh_
			_sign(kind, _front(bx, x, 3.6, d), minf(w / n - 1.0, 7.0), 1.1, nm, _neon_col(r), float(r.randi() % 6), r)
	# blade signs on the tall ones: vertical, off the front corners, read up and down the street
	if (storeys >= 4 or h > 12.0) and r.randf() < 0.35 + 0.8 * _density:
		if _extra.has("stack") and r.randf() < 0.5:
			_stack(bx * Transform3D(Basis(Vector3.UP, PI * 0.5), Vector3(w * 0.5 - 0.5, 0.0, -d * 0.5 - 0.6)), storeys, h / maxf(storeys, 1), r)
		var nb := 1 + (r.randi() % 3 if _density > 0.75 else r.randi() % 2)
		for k in nb:
			var sx := (w * 0.5 - 0.7) * (1.0 if k == 0 else -1.0)
			var top := minf(h - 1.0, 4.6 + 1.25 * 6.0)
			var txt := _short(_name("%s:blade%d" % [b.id, k]))
			_blade(bx * Transform3D(Basis(Vector3.UP, PI * 0.5), Vector3(sx, top, -d * 0.5 - 0.9)), txt, _neon_col(r), r)
	# a rooftop billboard, facing out over the rim (seen from other islands and the floor)
	if h > 11.0 and r.randf() < 0.12 + 0.35 * _density + (0.15 if _extra.has("billboard") else 0.0):
		_billboard(b, bx, w, d, h, r)


func _from_anchors(b: Dictionary, bx: Transform3D, anchors: Array, r: RandomNumberGenerator) -> void:
	## the generator's anchors (the brief's contract): sign_<kind>_<w>x<h>[_n], glow_<motif>_<n>, lights_<n>
	var lights := {}
	for a in anchors:
		var nm := str(a[0])
		var xf := bx * Transform3D(Basis(Vector3.UP, float(a[4]) if a.size() > 4 else 0.0), Vector3(a[1], a[2], a[3]))
		var parts := nm.split("_")
		if nm.begins_with("sign_") and parts.size() >= 3:
			var kind := parts[1]
			var wh := parts[2].split("x")
			var sw := float(wh[0]) if wh.size() == 2 else 3.0
			var shh := float(wh[1]) if wh.size() == 2 else 1.0
			var txt := _name("%s:%s" % [b.id, nm])
			if b.get("warren", false) and _blank(kind) != {}:
				_wblank(xf, kind, sw, shh, txt, r)
			elif kind == "blade" and b.get("warren", false):
				_wblade(xf, sw, shh, _short(txt), _neon_col(r), r)
			elif kind == "blade":
				_blade(xf * Transform3D(Basis(), Vector3(0, shh * 0.5, 0)), _short(txt), _neon_col(r), r)
			elif kind == "billboard":
				_sign("lightbox", xf, sw, shh, txt, _neon_col(r), 0.0, r)
			else:
				var k2 := kind if KINDS.has(kind) else _map(kind, KIND_MAP)
				if k2 == "" or k2 == "stack":
					k2 = _kinds[r.randi() % _kinds.size()]
				_sign(k2, xf, sw, shh, txt, _neon_col(r), float(r.randi() % 6), r)
		elif nm.begins_with("glow_"):
			var L := float(parts[parts.size() - 1]) if parts.size() >= 3 and parts[parts.size() - 1].is_valid_float() else 4.0
			var c: Color = MOODS[hash(str(b.id)) % MOODS.size()]
			_tube(xf.origin, xf * Vector3(L, 0, 0), 0.04, Color(c, 0.7), 5.0, r.randf())
		elif nm.begins_with("lights_"):
			var key := nm.get_slice("_", 1)
			lights[key] = lights.get(key, []) + [xf.origin]
	for k in lights:
		var pts: Array = lights[k]
		for i in range(0, pts.size() - 1, 2):
			_catenary(pts[i], pts[i + 1], 0.06, Color(1.0, 0.8, 0.45), 1.0)


# ------------------------------------------------------------------ sign kinds
func _sign(kind: String, xf: Transform3D, w: float, h: float, text: String, col: Color, mode: float, r: RandomNumberGenerator) -> void:
	count[kind] = count.get(kind, 0) + 1
	var ph := r.randf()
	match kind:
		"neon_script":
			var tw := _text("neon", xf, text, h * 0.62, Color(col, 1.0), mode, ph, 1, w)
			_tube(xf * Vector3(-tw * 0.5, -0.18, 0.02), xf * Vector3(tw * 0.5, -0.18, 0.02), 0.035, Color(NEON[(_accent + 3) % NEON.size()], 0.8), 2.0, ph)
			_box(xf * Transform3D(Basis(), Vector3(0, h * 0.25, -0.06)), Vector3(tw + 0.4, h * 0.95, 0.06), Color(0.08, 0.08, 0.1))
		"lightbox":
			_box(xf * Transform3D(Basis(), Vector3(0, h * 0.3, -0.15)), Vector3(w, h, 0.3), Color(0.12, 0.12, 0.14))
			var face := col.lerp(Color(1, 1, 1), 0.55)
			_quad("neon", xf * Transform3D(Basis(), Vector3(0, h * 0.3, 0.005)), w - 0.12, h - 0.12, Color(face, 0.5), Vector2.ZERO, Vector2.ONE, Vector2(0.0, ph))
			_text("solid", xf * Transform3D(Basis(), Vector3(0, h * 0.3 - h * 0.22, 0.02)), text, h * 0.42, col.darkened(0.6), 0, 0, 0, w - 0.4)
		"dot_matrix":
			_box(xf * Transform3D(Basis(), Vector3(0, h * 0.3, -0.1)), Vector3(w, h, 0.2), Color(0.05, 0.05, 0.06))
			var pitch := h / 9.0
			var cols := floorf((w - 0.2) / pitch)
			var msg := ("%s - %s" % [text, LED_MSGS[r.randi() % LED_MSGS.size()]]).to_upper().left(40)
			var row := _leds.size()
			_leds.append(msg)
			var led: Color = [Color(1.0, 0.55, 0.1), Color(1.0, 0.2, 0.15), Color(0.3, 1.0, 0.35), Color(1.0, 0.85, 0.3)][r.randi() % 4]
			_quad("led", xf * Transform3D(Basis(), Vector3(0, h * 0.3, 0.01)), cols * pitch, 7.0 * pitch, Color(led, 1.0),
				Vector2(0, 7), Vector2(cols, 0), Vector2(row, SkyDotFont.columns(msg)))
		"chochin":
			var n := maxi(2, int(w / 0.9))
			var lc: Color = [Color(1.0, 0.25, 0.15), Color(1.0, 0.85, 0.6)][r.randi() % 2]
			for i in n:
				var p := xf * Vector3(-w * 0.5 + (i + 0.5) * w / n, -0.2, 0.25)
				_bulb(p, lc, 1.0, r.randf(), 2.6)
			_text("neon", xf * Transform3D(Basis(), Vector3(0, 0.45, 0.02)), text, h * 0.4, Color(1.0, 0.9, 0.7, 0.9), 0.0, ph, 1, w)
			_box(xf * Transform3D(Basis(), Vector3(0, 0.65, -0.06)), Vector3(w, h * 0.7, 0.06), Color(0.35, 0.1, 0.08))
		"brass":
			_text("solid", xf, text, h * 0.55, Color(0.85, 0.65, 0.3), 0, 0, 1, w)
			for k in 3:
				_wash(xf * Transform3D(Basis(), Vector3(-w * 0.35 + k * w * 0.35, -0.9, -0.08)), w * 0.45, h * 2.4, Color(1.0, 0.8, 0.5, 0.7))
		"painted":
			var bc: Color = [Color(0.15, 0.25, 0.45), Color(0.45, 0.12, 0.12), Color(0.12, 0.35, 0.22), Color(0.92, 0.88, 0.78)][r.randi() % 4]
			_box(xf * Transform3D(Basis(), Vector3(0, h * 0.3, -0.05)), Vector3(w, h, 0.08), bc)
			var tc := Color(0.1, 0.1, 0.1) if bc.v > 0.6 else Color(0.95, 0.9, 0.75)
			_text("solid", xf * Transform3D(Basis(), Vector3(0, h * 0.3 - h * 0.2, 0.01)), text, h * 0.4, tc, 0, 0, 1, w - 0.3)
			for sx in [-w * 0.3, w * 0.3]:
				_box(xf * Transform3D(Basis(), Vector3(sx, h + 0.25, 0.4)), Vector3(0.18, 0.12, 0.3), Color(0.15, 0.15, 0.15))
				_quad("wash", xf * Transform3D(Basis.from_euler(Vector3(PI, 0, 0)), Vector3(sx, h * 0.5 + 0.1, 0.03)), w * 0.55, h * 0.9 + 0.3,
					Color(1.0, 0.9, 0.7, 0.8))
		"video":
			# a retrofit screen: dot-matrix tiles playing slow coloured frames (sky_neon mode 7)
			_box(xf * Transform3D(Basis(), Vector3(0, h * 0.3, -0.1)), Vector3(w + 0.2, h + 0.2, 0.2), Color(0.05, 0.05, 0.06))
			_quad("neon", xf * Transform3D(Basis(), Vector3(0, h * 0.3, 0.01)), w, h, Color(col.lerp(Color.WHITE, 0.2), 0.8),
				Vector2.ZERO, Vector2.ONE, Vector2(7.0, ph))
		"figure":
			# a giant figure sign over the door: an island creature or ware drawn in neon tube, its outline chasing
			_figure(xf * Transform3D(Basis(), Vector3(0, h * 0.4, 0.05)), maxf(w, h) * 0.9, col, r)
		"neon_frame":
			var tw := _text("neon", xf * Transform3D(Basis(), Vector3(0, -h * 0.05, 0.02)), text, h * 0.5, Color(col, 1.0), mode, ph, 0, w - 0.5)
			var fw := tw + 0.6
			var c2 := Color(NEON[(_accent + 5) % NEON.size()], 0.9)
			var y0 := -h * 0.3
			var y1 := h * 0.55
			var pts := [Vector3(-fw * 0.5, y0, 0.03), Vector3(fw * 0.5, y0, 0.03), Vector3(fw * 0.5, y1, 0.03), Vector3(-fw * 0.5, y1, 0.03)]
			for i in 4:
				_tube(xf * pts[i], xf * pts[(i + 1) % 4], 0.035, c2, 2.0, ph, i * 0.25, (i + 1) * 0.25)
			_box(xf * Transform3D(Basis(), Vector3(0, (y0 + y1) * 0.5, -0.05)), Vector3(fw + 0.2, y1 - y0 + 0.2, 0.06), Color(0.06, 0.06, 0.08))


const FIGURES := {
	"goat": [[-0.45, -0.2], [-0.3, 0.1], [0.25, 0.1], [0.35, 0.3], [0.45, 0.45], [0.42, 0.2], [0.5, 0.1], [0.32, 0.0],
		[0.3, -0.25], [0.2, -0.45], [0.15, -0.25], [-0.25, -0.2], [-0.3, -0.45], [-0.38, -0.25], [-0.45, -0.2]],
	"bell": [[-0.05, 0.45], [0.05, 0.45], [0.18, 0.3], [0.22, 0.0], [0.4, -0.3], [-0.4, -0.3], [-0.22, 0.0], [-0.18, 0.3], [-0.05, 0.45]],
	"lark": [[-0.5, 0.0], [-0.15, 0.08], [0.0, 0.4], [0.1, 0.1], [0.35, 0.12], [0.5, 0.05], [0.35, -0.05], [0.1, -0.08],
		[0.0, -0.4], [-0.15, -0.08], [-0.5, 0.0]],
	"fish": [[-0.5, 0.0], [-0.2, 0.22], [0.2, 0.18], [0.35, 0.0], [0.5, 0.2], [0.5, -0.2], [0.35, 0.0], [0.2, -0.18], [-0.2, -0.22], [-0.5, 0.0]],
	"kettle": [[-0.3, -0.35], [0.3, -0.35], [0.35, 0.1], [0.55, 0.3], [0.4, 0.12], [0.2, 0.25], [0.0, 0.32], [0.05, 0.42],
		[-0.05, 0.42], [-0.2, 0.25], [-0.35, 0.1], [-0.3, -0.35]],
	"bee": [[-0.35, 0.0], [-0.2, 0.18], [0.2, 0.18], [0.35, 0.0], [0.2, -0.18], [-0.2, -0.18], [-0.35, 0.0], [-0.05, 0.18],
		[-0.2, 0.45], [0.05, 0.2], [0.25, 0.45], [0.1, 0.18]],
	"cup": [[-0.3, 0.3], [0.3, 0.3], [0.2, -0.3], [-0.2, -0.3], [-0.3, 0.3], [0.3, 0.3], [0.32, 0.15], [0.45, 0.1], [0.3, -0.05]],
}


func _figure(xf: Transform3D, size: float, col: Color, r: RandomNumberGenerator) -> void:
	count["figure"] = count.get("figure", 0) + 1
	var keys := FIGURES.keys()
	var pts: Array = FIGURES[keys[r.randi() % keys.size()]]
	var ph := r.randf()
	var mode: float = [2.0, 4.0, 0.0][r.randi() % 3]
	var n := pts.size()
	for i in n - 1:
		var a := Vector3(pts[i][0], pts[i][1], 0.0) * size
		var b := Vector3(pts[i + 1][0], pts[i + 1][1], 0.0) * size
		_tube(xf * a, xf * b, 0.06, Color(col, 1.0), mode, ph, float(i) / n, float(i + 1) / n)
	# its eye, blinking
	_bulb(xf * Vector3(0.25 * size, 0.12 * size, 0.05), Color(1, 1, 1), 3.0, ph, 1.2)


func _blade(xf: Transform3D, text: String, col: Color, r: RandomNumberGenerator) -> void:
	## a vertical sign standing out from the wall (the Hong Kong / Tokyo street's): letters stacked, on both faces
	count["blade"] = count.get("blade", 0) + 1
	var cap := 1.1
	var n := maxi(text.length(), 2)
	var H := n * cap * 1.35 + 0.4
	var bw := 1.5
	var lightbox := r.randf() < 0.4
	_box(xf * Transform3D(Basis(), Vector3(0, -H * 0.5, 0)), Vector3(bw, H, 0.3), Color(0.08, 0.08, 0.1))
	var ph := r.randf()
	var mode: float = [0.0, 2.0, 3.0, 4.0, 5.0][r.randi() % 5]
	for side in [1.0, -1.0]:
		var fx := xf * Transform3D(Basis(Vector3.UP, 0.0 if side > 0 else PI), Vector3(0, -0.2, 0.17 * side))
		if lightbox:
			_quad("neon", fx * Transform3D(Basis(), Vector3(0, -H * 0.5 + 0.2, 0)), bw - 0.1, H - 0.1, Color(col.lerp(Color.WHITE, 0.5), 0.45))
			_vtext("solid", fx * Transform3D(Basis(), Vector3(0, -0.05, 0.02)), text, cap, col.darkened(0.65), 0, 0, 0)
		else:
			_vtext("neon", fx, text, cap, Color(col, 1.0), mode, ph, 0)
	# its edge in a chasing tube
	var c2 := Color(NEON[(_accent + 2) % NEON.size()], 0.8)
	_tube(xf * Vector3(0, 0, -0.2), xf * Vector3(0, -H, -0.2), 0.04, c2, 2.0, ph)
	_tube(xf * Vector3(0, 0, 0.2), xf * Vector3(0, -H, 0.2), 0.04, c2, 2.0, ph + 0.5)


# ------------------------------------------------------------------ the SIGNS agent's island blanks (signs.json)
## A warren's shop signs on its family's blank -- the fascia over a shop, the blade standing out (sky_<civ>_fascia /
## _blade cells of the sky_a / sky_b atlases) -- with the shop's name set in the blank's content rect, dark letters
## by day and lit at SIGN_EMIT by night (the user, 2026-10-16: the signs washed out and the dot-matrix text didn't
## form).  SIGN_EMIT, shared with the SIGNS agent: letters 2.0 at night, lit faces <= 0.9, backings dark.
static var _signs_json := {}
static var _atlas_mats := {}


func _blank(kind: String) -> Dictionary:
	if _signs_json.is_empty():
		var d = DataFile.json("res://remake/signs/signs.json")
		_signs_json = d if d is Dictionary else {"cells": {}}
	var wv = isl.get("warren")
	if wv == null or (wv.head as Dictionary).is_empty():
		return {}
	var fam := "blade" if kind == "blade" else "fascia"
	var cells: Dictionary = _signs_json.get("cells", {})
	return cells.get("sky_%s_%s" % [str(wv.head.civ), fam], {})


func _atlas_mat(atlas: String) -> Material:
	if _atlas_mats.has(atlas):
		return _atlas_mats[atlas]
	var a: Dictionary = (_signs_json.get("atlases", {}) as Dictionary).get(atlas, {})
	var m := ShaderMaterial.new()
	m.shader = load("res://remake/shaders/sign_atlas.gdshader")
	m.set_shader_parameter("albedo_tex", load(str(a.get("png", ""))))
	if a.has("emit"):
		m.set_shader_parameter("emit_tex", load(str(a.emit)))
	_atlas_mats[atlas] = m
	return m


func _wblank(xf: Transform3D, kind: String, w: float, h: float, text: String, r: RandomNumberGenerator) -> void:
	var cell := _blank(kind)
	count[kind] = count.get(kind, 0) + 1
	var uv: Array = cell.uv                                  # [u0, v0, du, dv] of the 256-px cell
	var reg: Array = cell.region
	var con: Array = cell.content                            # [x0, y0, x1, y1] px in the cell: the blank's ground
	var cw := float(reg[2])
	var chh := float(reg[3])
	# the whole cell drawn at the sign's height; its width kept to the cell's aspect, within the anchor's width
	var blade := kind == "blade"
	var H := h * (1.0 if blade else 1.35)
	var W := minf(H * cw / chh, w * (1.0 if blade else 1.1))
	H = W * chh / cw
	var bx := xf * Transform3D(Basis(), Vector3(-W * 0.5 - 0.06 if blade else 0.0, 0.0, 0.04 if not blade else 0.0))
	var u0 := Vector2(float(uv[0]), float(uv[1]) + float(uv[3]))
	var u1 := Vector2(float(uv[0]) + float(uv[2]), float(uv[1]))
	var bucket := "atlas_" + str(cell.atlas)
	var her := str(isl.canon.get("heritage", ""))
	var hfi := _heritage_font(her)
	var her_accent := float(absi(hash(text + ":accent")) % 1000) / 1000.0 < ACCENT_SHARE
	_box(bx * Transform3D(Basis(), Vector3(0, 0, -0.04)), Vector3(W, H, 0.05), Color(0.1, 0.09, 0.08))
	for side in ([1.0, -1.0] if blade else [1.0]):
		var f := bx * Transform3D(Basis(Vector3.UP, 0.0 if side > 0 else PI), Vector3(0, 0, 0.0))
		_quad(bucket, f, W, H, Color(1, 1, 1, 1), u0, u1)
		# the name, centred on the blank's content rect, a little proud of it
		var cx := ((float(con[0]) + float(con[2])) * 0.5 / cw - 0.5) * W
		var cy := (0.5 - (float(con[1]) + float(con[3])) * 0.5 / chh) * H
		var tw := (float(con[2]) - float(con[0])) / cw * W * 0.86
		var th := (float(con[3]) - float(con[1])) / chh * H
		var col := _neon_col(r).lerp(Color(1.0, 0.92, 0.75), 0.35)
		if her_accent and HERITAGE.has(her):
			var ac := Color(str(HERITAGE[her][1]))
			col = Color.from_hsv(ac.h, minf(ac.s, 0.75), maxf(ac.v, 0.95))     # (the accent, bright enough to glow)
		if blade:
			var nm := _short(text)
			var cap := minf(tw * 0.8, th * 0.9 / maxf(nm.length() * 1.35 - 0.35, 1.0))
			var y0 := (nm.length() * cap * 1.35 - cap * 0.35) * 0.5
			_vtext("solid", f * Transform3D(Basis(), Vector3(cx, cy + y0, 0.012)), nm, cap, Color(0.1, 0.08, 0.06), 0, 0, hfi)
			_vtext("neon", f * Transform3D(Basis(), Vector3(cx, cy + y0, 0.02)), nm, cap, Color(col, 1.0), 0.0, 0.0, hfi)
		else:
			var cap := minf(th * 0.62, 0.32)
			_text("solid", f * Transform3D(Basis(), Vector3(cx, cy - cap * 0.5, 0.012)), text, cap, Color(0.1, 0.08, 0.06), 0, 0, hfi, tw)
			_text("neon", f * Transform3D(Basis(), Vector3(cx, cy - cap * 0.5, 0.02)), text, cap, Color(col, 1.0), 0.0, 0.0, hfi, tw)


func _wblade(xf: Transform3D, w: float, h: float, text: String, col: Color, r: RandomNumberGenerator) -> void:
	## a warren's blade sign, its anchor's size (sign_blade_<w>x<h>: centred on the anchor; +Z along the street, +X
	## into the wall -- tools/sky/warren/pick.py): a painted board standing out from the wall on a bracket, its letters
	## stacked on both faces; by night softly lit (the old _blade is a tower's: metres tall, at full neon)
	count["blade"] = count.get("blade", 0) + 1
	var c := xf * Transform3D(Basis(), Vector3(-w * 0.5 - 0.08, 0, 0))
	var board := col.lerp(Color(0.88, 0.85, 0.78), 0.55)
	_box(c, Vector3(w, h, 0.12), board)
	_box(xf * Transform3D(Basis(), Vector3(-0.04, h * 0.5 - 0.12, 0)), Vector3(0.12, 0.05, 0.05), Color(0.2, 0.2, 0.2))
	_box(xf * Transform3D(Basis(), Vector3(-0.04, -h * 0.5 + 0.12, 0)), Vector3(0.12, 0.05, 0.05), Color(0.2, 0.2, 0.2))
	var n := maxi(text.replace(" ", "").length(), 1)
	var cap := minf(w * 0.68, (h - 0.2) / (n * 1.35 - 0.35))
	var y0 := (n * cap * 1.35 - cap * 0.35) * 0.5
	var lit := r.randf() < 0.5                    # (half are lightboxes: a soft face behind dark letters)
	var ph := r.randf()
	var mode: float = [0.0, 0.0, 2.0, 5.0][r.randi() % 4]
	for side in [1.0, -1.0]:
		var face := c * Transform3D(Basis(Vector3.UP, 0.0 if side > 0 else PI), Vector3(0, 0, 0.065 * side))
		if lit:
			_quad("neon", face, w - 0.1, h - 0.1, Color(col.lerp(Color.WHITE, 0.4), 0.1))
			_vtext("solid", face * Transform3D(Basis(), Vector3(0, y0, 0.01)), text, cap, col.darkened(0.6), 0, 0, 0)
		else:
			_vtext("solid", face * Transform3D(Basis(), Vector3(0, y0, 0.005)), text, cap, col.darkened(0.35), 0, 0, 0)
			_vtext("neon", face * Transform3D(Basis(), Vector3(0, y0, 0.012)), text, cap, Color(col, 0.4), mode, ph, 0)
	_tube(c * Vector3(-w * 0.5, h * 0.5, 0), c * Vector3(-w * 0.5, -h * 0.5, 0), 0.02, Color(col, 0.3), 1.0, ph)


func _stack(xf: Transform3D, storeys: int, sh: float, r: RandomNumberGenerator) -> void:
	## the zakkyo column: one lightbox per floor per tenant, up the corner, each a different colour
	count["stack"] = count.get("stack", 0) + 1
	for k in range(1, storeys):
		var y := k * sh + sh * 0.5
		var col := _neon_col(r)
		var txt := _short(_name("%s:stack%d" % [str(xf.origin), k])).left(4)
		var fx := xf * Transform3D(Basis(), Vector3(0, y, 0))
		_box(fx, Vector3(0.7, sh * 0.8, 0.25), Color(0.1, 0.1, 0.12))
		for side in [1.0, -1.0]:
			var f2 := fx * Transform3D(Basis(Vector3.UP, 0.0 if side > 0 else PI), Vector3(0, 0, 0.13 * side))
			var flick := 3.0 if r.randf() < 0.1 else 0.0
			_quad("neon", f2, 0.62, sh * 0.72, Color(col.lerp(Color.WHITE, 0.45), 0.5), Vector2.ZERO, Vector2.ONE, Vector2(flick, r.randf()))
			_text("solid", f2 * Transform3D(Basis(), Vector3(0, -sh * 0.12, 0.01)), txt, minf(sh * 0.22, 0.4), col.darkened(0.65), 0, 0, 0, 0.55)


func _bulb_frame(xf: Transform3D, w: float, h: float, col: Color) -> void:
	## a marquee's chase bulbs round a rectangle
	var per := 0.45
	var pts := [Vector3(-w * 0.5, -h * 0.5, 0), Vector3(w * 0.5, -h * 0.5, 0), Vector3(w * 0.5, h * 0.5, 0), Vector3(-w * 0.5, h * 0.5, 0)]
	var k := 0
	for i in 4:
		var a: Vector3 = pts[i]
		var b: Vector3 = pts[(i + 1) % 4]
		var n := maxi(1, int(a.distance_to(b) / per))
		for j in n:
			_bulb(xf * a.lerp(b, float(j) / n), col, 2.0, float(k) * 0.08)
			k += 1


func _cross(xf: Transform3D, s: float, col: Color) -> void:
	count["cross"] = count.get("cross", 0) + 1
	var a := s * 0.5
	var t := s * 0.17
	var pts := [Vector3(-t, a, 0), Vector3(t, a, 0), Vector3(t, t, 0), Vector3(a, t, 0), Vector3(a, -t, 0), Vector3(t, -t, 0),
		Vector3(t, -a, 0), Vector3(-t, -a, 0), Vector3(-t, -t, 0), Vector3(-a, -t, 0), Vector3(-a, t, 0), Vector3(-t, t, 0)]
	for i in pts.size():
		_tube(xf * pts[i], xf * pts[(i + 1) % pts.size()], 0.05, Color(col, 1.0), 5.0, 0.0)
	_box(xf * Transform3D(Basis(), Vector3(0, 0, -0.08)), Vector3(s + 0.3, s + 0.3, 0.1), Color(0.9, 0.9, 0.88))


func _billboard(b: Dictionary, bx: Transform3D, w: float, d: float, h: float, r: RandomNumberGenerator) -> void:
	## a roof billboard on posts, its face turned out over the rim
	count["billboard"] = count.get("billboard", 0) + 1
	var out := Vector3(b.x, 0, b.z).normalized()
	if out.length() < 0.5:
		out = Vector3(0, 0, -1)
	var yaw := atan2(out.x, out.z)                       # (+Z of the board along out)
	var bw := clampf(w * 0.8, 6.0, 14.0)
	var bh := bw * 0.4
	var at := Vector3(b.x, float(b.y) + h + 2.0 + bh * 0.5, b.z)
	var xf := Transform3D(Basis(Vector3.UP, yaw), at)
	for sx in [-bw * 0.35, bw * 0.35]:
		_box(xf * Transform3D(Basis(), Vector3(sx, -bh * 0.5 - 1.0, -0.4)), Vector3(0.2, 2.0, 0.2), Color(0.2, 0.2, 0.22))
	_box(xf * Transform3D(Basis(), Vector3(0, 0, -0.3)), Vector3(bw + 0.3, bh + 0.3, 0.3), Color(0.1, 0.1, 0.12))
	var col := _neon_col(r)
	var txt := _name("%s:bill" % b.id)
	match r.randi() % 3:
		0:      # backlit, big dark letters
			_quad("neon", xf * Transform3D(Basis(), Vector3(0, 0, -0.14)), bw, bh, Color(col.lerp(Color.WHITE, 0.4), 0.55))
			_text("solid", xf * Transform3D(Basis(), Vector3(0, -bh * 0.18, -0.12)), txt, bh * 0.38, col.darkened(0.7), 0, 0, 1, bw - 0.6)
		1:      # neon slogan, chase bulbs round it
			_text("neon", xf * Transform3D(Basis(), Vector3(0, -bh * 0.15, -0.13)), txt, bh * 0.36, Color(col, 1.0), 4.0, r.randf(), 1, bw - 0.6)
			_bulb_frame(xf * Transform3D(Basis(), Vector3(0, 0, -0.1)), bw, bh, Color(1.0, 0.85, 0.5))
		_:      # a giant LED board
			var pitch := bh / 9.0
			var cols := floorf(bw / pitch)
			var msg := ("%s - %s" % [txt, LED_MSGS[r.randi() % LED_MSGS.size()]]).to_upper().left(40)
			var row := _leds.size()
			_leds.append(msg)
			_quad("led", xf * Transform3D(Basis(), Vector3(0, 0, -0.13)), cols * pitch, 7.0 * pitch, Color(col, 1.0),
				Vector2(0, 7), Vector2(cols, 0), Vector2(row, SkyDotFont.columns(msg)))


# ------------------------------------------------------------------ mood lighting
func _mood(b: Dictionary, bx: Transform3D, w: float, d: float, h: float, storeys: int, sh: float, r: RandomNumberGenerator) -> void:
	## every building's mood: a colour and two motifs (the user: "mood lighting and a stylish motif")
	var mc: Color = _moods[absi(hash(str(b.id)) + _accent) % _moods.size()]
	if str(b.get("mood", "")).begins_with("#"):
		mc = Color(str(b.mood))                 # (the generator's: traits.mood)
	var picks: Array = []
	var tries := 0
	while picks.size() < 2 and tries < 20:
		tries += 1
		var pool: Array = _motifs if tries < 10 else MOTIFS
		var m: String = pool[r.randi() % pool.size()]
		if not picks.has(m):
			picks.append(m)
	var hw := w * 0.5 + 0.06
	var hd := d * 0.5 + 0.06
	var ring := [Vector3(-hw, 0, -hd), Vector3(hw, 0, -hd), Vector3(hw, 0, hd), Vector3(-hw, 0, hd)]
	var ph := r.randf()
	# every roofline strung with bulbs (the Christmas-tree outline), in the building's mood, chasing or twinkling
	var bulb_c := mc.lerp(Color(1.0, 0.9, 0.7), 0.45)
	var bm := 2.0 if r.randf() < 0.4 else 1.0
	for i in 4:
		var a0: Vector3 = ring[i] + Vector3(0, h + 0.35, 0)
		var a1: Vector3 = ring[(i + 1) % 4] + Vector3(0, h + 0.35, 0)
		var n := maxi(2, int(a0.distance_to(a1) / 0.9))
		for j in n:
			_bulb(bx * a0.lerp(a1, float(j) / n), bulb_c, bm, ph + (i * n + j) * 0.031)
	for m in picks:
		count[m] = count.get(m, 0) + 1
		match m:
			"floor_lines":
				for k in range(1, storeys):
					var y := k * sh
					for i in 4:
						_tube(bx * (ring[i] + Vector3(0, y, 0)), bx * (ring[(i + 1) % 4] + Vector3(0, y, 0)), 0.06, Color(mc, 0.6), 5.0, ph + k * 0.07)  # (floor lines)
			"corners":
				for c in ring:
					_tube(bx * (c + Vector3(0, 0.5, 0)), bx * (c + Vector3(0, h, 0)), 0.08, Color(mc, 0.85), 2.0, ph)
			"crown":
				for i in 4:
					_tube(bx * (ring[i] + Vector3(0, h + 0.05, 0)), bx * (ring[(i + 1) % 4] + Vector3(0, h + 0.05, 0)), 0.08, Color(mc, 1.0), 6.0 if r.randf() < 0.3 else 0.0, ph)
				# string lights criss-crossing the roof terrace
				for i in 2:
					_catenary(bx * (ring[i] + Vector3(0, h + 1.8, 0)), bx * (ring[(i + 2) % 4] + Vector3(0, h + 1.8, 0)), 0.04, Color(1.0, 0.85, 0.55), 1.0)
			"lanterns":
				var cols := maxi(1, int(w / 3.2))
				for k in range(1, storeys):
					for i in cols:
						if (i + k) % 2 == 0:
							_bulb(bx * Vector3(-w * 0.5 + (i + 0.5) * w / cols, k * sh + sh * 0.55, -hd - 0.25), mc.lerp(Color(1.0, 0.8, 0.5), 0.5), 1.0, r.randf(), 1.6)
			"uplights":
				var n := maxi(2, int(w / 5.0))
				for i in n:
					_wash(bx * Transform3D(Basis(Vector3.UP, PI), Vector3(-w * 0.5 + (i + 0.5) * w / n, 0.2, -hd - 0.05)), w / n * 0.9, minf(h * 0.75, 18.0), Color(mc, 0.75))
			"festoons":
				# bulbs swagged across the front, every other floor (laundry lines, jhalar curtains)
				for k in range(1, storeys, 2):
					var y := k * sh + sh * 0.8
					var segs := maxi(1, int(w / 6.0))
					for i in segs:
						var xa := -w * 0.5 + i * w / segs
						_catenary(bx * Vector3(xa, y, -hd - 0.4), bx * Vector3(xa + w / segs, y, -hd - 0.4), 0.09, mc.lerp(Color(1, 0.85, 0.6), 0.4), 1.0, 0.6)
			"window_glow":
				# light from the rooms spilling out: soft pools on every face, a floor at a time, most windows lit
				for face in 4:
					var fw := w if face % 2 == 0 else d
					var fxf := bx * Transform3D(Basis(Vector3.UP, [PI, -PI * 0.5, 0.0, PI * 0.5][face]),
						[Vector3(0, 0, -hd - 0.03), Vector3(hw + 0.03, 0, 0), Vector3(0, 0, hd + 0.03), Vector3(-hw - 0.03, 0, 0)][face])
					var cols := maxi(1, int(fw / 3.2))
					for k in storeys:
						for i in cols:
							if r.randf() < 0.7:
								_quad("wash", fxf * Transform3D(Basis(), Vector3(-fw * 0.5 + (i + 0.5) * fw / cols, k * sh + sh * 0.2, 0)),
									2.0, sh * 0.75, Color(mc.lerp(Color(1.0, 0.8, 0.55), 0.35), 0.45), Vector2(0, 0.35), Vector2(1, 1.0))
			"zigzag":
				var z := -hd - 0.02
				for k in range(1, storeys):
					var y0 := k * sh - sh * 0.35
					var y1 := k * sh + sh * 0.35
					var n := maxi(2, int(w / 3.0))
					for i in n:
						var xa := -w * 0.5 + i * w / n
						var xb := -w * 0.5 + (i + 1) * w / n
						_tube(bx * Vector3(xa, y0 if i % 2 == 0 else y1, z), bx * Vector3(xb, y1 if i % 2 == 0 else y0, z), 0.06, Color(mc, 0.55), 2.0, ph + k * 0.1)


# ------------------------------------------------------------------ string lights
func _catenary(a: Vector3, b: Vector3, sag_k: float, col: Color, mode: float, every := 0.9) -> void:
	var L := a.distance_to(b)
	var n := maxi(2, int(L / every))
	var ph := randf()
	for i in n + 1:
		var t := float(i) / n
		var p := a.lerp(b, t) - Vector3.UP * (4.0 * t * (1.0 - t)) * L * sag_k
		var c := col
		if mode >= 1.0 and i % 3 == 1:
			c = NEON[(_accent + i) % NEON.size()].lerp(Color.WHITE, 0.3)
		_bulb(p, c, mode, ph + t * 3.0)


func _string_lights() -> void:
	## across the lanes: each building to its nearest neighbour, roof corner to roof corner
	var blds: Array = isl.data.buildings
	var done := {}
	var pairs: Array = []
	for i in blds.size():
		var a: Dictionary = blds[i]
		var near: Array = []
		for j in blds.size():
			if j == i:
				continue
			var bj: Dictionary = blds[j]
			var dd := Vector2(a.x, a.z).distance_to(Vector2(bj.x, bj.z))
			if dd < 40.0 + 20.0 * _density:
				near.append([dd, j])
		near.sort_custom(func(p: Array, q: Array) -> bool: return p[0] < q[0])
		for k in mini(near.size(), 2 + int(_density * 2.0)):        # (dense styles: lanes roofed in lights)
			pairs.append([i, near[k][1]])
	for pr in pairs:
		var i: int = pr[0]
		var best: int = pr[1]
		var a: Dictionary = blds[i]
		if done.has(Vector2i(mini(i, best), maxi(i, best))):
			continue
		done[Vector2i(mini(i, best), maxi(i, best))] = true
		var b: Dictionary = blds[best]
		var ha := _height(a)
		var hb := _height(b)
		var lo := minf(ha, hb) * 0.55 + 3.0
		var pa := Vector3(a.x, float(a.y) + minf(ha, lo + 4.0), a.z)
		var pb := Vector3(b.x, float(b.y) + minf(hb, lo + 4.0), b.z)
		# from each building's face toward the other (not its middle)
		var dir := (pb - pa)
		dir.y = 0.0
		dir = dir.normalized()
		pa += dir * 7.0
		pb -= dir * 7.0
		_catenary(pa, pb, 0.07, Color(1.0, 0.82, 0.5), 1.0, 1.1)


func _link_lights() -> void:
	## string lights along the links between buildings (skybridges, plank bridges, covered alleys: the generator's
	## "links"), whatever shape they come in: points under a, b / from, to / points / path, as [x, y, z]
	for l in isl.data.get("links", []):
		var pts: Array = []
		if l is Dictionary:
			for k in ["points", "path"]:
				if l.has(k):
					pts = l[k]
			if pts.is_empty():
				for k in [["a", "b"], ["from", "to"]]:
					if l.has(k[0]) and l.has(k[1]):
						pts = [l[k[0]], l[k[1]]]
		elif l is Array:
			pts = l
		for i in pts.size() - 1:
			var a = pts[i]
			var b = pts[i + 1]
			if a is Array and b is Array and a.size() >= 3 and b.size() >= 3:
				var pa := Vector3(a[0], a[1], a[2]) + Vector3.UP * 2.6
				var pb := Vector3(b[0], b[1], b[2]) + Vector3.UP * 2.6
				_catenary(pa, pb, 0.04, Color(1.0, 0.85, 0.55), 1.0, 0.7)


static func warm_glyphs() -> void:
	## the glyphs, made once while the loading screen is up (each TextMesh syncs with the renderer: ~1 ms)
	for fi in FONTS.size():
		for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789&'-.!:":
			_glyph(fi, c)


func _height(b: Dictionary) -> float:
	var m: Dictionary = isl.sys.models.get(b.model, {}) if "models" in isl.sys else {}
	return float(m.get("roof", m.get("h", b.get("h", 15.0))))


func _fence_lights() -> void:
	var pts: Array = isl.data.get("fence", [])
	var k := 0
	for i in pts.size():
		var a := Vector2(pts[i][0], pts[i][1])
		var b := Vector2(pts[(i + 1) % pts.size()][0], pts[(i + 1) % pts.size()][1])
		var L := a.distance_to(b)
		var n := maxi(1, int(L / 2.2))
		for j in n:
			var p := a.lerp(b, float(j) / n)
			var c: Color = Color(1.0, 0.85, 0.55) if k % 4 != 0 else NEON[(_accent + k / 4) % NEON.size()]
			_bulb(Vector3(p.x, isl.deck_y(p.x, p.y) + 1.5, p.y), c, 2.0 if k % 2 == 0 else 1.0, float(k) * 0.02)
			k += 1


func _tether_lights() -> void:
	var base: float = isl.sys.BALLOON_BASE
	for b in isl.data.balloons:
		var a := Vector3(b.anchor[0], b.anchor[1], b.anchor[2])
		var top := Vector3(b.x, base, b.z)
		var L := a.distance_to(top)
		var n := int(L / 3.0)
		var c: Color = NEON[(_accent + int(absf(b.x))) % NEON.size()].lerp(Color.WHITE, 0.35)
		for j in n + 1:
			_bulb(a.lerp(top, float(j) / n), c, 2.0, float(j) * 0.05)


func _path_lamps() -> void:
	## lamps along the paths and roads (every LAMP_EVERY m), each with its pool of light on the deck
	var g: Dictionary = isl.data.get("graph", {})
	if g.is_empty():
		return
	var nodes: Array = g.nodes
	var lamp_c: Color = (_moods[0] as Color).lerp(Color(1.0, 0.82, 0.55), 0.6) if _moods.size() > 0 else Color(1.0, 0.82, 0.55)
	var carry := 0.0
	for e in g.edges:
		if float(e[2]) < 2.0:
			continue                                  # (not the spurs to doors)
		var a := Vector2(nodes[e[0]][0], nodes[e[0]][1])
		var b := Vector2(nodes[e[1]][0], nodes[e[1]][1])
		var L := a.distance_to(b)
		var t := LAMP_EVERY - carry
		while t < L:
			var p := a.lerp(b, t / L)
			var side := (b - a).normalized().orthogonal() * (float(e[2]) * 0.5 + 0.4)
			var q := p + side
			var y: float = isl.deck_y(q.x, q.y)
			_box(Transform3D(Basis(), Vector3(q.x, y + 1.5, q.y)), Vector3(0.1, 3.0, 0.1), Color(0.12, 0.12, 0.13))
			_bulb(Vector3(q.x, y + 3.1, q.y), lamp_c, 0.0, 0.0, 1.5)
			# the pool on the deck (a flat wash, lamp at its middle: two halves)
			for k in 2:
				_quad("wash", Transform3D(Basis(Vector3.RIGHT, -PI * 0.5).rotated(Vector3.UP, PI * k), Vector3(q.x, y + 0.06, q.y))
					* Transform3D(Basis(), Vector3(0, 1.8, 0)), 4.6, 3.6, Color(lamp_c, 0.3))
			t += LAMP_EVERY
		carry = fmod(L - (t - LAMP_EVERY), LAMP_EVERY)


func _searchlights() -> void:
	## a few searchlights sweeping the sky from the tallest roofs (more on the showier styles)
	var blds: Array = isl.data.buildings.duplicate()
	blds.sort_custom(func(p: Dictionary, q: Dictionary) -> bool: return _height(p) > _height(q))
	var n := clampi(1 + int(_density * 2.5), 1, 3)
	var cone := _beam_mesh()
	for k in mini(n, blds.size()):
		var b: Dictionary = blds[k]
		var mi := MeshInstance3D.new()
		mi.name = "Searchlight_%d" % k
		mi.mesh = cone
		var m := ShaderMaterial.new()
		m.shader = load("res://remake/shaders/sky_beam.gdshader")
		var c: Color = _palette[(k * 3 + _accent) % _palette.size()] if _palette != NEON else Color(0.85, 0.9, 1.0)
		m.set_shader_parameter("color", c.lerp(Color.WHITE, 0.5))
		m.set_shader_parameter("phase", _rng.randf() * TAU)
		m.set_shader_parameter("speed", _rng.randf_range(0.15, 0.35) * (1.0 if k % 2 == 0 else -1.0))
		mi.material_override = m
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.position = Vector3(b.x, float(b.y) + _height(b) + 1.0, b.z)
		mi.extra_cull_margin = 600.0
		add_child(mi)
		count["searchlight"] = count.get("searchlight", 0) + 1


static var _beam: ArrayMesh


static func _beam_mesh() -> ArrayMesh:
	## a cone 600 m long along +Y, 0.3 m wide at the lamp and 40 m at its end, as two crossed fans (UV.x across, UV.y along)
	if _beam:
		return _beam
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var L := 600.0
	for rot in [0.0, PI * 0.5]:
		var ax := Vector3(cos(rot), 0, sin(rot))
		var q := [ax * -0.15, ax * 0.15, ax * 20.0 + Vector3(0, L, 0), ax * -20.0 + Vector3(0, L, 0)]
		var uv := [Vector2(0, 0), Vector2(1, 0), Vector2(1, 1), Vector2(0, 1)]
		for i in [0, 1, 2, 0, 2, 3]:
			st.set_uv(uv[i])
			st.add_vertex(q[i])
	_beam = st.commit()
	return _beam


func _pad_lights() -> void:
	## the lark cradles' landing lights: a ring of blue and white
	for p in isl.data.get("pads", []):
		var c := Vector3(p.x, float(p.get("y", isl.deck_y(p.x, p.z))) + 0.15, p.z)
		for k in 16:
			var a := TAU * k / 16.0
			_bulb(c + Vector3(cos(a), 0, sin(a)) * 6.3, Color(0.4, 0.7, 1.0) if k % 2 == 0 else Color(1, 1, 1), 2.0, float(k) / 16.0)


# ------------------------------------------------------------------ commit
static func _mat(key: String) -> Material:
	if _mats.has(key):
		return _mats[key]
	var m: Material
	match key:
		"neon":
			m = ShaderMaterial.new()
			(m as ShaderMaterial).shader = load("res://remake/shaders/sky_neon.gdshader")
		"wash":
			m = ShaderMaterial.new()
			(m as ShaderMaterial).shader = load("res://remake/shaders/sky_wash.gdshader")
		"solid":
			var sm := StandardMaterial3D.new()
			sm.vertex_color_use_as_albedo = true
			sm.cull_mode = BaseMaterial3D.CULL_DISABLED
			sm.roughness = 0.7
			sm.metallic = 0.1
			m = sm
		"bulbs":
			m = ShaderMaterial.new()
			(m as ShaderMaterial).shader = load("res://remake/shaders/sky_bulbs.gdshader")
	_mats[key] = m
	return m


func _commit() -> void:
	for key in ["neon", "wash", "solid", "led", "atlas_sky_a", "atlas_sky_b"]:
		var st: SurfaceTool = _st[key]
		var mesh := st.commit()
		if mesh.get_surface_count() == 0:
			continue
		var mi := MeshInstance3D.new()
		mi.name = "Signs_" + key
		mi.mesh = mesh
		if key.begins_with("atlas_"):
			mi.material_override = _atlas_mat(key.trim_prefix("atlas_"))
		elif key == "led":
			var lm := ShaderMaterial.new()
			lm.shader = load("res://remake/shaders/sky_led.gdshader")
			lm.set_shader_parameter("msg", SkyDotFont.strip_texture(_leds))
			mi.material_override = lm
		else:
			mi.material_override = _mat(key)
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF if key != "solid" else GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		mi.visibility_range_end = SIGN_RANGE
		add_child(mi)
	if not _bulbs.is_empty():
		var sph := QuadMesh.new()                    # (a sprite: sky_bulbs turns it to the camera)
		sph.size = Vector2.ONE
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.use_colors = true
		mm.use_custom_data = true
		mm.mesh = sph
		mm.instance_count = _bulbs.size()
		for i in _bulbs.size():
			mm.set_instance_transform(i, _bulbs[i][0])
			mm.set_instance_color(i, _bulbs[i][1])
			mm.set_instance_custom_data(i, _bulbs[i][2])
		var mmi := MultiMeshInstance3D.new()
		mmi.name = "Bulbs"
		mmi.multimesh = mm
		mmi.material_override = _mat("bulbs")
		mmi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mmi.visibility_range_end = BULB_RANGE
		add_child(mmi)
	count["bulbs"] = _bulbs.size()
	count["led_boards"] = _leds.size()
	_st.clear()
	_bulbs.clear()
