"""
Shared Blender headless-build helpers for this project's procedural
buildings (first used by build_farm_buildings.py, now also
build_downtown_buildings.py). Every building is a REAL hollow wall
shell -- floor + 4 walls + ceiling cap, genuine wall thickness, a real
walkable interior void, not a facade -- with door/window holes cut via
boolean difference and recorded in godot_project/assets/editor_assets/
manifest.json's exact {kind,x,y,hinge_x,hinge_y,plane_rot,z,width,height}
shape, so scripts/world/OpeningsSetup.gd's spawn code works on them
unmodified.

Real UVs via per-face cube projection (bpy.ops.uv.cube_project), never
procedural texture coordinates -- confirmed dead on glTF export
(reference/memory.txt). Exported meshes are named "<id>-col" --
Godot's glTF-import node-name-suffix convention for real collision --
though scripts/world/RingCoords.add_trimesh_collision() is the actual
mechanism callers rely on at runtime (confirmed live in Phase B that a
fresh export needs that regardless of the "-col" name; kept here too in
case a future Godot/import-settings change makes the suffix start
working on its own).
"""

import bpy
import bmesh
import math
import os

FT = 0.3048

REPO = "/home/nelahi/goblin-engine/.claude/worktrees/station-player-controls/godot_project"
TEXTURES_DIR = os.path.join(REPO, "assets", "textures")

WALL_THICKNESS = 0.2
FLOOR_THICKNESS = 0.15
CEILING_THICKNESS = 0.15
DOOR_WIDTH = 1.0
DOOR_HEIGHT = 2.1


def clear_scene():
	bpy.ops.object.select_all(action="SELECT")
	bpy.ops.object.delete(use_global=False)
	for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.objects, bpy.data.images):
		for block in list(coll):
			if block.users == 0:
				coll.remove(block)


def load_material(name, texture_filename, roughness=0.85):
	mat = bpy.data.materials.new(name)
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes.get("Principled BSDF")
	tex_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
	tex_node.image = bpy.data.images.load(os.path.join(TEXTURES_DIR, texture_filename))
	mat.node_tree.links.new(bsdf.inputs["Base Color"], tex_node.outputs["Color"])
	bsdf.inputs["Roughness"].default_value = roughness
	return mat


def cube_uv(obj):
	bpy.context.view_layer.objects.active = obj
	bpy.ops.object.mode_set(mode="EDIT")
	bpy.ops.mesh.select_all(action="SELECT")
	bpy.ops.uv.cube_project(cube_size=1.0)
	bpy.ops.object.mode_set(mode="OBJECT")


def make_box(name, size, location):
	bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
	obj = bpy.context.active_object
	obj.name = name
	obj.scale = size
	bpy.context.view_layer.objects.active = obj
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	return obj


def boolean_diff(obj, cutter):
	mod = obj.modifiers.new(name="cut", type="BOOLEAN")
	mod.operation = "DIFFERENCE"
	mod.solver = "EXACT"
	mod.object = cutter
	bpy.context.view_layer.objects.active = obj
	bpy.ops.object.modifier_apply(modifier=mod.name)
	bpy.data.objects.remove(cutter, do_unlink=True)


def join_objects(objs):
	bpy.ops.object.select_all(action="DESELECT")
	for o in objs:
		o.select_set(True)
	bpy.context.view_layer.objects.active = objs[0]
	bpy.ops.object.join()
	return bpy.context.active_object


def build_shell(width, depth, wall_h):
	"""Outer box minus an inset interior void -- leaves a real floor
	slab, 4 walls, and a ceiling cap, all with WALL_THICKNESS of solid
	material between the outside and the walkable interior air."""
	outer = make_box("shell", (width, depth, wall_h), (0, 0, wall_h / 2.0))
	void_h = wall_h - FLOOR_THICKNESS - CEILING_THICKNESS
	inner = make_box("void", (width - 2 * WALL_THICKNESS, depth - 2 * WALL_THICKNESS, void_h),
		(0, 0, FLOOR_THICKNESS + void_h / 2.0))
	boolean_diff(outer, inner)
	return outer


def cut_front_door(obj, x, depth, z_center, width=DOOR_WIDTH, height=DOOR_HEIGHT):
	"""Cuts a door-sized hole through the FRONT wall (y = -depth/2) at
	local x. The cutter is thicker than the wall so it cuts all the way
	through regardless of exact wall alignment."""
	cutter = make_box("door_cut", (width, WALL_THICKNESS * 3.0, height), (x, -depth / 2.0, z_center))
	boolean_diff(obj, cutter)


def register_front_door(openings, x, depth, width=DOOR_WIDTH, height=DOOR_HEIGHT):
	# Front wall, plane_rot=0 -- same convention house1/2/3's manifest
	# entries use for their own front-wall doors (hinge offset along the
	# wall's own run axis, x; y/hinge_y unchanged at the wall's position).
	openings.append({
		"kind": "door", "x": x, "y": -depth / 2.0,
		"hinge_x": x - width / 2.0, "hinge_y": -depth / 2.0,
		"plane_rot": 0.0, "z": 0.0, "width": width, "height": height,
	})


def build_gable_roof(width, depth, base_z, pitch_deg, overhang, material):
	"""A simple gable roof -- ridge along the width (X) axis, sloping
	down to the eaves along the depth (Y) axis, with triangular gable-end
	caps so it reads as a closed volume from outside. Not structural
	(the shell's own flat ceiling already seals the interior) -- purely
	the visible roof shape sitting on top of it."""
	hw = width / 2.0 + overhang
	hd = depth / 2.0 + overhang
	rise = (depth / 2.0) * math.tan(math.radians(pitch_deg))
	ridge_z = base_z + rise

	bm = bmesh.new()
	fl = bm.verts.new((-hw, -hd, base_z))
	fr = bm.verts.new((hw, -hd, base_z))
	bl = bm.verts.new((-hw, hd, base_z))
	br = bm.verts.new((hw, hd, base_z))
	rl = bm.verts.new((-hw, 0.0, ridge_z))
	rr = bm.verts.new((hw, 0.0, ridge_z))
	bm.faces.new((fl, fr, rr, rl))   # front slope
	bm.faces.new((rl, rr, br, bl))   # back slope
	bm.faces.new((fl, rl, bl))       # left gable end
	bm.faces.new((fr, br, rr))       # right gable end (winding mirrored)
	bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

	mesh = bpy.data.meshes.new("roof_mesh")
	bm.to_mesh(mesh)
	bm.free()
	obj = bpy.data.objects.new("roof", mesh)
	bpy.context.collection.objects.link(obj)
	obj.data.materials.append(material)
	cube_uv(obj)
	return obj


def build_gambrel_roof(width, depth, base_z, lower_pitch_deg, upper_pitch_deg, lower_frac, overhang, material):
	"""Barn-style two-slope gambrel: a steep lower segment from each eave,
	meeting a shallow upper segment that closes at the ridge -- the
	classic barn silhouette, per the researched proportions (~24/12 lower
	over ~9/12 upper)."""
	hw = width / 2.0 + overhang
	hd = depth / 2.0
	break_y = hd * (1.0 - lower_frac)
	lower_rise = (hd - break_y) * math.tan(math.radians(lower_pitch_deg))
	break_z = base_z + lower_rise
	upper_rise = break_y * math.tan(math.radians(upper_pitch_deg))
	ridge_z = break_z + upper_rise

	bm = bmesh.new()
	fl = bm.verts.new((-hw, -hd - overhang, base_z))
	fr = bm.verts.new((hw, -hd - overhang, base_z))
	bl = bm.verts.new((-hw, hd + overhang, base_z))
	br = bm.verts.new((hw, hd + overhang, base_z))
	fbl = bm.verts.new((-hw, -break_y, break_z))
	fbr = bm.verts.new((hw, -break_y, break_z))
	bbl = bm.verts.new((-hw, break_y, break_z))
	bbr = bm.verts.new((hw, break_y, break_z))
	rl = bm.verts.new((-hw, 0.0, ridge_z))
	rr = bm.verts.new((hw, 0.0, ridge_z))
	bm.faces.new((fl, fr, fbr, fbl))     # front lower slope
	bm.faces.new((fbl, fbr, rr, rl))     # front upper slope
	bm.faces.new((rl, rr, bbr, bbl))     # back upper slope
	bm.faces.new((bbl, bbr, br, bl))     # back lower slope
	bm.faces.new((fl, fbl, rl, bbl, bl))  # left gable end (5-gon)
	bm.faces.new((fr, br, bbr, rr, fbr))  # right gable end (mirrored winding)
	bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

	mesh = bpy.data.meshes.new("roof_mesh")
	bm.to_mesh(mesh)
	bm.free()
	obj = bpy.data.objects.new("roof", mesh)
	bpy.context.collection.objects.link(obj)
	obj.data.materials.append(material)
	cube_uv(obj)
	return obj


def build_parapet(width, depth, base_z, height, thickness, material):
	"""A flat-roofed storefront's own low parapet lip -- a thin hollow
	rectangular ring standing proud of the roofline (built the same
	hollow-box-via-boolean way as the shell itself, just short and
	open-topped), instead of a gable/gambrel roof. Downtown storefronts
	read as flat-roofed rectangular boxes, not pitched roofs."""
	outer = make_box("parapet", (width, depth, height), (0, 0, base_z + height / 2.0))
	inner = make_box("parapet_void", (width - 2 * thickness, depth - 2 * thickness, height + 0.2),
		(0, 0, base_z + height / 2.0))
	boolean_diff(outer, inner)
	outer.data.materials.append(material)
	cube_uv(outer)
	return outer


def export_glb(obj, out_dir, filename):
	bpy.ops.object.select_all(action="DESELECT")
	obj.select_set(True)
	bpy.context.view_layer.objects.active = obj
	bpy.ops.export_scene.gltf(
		filepath=os.path.join(out_dir, filename),
		use_selection=True,
		export_format="GLB",
		export_yup=True,
	)
