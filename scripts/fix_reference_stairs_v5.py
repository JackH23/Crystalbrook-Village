"""Correct the reference stair/dock connection, removing the circular landing."""
import bpy,bmesh,math,os,ast,random,json
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
SOURCE_DIR=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v4.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
materials={m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
M={m.name.split('.00')[0]:m for m in materials};M['lamp']=M['Lantern • warm amber'];M['water']=M['Turquoise river']
for node in ast.parse(open(os.path.join(SOURCE_DIR,'build_village.py'),encoding='utf-8').read()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
    if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in ['Build','ring']:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
root=bpy.data.collections.new('13 • Reference stair and dock connection');scene.collection.children.link(root)
cols={}
for name in ['Stair fix • stone flights and landing','Stair fix • wood rails and dock','Stair fix • planting and lanterns']:
    col=bpy.data.collections.new(name);root.children.link(col);cols[name]=col
random.seed(506)

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

A=Vector((12.90,3.05,1.96));E=Vector((14.20,2.85,1.00))
F=Vector((14.25,2.15,1.00));B=Vector((13.65,.30,-.425));W=1.55
D1=Vector((E.x-A.x,E.y-A.y,0)).normalized();S1=Vector((-D1.y,D1.x,0))
D2=Vector((B.x-F.x,B.y-F.y,0)).normalized();S2=Vector((-D2.y,D2.x,0))

def distance_to_first_flight(p):
    d=E-A;den=d.x*d.x+d.y*d.y;t=((p.x-A.x)*d.x+(p.y-A.y)*d.y)/den
    dist=math.hypot(p.x-A.x-t*d.x,p.y-A.y-t*d.y)
    return -.08<t<1.1 and dist<W/2+.15

for ob in list(scene.objects):
    if ob.type!='MESH':continue
    if ob.name.startswith(('Pool terrace • broad stair flights','Pool terrace • stair handrails','Expansion • creek garden footbridge','Expansion • lower wooden dock','Expansion • small moored rowboat','Expansion • curved lower promenade 2')):
        bpy.data.objects.remove(ob,do_unlink=True);continue
    if ob.name.startswith('Pool terrace • planted cliff'):
        erase_parts(ob,lambda p:p.x>12.50 and distance_to_first_flight(p))
    if ob.name.startswith('Pool terrace • curved timber railings'):
        # Remove the last outside posts/rails across the stair approach.
        erase_parts(ob,lambda p:p.x>12.25 and p.y>1.70)
    if ob.name.startswith('Pool terrace • warm reference lanterns'):
        erase_parts(ob,lambda p:p.x>12.70 and p.y>.8)
    if ob.name.startswith('Pool terrace • benches and timber flower boxes'):
        erase_parts(ob,lambda p:p.x>11.8 and 1.40<p.y<2.75 and p.z>2.02)

def polygon_slab(builder,points,top,thickness,material):
    points=[Vector((p[0],p[1],top)) for p in points];n=len(points)
    v=[p-Vector((0,0,thickness)) for p in points]+points
    builder.add(v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],material)

def hull(points):
    pts=sorted(set((float(p[0]),float(p[1])) for p in points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]
    for p in pts:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
        lower.append(p)
    upper=[]
    for p in reversed(pts):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]

ST=Build('Reference stairs • two aligned stone flights','Stair fix • stone flights and landing')
RAIL=Build('Reference stairs • continuous side handrails','Stair fix • wood rails and dock')
def flight(a,b,width,N):
    d=b-a;L=math.hypot(d.x,d.y);R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z');side=Vector((-d.y,d.x,0)).normalized()
    for i in range(N):
        p=a+d*(i+.5)/N;walk=a.z+(b.z-a.z)*(i+1)/N
        bottom=-.78;top=walk-.09
        ST.box((p.x,p.y,(top+bottom)/2),(L/N+.012,width,top-bottom),'stone',R)
        ST.box((p.x,p.y,walk-.045),(L/N-.008,width+.035,.09),'paverLight',R)
    for sign in [-1,1]:
        for j in range(5):
            t=j/4;p=a+d*t+side*sign*(width/2+.055)
            RAIL.box(p+Vector((0,0,.38)),(.11,.11,.76),'woodLight')
            RAIL.cyl(p+Vector((0,0,.78)),.083,.07,'plank',6)
        for z in [.22,.64]:RAIL.beam(a+side*sign*(width/2+.055)+Vector((0,0,z)),b+side*sign*(width/2+.055)+Vector((0,0,z)),.075,'plank')
flight(A,E,W,7);flight(F,B,W,10)

# A stone entrance extends the existing terrace to the first tread.
entry_left=A+S1*W/2;entry_right=A-S1*W/2
entry_polygon=hull([(11.25,2.45),(11.5,3.30),tuple(entry_left),tuple(entry_right)])
polygon_slab(ST,entry_polygon,A.z,.18,'paverLight')

# The landing is a compact chamfered polygon, replacing the oversized round disk.
entry_l=E+S1*W/2;entry_r=E-S1*W/2;exit_l=F+S2*W/2;exit_r=F-S2*W/2
landing=hull([tuple(entry_l),tuple(entry_r),tuple(exit_l),tuple(exit_r),(14.98,3.40),(15.02,2.65)])
polygon_slab(ST,landing,1.008,.17,'paverLight')
polygon_slab(ST,landing,.83,1.55,'rockLight')
# A few paving seams keep the landing visually consistent with the steps.
for x in [13.95,14.30,14.65]:ST.box((x,2.90,1.012),(.018,.72,.008),'paverDark')
ST.finish(.024)

# Rail the exposed landing edge; keep the two flight mouths completely open.
for a,b in [((14.32,3.65,1.01),(14.98,3.40,1.01)),((14.98,3.40,1.01),(15.02,2.65,1.01)),((15.02,2.65,1.01),(14.99,1.91,1.01))]:
    a,b=Vector(a),Vector(b)
    for p in [a,b]:RAIL.box(p+Vector((0,0,.38)),(.11,.11,.76),'woodLight')
    for z in [.22,.64]:RAIL.beam(a+Vector((0,0,z)),b+Vector((0,0,z)),.075,'plank')
# Short safety fence on the outside of the new upper entrance.
for a,b in [((11.50,3.30,1.96),tuple(entry_left))]:
    a,b=Vector(a),Vector(b)
    for p in [a,b]:RAIL.box(p+Vector((0,0,.38)),(.11,.11,.76),'woodLight')
    for z in [.22,.64]:RAIL.beam(a+Vector((0,0,z)),b+Vector((0,0,z)),.075,'plank')
RAIL.finish(.014)

# A single level timber platform joins the lower path and the stair foot.
DK=Build('Reference dock • continuous wooden platform','Stair fix • wood rails and dock')
left=B-S2*W/2;right=B+S2*W/2
x0,x1=12.85,14.45;y0=-1.35;top=-.425
def north_y(x):
    t=(x-left.x)/(right.x-left.x);return left.y+(right.y-left.y)*t
for i in range(14):
    xa=x0+i*(x1-x0)/14+.005;xb=x0+(i+1)*(x1-x0)/14-.005
    na=north_y(xa);nb=north_y(xb)
    DK.add([(xa,y0,top-.12),(xb,y0,top-.12),(xb,nb,top-.12),(xa,na,top-.12),(xa,y0,top),(xb,y0,top),(xb,nb,top),(xa,na,top)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'plank')
for xx in [x0+.07,x1-.07]:
    ny=north_y(xx)
    for yy in [y0+.08,ny-.08]:
        DK.cyl((xx,yy,-.91),.095,1.2,'wood',10)
        DK.cyl((xx,yy,top+.12),.12,.08,'plank',10)
    for yy in [y0+.04,ny-.04]:DK.box((xx,yy,top+.38),(.11,.11,.76),'woodLight')
    for zz in [top+.23,top+.65]:DK.beam((xx,y0+.04,zz),(xx,ny-.04,zz),.075,'plank')
    DK.beam((xx,y0,top-.18),(xx,ny,top-.18),.14,'wood')
# Small front rail returns leave the lower promenade's central entrance open.
for xa,xb in [(x0,x0+.19),(x1-.19,x1)]:
    for z in [top+.23,top+.65]:DK.beam((xa,y0,z),(xb,y0,z),.075,'plank')
DK.finish(.014)

G=Build('Reference stairs • rock buttress and border planting','Stair fix • planting and lanterns')
# The landing is visibly supported by rock rather than a floating cylindrical column.
for x,y in [(14.90,3.25),(15.02,2.60),(14.82,2.0)]:
    for j in range(3):G.ico((x,y,.52-j*.57),(.42,.39,.58),random.choice(['rock','rockLight']))
for x,y,z in [(12.55,3.75,1.96),(14.75,3.45,1.02),(14.92,1.92,1.02),(14.30,.98,.05),(12.82,.72,-.30),(14.55,-1.0,-.55)]:
    for k in range(15):
        a=k*2.4;r=random.uniform(.04,.24)
        p=Vector((x+r*cos(a),y+r*sin(a),z+random.uniform(.04,.20)))
        G.ico(p,(.15,.14,.10),random.choice(['leaf','leafLight','moss']))
        if k%4==0:
            for j in range(5):
                aa=j*2*pi/5;G.ico(p+Vector((.035*cos(aa),.035*sin(aa),.10)),(.04,.04,.025),random.choice(['flowerWhite','flowerYellow','flowerPink']))
    for j in range(5):G.ico((x+.025*sin(j),y,z-.13*j),(.10,.09,.07),'leaf')
G.finish(.008)

L=Build('Reference stairs • lanterns beside the walking route','Stair fix • planting and lanterns')
for x,y,z in [(14.78,3.12,1.012),(14.36,-1.27,top),(12.91,.44,top)]:
    L.cyl((x,y,z+.055),.13,.11,'iron',10);L.cyl((x,y,z+.63),.042,1.15,'iron',8)
    L.box((x,y,z+1.31),(.18,.18,.30),'lamp')
    for xx in [-.1,.1]:
        for yy in [-.1,.1]:L.box((x+xx,y+yy,z+1.31),(.023,.023,.34),'iron')
    L.cyl((x,y,z+1.53),.17,.18,'iron',4,r2=.015)
L.finish(.008)

for col in root.children:
    for ob in col.objects:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()

camera_data=bpy.data.cameras.new('Camera • reference stair connection');camera_data.type='ORTHO';camera_data.ortho_scale=10.8
camera=bpy.data.objects.new(camera_data.name,camera_data);scene.collection.objects.link(camera)
target=Vector((12.55,1.0,.65));camera.location=target+Vector((20,-11,19));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera=camera;scene.render.resolution_x=1450;scene.render.resolution_y=1450;scene.cycles.samples=64
os.makedirs(os.path.join(OUT,'renders','v5'),exist_ok=True);scene.render.filepath=os.path.join(OUT,'renders','v5','03_reference_stairs.png')
scene['Revision']='V5 • continuous two-flight reference stairs, angled landing, open access and joined dock'
manifest=os.path.join(OUT,'project_manifest.json');report=json.load(open(manifest,encoding='utf-8'))
report.update({'revision':5,'previous_version':'versions/Crystalbrook_Village_v4.blend','objects':len(scene.objects),'saved_cameras':sum(o.type=='CAMERA' for o in scene.objects),'stair_fix':['Removed circular landing and overlapping stair geometry','Moved stair entrance outside terrace edge','Two uniform-width flights with matched elevations','Chamfered stone landing with exterior lantern','Continuous timber dock joining the stairs to the lower path','Open rail entrances and planted rock supports']})
with open(manifest,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('Reference stair and dock correction saved')
