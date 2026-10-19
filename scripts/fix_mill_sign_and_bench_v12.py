"""Attach the mill's leftover sign hardware and relocate the marked bench."""
import bpy,bmesh,ast,os,math,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village');source=os.path.dirname(os.path.abspath(__file__));scene=bpy.context.scene
if scene.get('Revision','').startswith('V12'):raise RuntimeError('V12 correction is already applied')
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v11.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
LOW=-.65
for filename,names in [('build_village.py',{'Build'}),('widen_garden_terrace_v7.py',{'parts'}),('add_marked_area_v3.py',{'old_outline','extension','pt'})]:
    for node in ast.parse(open(os.path.join(source,filename),encoding='utf-8').read()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
# Hardware and label were separate assets: the label moved in V11, the bracket did not.
sign=next(o for o in scene.objects if o.name.startswith('Signs • entrance and shop brackets'))
parts(sign,lambda p:Vector((1.5,-.2,-1.75)) if 8.10<p.x<8.70 and -8.20<p.y<-7.40 and 2.15<p.z<2.90 else False)
# Remove the old mill's small pottery/sack cluster left hovering near the roof/tree.
props=next(o for o in scene.objects if o.name.startswith('Market props • baskets, pottery, sacks and stacked crates'))
parts(props,lambda p:8.35<p.x<9.55 and -7.70<p.y<-6.80 and 1.0<p.z<1.85)
START=math.radians(-145);END=math.radians(40);LOW=-.65
a=math.radians(-45);old=pt(a,old_outline(a)+extension(a)*.80,LOW)
oldrot=Matrix.Rotation(a+pi/2,3,'Z');newrot=Matrix.Rotation(pi/2,3,'Z');target=Vector((11.94,-6.35,-.50))
ob=next(o for o in scene.objects if o.name.startswith('Expansion • promenade lanterns and overlook benches'))
bm=bmesh.new();bm.from_mesh(ob.data);seen=set();chosen=set();groups=0
for v in bm.verts:
    if v in seen:continue
    stack=[v];seen.add(v);group=[]
    while stack:
        q=stack.pop();group.append(q)
        for e in q.link_edges:
            r=e.other_vert(q)
            if r not in seen:seen.add(r);stack.append(r)
    center=sum((ob.matrix_world@q.co for q in group),Vector())/len(group)
    local=oldrot.inverted()@(center-old)
    # Bench pieces are boxes; exclude nearby cylindrical lantern poles and bases.
    if len(group)==8 and abs(local.x)<.70 and abs(local.y)<.36 and .0<local.z<.95:
        chosen.update(group);groups+=1
if not chosen:raise RuntimeError('Marked promenade bench was not found')
verts=list(chosen);index={v:i for i,v in enumerate(verts)}
faces=[f for f in bm.faces if all(v in chosen for v in f.verts)]
mesh=bpy.data.meshes.new('Relocated mill courtyard bench')
mesh.from_pydata([target+newrot@oldrot.inverted()@(ob.matrix_world@v.co-old) for v in verts],[],[[index[v] for v in f.verts] for f in faces])
for mat in ob.data.materials:mesh.materials.append(mat)
for polygon,face in zip(mesh.polygons,faces):polygon.material_index=face.material_index
mesh.update();bench=bpy.data.objects.new('Mill courtyard • bench moved to marked right-side position',mesh)
root=bpy.data.collections.new('20 • Mill sign and marked bench correction');scene.collection.children.link(root);root.objects.link(bench)
mod=bench.modifiers.new('Soft timber edges','BEVEL');mod.width=.01;mod.segments=2
bmesh.ops.delete(bm,geom=list(chosen),context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.update()
cols={'seat':root};P=Build('Mill courtyard • paved bench recess off the walking route','seat')
for i in range(3):
    for j in range(7):P.box((11.76+i*.25,-7.11+j*.25,-.535),(.243,.243,.07),'paverLight' if (i+j)%3 else 'paver')
P.finish(.008)
for obj in [sign,ob,bench]+list(root.objects):
    if obj.type!='MESH':continue
    normals=bmesh.new();normals.from_mesh(obj.data);bmesh.ops.recalc_face_normals(normals,faces=list(normals.faces));normals.to_mesh(obj.data);normals.free();obj.data.update()
# Verify the relocated seat is clear of all three nearby houses.
from mathutils.bvhtree import BVHTree
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
collisions={o.name:len(tree(bench).overlap(tree(o))) for o in scene.objects if o.type=='MESH' and (o.name.startswith(('06 •','07 •','08 •')) or '• 06 •' in o.name)}
if any(collisions.values()):raise RuntimeError('Bench intersects a house: '+str(collisions))
print('Removed bench components:',groups,'house intersection checks:',collisions)
scene.camera=next(o for o in scene.objects if o.type=='CAMERA' and o.name.startswith('Camera • accessible mill courtyard'))
folder=os.path.join(OUT,'renders','v12');os.makedirs(folder,exist_ok=True)
scene.render.filepath=os.path.join(folder,'01_mill_sign_and_bench.png');scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.cycles.samples=40
scene['Revision']='V12 • mill sign hardware attached to relocated house; marked bench moved into right-side paved recess'
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'));report.update({'revision':12,'previous_version':'versions/Crystalbrook_Village_v11.blend','latest_preview':'renders/v12/01_mill_sign_and_bench.png','sign_and_bench_fix':['Moved floating old mill sign hardware to the relocated house','Removed old mill pottery and sack remnants','Moved the existing front bench to the marked right-side position','Added a paved seating recess clear of the main path'],'bench_house_intersections':collisions,'objects':len(scene.objects)})
with open(p,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
reference=r'C:\Users\User\OneDrive\Pictures\Screenshots 1\Screenshot 2026-10-19 135345.png'
if os.path.isfile(reference):shutil.copy2(reference,os.path.join(OUT,'references','marked_mill_sign_and_bench.png'))
for o in scene.objects:o.select_set(False)
bench.select_set(True);bpy.context.view_layer.objects.active=bench
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
if bpy.app.background:bpy.ops.render.render(write_still=True)
print('V12 saved and rendered')
