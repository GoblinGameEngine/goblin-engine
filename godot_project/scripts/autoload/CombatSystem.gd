extends Node

# Single funnel for all damage in the game (player weapons, NPC weapons).
# Anything that can fight exposes:
#   func get_faction() -> String
#   a child Node named "Health" (see Health.gd)
# and optionally:
#   func on_attacked(attacker: Node) -> void   -- AI reaction hook

signal damage_dealt(attacker: Node, target: Node, amount: float)
signal target_died(target: Node, attacker: Node, target_faction: String)

func apply_damage(attacker: Node, target: Node, amount: float) -> void:
	if target == null or not is_instance_valid(target):
		return
	var health: Health = target.get_node_or_null("Health")
	if health == null or not health.is_alive():
		return

	var attacker_faction := _faction_of(attacker)
	var target_faction := _faction_of(target)

	health.apply_damage(amount, attacker)
	damage_dealt.emit(attacker, target, amount)

	if not health.is_alive():
		if target_faction != "":
			QuestManager.report_kill(target_faction)
		target_died.emit(target, attacker, target_faction)
		return

	# Provoke: getting hit by a faction you weren't already hostile to sours
	# relations and lets the victim's AI react (fight back or flee).
	if attacker_faction != "" and target_faction != "" and attacker_faction != target_faction:
		if not FactionManager.is_hostile(attacker_faction, target_faction):
			FactionManager.adjust_disposition(attacker_faction, target_faction, -40.0)
		if target.has_method("on_attacked"):
			target.on_attacked(attacker)

func _faction_of(node: Node) -> String:
	if node != null and is_instance_valid(node) and node.has_method("get_faction"):
		return node.get_faction()
	return ""
