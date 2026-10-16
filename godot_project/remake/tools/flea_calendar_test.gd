extends SceneTree

## The flea markets' pure model (research/flea_markets/00_plan.md §12 "flea_calendar_test"):
##   - day 0 is Wednesday 2752-05-24;
##   - over 730 days x 22 markets: occupancy >= 0.80 on every day the town's booths open;
##   - 35 % permanent (+-1 stall); season terms 8-16 weeks; nobody holds two stalls a day; day vendors only on
##     vacancies; the town's booths never open Mon-Thu outside a Bright Week or Sky Holiday;
##   - the modes and phases of §4.2; purity (fresh caches, another order: the same answers).
##   ../godot/godot4 --headless --path . --script res://remake/tools/flea_calendar_test.gd [-- days]

var fails := 0


func check(ok: bool, what: String) -> void:
	if not ok:
		fails += 1
		print("FAIL ", what)


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	var days := int(a[0]) if a.size() > 0 else 730
	var t0 := Time.get_ticks_msec()
	var ms := FleaData.markets()
	check(ms.size() == 22, "22 markets (got %d)" % ms.size())
	check(StationCalendar.weekday(0) == 2, "day 0 is a Wednesday")
	var d0 := StationCalendar.date(0)
	check(int(d0.y) == 2752 and int(d0.m) == 5 and int(d0.d) == 24, "day 0 is 2752-05-24")
	# 35 % permanent
	for M in ms:
		var n := (M.kind as PackedByteArray).size()
		var perm := 0
		for v in (M.perm as PackedByteArray):
			perm += v
		check(absf(perm - 0.35 * n) <= 1.0, "%s permanent %d of %d" % [M.id, perm, n])
		check(FleaVendors.pool(M.id).n >= n, "%s pool %d >= stalls %d" % [M.id, FleaVendors.pool(M.id).n, n])
	# occupancy, every open day
	var worst := 1.0
	var worst_at := ""
	var open_days := 0
	var sum_occ := 0.0
	var weekday_local := 0
	var dup := 0
	var isl_days := 0
	var isl_fill_bad := 0
	for M in ms:
		for day in days:
			var wd := StationCalendar.weekday(day)
			var openday := FleaCalendar.market_open_day(M, day)
			var r := FleaVendors.roster(M, day)
			if openday:
				var occ := float(r.local) / float(r.n)
				open_days += 1
				sum_occ += occ
				if occ < worst:
					worst = occ
					worst_at = "%s day %d" % [M.id, day]
				var seen := {}
				for w in (r.who as PackedInt32Array):
					if w >= 0:
						if seen.has(w):
							dup += 1
						seen[w] = true
			elif int(r.local) > 0:
				weekday_local += 1
			if int(r.get("islander", 0)) > 0:
				isl_days += 1
				# islanders fill exactly the vacancies (every stall is held on an open day)
				if openday:
					var held := 0
					for k in (r.kind as PackedByteArray):
						if k != 0:
							held += 1
					if held != int(r.n):
						isl_fill_bad += 1
			check(wd >= 4 or openday or int(r.local) == 0, "%s day %d: local booths on a weekday" % [M.id, day])
	check(worst >= 0.80, "occupancy >= 0.80 on every open day (worst %.3f at %s)" % [worst, worst_at])
	check(dup == 0, "nobody holds two stalls a day (%d doubles)" % dup)
	check(weekday_local == 0, "local booths shut Mon-Thu (%d days open)" % weekday_local)
	check(isl_fill_bad == 0, "islanders fill every vacancy on open days (%d short)" % isl_fill_bad)
	print("occupancy: %d open market-days, mean %.3f, worst %.3f (%s); islander days %d" % [open_days, sum_occ / maxf(1, open_days), worst, worst_at, isl_days])
	# season terms 8-16 weeks
	var M0: Dictionary = FleaData.market("FM-SOL")
	var bad_terms := 0
	var terms := 0
	for s in (M0.kind as PackedByteArray).size():
		if int((M0.perm as PackedByteArray)[s]) == 1:
			continue
		var last := -999
		var start := 0
		for w in range(0, 160):
			var L := FleaVendors._lease(M0, s, w)
			if int(L[3]) != last:
				if last != -999 and start > 0:
					var len_ := w - start
					terms += 1
					if len_ < 8 or len_ > 16:
						bad_terms += 1
				last = int(L[3])
				start = w
	check(bad_terms == 0, "season terms 8-16 weeks (%d of %d outside)" % [bad_terms, terms])
	print("season terms checked: %d" % terms)
	# permanent leases: 52 weeks, renewed ~85 %
	var changes := 0
	var perm_terms := 0
	for s in (M0.kind as PackedByteArray).size():
		if int((M0.perm as PackedByteArray)[s]) == 0:
			continue
		var prev := -2
		for w in range(0, 520, 52):
			var L := FleaVendors._lease(M0, s, w + 10)
			perm_terms += 1
			if prev != -2 and int(L[0]) != prev:
				changes += 1
			prev = int(L[0])
	print("permanent: %d lease-years, %.1f %% changed hands" % [perm_terms, 100.0 * changes / maxf(1, perm_terms)])
	# modes (§4.2): find a quiet week and a moored one
	var quiet := -1
	for day in range(0, 200):
		if StationCalendar.weekday(day) == 2 and FleaCalendar.bookings_on("FM-LG", day).is_empty() and FleaCalendar.bookings_on("FM-LG", day + 2).is_empty():
			quiet = day
			break
	check(quiet >= 0, "a quiet week at Loomis Grove")
	if quiet >= 0:
		var s := FleaCalendar.state("FM-LG", quiet, 10.0)
		check(s.mode == "CLOSED" and not s.local_open, "Wed 10:00 with no island: CLOSED (%s)" % s.mode)
		check(s.lot_lit == false and FleaCalendar.state("FM-LG", quiet, 23.0).lot_lit, "the lot is lit dusk to dawn")
		var f := FleaCalendar.state("FM-LG", quiet + 2, 10.0)
		check(f.mode == "LOCAL" and f.phase == "OPEN" and f.local_open, "Fri 10:00: LOCAL OPEN (%s %s)" % [f.mode, f.phase])
		check(FleaCalendar.state("FM-LG", quiet + 2, 8.0).phase == "SETUP", "Fri 08:00 SETUP")
		check(FleaCalendar.state("FM-LG", quiet + 2, 18.5).phase == "TEARDOWN", "Fri 18:30 TEARDOWN")
		check(FleaCalendar.state("FM-LG", quiet + 2, 22.0).phase == "AFTER_HOURS", "Fri 22:00 AFTER_HOURS")
		check(not FleaCalendar.state("FM-LG", quiet + 2, 22.0).local_open, "after hours: shut")
	# a moored weekday: ISLANDER, islanders open, local shut; gondolas carry people only after hours
	var found := false
	for w in range(0, 60):
		for b in FleaCalendar.week_plan(w):
			if found or b.kind != "":
				continue
			var e: Dictionary = b.members[0]
			var dd := floori((float(e.service) + 24.0) / 24.0)
			if StationCalendar.weekday(dd) >= 4 or FleaCalendar.is_celebration(b.market, dd) or float(e.leave) < dd * 24.0 + 20.0:
				continue
			var st := FleaCalendar.state(b.market, dd, 11.0)
			check(st.mode == "ISLANDER" and st.islander_open and not st.local_open, "%s day %d: ISLANDER (%s)" % [b.market, dd, st.mode])
			check(st.gondolas == "all", "gondolas run cargo by day (%s)" % st.gondolas)
			check(FleaCalendar.state(b.market, dd, 23.0).gondolas == "passenger", "after hours: passengers only")
			var r := FleaVendors.roster(b.market, dd)
			check(int(r.local) == 0 and int(r.islander) > 0, "ISLANDER day roster: islanders only (%d local, %d islander)" % [r.local, r.islander])
			found = true
	check(found, "found a moored weekday")
	# Bright Week: the whole market every day
	var bw := false
	for w in range(0, 520):
		if bw:
			break
		for b in FleaCalendar.week_plan(w):
			if int(b.n) < 5 or bw:
				continue
			var last: Dictionary = b.members[-1]
			var dd := floori(float(last.service) / 24.0) + 1
			if not FleaCalendar.is_celebration(b.market, dd):
				continue
			for k in 7:
				if StationCalendar.weekday(dd + k) < 4 and FleaCalendar.is_celebration(b.market, dd + k):
					var st := FleaCalendar.state(b.market, dd + k, 10.0)
					check(st.mode in ["CELEBRATION", "HOLIDAY"] and st.local_open, "Bright Week weekday open (%s)" % st.mode)
					check(FleaVendors.occupancy(b.market, dd + k) >= 0.8, "Bright Week weekday >= 80 %")
					check(FleaCalendar.state(b.market, dd + k, 19.5).phase == "LANTERN", "lantern market at 19:30")
					bw = true
					break
	check(bw, "found a Bright Week weekday")
	# purity: fresh caches, the reverse order
	var snap := {}
	for M in ms:
		for day in [3, 30, 101, 333]:
			snap["%s|%d" % [M.id, day]] = str(FleaVendors.roster(M, day).who) + str(FleaCalendar.state(M, day, 12.0))
	FleaVendors._cache = {}
	FleaVendors._cache_old = {}
	FleaCalendar._plans = {}
	FleaCalendar._plans_old = {}
	var same := 0
	var keys := snap.keys()
	keys.reverse()
	for k in keys:
		var id: String = k.get_slice("|", 0)
		var day := int(k.get_slice("|", 1))
		if str(FleaVendors.roster(id, day).who) + str(FleaCalendar.state(id, day, 12.0)) == snap[k]:
			same += 1
	check(same == keys.size(), "purity: %d/%d identical" % [same, keys.size()])
	# vending: the roster's people find their stall
	var vd := 0
	var vok := 0
	var M1: Dictionary = FleaData.market("FM-C")
	for day in range(2, 30):
		if not FleaCalendar.market_open_day(M1, day):
			continue
		var r := FleaVendors.roster(M1, day)
		var pids: PackedStringArray = FleaVendors.pool(M1.id).pids
		for s in (r.who as PackedInt32Array).size():
			var w := int((r.who as PackedInt32Array)[s])
			if w >= 0:
				vd += 1
				if int(FleaVendors.vending(pids[w], day).get("stall", -1)) == s:
					vok += 1
	check(vd > 0 and vok == vd, "vending() finds every vendor's stall (%d/%d)" % [vok, vd])
	print("tenant sample: ", FleaVendors.tenant("FM-SOL", 5, 2), " ", FleaVendors.tenant("FM-SOL", 300, 3))
	print("%s  (%d ms)" % ["PASS" if fails == 0 else "FAILED %d" % fails, Time.get_ticks_msec() - t0])
	quit(0 if fails == 0 else 1)
