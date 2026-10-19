"""Replace the marked narrow pool-edge walkway with the reference garden terrace."""
import bpy,bmesh,os,ast,math,random,json
from math import sin,cos,pi
from mathutils import Vector,Matrix
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
SOURCE_DIR=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v3.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
if any(c.name.startswith('12 • Pool terrace reference fix') for c in scene.collection.children):
    raise RuntimeError('Pool terrace is already refined. Rebuild using rebuild_project.py to start again.')
materials=list({m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m})
M={m.name.split('.00')[0]:m for m in materials}
M['lamp']=M['Lantern • warm amber'];M['water']=M['Turquoise river'];M['waterLight']=M['Waterfall cyan'];M['foam']=M['Foam and water glints']
src=open(os.path.join(SOURCE_DIR,'build_village.py'),encoding='utf-8').read()
for node in ast.parse(src).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'mesh_constants','exec'))
    if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in ['Build','ring','ribbon']:exec(compile(ast.Module(body=[node],type_ignores=[]),'mesh_helpers','exec'))
root=bpy.data.collections.new('12 • Pool terrace reference fix');scene.collection.children.link(root)
cols={}
for name in ['Terrace • paving and support','Terrace • railings and stairs','Terrace • seating and planters','Terrace • flowers and trailing greenery','Terrace • lanterns']:
    c=bpy.data.collections.new(name);root.children.link(c);cols[name]=c
random.seed(441)

CONTROL=[(10.45,-3.05,1.25),(11.5,-2.05,1.49),(11.95,-.55,1.85),(11.90,.95,1.91),(11.75,2.25,1.91),(10.7,3.0,1.91)]
def smoothline(points,steps=12):
    p=[Vector(points[0])]+[Vector(q) for q in points]+[Vector(points[-1])];out=[]
    for k in range(1,len(p)-2):
        for j in range(steps):
            t=j/steps;a,b,c,d=p[k-1:k+3]
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    out.append(Vector(points[-1]));return out
CURVE=smoothline(CONTROL)
def width(t):return 1.35+.48*sin(pi*t)+.36*math.exp(-((t-.38)/.13)**2)+.25*math.exp(-((t-.75)/.12)**2)
def frame(t):
    u=max(0,min(len(CURVE)-1,t*(len(CURVE)-1)));i=min(len(CURVE)-2,int(u));f=u-i
    p=CURVE[i].lerp(CURVE[i+1],f);d=CURVE[min(i+2,len(CURVE)-1)]-CURVE[max(i-1,0)]
    tangent=Vector((d.x,d.y,0)).normalized();out=Vector((tangent.y,-tangent.x,0))
    return p,tangent,out,width(t)
def center_of(ob,verts):return sum((ob.matrix_world@v.co for v in verts),Vector())/len(verts)
def erase_parts(ob,predicate):
    bm=bmesh.new();bm.from_mesh(ob.data);seen=set();delete=[]
    for v in bm.verts:
        if v in seen:continue
        stack=[v];seen.add(v);group=[]
        while stack:
            q=stack.pop();group.append(q)
            for e in q.link_edges:
                other=e.other_vert(q)
                if other not in seen:seen.add(other);stack.append(other)
        if predicate(center_of(ob,group)):delete.extend(group)
    if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    return len(delete)

# Retire the skinny paving and the old small stair flight in the marked strip.
for ob in list(scene.objects):
    if ob.type!='MESH':continue
    if ob.name.startswith(('Route • east river walk','Route • upper pool garden circuit','Expansion • eastern stair landing')):
        bpy.data.objects.remove(ob,do_unlink=True);continue
    if ob.name.startswith('Stairs • terrace connections'):
        erase_parts(ob,lambda p:10.55<p.x<12.1 and -2.2<p.y<1.1)
    if ob.name.startswith('Railings • garden boundaries'):
        erase_parts(ob,lambda p:p.x>10.45 and -3.5<p.y<3.5)
    if ob.name.startswith('Lanterns • paths, bridges'):
        erase_parts(ob,lambda p:p.x>10.3 and -3.5<p.y<3.8)
    if ob.name.startswith(('Expansion • two connected stairways','Expansion • stair handrails')):
        erase_parts(ob,lambda p:p.x>9.8)
    if ob.name.startswith('Expansion • promenade lanterns'):
        erase_parts(ob,lambda p:p.x>12.3 and p.y>1.35)

def terrace_surface():
    B=Build('Pool terrace • continuous curved stone platform','Terrace • paving and support')
    for i in range(len(CURVE)-1):
        a,ta,oa,wa=frame(i/(len(CURVE)-1));b,tb,ob,wb=frame((i+1)/(len(CURVE)-1))
        A=a-oa*wa/2;D=a+oa*wa/2;C=b+ob*wb/2;E=b-ob*wb/2
        # A continuous stone slab closes the previous gaps at the cliff edge.
        B.add([A+Vector((0,0,-.18)),D+Vector((0,0,-.18)),C+Vector((0,0,-.18)),E+Vector((0,0,-.18)),A,D,C,E],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone')
        n=6
        for j in range(n):
            s0=-.5+j/n+.009;s1=-.5+(j+1)/n-.009
            v=[a+oa*wa*s0+Vector((0,0,.04)),a+oa*wa*s1+Vector((0,0,.04)),b+ob*wb*s1+Vector((0,0,.04)),b+ob*wb*s0+Vector((0,0,.04))]
            B.add(v,[(0,1,2,3)],random.choice(['paver','paverLight','paver','paverDark']))
        # Raised coping follows both edges with individual rounded blocks.
        for side in [-1,1]:
            aa=a+oa*wa*.5*side;bb=b+ob*wb*.5*side
            B.beam(aa+Vector((0,0,.045)),bb+Vector((0,0,.045)),.13,'paverLight')
    B.finish(.018)
    R=Build('Pool terrace • planted cliff and retaining ledge','Terrace • paving and support')
    for i in range(42):
        t=(i+.5)/42;p,d,out,w=frame(t);q=p+out*(w/2-.03)
        # The exposed outer face reaches the lower terrace without an open seam.
        bottom=-.75;h=q.z-bottom
        R.box((q.x-.05*out.x,q.y-.05*out.y,bottom+h/2),(.32,.35,h),random.choice(['rock','rockLight']),Matrix.Rotation(math.atan2(d.y,d.x),3,'Z'))
        for j in range(2):
            z=q.z-.42-j*.65
            R.ico((q.x+.06*out.x,q.y+.06*out.y,z),(.29,.30,.46),random.choice(['rock','rockLight','stone']))
    R.finish(.035)

def rails_and_stairs():
    F=Build('Pool terrace • curved timber railings','Terrace • railings and stairs')
    # Outer rail provides a continuous boundary while leaving the stair entrance open.
    for side,t0,t1 in [(1,.025,.78),(-1,.12,.82)]:
        N=max(2,int((t1-t0)*18));points=[]
        for i in range(N+1):
            t=t0+(t1-t0)*i/N;p,d,out,w=frame(t);q=p+out*(w/2-.015)*side
            points.append(q)
            F.box(q+Vector((0,0,.39)),(.11,.11,.78),'woodLight')
            F.cyl(q+Vector((0,0,.80)),.085,.08,'plank',6)
        for a,b in zip(points[:-1],points[1:]):
            for dz in [.24,.65]:F.beam(a+Vector((0,0,dz)),b+Vector((0,0,dz)),.075,'plank')
    F.finish(.015)
    S=Build('Pool terrace • broad stair flights and rounded landing','Terrace • railings and stairs')
    H=Build('Pool terrace • stair handrails','Terrace • railings and stairs')
    runs=[((11.6,2.6,1.91),(13.1,3.05,.66),1.40,9),((13.1,3.05,.66),(13.9,1.35,-.49),1.40,10)]
    for aa,bb,w,N in runs:
        a,b=Vector(aa),Vector(bb);d=b-a;L=math.hypot(d.x,d.y);R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z');out=Vector((-d.y,d.x,0)).normalized()
        for i in range(N):
            p=a+d*(i+.5)/N;z=a.z+d.z*(i+.5)/N
            S.box((p.x,p.y,(z-.75)/2),(L/N+.02,w,z+.75),'stone',R)
            S.box((p.x,p.y,z+.045),(L/N+.03,w+.08,.09),'paverLight',R)
        for side in [-1,1]:
            for j in range(5):
                q=a+d*j/4+out*side*(w/2+.04)
                H.box(q+Vector((0,0,.39)),(.11,.11,.78),'woodLight')
            for z in [.23,.66]:H.beam(a+out*side*(w/2+.04)+Vector((0,0,z)),b+out*side*(w/2+.04)+Vector((0,0,z)),.075,'plank')
    S.cyl((13.1,3.05,.69),.98,.11,'paverLight',36)
    # Fill the short joins at the top and at the lower bridge approach.
    S.box((11.65,2.55,1.92),(1.55,1.2,.12),'paverLight')
    S.box((13.88,1.30,-.49),(1.45,.80,.12),'paverLight')
    S.finish(.03);H.finish(.018)

def seats_planters_and_lanterns():
    B=Build('Pool terrace • benches and timber flower boxes','Terrace • seating and planters')
    G=Build('Pool terrace • flowers, shrubs and trailing ivy','Terrace • flowers and trailing greenery')
    def plant(p,s=1):
        for j in range(10):
            a=j*2.4;r=random.uniform(.03,.18)*s
            G.ico(Vector(p)+Vector((r*cos(a),r*sin(a),random.uniform(.08,.23)*s)),(.15*s,.14*s,.11*s),random.choice(['leaf','leafLight','moss']))
    def flower(p,color):
        G.beam(p,Vector(p)+Vector((0,0,.17)),.008,'leaf',False)
        for j in range(5):
            a=j*2*pi/5;G.ico(Vector(p)+Vector((.035*cos(a),.035*sin(a),.19)),(.045,.045,.024),color)
    for t in [.37,.76]:
        p,d,out,w=frame(t);p+=out*(w/2-.35);R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z')
        for j in range(3):B.box(p+R@Vector((0,(j-1)*.10,.41)),(1.03,.085,.075),'plank',R)
        for x in [-.38,.38]:B.box(p+R@Vector((x,0,.20)),(.075,.30,.4),'iron',R)
        # Local +Y points inward, so the bench back faces the cliff edge.
        for j in range(2):B.box(p+R@Vector((0,-.23,.71+j*.13)),(1.03,.06,.10),'plank',R)
        for x in [-.41,.41]:B.box(p+R@Vector((x,0,.57)),(.06,.48,.06),'woodLight',R)
    for t in [.17,.55,.92]:
        p,d,out,w=frame(t);p+=out*(w/2-.24);R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z')
        for y in [-.21,.21]:
            for j in range(3):B.box(p+R@Vector((0,y,.12+j*.10)),(.82,.07,.08),'plank',R)
        for x in [-.39,.39]:B.box(p+R@Vector((x,0,.22)),(.07,.42,.35),'woodLight',R)
        B.box(p+Vector((0,0,.35)),(.65,.30,.035),'soilDark' if 'soilDark' in M else 'moss',R)
        for j in range(15):
            q=p+R@Vector((random.uniform(-.32,.32),random.uniform(-.14,.14),.36))
            plant(q,.6);flower(q+Vector((0,0,.10)),random.choice(['flowerWhite','flowerPink','flowerYellow']))
    # Trail plants down the exposed cliff and soften the pool-facing rail.
    for i in range(64):
        t=random.uniform(.04,.86);p,d,out,w=frame(t)
        side=1 if i%3 else -1;q=p+out*(w/2+.06)*side
        plant(q,.85)
        if i%3==0:flower(q+Vector((0,0,.13)),random.choice(['flowerWhite','flowerYellow','flowerBlue']))
        if side==1:
            for j in range(random.randint(3,8)):
                qq=q+Vector((.025*sin(j*1.5),.025*cos(j),-.13*j))
                G.ico(qq,(.11,.10,.065),random.choice(['leaf','leafLight','moss']))
    B.finish(.013);G.finish()
    L=Build('Pool terrace • warm reference lanterns','Terrace • lanterns')
    for t,side in [(.04,-1),(.25,-1),(.49,-1),(.70,1),(.91,-1)]:
        p,d,out,w=frame(t);p+=out*(w/2-.14)*side
        L.cyl(p+Vector((0,0,.06)),.14,.12,'stone',8);L.cyl(p+Vector((0,0,.71)),.043,1.3,'iron',8)
        L.box(p+Vector((0,0,1.46)),(.19,.19,.33),'lamp')
        for x in [-.11,.11]:
            for y in [-.11,.11]:L.box(p+Vector((x,y,1.46)),(.025,.025,.37),'iron')
        L.cyl(p+Vector((0,0,1.70)),.18,.19,'iron',4,r2=.015)
    # A lantern at the middle stair landing and one at its lower dock landing.
    for p in [Vector((13.65,3.25,.75)),Vector((14.47,1.15,-.42))]:
        L.cyl(p+Vector((0,0,.65)),.045,1.3,'iron',8);L.box(p+Vector((0,0,1.42)),(.19,.19,.32),'lamp');L.cyl(p+Vector((0,0,1.65)),.18,.18,'iron',4,r2=.015)
    L.finish(.009)

terrace_surface();rails_and_stairs();seats_planters_and_lanterns()
for col in root.children:
    for ob in col.objects:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()

data=bpy.data.cameras.new('Camera • pool terrace reference detail');data.type='ORTHO';data.ortho_scale=21.0
detail=bpy.data.objects.new(data.name,data);scene.collection.objects.link(detail)
target=Vector((8.0,-.25,.65));detail.location=target+Vector((29,-16,28));detail.rotation_euler=(target-detail.location).to_track_quat('-Z','Y').to_euler()
scene.camera=detail
scene.render.resolution_x=1600;scene.render.resolution_y=1450;scene.cycles.samples=64
os.makedirs(os.path.join(OUT,'renders','v4'),exist_ok=True)
scene.render.filepath=os.path.join(OUT,'renders','v4','03_pool_terrace_detail.png')
scene['Revision']='V4 • reference pool terrace, curved stone path, seating, planted railings and improved stairs'
manifest=os.path.join(OUT,'project_manifest.json');report=json.load(open(manifest,encoding='utf-8'))
report.update({'revision':4,'previous_version':'versions/Crystalbrook_Village_v3.blend','objects':len(scene.objects),'saved_cameras':sum(o.type=='CAMERA' for o in scene.objects),'pool_terrace_fix':['Continuous widened curved stone terrace around the upper pool','Matching timber rails and planted cliff edge','Two benches and three flower boxes','Warm lanterns and trailing greenery','Broader eastern stair flights and rounded landing connecting to the lower dock']})
with open(manifest,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V4 reference terrace saved')
