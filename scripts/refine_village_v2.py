"""Second art pass: tiered terrain, inset water, architecture and leaf geometry."""
import bpy, os, ast, random, math, json, shutil
from mathutils import Vector, Matrix
from math import sin, cos, pi
SOURCE_DIR=os.path.dirname(os.path.abspath(__file__))
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
os.makedirs(os.path.join(OUT,'versions'),exist_ok=True)
os.makedirs(os.path.join(OUT,'renders','v2'),exist_ok=True)
prior=os.path.join(OUT,'Crystalbrook_Village.blend')
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v1.blend')
if os.path.isfile(prior) and not os.path.isfile(backup):shutil.copy2(prior,backup)
old_render=os.path.join(OUT,'renders','03_village_hero.png')
old_copy=os.path.join(OUT,'versions','v1_hero.png')
if os.path.isfile(old_render) and not os.path.isfile(old_copy):shutil.copy2(old_render,old_copy)

# Reuse the existing mesh helpers and house kit without recreating the first map.
base=open(os.path.join(SOURCE_DIR,'build_village.py'),encoding='utf-8').read()
exec(compile(base[:base.index('def height(')],'village_mesh_helpers','exec'))
scene.name='Crystalbrook Village • Refined'
def load_functions(filename,names):
    src=open(os.path.join(SOURCE_DIR,filename),encoding='utf-8').read()
    for node in ast.parse(src).body:
        if isinstance(node,ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'),globals())
load_functions('build_village.py',{'house','stall','fountain'})
load_functions('finish_village.py',{'smoothline'})
random.seed(144)

def recolor(key,color,emission=None,rough=None):
    m=M[key];m.diffuse_color=(*color,1)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1)
    if emission is not None:
        p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    if rough is not None:p.inputs['Roughness'].default_value=rough
for key,col in {
 'grass':(.25,.44,.07),'grassLight':(.43,.64,.10),'moss':(.18,.37,.075),
 'leaf':(.21,.43,.055),'leafLight':(.44,.65,.085),'leafDark':(.065,.28,.075),'pine':(.10,.34,.12),
 'rock':(.43,.46,.45),'rockLight':(.57,.58,.54),'rockDark':(.31,.35,.37),
 'roof':(.76,.18,.052),'roofLight':(.94,.31,.09),'roofDark':(.56,.10,.032),
 'woodLight':(.37,.18,.065),'plaster':(.94,.83,.64),'plasterLight':(.99,.90,.73),
 'water':(.015,.48,.72),'waterLight':(.08,.72,.98)
}.items():recolor(key,col)
recolor('glow',(1,.48,.11),.65)
M['windowDark']=mat('Recessed teal window glass',(.035,.10,.115),.18,.16,.05)
M['windowWarm']=mat('Soft warm window glass',(.85,.39,.075),.24,0,.35)
M['leafGold']=mat('Sunlit lime leaf',(.57,.71,.12))
M['clay']=mat('Unglazed terracotta pottery',(.57,.19,.085))
M['soilDark']=mat('Moist riverbed',(.17,.16,.115))

LOW_POINTS=[(9.0,-1.4,.28),(8.7,-3.1,.28),(6.7,-5.0,.28),(3.7,-6.25,.28),(.1,-7.15,.28),(-3.5,-7.5,.28),(-6.8,-8.3,.28),(-9.3,-8.0,.28)]
RIVER=smoothline(LOW_POINTS,steps=7)
UPPER=(9.65,.95,1.48)
def segdist(x,y,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy+1e-8)))
    return math.hypot(x-a[0]-dx*t,y-a[1]-dy*t)
def riverdist(x,y):return min(segdist(x,y,a,b) for a,b in zip(LOW_POINTS[:-1],LOW_POINTS[1:]))
def outline(a):return 12.0+.46*sin(3*a+.3)+.27*sin(7*a-.8)+.12*cos(13*a)
def inside(x,y,margin=0):
    a=math.atan2(y/.88,x);return math.hypot(x,y/.88)<outline(a)-margin
def smoothstep(x):
    t=max(0,min(1,x));return t*t*(3-2*t)
def landheight(x,y):
    z=1.12
    if y>4.1:z=2.60
    elif (x>5.25 and y>-.15) or (x>8.2 and y>-.55):z=1.82
    elif x< -5.4 and y>1.5:z=1.52
    if y<-8.9:z=.98
    dp=math.hypot((x-UPPER[0])/1.0,(y-UPPER[1])/1.12)
    if dp<1.65:z=min(z,1.20+(z-1.2)*smoothstep((dp-1.05)/.60))
    if y<.5:
        d=riverdist(x,y)
        if d<1.53:z=-.10+(z+.10)*smoothstep((d-.72)/.81)
    return z
height=landheight

def terrain():
    T=Build('Terrain • carved river valley and three village levels','01 Island & cliffs')
    N=130;step=.20;verts=[]
    for j in range(N+1):
        y=-13+j*step
        for i in range(N+1):
            x=-13+i*step;zz=landheight(x,y)
            if riverdist(x,y)>.95:zz+=.018*sin(x*1.7)*cos(y*2.1)
            verts.append((x,y,zz))
    fgrass=[];fbed=[]
    for j in range(N):
        for i in range(N):
            x=-13+(i+.5)*step;y=-13+(j+.5)*step
            if not inside(x,y):continue
            a=j*(N+1)+i;face=(a,a+1,a+N+2,a+N+1)
            if landheight(x,y)<.35:fbed.append(face)
            else:fgrass.append(face)
    T.add(verts,fgrass,'grass');T.add(verts,fbed,'soilDark');T.finish()
    C=Build('Island • irregular suspended rock core','01 Island & cliffs')
    n=160;v=[]
    for fac,zz in [(1,None),(.99,-.85),(.87,-1.90),(.58,-2.75),(.12,-3.35)]:
        for i in range(n):
            a=2*pi*i/n;r=outline(a)*fac;x=r*cos(a);y=.88*r*sin(a)
            z=landheight(x,y)-.03 if zz is None else zz+.12*sin(i*1.7)
            v.append((x,y,z))
    faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(4) for i in range(n)]
    C.add(v,faces+[tuple(range(4*n,5*n))],'rockDark');C.finish()
    R=Build('Cliffs • fractured shelves and hanging stones','01 Island & cliffs')
    for i in range(185):
        a=i*2*pi/185;r=outline(a);x=r*cos(a);y=.88*r*sin(a)
        # Keep outlet openings clear.
        if math.hypot(x+9.3,y+8.0)<1.3:continue
        ztop=landheight(x*.97,y*.97)-random.uniform(.02,.18)
        zbot=random.uniform(-1.95,-1.2);n2=7;vs=[]
        width=random.uniform(.22,.43);depth=random.uniform(.32,.68)
        for j,z in enumerate([zbot,(ztop+zbot)*.38,ztop]):
            for k in range(n2):
                t=k*2*pi/n2;f=random.uniform(.85,1.15)
                vs.append((x+width*f*cos(t),y+depth*f*sin(t),z+random.uniform(-.10,.10)))
        faces=[tuple(range(n2-1,-1,-1)),tuple(range(2*n2,3*n2))]+[(j*n2+k,j*n2+(k+1)%n2,(j+1)*n2+(k+1)%n2,(j+1)*n2+k) for j in range(2) for k in range(n2)]
        R.add(vs,faces,random.choice(['rockLight','rock','rock','stone']))
        if i%3==0:
            R.ico((x*.94,y*.94,zbot-.2),(.37,.48,.86),random.choice(['rock','rockDark']))
    for i in range(100):
        a=random.random()*2*pi;r=random.uniform(1,10.4);x=r*cos(a);y=.88*r*sin(a)
        z=-3.1+.8*(r/11)
        R.ico((x,y,z),(random.uniform(.45,1.1),random.uniform(.45,1.0),random.uniform(.45,.9)),random.choice(['rock','rockDark','rockLight']))
    # Broad broken blocks and ledges interrupt the narrow vertical columns.
    for i in range(125):
        a=i*2*pi/125;r=outline(a)+random.uniform(-.13,.14);x=r*cos(a);y=.88*r*sin(a)
        if math.hypot(x+9.3,y+8.0)<1.4:continue
        ztop=landheight(x*.97,y*.97)
        for j in range(2):
            z=ztop-.48-j*random.uniform(.65,1.0)
            R.ico((x,y,z),(random.uniform(.37,.65),random.uniform(.36,.60),random.uniform(.48,.83)),random.choice(['rock','rock','rockLight']))
        if i%8==0:R.ico((x*.985,y*.985,ztop-.1),(.65,.65,.23),'moss')
    # Broken low retaining walls along changes in level.
    for x0,x1,y,top in [(-10.4,-3.15,4.10,2.60),(-.65,5.15,4.10,2.60),(5.25,10.9,-.15,1.82),(-9.8,-5.5,1.5,1.52)]:
        count=int((x1-x0)/.55)
        for k in range(count):
            x=x0+(k+.5)*(x1-x0)/count;bottom=1.1
            if abs(y+.15)<.01 and 8.75<x<10.50:continue
            for j in range(max(1,int((top-bottom)/.34))):
                R.box((x+.12*(j%2),y,top-.18-j*.32),(.52,.38,.28),random.choice(['stone','rockLight','rock']))
    for y in [.2,.8,1.4,2.0,2.6,3.2,3.8]:R.ico((5.25,y,1.42),(.33,.43,.41),'rockLight')
    R.finish(.025)

PATHS=[]
def paving(points,w=1.5,name='Walkway'):
    B=Build(name,'02 Paths & stairs');pts=smoothline(points,steps=5)
    PATHS.append((points,w))
    for a,b in zip(pts[:-1],pts[1:]):
        d=b-a;length=math.hypot(d.x,d.y)
        if length<.03:continue
        R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z');cols_n=max(2,round(w/.38))
        for j in range(cols_n):
            p=(a+b)/2+R@Vector((0,(j+.5-cols_n/2)*w/cols_n,0))
            B.box((p.x,p.y,p.z),(.97*length,.93*w/cols_n,.085),random.choice(['paver','paverLight','paver','paverDark']),R)
    return B.finish(.014)

def plaza_and_routes():
    B=Build('Plaza • expanded concentric stone paving','02 Paths & stairs')
    B.cyl((0,0,1.15),4.75,.12,'grout',96)
    for row in range(11):
        rr=1.42+row*.30;N=int(2*pi*rr/.44)
        for i in range(N):
            a=2*pi*(i+.5*(row%2))/N;da=2*pi/N*.95;r1=rr-.136;r2=rr+.136
            v=[(r*cos(t),r*sin(t),z) for z in [1.19,1.26+random.uniform(-.009,.009)] for r,t in [(r1,a-da/2),(r2,a-da/2),(r2,a+da/2),(r1,a+da/2)]]
            B.add(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],random.choice(['paver','paver','paverLight','paverDark']))
    B.finish(.015)
    paving([(-3.8,-1.9,1.23),(-5,-2.5,1.22),(-7.0,-2.6,1.22),(-9,-3.4,1.22),(-10,-5.0,1.22),(-8.8,-6.3,1.22)],1.55,'Route • west cottages and market')
    paving([(-8.8,-6.3,1.22),(-6.3,-6.5,1.22),(-4.7,-6,1.22),(-.56,-5.36,1.22),(0,-4.25,1.25)],1.45,'Route • plaza to north bridge landing')
    paving([(-4.43,-8.84,1.15),(-3.4,-9.35,1.08),(0,-9.55,1.07),(3.9,-9.1,1.07),(6.6,-8.4,1.2),(8.4,-8.0,1.2)],1.55,'Route • entrance and south river promenade')
    paving([(2.8,-3.6,1.24),(4.4,-4.0,1.23),(5.4,-3.7,1.23),(6.0,-2.7,1.23)],1.35,'Route • eastern garden landing')
    paving([(8.4,-8.0,1.22),(10.1,-6.2,1.22),(10.65,-3.5,1.22),(11.45,-1.5,1.22)],1.1,'Route • east river walk')
    paving([(-8.5,5.2,2.69),(-5.5,5.25,2.69),(-1.4,5.25,2.69),(2.1,5.25,2.69),(5,4.65,2.69)],1.5,'Route • manor terrace')
    paving([(5.7,1.2,1.91),(6.2,.90,1.91),(7.2,.90,1.91)],1.2,'Route • middle terrace bakery entrance')
    paving([(11.45,.2,1.91),(11.65,.85,1.91),(11.48,1.8,1.91),(10.7,3.0,1.91),(8.8,2.9,1.91)],.8,'Route • upper pool garden circuit')
    paving([(5.0,4.5,2.69),(8.8,4.5,2.69)],1.15,'Route • hill terrace frontage')
    paving([(6.3,4.4,2.69),(6.5,4.8,2.69)],1.4,'Route • hill house entrance')
    paving([(-5.2,1.1,1.23),(-6.5,.8,1.23),(-8.5,.45,1.23),(-9.25,-.2,1.23)],1.3,'Route • western stall frontage')
    S=Build('Stairs • terrace connections and broad landings','02 Paths & stairs')
    def stairs(start,end,width,N):
        a=Vector(start);b=Vector(end);d=b-a;L=math.hypot(d.x,d.y);R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z')
        for i in range(N):
            p=a+d*((i+.5)/N);zz=a.z+(b.z-a.z)*(i+1)/N
            S.box((p.x,p.y,(a.z+zz)/2),(.98*L/N,width,zz-a.z+.1),'stone',R)
            S.box((p.x,p.y,zz+.045),(L/N+.025,width+.07,.09),'paverLight',R)
        direction=Vector((d.x,d.y,0)).normalized()
        for p,side in [(a,-1),(b,1)]:
            q=p+direction*.415*side
            S.box((q.x,q.y,p.z+.045),(.8,width+.2,.09),'paverLight',R)
        PATHS.append(([tuple(a),tuple(b)],width))
    stairs((-1.8,2.10,1.25),(-1.8,4.18,2.65),2.05,9)
    stairs((4.45,1.2,1.25),(5.9,1.2,1.87),1.35,5)
    stairs((6.4,2.8,1.89),(6.4,4.3,2.65),1.35,6)
    stairs((-6.8,.85,1.24),(-6.8,1.8,1.58),1.25,3)
    stairs((11.45,-1.5,1.23),(11.45,.2,1.89),.85,5)
    stairs((8.8,2.9,1.89),(8.8,4.2,2.65),1.05,6)
    S.finish(.025)

terrain();plaza_and_routes()
print('V2: carved terrain, three terraces and connected paved routes created')
