extends CharacterBody3D
class_name NPCBase

# General-purpose NPC: wanders when idle, reacts to being attacked (or to
# spotting a hostile faction) by either fighting back or fleeing depending
# on its faction's behavior (see data/factions.json), and can path anywhere
# the baked NavigationRegion3D covers. Dialog/quest-giving are opt-in hooks
# for named NPCs -- background NPCs just leave them at their defaults.

enum State { IDLE, PATROL, COMBAT, FLEE, TALKING }

@export var faction_id: String = "civilian"
@export var move_speed: float = 3.0
@export var wander_radius: float = 12.0
@export var awareness_radius: float = 14.0
@export var attack_range: float = 1.8
@export var attack_damage: float = 8.0
@export var attack_cooldown: float = 1.2
@export var run_speed_multiplier: float = 1.7

# Opt-in dialog/quest hooks for named NPCs. Left empty, this NPC just isn't
# talkable -- Player interaction code should check has_dialog() first.
@export var dialog_id: String = ""
@export var offered_quest_ids: Array[String] = []

# Opt-in loot. Empty means "no corpse" -- on death this NPC just does the
# generic shrink-and-vanish. Non-empty means it becomes a persistent,
# lootable corpse instead (see has_loot()/loot()).
@export var loot_table: Dictionary = {}

var is_dead := false
var looted := false

var state: State = State.IDLE
var target: Node3D = null
var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

var _home_position: Vector3
var _wait_timer: float = 0.0
var _attack_cooldown_left: float = 0.0
var _scan_timer: float = 0.0
var _repath_timer: float = 0.0

@onready var nav_agent: NavigationAgent3D = $NavAgent
@onready var health: Health = $Health
@onready var collision_shape: CollisionShape3D = $CollisionShape3D

# Generic sprite-driving: any NPC scene that has a child named "Sprite"
# implementing play()/stop()/is_playing()/current_animation (see
# DirectionalSprite.gd) gets automatic Walk/Run/Idle switching for free,
# with Attack/Death played from the hooks below. Vanilla NPCBase scenes
# with no such child just skip all of this -- `sprite` stays null.
var sprite: Node = null
var _current_loop := ""

# Off-screen culling: wander/combat/nav AI and sprite frame-switching are
# real per-NPC CPU cost every physics frame, paid whether or not the NPC
# is actually in view. A VisibleOnScreenNotifier3D (Godot's own screen-
# frustum check, not a hand-rolled one) toggles both off while off-screen
# and back on when the camera finds the NPC again -- invisible to the
# player by construction, since nothing off-screen can be seen changing.
var _screen_notifier: VisibleOnScreenNotifier3D

func get_faction() -> String:
	return faction_id

## Player's E key calls this on whatever it's aimed at (see Player.gd's
## _try_interact()) -- loot a corpse if there is one, otherwise talk if this
## NPC has dialog. Doors/switches/pickups should implement their own
## interact(by) the same way; nothing else needs to know about them.
func interact(by: Node) -> void:
	if has_loot():
		if loot(by):
			print("Looted: ", loot_table)
		return
	if not has_dialog():
		return
	var tree := get_dialog_tree()
	if not tree.is_empty():
		DialogBox.start(self, tree)

func has_dialog() -> bool:
	return dialog_id != ""

## Override in named NPCs to return a dialog tree (see DialogBox.gd for the
## expected format). Can branch on quest/world state -- it's re-fetched
## every time the player interacts, not cached.
func get_dialog_tree() -> Dictionary:
	return {}

## Real render distance for the sprite itself, on top of (not instead of)
## the screen-frustum-based AI/animation pause below -- a background NPC
## far enough away to be a few pixels tall doesn't need to be drawn at
## all, comic-book outline or not. Same Godot visibility_range mechanism
## DistanceCulling.gd uses for world scenery, just applied here directly
## since NPCs live outside that script's own `neighborhood` subtree.
const SPRITE_RENDER_RANGE := 65.0
const SPRITE_RENDER_FADE_MARGIN := 8.0

func _ready() -> void:
	add_to_group("combatants")
	_home_position = global_position
	health.died.connect(_on_died)
	nav_agent.path_desired_distance = 0.5
	nav_agent.target_desired_distance = 0.6
	_pick_new_wander_target()
	sprite = find_child("Sprite", true, false)
	if sprite is GeometryInstance3D:
		sprite.visibility_range_end = SPRITE_RENDER_RANGE
		sprite.visibility_range_end_margin = SPRITE_RENDER_FADE_MARGIN
		# DISABLED, not SELF -- see DistanceCulling.gd's own comment on
		# _apply(): Godot's "smooth" fade is actually a per-pixel dither,
		# which fed false edges into the screen-space outline pass right
		# at this fade distance. Same fix, same reason, here too.
		sprite.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	_setup_visibility_culling()

## Sized generously enough to cover the tallest NPC sprite (~1.7m, the
## officer/Lloyd characters) with margin -- an oversized box for the
## smaller bedbugs (~0.85m) just means they get culled a touch more
## conservatively, which is harmless.
func _setup_visibility_culling() -> void:
	_screen_notifier = VisibleOnScreenNotifier3D.new()
	_screen_notifier.aabb = AABB(Vector3(-0.7, -0.2, -0.7), Vector3(1.4, 2.4, 1.4))
	add_child(_screen_notifier)
	_screen_notifier.screen_entered.connect(_on_screen_entered)
	_screen_notifier.screen_exited.connect(_on_screen_exited)
	# Deliberately no initial is_on_screen() check here -- the notifier
	# needs a frame in the tree before that's accurate, and a freshly
	# spawned NPC (e.g. bedbugs, spawned right next to the player when a
	# quest starts) must default to fully active rather than risk being
	# wrongly paused for a frame. Every NPC just starts active and only
	# pauses once Godot's own visibility check actually fires exited.

func _on_screen_entered() -> void:
	if is_dead:
		return
	set_physics_process(true)
	if sprite:
		sprite.set_process(true)

func _on_screen_exited() -> void:
	if is_dead:
		return
	set_physics_process(false)
	if sprite:
		sprite.set_process(false)

func on_attacked(attacker: Node3D) -> void:
	if state == State.TALKING or not health.is_alive():
		return
	target = attacker
	match FactionManager.get_behavior(faction_id):
		"flee":
			state = State.FLEE
		"aggressive":
			state = State.COMBAT
		_:
			pass

func _physics_process(delta: float) -> void:
	if not health.is_alive():
		return

	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		velocity.y = 0.0

	_attack_cooldown_left = max(0.0, _attack_cooldown_left - delta)

	if state != State.TALKING:
		_scan_timer -= delta
		if _scan_timer <= 0.0:
			_scan_timer = 0.5
			_scan_for_threats()

	match state:
		State.IDLE, State.PATROL:
			_process_wander(delta)
		State.COMBAT:
			_process_combat(delta)
		State.FLEE:
			_process_flee(delta)
		State.TALKING:
			velocity.x = 0.0
			velocity.z = 0.0

	_try_step_up(Vector3(velocity.x, 0, velocity.z))
	move_and_slide()
	_update_sprite_animation()

# Same raycast-based curb-step as Player.gd's _try_step_up() (kept as a
# separate copy rather than a shared base class -- Player and NPCBase
# don't share one -- but identical logic): probe forward at foot height
# for an obstacle, confirm it's short enough to clear at head-STEP_HEIGHT,
# then snap up to the exact surface height found just past it. Without
# this, NPCs could path fine on the nav mesh right up to a curb and then
# just push into it forever, never actually crossing -- the player has
# had this since curbs were first added, but nothing gave NPCs the same
# treatment until now.
#
# REAL BUG, found live (same root cause as Player.gd's own copy -- see its
# comment for the full write-up): every probe ray was built from
# `global_position` directly, which is EYE height on this CharacterBody3D,
# not ground level (the CollisionShape3D carries a large negative Y offset
# so feet land at the floor). All 3 rays fired ~0.9-1.9m above the actual
# ground/curb/stair surface -- comfortably above anything they were meant
# to detect -- so this never once triggered in practice; NPCs pathing
# across a curb or up a stairwell just pushed into it and stalled, same as
# the player. Fixed the same way: derive real foot Y from the collision
# capsule's own bottom instead of assuming the root origin is ground level.
const STEP_HEIGHT := 0.3

func _foot_y() -> float:
	var capsule := collision_shape.shape as CapsuleShape3D
	return collision_shape.global_position.y - capsule.height / 2.0

func _try_step_up(move_dir: Vector3) -> void:
	if move_dir.length_squared() < 0.0001 or not is_on_floor():
		return
	var space_state := get_world_3d().direct_space_state
	var probe := move_dir.normalized() * 0.4
	var foot_y := _foot_y()
	var eye_to_foot := global_position.y - foot_y
	var origin := Vector3(global_position.x, foot_y, global_position.z)

	var foot_from := origin + Vector3(0, 0.1, 0)
	var foot_query := PhysicsRayQueryParameters3D.create(foot_from, foot_from + probe)
	foot_query.exclude = [self]
	if not space_state.intersect_ray(foot_query):
		return  # nothing in the way -- no step needed

	var head_from := origin + Vector3(0, STEP_HEIGHT + 0.02, 0)
	var head_query := PhysicsRayQueryParameters3D.create(head_from, head_from + probe)
	head_query.exclude = [self]
	if space_state.intersect_ray(head_query):
		return  # still blocked above step height -- a real wall, not a curb

	var down_from := origin + probe + Vector3(0, STEP_HEIGHT + 0.05, 0)
	var down_query := PhysicsRayQueryParameters3D.create(down_from, down_from + Vector3(0, -(STEP_HEIGHT + 0.15), 0))
	down_query.exclude = [self]
	var down_hit := space_state.intersect_ray(down_query)
	if down_hit:
		var new_foot_y: float = down_hit["position"].y
		if new_foot_y > foot_y:
			global_position.y = new_foot_y + eye_to_foot

func _update_sprite_animation() -> void:
	if sprite == null:
		return
	if sprite.current_animation == "Attack" and sprite.is_playing():
		return  # let the attack animation finish before switching back
	var speed := Vector2(velocity.x, velocity.z).length()
	var desired := ""
	if speed > move_speed * 1.2:
		desired = "Run"
	elif speed > 0.15:
		desired = "Walk"
	else:
		desired = "Idle"
	if _current_loop != desired:
		sprite.play(desired)
		_current_loop = desired

func _scan_for_threats() -> void:
	if state == State.COMBAT or state == State.FLEE:
		if target != null and is_instance_valid(target) and _has_health(target) and _get_health(target).is_alive():
			return  # already reacting to something valid
	for node in get_tree().get_nodes_in_group("combatants") + get_tree().get_nodes_in_group("player"):
		if node == self:
			continue
		if not _has_health(node) or not _get_health(node).is_alive():
			continue
		var other_faction: String = node.get_faction() if node.has_method("get_faction") else ""
		if other_faction == "" or not FactionManager.is_hostile(faction_id, other_faction):
			continue
		if global_position.distance_to(node.global_position) <= awareness_radius:
			on_attacked(node)
			return

func _has_health(node: Node) -> bool:
	return node.get_node_or_null("Health") != null

func _get_health(node: Node) -> Health:
	return node.get_node_or_null("Health")

func _process_wander(delta: float) -> void:
	if nav_agent.is_navigation_finished():
		_wait_timer -= delta
		velocity.x = 0.0
		velocity.z = 0.0
		if _wait_timer <= 0.0:
			_pick_new_wander_target()
		return
	_move_toward_nav_target(move_speed)

func _pick_new_wander_target() -> void:
	var angle := randf() * TAU
	var dist := randf() * wander_radius
	var candidate := _home_position + Vector3(cos(angle) * dist, 0.0, sin(angle) * dist)
	nav_agent.target_position = candidate
	_wait_timer = randf_range(2.0, 6.0)
	state = State.PATROL

## Repathing (nav_agent.target_position = ...) triggers a real pathfinding
## query on the NavigationServer -- setting it every physics frame while
## chasing a moving target means every combat/flee NPC recomputes its whole
## path 60x/second. Fine for one or two NPCs, but a 20-bedbug swarm all
## chasing the same moving player was the single biggest cost behind the
## spawn-time slowdown (measured: 1 fps). Re-pathing 5x/second instead
## (REPATH_INTERVAL) is imperceptible for a chase and roughly 12x cheaper.
const REPATH_INTERVAL := 0.2

func _process_combat(delta: float) -> void:
	if target == null or not is_instance_valid(target) or not _get_health(target).is_alive():
		state = State.IDLE
		target = null
		return
	var dist := global_position.distance_to(target.global_position)
	if dist > attack_range:
		_repath_timer -= delta
		if _repath_timer <= 0.0:
			_repath_timer = REPATH_INTERVAL
			nav_agent.target_position = target.global_position
		_move_toward_nav_target(move_speed * run_speed_multiplier)
	else:
		velocity.x = 0.0
		velocity.z = 0.0
		look_at(Vector3(target.global_position.x, global_position.y, target.global_position.z), Vector3.UP)
		if _attack_cooldown_left <= 0.0:
			_attack_cooldown_left = attack_cooldown
			CombatSystem.apply_damage(self, target, attack_damage)
			_on_attack_performed()

func _process_flee(delta: float) -> void:
	if target == null or not is_instance_valid(target):
		state = State.IDLE
		return
	var away := (global_position - target.global_position)
	if away.length() > awareness_radius * 1.5:
		state = State.IDLE
		target = null
		return
	away = away.normalized()
	_repath_timer -= delta
	if _repath_timer <= 0.0:
		_repath_timer = REPATH_INTERVAL
		nav_agent.target_position = global_position + away * 6.0
	_move_toward_nav_target(move_speed * run_speed_multiplier)

func _move_toward_nav_target(speed: float) -> void:
	var next_pos := nav_agent.get_next_path_position()
	var dir := (next_pos - global_position)
	dir.y = 0.0
	if dir.length() < 0.05:
		velocity.x = 0.0
		velocity.z = 0.0
		return
	dir = dir.normalized()
	velocity.x = dir.x * speed
	velocity.z = dir.z * speed
	if dir.length_squared() > 0.001:
		var target_angle := atan2(dir.x, dir.z)
		rotation.y = lerp_angle(rotation.y, target_angle, 0.15)

func begin_dialog() -> void:
	state = State.TALKING
	velocity = Vector3.ZERO

func end_dialog() -> void:
	state = State.IDLE

## Called once, right as the NPC dies. Default drives the generic `sprite`
## (see _update_sprite_animation()) if this NPC has one; override in
## subclasses for anything fancier.
func _play_death_visual() -> void:
	if sprite:
		sprite.play("Death")

## Called each time attack_damage is applied. Default drives the generic
## `sprite`; override in subclasses for anything fancier.
func _on_attack_performed() -> void:
	if sprite:
		sprite.play("Attack")
		_current_loop = ""

func has_loot() -> bool:
	return is_dead and not looted and not loot_table.is_empty()

func loot(_by: Node) -> bool:
	if not has_loot():
		return false
	for item_id in loot_table.keys():
		Inventory.add(item_id, int(loot_table[item_id]))
	looted = true
	return true

func _on_died(_attacker: Node) -> void:
	is_dead = true
	set_physics_process(false)
	velocity = Vector3.ZERO
	_play_death_visual()
	if loot_table.is_empty():
		# No loot defined -- collapse and vanish rather than leaving a
		# permanent, un-lootable corpse cluttering the world.
		collision_layer = 0
		collision_mask = 0
		if sprite and sprite.is_playing():
			# A real Death clip just started (see _play_death_visual) --
			# let it actually finish playing before the corpse disappears.
			# The old code always squashed-and-vanished after a flat 0.4s,
			# which cut every Death animation off after a fraction of a
			# second (only ever unnoticed before because Lloyd/Marty had
			# no Death frames at all until now, and bedbugs always take
			# the loot-table branch below instead). NPCs with no real
			# Death clip fall straight through to the old squash tween,
			# since sprite.is_playing() is false immediately (play() is a
			# no-op for an animation name with no frames).
			while is_instance_valid(sprite) and sprite.is_playing():
				await get_tree().process_frame
			if is_instance_valid(self):
				queue_free()
		else:
			var tw := create_tween()
			tw.tween_property(self, "scale", Vector3(1, 0.05, 1), 0.4)
			tw.tween_callback(queue_free)
	# Otherwise: stays in the world, collision intact, so Player's
	# interact raycast can still find it and call loot() on it.
