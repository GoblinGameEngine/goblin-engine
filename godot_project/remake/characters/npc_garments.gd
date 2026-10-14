extends RefCounted
class_name NpcGarments

## Clothes for a generated body, built from the body's own rings (NpcBody) plus ease, so a garment
## fits any body the builder can make and can't pass through it: a garment ring has the same frame
## and skin weights as the body ring under it, just larger (generator_design_notes.md 5).  Skirts,
## dresses and coats that must clear both legs are lofted from the waist to a hem ring round both.
##
## What a person wears is chosen from npc_outfits.json by outfit(): per slot a weighted pick on the
## person's own stream ("outfit:<slot>"), so it is the same every time, and a colour and fabric
## pattern for each garment.  The shader draws the pattern (no textures).

const PATH := "res://remake/characters/npc_outfits.json"
## inner first.  skirt (an over-skirt on leggings), sash, harness, neck, hands and brow are only in the sky folk's outfits
## (cultures in npc_outfits.json); an outfit without a slot never draws from that slot's stream, so adding slots
## changes nobody else.
const SLOTS := ["bottom", "skirt", "top", "dress", "over", "sash", "harness", "neck", "feet", "hands", "head", "brow"]
const PATTERNS := ["solid", "stripes", "pinstripe", "check", "tartan", "dots", "floral", "knit", "denim", "pleats", "weave", "herring",
	"quilt", "zigzag", "patch", "peerie"]
## patterns that are the cloth's make, not a print: not counted against the one-print-per-outfit limit
const WEAVES := ["solid", "denim", "knit", "pleats", "weave", "quilt"]

static var _data: Dictionary


static func data() -> Dictionary:
	if _data.is_empty():
		_data = JSON.parse_string(FileAccess.get_file_as_string(PATH))
	return _data


# -- choosing ---------------------------------------------------------------------------------------

static func tags(v: Dictionary) -> Array:
	var age := float(v.get("age", 30))
	var t := [v.get("sex", "female"), "style:" + str(v.get("style", "plain"))]
	t.append("child" if age < 13.0 else "teen" if age < 18.0 else "elder" if age >= 65.0 else "adult")
	return t


static func outfit(v: Dictionary, world_seed: int, pid: String, occasion := "work") -> Array:
	## -> [{slot, garment, def, colour: Color, pattern, colours: [Color, Color, Color], scale}], inner first.
	var d := data()
	var key := "casual"
	var culture := str(v.get("culture", ""))
	if culture != "" and d.get("cultures", {}).has(culture):
		key = _culture_key(d.cultures[culture], v, occasion)
	elif occasion == "work":
		var occ: String = str(v.get("occupation", ""))
		var tb: Dictionary = NpcTraits.shared().tables.occupations
		if tb.has(occ):
			key = str(tb[occ][(tb["_cols"] as Array).find("outfit")])
	if not d.outfits.has(key):
		key = "casual"
	var of: Dictionary = d.outfits[key]
	var tg := tags(v)
	var out := []
	var accent_slot := ""
	var patterned := 0
	var pal := _palette(v)
	for slot in SLOTS:
		var opts: Dictionary = of.slots.get(slot, {})
		if opts.is_empty():
			continue
		var w := {}
		for g in opts:
			var o: Variant = opts[g]
			if typeof(o) == TYPE_DICTIONARY:
				var ok := true
				for need in o.get("if", []):
					if not need in tg:
						ok = false
				if ok:
					w[g] = float(o.w)
			else:
				w[g] = float(o)
		if w.is_empty():
			continue
		var rng := NpcRng.for_trait(world_seed, pid, "outfit:" + slot)
		var g: String = rng.pick(w)
		if g == "none" or not d.garments.has(g):
			continue
		var def: Dictionary = d.garments[g]
		# colour
		var src: String = def.get("colour", of.colours.get(slot, "palette"))     # (a garment may carry its own)
		var col := _colour(src, pal, rng, v, slot, accent_slot)
		if src == "accent" and int(v.get("accent_colour", -1)) >= 0 and accent_slot == "":
			accent_slot = slot
		# pattern: at most one patterned garment (two for children and the flamboyant)
		var pw: Dictionary = def.get("patterns", {"solid": 1})
		var limit := 2 if ("child" in tg or "style:flamboyant" in tg) else 1
		var pat: String = rng.pick(pw)
		if not pat in WEAVES:
			if patterned >= limit:
				pat = "solid"
			else:
				patterned += 1
		if pat == "denim":
			col = Color(d.colours.denim)
		var c2 := _second(col, pal, rng, pat)
		out.append({"slot": slot, "garment": g, "def": def, "colour": _worn(col, float(v.get("wear", 0.3))),
			"colours": [_worn(c2[0], float(v.get("wear", 0.3))), _worn(c2[1], float(v.get("wear", 0.3)))],
			"pattern": pat, "scale": 0.6 + rng.rand() * 0.8})
		if def.has("trim"):
			# bands at the hem, cuffs and collar in another colour (the sky folk's coats: gakti-like trims)
			var trng := NpcRng.for_trait(world_seed, pid, "outfit:trim")
			var tc := _colour(str(def.trim), pal, trng, v, "trim", "x")
			var tpat: String = str(def.get("trim_pattern", "solid"))
			var t2 := _second(tc, pal, trng, tpat)
			out.append({"slot": "trim", "garment": g + "_trim", "def": {"build": "trim", "of": def, "patterns": {tpat: 1}},
				"colour": _worn(tc, float(v.get("wear", 0.3))), "colours": [t2[0], t2[1]], "pattern": tpat, "scale": 0.8})
	# a dress replaces top and bottom
	var has_dress := out.any(func(x): return x.slot == "dress")
	if has_dress:
		out = out.filter(func(x): return x.slot != "top" and x.slot != "bottom")
	# an over-skirt that a coat's skirt would hide (and its flare poke through) is left off
	var coat_hem := 0.0
	for x in out:
		if x.slot == "over" and str(x.def.build) == "coat":
			coat_hem = float(x.def.get("hem", 0.0))
	if coat_hem > 0.0:
		out = out.filter(func(x): return x.slot != "skirt" or float(x.def.get("hem", 0.0)) > coat_hem + 0.12)
	# coveralls replace the bottom
	if out.any(func(x): return x.def.build == "top+bottom"):
		out = out.filter(func(x): return x.slot != "bottom")
	return out


static func _culture_key(c: Dictionary, v: Dictionary, occasion: String) -> String:
	## A culture's outfit for this person: their own outfit_key, else their role's work clothes, else by age.
	if v.has("outfit_key"):
		return str(v.outfit_key)
	var age := float(v.get("age", 30))
	if age < 13.0 and c.has("child"):
		return str(c.child)
	var roles: Dictionary = c.get("roles", {})
	if occasion == "work" and roles.has(str(v.get("culture_role", ""))):
		return str(roles[str(v.culture_role)])
	if age >= 65.0 and c.has("elder"):
		return str(c.elder)
	return str(c.get("default", "casual"))


const UNDYED := ["#e8e2d0", "#b8b0a0", "#6f6a60"]           # the sky folk's undyed wool (canon palette_rule)


static func _palette(v: Dictionary) -> Array:
	if v.has("clan_colors"):
		# a sky clan: its three colours, the undyed wools that go with any, a moss-dyed green and a lichen yellow
		var cc: Array = v.clan_colors
		return [Color(cc[0]), Color(cc[1]), Color(cc[2]), Color(UNDYED[0]), Color(UNDYED[1]), Color(UNDYED[2]),
			Color("#6b7a45"), Color("#c2ad5a")]
	var tb: Dictionary = NpcTraits.shared().tables.palettes
	var fam: String = str(v.get("palette", "earth"))
	var sw: Array = tb.get(fam, tb.earth)
	return sw.map(func(h): return Color.from_hsv(float(h[0]) / 360.0, float(h[1]), float(h[2])))


static func _colour(src: String, pal: Array, rng: NpcRng, v: Dictionary, slot: String, accent_slot: String) -> Color:
	var d := data()
	if src == "accent":
		var ai := int(v.get("accent_colour", -1))
		if ai >= 0 and accent_slot == "":
			var acc: Array = NpcTraits.shared().tables.palettes.accent
			var a: Array = acc[ai % acc.size()]
			return Color.from_hsv(float(a[0]) / 360.0, float(a[1]), float(a[2]))
		src = "palette"
	if src == "palette":
		return pal[int(rng.rand() * pal.size()) % pal.size()]
	if src == "clan" or src == "clan_dark":                 # a sky clan's colours: [main, second, accent] = swatches 0, 1, 2
		var k: Color = pal[0]
		return k if src == "clan" else Color.from_hsv(k.h, k.s, k.v * 0.62)
	if src == "clan_second":
		return pal[1]
	if src == "clan_accent":
		return pal[2]
	if src == "clan_or_grey":                              # a rigger's anorak
		return pal[0] if rng.rand() < 0.5 else Color(d.colours.anorak)
	if src == "undyed":
		return Color(UNDYED[int(rng.rand() * 3.0) % 3])
	if src == "palette_dark":
		var c: Color = pal[int(rng.rand() * pal.size()) % pal.size()]
		return Color.from_hsv(c.h, minf(c.s * 1.1, 0.5), clampf(c.v * 0.6, 0.18, 0.45))
	if d.colours.has(src):
		return Color(d.colours[src])
	return Color(src) if src.begins_with("#") else pal[0]


static func _second(base: Color, pal: Array, rng: NpcRng, pat: String) -> Array:
	## The pattern's other colours: stripes/checks against cream or a palette swatch; small prints
	## (dots, florals) in a lighter or darker tint.
	var cream := Color("#e6dfcc")
	var other: Color = pal[int(rng.rand() * pal.size()) % pal.size()]
	match pat:
		"stripes", "check", "pinstripe":
			return [cream if base.v < 0.7 else other, other]
		"tartan":
			return [other, Color.from_hsv(fposmod(base.h + 0.08, 1.0), base.s, base.v * 0.6)]
		"dots", "floral":
			return [cream if base.v < 0.6 else base.darkened(0.45), other]
		"peerie":                                          # Fair Isle bands: a clan colour and cream on the ground
			return [pal[1] if pal[1] != base else pal[0], cream if base.v < 0.75 else base.darkened(0.5)]
		"zigzag":                                          # woven bands: the clan colour (or a swatch) on cream
			return [pal[0] if pal[0] != base else other, cream if base.v < 0.75 else base.darkened(0.5)]
		"patch":                                           # mended patchwork: other cloths of the household
			return [other, Color.from_hsv(base.h, base.s, base.v * 0.72)]
	return [base.darkened(0.15), base.lightened(0.15)]


static func _worn(c: Color, wear: float) -> Color:
	## Faded with wear: less saturated, a little lighter (ghibli_style.md 2.2 rule 5).
	return Color.from_hsv(c.h, c.s * (1.0 - 0.4 * wear), minf(1.0, c.v * (1.0 + 0.1 * wear)))


# -- building ----------------------------------------------------------------------------------------

static func _ring_at(rings: Array, f: float) -> Dictionary:
	## A ring at fractional index f along a part's rings (interpolated).
	f = clampf(f, 0.0, rings.size() - 1.0)
	var i := mini(int(f), rings.size() - 2)
	var t := f - i
	var a: Dictionary = rings[i]
	var b: Dictionary = rings[i + 1]
	return {"c": (a.c as Vector3).lerp(b.c, t), "ax": (a.ax as Vector3).lerp(b.ax, t).normalized(),
		"az": (a.az as Vector3).lerp(b.az, t).normalized(), "a": lerpf(a.a, b.a, t), "b": lerpf(a.b, b.b, t),
		"e": lerpf(a.e, b.e, t), "w": a.w if t < 0.5 else b.w}


static func _grow(r: Dictionary, e: float, ex := 0.0) -> Dictionary:
	var g := r.duplicate()
	g.a = r.a + e + ex
	g.b = r.b + e + ex * 0.7
	return g


static func _range(rings: Array, f0: float, f1: float, e: float, step := 1.0) -> Array:
	## Rings from fractional index f0 to f1 (either direction), grown by ease e.
	var out := []
	var dirn := 1.0 if f1 >= f0 else -1.0
	var f := f0
	while (f - f1) * dirn < -1e-4:
		out.append(_grow(_ring_at(rings, f), e))
		var nxt := floorf(f + 1.0) if dirn > 0 else ceilf(f - 1.0)
		f = minf(nxt, f1) if dirn > 0 else maxf(nxt, f1)
	out.append(_grow(_ring_at(rings, f1), e))
	return out


static func build(def: Dictionary, body: Dictionary, layer_ease := 0.0) -> Array:
	## -> Array of NpcBody.Part for one garment.  layer_ease: extra room for layers worn under it.
	var parts: Dictionary = {}
	for p: NpcBody.Part in body.parts:
		parts[p.name] = p
	var L: Dictionary = body.landmarks
	var e: float = float(def.get("ease", 0.015)) + layer_ease
	def = def.duplicate()
	def["_sleeve_ease"] = float(def.get("ease", 0.015)) * 0.8 + layer_ease * 0.35    # layering room is for the torso
	var out: Array = []
	match str(def.build):
		"top":
			out.append_array(_top(def, parts, L, e))
		"bottom":
			out.append_array(_bottom(def, parts, L, e))
		"top+bottom":
			out.append_array(_top(def, parts, L, e))
			var bd := def.duplicate()
			bd.top = def.torso[0] + 3.4
			out.append_array(_bottom(bd, parts, L, e + 0.002))
		"skirt":
			out.append(_skirt(float(def.top), float(def.hem), float(def.get("flare", 0.3)), parts, L, e + 0.004, "skirt"))
		"dress":
			out.append_array(_top(def, parts, L, e))
			out.append(_skirt(float(def.torso[0]) + 0.2, float(def.hem), float(def.get("flare", 0.4)), parts, L, e + 0.002, "dress_skirt"))
		"coat":
			out.append_array(_top(def, parts, L, e))
			if float(def.get("hem", 0.0)) > 0.02:
				out.append(_skirt(float(def.torso[0]) + 0.6, float(def.hem), float(def.get("flare", 0.25)), parts, L, e + 0.012, "coat_skirt"))
			if float(def.get("cape", 0.0)) > 0.01:
				out.append(_cape(float(def.cape), parts, L, e))
		"overalls":
			var bd := def.duplicate()
			out.append_array(_bottom(bd, parts, L, e))
		"apron":
			out.append(_apron(def, parts, L, e * 0.5 + 0.006))
		"shoes":
			out.append_array(_shoes(def, parts, L, e))
		"cap", "brim_hat", "headscarf", "earflap", "hood_up", "headband":
			out.append_array(_headwear(def, parts, L))
		"sash":
			out.append_array(_sash(def, parts, L, e))
		"trim":
			out.append_array(_trim(def.of, body, layer_ease))
		"scarf":
			out.append_array(_scarf(def, parts, L, e))
		"hood":
			out.append(_hood(def, parts, L, e))
		"gloves":
			out.append_array(_gloves(def, parts, L, e))
		"mittens":
			out.append_array(_mittens(def, parts, L, e))
		"harness":
			out.append_array(_harness(def, parts, L, e))
		"goggles":
			out.append_array(_goggles(def, parts, L, layer_ease))
	return out


static func _top(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	var torso: NpcBody.Part = parts.torso
	var t0: float = def.torso[0]
	var t1: float = def.torso[1]
	var rs := _range(torso.rings, t0, t1, e)
	# the neck opening: the top ring pulled in to sit round the neck, collars stand up a little
	var neck: String = def.get("neck", "round")
	var top: Dictionary = rs[-1]
	if neck == "collar" or neck == "sailor":
		var col := _grow(top, 0.004)
		col.c = (top.c as Vector3) + Vector3(0, 0.018 * L.T, 0)
		col.a = top.a * 0.92
		col.b = top.b * 0.95
		rs.append(col)
	elif neck == "funnel":
		# a stand-up collar round the neck (deels, parkas, roll-necks): rings up the neck, carried by it
		var nk: NpcBody.Part = parts.neck
		for f in [0.5, 1.4]:
			var col := _grow(_ring_at(nk.rings, f), minf(e, 0.035) + 0.006 + 0.004 * float(def.get("layer", 0)))
			col.w = [["Neck", 0.6], ["UpperChest", 0.4]]
			rs.append(col)
	elif neck == "v" or neck == "square":
		var low := _grow(top, 0.0)
		low.c = (top.c as Vector3) - Vector3(0, 0.03 * L.T, 0)
		rs[-1] = low
	# hem: tucked-in tops end at the waistband; others hang a little looser at the bottom
	(rs[0] as Dictionary).a *= 1.03
	(rs[0] as Dictionary).b *= 1.03
	var out := [NpcBody.loft("top", rs, NpcBody.RING, false, false)]
	var sl: float = def.get("sleeve", 0.0)
	for side in ["L", "R"]:
		var arm: NpcBody.Part = parts["arm" + side]
		if sl > 0.01:
			var end := 0.2 + sl * (arm.rings.size() - 1.2)
			var srs := _range(arm.rings, 0.0, end, float(def.get("_sleeve_ease", e * 0.9)))
			(srs[0] as Dictionary).a = (arm.rings[0] as Dictionary).a + e * 0.3      # (a full-ease start stood up as a wing)
			(srs[0] as Dictionary).b = (arm.rings[0] as Dictionary).b + e * 0.3
			# short sleeves flare open at the hem
			if sl < 0.6:
				(srs[-1] as Dictionary).a += 0.003 * L.T
				(srs[-1] as Dictionary).b += 0.003 * L.T
			out.append(NpcBody.loft("sleeve" + side, srs, NpcBody.LIMB, true, false))
	return out


static func _bottom(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	var torso: NpcBody.Part = parts.torso
	var out := [NpcBody.loft("pants_top", _range(torso.rings, 0.0, float(def.top), e + 0.002), NpcBody.RING, true, false)]
	var ln: float = def.get("legs", 1.0)
	for side in ["L", "R"]:
		var leg: NpcBody.Part = parts["leg" + side]
		var end := ln * (leg.rings.size() - 1.0)
		var lrs := _range(leg.rings, 0.0, end, e)
		# trouser legs hang straight below the knee rather than hugging the calf
		for r in lrs:
			r.a = maxf(r.a, L.knee_r * 1.3 + e)
			r.b = maxf(r.b, L.knee_r * 1.3 + e)
		out.append(NpcBody.loft("pants" + side, lrs, NpcBody.LIMB, false, false))
	return out


static func _skirt(top_f: float, hem: float, flare: float, parts: Dictionary, L: Dictionary, e: float, pname: String) -> NpcBody.Part:
	## From a torso ring down to a hem ring that encloses both legs; hem = 0 at the crotch, 1 at the
	## ankle.  The lower rings follow the hips and both thighs half each, so walking swings them.
	var torso: NpcBody.Part = parts.torso
	var top := _grow(_ring_at(torso.rings, top_f), e)
	var hip := _grow(_ring_at(torso.rings, 2.0), e + 0.004)
	var T: float = L.T
	var hem_y: float = lerpf(L.crotch, L.ankle_y, clampf(hem, -0.3, 1.0))
	var legs_w: float = L.leg_sep + L.thigh_r * 1.2
	var rs := [top]
	if top_f > 2.2:
		rs.append(hip)
	var n := 4
	var start_y: float = (rs[-1] as Dictionary).c.y
	for i in range(1, n + 1):
		var t := float(i) / n
		var y := lerpf(start_y, hem_y, t)
		var w := maxf(lerpf(hip.a, legs_w + e, t), hip.a) + flare * 0.12 * T * t * t
		var dd := maxf(lerpf(hip.b, L.thigh_r * 1.25 + e, t), hip.b * 0.95) + flare * 0.08 * T * t * t
		var wts := [["Hips", 1.0 - 0.6 * t], ["UpperLegL", 0.3 * t], ["UpperLegR", 0.3 * t]]
		rs.append(NpcBody.ring(Vector3(0, y, (hip.c as Vector3).z), Vector3.RIGHT, Vector3.BACK, w, dd, wts, 2.1))
	var part := NpcBody.loft(pname, rs, NpcBody.RING + 4, false, false)
	_skirt_weights(part, L)
	return part


static func _skirt_weights(p: NpcBody.Part, L: Dictionary) -> void:
	## Per vertex, not per ring: each side of a skirt is carried by the leg under it, more so toward
	## the hem, so a stepping thigh pushes the cloth forward instead of passing through it.
	var top_y := p.verts[0].y
	var hem_y := p.verts[p.verts.size() - 1].y
	var hips := NpcBody.BONES.find("Hips")
	var ll := NpcBody.BONES.find("UpperLegL")
	var lr := NpcBody.BONES.find("UpperLegR")
	var w0: float = maxf(float(L.leg_sep), 0.02)
	for i in p.verts.size():
		var v := p.verts[i]
		var t := clampf((top_y - v.y) / maxf(top_y - hem_y, 0.01), 0.0, 1.0)
		var side := 1.0 / (1.0 + exp(-v.x / (w0 * 0.6)))                 # 0 left .. 1 right
		var legs := 0.85 * smoothstep(0.0, 0.7, t)
		var wl := legs * (1.0 - side)
		var wr := legs * side
		p.bones[i * 4] = hips
		p.bones[i * 4 + 1] = ll
		p.bones[i * 4 + 2] = lr
		p.bones[i * 4 + 3] = 0
		p.weights[i * 4] = 1.0 - wl - wr
		p.weights[i * 4 + 1] = wl
		p.weights[i * 4 + 2] = wr
		p.weights[i * 4 + 3] = 0.0


static func _apron(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> NpcBody.Part:
	## A front panel: the front arc (about 40% of the way round) of rings from the bib or waist down
	## to the hem, standing off the body.
	var torso: NpcBody.Part = parts.torso
	var top_f: float = def.top
	var hem_y: float = lerpf(L.crotch, L.ankle_y, float(def.hem))
	var rs := _range(torso.rings, top_f, 1.0, e)
	var last: Dictionary = rs[-1]
	var hang_w: float = maxf(last.a, L.hip_w * 1.0 + e)
	var hang_d: float = maxf(last.b, L.hip_d * 1.02 + e)
	for i in range(1, 4):
		var t := i / 3.0
		var y := lerpf((last.c as Vector3).y, hem_y, t)
		rs.append(NpcBody.ring(Vector3(0, y, (last.c as Vector3).z), Vector3.RIGHT, Vector3.BACK, hang_w, hang_d, [["Hips", 1.0 - 0.5 * t], ["UpperLegL", 0.25 * t], ["UpperLegR", 0.25 * t]], 2.2))
	return _front_panel("apron", rs, 0.3)


static func _front_panel(pname: String, rings: Array, frac: float) -> NpcBody.Part:
	## A loft over only the front arc (-frac/2 .. +frac/2 of the way round), made two-sided.
	var p := NpcBody.Part.new()
	p.name = pname
	p.rings = rings
	var cols := 9
	p.around = cols - 1
	var acc := 0.0
	for i in rings.size():
		if i > 0:
			acc += ((rings[i].c as Vector3) - (rings[i - 1].c as Vector3)).length()
		for k in cols:
			var t := fposmod(-frac * 0.5 + frac * k / (cols - 1.0), 1.0)
			p.verts.append(NpcBody.ring_point(rings[i], t))
			p.uvs.append(Vector2(k * 0.05, acc))
			p.uv2s.append(Vector2(-10, -10))
			NpcBody._push_weights(p, rings[i].w)
	for i in rings.size() - 1:
		for k in cols - 1:
			var a := i * cols + k
			var b := a + 1
			var c := a + cols
			var d := c + 1
			p.indices.append_array([a, c, b, b, c, d])
	NpcBody._orient_outward(p, rings, 0, p.indices.size())
	p.normals.resize(p.verts.size())
	var acc_n := {}
	for t in range(0, p.indices.size(), 3):
		var fn := (p.verts[p.indices[t + 1]] - p.verts[p.indices[t]]).cross(p.verts[p.indices[t + 2]] - p.verts[p.indices[t]])
		for j in 3:
			acc_n[p.indices[t + j]] = acc_n.get(p.indices[t + j], Vector3.ZERO) + fn
	for i in p.verts.size():
		p.normals[i] = (acc_n.get(i, Vector3.FORWARD) as Vector3).normalized()
	# back faces too (the panel is seen from behind at its edges)
	var n := p.indices.size()
	for t in range(0, n, 3):
		p.indices.append_array([p.indices[t], p.indices[t + 2], p.indices[t + 1]])
	return p


static func _shoes(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	var out := []
	var h: float = def.get("height", 0.0)
	for side in ["L", "R"]:
		var foot: NpcBody.Part = parts["foot" + side]
		var rs := _range(foot.rings, 0.0, foot.rings.size() - 1.0, e)
		# a sole: the rings' bottoms flattened onto the ground
		for r in rs:
			r.c = (r.c as Vector3) + Vector3(0, 0.002, 0)
		out.append(NpcBody.loft("shoe" + side, rs, NpcBody.LIMB, true, true))
		if h > 0.01:
			var leg: NpcBody.Part = parts["leg" + side]
			var n := leg.rings.size() - 1.0
			out.append(NpcBody.loft("boot" + side, _range(leg.rings, n, n - h * n * 0.6, e * 1.4), NpcBody.LIMB, false, false))
	return out


static func _headwear(def: Dictionary, parts: Dictionary, L: Dictionary) -> Array:
	var head: NpcBody.Part = parts.head
	var H: float = L.H
	var rs := head.rings
	var out := []
	var hair_room := 0.035 * H                                   # hats sit on hair
	match str(def.build):
		"cap":
			var tall: float = def.get("tall", 0.0)
			var crs := _range(rs, 7.6 - float(def.get("low", 0.0)), rs.size() - 1.0, hair_room + 0.01 * H)
			for i in crs.size():
				var t := float(i) / (crs.size() - 1)
				crs[i].c = (crs[i].c as Vector3) + Vector3(0, tall * H * t, 0)
				if def.get("flat", false):
					crs[i].c = (crs[i].c as Vector3) + Vector3(0, 0, -0.06 * H * t)
			out.append(NpcBody.loft("cap", crs, NpcBody.HEAD_AROUND, false, true))
			var vis: float = def.get("visor", 0.0)
			if vis > 0.01:
				var r0: Dictionary = crs[0]
				var v := _grow(r0, 0.0)
				var v2 := _grow(r0, 0.0)
				v2.c = (r0.c as Vector3) + Vector3(0, -0.02 * H, -vis * 0.35 * H)
				v2.a = r0.a * 0.9
				v2.b = r0.b * 0.6
				out.append(_front_panel("visor", [v, v2], 0.36))
			var pom: float = def.get("pom", 0.0)
			if pom > 0.001:
				out.append(_ball("pom", (crs[-1].c as Vector3) + Vector3(0, pom * 0.55 * H, 0), pom * H, [["Head", 1.0]]))
		"earflap":
			# a fur-lined trapper: a low crown, and flaps down over both ears to the jaw
			var room := hair_room + 0.014 * H
			var crs := _range(rs, 6.9, rs.size() - 1.0, room)
			for i in crs.size():
				crs[i].c = (crs[i].c as Vector3) + Vector3(0, float(def.get("crown", 0.06)) * H * float(i) / (crs.size() - 1), 0)
			out.append(NpcBody.loft("crown", crs, NpcBody.HEAD_AROUND, false, true))
			if float(def.get("pom", 0.0)) > 0.001:
				out.append(_ball("pom", (crs[-1].c as Vector3) + Vector3(0, float(def.pom) * 0.6 * H, 0), float(def.pom) * H, [["Head", 1.0]]))
			var frs := _range(rs, 7.0, 2.4, room + 0.004 * H)
			for t in [0.25, 0.75]:
				out.append(_arc_panel("flap", frs, t, 0.17))
		"hood_up":
			# an anorak's hood up: round the back and over the crown, open round the face, down to the shoulders
			var room := hair_room + 0.07 * H
			var hrs := _range(rs, 2.2, rs.size() - 1.0, room)
			var nk: NpcBody.Part = parts.neck
			var low := _grow(_ring_at(nk.rings, 1.0), 0.05 * H + room)
			low.c = (low.c as Vector3) + Vector3(0, 0, 0.03 * H)
			low.w = [["Neck", 0.6], ["Head", 0.4]]
			hrs.insert(0, low)
			out.append(_arc_panel("hood", hrs, 0.5, 0.74))
		"headband":
			var band := _range(rs, 7.2, 7.9, hair_room + 0.012 * H)
			out.append(NpcBody.loft("headband", band, NpcBody.HEAD_AROUND, false, false))
		"brim_hat":
			var crown: float = def.get("crown", 0.4)
			var crs := _range(rs, 7.6, rs.size() - 1.0, hair_room + 0.012 * H)
			for i in crs.size():
				crs[i].c = (crs[i].c as Vector3) + Vector3(0, crown * 0.3 * H * float(i) / (crs.size() - 1), 0)
			out.append(NpcBody.loft("crown", crs, NpcBody.HEAD_AROUND, false, true))
			var r0: Dictionary = crs[0]
			var brim := _grow(r0, float(def.get("brim", 0.3)) * H)
			brim.c = (r0.c as Vector3) - Vector3(0, 0.01 * H, 0)
			var inner := _grow(r0, 0.0)
			var brs := [inner, brim]
			var p := NpcBody.loft("brim", brs, NpcBody.HEAD_AROUND, false, false)
			var n := p.indices.size()                          # two-sided
			for t in range(0, n, 3):
				p.indices.append_array([p.indices[t], p.indices[t + 2], p.indices[t + 1]])
			out.append(p)
		"headscarf":
			# above the brow (from ring 5 it covered the eyes), tied a little lower at the back
			var crs := _range(rs, 7.4, rs.size() - 1.0, hair_room + 0.008 * H)
			for i in crs.size():
				var tt := 1.0 - float(i) / (crs.size() - 1)
				crs[i].c = (crs[i].c as Vector3) + Vector3(0, -0.04 * H * tt, 0.05 * H * tt)
			out.append(NpcBody.loft("scarf", crs, NpcBody.HEAD_AROUND, false, true))
	return out


# -- the sky folk's things (research/sky_islands/05) ------------------------------------------------------

static func _torso_at(torso: NpcBody.Part, y: float) -> Dictionary:
	## The torso ring at a height (interpolated between the rings round it).
	var rs: Array = torso.rings
	for i in rs.size() - 1:
		var y0: float = (rs[i].c as Vector3).y
		var y1: float = (rs[i + 1].c as Vector3).y
		if y <= y1 or i == rs.size() - 2:
			return _ring_at(rs, i + clampf((y - y0) / maxf(y1 - y0, 1e-4), 0.0, 1.0))
	return rs[-1]


static func _strip(pname: String, pts: Array, half_w: float, half_t: float, w: Array) -> NpcBody.Part:
	## A flat band of cloth through pts (a scarf's or sash's hanging end): boxy rings across it, capped.
	var rs := []
	for i in pts.size():
		var a: Vector3 = pts[maxi(i - 1, 0)]
		var b: Vector3 = pts[mini(i + 1, pts.size() - 1)]
		var along := (b - a).normalized()
		var across := Vector3.RIGHT
		var thick := along.cross(across).normalized()
		rs.append(NpcBody.ring(pts[i], across, thick, half_w, half_t, w, 3.0))
	return NpcBody.loft(pname, rs, 8, true, true)


static func _ball(pname: String, c: Vector3, r: float, w: Array) -> NpcBody.Part:
	var rs := []
	for k in 7:
		var th := PI * k / 6.0
		rs.append(NpcBody.ring(c - Vector3(0, cos(th) * r, 0), Vector3.RIGHT, Vector3.BACK, sin(th) * r, sin(th) * r, w))
	return NpcBody.loft(pname, rs, 12, true, true)


static func _arc_panel(pname: String, rings: Array, centre: float, frac: float) -> NpcBody.Part:
	## _front_panel round any part of the rings: centre 0 front, 0.25 the +x side, 0.5 the back.
	var p := NpcBody.Part.new()
	p.name = pname
	p.rings = rings
	var cols := 9
	p.around = cols - 1
	var acc := 0.0
	for i in rings.size():
		if i > 0:
			acc += ((rings[i].c as Vector3) - (rings[i - 1].c as Vector3)).length()
		for k in cols:
			var t := fposmod(centre - frac * 0.5 + frac * k / (cols - 1.0), 1.0)
			p.verts.append(NpcBody.ring_point(rings[i], t))
			p.uvs.append(Vector2(k * frac * 0.12, acc))
			p.uv2s.append(Vector2(-10, -10))
			NpcBody._push_weights(p, rings[i].w)
	for i in rings.size() - 1:
		for k in cols - 1:
			var a := i * cols + k
			var b := a + 1
			var c := a + cols
			var d := c + 1
			p.indices.append_array([a, c, b, b, c, d])
	NpcBody._orient_outward(p, rings, 0, p.indices.size())
	p.normals.resize(p.verts.size())
	var acc_n := {}
	for t in range(0, p.indices.size(), 3):
		var fn := (p.verts[p.indices[t + 1]] - p.verts[p.indices[t]]).cross(p.verts[p.indices[t + 2]] - p.verts[p.indices[t]])
		for j in 3:
			acc_n[p.indices[t + j]] = acc_n.get(p.indices[t + j], Vector3.ZERO) + fn
	for i in p.verts.size():
		p.normals[i] = (acc_n.get(i, Vector3.FORWARD) as Vector3).normalized()
	var n := p.indices.size()
	for t in range(0, n, 3):
		p.indices.append_array([p.indices[t], p.indices[t + 2], p.indices[t + 1]])
	return p


static func _sash(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	## A wide sash wound round the waist over everything, its end hanging at the left hip.
	var torso: NpcBody.Part = parts.torso
	var y: Array = def.get("y", [3.5, 4.5])
	var rs := _range(torso.rings, float(y[0]), float(y[1]), e + 0.004)
	var out := [NpcBody.loft("sash", rs, NpcBody.RING, false, false)]
	var tail: float = def.get("tail", 0.0)
	if tail > 0.01:
		var r0: Dictionary = rs[0]
		var p0 := NpcBody.ring_point(r0, 0.16)
		var outward := Vector3(p0.x - (r0.c as Vector3).x, 0, p0.z - (r0.c as Vector3).z).normalized()
		var length: float = tail * 0.32 * L.T
		var pts := []
		for i in 5:
			var t := i / 4.0
			pts.append(p0 + Vector3(0, -length * t, 0) + outward * (0.012 + 0.07 * t * t))
		out.append(_strip("sash_end", pts, 0.035 * L.T / 1.65, 0.005, [["Hips", 0.8], ["UpperLegL", 0.2]]))
	return out


static func _scarf(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	## A thick scarf (or cowl) wound round the neck over the collar, an end hanging down the chest.
	var torso: NpcBody.Part = parts.torso
	var nk: NpcBody.Part = parts.neck
	var T: float = L.T
	var bulk: float = def.get("bulk", 0.02)
	var r0 := _grow(torso.rings[-1], 0.0)                # round the base of the neck, not out over the shoulders
	r0.a = float(L.neck_r) * 1.7 + e + bulk
	r0.b = float(L.neck_r) * 1.5 + e + bulk
	r0.c = (r0.c as Vector3) - Vector3(0, 0.006 * T, 0)
	var rs := [r0, _grow(_ring_at(nk.rings, 0.4), e + bulk), _grow(_ring_at(nk.rings, 1.2), e + bulk), _grow(_ring_at(nk.rings, 1.8), e * 0.6 + bulk * 0.7)]
	for i in rs.size():
		rs[i].w = [["UpperChest", 0.5], ["Neck", 0.5]] if i < 2 else [["Neck", 0.85], ["Head", 0.15]]
	var out := [NpcBody.loft("scarf", rs, NpcBody.RING, false, false)]
	var tail: float = def.get("tail", 0.0)
	if tail > 0.01:
		var x := (r0.a as float) * 0.45
		var y0: float = (r0.c as Vector3).y
		var length: float = tail * 0.36 * T
		var pts := []
		for i in 6:
			var t := i / 5.0
			var y := y0 - length * t
			var tr := _torso_at(torso, y)
			pts.append(Vector3(x, y, (tr.c as Vector3).z - float(tr.b) - (e + 0.022) * (0.8 + 0.2 * t)))
		out.append(_strip("scarf_end", pts, 0.042 * T / 1.65, 0.007, [["UpperChest", 0.7], ["Chest", 0.3]]))
	return out


static func _hood(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> NpcBody.Part:
	## A parka's hood thrown back: a fold of cloth lying on the upper back from the collar.
	var torso: NpcBody.Part = parts.torso
	var T: float = L.T
	var a := _grow(torso.rings[-1], e + 0.02)
	a.c = (a.c as Vector3) + Vector3(0, 0.01 * T, 0.004 * T)
	var b := _grow(torso.rings[8], e + 0.045)
	b.c = (b.c as Vector3) + Vector3(0, 0, 0.022 * T)
	var c := _grow(torso.rings[7], e + 0.02)
	c.c = (c.c as Vector3) + Vector3(0, 0, 0.01 * T)
	var rs := [a, b, c]
	for r in rs:
		r.w = [["UpperChest", 0.8], ["Chest", 0.2]]
	return _arc_panel("hood", rs, 0.5, 0.42)


static func _gloves(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	## Gloves over the palm and every finger (they follow the fingers' bones), and a cuff over the wrist --
	## a gauntlet's up the forearm, over the sleeve.
	var out := []
	var ge: float = def.get("ease", 0.0035)
	for side in ["L", "R"]:
		for pn in ["palm", "thumb", "index", "middle", "ring", "pinky"]:
			if not parts.has(pn + side):
				continue
			var p: NpcBody.Part = parts[pn + side]
			if def.get("fingerless", false) and pn != "palm":
				out.append(NpcBody.loft(pn + side + "_glove", _range(p.rings, 0.0, 1.6, ge), p.around, false, false))
			else:
				out.append(NpcBody.loft(pn + side + "_glove", _range(p.rings, 0.0, p.rings.size() - 1.0, ge), p.around, false, true))
		var arm: NpcBody.Part = parts["arm" + side]
		var n := arm.rings.size() - 1.0
		var cuff: float = def.get("cuff", 0.15)
		var crs := _range(arm.rings, n - cuff * n, n, e + 0.004)
		var end := _grow(crs[-1], -0.002)
		end.c = (end.c as Vector3) + ((crs[-1].c as Vector3) - (crs[-2].c as Vector3)).normalized() * 0.01
		crs.append(end)
		out.append(NpcBody.loft("cuff" + side, crs, NpcBody.LIMB, false, false))
	return out


static func _goggles(def: Dictionary, parts: Dictionary, L: Dictionary, extra: float) -> Array:
	## Wind goggles pushed up on the brow: a strap round the head and two round lenses in front.
	var head: NpcBody.Part = parts.head
	var H: float = L.H
	var room := 0.035 * H + 0.016 * H + extra
	var band := _range(head.rings, 6.25, 6.6, room)
	for r in band:
		r.w = [["Head", 1.0]]
	var out := [NpcBody.loft("strap", band, NpcBody.HEAD_AROUND, false, false)]
	var mid := _grow(_ring_at(head.rings, 6.45), room)
	for t in [0.075, -0.075]:
		var p := NpcBody.ring_point(mid, fposmod(t, 1.0))
		var dir := Vector3(p.x - (mid.c as Vector3).x, 0, p.z - (mid.c as Vector3).z).normalized()
		var ax := dir.cross(Vector3.UP).normalized()
		var r := 0.058 * H
		var rs := [NpcBody.ring(p - dir * 0.01 * H, ax, Vector3.UP, r, r, [["Head", 1.0]]),
			NpcBody.ring(p + dir * 0.035 * H, ax, Vector3.UP, r, r, [["Head", 1.0]]),
			NpcBody.ring(p + dir * 0.045 * H, ax, Vector3.UP, r * 0.82, r * 0.82, [["Head", 1.0]])]
		out.append(NpcBody.loft("lens", rs, 12, false, true))
	return out


static func _mittens(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	## Knitted mittens: one shell over the palm and the four fingers, carried by the middle finger's bones (the
	## fingers curl together, so the shell curls with them), the thumb in its own glove, and a cuff.
	var out := []
	var ge: float = def.get("ease", 0.008)
	for side in ["L", "R"]:
		var palm: NpcBody.Part = parts["palm" + side]
		var mid: NpcBody.Part = parts["middle" + side]
		var rs := _range(palm.rings, 0.0, palm.rings.size() - 1.0, ge)
		var wide: Dictionary = rs[-1]
		var fr: Array = mid.rings
		for i in range(1, fr.size()):
			var f: Dictionary = fr[i]
			var k := 1.0 - 0.35 * pow(float(i) / (fr.size() - 1), 2.0)          # rounded off at the tip
			rs.append(NpcBody.ring(f.c, f.ax, f.az, float(wide.a) * k, float(wide.b) * k, f.w, 2.2))
		out.append(NpcBody.loft("mitten" + side, rs, NpcBody.LIMB, false, true))
		var th: NpcBody.Part = parts["thumb" + side]
		out.append(NpcBody.loft("thumb" + side + "_mitt", _range(th.rings, 0.0, th.rings.size() - 1.0, ge), th.around, false, true))
	var arms := {"armL": parts.armL, "armR": parts.armR}             # (only the arms: _gloves makes just the cuffs)
	out.append_array(_gloves({"cuff": def.get("cuff", 0.15), "ease": ge}, arms, L, e))
	return out


static func _cape(length: float, parts: Dictionary, L: Dictionary, e: float) -> NpcBody.Part:
	## A short shoulder cape over a coat (the factors' and knot keepers' cape coat): from the collar, round over
	## the shoulders and the tops of the arms, hanging to about the elbow.
	var torso: NpcBody.Part = parts.torso
	var T: float = L.T
	var top := _grow(torso.rings[-1], e + 0.01)
	top.e = 2.0
	var sh := _grow(torso.rings[8], e + 0.02)
	sh.a = float(L.shoulder_w) + 1.5 * float(L.upperarm_r) + e
	sh.b = float(sh.b) + 0.012
	sh.e = 2.0
	var y_end: float = float(L.shoulder_y) - (0.06 + length * 0.1) * T
	var hem := _grow(_torso_at(torso, y_end), e + 0.04)
	hem.a = float(sh.a) + 0.035 * T
	hem.b = float(hem.b) + 0.025
	hem.c = Vector3(0, y_end, (hem.c as Vector3).z)
	hem.e = 2.0
	var rs := [top, sh, hem]
	for r in rs:
		r.w = [["UpperChest", 0.7], ["Chest", 0.3]]
	return NpcBody.loft("cape", rs, NpcBody.RING + 4, false, false)


static func _harness(def: Dictionary, parts: Dictionary, L: Dictionary, e: float) -> Array:
	## A rim harness: a webbing belt, two straps over the shoulders, and a short tether with its clip at the hip.
	var torso: NpcBody.Part = parts.torso
	var T: float = L.T
	var out := [NpcBody.loft("belt", _range(torso.rings, 3.7, 4.1, e + 0.006), NpcBody.RING, false, false)]
	var off := e + 0.008
	for sx in [-1.0, 1.0]:
		var x: float = sx * 0.085 * T / 1.65
		var pts := []
		for y in [float(L.waist_y), lerpf(float(L.waist_y), float(L.chest_y), 0.6), float(L.chest_y), lerpf(float(L.chest_y), float(L.shoulder_y), 0.7)]:
			var tr := _torso_at(torso, y)
			pts.append(Vector3(x, y, (tr.c as Vector3).z - float(tr.b) - off))
		var ts := _torso_at(torso, float(L.shoulder_y))
		pts.append(Vector3(x, float(L.shoulder_y) + 0.012 * T + off * 0.6, (ts.c as Vector3).z))
		for y in [lerpf(float(L.chest_y), float(L.shoulder_y), 0.7), float(L.chest_y), float(L.waist_y)]:
			var tr := _torso_at(torso, y)
			pts.append(Vector3(x, y, (tr.c as Vector3).z + float(tr.b) + off))
		out.append(_strip("strap", pts, 0.016, 0.003, [["UpperChest", 0.6], ["Chest", 0.4]]))
	var r0: Dictionary = _grow(_ring_at(torso.rings, 3.9), e + 0.006)
	var p0 := NpcBody.ring_point(r0, 0.3)
	var tether := []
	for i in 4:
		tether.append(p0 + Vector3(0.012 * i, -0.06 * T * i, 0.0))
	out.append(_strip("tether", tether, 0.012, 0.004, [["Hips", 1.0]]))
	out.append(_ball("clip", tether[-1] + Vector3(0, -0.015, 0), 0.016, [["Hips", 1.0]]))
	return out


static func _trim(of: Dictionary, body: Dictionary, layer_ease: float) -> Array:
	## The trim of a garment (of): its own hem, cuffs and collar rebuilt a few mm proud of it, kept only near
	## their ends -- a band round each, drawn in the trim's colour.
	var out := []
	var T: float = body.landmarks.T
	for p: NpcBody.Part in build(of, body, layer_ease + 0.003):
		var rs: Array = p.rings
		if rs.size() < 2:
			continue
		var band := 0.0
		var from_end := true
		match p.name:
			"coat_skirt", "dress_skirt":
				band = 0.06 * T
			"sleeveL", "sleeveR":
				band = 0.045 * T
			"top":
				band = 0.03 * T if str(of.get("neck", "")) in ["funnel", "collar"] else 0.0
				if float(of.get("hem", 0.0)) < 0.02:
					out.append(_band(rs, 0.05 * T, false, p.name + "_hemtrim"))
		if band > 0.0:
			out.append(_band(rs, band, from_end, p.name + "_trim"))
	return out


static func _band(rs: Array, length: float, from_end: bool, pname: String) -> NpcBody.Part:
	## The rings of a loft within length (m, along it) of its last ring (or its first), as their own loft.
	var order: Array = rs.duplicate()
	if from_end:
		order.reverse()
	var out := [order[0]]
	var acc := 0.0
	for i in range(1, order.size()):
		var d := ((order[i].c as Vector3) - (order[i - 1].c as Vector3)).length()
		if acc + d >= length:
			var t := (length - acc) / maxf(d, 1e-5)
			var r: Dictionary = (order[i - 1] as Dictionary).duplicate()
			r.c = (order[i - 1].c as Vector3).lerp(order[i].c, t)
			r.a = lerpf(float(order[i - 1].a), float(order[i].a), t)
			r.b = lerpf(float(order[i - 1].b), float(order[i].b), t)
			out.append(r)
			break
		acc += d
		out.append(order[i])
	if from_end:
		out.reverse()
	return NpcBody.loft(pname, out, NpcBody.RING + 4 if pname.begins_with("coat") or pname.begins_with("dress") else NpcBody.LIMB if pname.begins_with("sleeve") else NpcBody.RING, false, false)
