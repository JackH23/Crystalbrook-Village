"""Open the eastern stair approach into the reference's curved flower garden."""
import bpy,bmesh,math,os,ast,random,json
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
SOURCE_DIR=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v5.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
M['lamp']=M['Lantern • warm amber']
for node in ast.parse(open(os.path.join(SOURCE_DIR,'build_village.py'),encoding='utf-8').read()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
    if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name=='Build':exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
def erase_parts(ob,predicate):
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
        if predicate(p):delete.extend(group)
    if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
for ob in list(scene.objects):
    if ob.type!='MESH':continue
    if ob.name.startswith('Reference stairs • continuous side handrails'):
        erase_parts(ob,lambda p:11.25<p.x<12.86 and 3.23<p.y<4.05)
    if ob.name.startswith(('Pool terrace • curved timber railings','Pool terrace • benches and timber flower boxes','Pool terrace • flowers, shrubs and trailing ivy','Pool terrace • warm reference lanterns')):
        erase_parts(ob,lambda p:10.55<p.x<13.20 and 2.15<p.y<4.40 and p.z>1.75)
    if ob.name.startswith('Reference stairs • rock buttress and border planting'):
        erase_parts(ob,lambda p:11.8<p.x<13.2 and 3.30<p.y<4.15)
root=bpy.data.collections.new('14 • Curved stair entrance garden');scene.collection.children.link(root)
cols={}
for name in ['Garden entrance • cream paving and cliff support','Garden entrance • timber edging and flower boxes','Garden entrance • planting and trees','Garden entrance • warm lantern']:
    c=bpy.data.collections.new(name);root.children.link(c);cols[name]=c
random.seed(619)
Z=1.982;C=Vector((11.65,3.10,Z));RX=1.55;RY=1.38
P=Build('Garden entrance • rounded hand-laid flagstone landing',list(cols)[0])
def slab(builder,points,top,thick,mat):
    n=len(points);v=[(p[0],p[1],z) for z in [top-thick,top] for p in points]
    builder.add(v,[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
edge=[(C.x+RX*cos(2*pi*i/64),C.y+RY*sin(2*pi*i/64)) for i in range(64)]
slab(P,edge,Z-.045,.19,'grout')
# Five staggered concentric courses give the curved paving a readable scale.
P.cyl((C.x,C.y,Z-.022),.13,.045,'paverLight',12)
for row in range(5):
    r0=.09+row*.182;r1=r0+.177;N=max(8,int(2*pi*(r0+r1)/2*1.45/.33))
    for i in range(N):
        a=2*pi*(i+.5*(row%2))/N;b=a+2*pi/N-.012
        pts=[(C.x+RX*r*cos(t),C.y+RY*r*sin(t)) for r,t in [(r0,a),(r1,a),(r1,b),(r0,b)]]
        slab(P,pts,Z,.045,random.choice(['paver','paverLight','paverLight']))
# The last course is a quiet continuous curb around the garden side.
for i in range(30):
    a=pi*.02+pi*.93*i/30;b=pi*.02+pi*.93*(i+1)/30-.009
    pts=[(C.x+RX*r*cos(t),C.y+RY*r*sin(t)) for r,t in [(.991,a),(1.055,a),(1.055,b),(.991,b)]]
    slab(P,pts,Z+.035,.12,'stone')
P.finish(.009)
R=Build('Garden entrance • supported irregular stone ledge',list(cols)[0])
for i in range(16):
    a=.15+2.70*i/15;x=C.x+(RX+.025)*cos(a);y=C.y+(RY+.025)*sin(a)
    for j in range(3):R.ico((x,y,1.62-j*.57),(.29,.29,.47),random.choice(['rock','rockLight']))
R.finish(.012)
T=Build('Garden entrance • curved boundary railing',list(cols)[1])
# Behind the planting, returning to the existing first-flight handrail.
rail=[(10.34,3.65),(10.57,4.10),(11.12,4.43),(11.80,4.52),(12.45,4.33),(12.87,4.05),(13.026,3.875)]
for x,y in rail:
    T.box((x,y,Z+.38),(.105,.105,.76),'woodLight');T.cyl((x,y,Z+.78),.079,.065,'plank',6)
for a,b in zip(rail,rail[1:]):
    for h in [.24,.64]:T.beam((*a,Z+h),(*b,Z+h),.075,'plank')
T.finish(.016)
B=Build('Garden entrance • paired timber flower planters',list(cols)[1])
G=Build('Garden entrance • flowers and trailing leaves',list(cols)[2])
def foliage(p,s=1):
    p=Vector(p)
    for j in range(8):
        a=j*2.4;r=random.uniform(.04,.17)*s
        G.ico(p+Vector((r*cos(a),r*sin(a),random.uniform(.05,.16)*s)),(.13*s,.12*s,.09*s),random.choice(['leaf','leafLight','moss']))
def flower(p,color):
    p=Vector(p);G.beam(p,p+Vector((0,0,.15)),.009,'leaf',False)
    for j in range(5):
        a=j*2*pi/5;G.ico(p+Vector((.031*cos(a),.031*sin(a),.17)),(.036,.036,.022),color)
    G.ico(p+Vector((0,0,.18)),(.022,.022,.018),'flowerYellow')
for x,y,angle in [(10.77,3.43,-.78),(12.46,3.88,.72)]:
    rot=Matrix.Rotation(angle,3,'Z');p=Vector((x,y,Z))
    for yy in [-.24,.24]:
        for j in range(3):B.box(p+rot@Vector((0,yy,.13+j*.105)),(1.02,.065,.09),'plank',rot)
    for xx in [-.48,.48]:B.box(p+rot@Vector((xx,0,.24)),(.075,.48,.38),'woodLight',rot)
    for xx in [-.52,.52]:B.box(p+rot@Vector((xx,0,.10)),(.10,.64,.12),'woodLight',rot)
    B.box(p+Vector((0,0,.39)),(.91,.39,.04),'moss',rot)
    for j in range(28):
        q=p+rot@Vector((random.uniform(-.43,.43),random.uniform(-.17,.17),.41))
        foliage(q,.70);flower(q+Vector((0,0,.10)),random.choice(['flowerWhite','flowerWhite','flowerPink','flowerYellow']))
B.finish(.012)
for i in range(34):
    a=random.uniform(.25,2.8);p=C+Vector(((RX+.07)*cos(a),(RY+.07)*sin(a),.02))
    foliage(p,1.10)
    if i%2==0:flower(p+Vector((0,0,.13)),random.choice(['flowerWhite','flowerPink','flowerYellow']))
    if i%3==0:
        for j in range(7):G.ico(p+Vector((.025*sin(j*2),.01*cos(j),-.13*j)),(.105,.09,.07),'leaf')
G.finish()
# A modest tree behind the garden balances the existing left-hand tree.
TR=Build('Garden entrance • branching rear garden tree',list(cols)[2])
base=Vector((11.98,4.47,Z))
TR.beam(base,base+Vector((-.08,.04,1.65)),.085,'woodLight',False)
for j in range(7):
    a=j*2.4;tip=base+Vector((.52*cos(a),.44*sin(a),1.55+.28*(j%3)))
    TR.beam(base+Vector((-.03,0,.85)),tip,.035,'wood',False)
    for k in range(8):
        aa=k*2.4;q=tip+Vector((.22*cos(aa),.18*sin(aa),random.uniform(-.12,.20)))
        TR.ico(q,(.29,.25,.17),random.choice(['leaf','leafLight','leafLight','leafDark']))
TR.finish()
L=Build('Garden entrance • amber lantern on stone base',list(cols)[3]);x,y=11.30,4.04
L.cyl((x,y,Z+.045),.125,.09,'iron',10);L.cyl((x,y,Z+.67),.037,1.25,'iron',8)
L.box((x,y,Z+1.40),(.18,.18,.29),'lamp')
for xx in [-.10,.10]:
    for yy in [-.10,.10]:L.box((x+xx,y+yy,Z+1.40),(.022,.022,.33),'iron')
L.cyl((x,y,Z+1.61),.165,.18,'iron',4,r2=.012);L.cyl((x,y,Z+1.72),.025,.05,'gold',8)
L.finish(.008)
for col in root.children:
    for ob in col.objects:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
data=bpy.data.cameras.new('Camera • curved garden entrance detail');data.type='ORTHO';data.ortho_scale=7.4
camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera)
target=Vector((11.55,3.05,2.0));camera.location=target+Vector((11,-7,11));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera=camera;scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.cycles.samples=48
os.makedirs(os.path.join(OUT,'renders','v6'),exist_ok=True)
scene.render.filepath=os.path.join(OUT,'renders','v6','01_garden_entrance.png')
scene['Revision']='V6 • curved paved garden landing with open stair approach, paired flower planters and amber lantern'
manifest=os.path.join(OUT,'project_manifest.json');report=json.load(open(manifest,encoding='utf-8'))
report.update({'revision':6,'previous_version':'versions/Crystalbrook_Village_v5.blend','objects':len(scene.objects),'saved_cameras':sum(o.type=='CAMERA' for o in scene.objects),'garden_entrance_fix':['Removed diagonal fence and plants obstructing the upper stair approach','Rounded cream flagstone garden landing','Boundary rail behind the garden returns to first stair handrail','Paired timber planters with white, pink and yellow flowers','Rear tree, warm amber lantern and trailing cliff greenery']})
with open(manifest,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V6 curved garden entrance saved')
