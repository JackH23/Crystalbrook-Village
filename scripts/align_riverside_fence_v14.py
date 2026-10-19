"""Align the south riverside timber fence to the actual stone promenade edge."""
import bpy,bmesh,ast,os,math,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village');source=os.path.dirname(os.path.abspath(__file__));scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v13.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
for filename,names in [('build_village.py',{'Build'}),('widen_garden_terrace_v7.py',{'parts'})]:
    for node in ast.parse(open(os.path.join(source,filename),encoding='utf-8').read()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helper','exec'))
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'helper','exec'))
old=next(o for o in scene.objects if o.name.startswith('Railings • garden boundaries'))
parts(old,lambda p:3.5<p.x<8.7 and -9.9<p.y<-6.0 and p.z>.95)
root=bpy.data.collections.get('21 • Aligned riverside walkway fence')
if root:
    for ob in list(root.objects):bpy.data.objects.remove(ob,do_unlink=True)
else:
    root=bpy.data.collections.new('21 • Aligned riverside walkway fence');scene.collection.children.link(root)
cols={'fence':root};F=Build('Riverside walkway • fence aligned to stone path edge','fence');C=Build('Riverside walkway • stone curb beneath fence posts','fence')
# These points follow the river-facing edge of Route • entrance and south river promenade.
points=[Vector((3.72,-8.39,1.11)),Vector((6.43,-7.69,1.24)),Vector((7.96,-7.35,1.24))]
posts=[]
for a,b in zip(points,points[1:]):
    n=max(1,math.ceil((b-a).length/.80))
    for i in range(n):posts.append(a+(b-a)*i/n)
posts.append(points[-1])
for p in posts:
    C.box(p-Vector((0,0,.055)),(.22,.22,.11),'stone')
    F.box(p+Vector((0,0,.39)),(.11,.11,.78),'woodLight');F.cyl(p+Vector((0,0,.80)),.083,.07,'plank',6)
for a,b in zip(posts,posts[1:]):
    for h in [.24,.65]:F.beam(a+Vector((0,0,h)),b+Vector((0,0,h)),.075,'plank')
fence=F.finish(.014);C.finish(.01)
for ob in [old]+list(root.objects):
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
scene['Revision']='V14 • riverside fence realigned to the stone promenade border with seated posts and connected rails'
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'));report.update({'revision':14,'previous_version':'versions/Crystalbrook_Village_v13.blend','riverside_fence_fix':['Replaced the old island-outline fence beside the south river path','Aligned the replacement fence with the river-facing paving border','Removed duplicate joint posts and connected each rail span','Seated the posts on stone curb pads'],'riverside_fence_posts':len(posts)})
with open(p,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
for o in scene.objects:o.select_set(False)
fence.select_set(True);bpy.context.view_layer.objects.active=fence
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('Riverside fence aligned with the promenade; posts:',len(posts))
