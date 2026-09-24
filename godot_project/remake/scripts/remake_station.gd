extends Node3D
class_name RemakeStation

## The remake's station: an O'Neill cylinder (StationGeo -- 500 m radius, 3 km long, central shaft
## 50 m) holding only the map's world (tools/map_preview.py -> remake/user_reference/map_current.png):
##   * the shell -- the two end walls (annuli from the shaft out past the floor) and the central
##     shaft, which the day/night sky system colours (DaySkySystem, surface 1 = the "ceiling");
##   * the map's terrain (MapTerrain / MapTerrainMesh, streamed round the player), its river and
##     lake (MapWater), the end-cap cliffs (CliffWalls);
##   * the map's structures (RemakeWorld: SETTLEMENTS, or everything), with full detail streamed
##     near the player (RemakeDetailStreamer).
## Nothing of the earlier procedural layout.  The player (StationPlayer, radial spin gravity via
## SpaceStation.gravity_at) finds this node through the "space_station" group.

const STATION_PLAYER_SCENE := preload("res://scenes/StationPlayer.tscn")
const WALL_TILE := 6.0

static var SETTLEMENTS: Array = []            # [] = the whole map
static var SPAWN_S := 395.0                   # Harrow Falls, Main Street
static var SPAWN_X := 283.0

var player: StationPlayer
var sun: DirectionalLight3D
var environment: Environment
var sky_system: DaySkySystem
var shell_mesh: MeshInstance3D
var terrain: MapTerrainMesh
var world: Node3D
var streamer: RemakeDetailStreamer
var far_side: RemakeFarSide


func _ready() -> void:
	add_to_group("space_station")
	_setup_environment()
	_build_shell()
	_spawn_player()
	var floor_mat := StandardMaterial3D.new()
	floor_mat.albedo_texture = _neutral_detail("res://assets/textures/grass_tinted.png")
	floor_mat.vertex_color_use_as_albedo = true          # MapTerrainMesh colours the ground by land cover
	floor_mat.vertex_color_is_srgb = true
	terrain = MapTerrainMesh.new()
	terrain.name = "Terrain"
	add_child(terrain)
	far_side = RemakeFarSide.new()
	far_side.name = "FarSide"
	add_child(far_side)
	far_side.setup(player, terrain, floor_mat.albedo_texture)
	terrain.setup(player, floor_mat)
	MapWater.build(self)
	MapWater.build_small(self)
	var trees := MapTrees.new()
	trees.name = "Trees"
	add_child(trees)
	trees.setup()
	var roads := MapRoads.new()
	roads.name = "Roads"
	add_child(roads)
	roads.setup()
	var cliffs := CliffWalls.new()
	cliffs.name = "CliffWalls"
	add_child(cliffs)
	cliffs.setup(player)
	for c in get_children():
		if c.name.begins_with("map_water_") or c.name.begins_with("map_small_water_"):
			far_side.add_node(c)
	sky_system = DaySkySystem.new()
	sky_system.name = "DaySkySystem"
	add_child(sky_system)
	sky_system.setup(self, sun, shell_mesh, StationGeo.R - StationGeo.SHAFT_R, WALL_TILE, environment)
	world = Node3D.new()
	world.name = "World"
	add_child(world)
	streamer = RemakeDetailStreamer.new()
	streamer.name = "DetailStreamer"
	add_child(streamer)
	_place_structures()


static func _neutral_detail(path: String) -> ImageTexture:
	## A texture's grain without its colour: greyscale, scaled so its mean is 1 -- the vertex colour
	## is then the colour you see.
	var img: Image = (load(path) as Texture2D).get_image()
	img.decompress()
	img.convert(Image.FORMAT_RGB8)
	var total := 0.0
	var n := 0
	for y in range(0, img.get_height(), 4):
		for x in range(0, img.get_width(), 4):
			total += img.get_pixel(x, y).get_luminance()
			n += 1
	var mean := maxf(0.05, total / n)
	for y in img.get_height():
		for x in img.get_width():
			var l := clampf(img.get_pixel(x, y).get_luminance() / mean, 0.0, 1.0)
			img.set_pixel(x, y, Color(l, l, l))
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


func _place_structures() -> void:
	## Not awaited: the structures fill in a building per frame while the game runs.
	var info: Dictionary = await RemakeWorld.build(world, SETTLEMENTS)
	streamer.setup(player, info.records)
	# the far side draws them flat (RemakeFarSide): every merged district mesh and ordinary
	# building, the trees and roads -- not the landmarks
	var landmarks := {}
	for r in info.records:
		if r.landmark:
			landmarks[r.root] = true
	far_side.add_children_of(world, func(n: Node) -> bool: return landmarks.has(n))
	while get_node("Trees").is_processing() or get_node("Roads").is_processing():
		await get_tree().process_frame
	far_side.add_children_of(get_node("Trees"))
	far_side.add_children_of(get_node("Roads"))
	info.erase("records")
	print("RemakeStation: placed ", info)


func _setup_environment() -> void:
	environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.01, 0.01, 0.02)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.5, 0.5, 0.55)
	environment.ambient_light_energy = 1.2
	var world_env := WorldEnvironment.new()
	world_env.environment = environment
	add_child(world_env)
	sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-35, 40, 0)
	sun.light_energy = 1.3
	sun.light_color = Color(1.0, 0.98, 0.92)
	sun.shadow_enabled = true
	add_child(sun)


func _build_shell() -> void:
	## End walls (surface 0) and the central shaft (surface 1, the sky system's "ceiling").
	var n := 256
	var walls := SurfaceTool.new()
	walls.begin(Mesh.PRIMITIVE_TRIANGLES)
	var r_in := StationGeo.SHAFT_R
	var r_out := StationGeo.R + 30.0                   # past the floor, under the terrain's lowest point
	for end in [-1.0, 1.0]:
		var x: float = end * StationGeo.HALF_LEN
		for i in n:
			var a0 := TAU * i / n
			var a1 := TAU * (i + 1) / n
			var q := [Vector3(x, r_in * cos(a0), r_in * sin(a0)), Vector3(x, r_out * cos(a0), r_out * sin(a0)),
				Vector3(x, r_out * cos(a1), r_out * sin(a1)), Vector3(x, r_in * cos(a1), r_in * sin(a1))]
			var order := [0, 1, 2, 0, 2, 3] if end > 0.0 else [0, 2, 1, 0, 3, 2]
			for k in order:
				var v: Vector3 = q[k]
				walls.set_normal(Vector3(-end, 0, 0))
				walls.set_uv(Vector2(v.y / WALL_TILE, v.z / WALL_TILE))
				walls.add_vertex(v)
	var wall_mat := StandardMaterial3D.new()
	wall_mat.albedo_texture = load("res://assets/textures/station_metal_wall.png")
	walls.set_material(wall_mat)
	var shaft := SurfaceTool.new()
	shaft.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in n:
		var a0 := TAU * i / n
		var a1 := TAU * (i + 1) / n
		var q := [Vector3(-StationGeo.HALF_LEN, r_in * cos(a0), r_in * sin(a0)), Vector3(StationGeo.HALF_LEN, r_in * cos(a0), r_in * sin(a0)),
			Vector3(StationGeo.HALF_LEN, r_in * cos(a1), r_in * sin(a1)), Vector3(-StationGeo.HALF_LEN, r_in * cos(a1), r_in * sin(a1))]
		for k in [0, 2, 1, 0, 3, 2]:
			var v: Vector3 = q[k]
			shaft.set_normal(Vector3(0, v.y, v.z).normalized())       # facing out, toward the floor
			shaft.set_uv(Vector2(v.x / WALL_TILE, TAU * r_in * (i + (1 if k in [1, 2] else 0)) / n / WALL_TILE))
			shaft.add_vertex(v)
	shaft.set_material(StandardMaterial3D.new())
	var mesh := ArrayMesh.new()
	walls.commit(mesh)
	shaft.commit(mesh)
	shell_mesh = MeshInstance3D.new()
	shell_mesh.name = "Shell"
	shell_mesh.mesh = mesh
	var body := StaticBody3D.new()
	body.name = "RingBody"                # the HUD compass reads the station frame from this node
	add_child(body)
	body.add_child(shell_mesh)
	var cs := CollisionShape3D.new()
	var shape := mesh.create_trimesh_shape()
	shape.backface_collision = true
	cs.shape = shape
	body.add_child(cs)


func _spawn_player() -> void:
	## On the ground at (SPAWN_S, SPAWN_X), facing along the ring.  The transform is set before
	## add_child(): StationPlayer._ready() records it as the respawn point.
	var h := MapTerrain.elevation(SPAWN_S, SPAWN_X)
	var up := StationGeo.up(SPAWN_S)
	var feet := StationGeo.point(SPAWN_S, SPAWN_X, h + 0.05)
	player = STATION_PLAYER_SCENE.instantiate() as StationPlayer
	player.global_transform = Transform3D(Basis.looking_at(StationGeo.forward(SPAWN_S), up), feet + up * 1.43)
	add_child(player)
	ScreenOutline.attach_to_camera(player.camera)
