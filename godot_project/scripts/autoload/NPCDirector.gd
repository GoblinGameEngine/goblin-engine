extends Node

# Spawns and tracks NPCs -- both "background" ones that just populate the
# world (wander, react to faction hostility) and quest-specific batches
# (e.g. the 20 bedbugs for "Exterminator"), which get tagged into a group
# so quest/compass code can find the survivors.

const NPC_SCENE := preload("res://scenes/npc/NPCBase.tscn")
const BEDBUG_SCENE := preload("res://scenes/npc/Bedbug.tscn")

var spawned: Array[Node] = []

func populate(parent: Node, area_center: Vector3, area_radius: float, count: int, faction: String = "civilian") -> void:
	spawn_group(parent, NPC_SCENE, "", faction, area_center, area_radius, count)

## Spawns exactly one NPC at each given point (e.g. one per house's front
## yard, per map_layout.json) instead of scattering randomly in a disk --
## used so "every house is inhabited" is guaranteed, not probabilistic.
func populate_at_points(parent: Node, points: Array, faction: String = "civilian") -> void:
	for p in points:
		var npc := NPC_SCENE.instantiate()
		npc.faction_id = faction
		npc.position = p
		if "wander_radius" in npc:
			npc.wander_radius = 8.0
		parent.add_child(npc)
		spawned.append(npc)

## Spawns `count` copies of `scene` scattered in a circle, tags each into
## `group` (if non-empty) so it can be found later (e.g. quest kill-tracking
## or a compass showing red arrows at survivors), and sets faction_id.
func spawn_group(parent: Node, scene: PackedScene, group: String, faction: String, area_center: Vector3, area_radius: float, count: int) -> Array:
	var batch: Array = []
	for i in range(count):
		var npc := scene.instantiate()
		npc.faction_id = faction
		var angle := randf() * TAU
		var dist := randf() * area_radius
		npc.position = area_center + Vector3(cos(angle) * dist, 0.2, sin(angle) * dist)
		if "wander_radius" in npc:
			npc.wander_radius = min(area_radius, 10.0)
		parent.add_child(npc)
		if group != "":
			npc.add_to_group(group)
		spawned.append(npc)
		batch.append(npc)
	return batch

func spawn_bedbugs(parent: Node, area_center: Vector3, area_radius: float, count: int, group: String = "quest_exterminator_targets") -> Array:
	return spawn_group(parent, BEDBUG_SCENE, group, "hostile", area_center, area_radius, count)

func clear() -> void:
	for npc in spawned:
		if is_instance_valid(npc):
			npc.queue_free()
	spawned.clear()

func count_alive() -> int:
	return spawned.filter(func(n): return is_instance_valid(n)).size()

func count_alive_in_group(group: String) -> int:
	var tree := Engine.get_main_loop() as SceneTree
	var nodes: Array = tree.get_nodes_in_group(group) if tree else []
	return nodes.filter(func(n): return is_instance_valid(n) and n.has_method("get_faction")).size()
