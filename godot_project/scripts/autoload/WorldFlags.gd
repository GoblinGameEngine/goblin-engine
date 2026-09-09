extends Node

# Generic one-off story flags for the quest-giver action system (see
# QuestGiverGeneric._execute_action(), the "set_flag"/"has_flag" action and
# condition types) -- for state that doesn't belong to any one quest
# (e.g. "met_lloyd_once") and would otherwise need a whole fake quest just
# to have something to check. In-memory only, same as QuestManager's
# runtime progress -- no save/load system exists yet to persist this
# across a restart (see reference/memory.txt's map-editor save-confirm
# note; a real save-game system was explicitly not asked for yet).

var _flags: Dictionary = {}

func get_flag(id: String, default: bool = false) -> bool:
	return _flags.get(id, default)

func set_flag(id: String, value: bool = true) -> void:
	_flags[id] = value
