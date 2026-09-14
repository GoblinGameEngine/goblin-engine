extends Node
class_name DistanceCulling

# Tiered distance culling for the cel-shaded "comic book" look -- thick
# outlines (see shaders/toon_outline.gdshader) make small or distant
# objects read as illegible blobs well before they'd naturally leave
# view, so there's no visual cost to hiding them outright past a
# reasonable distance, only a real render-time saving. Three tiers,
# smallest culled nearest (matches how little a small prop registers at
# range vs. a whole house): small scenery/props, then trees, then houses
# (culled only at extreme range -- they're the neighborhood's own
# landmarks, meant to stay recognizable from far away).
#
# Built on Godot's own GeometryInstance3D.visibility_range_* system (a
# real engine feature: the renderer skips drawing the instance entirely
# past visibility_range_end, with a distance-based opacity fade over the
# last visibility_range_end_margin units so things don't hard-pop) rather
# than a hand-rolled per-frame distance-check loop -- this costs nothing
# per frame beyond what the renderer's own culling already does.

const SMALL_RANGE := 40.0
const TREE_RANGE := 85.0
const HOUSE_RANGE := 200.0
const FADE_MARGIN := 8.0

# Matched against the LOWERCASED node name -- covers both the original
# per-object names (collision-relevant scenery SceneryOptimizer leaves
# alone, e.g. "tree_trunk-col_1234") and the "<original>_multimesh" names
# SceneryOptimizer gives the batched groups it collapses decorative
# scenery into (e.g. "conifer_5678_multimesh") -- the prefix survives
# either way.
const SMALL_KEYWORDS := [
	"bush", "weed", "flower", "hedge", "chain", "porch_rail",
	"mailbox", "perimbush", "perimleaf", "bloom", "stem", "fence",
]
const TREE_KEYWORDS := [
	"conifer", "leaf", "canopy", "branch", "tree_trunk", "narrowleaf",
	"autumn", "shrubby", "weeping", "bark",
]
const HOUSE_KEYWORDS := ["structure"]

static func _category(node_name: String) -> String:
	var lower := node_name.to_lower()
	for kw in SMALL_KEYWORDS:
		if lower.find(kw) != -1:
			return "small"
	for kw in TREE_KEYWORDS:
		if lower.find(kw) != -1:
			return "tree"
	for kw in HOUSE_KEYWORDS:
		if lower.find(kw) != -1:
			return "house"
	return ""

## REAL BUG found live: VISIBILITY_RANGE_FADE_SELF (a smooth-looking
## fade) is implemented by Godot as a per-pixel DITHERED transparency
## pattern, not an actual alpha blend -- right at an object's fade-out
## distance, individual screen pixels flicker between fully opaque and
## fully absent in a stipple pattern. That's invisible to the eye alone
## normally, but it writes chaotic, dense depth/normal discontinuities
## into the buffers the screen-space outline pass (shaders/
## screen_outline.gdshader) reads every frame -- read as a solid band of
## false edges at whatever distance small props (fences, mailboxes) were
## fading out around (40m). Switched to VISIBILITY_RANGE_FADE_DISABLED:
## a hard cutoff, no dither, no fade-adjacent noise -- the object just
## pops rather than fading, a worthwhile trade now that the fade was
## actively breaking a different system, not merely cosmetic on its own.
static func _apply(gi: GeometryInstance3D, range_end: float) -> void:
	gi.visibility_range_end = range_end
	gi.visibility_range_end_margin = FADE_MARGIN
	gi.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED

## Recursively walks `root`, setting a distance-appropriate
## visibility_range on every categorized GeometryInstance3D (covers both
## MeshInstance3D and MultiMeshInstance3D, since both extend it). Returns
## a per-category count for a one-line boot log, same convention as
## ToonShading.apply_to_world()'s own return value.
##
## `multiplier` scales all three tiers uniformly -- Settings.draw_distance_mult,
## normally, but callable() and re-callable directly too so re-applying
## after the player changes the Graphics setting mid-game (Main.gd, on
## Settings.changed) is just calling this again on the same root, not a
## separate code path.
static func apply_to_world(root: Node, multiplier: float = 1.0) -> Dictionary:
	var counts := {"small": 0, "tree": 0, "house": 0}
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is GeometryInstance3D:
			var cat := _category(n.name)
			if cat == "small":
				_apply(n, SMALL_RANGE * multiplier)
				counts["small"] += 1
			elif cat == "tree":
				_apply(n, TREE_RANGE * multiplier)
				counts["tree"] += 1
			elif cat == "house":
				_apply(n, HOUSE_RANGE * multiplier)
				counts["house"] += 1
		for c in n.get_children():
			stack.append(c)
	return counts
