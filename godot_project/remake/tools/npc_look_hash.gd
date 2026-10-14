extends SceneTree

## A fingerprint of how generated people look: traits, outfit picks and colours, and the body and
## clothes geometry, for N people across every population.  Run before and after a change to the
## generator that must not alter existing people (e.g. a new outfit family): the two hashes must match.
##   ../godot/godot4 --headless --path . --script res://remake/tools/npc_look_hash.gd [-- people]

func _init() -> void:
	var a := OS.get_cmdline_user_args()
	var people := int(a[0]) if a.size() > 0 else 400
	var db := NpcTraits.shared()
	var pops := ["", "stable_town", "rust_belt", "exurban", "county_seat", "college_town", "lake_resort"]
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	for i in people:
		var pid := "B%d:%d" % [70000 + i, i % 4]
		var v := db.person(7, pid, ["L0", "L1"], pops[i % pops.size()])
		for occ in ["work", "casual"]:
			var d := NpcCharacter.prepare(v, pid, 7, occ)
			var s := JSON.stringify(v)
			for g in d.outfit:
				s += "|%s/%s/%s/%s/%s" % [g.slot, g.garment, (g.colour as Color).to_html(), g.pattern, g.scale]
			ctx.update(s.to_utf8_buffer())
			for surf in d.surfaces:
				var arr: Array = surf.arrays
				ctx.update((arr[Mesh.ARRAY_VERTEX] as PackedVector3Array).to_byte_array())
				ctx.update((arr[Mesh.ARRAY_INDEX] as PackedInt32Array).to_byte_array())
			ctx.update((d.body[Mesh.ARRAY_VERTEX] as PackedVector3Array).to_byte_array())
	print("look hash (%d people): %s" % [people, ctx.finish().hex_encode()])
	quit(0)
