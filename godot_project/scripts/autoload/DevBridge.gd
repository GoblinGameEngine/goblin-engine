extends Node

# A local-only command server for driving/inspecting a RUNNING game
# instance from the outside (Claude's shell, not the human player) --
# built specifically to stop relying on xdotool key/mouse simulation +
# scrot screenshots + guessing pixel coordinates for everything, which is
# slow, imprecise, and breaks entirely if the desktop session locks (all
# of which happened in the session that led to building this).
#
# Debug-only (see _ready()) -- never listens in an exported release
# build. Listens on 127.0.0.1 only, never any external interface.
#
# Protocol: connect a TCP socket to 127.0.0.1:PORT, send ONE line of JSON
# (a command object) terminated by "\n", read back ONE line of JSON (the
# response), connection closes after that. See tools/gcmd.py (outside
# this project, in ~/goblins/tools/) for the client half.
#
# Commands (each is {"cmd": "<name>", ...fields}):
#   ping                                        -> {"ok": true, "result": "pong"}
#   help                                        -> {"ok": true, "result": [<this list>]}
#   eval        {"code": "<one expression>"}    -> evaluates via Expression, base
#                                                   instance = this node, so
#                                                   get_tree()/get_node() etc. work
#                                                   unqualified. Autoloads: address
#                                                   as get_node("/root/QuestManager").
#   run         {"code": "<gdscript statements>"} -> code becomes the BODY of
#                                                   `func run(root: Node):` on a
#                                                   throwaway RefCounted script --
#                                                   `root` is the SceneTree root
#                                                   (i.e. root.get_node("/root/Main"),
#                                                   root.get_node("/root/QuestManager")).
#                                                   Write a `return` to get a value
#                                                   back. This is the main way to
#                                                   drive MapEditorUI/QuestEditorUI
#                                                   etc. precisely -- call their own
#                                                   methods directly instead of
#                                                   simulating clicks on them.
#   screenshot  {"path": "/abs/path.png"}       -> saves the current rendered frame.
#                                                   Reads the real framebuffer, so it
#                                                   works even if the OS desktop is
#                                                   locked/obscured (unlike scrot).
#   dump_tree   {"path": "/root", "max_depth": 4} -> node names/types/paths, plus
#                                                   position+size+text for Controls --
#                                                   for finding a button's real
#                                                   coordinates instead of guessing
#                                                   from a screenshot.
#   key         {"physical_keycode": 4194333, "pressed": true, "ctrl"/"shift"/"alt": false}
#   key_tap     {"physical_keycode": 4194333, ...}   -> press then release
#   press_action / release_action  {"action": "toggle_editor"} -> Input.action_press/release
#   mouse_button {"button_index": 1, "pressed": true, "x":.., "y":..}
#   mouse_click  {"button_index": 1, "x":.., "y":..}  -> press then release
#   mouse_motion {"x":.., "y":.., "dx":.., "dy":..}   -> for camera-look drags;
#                                                        dx/dy is the RELATIVE delta,
#                                                        constructed directly (no OS
#                                                        cursor-warp synthetic-delta
#                                                        issue the way xdotool has)
#   mouse_wheel  {"direction": "up"|"down", "steps": 1, "x":.., "y":..}
#   quit                                        -> get_tree().quit()
#
# Every response is {"ok": true, "result": <json-safe value or omitted>,
# "result_str": str(value)} or {"ok": false, "error": "..."}.

const PORT_ENV := "GOBLINS_DEV_BRIDGE_PORT"
const DEFAULT_PORT := 8765

const COMMAND_NAMES := [
	"ping", "help", "eval", "run", "screenshot", "dump_tree",
	"key", "key_tap", "press_action", "release_action",
	"mouse_button", "mouse_click", "mouse_motion", "mouse_wheel", "quit",
]

var _server := TCPServer.new()
var _peers: Array = []   # [{peer: StreamPeerTCP, buffer: String}]
var _port := DEFAULT_PORT


func _ready() -> void:
	if not OS.is_debug_build():
		return
	process_mode = Node.PROCESS_MODE_ALWAYS
	var env_port := OS.get_environment(PORT_ENV)
	if env_port != "" and env_port.is_valid_int():
		_port = int(env_port)
	var err := _server.listen(_port, "127.0.0.1")
	if err != OK:
		push_warning("DevBridge: could not listen on 127.0.0.1:%d (error %d)" % [_port, err])
		return
	print("DevBridge: listening on 127.0.0.1:%d" % _port)


func _process(_delta: float) -> void:
	if not _server.is_listening():
		return
	while _server.is_connection_available():
		_peers.append({"peer": _server.take_connection(), "buffer": ""})

	var still_alive: Array = []
	for entry in _peers:
		var peer: StreamPeerTCP = entry["peer"]
		peer.poll()
		if peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
			continue   # dropped -- don't keep it
		var avail := peer.get_available_bytes()
		var responded := false
		if avail > 0:
			var chunk_result: Array = peer.get_partial_data(avail)
			if chunk_result[0] == OK:
				entry["buffer"] += (chunk_result[1] as PackedByteArray).get_string_from_utf8()
			var nl: int = entry["buffer"].find("\n")
			if nl != -1:
				var line: String = entry["buffer"].substr(0, nl)
				var response := _dispatch_line(line)
				peer.put_data((response + "\n").to_utf8_buffer())
				peer.disconnect_from_host()
				responded = true
		if not responded:
			still_alive.append(entry)
	_peers = still_alive


func _dispatch_line(line: String) -> String:
	var req = JSON.parse_string(line)
	if typeof(req) != TYPE_DICTIONARY or not req.has("cmd"):
		return JSON.stringify({"ok": false, "error": "expected a JSON object with a \"cmd\" field, got: %s" % line})
	var result := _handle(req)
	return JSON.stringify(result)


func _handle(req: Dictionary) -> Dictionary:
	var cmd: String = req.get("cmd", "")
	match cmd:
		"ping":
			return {"ok": true, "result": "pong"}
		"help":
			return {"ok": true, "result": COMMAND_NAMES}
		"eval":
			return _cmd_eval(req.get("code", ""))
		"run":
			return _cmd_run(req.get("code", ""))
		"screenshot":
			return _cmd_screenshot(req.get("path", ""))
		"dump_tree":
			return _cmd_dump_tree(req.get("path", "/root"), int(req.get("max_depth", 4)))
		"key":
			return _cmd_key(req)
		"key_tap":
			_cmd_key(_with(req, "pressed", true))
			_cmd_key(_with(req, "pressed", false))
			return {"ok": true}
		"press_action":
			Input.action_press(StringName(req.get("action", "")))
			return {"ok": true}
		"release_action":
			Input.action_release(StringName(req.get("action", "")))
			return {"ok": true}
		"mouse_button":
			return _cmd_mouse_button(req)
		"mouse_click":
			_cmd_mouse_button(_with(req, "pressed", true))
			_cmd_mouse_button(_with(req, "pressed", false))
			return {"ok": true}
		"mouse_motion":
			return _cmd_mouse_motion(req)
		"mouse_wheel":
			return _cmd_mouse_wheel(req)
		"quit":
			call_deferred("_do_quit")
			return {"ok": true}
		_:
			return {"ok": false, "error": "unknown cmd '%s' -- see 'help'" % cmd}


func _do_quit() -> void:
	get_tree().quit()


func _with(d: Dictionary, key: String, value) -> Dictionary:
	var d2 := d.duplicate()
	d2[key] = value
	return d2


## Wraps a raw GDScript value for the JSON response: JSON.stringify()
## can't serialize arbitrary Objects/Vector3/etc., so the human/JSON-safe
## "result" field is only included for types it actually supports --
## "result_str" (via GDScript's own str()) always works and is usually
## enough to just read the answer.
func _wrap_result(value) -> Dictionary:
	var out := {"ok": true, "result_str": str(value)}
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_ARRAY, TYPE_DICTIONARY:
			out["result"] = value
	return out


func _cmd_eval(code: String) -> Dictionary:
	var expr := Expression.new()
	var err := expr.parse(code, [])
	if err != OK:
		return {"ok": false, "error": "parse error: %s" % expr.get_error_text()}
	var result = expr.execute([], self, true)
	if expr.has_execute_failed():
		return {"ok": false, "error": "execution failed -- see the game's own log for details"}
	return _wrap_result(result)


## Multi-statement code, unlike eval's single expression. Inserted as the
## indented body of a function on a throwaway script -- write it exactly
## as you would inside that function (your own nested blocks need their
## own relative indentation, same as any GDScript function body), and
## write `return ...` if you want a value back.
func _cmd_run(code: String) -> Dictionary:
	var src := "extends RefCounted\nfunc run(root: Node):\n"
	for line in code.split("\n"):
		src += "\t" + line + "\n"
	var script := GDScript.new()
	script.source_code = src
	var err := script.reload()
	if err != OK:
		return {"ok": false, "error": "GDScript compile error (code %d) -- see the game's own log for the exact line/message" % err}
	var instance = script.new()
	var result = instance.run(get_tree().root)
	return _wrap_result(result)


func _cmd_screenshot(path: String) -> Dictionary:
	if path == "":
		return {"ok": false, "error": "missing 'path'"}
	var img := get_viewport().get_texture().get_image()
	var err := img.save_png(path)
	if err != OK:
		return {"ok": false, "error": "save_png failed with code %d" % err}
	return {"ok": true, "result": path}


func _cmd_dump_tree(path: String, max_depth: int) -> Dictionary:
	var start := get_node_or_null(path)
	if start == null:
		return {"ok": false, "error": "no node at path '%s'" % path}
	return {"ok": true, "result": _dump_node(start, 0, max_depth)}


func _dump_node(node: Node, depth: int, max_depth: int) -> Dictionary:
	var d := {"name": String(node.name), "type": node.get_class()}
	if node is Control:
		var c := node as Control
		d["rect"] = [c.global_position.x, c.global_position.y, c.size.x, c.size.y]
		d["visible"] = c.visible
		for prop in ["text", "title"]:
			if prop in node:
				d[prop] = node.get(prop)
	elif node is Node3D:
		d["global_position"] = var_to_str((node as Node3D).global_position)
	if depth < max_depth:
		var children := []
		for c in node.get_children():
			children.append(_dump_node(c, depth + 1, max_depth))
		if not children.is_empty():
			d["children"] = children
	return d


func _cmd_key(data: Dictionary) -> Dictionary:
	var ev := InputEventKey.new()
	var code := int(data.get("physical_keycode", data.get("keycode", 0)))
	ev.physical_keycode = code
	ev.keycode = int(data.get("keycode", code))
	ev.pressed = data.get("pressed", true)
	ev.ctrl_pressed = data.get("ctrl", false)
	ev.shift_pressed = data.get("shift", false)
	ev.alt_pressed = data.get("alt", false)
	ev.echo = data.get("echo", false)
	Input.parse_input_event(ev)
	return {"ok": true}


func _cmd_mouse_button(data: Dictionary) -> Dictionary:
	var ev := InputEventMouseButton.new()
	ev.button_index = int(data.get("button_index", MOUSE_BUTTON_LEFT))
	ev.pressed = data.get("pressed", true)
	ev.position = Vector2(float(data.get("x", 0.0)), float(data.get("y", 0.0)))
	ev.global_position = ev.position
	Input.parse_input_event(ev)
	return {"ok": true}


func _cmd_mouse_motion(data: Dictionary) -> Dictionary:
	var ev := InputEventMouseMotion.new()
	ev.position = Vector2(float(data.get("x", 0.0)), float(data.get("y", 0.0)))
	ev.relative = Vector2(float(data.get("dx", 0.0)), float(data.get("dy", 0.0)))
	Input.parse_input_event(ev)
	return {"ok": true}


func _cmd_mouse_wheel(data: Dictionary) -> Dictionary:
	var idx := MOUSE_BUTTON_WHEEL_UP if data.get("direction", "up") == "up" else MOUSE_BUTTON_WHEEL_DOWN
	var steps := int(data.get("steps", 1))
	for i in range(steps):
		_cmd_mouse_button({"button_index": idx, "pressed": true, "x": data.get("x", 0.0), "y": data.get("y", 0.0)})
		_cmd_mouse_button({"button_index": idx, "pressed": false, "x": data.get("x", 0.0), "y": data.get("y", 0.0)})
	return {"ok": true}
