"""Replace the bare stair-side grass seam with connected paving and a low stone flower bed."""
import bpy,bmesh,ast,os,math,random,json,shutil
from mathutils import Vector,Matrix
from math import sin,cos,pi
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village');source=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v7.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
for filename,names in [('build_village.py',{'Build'}),('widen_garden_terrace_v7.py',{'parts'})]:
    for node in ast.parse(open(os.path.join(source,filename),encoding='utf-8').read()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
        if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
for ob in scene.objects:
    if ob.name.startswith('Wide garden • long timber flower beds'):
        parts(ob,lambda p:p.x<11.10)
    if ob.name.startswith('Wide garden • border flowers and cascading ivy'):
        parts(ob,lambda p:9.55<p.x<11.1 and 3.50<p.y<4.30 and p.z>2.13)
root=bpy.data.collections.new('16 • House stair garden connection');scene.collection.children.link(root)
cols={}
for name in ['Stair garden • connected paving','Stair garden • low stone flower bed','Stair garden • flowers and shrubs']:
    col=bpy.data.collections.new(name);root.children.link(col);cols[name]=col
random.seed(812);Z=1.978
def slab(B,pts,z,thick,mat):
    if len(pts)<3:return
    n=len(pts);v=[(p[0],p[1],h) for h in [z-thick,z] for p in pts]
    B.add(v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
outline=[(9.13,2.58),(9.58,2.48),(10.65,2.55),(10.84,3.20),(10.40,3.48),(9.13,3.48)]
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
P=Build('Stair garden • flagstones joining house landing to curved path',list(cols)[0]);slab(P,outline,Z-.048,.14,'grout')
for row in range(4):
    y=2.46+row*.26
    for i in range(6):
        x=9.0+i*.34+(row%2)*.17
        pts=clipped([(x+.004,y+.004),(x+.332,y+.004),(x+.332,y+.252),(x+.004,y+.252)])
        slab(P,pts,Z,.048,random.choice(['paverLight','paverLight','paver']))
P.finish(.008)
# The planting sits behind the walking route, below the tree and beside the house stairs.
B=Build('Stair garden • low warm stone planter border',list(cols)[1])
bed=[(9.43,3.47),(10.38,3.47),(10.72,3.76),(10.72,4.17),(9.43,4.17)]
slab(B,bed,2.12,.22,'stone')
inner=[(9.53,3.57),(10.34,3.57),(10.62,3.81),(10.62,4.07),(9.53,4.07)]
slab(B,inner,2.145,.035,'moss')
for a,b in zip(bed,bed[1:]+bed[:1]):
    a,b=Vector((*a,0)),Vector((*b,0));d=b-a;N=max(1,math.ceil(d.length/.28));rot=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z')
    for i in range(N):
        q=a+d*(i+.5)/N;B.box((q.x,q.y,2.12),(d.length/N-.008,.12,.20),random.choice(['stone','paver','paverLight']),rot)
B.finish(.012)
G=Build('Stair garden • lush shrubs with pink white and yellow flowers',list(cols)[2])
def plant(p,s=1):
    p=Vector(p)
    for j in range(8):
        a=j*2.4;r=random.uniform(.02,.14)*s
        G.ico(p+Vector((r*cos(a),r*sin(a),random.uniform(.06,.18)*s)),(.14*s,.12*s,.105*s),random.choice(['leaf','leafLight','leafDark']))
def flower(p,color):
    p=Vector(p);G.beam(p,p+Vector((0,0,.19)),.009,'leaf',False)
    for j in range(5):
        a=j*2*pi/5;G.ico(p+Vector((.04*cos(a),.04*sin(a),.21)),(.045,.042,.026),color)
    G.ico(p+Vector((0,0,.22)),(.023,.023,.018),'flowerYellow')
for j in range(65):
    x=random.uniform(9.56,10.57);y=random.uniform(3.59,4.03)
    if x>10.33 and y<3.63+(x-10.33)*.85:continue
    p=Vector((x,y,2.15));plant(p,random.uniform(.8,1.15))
    if j%2==0:flower(p+Vector((0,0,.14)),random.choice(['flowerPink','flowerPink','flowerWhite','flowerYellow']))
G.finish()
for col in root.children:
    for ob in col.objects:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
folder=os.path.join(OUT,'renders','v8');os.makedirs(folder,exist_ok=True)
scene.render.filepath=os.path.join(folder,'01_stairside_garden_fix.png');scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.cycles.samples=40
scene['Revision']='V8 • paved house stair connection and low stone flower bed beside garden lantern'
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'));report.update({'revision':8,'previous_version':'versions/Crystalbrook_Village_v7.blend','latest_preview':'renders/v8/01_stairside_garden_fix.png','stairside_garden_v8':['Paved the bare grass gap between house stairs and garden path','Replaced the left timber box with a low stone flower bed','Added dense pink white and yellow flowers below the trees','Kept the lantern base and bench approach clear'],'objects':len(scene.objects)})
with open(p,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
for filename,dest in [('codex-clipboard-e578d6ac-5e3e-4b82-a26a-0f965f22976b.png','stairside_garden_before.png'),('codex-clipboard-dbbf3a5c-a6fa-4569-8f62-f2cf943781c9.png','stairside_garden_reference.png')]:
    p=os.path.join(os.environ['TEMP'],filename)
    if os.path.isfile(p):shutil.copy2(p,os.path.join(OUT,'references',dest))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V8 stair-side paving and stone flower bed saved')
