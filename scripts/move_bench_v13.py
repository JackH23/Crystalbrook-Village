
import bpy
import os
from mathutils import Vector

OUT = r"D:\codex+blender\village"
scene = bpy.context.scene

# Adjust these values to move the bench.
# These are WORLD coordinates, not screen directions.
MOVE_X = -0.20
MOVE_Y = 0.0
MOVE_Z = 0.0

# Find the existing bench
bench = next(
    (
        obj for obj in scene.objects
        if obj.name.startswith(
            "Mill courtyard • bench moved to marked right-side position"
        )
    ),
    None
)

if bench is None:
    raise RuntimeError("Bench not found in the current scene")

# Prevent accidentally moving the bench twice
if scene.get("BenchMoveV13Applied", False):
    raise RuntimeError("V13 bench movement already applied")

# Save a backup before modifying anything
backup = os.path.join(
    OUT,
    "versions",
    "Crystalbrook_Village_v12_before_bench_move.blend"
)

os.makedirs(os.path.dirname(backup), exist_ok=True)

bpy.ops.wm.save_as_mainfile(
    filepath=backup,
    copy=True
)

# Record original world position
original = bench.matrix_world.translation.copy()

# Move existing bench without changing rotation
bench.matrix_world.translation += Vector((
    MOVE_X,
    MOVE_Y,
    MOVE_Z
))

bpy.context.view_layer.update()

new_position = bench.matrix_world.translation.copy()

# Update revision information
scene["Revision"] = "V13 • Bench moved closer to house"
scene["BenchMoveV13Applied"] = True

# Save the updated village
bpy.ops.wm.save_as_mainfile(
    filepath=os.path.join(
        OUT,
        "Crystalbrook_Village.blend"
    )
)

print("SUCCESS: Bench position updated!")
print("Original:", tuple(original))
print("New:", tuple(new_position))
print("Movement:", MOVE_X, MOVE_Y, MOVE_Z)
