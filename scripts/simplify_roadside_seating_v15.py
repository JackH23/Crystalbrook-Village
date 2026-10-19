"""Replace the crossed-out circular seating court and outer bench with one roadside bench."""
import bpy,bmesh,ast,os,math,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village');source=os.path.dirname(os.path.abspath(__file__));scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v14.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
LOW=-.65;START=math.radians(-145);END=math.radians(40)
for filename,names in [('build_village.py',{'Build'}),('widen_garden_terrace_v7.py',{'parts'}),('add_marked_area_v3.py',{'old_outline','extension','pt'})]:
    for node in ast.parse(open(os.path.join(source,filename),encoding='utf-8').read()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
a=math.radians(-94);court=pt(a,old_outline(a)+1.10,LOW)
garden=next(o for o in scene.objects if o.name.startswith('Expansion • flower garden and seating court'))
parts(garden,lambda p:math.hypot(p.x-court.x,p.y-court.y)<1.45)
aa=math.radians(-103);outer=pt(aa,old_outline(aa)+extension(aa)*.80,LOW);oldrot=Matrix.Rotation(aa+pi/2,3,'Z')
promenade=next(o for o in scene.objects if o.name.startswith('Expansion • promenade lanterns and overlook benches'))
def old_bench(p):
    q=oldrot.inverted()@(p-outer)
    return abs(q.x)<.70 and abs(q.y)<.36 and 0<q.z<.95
# Only the bench boxes are removed; nearby lantern cylinders remain intact.
bm=bmesh.new();bm.from_mesh(promenade.data);seen=set();delete=[];count=0
for v in bm.verts:
    if v in seen:continue
    stack=[v];seen.add(v);group=[]
    while stack:
        q=stack.pop();group.append(q)
        for edge in q.link_edges:
            r=edge.other_vert(q)
            if r not in seen:seen.add(r);stack.append(r)
    center=sum((promenade.matrix_world@q.co for q in group),Vector())/len(group)
    if len(group)==8 and old_bench(center):delete.extend(group);count+=1
if count!=7:raise RuntimeError('Expected seven marked outer bench parts; found '+str(count))
bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(promenade.data);bm.free();promenade.data.update()
root=bpy.data.collections.new('22 • Single roadside bench');scene.collection.children.link(root);cols={'seat':root}
position=court+Vector((0,-.40,.11));rot=Matrix.Rotation(a+pi/2,3,'Z')
B=Build('Roadside • single bench beside the inner cliff','seat')
for j in range(3):B.box(position+rot@Vector((0,(j-1)*.115,.42)),(1.10,.10,.075),'plank',rot)
for xx in [-.42,.42]:
    B.box(position+rot@Vector((xx,0,.21)),(.08,.34,.42),'iron',rot)
    B.box(position+rot@Vector((xx,.24,.57)),(.065,.065,.58),'woodLight',rot)
for j in range(2):B.box(position+rot@Vector((0,.24,.70+j*.13)),(1.10,.065,.10),'plank',rot)
bench=B.finish(.012)
P=Build('Roadside • compact stone bench pad and road connection','seat')
for row in range(6):
    for i in range(5):
        p=position+rot@Vector(((i-2)*.27,.28-row*.25,-.035))
        P.box(p,(.262,.242,.07),'paverLight' if (i+row)%3 else 'paver',rot)
P.finish(.008)
for ob in [garden,promenade]+list(root.objects):
    normals=bmesh.new();normals.from_mesh(ob.data);bmesh.ops.recalc_face_normals(normals,faces=list(normals.faces));normals.to_mesh(ob.data);normals.free();ob.data.update()
scene['Revision']='V15 • marked circular seating court and outer bench removed; one bench placed beside the road at the inner cliff'
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'));report.update({'revision':15,'previous_version':'versions/Crystalbrook_Village_v14.blend','roadside_seating_fix':['Removed the two-seat circular court and surrounding marked planting','Removed the marked outer-fence bench','Added one bench at the inner roadside with a compact stone pad','Kept the main promenade and outer safety fence clear'],'new_roadside_bench_position':list(position)})
with open(p,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
reference=r'C:\Users\User\OneDrive\Pictures\Screenshots 1\Screenshot 2026-10-19 171802.png'
if os.path.isfile(reference):shutil.copy2(reference,os.path.join(OUT,'references','marked_roadside_seating_cleanup.png'))
for ob in scene.objects:ob.select_set(False)
bench.select_set(True);bpy.context.view_layer.objects.active=bench
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('Marked seating removed and one new roadside bench added:',tuple(position))
