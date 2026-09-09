extends NPCBase
class_name BedbugEnemy

# No bedbug-specific behavior needed anymore -- NPCBase.gd drives any NPC's
# "Sprite" child generically (Walk/Run/Idle/Attack/Death), and the bedbug's
# DirectionalSprite (see scenes/npc/Bedbug.tscn) implements that interface
# the same way every other NPC's sprite does.
