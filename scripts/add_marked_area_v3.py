"""Extend the current village into the user's marked front/right crescent."""
import bpy, bmesh, math, random, os, ast, json, shutil
from math import sin,cos,pi
from mathutils import Vector,Matrix

OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
SOURCE_DIR=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
if any(c.name.startswith('11 • Marked front and right expansion') for c in scene.collection.children):
    raise RuntimeError('This scene already has the expansion. Use rebuild_project.py for a fresh full rebuild.')
os.makedirs(os.path.join(OUT,'versions'),exist_ok=True)
os.makedirs(os.path.join(OUT,'renders','v3'),exist_ok=True)
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v2.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)

# Use the current scene's materials, so applying the extension preserves hand edits.
scene_materials=list({m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m})
def find_material(name):
    matches=[m for m in scene_materials if m.name.split('.00')[0]==name]
    if not matches:raise RuntimeError('Required village material missing: '+name)
    return max(matches,key=lambda m:m.users)
M={m.name.split('.00')[0]:m for m in scene_materials}
M['glow']=find_material('Amber window glass')
M['water']=find_material('Turquoise river');M['waterLight']=find_material('Waterfall cyan');M['foam']=find_material('Foam and water glints')
M['lamp']=find_material('Lantern • warm amber')

# Load geometry helpers without creating a new scene or touching the village kit.
src=open(os.path.join(SOURCE_DIR,'build_village.py'),encoding='utf-8').read()
tree=ast.parse(src)
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):
        exec(compile(ast.Module(body=[node],type_ignores=[]),'mesh_constants','exec'))
    if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in ['Build','ring','ribbon','house']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'mesh_helpers','exec'))

root=bpy.data.collections.new('11 • Marked front and right expansion');scene.collection.children.link(root)
cols={}
for name in ['Expansion • terrain','Expansion • paths','Expansion • water','Expansion • gardens','Expansion • railings and props','Expansion • houses']:
    c=bpy.data.collections.new(name);root.children.link(c);cols[name]=c
cols['03 Houses']=cols['Expansion • houses']
random.seed(319)
LOW=-.65
START=math.radians(-145);END=math.radians(40)
def old_outline(a):return 12+.46*sin(3*a+.3)+.27*sin(7*a-.8)+.12*cos(13*a)
def extension(a):
    t=(a-START)/(END-START)
    return 4.2*max(0,sin(pi*t))**.8 if 0<t<1 else 0
def pt(a,r,z=LOW):return Vector((r*cos(a),.88*r*sin(a),z))
def angular(x,y):return math.atan2(y/.88,x)
def radius(x,y):return math.hypot(x,y/.88)
def footprint(x,y,pad=0):
    a=angular(x,y);r=radius(x,y)
    return START<a<END and old_outline(a)-.45+pad<r<old_outline(a)+extension(a)-pad
def segdist(x,y,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy+1e-9)))
    return math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
STREAM=[(12.45,1.20),(12.8,.65),(13.2,.20),(14.1,.05),(15.0,-.10)]
POND=(13.2,.20)
WATER=-.83
STAIR_RUNS=[((3,-10.15,1.07),(3,-12.65,LOW+.06),1.85,14),((10.7,3.0,1.91),(12.6,3.8,.65),1.15,9),((12.6,3.8,.65),(14.0,1.9,LOW+.06),1.15,11)]
def stair_projection(x,y,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];t=((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)
    return t,math.hypot(x-a[0]-t*dx,y-a[1]-t*dy)
def floor_z(x,y):
    d=min(segdist(x,y,a,b) for a,b in zip(STREAM[:-1],STREAM[1:]))
    pond=math.hypot(x-POND[0],y-POND[1])
    cut=max(max(0,1-d/.72),max(0,1-pond/1.34))
    return LOW-.38*min(1,cut*1.7)

def lower_terrain():
    B=Build('New lower terrace • open buildable land','Expansion • terrain')
    na=186;nr=18;v=[]
    for i in range(na+1):
        a=START+(END-START)*i/na;ri=old_outline(a)-.48;ro=old_outline(a)+extension(a)
        for j in range(nr+1):
            r=ri+(ro-ri)*j/nr;p=pt(a,r)
            p.z=floor_z(p.x,p.y)+.012*sin(p.x*1.9)*cos(p.y*1.4);v.append(p)
    B.add(v,[(i*(nr+1)+j,(i+1)*(nr+1)+j,(i+1)*(nr+1)+j+1,i*(nr+1)+j+1) for i in range(na) for j in range(nr)],'grass')
    B.finish()
    C=Build('Expansion • integrated cliff body and underside','Expansion • terrain')
    n=186;v=[]
    for fac,z in [(1,LOW-.025),(.995,-1.55),(.94,-2.85),(.82,-3.65)]:
        for i in range(n+1):
            a=START+(END-START)*i/n;ri=old_outline(a)-.6;ro=old_outline(a)+extension(a)
            rr=ri+(ro-ri)*fac
            p=pt(a,rr,z+.08*sin(i*1.61))
            if fac==1:p.z=floor_z(p.x,p.y)-.035
            v.append(p)
    faces=[(k*(n+1)+i,k*(n+1)+i+1,(k+1)*(n+1)+i+1,(k+1)*(n+1)+i) for k in range(3) for i in range(n)]
    C.add(v,faces,'rockDark')
    # Underside slopes back under the old island to avoid a detached shelf.
    for i in range(n):
        a=START+(END-START)*i/n;b=START+(END-START)*(i+1)/n
        r0=old_outline(a)-.6;r1=old_outline(b)-.6
        C.add([pt(a,r0+(.6+extension(a))*.82,-3.65+.08*sin(i*1.61)),pt(b,r1+(.6+extension(b))*.82,-3.65+.08*sin((i+1)*1.61)),pt(b,r1-1.5,-2.45),pt(a,r0-1.5,-2.45)],[(0,1,2,3)],'rockDark')
    C.finish()
    R=Build('Expansion • matching fractured outer cliffs','Expansion • terrain')
    for i in range(160):
        a=START+(END-START)*(i+.5)/160
        if extension(a)<.30:continue
        r=old_outline(a)+extension(a);p=pt(a,r)
        # Leave an opening at the new stream outlet.
        if abs(p.y+.16)<.70 and p.x>14.5:continue
        n2=7;width=random.uniform(.24,.43);depth=random.uniform(.36,.60);bottom=random.uniform(-3.3,-2.75)
        vv=[]
        for j,z in enumerate([bottom,-1.75,LOW-.06]):
            for k in range(n2):
                t=k*2*pi/n2;f=random.uniform(.80,1.18)
                vv.append((p.x+width*f*cos(t),p.y+depth*f*sin(t),z+random.uniform(-.09,.09)))
        R.add(vv,[tuple(range(n2-1,-1,-1)),tuple(range(2*n2,3*n2))]+[(j*n2+k,j*n2+(k+1)%n2,(j+1)*n2+(k+1)%n2,(j+1)*n2+k) for j in range(2) for k in range(n2)],random.choice(['rock','rockLight','rock','stone']))
        for j in range(2):R.ico((p.x,p.y,-1.1-j*.85),(random.uniform(.35,.55),random.uniform(.35,.55),random.uniform(.55,.85)),random.choice(['rock','rockLight']))
        if i%3==0:R.ico((p.x*.99,p.y*.99,-3.25),(.40,.42,.65),'rockDark')
    R.finish(.016)

PATH_POINTS=[]
def path(points,width,name):
    B=Build(name,'Expansion • paths');PATH_POINTS.append((points,width))
    for a,b in zip(points[:-1],points[1:]):
        a,b=Vector(a),Vector(b);d=b-a;L=math.hypot(d.x,d.y)
        if L<.02:continue
        R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z');rows=max(1,round(L/.36));nc=max(2,round(width/.36))
        for i in range(rows):
            for j in range(nc):
                p=a+d*((i+.5)/rows)+R@Vector((0,(j+.5-nc/2)*width/nc,0))
                B.box(p,(L/rows*.94,width/nc*.94,.08),random.choice(['paver','paverLight','paver','paverDark']),R)
    return B.finish(.013)

def erase_components(ob,predicate):
    """Remove complete disconnected primitives only where an opening is required."""
    bm=bmesh.new();bm.from_mesh(ob.data);seen=set();remove=[]
    for v in bm.verts:
        if v in seen:continue
        stack=[v];seen.add(v);group=[]
        while stack:
            q=stack.pop();group.append(q)
            for edge in q.link_edges:
                other=edge.other_vert(q)
                if other not in seen:seen.add(other);stack.append(other)
        center=sum((ob.matrix_world@q.co for q in group),Vector())/len(group)
        if predicate(center):remove.extend(group)
    if remove:bmesh.ops.delete(bm,geom=remove,context='VERTS')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    return len(remove)

def stairs_and_paths():
    def in_stair_opening(p):
        for a,b,w,n in STAIR_RUNS:
            t,d=stair_projection(p.x,p.y,a,b)
            if -.05<t<1.05 and d<w/2+.25:return True
        return False
    # Cut stair access into the existing rim, preserving the rest of the village.
    for ob in scene.objects:
        if ob.type=='MESH' and ob.name.startswith('Railings • garden boundaries'):
            print('Fence opening vertices:',erase_components(ob,in_stair_opening))
        if ob.type=='MESH' and ob.name.startswith('Cliffs • fractured shelves'):
            print('Cliff opening vertices:',erase_components(ob,lambda p:p.z>LOW-.4 and in_stair_opening(p)))
        if ob.type=='MESH' and ob.name.startswith('Terrain • carved river valley'):
            inv=ob.matrix_world.inverted()
            for v in ob.data.vertices:
                p=ob.matrix_world@v.co
                for a,b,w,n in STAIR_RUNS:
                    t,d=stair_projection(p.x,p.y,a,b)
                    if 0<t<1 and d<w/2+.04:p.z=min(p.z,a[2]+(b[2]-a[2])*t-.07)
                v.co=inv@p
            ob.data.update()
        if ob.type=='MESH' and ob.name.startswith('Island • irregular suspended'):
            bm=bmesh.new();bm.from_mesh(ob.data)
            faces=[f for f in bm.faces if (ob.matrix_world@f.calc_center_median()).z>LOW-.1 and in_stair_opening(ob.matrix_world@f.calc_center_median())]
            if faces:bmesh.ops.delete(bm,geom=faces,context='FACES')
            bm.to_mesh(ob.data);bm.free();ob.data.update()
    A=Build('Expansion • two connected stairways','Expansion • paths')
    RAIL=Build('Expansion • stair handrails and landing posts','Expansion • railings and props')
    def stairs(a,b,width,N):
        a,b=Vector(a),Vector(b);d=b-a;L=math.hypot(d.x,d.y);R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z')
        bottom=min(a.z,b.z)-.13;side=Vector((-d.y,d.x,0)).normalized()
        for i in range(N):
            p=a+d*((i+.5)/N);zz=a.z+d.z*(i+.5)/N
            A.box((p.x,p.y,(zz+bottom)/2),(L/N+.018,width,zz-bottom),'stone',R)
            A.box((p.x,p.y,zz+.045),(L/N+.025,width+.06,.09),'paverLight',R)
        for s in [-1,1]:
            for j in range(5):
                p=a+d*j/4+side*s*(width/2+.08)
                RAIL.box(p+Vector((0,0,.39)),(.10,.10,.78),'woodLight')
            for dz in [.24,.67]:RAIL.beam(a+side*s*(width/2+.08)+Vector((0,0,dz)),b+side*s*(width/2+.08)+Vector((0,0,dz)),.075,'plank')
    for a,b,w,n in STAIR_RUNS:stairs(a,b,w,n)
    path([(3,-9.15,1.09),(3,-10.15,1.09)],1.85,'Expansion • front village stair approach')
    path([(3,-12.65,LOW+.09),(3,-12.40,LOW+.09),(3.6,-12.45,LOW+.09)],1.85,'Expansion • front stair landing')
    A.box((12.6,3.8,.68),(1.55,1.45,.12),'paverLight')
    path([(14,1.9,LOW+.09),(13.6,1.3,LOW+.09)],1.25,'Expansion • eastern stair landing')
    A.finish(.022);RAIL.finish(.015)
    # A crescent promenade leaves usable grass on both sides.
    sections=[(-132,-8),(8,29)]
    for idx,(aa,bb) in enumerate(sections):
        points=[]
        for i in range(92 if idx==0 else 23):
            t=i/(91 if idx==0 else 22);a=math.radians(aa+(bb-aa)*t)
            deg=math.degrees(a)
            lot_detour=max(math.exp(-((deg+55)/14)**4),math.exp(-((deg+22)/11)**4))
            base=extension(a)*.53;outer=max(base,extension(a)-.95)
            r=old_outline(a)+base+(outer-base)*lot_detour
            points.append(tuple(pt(a,r,LOW+.075)))
        path(points,1.10,'Expansion • curved lower promenade '+str(idx+1))
    # A small footbridge keeps the new creek and footpath connected.
    B=Build('Expansion • creek garden footbridge','Expansion • paths');x=13.6;y0=-1.35;y1=1.35;z=LOW+.15
    for i in range(19):B.box((x,y0+(i+.5)*(y1-y0)/19,z),(1.42,(y1-y0)/19-.014,.12),'plank')
    for xx in [x-.63,x+.63]:
        B.beam((xx,y0,z-.10),(xx,y1,z-.10),.13,'wood')
        for yy in [y0,0,y1]:B.box((xx,yy,z+.35),(.10,.10,.80),'woodLight')
        for dz in [.25,.66]:B.beam((xx,y0,z+dz),(xx,y1,z+dz),.07,'plank')
    B.finish(.016)
    path([(13.6,-1.35,LOW+.13),(13.7,-1.55,LOW+.08)],1.35,'Expansion • creek bridge south landing')

def extension_water():
    # The old eastern waterfall now feeds the new terrace instead of passing through it.
    for ob in scene.objects:
        if ob.type=='MESH' and ob.name.startswith('Waterfalls • upper cascade'):
            print('Redirected waterfall vertices:',erase_components(ob,lambda p:p.x>10.9 and p.y>.55))
    B=Build('Expansion • lower pool and outgoing stream','Expansion • water')
    B.cyl((POND[0],POND[1],WATER),1.12,.025,'water',56)
    for a,b in zip(STREAM[:-1],STREAM[1:]):
        d=Vector((b[0]-a[0],b[1]-a[1],0));side=Vector((-d.y,d.x,0)).normalized()*.28
        p,q=Vector((a[0],a[1],WATER)),Vector((b[0],b[1],WATER))
        B.add([p-side,p+side,q+side,q-side],[(0,1,2,3)],'water')
    B.finish()
    F=Build('Expansion • linked cascades and new outer waterfall','Expansion • water')
    def waterfall(points,width):
        pts=[Vector(p) for p in points]
        for k in range(19):
            v=[]
            for j,p in enumerate(pts):
                prev=pts[max(0,j-1)];nxt=pts[min(len(pts)-1,j+1)];d=nxt-prev
                if d.x*d.x+d.y*d.y<.0001:d=pts[-1]-pts[0]
                side=Vector((-d.y,d.x,0)).normalized()
                for ss in [0,1]:v.append(p+side*((k+ss)/19-.5)*width)
            F.add(v,[(j*2,j*2+1,j*2+3,j*2+2) for j in range(len(pts)-1)],'foam' if k in [0,6,13,18] else 'waterLight')
        for i in range(26):
            p=pts[-1]+Vector((random.uniform(-.28,.28),random.uniform(-.28,.28),random.uniform(0,.18)))
            F.ico(p,(.045,.045,.06),'foam')
    waterfall([(11.2,1.50,1.48),(11.9,1.45,1.48),(12.10,1.4,.60),(12.25,1.3,-.72),(12.65,.90,WATER)],.85)
    a=angular(15.4,-.16);out=old_outline(a)+extension(a)
    x=out*cos(a);y=.88*out*sin(a)
    waterfall([(x-.50,y,WATER),(x+.08,y-.01,WATER),(x+.27,y-.03,-1.25),(x+.33,y-.05,-2.9),(x+.40,y-.08,-4.1)],.66)
    F.finish()
    R=Build('Expansion • creek rocks and water glints','Expansion • water')
    for i in range(26):
        a=i*2*pi/26;x=POND[0]+1.23*cos(a);y=POND[1]+1.23*sin(a)
        if x>13.75 or (12.1<x<13.7 and y<.6):continue
        R.ico((x,y,LOW-.03),(.15,.16,.16),'rockLight')
    for a,b in zip(STREAM[:-1],STREAM[1:]):
        for i in range(8):
            t=(i+.5)/8;p=Vector((a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,WATER+.025))
            R.ico(p,(.06,.02,.009),'foam')
    R.finish()

def garden_details():
    G=Build('Expansion • low border plants and open lawn','Expansion • gardens')
    for i in range(230):
        a=random.uniform(START+.1,END-.1)
        if extension(a)<1:continue
        r=old_outline(a)+extension(a)-random.uniform(.15,.50);p=pt(a,r)
        if abs(p.y)<.9 and p.x>12.4:continue
        for j in range(7):
            aa=j*2.4;q=p+Vector((.16*cos(aa),.16*sin(aa),.09+random.random()*.15))
            G.ico(q,(.14,.13,.09),random.choice(['leaf','leafLight','moss']))
        if i%4==0:
            G.beam(p,p+Vector((0,0,.27)),.009,'leaf',False)
            for j in range(5):
                aa=j*2*pi/5;G.ico(p+Vector((.04*cos(aa),.04*sin(aa),.28)),(.05,.05,.025),random.choice(['flowerWhite','flowerYellow','flowerBlue']))
    G.finish()
    F=Build('Expansion • outer safety fence','Expansion • railings and props')
    # Leave meadow views open; use fence sections rather than a continuous barrier.
    for aa,bb in [(-124,-94),(-87,-57),(-50,-23),(-17,-7),(12,25)]:
        n=round((bb-aa)/4);points=[]
        for i in range(n+1):
            a=math.radians(aa+(bb-aa)*i/n);r=old_outline(a)+extension(a)-.42
            points.append(pt(a,r,LOW+.02))
        for a,b in zip(points[:-1],points[1:]):
            F.box(a+Vector((0,0,.37)),(.10,.10,.74),'woodLight')
            for z in [.22,.61]:F.beam(a+Vector((0,0,z)),b+Vector((0,0,z)),.065,'plank')
        F.box(points[-1]+Vector((0,0,.37)),(.10,.10,.74),'woodLight')
    F.finish(.014)
    P=Build('Expansion • promenade lanterns and overlook benches','Expansion • railings and props')
    for aa in [-116,-94,-71,-47,-23,16]:
        a=math.radians(aa);r=old_outline(a)+extension(a)*.53+.85;p=pt(a,r,LOW+.08)
        P.cyl(p+Vector((0,0,.60)),.04,1.2,'iron',8);P.cyl(p+Vector((0,0,.06)),.12,.12,'stone',8)
        P.box(p+Vector((0,0,1.28)),(.17,.17,.28),'lamp')
        for xx in [-.1,.1]:
            for yy in [-.1,.1]:P.box(p+Vector((xx,yy,1.28)),(.023,.023,.33),'iron')
        P.cyl(p+Vector((0,0,1.49)),.15,.16,'iron',4,r2=.02)
    for aa in [-103,-45]:
        a=math.radians(aa);r=old_outline(a)+extension(a)*.80;p=pt(a,r,LOW);R=Matrix.Rotation(a+pi/2,3,'Z')
        for j in range(3):P.box(p+R@Vector((0,(j-1)*.12,.4)),(1.2,.10,.075),'plank',R)
        for xx in [-.45,.45]:P.box(p+R@Vector((xx,0,.2)),(.075,.35,.4),'iron',R)
        for j in range(2):P.box(p+R@Vector((0,.23,.69+j*.13)),(1.2,.06,.09),'plank',R)
    P.finish(.01)

def reference_houses_dock_and_garden():
    # Two additional cottages occupy the newly requested front/right land.
    for name,degrees,w,d,h,offset in [
        ('07 • Lower garden cottage',-55,2.3,1.7,2.50,1.35),
        ('08 • Creekside cottage',-22,1.9,1.4,2.50,1.20)]:
        a=math.radians(degrees);p=pt(a,old_outline(a)+offset,LOW+.015);angle=a+pi/2
        ob=house(name,p.x,p.y,p.z,w,d,h,angle,False);ob.scale=(.90,.90,.78 if w>2 else .74)
        direction=Vector((cos(a),sin(a),0));door=p+direction*((d/2+.50)*.9)
        end=pt(a,old_outline(a)+max(extension(a)*.53,extension(a)-.95),LOW+.10)
        path([tuple(Vector((door.x,door.y,LOW+.11))),tuple(end)],.80,'Expansion • cottage entrance '+name[:2])
    # The small wooden dock sits over the new pool and joins its footbridge.
    D=Build('Expansion • lower wooden dock and mooring posts','Expansion • paths')
    x0,x1=12.25,13.6;y0,y1=-.67,.45;z=LOW+.17
    for j in range(10):D.box((x0+(j+.5)*(x1-x0)/10,(y0+y1)/2,z),((x1-x0)/10-.014,y1-y0,.11),'plank')
    for xx in [x0+.08,x1-.08]:
        for yy in [y0+.08,y1-.08]:
            D.cyl((xx,yy,WATER-.16),.075,.95,'wood',10)
            D.cyl((xx,yy,z+.16),.11,.08,'plank',10)
    for yy in [y0+.06,y1-.06]:D.beam((x0,yy,z-.12),(x1,yy,z-.12),.13,'wood')
    for yy in [y0,y1]:
        D.beam((x0,yy,z+.50),(x1-.3,yy,z+.50),.06,'woodLight')
        for xx in [x0,x1-.3]:D.box((xx,yy,z+.25),(.09,.09,.6),'woodLight')
    D.beam((x0,y0,z+.50),(x0,y1,z+.50),.06,'woodLight')
    D.cyl((12.5,.15,z+.22),.15,.38,'woodLight',12)
    ring(D,(12.5,.15),.15,.17,z+.10,.035,'iron',12);ring(D,(12.5,.15),.15,.17,z+.34,.035,'iron',12)
    D.finish(.015)
    # A small moored rowboat remains below deck level in the quiet pool.
    B=Build('Expansion • small moored rowboat','Expansion • water')
    center=Vector((12.63,-.97,WATER+.04));n=18;v=[]
    for s,zz in [(1,0),(.78,-.13),(.72,-.08),(.9,.07)]:
        for i in range(n):
            a=i*2*pi/n;v.append(center+Vector((.53*s*cos(a),.20*s*sin(a),zz)))
    B.add(v,[(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(3) for i in range(n)],'woodLight')
    for xx in [-.19,.18]:B.box(center+Vector((xx,0,.065)),(.08,.30,.035),'plank')
    B.finish(.008)
    # Seating garden: planted beds and small shade trees beside the lower path.
    G=Build('Expansion • flower garden and seating court','Expansion • gardens')
    a=math.radians(-94);p=pt(a,old_outline(a)+1.10,LOW)
    G.cyl(p+Vector((0,0,.045)),.82,.085,'paverLight',40)
    for side in [-1,1]:
        pos=p+Vector((side*.59,0,0));R=Matrix.Rotation(side*pi/2,3,'Z')
        for j in range(3):G.box(pos+R@Vector((0,(j-1)*.105,.38)),(.83,.085,.065),'plank',R)
        for xx in [-.29,.29]:G.box(pos+R@Vector((xx,0,.19)),(.06,.27,.38),'iron',R)
        G.box(pos+R@Vector((0,.21,.65)),(.83,.06,.16),'plank',R)
    for i in range(55):
        aa=i*2.4;rr=random.uniform(.93,1.24);q=p+Vector((rr*cos(aa),rr*sin(aa),.13))
        G.ico(q,(.15,.14,.15),random.choice(['leaf','leafLight','moss']))
        if i%3==0:
            for j in range(5):
                bb=j*2*pi/5;G.ico(q+Vector((.045*cos(bb),.045*sin(bb),.15)),(.05,.05,.025),random.choice(['flowerWhite','flowerYellow','flowerBlue']))
    for degrees,offset in [(-84,.72),(-115,.80),(-38,.75)]:
        aa=math.radians(degrees);q=pt(aa,old_outline(aa)+offset,LOW)
        G.cyl(q+Vector((0,0,.67)),.055,1.34,'wood',8,r2=.025)
        for k in range(6):
            bb=k*2.4;end=q+Vector((.30*cos(bb),.30*sin(bb),1.1+random.random()*.35))
            G.beam(q+Vector((0,0,.7)),end,.025,'woodLight',False)
            for j in range(13):
                cc=j*2.4;G.ico(end+Vector((.23*cos(cc),.23*sin(cc),random.uniform(-.04,.20))),(.19,.17,.10),random.choice(['leaf','leafLight']))
    G.finish(.008)

lower_terrain();stairs_and_paths();extension_water();garden_details();reference_houses_dock_and_garden()

# Finish only the newly added geometry; all previous village meshes retain their edits.
for c in root.children:
    for ob in c.objects:
        if ob.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        if ob.name.startswith(('New lower terrace','Expansion • lower pool')):
            for f in bm.faces:
                if f.normal.z<0:f.normal_flip()
        bm.to_mesh(ob.data);bm.free();ob.data.update()

# Reframe the expanded map and add a front view matching the marker's orientation.
hero=next(o for o in scene.objects if o.type=='CAMERA' and o.name.startswith('Camera • hero isometric'))
target=Vector((1.0,-1.4,.6));hero.location=target+Vector((25,-38,31.9))
hero.rotation_euler=(target-hero.location).to_track_quat('-Z','Y').to_euler();hero.data.ortho_scale=36
cam_data=bpy.data.cameras.new('Camera • marked expansion overview');cam_data.type='ORTHO';cam_data.ortho_scale=35
marker_camera=bpy.data.objects.new(cam_data.name,cam_data);scene.collection.objects.link(marker_camera)
marker_camera.location=Vector((1,-1.5,.5))+Vector((-3,-47,35))
marker_camera.rotation_euler=(Vector((1,-1.5,.5))-marker_camera.location).to_track_quat('-Z','Y').to_euler()
for ob in scene.objects:
    if ob.type=='CAMERA' and ob.name.startswith('Camera • top layout'):
        ob.location=(1,-1.1,45);ob.data.ortho_scale=35
scene.camera=marker_camera
scene.render.resolution_x=1700;scene.render.resolution_y=1450;scene.render.resolution_percentage=100
scene.cycles.samples=64;scene.cycles.use_denoising=True
scene.render.filepath=os.path.join(OUT,'renders','v3','03_expanded_village.png')
scene['Revision']='V3 • front and right lower terrace following marked crescent'
scene['Expansion']='Reference crescent with two cottages, cliff promenade, stairs, lower pool and waterfall, wooden dock and seating garden'
scene.name='Crystalbrook Village • Expanded'
manifest_path=os.path.join(OUT,'project_manifest.json')
report=json.load(open(manifest_path,encoding='utf-8')) if os.path.isfile(manifest_path) else {}
report.update({'revision':3,'active_scene':scene.name,'previous_version':'versions/Crystalbrook_Village_v2.blend','objects':len(scene.objects),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'faces':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),'saved_cameras':sum(o.type=='CAMERA' for o in scene.objects),'hero_resolution':[1700,1450],
 'houses':8,'expansion':{'sector_degrees':[-145,40],'maximum_added_width':4.2,'new_terrain_height':LOW,'use':'Reference expansion: cottages, cliff path, lower water and dock, seating garden','features':['Front and right crescent following user reference','Two stairs connecting existing routes','Matching cliff face and continuous underside','Two small additional timber cottages','Redirected eastern cascade into lower creek and new outer waterfall','Lower wooden dock and small rowboat','Creek footbridge, railings, lanterns and seating garden']}})
with open(manifest_path,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
with open(os.path.join(OUT,'V3_CHANGELOG.txt'),'w',encoding='utf-8') as f:f.write('V3 - REFERENCE AREA EXPANSION\n\nAdded a lower crescent around the front and right of the original island.\nMaximum outward extension: 4.2 Blender units. New level: -0.65.\nAdded two matching cottages, a curved stone cliff path with fences and lanterns,\na lower pool and waterfall, a wooden dock with rowboat, and a seating garden.\nVillage connections: front stairs and eastern switchback stairs.\nV2 is preserved in versions/Crystalbrook_Village_v2.blend.\n')
readme='''CRYSTALBROOK VILLAGE - EXPANDED VERSION 3

Open Crystalbrook_Village.blend. The active scene is Crystalbrook Village - Expanded.
The original village center is retained. The right and bottom sides have been
expanded to follow the supplied expanded-design reference.

ADDITIONS
Curved lower stone promenade with fences and lanterns.
Two matching timber cottages, bringing the village to eight houses.
Lower pool, continued cascade and new waterfall over the expanded rim.
Wooden dock, mooring posts, small rowboat and creek footbridge.
Garden court with benches, shade trees and flowers.
Front stairway and eastern switchback stairs connecting the old and new areas.

FILES
Crystalbrook_Village.blend            Current editable project.
renders/v3/                          Expanded overview, isometric and check views.
versions/Crystalbrook_Village_v2.blend Previous version before expansion.
references/expanded_design_reference.png Supplied expansion reference.
scripts/                             Rebuild and additive modeling sources.

REBUILD
Run scripts/rebuild_project.py in Blender's Scripting workspace for a fresh full
rebuild. The add_marked_area_v3.py script applies the extension to an unexpanded
V2 scene and prevents accidental duplication in an already expanded scene.
Run scripts/render_expanded_views.py to regenerate the saved camera renders.

The scene uses modeled geometry and self-contained materials. Water is static.
The main reference-facing camera is Camera - marked expansion overview.
The original isometric camera is also reframed to include the expanded island.
'''
with open(os.path.join(OUT,'PROJECT_README.txt'),'w',encoding='utf-8') as f:f.write(readme)
txt=bpy.data.texts.get('PROJECT • Expanded V3 read me') or bpy.data.texts.new('PROJECT • Expanded V3 read me');txt.clear();txt.write(readme)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V3 expanded village saved. New objects:',sum(len(c.objects) for c in root.children))
