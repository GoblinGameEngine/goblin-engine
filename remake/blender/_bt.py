import bpy, sys
bpy.ops.mesh.primitive_cube_add()
bpy.ops.export_scene.gltf(filepath="/home/deck/goblin-engine/remake/blender/_test.glb")
print("OK", bpy.app.version_string)
