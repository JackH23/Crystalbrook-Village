"""Crystalbrook Village V14: mark, preview and remove selected lamppost mesh pieces.

Run via Blender Python Console with:
exec(compile(open('D:/codex+blender/village/scripts/remove_marked_lampposts_v14.py', encoding='utf-8').read(), 'remove_marked_lampposts_v14.py', 'exec'))

1. Place the 3D Cursor at the BASE of an unwanted lamppost and run mark_lamp().
2. Repeat for the other two poles.
3. Run preview_lamps() and inspect the printed candidate summary.
4. Run remove_lamps(confirm=True) only if the preview lists exactly three targets
   and plausible lamp components. The original .blend is backed up first.
"""
import bpy
import bmesh
import os
import json
from mathutils import Vector

OUT = os.environ.get('VILLAGE_PROJECT_DIR', r'D:\codex+blender\village')
PREFIXES = (
    'Lanterns • paths, bridges and terrace landings',
    'Expansion • promenade lanterns and overlook benches',
    'Pool terrace • warm reference lanterns',
    'Reference stairs • lanterns beside the walking route',
    'Wide garden • warm lantern beside bench',
    'Stair landing • warm lantern beside outer railing',
)
# A lamp's components (pole, housing, cap, etc.) should be close to its base in XY.
# The search also requires narrow components, so a nearby bench is not removed.
RADIUS = 0.36
MAX_COMPONENT_WIDTH = 0.75
MARK_KEY = 'V15LampBaseMarkers'
DONE_KEY = 'V15LampRemovalApplied'


def mark_lamp():
    scene = bpy.context.scene
    points = json.loads(scene.get(MARK_KEY, '[]'))
    if len(points) >= 3:
        raise RuntimeError('Already marked 3 lamps. Run clear_lamp_marks() to start over.')
    p = scene.cursor.location
    points.append([float(p.x), float(p.y), float(p.z)])
    scene[MARK_KEY] = json.dumps(points)
    print(f'Marked lamp {len(points)}/3 at {tuple(round(v, 3) for v in p)}')


def clear_lamp_marks():
    bpy.context.scene[MARK_KEY] = '[]'
    print('Cleared V14 lamp markers.')


def _components(bm):
    visited = set()
    for v in bm.verts:
        if v in visited:
            continue
        stack = [v]
        visited.add(v)
        component = []
        while stack:
            q = stack.pop()
            component.append(q)
            for edge in q.link_edges:
                other = edge.other_vert(q)
                if other not in visited:
                    visited.add(other)
                    stack.append(other)
        yield component



def _candidates():
    scene = bpy.context.scene
    marks = json.loads(scene.get(MARK_KEY, '[]'))

    # Allow removing 1, 2, or 3 lampposts
    if not 1 <= len(marks) <= 3:
        raise RuntimeError(
            f'Expected 1 to 3 cursor marks; currently have {len(marks)}.'
        )

    result = {}

    for obj in scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith(PREFIXES):
            continue

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        matches = []

        for component in _components(bm):
            world = [
                obj.matrix_world @ v.co
                for v in component
            ]

            low = Vector((
                min(p.x for p in world),
                min(p.y for p in world),
                min(p.z for p in world)
            ))

            high = Vector((
                max(p.x for p in world),
                max(p.y for p in world),
                max(p.z for p in world)
            ))

            center = (low + high) * 0.5
            width = max(
                high.x - low.x,
                high.y - low.y
            )

            if width > MAX_COMPONENT_WIDTH:
                continue

            for index, (x, y, z) in enumerate(marks):
                dist = (
                    (center.x - x) ** 2
                    + (center.y - y) ** 2
                ) ** 0.5

                if (
                    dist <= RADIUS
                    and low.z >= z - 0.25
                    and low.z <= z + 5.0
                ):
                    matches.append((
                        index,
                        component,
                        center.copy(),
                        width
                    ))
                    break

        if matches:
            result[obj] = (bm, matches)
        else:
            bm.free()

    return result

def preview_lamps():
    matches = _candidates()
    counts = [0] * len(
        json.loads(bpy.context.scene.get(MARK_KEY, "[]"))
    )
    print('\n=== V14 LAMP REMOVAL PREVIEW (NO DELETION) ===')
    for obj, (bm, groups) in matches.items():
        for index, component, center, width in groups:
            counts[index] += 1
            print(f'Target {index+1}: {obj.name} | {len(component)} vertices | '
                  f'center={tuple(round(v, 3) for v in center)} | width={width:.3f}')
        bm.free()
    print('Components per marked lamp:', counts)
    if any(n == 0 for n in counts):
        print('WARNING: One or more lamps have no matched geometry. Reposition cursor marks.')
    print('Inspect carefully: the preview is not proof that all components belong to lamps.')
    return counts


def remove_lamps(confirm=False):
    if confirm is not True:
        raise RuntimeError('Preview first; then call remove_lamps(confirm=True).')
    scene = bpy.context.scene
    if scene.get(DONE_KEY):
        raise RuntimeError('V14 removal was already applied to this scene.')
    matches = _candidates()
    counts = [0] * len(
        json.loads(bpy.context.scene.get(MARK_KEY, "[]"))
    )
    for bm, groups in matches.values():
        for index, *_ in groups:
            counts[index] += 1
    if any(n == 0 for n in counts):
        for bm, _ in matches.values():
            bm.free()
        raise RuntimeError(f'No geometry for one or more marked lamps: {counts}. Nothing removed.')
    version_dir = os.path.join(OUT, 'versions')
    os.makedirs(version_dir, exist_ok=True)
    backup = os.path.join(
        OUT,
        "versions",
        "Crystalbrook_Village_v14_before_remaining_lamp_removal.blend"
    )
    if os.path.exists(backup):
        for bm, _ in matches.values():
            bm.free()
        raise RuntimeError('Backup already exists. Refusing to overwrite: ' + backup)
    bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
    for obj, (bm, groups) in matches.items():
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        verts = {v for _, group, _, _ in groups for v in group}
        bmesh.ops.delete(bm, geom=list(verts), context='VERTS')
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
    scene[DONE_KEY] = True
    scene['Revision'] = 'V14 • Three marked courtyard and stair lampposts removed'
    dest = os.path.join(OUT, 'Crystalbrook_Village.blend')
    bpy.ops.wm.save_as_mainfile(filepath=dest)
    print(f'V14 saved: {dest} | removed component counts {counts}')
    print('Check the viewport for remaining pieces; use the backup if removal was incomplete.')

print('V14 loaded. Use mark_lamp(), preview_lamps(), then remove_lamps(confirm=True).')
