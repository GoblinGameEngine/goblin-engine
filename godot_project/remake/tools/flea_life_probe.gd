extends SceneTree

## A quick look at the flea hooks in people's days (handoff_world.md): load time, vending and market trips on a
## weekend, a sample of FleaMarkets.vendor_spot.
##   ../godot/godot4 --headless --path . --script res://remake/tools/flea_life_probe.gd [-- town]

func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	var town := a[0] if a.size() > 0 else "Calder"
	var t0 := Time.get_ticks_msec()
	print("probe start")
	NpcPlaces.load_all()
	print("places %d ms" % (Time.get_ticks_msec() - t0))
	var life := NpcLife.shared()
	print("life %d ms" % (Time.get_ticks_msec() - t0))
	var M := FleaData.of_town(town)
	var pool: PackedStringArray = FleaVendors.pool(M.id).pids
	var day := 2                                       # Friday
	var vend := 0
	var trips := 0
	var flea := 0
	var n := 0
	var t1 := Time.get_ticks_msec()
	for pid in pool.slice(0, 400):
		n += 1
		for s in life.stays(pid, day):
			if s.what == "vending":
				vend += 1
			elif s.what == "market_trip":
				trips += 1
			elif s.what == "flea":
				flea += 1
	print("%s pool sample %d: vending %d, trips %d, flea errands %d (%d ms)" % [M.id, n, vend, trips, flea, Time.get_ticks_msec() - t1])
	var r := FleaVendors.roster(M, day)
	print("roster: local %d islander %d of %d" % [r.local, r.islander, r.n])
	for i in 3:
		var w := int((r.who as PackedInt32Array)[i])
		if w >= 0:
			print("  stall %d vendor %s at %s" % [i, pool[w], FleaMarkets.vendor_spot(pool[w], day)])
	print("done %d ms" % (Time.get_ticks_msec() - t0))
	quit()
