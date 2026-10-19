HOUSES=[
 ('01 • Copper Finch Manor',-1.3,7.05,2.60,4.7,3.35,3.65,0,True),
 ('02 • West merchant cottage',-7.15,3.3,1.52,3.1,2.75,3.05,-.13,False),
 ('03 • East hill cottage',6.5,6.15,2.60,2.65,2.6,2.45,.16,False),
 ('04 • Riverside baker',6.6,2.65,1.82,2.9,2.65,2.75,-.25,False),
 ('05 • Garden cottage',-6.15,-4.7,1.12,2.85,2.6,2.6,-.20,False),
 ('06 • Little mill house',8.2,-6.65,1.12,1.8,1.75,1.6,.12,False)]

def architecture():
    for name,x,y,z,w,d,h,angle,manor in HOUSES:
        ob=house(name,x,y,z,w,d,h,angle,manor);ob.scale=(.96,1.02,.80 if manor else .83)
        # A gentle overhang of the upper floor gives cottages a less rectangular outline.
        for v in ob.data.vertices:
            if h*.52+.30<v.co.z<h+.30:v.co.x*=1.035;v.co.y*=1.025
        D=Build('Architecture • porches, dormers and shutters • '+name,'03 Houses',(x,y,z),angle)
        H=h+.30
        # Rear and left-side windows complete the model for all viewpoints.
        for xx in [-w*.28,w*.28]:
            D.box((xx,d/2+.06,H/2),(.11,.12,H),'wood')
            for zz in [.3+h*.24,.3+h*.74]:
                ww=min(.55,w*.22);hh=min(.67,h*.26)
                D.box((xx,d/2+.12,zz),(ww+.18,.10,hh+.18),'wood')
                D.box((xx,d/2+.18,zz),(ww,.04,hh),'windowDark' if random.random()<.4 else 'windowWarm')
                D.box((xx,d/2+.22,zz),(.045,.045,hh),'wood')
                D.box((xx,d/2+.22,zz),(ww,.045,.045),'wood')
                D.box((xx,d/2+.19,zz-hh/2-.08),(ww+.22,.21,.09),'plank')
        for yy in [-d*.24,d*.24]:
            for zz in [.3+h*.24,.3+h*.74]:
                ww=min(.54,d*.25);hh=min(.66,h*.26)
                D.box((-w/2-.1,yy,zz),(.10,ww+.18,hh+.18),'wood')
                D.box((-w/2-.17,yy,zz),(.04,ww,hh),'windowWarm')
                D.box((-w/2-.2,yy,zz),(.045,.045,hh),'wood')
                D.box((-w/2-.2,yy,zz),(.045,ww,.045),'wood')
        # Recesses, varied shutters and fine diagonal timber braces.
        for xx in [-w*.28,w*.28]:
            zz=h*.72+.25
            if random.random()<.6:D.box((xx,-d/2-.189,zz),(.23,.026,.65),'windowDark')
            for side in [-1,1]:
                sx=xx+side*.43
                for j in range(3):D.box((sx+(j-1)*.058,-d/2-.19,zz),(.05,.055,.70),'woodLight')
                D.box((sx,-d/2-.23,zz-.21),(.21,.04,.055),'wood')
                D.box((sx,-d/2-.23,zz+.21),(.21,.04,.055),'wood')
        for side in [-1,1]:
            D.beam((side*w*.48,-d/2-.095,h*.53+.3),(side*w*.26,-d/2-.095,h*.53+.75),.075,'wood')
        # Eaves are layered beams; dark gutters follow the long roof edges.
        if manor:
            for yy in [-d/2-.28,d/2+.28]:
                D.beam((-w/2-.25,yy,H-.03),(w/2+.25,yy,H-.03),.16,'wood')
                D.beam((-w/2-.27,yy,H-.10),(w/2+.27,yy,H-.10),.06,'iron')
        else:
            for xx in [-w/2-.28,w/2+.28]:
                D.beam((xx,-d/2-.26,H-.02),(xx,d/2+.26,H-.02),.15,'wood')
                D.beam((xx,-d/2-.25,H-.13),(xx,d/2+.25,H-.13),.055,'iron')
            # Small roof dormer facing the square on alternate cottages.
            if 'merchant' in name or 'baker' in name:
                dx=.48;dy=-.22;dz=H+w*.34
                D.box((dx,dy,dz),(.55,.58,.62),'plaster')
                D.box((dx,dy-.31,dz),(.28,.035,.35),'windowWarm')
                D.box((dx,dy-.34,dz),(.035,.04,.36),'wood')
                for s in [-1,1]:D.box((dx+s*.19,dy,dz+.40),(.48,.76,.08),'roofLight',Matrix.Rotation(s*pi/4,3,'Y'))
        # Visible chimney masonry.
        cx=-w*.27;cy=d*.18;cz=H+(d*.67 if manor else w*.57)*.66
        for j in range(5):
            D.box((cx,cy-.235,cz-.12+j*.24),(.43,.018,.026),'paverDark')
            for sx in [-.10,.10]:D.box((cx+sx,cy-.25,cz-.03+j*.24),(.018,.02,.16),'paverDark')
        # Short timber porch roofs and corner supports.
        doorx=0 if manor else w*.18;py=-d/2-.40
        D.box((doorx,py,1.77),(1.2,.75,.11),'plank',Matrix.Rotation(.16,3,'X'))
        for xx in [doorx-.48,doorx+.48]:
            D.beam((xx,py-.25,.22),(xx,py-.25,1.76),.075,'wood')
            D.beam((xx,py-.25,1.46),(xx,py+.13,1.76),.06,'woodLight')
        detail=D.finish(.014);detail.scale=ob.scale
        # A low side annex varies the silhouette of the mill and baker.
        if 'mill' in name:
            E=Build('Architecture • side lean-to • '+name,'03 Houses',(x,y,z),angle)
            E.box((w*.62,d*.12,.68),(w*.40,d*.65,1.36),'plaster')
            for yy in [-d*.20,d*.44]:E.box((w*.81,yy,.7),(.09,.09,1.4),'wood')
            for k in range(7):
                for j in range(6):E.box((w*.47+k*w*.048,-d*.24+j*d*.13,1.58-(k/7)*.36),(.20,.27,.065),'roof' if (j+k)%3 else 'roofLight',Matrix.Rotation(.5,3,'Y'))
            E.finish(.018).scale=ob.scale
    stall('Market • apple and preserves',-4.9,.10,1.23,'red',-.20)
    stall('Market • blue vegetable stall',4.3,1.65,1.23,'blue',.18)
    stall('Market • manor bakery',-5.05,6.1,2.65,'orange',0)
    stall('Market • western fish stall',-9.1,-.65,1.23,'blue',-.35)

def water_and_fountain():
    W=Build('River • recessed pools and curved current','06 River & waterfalls')
    def surface(points,width):
        for i in range(len(points)-1):
            a,b=Vector(points[i]),Vector(points[i+1]);d=b-a;side=Vector((-d.y,d.x,0)).normalized()
            wa=width*(1+.09*sin(i*.85));v=[a-side*wa/2,a+side*wa/2,b+side*wa/2,b-side*wa/2]
            W.add(v,[(0,1,2,3)],'water')
    surface(RIVER,1.55)
    W.cyl(UPPER,1.24,.035,'water',64)
    W.cyl((9,-1.28,.28),1.05,.035,'water',64)
    W.cyl((6.9,-4.75,.28),1.2,.035,'water',64)
    surface(smoothline([(UPPER[0],UPPER[1],1.48),(10.7,1.3,1.48),(11.9,1.45,1.48)]),.85)
    W.finish()
    F=Build('Waterfalls • upper cascade and island outflows','06 River & waterfalls')
    def waterfall(points,width,tail=False):
        pts=smoothline(points,steps=5)
        for k in range(23):
            v=[]
            for j,p in enumerate(pts):
                t=j/(len(pts)-1)
                a=pts[max(0,j-1)];b=pts[min(len(pts)-1,j+1)]
                dx=b.x-a.x;dy=b.y-a.y
                if dx*dx+dy*dy<.0001:dx=points[-1][0]-points[0][0];dy=points[-1][1]-points[0][1]
                side=Vector((-dy,dx,0)).normalized()
                taper=(1-.55*t**5) if tail else 1
                for s in [0,1]:
                    off=((k+s)/23-.5)*width*taper+.014*sin(j*1.1+k)
                    v.append(p+side*off)
            F.add(v,[(j*2,j*2+1,j*2+3,j*2+2) for j in range(len(pts)-1)],'foam' if k in [0,7,15,22] else 'waterLight')
        end=Vector(points[-1])
        for k in range(45):
            a=random.random()*2*pi;r=random.uniform(.04,width*.6)
            F.ico(end+Vector((r*cos(a),r*sin(a),random.uniform(0,.2))),(.055,.055,.05),'foam')
    waterfall([(9.65,-.20,1.48),(9.65,-.40,1.43),(9.5,-.57,1.14),(9.4,-.70,.35),(9,-1.2,.28)],1.65)
    waterfall([(-8.9,-8.0,.28),(-9.65,-8.1,.28),(-9.9,-8.23,-.15),(-10.0,-8.26,-2.5),(-10.1,-8.28,-3.15)],1.35,True)
    waterfall([(11.2,1.50,1.48),(11.9,1.45,1.48),(12.1,1.4,1.1),(12.2,1.35,-2.5),(12.3,1.3,-3.05)],.85,True)
    waterfall([(-11,-3.9,1.05),(-11.65,-4.1,.92),(-11.9,-4.15,-1.9),(-12,-4.2,-2.9)],.48,True)
    F.finish()
    B=Build('Riverbanks • embedded rocks, foam and ripples','06 River & waterfalls')
    for i,p in enumerate(RIVER):
        if i%2:continue
        d=RIVER[min(i+1,len(RIVER)-1)]-RIVER[max(0,i-1)];side=Vector((-d.y,d.x,0)).normalized()
        for s in [-1,1]:
            q=p+side*s*random.uniform(.9,1.12);z=max(.36,landheight(q.x,q.y))
            B.ico((q.x,q.y,z+.07),(.32,.30,.28),random.choice(['rockLight','stone','rock']))
            if i%4==0:B.ico((q.x,q.y,z+.23),(.24,.23,.09),'moss')
        for j in range(3):
            q=p+side*random.uniform(-.58,.58)
            B.ico((q.x,q.y,.309),(.08,.025,.009),'foam')
    for i in range(44):
        a=i*2*pi/44;x=UPPER[0]+1.42*cos(a);y=UPPER[1]+1.40*sin(a)
        B.ico((x,y,max(1.5,landheight(x,y))+.02),(.23,.24,.18),random.choice(['rockLight','stone']))
    for c,r,z in [((9,-.95),.30,.32),((UPPER[0],UPPER[1]),.75,1.506),((7,-4.7),.64,.31)]:
        for j in range(4):
            a=random.random()*2*pi;pts=[(c[0]+r*cos(a+k*.07),c[1]+r*sin(a+k*.07),z) for k in range(8)]
            ribbon(B,pts,.022,'foam')
    B.finish(.012)
    fountain()
    D=Build('Fountain • carved rim, spouts and water jets','05 Crystal fountain')
    ring(D,(0,0),1.46,1.62,1.48,.10,'paverLight',64)
    ring(D,(0,0),1.36,1.56,1.92,.07,'stone',64)
    for i in range(8):
        a=i*2*pi/8;D.box((1.45*cos(a),1.45*sin(a),1.67),(.12,.12,.32),'paverDark',Matrix.Rotation(a,3,'Z'))
        if i%2==0:
            start=Vector((.61*cos(a),.61*sin(a),2.04))
            pts=[start+Vector((.45*t*cos(a),.45*t*sin(a),.55*sin(pi*t)-.27*t)) for t in [k/16 for k in range(17)]]
            for p,q in zip(pts[:-1],pts[1:]):D.beam(p,q,.022,'waterLight',False)
            ring(D,(1.04*cos(a),1.04*sin(a)),.055,.11,1.77,.013,'foam',16)
    D.finish(.012)
    for k in ['crystal','crystalLight','crystalDark']:
        p=next(n for n in M[k].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        p.inputs['Transmission Weight'].default_value=.16;p.inputs['IOR'].default_value=1.45
        p.inputs['Emission Strength'].default_value=.55 if k!='crystalLight' else 1.3
    light=bpy.data.lights.new('Crystal • local cyan glow','POINT');light.energy=20;light.color=(.02,.65,1);light.shadow_soft_size=.5
    ob=bpy.data.objects.new(light.name,light);cols['10 Lighting & cameras'].objects.link(ob);ob.location=(0,0,2.5)

BRIDGE_CENTER=Vector((-2.5,-7.1,0));BRIDGE_AXIS=Vector((.744,.668,0)).normalized();BRIDGE_SIDE=Vector((-BRIDGE_AXIS.y,BRIDGE_AXIS.x,0))
def bp(s,w,z):return BRIDGE_CENTER+BRIDGE_AXIS*s+BRIDGE_SIDE*w+Vector((0,0,z))
def crossings_and_rails():
    B=Build('Bridge • broad diagonal masonry arch','07 Bridges & fences');N=27;L=5.25;w=2.25
    for i in range(N):
        ta=i/N;tb=(i+1)/N;s0=(ta-.5)*L;s1=(tb-.5)*L
        z0=1.15+.48*sin(pi*ta);z1=1.15+.48*sin(pi*tb)
        inner0=-.08+1.17*sin(pi*ta)**.72;inner1=-.08+1.17*sin(pi*tb)**.72
        for j in range(6):
            u0=-w/2+j*w/6+.01;u1=u0+w/6-.02
            B.add([bp(s0,u0,z0-.13),bp(s0,u1,z0-.13),bp(s1,u1,z1-.13),bp(s1,u0,z1-.13),bp(s0,u0,z0),bp(s0,u1,z0),bp(s1,u1,z1),bp(s1,u0,z1)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],random.choice(['paver','paverLight','stone']))
        for side in [-1,1]:
            u0=side*(w/2+.12)-.13;u1=u0+.26
            v=[bp(s0,u0,inner0),bp(s0,u1,inner0),bp(s1,u1,inner1),bp(s1,u0,inner1),bp(s0,u0,z0+.30),bp(s0,u1,z0+.30),bp(s1,u1,z1+.30),bp(s1,u0,z1+.30)]
            B.add(v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone' if i%3 else 'paverLight')
            B.beam(bp(s0,side*(w/2+.12),z0+.35),bp(s1,side*(w/2+.12),z1+.35),.20,'paverLight')
    B.finish(.022)
    # Timber footbridge spans the wider lower river pool.
    W=Build('Bridge • lower pool timber crossing','07 Bridges & fences')
    x0=6.8;x1=10.45;y=-3.05;z=1.21
    for i in range(22):W.box((x0+(i+.5)*(x1-x0)/22,y,z),((x1-x0)/22-.014,1.18,.13),'plank')
    for yy in [y-.54,y+.54]:
        W.beam((x0,yy,z-.14),(x1,yy,z-.14),.15,'wood')
        for xx in [x0,x0+1.2,x0+2.4,x1]:W.box((xx,yy,z+.42),(.12,.12,.91),'woodLight')
        for zz in [z+.25,z+.70]:W.beam((x0,yy,zz),(x1,yy,zz),.085,'plank')
    for xx in [x0+.2,x1-.2]:
        for yy in [y-.46,y+.46]:W.box((xx,yy,.68),(.16,.16,1.12),'wood')
    W.finish(.02)
    paving([(6,-2.7,1.23),(6.8,-3.05,1.24)],1.18,'Route • timber bridge west landing')
    paving([(10.45,-3.05,1.24),(10.65,-3.5,1.24)],1.18,'Route • timber bridge east landing')
    F=Build('Railings • garden boundaries and stairs','07 Bridges & fences')
    def fence(points):
        for a,b in zip(points[:-1],points[1:]):
            a=Vector(a);b=Vector(b);N=max(1,round((b-a).length/.9))
            for j in range(N+1):
                p=a+(b-a)*j/N
                F.box(p+Vector((0,0,.40)),(.11,.11,.80),'woodLight')
                F.cyl(p+Vector((0,0,.82)),.085,.085,'plank',6)
            for zz in [.24,.65]:F.beam(a+Vector((0,0,zz)),b+Vector((0,0,zz)),.075,'plank')
    for a0,a1 in [(15,40),(55,74),(82,108),(118,146),(158,190),(200,222),(260,283),(290,320),(326,340)]:
        pts=[]
        for j in range(8):
            a=math.radians(a0+(a1-a0)*j/7);r=outline(a)-.65;x=r*cos(a);y=.88*r*sin(a)
            if landheight(x,y)<.55:continue
            pts.append((x,y,landheight(x,y)+.04))
        fence(pts)
    fence([(-7.8,4.06,2.65),(-3,4.06,2.65)])
    fence([(-.55,4.06,2.65),(4.8,4.06,2.65)])
    fence([(-2.92,2.08,1.3),(-2.92,4.18,2.68)])
    fence([(-.68,2.08,1.3),(-.68,4.18,2.68)])
    fence([(5.28,-.2,1.87),(7.25,-.2,1.87)])
    F.finish(.02)

architecture();water_and_fountain();crossings_and_rails()
print('V2: shorter detailed buildings, recessed water, fountain jets and diagonal stone bridge created')
