extends SceneTree
## micro-benchmark of SkyMooring (handoff_sky.md): drive vs refresh vs the drift's own step
func _initialize() -> void:
	var lay: Dictionary = JSON.parse_string(DataFile.text("res://remake/sky/islands.json"))
	var defs := []
	for L in lay.islands:
		defs.append({"id": L.id, "faces": L.faces, "bridges": L.bridges})
	var drift := SkyDrift.new()
	drift.setup(defs)
	var mo := drift.mooring
	var b: Dictionary = {}
	for w in range(1, 40):
		for bb in FleaCalendar.week_plan(w):
			if FleaData.market(str(bb.market)).get("sited", false) and int(bb.n) >= 3 and b.is_empty():
				b = bb
	mo.now_h = float(b.members[0].service) + 3.0
	drift.step(0.1)
	var t0 := Time.get_ticks_usec()
	for k in 200:
		mo._refresh(drift)
	print("refresh %.0f us" % ((Time.get_ticks_usec() - t0) / 200.0))
	t0 = Time.get_ticks_usec()
	for k in 200:
		mo.drive(drift, 0.1)
	print("drive %.0f us (members %d)" % [(Time.get_ticks_usec() - t0) / 200.0, mo.members.size()])
	var keep := drift.mooring
	drift.mooring = null
	t0 = Time.get_ticks_usec()
	for k in 200:
		drift.step(0.1)
	print("drift.step without mooring %.0f us" % ((Time.get_ticks_usec() - t0) / 200.0))
	drift.mooring = keep
	t0 = Time.get_ticks_usec()
	for k in 200:
		drift.step(0.1)
	print("drift.step with mooring %.0f us" % ((Time.get_ticks_usec() - t0) / 200.0))
	var kinds := {}
	for e in drift.events:
		kinds[e[0]] = kinds.get(e[0], 0) + 1
	print("events ", kinds, " rafts ", drift.rafts.size(), " lines ", drift.lines.size())
	drift.events.clear()
	t0 = Time.get_ticks_usec()
	for k in 200:
		drift._meetings()
	print("_meetings %.0f us" % ((Time.get_ticks_usec() - t0) / 200.0))
	t0 = Time.get_ticks_usec()
	for k in 200:
		drift._keep_apart()
	print("_keep_apart %.0f us" % ((Time.get_ticks_usec() - t0) / 200.0))
	t0 = Time.get_ticks_usec()
	for k in 200:
		FleaCalendar.week_plan(5)
	print("week_plan cached %.0f us" % ((Time.get_ticks_usec() - t0) / 200.0))
	quit(0)
