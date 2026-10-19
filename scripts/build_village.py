import bpy, math, random, os, json, shutil
from mathutils import Vector, Matrix
from math import sin, cos, pi

OUT = os.environ.get('VILLAGE_PROJECT_DIR', r'D:\codex+blender\village')
random.seed(27)
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, 'renders'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'references'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'scripts'), exist_ok=True)

# A fresh scene preserves anything that may already exist in the current file.
scene = bpy.data.scenes.new('Crystalbrook Village')
bpy.context.window.scene = scene
cols = {}
for name in ['01 Island & cliffs','02 Paths & stairs','03 Houses','04 Market','05 Crystal fountain','06 River & waterfalls','07 Bridges & fences','08 Trees & gardens','09 Village props','10 Lighting & cameras']:
    c=bpy.data.collections.new(name); scene.collection.children.link(c); cols[name]=c

def mat(name, color, rough=.65, metal=0, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    return m

M={}
pal={
'grass':(.24,.40,.075),'grassLight':(.39,.53,.10),'moss':(.18,.30,.065),'soil':(.20,.16,.085),
'rock':(.34,.38,.40),'rockLight':(.46,.48,.46),'rockDark':(.22,.27,.30),'stone':(.62,.59,.48),
'paver':(.72,.66,.52),'paverLight':(.82,.74,.59),'paverDark':(.60,.55,.45),'grout':(.40,.38,.31),
'plaster':(.91,.79,.56),'plasterLight':(.99,.90,.71),'wood':(.23,.105,.043),'woodLight':(.42,.22,.08),
'plank':(.54,.31,.12),'roof':(.63,.14,.045),'roofLight':(.83,.25,.075),'roofDark':(.43,.075,.028),
'red':(.86,.08,.035),'blue':(.035,.32,.67),'cream':(.99,.93,.75),'iron':(.055,.085,.09),
'leaf':(.22,.40,.055),'leafLight':(.40,.57,.075),'leafDark':(.08,.25,.085),'pine':(.14,.34,.10),
'flowerYellow':(1,.64,.025),'flowerWhite':(.96,.91,.75),'flowerBlue':(.29,.28,.84),'flowerPink':(.87,.22,.40),
'apple':(.72,.065,.025),'orange':(1,.39,.015),'sack':(.57,.44,.22),'gold':(.72,.46,.10),
}
for k,v in pal.items(): M[k]=mat(k,v)
M['water']=mat('Turquoise river',(.015,.48,.69),.20,.12)
M['waterLight']=mat('Waterfall cyan',(.06,.68,.93),.24,.06,.18)
M['foam']=mat('Foam and water glints',(.63,.97,1),.30,0,.25)
M['crystal']=mat('Crystal azure',(.01,.45,1),.17,.18,.8)
M['crystalLight']=mat('Crystal bright facets',(.055,.83,1),.15,.10,1.25)
M['crystalDark']=mat('Crystal deep facets',(.015,.18,.61),.20,.20,.35)
M['glow']=mat('Amber window glass',(1,.48,.085),.24,0,2.0)

cubev=[(-.5,-.5,-.5),(-.5,-.5,.5),(-.5,.5,-.5),(-.5,.5,.5),(.5,-.5,-.5),(.5,-.5,.5),(.5,.5,-.5),(.5,.5,.5)]
cubef=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
class Build:
    def __init__(self,name,col,origin=(0,0,0),angle=0):
        self.name=name; self.col=col; self.v=[]; self.f=[]; self.mi=[]; self.mats=[]; self.origin=origin; self.angle=angle
    def add(self,v,f,m):
        if isinstance(m,str): m=M[m]
        if m not in self.mats:self.mats.append(m)
        idx=self.mats.index(m); off=len(self.v); self.v.extend(v); self.f.extend([tuple(off+i for i in q) for q in f]); self.mi.extend([idx]*len(f))
    def box(self,p,d,m,rot=None):
        R=Matrix.Identity(3) if rot is None else rot
        self.add([Vector(p)+R@Vector((q[0]*d[0],q[1]*d[1],q[2]*d[2])) for q in cubev],cubef,m)
    def cyl(self,p,r,h,m,n=12,r2=None):
        r2=r if r2 is None else r2
        v=[(p[0]+rr*cos(2*pi*i/n),p[1]+rr*sin(2*pi*i/n),p[2]+z) for rr,z in [(r,-h/2),(r2,h/2)] for i in range(n)]
        f=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        self.add(v,f,m)
    def beam(self,a,b,r,m,square=True):
        a,b=Vector(a),Vector(b); delta=b-a; R=delta.to_track_quat('Z','Y').to_matrix()
        if square:self.box((a+b)/2,(r,r,delta.length),m,R)
        else:
            n=7; v=[(a+b)/2+R@Vector((r*cos(2*pi*i/n),r*sin(2*pi*i/n),z)) for z in [-delta.length/2,delta.length/2] for i in range(n)]
            self.add(v,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
    def ico(self,p,s,m):
        t=(1+5**.5)/2
        vv=[(-1,t,0),(1,t,0),(-1,-t,0),(1,-t,0),(0,-1,t),(0,1,t),(0,-1,-t),(0,1,-t),(t,0,-1),(t,0,1),(-t,0,-1),(-t,0,1)]
        ff=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
        self.add([(p[0]+q[0]*s[0]/1.9,p[1]+q[1]*s[1]/1.9,p[2]+q[2]*s[2]/1.9) for q in vv],ff,m)
    def finish(self,bevel=0):
        mesh=bpy.data.meshes.new(self.name); mesh.from_pydata(self.v,[],self.f); mesh.materials.clear()
        for m in self.mats:mesh.materials.append(m)
        mesh.update(); ob=bpy.data.objects.new(self.name,mesh); cols[self.col].objects.link(ob)
        for poly,idx in zip(mesh.polygons,self.mi):poly.material_index=idx
        ob.location=self.origin; ob.rotation_euler.z=self.angle
        if bevel:
            mod=ob.modifiers.new('Soft handmade edges','BEVEL');mod.width=bevel;mod.segments=2
        return ob

def ring(B,c,r1,r2,z,h,m,n=64):
    for i in range(n):
        a=2*pi*i/n;b=2*pi*(i+1)/n
        vs=[(c[0]+r*cos(t),c[1]+r*sin(t),zz) for zz in [z-h/2,z+h/2] for r,t in [(r1,a),(r2,a),(r2,b),(r1,b)]]
        B.add(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)

def ribbon(B,points,width,matname,thick=.08):
    for i in range(len(points)-1):
        a,b=Vector(points[i]),Vector(points[i+1]); d=b-a
        side=Vector((-d.y,d.x,0)).normalized()*width/2
        v=[a-side,a+side,b+side,b-side]
        B.add(v,[(0,1,2,3)],matname)

def height(x,y):
    # Raised northern terrace and lower southern river valley.
    return 2.6 if y>4.2 else 1.15

def build_land():
    B=Build('Island • grass and earth','01 Island & cliffs')
    n=96; radii=[12.15+.32*sin(i*.73)+.18*cos(i*1.91) for i in range(n)]
    top=[(radii[i]*cos(2*pi*i/n),radii[i]*.88*sin(2*pi*i/n),1.0) for i in range(n)]
    bottom=[(p[0]*.93,p[1]*.93,-1.7-random.random()*.55) for p in top]
    B.add(top+bottom,[tuple(range(n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]+[tuple(range(2*n-1,n-1,-1))],'soil')
    B.add([(0,0,1.10)]+[(p[0],p[1],1.10+random.uniform(-.04,.04)) for p in top],[(0,i+1,(i+1)%n+1) for i in range(n)],'grass')
    # Broad rear raised terrace.
    pts=[(-10.5,4.1),(-9.4,7.3),(-6.4,9.1),(0,10.45),(5,9.4),(9.3,6.5),(10.4,4.1)]
    v=[(x,y,z) for z in [1,2.6] for x,y in pts];n2=len(pts)
    B.add(v,[tuple(range(n2,2*n2))]+[(i,(i+1)%n2,(i+1)%n2+n2,i+n2) for i in range(n2)],'grass')
    B.finish(.08)
    R=Build('Cliffs • layered angular stone','01 Island & cliffs')
    for i in range(106):
        a=2*pi*i/106;r=12.0+random.uniform(-.2,.15);x=r*cos(a);y=.88*r*sin(a)
        for j in range(2):
            z=-.05-j*1.30+random.uniform(-.3,.1)
            R.ico((x*(1-.035*j),y*(1-.035*j),z),(random.uniform(.65,1.2),random.uniform(.7,1.3),random.uniform(1.2,2.0)),random.choice(['rock','rock','rockLight','rockDark']))
    for i in range(95):
        a=random.uniform(0,2*pi); rr=random.random()**.5*11.3
        x=rr*cos(a);y=rr*.88*sin(a);z=-2.0-1.1*(1-rr/12)
        R.ico((x,y,z),(random.uniform(1,2),random.uniform(1,2),random.uniform(.8,1.7)),random.choice(['rock','rockDark']))
    for x in [-9.5,-8,-6.5,-5,-3.5,-2,0,2,3.5,5,6.5,8,9.5]:
        R.ico((x,4.13,1.75),(1.1,.56,.96),random.choice(['rock','rockLight']))
    R.finish()
    P=Build('Plaza • concentric hand laid paving','02 Paths & stairs')
    P.cyl((0,0,1.14),4.55,.12,'grout',96)
    for row in range(10):
        rad=1.45+row*.31;cnt=int(2*pi*rad/.51)
        for i in range(cnt):
            a=2*pi*(i+(row%2)*.5)/cnt;da=2*pi/cnt*.93;r1=rad-.137;r2=rad+.137
            v=[(r*cos(t),r*sin(t),z) for z in [1.18,1.25+random.uniform(-.008,.008)] for r,t in [(r1,a-da/2),(r2,a-da/2),(r2,a+da/2),(r1,a+da/2)]]
            P.add(v,cubef if False else [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],random.choice(['paver','paver','paverLight','paverDark']))
    P.finish(.018)
    # Paths stay above the grass; river crosses beneath the front bridge.
    paths=Build('Village walkways • laid flagstones','02 Paths & stairs')
    def path(points,w=1.7):
        for j in range(len(points)-1):
            a,b=Vector(points[j]),Vector(points[j+1]);d=b-a;L=d.length;R=Matrix.Rotation(math.atan2(d.y,d.x),3,'Z')
            rows=max(1,int(L/.43));nc=max(2,int(w/.42))
            for k in range(rows):
                for c in range(nc):
                    pp=a+d*((k+.5)/rows)+R@Vector((0,(c+.5-nc/2)*w/nc,0))
                    paths.box((pp.x,pp.y,pp.z),(.94*L/rows,.94*w/nc,.10),random.choice(['paver','paverLight','paverDark']),R)
    path([(-4,0,1.24),(-7,-1.7,1.24),(-9,-4,1.24),(-8.2,-6.5,1.24),(-5,-8.3,1.24),(-2.9,-8.7,1.24)])
    path([(2.7,-3.6,1.24),(5.4,-5.1,1.24),(8.7,-4.7,1.24),(10,-1.4,1.24),(9.7,1.7,1.24),(7,3.5,1.24)])
    path([(-2,3.9,1.24),(-2,4.1,1.24)],2.6)
    path([(-8.6,4.9,2.7),(-5,5.2,2.7),(0,5.0,2.7),(4.7,5.1,2.7),(8.6,5,2.7)],1.6)
    path([(0,-4.1,1.24),(0,-5.1,1.24)],2.1)
    path([(1.2,-9.1,1.24),(3.5,-8.8,1.24),(6.5,-7.9,1.24),(9.2,-6.3,1.24)],1.8)
    paths.finish(.018)
    stairs=Build('Terrace stairs • center and east','02 Paths & stairs')
    for x,y,w,rise,N in [(-1.9,2.20,2.1,1.45,8),(8.9,2.20,1.6,1.45,8),(-9.3,2.20,1.5,1.45,8)]:
        for i in range(N):
            stairs.box((x,y+i*.25,1.14+rise*(i+1)/(2*N)),(w,.28,rise*(i+1)/N),'stone')
    stairs.finish(.035)

build_land()
print('Island, terraces, paving and stairs created')

def house(name,x,y,z,w,d,h,angle=0,manor=False):
    B=Build(name,'03 Houses',(x,y,z),angle)
    B.box((0,0,.15),(w+.22,d+.22,.30),'stone')
    B.box((0,0,h/2+.3),(w,d,h),'plasterLight' if manor else 'plaster')
    # The main house has a long ridge; cottages turn their gable toward the square.
    H=h+.3; rise=w*.57 if not manor else d*.67
    if not manor:
        B.add([(-w/2,-d/2,H),(w/2,-d/2,H),(0,-d/2,H+rise),(-w/2,d/2,H),(w/2,d/2,H),(0,d/2,H+rise)],[(0,1,2),(3,5,4)],'plaster')
        for side in [-1,1]:
            for row in range(9):
                u=(row+.5)/9;xx=side*(w/2+.22)*u;zz=H+rise*(1-u)
                slope=math.atan2(rise,w/2+.22)*side
                for k in range(max(6,int(d/.24))):
                    yy=-d/2-.22+(k+.5)*(d+.44)/max(6,int(d/.24))
                    if row%2: yy+=.06
                    B.box((xx,yy,zz+.055),((w/2+.22)/9/math.cos(slope)*1.16,.245,.075),random.choice(['roof','roof','roofLight','roofDark']),Matrix.Rotation(slope,3,'Y'))
        for yy in [-d/2-.24,d/2+.24]:
            B.beam((-w/2-.24,yy,H),(0,yy,H+rise+.10),.14,'wood')
            B.beam((0,yy,H+rise+.10),(w/2+.24,yy,H),.14,'wood')
        B.beam((0,-d/2-.3,H+rise+.07),(0,d/2+.3,H+rise+.07),.16,'roofLight')
        B.beam((0,-d/2-.025,H),(0,-d/2-.025,H+rise-.12),.14,'wood')
        for xx in [-w*.25,w*.25]: B.beam((xx,-d/2-.04,H),(xx,-d/2-.04,H+rise*.45),.09,'wood')
    else:
        B.add([(-w/2,-d/2,H),(-w/2,d/2,H),(-w/2,0,H+rise),(w/2,-d/2,H),(w/2,d/2,H),(w/2,0,H+rise)],[(0,2,1),(3,4,5)],'plaster')
        rows=10;cnt=int(w/.25)
        for side in [-1,1]:
            for row in range(rows):
                u=(row+.5)/rows;yy=side*(d/2+.24)*u;zz=H+rise*(1-u);slope=-side*math.atan2(rise,d/2+.24)
                for k in range(cnt):
                    xx=-w/2-.2+(k+.5)*(w+.4)/cnt+(row%2)*.055
                    B.box((xx,yy,zz+.06),(.26,(d/2+.24)/rows/math.cos(slope)*1.15,.08),random.choice(['roof','roof','roofLight','roofDark']),Matrix.Rotation(slope,3,'X'))
        for xx in [-w/2-.2,w/2+.2]:
            B.beam((xx,-d/2-.26,H),(xx,0,H+rise+.10),.16,'wood')
            B.beam((xx,0,H+rise+.10),(xx,d/2+.26,H),.16,'wood')
        B.beam((-w/2-.25,0,H+rise+.09),(w/2+.25,0,H+rise+.09),.20,'roofLight')
        # Front dormer with its own tiled gable.
        dx=.45;dy=-d*.31;dz=H+rise*.49
        B.box((dx,dy,dz+.30),(1.0,.78,.85),'plasterLight')
        B.add([(dx-.53,dy-.43,dz+.72),(dx+.53,dy-.43,dz+.72),(dx,dy-.43,dz+1.30)],[(0,1,2)],'plaster')
        for side in [-1,1]:
            for j in range(4):
                xx=side*(j+.5)*.15
                B.box((dx+xx,dy,dz+1.30-abs(xx)),(.23,1.02,.08),'roofLight',Matrix.Rotation(side*pi/4,3,'Y'))
        for xx in [dx-.5,dx+.5]:B.box((xx,dy-.44,dz+.35),(.09,.09,.8),'wood')
        B.box((dx,dy-.46,dz+.37),(.36,.04,.46),'glow')
        B.box((dx,dy-.5,dz+.37),(.045,.04,.48),'wood')
    # Foundation blocks and two levels of exposed timber framing.
    for xx in [-w/2,w/2]:
        for yy in [-d/2-.025,d/2+.025]:B.box((xx,yy,H/2),(.17,.17,H),'wood')
    for zz in [.35,h*.52+.3,H-.06]:
        B.box((0,-d/2-.045,zz),(w+.16,.15,.16),'wood')
        B.box((0,d/2+.045,zz),(w+.16,.15,.16),'wood')
        B.box((-w/2-.025,0,zz),(.15,d,.16),'wood')
        B.box((w/2+.025,0,zz),(.15,d,.16),'wood')
    for xx in [-w*.25,0,w*.25]:B.box((xx,-d/2-.055,H/2),(.12,.12,H),'wood')
    for yy in [-d*.25,d*.25]:B.box((w/2+.04,yy,H/2),(.13,.13,H),'wood')
    # Recessed windows with glowing panes, heavy lintels and shutters.
    def window(xx,yy,zz,side=False,ww=.57,hh=.72):
        R=Matrix.Rotation(pi/2,3,'Z') if side else Matrix.Identity(3)
        pos=Vector((xx,yy,zz))
        for off,dim,m in [((0,0,0),(ww+.20,.10,hh+.20),'wood'),((0,-.062,0),(ww,.04,hh),'glow'),((0,-.096,0),(.055,.05,hh),'wood'),((0,-.096,0),(ww,.05,.055),'wood'),((0,-.13,-hh/2-.09),(ww+.30,.25,.10),'plank')]:
            B.box(pos+R@Vector(off),dim,m,R)
        for s in [-1,1]:
            B.box(pos+R@Vector((s*(ww/2+.16),-.03,0)),(.19,.10,hh+.1),'woodLight',R)
    for xx in [-w*.28,w*.28]:
        window(xx,-d/2-.12,h*.72+.25)
    if manor:
        for xx in [-w*.32,w*.32]:window(xx,-d/2-.12,h*.22+.3)
    else:window(-w*.27,-d/2-.12,h*.24+.3,ww=.48,hh=.58)
    for yy in [-d*.25,d*.25]:
        window(w/2+.12,yy,h*.72+.25,True)
        window(w/2+.12,yy,h*.24+.3,True,ww=.48,hh=.58)
    # Front door and entrance steps.
    doorx=0 if manor else w*.18
    B.box((doorx,-d/2-.10,.94),(.79,.12,1.43),'wood')
    for k in range(5):B.box((doorx+(k-2)*.13,-d/2-.18,.92),(.115,.08,1.32),'woodLight')
    B.box((doorx,-d/2-.24,1.35),(.49,.04,.38),'glow')
    B.ico((doorx+.23,-d/2-.26,.82),(.06,.06,.06),'gold')
    for i in range(2):B.box((doorx,-d/2-.30-i*.22,.18-i*.07),(1.08,.48,.20),'stone')
    # Chimney, caps and little flower boxes.
    cx=-w*.27;cy=d*.18;cz=H+rise*.66
    B.box((cx,cy,cz+.48),(.42,.44,1.35),'stone')
    B.box((cx,cy,cz+1.13),(.54,.56,.13),'paverLight')
    B.box((cx,cy,cz+1.21),(.29,.30,.03),'rockDark')
    for xx in [-w*.28,w*.28]:
        B.box((xx,-d/2-.31,h*.72-.22),(.79,.33,.20),'plank')
        for k in range(5):
            B.ico((xx+(k-2)*.13,-d/2-.34,h*.72-.05),(.18,.17,.16),'leaf')
            B.ico((xx+(k-2)*.13,-d/2-.39,h*.72+.035),(.07,.07,.08),random.choice(['flowerYellow','flowerPink','flowerWhite']))
    return B.finish(.022)

house('01 • The Copper Finch Manor',-1.3,7.05,2.60,4.7,3.35,3.65,0,True)
house('02 • West merchant cottage',-7.15,3.3,1.15,3.1,2.75,3.05,-.13)
house('03 • East hill cottage',6.3,5.9,2.60,2.65,2.6,2.45,.16)
house('04 • Riverside baker',7.35,.75,1.15,2.9,2.65,2.75,-.25)
house('05 • Garden cottage',-6.15,-4.7,1.15,2.85,2.6,2.6,-.20)
house('06 • Little mill house',8.2,-6.65,1.15,1.8,1.75,1.6,.12)

def stall(name,x,y,z,color,angle=0):
    B=Build(name,'04 Market',(x,y,z),angle);w=2.0;d=1.55
    for xx in [-w/2,w/2]:
        for yy in [-d/2,d/2]:B.box((xx,yy,1.12),(.105,.105,2.24),'wood')
    B.box((0,0,.75),(2.07,1.36,.15),'plank')
    B.box((0,.57,.42),(2,.12,.72),'woodLight')
    for xx in [-.92,.92]:B.box((xx,0,.43),(.12,1.25,.72),'woodLight')
    # Curved fabric canopy built as alternating strips, with a scalloped valance.
    for k in range(10):
        x1=-1.14+k*.228;x2=x1+.228;verts=[]
        for j in range(13):
            yy=-.99+j*1.98/12; zz=2.25+.32*cos(yy/1.98*pi)
            verts.extend([(x1,yy,zz),(x2,yy,zz)])
        B.add(verts,[(2*j,2*j+1,2*j+3,2*j+2) for j in range(12)],color if k%2==0 else 'cream')
        B.add([(x1,-.99,2.25),(x2,-.99,2.25),(x2,-.99,2.08),(x1+.114,-.99,2.02),(x1,-.99,2.08)],[(0,1,2,3,4)],color if k%2==0 else 'cream')
    for xx in [-.61,0,.61]:
        B.box((xx,-.17,.91),(.53,.73,.18),'wood')
        for k in range(13):
            B.ico((xx+random.uniform(-.20,.2),random.uniform(-.43,.08),1.04),(.105,.105,.095),random.choice(['apple','orange','flowerYellow']) if color=='red' else random.choice(['leafLight','orange','sack']))
    B.box((0,-.75,.4),(1.8,.12,.63),'woodLight')
    for xx in [-.65,.65]:B.beam((xx,-.82,.15),(xx,-.82,.67),.05,'wood')
    return B.finish(.018)

stall('Market • red apple stall',-4.8,.35,1.23,'red',-.22)
stall('Market • blue produce stall',4.25,1.85,1.23,'blue',.18)
stall('Market • golden bakery stall',-5.25,6.0,2.68,'orange',0)
stall('Market • striped western stall',-8.8,-.65,1.23,'blue',-.40)

def fountain():
    B=Build('Fountain • stone basin and garden ring','05 Crystal fountain')
    B.cyl((0,0,1.32),1.58,.23,'paverDark',48)
    ring(B,(0,0),1.24,1.49,1.62,.38,'stone',40)
    ring(B,(0,0),1.19,1.55,1.85,.12,'paverLight',40)
    for i in range(32):
        a=2*pi*i/32
        B.box((1.38*cos(a),1.38*sin(a),1.63),(.23,.26,.31),'paverLight' if i%3==0 else 'stone',Matrix.Rotation(a,3,'Z'))
    B.cyl((0,0,1.73),1.23,.045,'water',64)
    B.cyl((0,0,1.80),.56,.22,'stone',12)
    ring(B,(0,0),1.86,2.04,1.30,.15,'stone',64)
    B.finish(.025)
    C=Build('Fountain • faceted luminous crystal','05 Crystal fountain')
    def crystal(p,r,h,tilt=0):
        n=6;v=[(p[0],p[1],p[2])]+[(p[0]+r*cos(2*pi*i/n),p[1]+r*sin(2*pi*i/n),p[2]+h*.37) for i in range(n)]+[(p[0]+r*.72*cos(2*pi*i/n),p[1]+r*.72*sin(2*pi*i/n),p[2]+h*.67) for i in range(n)]+[(p[0]+tilt,p[1],p[2]+h)]
        for i in range(n):
            j=(i+1)%n
            C.add(v,[(0,i+1,j+1),(i+1,i+7,j+7,j+1),(i+7,13,j+7)],['crystal','crystalLight','crystalDark'][i%3])
    crystal((0,0,1.95),.52,3.05,.1)
    crystal((-.54,-.15,1.95),.23,1.48,-.32)
    crystal((.48,.12,1.95),.22,1.80,.31)
    for i in range(12):
        a=i*2*pi/12
        C.ico((.87*cos(a),.87*sin(a),1.83),(.13,.13,.05),'foam')
    C.finish()

fountain()
print('Six timber houses, four market stalls and crystal fountain created')
