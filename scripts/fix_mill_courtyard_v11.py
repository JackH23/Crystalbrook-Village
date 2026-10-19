"""Separate the mill from neighbouring cottages and provide two usable access routes."""
import bpy,bmesh,ast,os,math,random,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village');source=os.path.dirname(os.path.abspath(__file__));scene=bpy.context.scene
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v10.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
for filename,names in [('build_village.py',{'Build'}),('widen_garden_terrace_v7.py',{'parts'}),('fix_reference_stairs_v5.py',{'polygon_slab'})]:
    for node in ast.parse(open(os.path.join(source,filename),encoding='utf-8').read()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
delta=Vector((1.5,-.2,-1.75))
for ob in scene.objects:
    if '06 • Little mill house' in ob.name or ob.name.startswith('Shop sign • RIVER MILL'):ob.location+=delta
def court(p):return 8.40<p.x<11.70 and -9.05<p.y<-5.25
for ob in scene.objects:
    if ob.type!='MESH':continue
    if ob.name.startswith('Terrain • carved'):
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            if court(p):v.co.z=min(v.co.z,-.65)
        ob.data.update()
    if ob.name.startswith(('Cliffs • fractured','Gardens • leafy shrubs','Railings • garden boundaries','River • shoreline')):
        parts(ob,lambda p:court(p) and p.z>-.60)
    if ob.name.startswith(('Trees • visible branching','Trees • layered individual')):
        parts(ob,lambda p:Vector((-2.6,-1.3,0)) if (p.x-10.6)**2+(p.y+5.4)**2<.90**2 and p.y<-4.65 else False)
    if ob.name.startswith('Lanterns • paths'):
        parts(ob,lambda p:9.9<p.x<11.5 and -5.65<p.y<-3.45)
root=bpy.data.collections.new('19 • Accessible mill house courtyard');scene.collection.children.link(root)
cols={}
for name in ['Mill court • terrain and retaining walls','Mill court • paving and access stairs','Mill court • railings and lamps','Mill court • gardens']:
    c=bpy.data.collections.new(name);root.children.link(c);cols[name]=c
random.seed(1127);GROUND=-.65;WALK=-.50
T=Build('Mill courtyard • widened lower garden platform',list(cols)[0])
outline=[(8.45,-8.20),(9.08,-9.05),(11.60,-9.05),(11.90,-8.40),(11.90,-5.45),(11.45,-4.90),(10.65,-5.20),(8.45,-5.50)]
polygon_slab(T,outline,GROUND,.23,'grass');T.finish(.02)
R=Build('Mill courtyard • garden retaining walls and planted ledges',list(cols)[0])
for a,b,top in [((8.38,-8.10),(8.38,-5.60),1.10),((8.38,-5.60),(10.30,-5.25),1.05)]:
    a,b=Vector((*a,0)),Vector((*b,0));d=b-a;N=math.ceil(d.length/.34);rot=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z')
    for i in range(N):
        p=a+d*(i+.5)/N
        for j in range(5):R.box((p.x,p.y,-.48+j*.31),(d.length/N-.01,.28,.29),random.choice(['rock','rockLight','stone']),rot)
        R.box((p.x,p.y,top),(d.length/N-.008,.37,.10),'stone',rot)
R.finish(.018)
P=Build('Mill courtyard • connected front door and perimeter flagstones',list(cols)[1])
paths=[]
def path(points,width):
    for aa,bb in zip(points,points[1:]):paths.append((Vector(aa),Vector(bb),width))
# Door apron leads to a generous front court and then the existing lower loop.
path([(9.87,-8.18,WALK),(9.87,-8.65,WALK),(11.13,-8.65,WALK)],1.05)
path([(11.13,-8.65,WALK),(11.23,-7.15,WALK),(11.23,-5.65,WALK),(10.27,-5.05,WALK)],.90)
path([(11.13,-8.65,WALK),(11.70,-8.65,WALK)],1.0)
for j in range(20):
    for i in range(13):
        x=9.04+i*.24+(j%2)*.12;y=-9.02+j*.24;p=Vector((x,y,WALK));inside=False
        for aa,bb,w in paths:
            dd=bb-aa;t=max(0,min(1,(p-aa).dot(dd)/dd.length_squared))
            if (p-aa-dd*t).length<w/2:inside=True
        if inside:P.box((x,y,WALK-.035),(.232,.232,.07),random.choice(['paver','paverLight']))
P.finish(.01)
S=Build('Mill courtyard • stairs to upper timber bridge',list(cols)[1]);H=Build('Mill courtyard • matching stair handrails',list(cols)[2])
a=Vector((9.90,-3.50,1.24));b=Vector((10.27,-5.05,WALK));d=b-a;L=math.hypot(d.x,d.y);side=Vector((-d.y,d.x,0)).normalized();rot=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z');width=1.05;N=12
for i in range(N):
    p=a+d*(i+.5)/N;z=a.z+d.z*(i+1)/N
    S.box((p.x,p.y,(z-.895)/2),(L/N+.005,width,z+.745),'stone',rot)
    S.box((p.x,p.y,z-.035),(L/N-.007,width+.02,.07),'paverLight',rot)
for sign in [-1,1]:
    for t in [0,.33,.67,1]:
        p=a+d*t+side*sign*(width/2+.055);H.box(p+Vector((0,0,.38)),(.105,.105,.76),'woodLight');H.cyl(p+Vector((0,0,.78)),.08,.065,'plank',6)
    for z in [.22,.64]:H.beam(a+side*sign*(width/2+.055)+Vector((0,0,z)),b+side*sign*(width/2+.055)+Vector((0,0,z)),.075,'plank')
S.finish(.012);H.finish(.012)
def corridor(p):
    q=p-a;q.z=0;flat=Vector((d.x,d.y,0));t=q.dot(flat)/flat.length_squared
    return -.04<t<1.05 and (q-flat*t).length<.77
for ob in scene.objects:
    if ob.type!='MESH':continue
    if ob.name.startswith('Terrain • carved'):
        for vert in ob.data.vertices:
            p=ob.matrix_world@vert.co
            if corridor(p):
                flat=Vector((d.x,d.y,0));t=max(0,min(1,Vector((p.x-a.x,p.y-a.y,0)).dot(flat)/flat.length_squared))
                vert.co.z=min(vert.co.z,a.z+d.z*t-.16)
        ob.data.update()
    if ob.name.startswith(('Railings • garden','Cliffs • fractured','Gardens • leafy','Lanterns • paths')):parts(ob,corridor)
    if ob.name.startswith(('Trees • visible branching','Trees • branch whorls')):
        parts(ob,lambda p:(p.x-10.8)**2+(p.y+4.1)**2<1.1**2 and p.z>1.0)
# Remove fences that would close the new upper and lower approaches.
for ob in scene.objects:
    if ob.type=='MESH' and ob.name.startswith(('Railings • garden','Expansion • timber','Pool terrace • curved timber')):
        parts(ob,lambda p:10.00<p.x<11.8 and -5.55<p.y<-3.25 and p.z<2.1)
G=Build('Mill courtyard • retaining wall flowers and low shrubs',list(cols)[3])
for k in range(50):
    if k<30:x,y=8.39,random.uniform(-7.9,-5.7);z=1.16
    else:x,y=random.uniform(8.55,10.2),-5.27;z=1.12
    for j in range(5):
        aa=j*2.4;G.ico((x+.12*cos(aa),y+.12*sin(aa),z+.06),(.15,.13,.10),random.choice(['leaf','leafLight']))
    if k%3==0:
        for j in range(5):
            aa=j*2*pi/5;G.ico((x+.04*cos(aa),y+.04*sin(aa),z+.22),(.045,.04,.025),random.choice(['flowerWhite','flowerPink','flowerYellow']))
G.finish()
for col in root.children:
    for ob in col.objects:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
data=bpy.data.cameras.new('Camera • accessible mill courtyard');data.type='ORTHO';data.ortho_scale=12.0
cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);target=Vector((9.2,-6.35,.60));cam.location=target+Vector((16,-23,22));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
folder=os.path.join(OUT,'renders','v11');os.makedirs(folder,exist_ok=True);scene.render.filepath=os.path.join(folder,'01_mill_courtyard.png');scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.cycles.samples=40
scene['Revision']='V11 • separated mill house, wider lower courtyard, connected front access and stairs to upper bridge'
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'));report.update({'revision':11,'previous_version':'versions/Crystalbrook_Village_v10.blend','latest_preview':'renders/v11/01_mill_courtyard.png','mill_courtyard_fix':['Moved mill east and down onto a wider lower courtyard','Removed intersection with neighbouring garden cottage','Connected front door to existing lower perimeter path','Added matching stairs to upper timber bridge','Replaced old cramped cliff with garden retaining walls'],'objects':len(scene.objects)})
with open(p,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V11 accessible mill courtyard saved')
