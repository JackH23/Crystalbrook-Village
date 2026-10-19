r"""Crystalbrook Village V15: remove 1–3 marked lampposts from existing meshes.

Blender Python Console:
exec(compile(open(r'D:\codex+blender\village\scripts\remove_marked_lampposts_v15.py', encoding='utf-8').read(), 'remove_marked_lampposts_v15.py', 'exec'))

Use mark_lamp() at each unwanted pole's base, preview_lamps(), then
remove_lamps(confirm=True) only after verifying the candidate components.
"""
import bpy
import bmesh
import os
import json
from datetime import datetime
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
RADIUS = 0.36
MAX_COMPONENT_WIDTH = 0.75
MARK_KEY = 'V15LampBaseMarkers'
DONE_KEY = 'V15LampRemovalApplied'


def _marks():
    return json.loads(bpy.context.scene.get(MARK_KEY, '[]'))


def mark_lamp():
    points = _marks()
    if len(points) >= 3:
        raise RuntimeError('Already marked 3 lamps. Run clear_lamp_marks() to start over.')
    p = bpy.context.scene.cursor.location
    points.append([float(p.x), float(p.y), float(p.z)])
    bpy.context.scene[MARK_KEY] = json.dumps(points)
    print(f'Marked lamp {len(points)}/3 at {tuple(round(v, 3) for v in p)}')


def clear_lamp_marks():
    bpy.context.scene[MARK_KEY] = '[]'
    print('Cleared V15 lamp markers.')


def _components(bm):
    visited = set()
    for v in bm.verts:
        if v in visited:
            continue
        stack = [v]
        visited.add(v)
        group = []
        while stack:
            q = stack.pop()
            group.append(q)
            for edge in q.link_edges:
                other = edge.other_vert(q)
                if other not in visited:
                    visited.add(other)
                    stack.append(other)
        yield group


def _candidates():
    marks = _marks()
    if not 1 <= len(marks) <= 3:
        raise RuntimeError(f'Expected 1 to 3 cursor marks; currently have {len(marks)}.')
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or not obj.name.startswith(PREFIXES):
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        matches = []
        for component in _components(bm):
            world = [obj.matrix_world @ v.co for v in component]
            low = Vector((min(p.x for p in world), min(p.y for p in world), min(p.z for p in world)))
            high = Vector((max(p.x for p in world), max(p.y for p in world), max(p.z for p in world)))
            center = (low + high) * 0.5
            width = max(high.x - low.x, high.y - low.y)
            if width > MAX_COMPONENT_WIDTH:
                continue
            for index, (x, y, z) in enumerate(marks):
                distance = ((center.x - x)**2 + (center.y - y)**2)**0.5
                if distance <= RADIUS and z - 0.25 <= low.z <= z + 5.0:
                    matches.append((index, component, center.copy(), width))
                    break
        if matches:
            result[obj] = (bm, matches)
        else:
            bm.free()
    return result


def preview_lamps():
    matches = _candidates()
    counts = [0] * len(_marks())
    print('\n=== V15 LAMP REMOVAL PREVIEW (NO DELETION) ===')
    for obj, (bm, groups) in matches.items():
        for index, component, center, width in groups:
            counts[index] += 1
            print(f'Target {index + 1}: {obj.name} | {len(component)} vertices | '
                  f'center={tuple(round(v, 3) for v in center)} | width={width:.3f}')
        bm.free()
    print('Components per marked lamp:', counts)
    if any(n == 0 for n in counts):
        print('WARNING: One or more marks have no matching geometry.')
    print('Review each component before deleting; matching by proximity is not definitive.')
    return counts


def remove_lamps(confirm=False):
    if confirm is not True:
        raise RuntimeError('Run preview_lamps() and verify all matches before confirming.')
    scene = bpy.context.scene
    if scene.get(DONE_KEY):
        raise RuntimeError('V15 removal was already applied to this scene.')
    matches = _candidates()
    try:
        counts = [0] * len(_marks())
        for bm, groups in matches.values():
            for index, *_ in groups:
                counts[index] += 1
        if any(n == 0 for n in counts):
            raise RuntimeError(f'Missing geometry for a marked lamp: {counts}. Nothing removed.')
        version_dir = os.path.join(OUT, 'versions')
        os.makedirs(version_dir, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        backup = os.path.join(version_dir, f'Crystalbrook_Village_v14_before_remaining_lamp_removal_{stamp}.blend')
        if os.path.exists(backup):
            raise RuntimeError('Backup filename collision: ' + backup)
        bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
        for obj, (bm, groups) in matches.items():
            if obj.data.users > 1:
                obj.data = obj.data.copy()
            verts = {v for _, component, _, _ in groups for v in component}
            bmesh.ops.delete(bm, geom=list(verts), context='VERTS')
            bm.to_mesh(obj.data)
            obj.data.update()
        scene[DONE_KEY] = True
        scene['Revision'] = f'V15 • {len(counts)} additional marked lamppost(s) removed'
        dest = os.path.join(OUT, 'Crystalbrook_Village.blend')
        bpy.ops.wm.save_as_mainfile(filepath=dest)
        print(f'V15 saved: {dest} | removed component counts {counts}')
        print(f'Backup: {backup}')
    finally:
        for bm, _ in matches.values():
            bm.free()


print('V15 loaded. Use mark_lamp(), preview_lamps(), then remove_lamps(confirm=True).')
