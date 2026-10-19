"""Replace the tight round landing with the broad curved reference garden terrace."""
import bpy,bmesh,ast,os,math,random,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
scene=bpy.context.scene
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
SOURCE_DIR=os.path.dirname(os.path.abspath(__file__))
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v6.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
M['lamp']=next(m for m in bpy.data.materials if m.name.startswith('Garden lantern • golden glow'))
for node in ast.parse(open(os.path.join(SOURCE_DIR,'build_village.py'),encoding='utf-8').read()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
    if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name=='Build':exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
def parts(ob,action):
    bm=bmesh.new();bm.from_mesh(ob.data);seen=set();delete=[]
    for v in bm.verts:
        if v in seen:continue
        stack=[v];seen.add(v);group=[]
        while stack:
            q=stack.pop();group.append(q)
            for e in q.link_edges:
                r=e.other_vert(q)
                if r not in seen:seen.add(r);stack.append(r)
        p=sum((ob.matrix_world@q.co for q in group),Vector())/len(group)
        result=action(p)
        if result is True:delete.extend(group)
        elif isinstance(result,Vector):
            for q in group:q.co+=result
    if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
# Retain the rear tree framing; replace the narrow paving, boxes and border geometry.
for ob in list(scene.objects):
    if ob.name.startswith('Garden entrance') and not ob.name.startswith(('Garden entrance • branching rear garden tree','Garden entrance • fine lobed tree canopy')):
        bpy.data.objects.remove(ob,do_unlink=True)
root=bpy.data.collections.new('15 • Widened curved garden terrace');scene.collection.children.link(root)
cols={}
for name in ['Wide terrace • paving and rock support','Wide terrace • bench planters and railings','Wide terrace • flowers and cliff ivy','Wide terrace • lantern']:
    col=bpy.data.collections.new(name);root.children.link(col);cols[name]=col
Z=1.985;C=Vector((9.65,.95,Z));A=Vector((12.90,3.05,Z));D=Vector((1.3,-.2,0)).normalized()
def polar(r,a):return Vector((C.x+r*cos(a),C.y+r*sin(a),Z))
def domain(p):
    r=math.hypot(p.x-C.x,p.y-C.y);a=math.atan2(p.y-C.y,p.x-C.x)
    return 1.78<r<4.60 and .20<a<1.39 and (p-A).dot(D)<.05
for ob in list(scene.objects):
    if ob.type!='MESH':continue
    if ob.name.startswith(('Gardens • leafy shrubs','Pool terrace • flowers','Cliffs • fractured')):
        parts(ob,lambda p:domain(p) and p.z>1.87)
    if ob.name.startswith('Terrain • carved'):
        # This is a connected terrain grid; edit vertices, not component centroids.
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            if domain(p) and p.z>1.80:v.co.z=1.80
        ob.data.update()
    if ob.name.startswith(('Pool terrace • curved timber railings','Railings • garden boundaries','Pool terrace • benches and timber flower boxes')):
        parts(ob,lambda p:domain(p) and math.hypot(p.x-C.x,p.y-C.y)>2.04)
random.seed(741)
def clip(points):
    result=[]
    for p,q in zip(points,points[1:]+points[:1]):
        dp=(p-A).dot(D);dq=(q-A).dot(D)
        if dp<=0:result.append(p)
        if (dp<0)!=(dq<0):result.append(p+(q-p)*(dp/(dp-dq)))
    return result
def slab(B,pts,top,thick,mat):
    if len(pts)<3:return
    n=len(pts);v=[(p[0],p[1],z) for z in [top-thick,top] for p in pts]
    B.add(v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
P=Build('Wide garden • sweeping cream flagstone path',list(cols)[0])
angles=[math.radians(15+i*61/48) for i in range(49)]
outline=[polar(1.83,a) for a in angles]+[polar(4.45,a) for a in reversed(angles)]
slab(P,clip(outline),Z-.052,.20,'grout')
for row in range(9):
    r0=1.83+row*(4.45-1.83)/9;r1=r0+(4.45-1.83)/9-.008
    N=math.ceil((math.radians(61)*(r0+r1)/2)/.34)
    for i in range(N):
        a=math.radians(15+61*i/N)+.001;b=math.radians(15+61*(i+1)/N)-.001
        pts=clip([polar(r0,a),polar(r1,a),polar(r1,b),polar(r0,b)])
        slab(P,pts,Z,.052,random.choice(['paverLight','paverLight','paver']))
P.finish(.008)
R=Build('Wide garden • faceted supporting cliff ledge',list(cols)[0])
for i in range(20):
    a=math.radians(40+i*36/19);p=polar(4.45,a)
    for j in range(4):R.ico((p.x,p.y,1.58-j*.58),(.34,.30,.50),random.choice(['rock','rockLight']))
R.finish(.014)
parts(bpy.data.objects[R.name],lambda p:p.x>12.65 and p.y<3.95 and p.z>1.25)
# Border follows the outside of the terrace and meets the existing stair rail.
F=Build('Wide garden • continuous boundary railing',list(cols)[1])
left=A+Vector((.2,1.3,0)).normalized()*.83
rear=[left]+[polar(4.44,math.radians(a)) for a in [42,50,58,66,74,76]]
right=A-Vector((.2,1.3,0)).normalized()*.83
front=[Vector((12.72,1.64,Z)),right]
for path in [rear,front]:
    for p in path:
        F.box(p+Vector((0,0,.38)),(.105,.105,.76),'woodLight');F.cyl(p+Vector((0,0,.78)),.08,.065,'plank',6)
    for a,b in zip(path,path[1:]):
        for h in [.24,.64]:F.beam(a+Vector((0,0,h)),b+Vector((0,0,h)),.075,'plank')
F.finish(.012)
W=Build('Wide garden • slatted timber seating bench',list(cols)[1])
q=polar(3.55,math.radians(58));rot=Matrix.Rotation(math.radians(210),3,'Z')
for j in range(4):W.box(q+rot@Vector((0,(j-1.5)*.12,.43)),(1.55,.105,.085),'plank',rot)
for x in [-.59,.59]:
    W.box(q+rot@Vector((x,0,.22)),(.10,.40,.44),'wood',rot)
    W.box(q+rot@Vector((x,-.23,.65)),(.08,.08,.75),'woodLight',rot)
    W.box(q+rot@Vector((x,0,.69)),(.065,.58,.065),'woodLight',rot)
for j in range(3):W.box(q+rot@Vector((0,-.24,.67+j*.12)),(1.55,.07,.10),'plank',rot)
W.finish(.015)
B=Build('Wide garden • long timber flower beds',list(cols)[1]);G=Build('Wide garden • border flowers and cascading ivy',list(cols)[2])
def leafclump(p,s=1):
    p=Vector(p)
    for j in range(7):
        a=j*2.4;r=random.uniform(.03,.14)*s
        G.ico(p+Vector((r*cos(a),r*sin(a),random.uniform(.06,.18)*s)),(.13*s,.12*s,.09*s),random.choice(['leaf','leafLight','moss']))
def flower(p,mat):
    p=Vector(p);G.beam(p,p+Vector((0,0,.16)),.008,'leaf',False)
    for j in range(5):
        a=j*2*pi/5;G.ico(p+Vector((.034*cos(a),.034*sin(a),.18)),(.037,.037,.024),mat)
    G.ico(p+Vector((0,0,.193)),(.018,.018,.013),'flowerYellow')
def planter(x,y,length,angle):
    p=Vector((x,y,Z));rot=Matrix.Rotation(angle,3,'Z')
    for yy in [-.25,.25]:
        for j in range(3):B.box(p+rot@Vector((0,yy,.11+j*.09)),(length,.065,.075),'plank',rot)
    for xx in [-length/2+.04,length/2-.04]:B.box(p+rot@Vector((xx,0,.20)),(.075,.50,.34),'woodLight',rot)
    B.box(p+Vector((0,0,.325)),(length-.10,.43,.03),'moss',rot)
    for j in range(int(length*40)):
        q=p+rot@Vector((random.uniform(-length/2+.07,length/2-.07),random.uniform(-.18,.18),.35))
        leafclump(q,.80);flower(q+Vector((0,0,.1)),random.choice(['flowerWhite','flowerWhite','flowerPink','flowerYellow']))
planter(10.43,3.90,1.14,math.radians(-8))
planter(12.53,3.91,1.35,math.radians(108))
B.finish(.012)
# Low planting remains along both borders, leaving the central sweep open.
for i in range(48):
    a=math.radians(random.uniform(20,76));p=polar(1.76,a)
    if i%3==0:p=polar(4.49,math.radians(random.uniform(41,76)))
    leafclump(p,1)
    if i%2==0:flower(p+Vector((0,0,.12)),random.choice(['flowerWhite','flowerPink','flowerYellow']))
    if i%6==0:
        for j in range(10):G.ico(p+Vector((.035*sin(j*2),.02*cos(j),-.13*j)),(.12,.095,.07),random.choice(['leaf','leafLight']))
G.finish()
L=Build('Wide garden • warm lantern beside bench',list(cols)[3]);x,y=10.55,3.38
L.cyl((x,y,Z+.055),.125,.11,'iron',10);L.cyl((x,y,Z+.72),.037,1.35,'iron',8)
L.box((x,y,Z+1.48),(.18,.18,.30),'lamp')
for xx in [-.1,.1]:
    for yy in [-.1,.1]:L.box((x+xx,y+yy,Z+1.48),(.022,.022,.34),'iron')
L.cyl((x,y,Z+1.69),.17,.18,'iron',4,r2=.012);L.finish(.008)
data=bpy.data.lights.new('Wide garden • soft amber lantern light','POINT');data.energy=12;data.color=(1,.5,.15);data.shadow_soft_size=.35
light=bpy.data.objects.new(data.name,data);cols[list(cols)[3]].objects.link(light);light.location=(x,y,Z+1.42)
for col in root.children:
    for ob in col.objects:
        if ob.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
camera=next(o for o in scene.objects if o.type=='CAMERA' and o.name.startswith('Camera • curved garden entrance detail'))
target=Vector((11.6,3.1,2.0));camera.location=target+Vector((11,-7,11));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=8.6
scene.camera=camera;scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.cycles.samples=40
folder=os.path.join(OUT,'renders','v7');os.makedirs(folder,exist_ok=True);scene.render.filepath=os.path.join(folder,'01_wide_garden_terrace.png')
scene['Revision']='V7 • broad sweeping garden path, bench, long border flower beds and continuous stair approach'
reportpath=os.path.join(OUT,'project_manifest.json');report=json.load(open(reportpath,encoding='utf-8'))
report.update({'revision':7,'previous_version':'versions/Crystalbrook_Village_v6.blend','latest_preview':'renders/v7/01_wide_garden_terrace.png','garden_terrace_v7':['Replaced tight circular landing with broad curved flagstone terrace','Added slatted timber bench between long flower beds','Moved flowers and railings to the outer edge','Retained clear stair approach and pool-facing route'],'objects':len(scene.objects)})
with open(reportpath,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
source_target=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(source_target)):shutil.copy2(__file__,source_target)
reference=os.path.join(os.environ['TEMP'],'codex-clipboard-46e089f8-a9c5-4a2a-b4e3-647537208267.png')
if os.path.isfile(reference):shutil.copy2(reference,os.path.join(OUT,'references','wide_garden_before_after_reference.png'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V7 widened curved garden terrace saved')
