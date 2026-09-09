extends NPCBase
class_name QuestGiver

# Generic quest-giving NPC: starts one quest, reacts once it's done, and
# reads back its own state on every interaction (dialog is re-fetched
# each time, never cached). Configurable per-instance via the exported
# fields below -- speaker_name is substituted straight into the dialog
# text -- so multiple quest givers (each just a .tscn instance of this
# same script with its own Sprite character + these fields set) can
# share one script instead of duplicating QuestGiverLloyd-style
# subclasses per NPC.

@export var speaker_name: String = "Lloyd"
@export var quest_id: String = "exterminator"
@export var spawn_count: int = 7
@export var spawn_radius: float = 24.0

func _ready() -> void:
	super._ready()
	dialog_id = speaker_name.to_lower()
	DialogBox.dialog_action.connect(_on_dialog_action)

func get_dialog_tree() -> Dictionary:
	if QuestManager.is_turned_in(quest_id):
		return {
			"start": {
				"speaker": speaker_name,
				"text": "Thanks again for clearing those things out.",
				"choices": [],
			}
		}
	if QuestManager.is_completed(quest_id):
		return {
			"start": {
				"speaker": speaker_name,
				"text": "Hooray! Thank you so much, now the police are leaving!",
				"choices": [
					{ "text": "Glad to help.", "next": "", "action": "police_leave" },
				],
			}
		}
	if QuestManager.is_active(quest_id):
		return {
			"start": {
				"speaker": speaker_name,
				"text": "Please hurry -- they're everywhere out there!",
				"choices": [],
			}
		}
	return {
		"start": {
			"speaker": speaker_name,
			"text": "Help! Bedbugs are attacking Lloyd Street! Will you help us?",
			"choices": [
				{ "text": "Yes", "next": "", "action": "start_exterminator" },
				{ "text": "No", "next": "" },
			],
		}
	}

func _on_dialog_action(action: String, npc: Node) -> void:
	if npc != self:
		return
	match action:
		"start_exterminator":
			QuestManager.start_quest(quest_id)
			NPCDirector.spawn_bedbugs(get_parent(), global_position, spawn_radius, spawn_count)
		"police_leave":
			QuestManager.mark_turned_in(quest_id)
			var blockade := get_tree().get_first_node_in_group("police_blockade")
			if blockade:
				blockade.depart()
