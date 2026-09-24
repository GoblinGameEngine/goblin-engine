extends Node3D

## Bakes the far-side image: the finished world seen straight down, unshaded (its surface colours
## only -- the station lights it at runtime), at 1 m / px over the whole floor:
##   remake/farside.png, (TILES_S x TILE) x (TILES_X x TILE) px, column = s, row = x + HALF_EXTENT.
## Builds the world like RemakeStation (terrain, water, roads, trees, structures), then renders
## TILE m x TILE m tiles through an orthographic camera 250 m up, moving the terrain's streaming
## probe to each tile first so its ground is at full detail.  Run:
##   godot4 --path . res://remake/scenes/FarsideBake.tscn          (a window; takes a few minutes)

const TILE := 128
const TILES_S := 25                  # 3,200 m >= the 3,141.6 m circumference (the rest wraps)
const TILES_X := 24                  # 3,072 m >= the 3,000 m length
const HALF_EXTENT := 1536.0
const CAM_H := 250.0
const OUT := "res://remake/farside.png"

var probe: Node3D
var terrain: MapTerrainMesh
var world: Node3D


func _ready() -> void:
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.3, 0.3, 0.3)
	add_child(env)
	probe = Node3D.new()
	add_child(probe)
	probe.global_position = StationGeo.point(0.0, 0.0, 0.0)
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_texture = RemakeStation._neutral_detail("res://assets/textures/grass_tinted.png")
	floor_mat.vertex_color_use_as_albedo = true
	floor_mat.vertex_color_is_srgb = true
	terrain = MapTerrainMesh.new()
	add_child(terrain)
	terrain.setup(probe, floor_mat)
	MapWater.build(self)
	MapWater.build_small(self)
	var roads := MapRoads.new()
	add_child(roads)
	roads.setup()
	var trees := MapTrees.new()
	add_child(trees)
	trees.setup()
	world = Node3D.new()
	add_child(world)
	_bake(roads, trees)


func _bake(roads: MapRoads, trees: MapTrees) -> void:
	var tree := get_tree()
	await RemakeWorld.build(world, [])
	while roads.is_processing() or trees.is_processing():
		await tree.process_frame
	var vp := SubViewport.new()
	vp.size = Vector2i(TILE, TILE)
	vp.debug_draw = Viewport.DEBUG_DRAW_UNSHADED
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = TILE
	cam.near = 1.0
	cam.far = CAM_H + 80.0
	vp.add_child(cam)
	var img := Image.create(TILES_S * TILE, TILES_X * TILE, false, Image.FORMAT_RGB8)
	var t0 := Time.get_ticks_msec()
	for ts in TILES_S:
		for tx in TILES_X:
			var s := (ts + 0.5) * TILE
			var x := -HALF_EXTENT + (tx + 0.5) * TILE
			# the ground under the tile at full detail first
			probe.global_position = StationGeo.point(s, x, 0.0)
			terrain._update()
			while terrain.busy():
				await tree.process_frame
			# straight down: screen right = +s, screen up = -x, looking along -up
			var up := StationGeo.up(s)
			var b := Basis(StationGeo.forward(s), -Vector3.RIGHT, up)
			cam.global_transform = Transform3D(b, StationGeo.point(s, x, CAM_H))
			for f in 3:
				await RenderingServer.frame_post_draw
			var tile := vp.get_texture().get_image()
			tile.convert(Image.FORMAT_RGB8)
			img.blit_rect(tile, Rect2i(0, 0, TILE, TILE), Vector2i(ts * TILE, tx * TILE))
		print("farside bake: column %d/%d  %.0f s" % [ts + 1, TILES_S, (Time.get_ticks_msec() - t0) / 1000.0])
	img.save_png(ProjectSettings.globalize_path(OUT))
	print("FARSIDE_BAKED ", OUT, " ", img.get_size())
	get_tree().quit()
