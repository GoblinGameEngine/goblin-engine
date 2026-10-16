extends SceneTree

## The sky side of the market moorings (research/flea_markets/00_plan.md §12 "flea_sky_test"; handoff_sky.md):
## SkyDrift with SkyMooring driving the booked rafts, stepped through real bookings.
##   - every booked island reaches its berth by its arrival and holds there (within 5 m) at MOOR_H while moored;
##   - followers lash to the raft (one raft per booking at the market), rafts <= 10, only the tier's first n ground;
##   - nobody hangs over a market floor (the layout), the hosts' ropeways reach a ground station;
##   - each casts off at its leave hour and climbs back into the band;
##   - a clock jump into a stay places the raft at once (snapped);
##   - SkyMooring.drive's cost per step.
##   ../godot/godot4 --headless --path . --script res://remake/tools/flea_sky_test.gd [-- bookings]

var fails := 0


func check(ok: bool, what: String) -> void:
	if not ok:
		fails += 1
	print("PASS " if ok else "FAIL ", what)


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	var want_n := int(a[0]) if a.size() > 0 else 3
	var lay: Dictionary = JSON.parse_string(DataFile.text("res://remake/sky/islands.json"))
	var defs := []
	for L in lay.islands:
		defs.append({"id": L.id, "faces": L.faces, "bridges": L.bridges})
	var drift := SkyDrift.new()
	drift.setup(defs)
	var mo := drift.mooring
	check(not mo.moor.is_empty(), "moorings.json loaded: %d islands" % mo.moor.size())
	# the bookings to follow: rafts of 3+ first (a fair), at sited markets
	var picks: Array = []
	for w in range(1, 40):
		for b in FleaCalendar.week_plan(w):
			var M := FleaData.market(str(b.market))
			if M.get("sited", false) and int(b.n) >= 3 and picks.size() < want_n:
				picks.append(b)
	check(picks.size() > 0, "bookings of 3+ found: %d" % picks.size())
	var t_drive := 0
	var n_drive := 0
	for b in picks:
		var L := mo.layout(b, drift)
		var M: Dictionary = L.M
		print("-- %s at %s (%s), %d members" % [b.id, M.id, M.tier, b.n])
		var host_ok := not (L.members[0].station as Dictionary).is_empty()
		check(host_ok, "  host %s has a ropeway station, ground station at %s" % [L.members[0].island, L.members[0].gstation])
		var over := 0.0
		for r in L.members:
			if r.absent:
				continue
			over = maxf(over, mo._over_floor(M, L.origin, r.off, int(r.i), drift))
		check(over == 0.0, "  nobody over the floor (+20 m): worst share %.2f" % over)
		var absent := 0
		for r in L.members:
			absent += 1 if r.absent else 0
		print("  absent (no free face): %d / %d" % [absent, L.members.size()])
		# fly it: from a day and a half before the host arrives to its last member's leave + 2 h
		var A0 := float(b.members[0].arrive)
		var t_end := 0.0
		for e in b.members:
			t_end = maxf(t_end, float(e.leave))
		var now := A0 - 30.0
		var dt := 10.0
		var worst_hold := 0.0
		var worst_h := 0.0
		var lashed_ok := true
		var max_raft := 0
		var ground_ok := true
		var cast_ok := true
		var arrived := {}
		var steps := 0
		while now < t_end + 2.0:
			mo.now_h = now
			var t0 := Time.get_ticks_usec()
			drift.step(dt)
			t_drive += Time.get_ticks_usec() - t0
			n_drive += 1
			now += dt / SkyMooring.HOUR_S
			steps += 1
			if steps % 600 == 0:
				print("    t %.1f h (%d steps, %.0f us a step)" % [now - A0, steps, float(t_drive) / maxf(n_drive, 1)])
			if steps % 6 != 0:
				continue
			var ids_in := {}
			for kk in (b.members as Array).size():
				var e: Dictionary = b.members[kk]
				var rec: Dictionary = L.members[kk]
				if rec.absent:
					continue
				var i: int = rec.i
				var ph := SkyMooring.phase_at(e, bool(e.ground), now)
				if ph in ["HOLD", "CREW_DOWN", "ANCHOR", "LOGISTICS", "RIGGING", "SERVICE", "STRIKE", "LASHED"]:
					var p := drift.pos(i)
					var tg := mo.target_of(mo.members[i]) if mo.members.has(i) else p
					var d := Vector2(StationGeo.wrap_ds(p.x - tg.x), p.y - tg.y).length()
					if now > float(e.arrive) + 0.6:
						worst_hold = maxf(worst_hold, d)
						worst_h = maxf(worst_h, absf(drift.altitude(i) - SkyMooring.MOOR_H))
						arrived[i] = true
						ids_in[drift.islands[i].raft] = true
						max_raft = maxi(max_raft, drift.raft_of(i).members.size())
				elif ph == "" and now > float(e.leave) + 1.0 and arrived.has(i):
					if mo.members.has(i) or drift.raft_of(i).get("held", false):
						cast_ok = false
			# (one raft per booking once everyone present has lashed: those whose parent is here)
			if ids_in.size() > 1:
				var lone := 0
				for kk in (b.members as Array).size():
					var rec2: Dictionary = L.members[kk]
					if rec2.absent or not arrived.has(rec2.i):
						continue
					var pk := int(rec2.parent)
					if pk >= 0 and arrived.has(L.members[pk].i) and drift.islands[rec2.i].raft != drift.islands[L.members[pk].i].raft:
						if now > float(b.members[kk].arrive) + 0.2 and now < float(b.members[kk].leave) - 0.1 \
								and now < float(b.members[pk].leave) - 0.1:
							lone += 1
				if lone > 0:
					lashed_ok = false
		var gn := 0
		for r in L.members:
			gn += 1 if (not r.absent and r.ground) else 0
		ground_ok = gn <= int((M.get("mooring_tier", {}) as Dictionary).get("ground_islands", 3))
		check(arrived.size() > 0, "  arrived and moored: %d" % arrived.size())
		check(worst_hold < 5.0, "  held over the berth: worst %.2f m" % worst_hold)
		check(worst_h < 25.0, "  at the moor height: worst %.1f m off %d m" % [worst_h, int(SkyMooring.MOOR_H)])
		check(lashed_ok, "  followers lashed to their parents (one raft)")
		check(max_raft <= SkyDrift.MAX_RAFT, "  rafts <= %d: %d" % [SkyDrift.MAX_RAFT, max_raft])
		check(ground_ok, "  ground-anchored <= the tier's %d: %d" % [int((M.get("mooring_tier", {}) as Dictionary).get("ground_islands", 3)), gn])
		check(cast_ok, "  cast off and free after leaving")
		# a clock jump into the middle of the stay: placed at once
		var mid := float(b.members[0].service) + 5.0
		mo.now_h = mid
		drift.step(dt)
		var i0: int = L.members[0].i
		var p0 := drift.pos(i0)
		var tg0 := mo.target_of(mo.members[i0]) if mo.members.has(i0) else Vector2.INF
		var d0 := Vector2(StationGeo.wrap_ds(p0.x - tg0.x), p0.y - tg0.y).length() if tg0.is_finite() else INF
		check(d0 < 5.0 and absf(drift.altitude(i0) - SkyMooring.MOOR_H) < 1.0,
			"  a clock jump into the stay: host at %.2f m, %.0f m up (snapped %d)" % [d0, drift.altitude(i0), mo.snapped.size()])
	# the mooring's own cost: the game's step (SkyIslands: 10 Hz, dt 0.1 s) and the fast-forward step (warm_up /
	# this test, dt 10-30); the drift's own meetings / keep-apart are not ours (they ran pre-moorings too)
	var t1 := Time.get_ticks_usec()
	for k in 200:
		mo.drive(drift, 0.1)
	var per := float(Time.get_ticks_usec() - t1) / 200.0
	check(per < 300.0, "SkyMooring.drive at dt 0.1: %.0f us a step (budget 300 us)" % per)
	t1 = Time.get_ticks_usec()
	for k in 200:
		mo.now_h += 10.0 / SkyMooring.HOUR_S
		mo.drive(drift, 10.0)
	var per10 := float(Time.get_ticks_usec() - t1) / 200.0
	check(per10 < 800.0, "SkyMooring.drive at dt 10: %.0f us a step (budget 800 us; SkyDrift.step whole %.0f us at dt 10)" % [per10, float(t_drive) / maxf(n_drive, 1)])
	print("log (last 12):")
	for e in mo.log_events.slice(-12):
		print("  %.2f %s %s %s" % [e[0], e[1], e[2], e[3]])
	print("flea_sky_test: %s (%d failures)" % ["PASS" if fails == 0 else "FAIL", fails])
	quit(1 if fails else 0)
