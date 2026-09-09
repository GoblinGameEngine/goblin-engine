extends NPCBase
class_name QuestGiverGeneric

# Fully data-driven quest giver: dialogue trees, what each dialogue choice
# actually DOES, and where this NPC stands through the day (routine +
# quest-conditional schedule) are all read from data/quest_givers.json
# (keyed by npc_id) instead of being hand-coded per NPC like the old
# QuestGiver.gd. Built so the in-game Quest Editor (F3, QuestEditorUI.gd)
# can author all of this without anyone touching a script -- see that
# file's header for the on-disk schema.

const DATA_PATH := "res://data/quest_givers.json"

# Loaded once and shared by every instance -- there's no per-instance
# state in the file itself (each NPC just looks up its own npc_id key),
# so re-reading it per NPC would be pure waste on a map with several
# quest givers.
static var _cache: Dictionary = {}
static var _cache_loaded := false

@export var npc_id: String = ""

var _data: Dictionary = {}

func _ready() -> void:
	super._ready()
	_load_cache()
	_data = _cache.get(npc_id, {})
	if _data.is_empty():
		push_warning("QuestGiverGeneric: no data/quest_givers.json entry for npc_id '%s'" % npc_id)
	dialog_id = npc_id
	DialogBox.dialog_action.connect(_on_dialog_action)

static func _load_cache() -> void:
	if _cache_loaded:
		return
	_cache_loaded = true
	if not FileAccess.file_exists(DATA_PATH):
		return
	var f := FileAccess.open(DATA_PATH, FileAccess.READ)
	var parsed = JSON.parse_string(f.get_as_text())
	if typeof(parsed) == TYPE_DICTIONARY:
		_cache = parsed

## Called by the Quest Editor right after it writes quest_givers.json so a
## still-running game (playtesting through the same F2/F3 session) picks
## up edits without a restart.
static func reload_cache() -> void:
	_cache_loaded = false
	_cache.clear()
	_load_cache()

# ---------------------------------------------------------------
# Dialogue
# ---------------------------------------------------------------

func get_dialog_tree() -> Dictionary:
	for state_entry in _data.get("dialogue_states", []):
		if _condition_matches(state_entry.get("condition")):
			return state_entry.get("tree", {})
	return {}

## condition == null always matches -- used as a catch-all fallback entry.
## Anything else is {"quest_id": "...", "state": "not_started"|"active"|
## "completed"|"turned_in"}, checked against QuestManager.get_state().
func _condition_matches(cond) -> bool:
	if cond == null:
		return true
	return QuestManager.get_state(cond["quest_id"]) == cond["state"]

func _on_dialog_action(action, npc: Node) -> void:
	if npc != self or typeof(action) != TYPE_ARRAY:
		return
	for a in action:
		_execute_action(a)

## Generic action vocabulary the Quest Editor's dialogue choice UI builds
## from. Kept intentionally small and composable (a choice fires a LIST of
## these) rather than trying to cover every possible scripted moment --
## "custom" is the escape hatch for the rest (see _run_custom_action()).
func _execute_action(a: Dictionary) -> void:
	match a.get("type", ""):
		"start_quest":
			QuestManager.start_quest(a["quest_id"])
		"mark_turned_in":
			QuestManager.mark_turned_in(a["quest_id"])
		"give_item":
			Inventory.add(a["item_id"], int(a.get("count", 1)))
		"spawn_npcs":
			_spawn_npcs(a)
		"set_flag":
			WorldFlags.set_flag(a["flag"], a.get("value", true))
		"custom":
			_run_custom_action(a.get("id", ""))
		_:
			push_warning("QuestGiverGeneric: unknown action type '%s'" % a.get("type", ""))

func _spawn_npcs(a: Dictionary) -> void:
	var scene_path := "res://scenes/npc/%s.tscn" % a.get("kind", "Bedbug")
	if not ResourceLoader.exists(scene_path):
		push_warning("QuestGiverGeneric: spawn_npcs -- no scene at %s" % scene_path)
		return
	var scene: PackedScene = load(scene_path)
	NPCDirector.spawn_group(get_parent(), scene, a.get("group", ""), a.get("faction", "hostile"),
		global_position, float(a.get("radius", 20.0)), int(a.get("count", 1)))

## Escape hatch for one-off scripted moments too bespoke to deserve a
## generic action type of their own -- there's exactly one today (the
## police blockade driving off, scripts/PoliceBlockade.gd). Add a new
## match arm here for the next one-off rather than growing the generic
## action vocabulary for something that will only ever be used once.
func _run_custom_action(id: String) -> void:
	match id:
		"police_leave":
			var blockade := get_tree().get_first_node_in_group("police_blockade")
			if blockade:
				blockade.depart()
		_:
			push_warning("QuestGiverGeneric: unknown custom action id '%s'" % id)

# ---------------------------------------------------------------
# Schedule: routine (time-of-day) + conditional (quest-state) waypoints
# ---------------------------------------------------------------
# Re-evaluated every _process_wander() call (a few times a second at most,
# gated by NPCBase's own nav-arrival/wait-timer cadence) rather than
# cached and invalidated on signals -- simpler, and cheap enough that it
# doesn't need to be an event-driven cache.

func _process_wander(delta: float) -> void:
	var wp = _current_scheduled_position()
	if wp == null:
		super._process_wander(delta)
		return
	state = State.PATROL
	if nav_agent.target_position.distance_to(wp) > 0.1:
		nav_agent.target_position = wp
	if nav_agent.is_navigation_finished():
		velocity.x = 0.0
		velocity.z = 0.0
		return
	_move_toward_nav_target(move_speed)

## Conditional entries win over routine ones whenever both would apply
## (e.g. "stand at the street corner while Exterminator is active", which
## should override "spend daytime hours on the porch") -- checked in the
## order they're listed, first match wins. Returns null (meaning "no
## schedule applies, wander normally") if nothing matches either list.
func _current_scheduled_position() -> Variant:
	var schedule: Dictionary = _data.get("schedule", {})
	for entry in schedule.get("conditional", []):
		if _condition_matches(entry.get("condition")):
			var pos = Waypoints.get_position(entry.get("waypoint_id", ""))
			if pos != null:
				return pos
	var hour: float = GameClock.hour
	for entry in schedule.get("routine", []):
		if _hour_in_range(hour, float(entry.get("start_hour", 0.0)), float(entry.get("end_hour", 24.0))):
			var pos = Waypoints.get_position(entry.get("waypoint_id", ""))
			if pos != null:
				return pos
	return null

## Handles an overnight range (e.g. 20 -> 6) the same as a same-day range
## (e.g. 6 -> 20): "in range" means "on the forward arc from start to end",
## whichever way round that wraps past midnight.
func _hour_in_range(hour: float, start: float, end: float) -> bool:
	if start <= end:
		return hour >= start and hour < end
	return hour >= start or hour < end
