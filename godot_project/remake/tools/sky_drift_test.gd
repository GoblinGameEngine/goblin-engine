extends SceneTree
## Headless check of SkyDrift: godot4 --headless --path . --script res://remake/tools/sky_drift_test.gd
## Stub islands (rectangles, bridges every 20 m), a few in-game days; invariants checked as it runs.

const Drift = preload("res://remake/scripts/sky/sky_drift.gd")


func _init() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var defs := []
	for i in 100:
		var blocks := rng.randi_range(1, 10)
		var w := sqrt(blocks * 8000.0) * rng.randf_range(0.8, 1.25)
		var d := blocks * 8000.0 / w
		var br := []
		for side in ["N", "S", "E", "W"]:
			var face := w if side in ["N", "S"] else d
			var n := clampi(int(face / 90.0), 1, 3)
			for k in n:
				br.append({"side": side, "along": (k - (n - 1) * 0.5) * 40.0})
		defs.append({"id": "SKY-%03d" % (i + 1), "faces": {"N": d * 0.5, "S": d * 0.5, "E": w * 0.5, "W": w * 0.5}, "bridges": br})
	print("defs ready")
	var sd = Drift.new()
	var t0 := Time.get_ticks_msec()
	sd.setup(defs)
	print("setup %d ms" % (Time.get_ticks_msec() - t0))
	sd.warm_up(float(OS.get_environment("WARM") if OS.get_environment("WARM") != "" else "72"))
	print("warm-up 72 h: %d ms  %s" % [Time.get_ticks_msec() - t0, sd.summary()])
	var lashes := 0
	var casts := 0
	var fires := 0
	var worst := 0
	var bad := {}
	for k in int(OS.get_environment("DAYS") if OS.get_environment("DAYS") != "" else "6") * 24 * 6:         # 6 days at 10 min steps... (dt = 20 s)
		for j in 6:
			sd.step(20.0)
		for ev in sd.events:
			match ev[0]:
				"lash": lashes += 1
				"cast_off": casts += 1
				"fire": fires += 1
		sd.events.clear()
		for r in sd.rafts.values():
			worst = maxi(worst, r.members.size())
			assert(r.members.size() <= 10)
			# no two islands of a raft overlap
			for a in r.members:
				for b in r.members:
					if a < b and sd._box(a).grow(12.0).intersects(sd._box(b).grow(12.0)):
						if not bad.has(Vector2i(a, b)):
							bad[Vector2i(a, b)] = true
							print("overlap %d %d in raft %d: %s %s edges %s" % [a, b, r.id, sd._box(a), sd._box(b), r.edges])
			for e in r.edges:
				assert(sd.hours - e.born <= 72.0 + 0.2)
		if k % 144 == 0:
			print(sd.summary())
	print("6 days: fires %d lashes %d cast-offs %d biggest raft %d" % [fires, lashes, casts, worst])
	quit()
