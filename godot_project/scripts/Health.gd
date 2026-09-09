extends Node
class_name Health

# Attach as a child node named "Health" to anything that can take damage
# (Player, NPCBase). CombatSystem looks it up by that node name/path.

signal damaged(amount: float, attacker: Node)
signal died(attacker: Node)
signal healed(amount: float)

@export var max_health: float = 100.0
var current: float

func _ready() -> void:
	current = max_health

func is_alive() -> bool:
	return current > 0.0

func apply_damage(amount: float, attacker: Node = null) -> void:
	if not is_alive() or amount <= 0.0:
		return
	current = max(0.0, current - amount)
	damaged.emit(amount, attacker)
	if current <= 0.0:
		died.emit(attacker)

func heal(amount: float) -> void:
	if amount <= 0.0:
		return
	current = min(max_health, current + amount)
	healed.emit(amount)
