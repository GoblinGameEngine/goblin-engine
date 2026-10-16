extends SceneTree

## The island bookings over 20 simulated years (research/flea_markets/00_plan.md §5.1, §12 "flea_occasions_test"):
##   - moorings a year by tier (cities ~83, towns ~104, villages ~78: +-30 %);
##   - rafts >= 3 / >= 5 / >= 7 per mooring by tier against q^(k-1) (+-30 %);
##   - Bright Weeks ~20 a year (+-30 %), Sky Holidays ~1.8 a year (+-50 %), HOLIDAY only at towns and villages, at
##     most 3 days in a row; CELEBRATION opens the local booths every day;
##   - stays: >= 60 % leave after one weekend, none over 21 days, followers <= host + 7 days; rafts <= 10; no island
##     at two markets at once; the Great Fairs and Market Days happen.
##   ../godot/godot4 --headless --path . --script res://remake/tools/flea_occasions_test.gd [-- years]

var fails := 0


func check(ok: bool, what: String) -> void:
	if not ok:
		fails += 1
	print("PASS " if ok else "FAIL ", what)


func near(got: float, want: float, tol: float, what: String) -> void:
	check(absf(got - want) <= tol * want, "%s: %.2f (expected %.2f +-%d %%)" % [what, got, want, int(tol * 100)])


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	var years := int(a[0]) if a.size() > 0 else 20
	var t0 := Time.get_ticks_msec()
	var weeks := int(years * 52.18)
	var mo := {"city": 0, "town": 0, "village": 0}
	var ge := {}
	for t in mo:
		ge[t] = [0, 0, 0, 0]          # >= 3, >= 5, >= 7, == 10
	var bright := 0
	var fair_n := 0
	var fair_sim := 0
	var bright_sim := 0
	var specials := {"great_fair": 0, "market_day": 0}
	var stays := [0, 0, 0]
	var over21 := 0
	var past_host := 0
	var over10 := 0
	var island_busy := {}            # island -> [[arrive, leave]]
	var clash := 0
	var hol_runs := 0
	var hol_bad_tier := 0
	var hol_long := 0
	var cel_shut := 0
	var hol_markets := {}
	for w in range(0, weeks):
		for b in FleaCalendar.week_plan(w):
			var M := FleaData.market(b.market)
			var tier := str(M.tier)
			var n := int(b.n)
			mo[tier] += 1
			if b.kind != "":
				specials[b.kind] += 1
			for i in 4:
				if n >= [3, 5, 7, 10][i]:
					ge[tier][i] += 1
			if n > 10:
				over10 += 1
			var host: Dictionary = b.members[0]
			for e in b.members:
				var weekends := roundi((float(e.leave) - FleaCalendar._mon_after(float(e.arrive))) / 168.0) + 1
				stays[clampi(weekends - 1, 0, 2)] += 1
				if float(e.leave) - float(e.arrive) > 21.0 * 24.0 + 0.01:
					over21 += 1
				if e.role == "follower" and float(e.leave) > float(host.leave) + 7.0 * 24.0 + 0.01:
					past_host += 1
				var busy: Array = island_busy.get(e.island, [])
				for iv in busy:
					if float(e.arrive) < float(iv[1]) and float(iv[0]) < float(e.leave):
						clash += 1
				busy.append([float(e.arrive), float(e.leave)])
				island_busy[e.island] = busy.slice(-4)
			if n >= 3:
				fair_n += 1
				var mx := 0
				for e in b.members:
					mx = maxi(mx, FleaCalendar.in_service(M, float(e.service) + 0.01))
				if mx >= 3:
					fair_sim += 1
			if n >= 5:
				bright += 1
				var last: Dictionary = b.members[-1]
				if FleaCalendar.in_service(M, float(last.service) + 0.01) >= 5:
					bright_sim += 1
			if n >= 7:
				# the Sky Holiday's days at this booking
				var d0 := floori(float(host.arrive) / 24.0)
				var d1 := 0
				for e in b.members:
					d1 = maxi(d1, floori(float(e.leave) / 24.0))
				var run := 0
				for d in range(d0, d1 + 1):
					var hol := FleaCalendar.is_holiday(M, d)
					if hol:
						if tier == "city":
							hol_bad_tier += 1
						if run == 0:
							hol_runs += 1
							hol_markets[b.market] = int(hol_markets.get(b.market, 0)) + 1
						run += 1
						if run > 3:
							hol_long += 1
					else:
						run = 0
					if FleaCalendar.is_celebration(M, d) and not FleaCalendar.state(M, d, 10.0).local_open:
						cel_shut += 1
	var yr := float(weeks) / 52.18
	print("%d years, %d weeks: moorings city %d town %d village %d; specials %s" % [years, weeks, mo.city, mo.town, mo.village, specials])
	near(mo.city / yr, 4 * 0.40 * 52 + 4 * 0.6, 0.30, "city moorings a year")
	near(mo.town / yr, 8 * 0.25 * 52 + 8 * 0.55, 0.30, "town moorings a year")
	near(mo.village / yr, 10 * 0.15 * 52 + 10 * 0.65, 0.30, "village moorings a year")
	var Q := {"city": 0.60, "town": 0.45, "village": 0.42}
	for t in ["city", "town", "village"]:
		var nn := float(mo[t])
		print("  %s: >= 3 %.3f, >= 5 %.3f, >= 7 %.4f, 10 %.4f" % [t, ge[t][0] / nn, ge[t][1] / nn, ge[t][2] / nn, ge[t][3] / nn])
		near(ge[t][0] / nn, pow(Q[t], 2), 0.30, "%s rafts >= 3 per mooring" % t)
		near(ge[t][1] / nn, pow(Q[t], 4), 0.30, "%s rafts >= 5 per mooring" % t)
	near(bright / yr, 20.0, 0.30, "Bright Weeks a year")
	check(bright_sim == bright, "every raft of 5+ has 5 in SERVICE at once (%d/%d)" % [bright_sim, bright])
	check(fair_sim >= 0.9 * fair_n, "rafts of 3+ make a fair (3 in SERVICE at once): %d/%d" % [fair_sim, fair_n])
	near(hol_runs / yr, 1.8, 0.50, "Sky Holidays a year")
	print("  holidays by market: ", hol_markets)
	check(hol_bad_tier == 0, "HOLIDAY only at towns and villages (%d city days)" % hol_bad_tier)
	check(hol_long == 0, "HOLIDAY at most 3 days in a row (%d longer)" % hol_long)
	check(cel_shut == 0, "CELEBRATION opens the local booths every day (%d shut)" % cel_shut)
	var tot := float(stays[0] + stays[1] + stays[2])
	print("  stays: one weekend %.2f, two %.2f, three %.2f" % [stays[0] / tot, stays[1] / tot, stays[2] / tot])
	check(stays[0] / tot >= 0.60, ">= 60 % leave after one weekend")
	check(over21 == 0, "no stay over 21 days (%d)" % over21)
	check(past_host == 0, "no follower past its host + 7 days (%d)" % past_host)
	check(over10 == 0, "rafts <= 10")
	check(clash == 0, "no island at two markets at once (%d clashes)" % clash)
	check(specials.great_fair >= years * 4 - 2, "a Great Fair a city a year (%d)" % specials.great_fair)
	print("%s  (%d ms)" % ["PASS" if fails == 0 else "FAILED %d" % fails, Time.get_ticks_msec() - t0])
	quit(0 if fails == 0 else 1)
