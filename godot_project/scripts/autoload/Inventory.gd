extends Node

# Simple stacking inventory for the (single) player. Loads item definitions
# from data/items.json; runtime stacks are just an id->count dictionary,
# which keeps save/load trivial later (it's already a Dictionary you can
# dump straight to JSON).

signal item_added(item_id: String, count: int)
signal item_removed(item_id: String, count: int)
signal changed()

const DATA_PATH := "res://data/items.json"

var definitions: Dictionary = {}   # item_id -> {name, stackable, max_stack, description, ...}
var stacks: Dictionary = {}        # item_id -> count

func _ready() -> void:
	var text := _read_file(DATA_PATH)
	if text.is_empty():
		push_error("Inventory: failed to read %s" % DATA_PATH)
		return
	var data = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		push_error("Inventory: malformed JSON in %s" % DATA_PATH)
		return
	for item in data.get("items", []):
		definitions[item.id] = item

func _read_file(path: String) -> String:
	if not FileAccess.file_exists(path):
		return ""
	var f := FileAccess.open(path, FileAccess.READ)
	var text := f.get_as_text()
	f.close()
	return text

func get_definition(item_id: String) -> Dictionary:
	return definitions.get(item_id, {})

func count(item_id: String) -> int:
	return stacks.get(item_id, 0)

func has(item_id: String, amount: int = 1) -> bool:
	return count(item_id) >= amount

func add(item_id: String, amount: int = 1) -> void:
	if amount <= 0:
		return
	stacks[item_id] = count(item_id) + amount
	item_added.emit(item_id, amount)
	changed.emit()
	QuestManager.report_item_collected(item_id, count(item_id))

func remove(item_id: String, amount: int = 1) -> bool:
	if not has(item_id, amount):
		return false
	stacks[item_id] = count(item_id) - amount
	if stacks[item_id] <= 0:
		stacks.erase(item_id)
	item_removed.emit(item_id, amount)
	changed.emit()
	return true

## Applies an item's use_effect (currently just "heal") and consumes one.
func use(item_id: String, user: Node) -> bool:
	if not has(item_id, 1):
		return false
	var def := get_definition(item_id)
	match def.get("use_effect", ""):
		"heal":
			var health := user.get_node_or_null("Health")
			if health:
				health.heal(float(def.get("use_value", 0)))
		_:
			pass
	return remove(item_id, 1)

func all_stacks() -> Dictionary:
	return stacks.duplicate()
