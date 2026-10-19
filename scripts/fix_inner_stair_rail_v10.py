"""Replace the crowded inner stair corner with one clean continuous timber return."""
import bpy,bmesh,ast,os,math,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village');source=os.path.dirname(os.path.abspath(__file__));scene=bpy.context.scene
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v9.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
for filename,names in [('build_village.py',{'Build'}),('widen_garden_terrace_v7.py',{'parts'})]:
    for node in ast.parse(open(os.path.join(source,filename),encoding='utf-8').read()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
A=Vector((12.9,3.05,1.96));E=Vector((14.2,2.85,1));F=Vector((14.25,2.15,1));B=Vector((13.65,.3,-.425))
d1=Vector((1.3,-.2,0)).normalized();s1=Vector((-d1.y,d1.x,0));d2=Vector((-.6,-1.85,0)).normalized();s2=Vector((-d2.y,d2.x,0))
a=A-s1*.83;e=E-s1*.83;f=F-s2*.83;b=B-s2*.83
def near(p,u,v,tolerance=.15):
    delta=v-u;delta.z=0;q=p-u;q.z=0;t=q.dot(delta)/delta.length_squared
    return -.08<t<1.08 and (q-delta*t).length<tolerance
for ob in scene.objects:
    if ob.name.startswith('Reference stairs • continuous side handrails'):
        parts(ob,lambda p:near(p,a,e) or near(p,f,b))
    if ob.name.startswith('Stair landing • aligned corner posts and continuous handrails'):
        parts(ob,lambda p:near(p,e,f,.12))
root=bpy.data.collections.new('18 • Clean inner stair handrail');scene.collection.children.link(root)
cols={'rail':root}
R=Build('Stair corner • single post and continuous inner handrail','rail')
corner=Vector((13.84,2.14,1.03))
points=[a,a+(e-a)*.45,corner,f+(b-f)*.38,b]
for p in points:
    R.box(p+Vector((0,0,.39)),(.115,.115,.78),'woodLight')
    R.cyl(p+Vector((0,0,.80)),.082,.065,'plank',6)
for p,q in zip(points,points[1:]):
    for height in [.24,.65]:R.beam(p+Vector((0,0,height)),q+Vector((0,0,height)),.075,'plank')
ob=R.finish(.012);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
scene['Revision']='V10 • removed crowded inner stair posts and rebuilt a continuous single-corner handrail'
folder=os.path.join(OUT,'renders','v10');os.makedirs(folder,exist_ok=True)
scene.camera=next(o for o in scene.objects if o.type=='CAMERA' and o.name.startswith('Camera • repaired middle stair landing'))
scene.render.filepath=os.path.join(folder,'01_clean_inner_stair_corner.png');scene.render.resolution_x=1050;scene.render.resolution_y=1050;scene.cycles.samples=32
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'));report.update({'revision':10,'previous_version':'versions/Crystalbrook_Village_v9.blend','latest_preview':'renders/v10/01_clean_inner_stair_corner.png','inner_rail_fix':['Removed redundant clustered inner flight-end posts','Replaced overlapping return rails with a single corner post','Continuous upper and lower inner handrail with spaced supports'],'objects':len(scene.objects)})
with open(p,'w',encoding='utf-8') as h:json.dump(report,h,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V10 marked inner stair railing corrected')
