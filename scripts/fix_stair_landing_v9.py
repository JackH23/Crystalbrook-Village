"""Finish the eastern switchback landing with flagstones and continuous timber rails."""
import bpy,bmesh,ast,os,math,random,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village');source=os.path.dirname(os.path.abspath(__file__));scene=bpy.context.scene
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v8.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
M['lamp']=next(m for m in bpy.data.materials if m.name.startswith('Garden lantern • golden glow'))
for filename,names in [('build_village.py',{'Build'}),('widen_garden_terrace_v7.py',{'parts'}),('fix_reference_stairs_v5.py',{'hull','polygon_slab'})]:
    for node in ast.parse(open(os.path.join(source,filename),encoding='utf-8').read()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
for ob in scene.objects:
    if ob.name.startswith('Reference stairs • continuous side handrails'):
        parts(ob,lambda p:p.x>14.25 and p.y>1.80 and p.z>1.05)
    if ob.name.startswith('Reference stairs • lanterns beside the walking route'):
        parts(ob,lambda p:14.45<p.x<15.12 and 2.75<p.y<3.50)
root=bpy.data.collections.new('17 • Finished switchback stair landing');scene.collection.children.link(root)
cols={}
for name in ['Landing • irregular stone paving','Landing • connected timber railings','Landing • lantern and cliff flowers']:
    c=bpy.data.collections.new(name);root.children.link(c);cols[name]=c
E=Vector((14.20,2.85,1.00));F=Vector((14.25,2.15,1.00));D1=Vector((1.3,-.2,0)).normalized();S1=Vector((-D1.y,D1.x,0));D2=Vector((-.60,-1.85,0)).normalized();S2=Vector((-D2.y,D2.x,0));W=1.55
outline=hull([E+S1*W/2,E-S1*W/2,F+S2*W/2,F-S2*W/2,(14.98,3.40),(15.02,2.65)])
def clipped(poly):
    for a,b in zip(outline,outline[1:]+outline[:1]):
        result=[]
        def side(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
        if not poly:break
        for p,q in zip(poly,poly[1:]+poly[:1]):
            dp,dq=side(p),side(q)
            if dp>=0:result.append(p)
            if (dp<0)!=(dq<0):
                t=dp/(dp-dq);result.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
        poly=result
    return poly
random.seed(917)
P=Build('Stair landing • individual irregular flagstones',list(cols)[0])
polygon_slab(P,outline,1.017,.025,'grout')
for j in range(6):
    y=1.80+j*.34
    for i in range(6):
        x=13.38+i*.31+.155*(j%2);dx=random.uniform(-.02,.02)
        pts=clipped([(x+.005,y+.005),(x+.301,y+.005+dx),(x+.301,y+.33),(x+.005,y+.33-dx)])
        if len(pts)>2:polygon_slab(P,pts,1.03,.013,random.choice(['paver','paverLight','paverLight']))
P.finish(.005)
R=Build('Stair landing • aligned corner posts and continuous handrails',list(cols)[1])
outer=[E+S1*.83,Vector((14.98,3.40,1)),Vector((15.02,2.65,1)),F+S2*.83]
for p in outer:
    R.box(p+Vector((0,0,.39)),(.115,.115,.78),'woodLight');R.cyl(p+Vector((0,0,.80)),.082,.065,'plank',6)
for a,b in zip(outer,outer[1:]):
    for z in [.22,.64]:R.beam(a+Vector((0,0,z)),b+Vector((0,0,z)),.075,'plank')
# The short inside return meets the existing two flight-end posts.
for z in [.22,.64]:R.beam(E-S1*.83+Vector((0,0,z)),F-S2*.83+Vector((0,0,z)),.075,'plank')
R.finish(.012)
L=Build('Stair landing • warm lantern beside outer railing',list(cols)[2]);x,y,z=14.76,3.08,1.03
L.cyl((x,y,z+.05),.125,.10,'iron',10);L.cyl((x,y,z+.68),.039,1.25,'iron',8);L.box((x,y,z+1.39),(.18,.18,.30),'lamp')
for xx in [-.1,.1]:
    for yy in [-.1,.1]:L.box((x+xx,y+yy,z+1.39),(.022,.022,.34),'iron')
L.cyl((x,y,z+1.60),.17,.18,'iron',4,r2=.012);L.finish(.008)
G=Build('Stair landing • flowers and trailing cliff greenery',list(cols)[2])
for x,y in [(15.17,2.45),(14.95,3.57),(14.90,1.88)]:
    for k in range(16):
        a=k*2.4;r=random.uniform(.03,.20);p=Vector((x+r*cos(a),y+r*sin(a),1.01+random.uniform(.02,.10)))
        G.ico(p,(.13,.11,.09),random.choice(['leaf','leafLight']))
        if k%4==0:
            for j in range(5):
                aa=j*2*pi/5;G.ico(p+Vector((.035*cos(aa),.035*sin(aa),.15)),(.04,.04,.025),random.choice(['flowerWhite','flowerPink','flowerYellow']))
    for j in range(9):G.ico((x+.03*sin(j*2),y,.98-.12*j),(.11,.09,.07),'leaf')
G.finish()
for col in root.children:
    for ob in col.objects:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
data=bpy.data.cameras.new('Camera • repaired middle stair landing');data.type='ORTHO';data.ortho_scale=5.1
cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);target=Vector((14.0,2.35,1.05));cam.location=target+Vector((20,-11,19));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
folder=os.path.join(OUT,'renders','v9');os.makedirs(folder,exist_ok=True);scene.render.filepath=os.path.join(folder,'01_middle_stair_landing.png');scene.render.resolution_x=1050;scene.render.resolution_y=1050;scene.cycles.samples=32
scene['Revision']='V9 • finished middle stair landing, irregular flagstones, joined corner rails and warm lantern'
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'));report.update({'revision':9,'previous_version':'versions/Crystalbrook_Village_v8.blend','latest_preview':'renders/v9/01_middle_stair_landing.png','landing_fix_v9':['Individual flagstones on the middle landing','Aligned timber corner posts and continuous inner and outer handrails','Warm lantern beside a clear walking route','Edge flowers and trailing ivy'],'objects':len(scene.objects)})
with open(p,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V9 middle stair landing saved')
