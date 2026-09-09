extends Node

# Quest definitions come from data/quests.json (static data). Runtime
# progress is tracked here in memory. Objective types:
#   fetch  - target = item_id,   count = how many the player must hold
#   kill   - target = faction_id (or a specific npc "tag"), count = kills needed
#   action - target = arbitrary action id, count = times it must be reported
#   quest  - target = another quest's id, count always 1 (quest-chain gate)

signal quest_started(quest_id: String)
signal quest_updated(quest_id: String)
signal quest_completed(quest_id: String)
signal quest_failed(quest_id: String)
signal quest_turned_in(quest_id: String)
signal tracked_quest_changed(quest_id: String)

const DATA_PATH := "res://data/quests.json"

var definitions: Dictionary = {}     # quest_id -> quest def dict
var active: Dictionary = {}          # quest_id -> runtime state dict
var completed: Dictionary = {}       # quest_id -> true

# Objectives completing (see _complete()) grants rewards immediately, but
# some quests have a narrative "go tell the quest-giver" beat after that --
# turned_in tracks whether that closing conversation has happened yet, so
# UI (compass/map) can keep pointing the player at the giver until it has.
var turned_in: Dictionary = {}

# Which quest the compass/map currently show a marker for. The player can
# change this from the Quests menu page.
var tracked_quest_id: String = ""

func _ready() -> void:
	var text := _read_file(DATA_PATH)
	if text.is_empty():
		push_error("QuestManager: failed to read %s" % DATA_PATH)
		return
	var data = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		push_error("QuestManager: malformed JSON in %s" % DATA_PATH)
		return
	for q in data.get("quests", []):
		definitions[q.id] = q
	for q in definitions.values():
		if q.get("auto_start", false):
			start_quest(q.id)

func _read_file(path: String) -> String:
	if not FileAccess.file_exists(path):
		return ""
	var f := FileAccess.open(path, FileAccess.READ)
	var text := f.get_as_text()
	f.close()
	return text

func is_active(quest_id: String) -> bool:
	return active.has(quest_id)

func is_completed(quest_id: String) -> bool:
	return completed.has(quest_id)

## Single-word state for the quest-giver dialogue/schedule system (see
## QuestGiverGeneric.gd, data/quest_givers.json) -- lets a dialogue-state
## or schedule condition say {"quest_id": "x", "state": "active"} instead
## of every author having to know the is_active()/is_completed()/
## is_turned_in() combination that means each state.
func get_state(quest_id: String) -> String:
	if is_turned_in(quest_id):
		return "turned_in"
	if is_completed(quest_id):
		return "completed"
	if is_active(quest_id):
		return "active"
	return "not_started"

func can_start(quest_id: String) -> bool:
	if is_active(quest_id) or is_completed(quest_id):
		return false
	var def: Dictionary = definitions.get(quest_id, {})
	for prereq in def.get("prereq", []):
		if not is_completed(prereq):
			return false
	return true

func start_quest(quest_id: String) -> bool:
	if not definitions.has(quest_id) or not can_start(quest_id):
		return false
	var def: Dictionary = definitions[quest_id]
	var objectives := []
	for o in def.get("objectives", []):
		objectives.append({ "type": o.type, "target": o.target, "count": o.count, "progress": 0 })
	active[quest_id] = { "objectives": objectives }
	quest_started.emit(quest_id)
	if tracked_quest_id == "" or is_completed(tracked_quest_id):
		set_tracked_quest(quest_id)
	_check_quest_gated_starts()
	_evaluate(quest_id)
	return true

func set_tracked_quest(quest_id: String) -> void:
	tracked_quest_id = quest_id
	tracked_quest_changed.emit(quest_id)

func is_turned_in(quest_id: String) -> bool:
	return turned_in.get(quest_id, false)

func mark_turned_in(quest_id: String) -> void:
	turned_in[quest_id] = true
	quest_turned_in.emit(quest_id)

func get_target_group(quest_id: String) -> String:
	return definitions.get(quest_id, {}).get("target_group", "")

func get_active_quests() -> Array:
	return active.keys()

func get_completed_quests() -> Array:
	return completed.keys()

func get_quest_title(quest_id: String) -> String:
	return definitions.get(quest_id, {}).get("title", quest_id)

func get_quest_description(quest_id: String) -> String:
	return definitions.get(quest_id, {}).get("description", "")

func get_map_marker(quest_id: String) -> Dictionary:
	return definitions.get(quest_id, {}).get("map_marker", {})

func get_objectives(quest_id: String) -> Array:
	return active.get(quest_id, {}).get("objectives", [])

## --- Progress reporting (called from gameplay systems) ---

func report_item_collected(item_id: String, current_total: int) -> void:
	_report("fetch", item_id, current_total, true)

func report_kill(faction_id: String) -> void:
	_report("kill", faction_id, 1, false)

func report_action(action_id: String) -> void:
	_report("action", action_id, 1, false)

func _report(obj_type: String, target: String, amount: int, is_absolute: bool) -> void:
	for quest_id in active.keys():
		var state: Dictionary = active[quest_id]
		var touched := false
		for obj in state.objectives:
			if obj.type == obj_type and obj.target == target and obj.progress < obj.count:
				obj.progress = amount if is_absolute else obj.progress + amount
				obj.progress = min(obj.progress, obj.count)
				touched = true
		if touched:
			_evaluate(quest_id)

func _check_quest_gated_starts() -> void:
	# Quest-chain objectives reference OTHER quest ids; re-evaluate any
	# active quest that's waiting on a "quest" type objective whenever
	# something completes.
	for quest_id in active.keys():
		for obj in active[quest_id].objectives:
			if obj.type == "quest" and is_completed(obj.target):
				obj.progress = obj.count
		_evaluate(quest_id)

func _evaluate(quest_id: String) -> void:
	if not active.has(quest_id):
		return
	var state: Dictionary = active[quest_id]
	quest_updated.emit(quest_id)
	for obj in state.objectives:
		if obj.progress < obj.count:
			return
	_complete(quest_id)

func _complete(quest_id: String) -> void:
	if not active.has(quest_id):
		return
	active.erase(quest_id)
	completed[quest_id] = true
	var def: Dictionary = definitions.get(quest_id, {})
	for reward in def.get("rewards", {}).get("items", []):
		Inventory.add(reward.id, int(reward.get("count", 1)))
	quest_completed.emit(quest_id)
	report_action("quest_complete:" + quest_id)
	_check_quest_gated_starts()
	# Auto-start any quest whose only blocker was this one completing.
	for q in definitions.values():
		if can_start(q.id) and not q.get("auto_start", false):
			for prereq in q.get("prereq", []):
				if prereq == quest_id:
					start_quest(q.id)
