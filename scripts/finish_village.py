def smoothline(points,steps=9):
    p=[Vector(points[0])]+[Vector(q) for q in points]+[Vector(points[-1])];out=[]
    for k in range(1,len(p)-2):
        for j in range(steps):
            t=j/steps;a,b,c,d=p[k-1:k+3]
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    out.append(Vector(points[-1]));return out

def waterworks():
    B=Build('Brook • winding turquoise water','06 River & waterfalls')
    pts=smoothline([(9.1,3.8,1.32),(9,1.7,1.32),(9.3,-.3,1.32),(8.2,-2.5,1.32),(6.6,-4.8,1.32),(3.6,-6.4,1.32),(0,-7.2,1.32),(-3.6,-7.5,1.32),(-6.4,-8.3,1.32),(-8.25,-8.5,1.32)])
    ribbon(B,pts,1.60,'water')
    B.cyl((8.8,.2,1.31),1.6,.06,'water',48)
    B.cyl((5.6,-5.1,1.31),1.50,.06,'water',48)
    # Side overflow reaching the eastern cliff edge.
    ribbon(B,smoothline([(8.7,.0,1.32),(10.2,-.2,1.32),(11.95,-.6,1.32)]),1.1,'water')
    R=Build('Brook • banks, stepping rocks and foam','06 River & waterfalls')
    for i,p in enumerate(pts):
        if i%3:continue
        prev=pts[max(0,i-1)];nex=pts[min(len(pts)-1,i+1)];d=nex-prev;side=Vector((-d.y,d.x,0)).normalized()
        for s in [-1,1]:
            pos=p+side*s*random.uniform(.93,1.07)
            R.ico((pos.x,pos.y,1.30),(.32,.30,.22),random.choice(['stone','rockLight','moss']))
        for j in range(2):
            v=p+side*random.uniform(-.6,.6)
            R.ico((v.x,v.y,1.36),(random.uniform(.07,.22),.045,.012),'foam')
    for x,y in [(9,1.0),(8.4,-1),(6,-5.2),(-4.5,-7.5),(-7.3,-8.3)]:
        R.ico((x,y,1.47),(.35,.28,.26),'rockLight')
    B.finish();R.finish()
    W=Build('Waterfalls • cascading ribbons and droplets','06 River & waterfalls')
    def fall(start,forward,width,drop):
        x,y,z=start;fx,fy=forward;l=(fx*fx+fy*fy)**.5;fx/=l;fy/=l;sx=-fy;sy=fx
        for k in range(15):
            off=(k-7)*width/15;ww=width/15*1.05
            v=[]
            for j in range(11):
                t=j/10;u=.45*(1-math.exp(-t*7));zz=z-drop*t
                for ss in [-1,1]:
                    o=(off+ss*ww/2)*(1-.56*t**4)+.035*sin(t*16+k)
                    v.append((x+fx*u+sx*o,y+fy*u+sy*o,zz))
            W.add(v,[(j*2,j*2+1,j*2+3,j*2+2) for j in range(10)],'foam' if k in [0,4,10,14] else 'waterLight')
        for j in range(14):
            r=random.uniform(.04,width*.38);a=random.random()*2*pi
            W.ico((x+fx*.48+cos(a)*r,y+fy*.48+sin(a)*r*.65,z-drop+.04),(.07,.07,.11),'foam' if j%3 else 'waterLight')
        W.cyl((x+fx*.47,y+fy*.47,z-drop-.08),.025,.30,'waterLight',8,r2=width*.19)
        for j in range(14):
            t=random.uniform(.3,1.02);o=random.uniform(-width*.65,width*.65)
            W.ico((x+fx*.50+sx*o,y+fy*.50+sy*o,z-drop*t),(.045,.045,.13),'foam')
    fall((9.1,4.14,2.72),(0,-1),1.15,1.35)
    fall((11.94,-.6,1.33),(1,-.15),1.12,4.9)
    fall((-8.25,-8.55,1.33),(-.55,-1),1.45,4.6)
    fall((-10.1,-5.9,1.18),(-1,-.4),.46,4.25)
    W.finish()

waterworks()

def stonebridge():
    B=Build('Bridge • arched stone crossing','07 Bridges & fences')
    N=22;start=-5.20;end=-9.35;width=2.15
    def Z(t):return 1.30+1.45*sin(pi*t)
    for i in range(N):
        t0=i/N;t1=(i+1)/N;y0=start+(end-start)*t0;y1=start+(end-start)*t1
        za=Z(t0);zb=Z(t1)
        # Walkable stone deck, visible arch extrados and individual side voussoirs.
        for k in range(5):
            x1=-width/2+k*width/5+.012;x2=x1+width/5-.024
            B.add([(x1,y0,za-.24),(x2,y0,za-.24),(x2,y1,zb-.24),(x1,y1,zb-.24),(x1,y0,za),(x2,y0,za),(x2,y1,zb),(x1,y1,zb)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],random.choice(['stone','paver','paverLight']))
        for s in [-1,1]:
            x1=s*width/2-.13;x2=s*width/2+.13
            B.add([(x1,y0,za-.58),(x2,y0,za-.58),(x2,y1,zb-.58),(x1,y1,zb-.58),(x1,y0,za+.39),(x2,y0,za+.39),(x2,y1,zb+.39),(x1,y1,zb+.39)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone' if i%3 else 'paverLight')
            B.beam((s*width/2,y0,za+.44),(s*width/2,y1,zb+.44),.23,'paverLight')
    for yy in [start,end]:
        for xx in [-width/2,width/2]:B.box((xx,yy,.77),(.50,.58,1.15),'stone')
    B.finish(.025)

stonebridge()

def wooden_bridge():
    B=Build('Bridge • riverside timber footbridge','07 Bridges & fences')
    x0=5.55;x1=8.8;y=-4.55;z=1.57
    for i in range(17):B.box((x0+(i+.5)*(x1-x0)/17,y,z),((x1-x0)/17-.018,1.25,.16),'plank')
    for yy in [y-.54,y+.54]:
        B.beam((x0,yy,z-.18),(x1,yy,z-.18),.16,'wood')
        for xx in [x0,x0+1.1,x0+2.2,x1]:
            B.box((xx,yy,z+.43),(.13,.13,1.05),'woodLight')
            B.cyl((xx,yy,z+.98),.12,.10,'plank',8)
        for zz in [z+.30,z+.77]:B.beam((x0,yy,zz),(x1,yy,zz),.095,'woodLight')
    for xx in [x0+.2,x1-.2]:
        for yy in [y-.48,y+.48]:B.box((xx,yy,.85),(.18,.18,1.4),'wood')
    B.finish(.025)

wooden_bridge()

def fences():
    B=Build('Railings • perimeter and terrace fences','07 Bridges & fences')
    def fence(points):
        for j in range(len(points)-1):
            a,b=Vector(points[j]),Vector(points[j+1]);N=max(1,int((b-a).length/1.0))
            for k in range(N+1):
                p=a+(b-a)*k/N
                B.box((p.x,p.y,p.z+.46),(.13,.13,.92),'woodLight')
                B.cyl((p.x,p.y,p.z+.94),.11,.09,'plank',6)
            for zz in [.27,.71]:B.beam(a+Vector((0,0,zz)),b+Vector((0,0,zz)),.09,'plank')
    for a0,a1 in [(185,218),(226,250),(285,314),(322,349),(12,32),(47,68),(80,108),(120,158)]:
        points=[]
        for j in range(9):
            a=math.radians(a0+(a1-a0)*j/8);x=11.45*cos(a);y=10.0*sin(a)
            points.append((x,y,2.65 if y>4.4 else 1.16))
        fence(points)
    fence([(-7.7,4.14,2.65),(-3.3,4.14,2.65)])
    fence([(-.5,4.14,2.65),(4.7,4.14,2.65)])
    fence([(-3.05,2.10,1.2),(-3.05,4.15,2.65)])
    fence([(-.75,2.10,1.2),(-.75,4.15,2.65)])
    B.finish(.025)

fences()

def vegetation():
    T=Build('Trees • branching broadleaf grove','08 Trees & gardens')
    P=Build('Trees • layered mountain pines','08 Trees & gardens')
    G=Build('Gardens • shrubs, grasses and flowers','08 Trees & gardens')
    def broadleaf(x,y,z,s=1):
        T.beam((x,y,z),(x+.12*s,y,z+2.0*s),.15*s,'wood',False)
        for k in range(7):
            a=k*2.4;rr=random.uniform(.42,.85)*s;h=random.uniform(1.65,2.8)*s
            pos=(x+rr*cos(a),y+rr*sin(a),z+h)
            T.beam((x+.05,y,z+1.35*s),pos,.055*s,'woodLight',False)
            for j in range(5):
                aa=j*2.4;rad=random.uniform(.15,.40)*s
                T.ico((pos[0]+rad*cos(aa),pos[1]+rad*sin(aa),pos[2]+random.uniform(-.13,.20)*s),(.68*s,.62*s,.46*s),random.choice(['leaf','leaf','leafLight','leafDark']))
        for k in range(4):
            a=k*pi/2
            T.beam((x,y,z+.3*s),(x+.35*s*cos(a),y+.35*s*sin(a),z+.025),.065*s,'wood',False)
    def pine(x,y,z,s):
        P.beam((x,y,z),(x,y,z+3.1*s),.10*s,'wood',False)
        for j in range(6):
            h=(.75+j*.38)*s;r=(.94-j*.12)*s;nn=10
            v=[(x+r*(1+.12*(i%2))*cos(i*2*pi/nn),y+r*(1+.12*(i%2))*sin(i*2*pi/nn),z+h-.12*s*(i%2)) for i in range(nn)]+[(x,y,z+h+1.05*s)]
            P.add(v,[(i,(i+1)%nn,nn) for i in range(nn)]+[tuple(range(nn-1,-1,-1))],'pine' if j%2 else 'leaf')
    # Keep the southern edge open to reveal the bridge and river.
    for i,a in enumerate([10,23,38,52,66,78,92,105,118,131,145,157,170,185,199,212,224,240,339,353]):
        a=math.radians(a);rr=random.uniform(10.2,11.15);x=rr*cos(a);y=.88*rr*sin(a);z=height(x,y)
        if i%4==0:pine(x,y,z,random.uniform(.78,1.1))
        else:broadleaf(x,y,z,random.uniform(.72,1.05))
    for x,y,s in [(-4,8.4,.8),(3.0,8.8,1.1),(9.3,3.8,.8),(-8.5,-3,.8),(-3.7,-5.1,.7),(5.3,-1.2,.7),(-10,1.4,.8)]:
        pine(x,y,height(x,y),s) if y>7 else broadleaf(x,y,height(x,y),s)
    # Garden ring around the fountain.
    for i in range(70):
        a=i*2*pi/70;r=random.uniform(1.72,1.91);x=r*cos(a);y=r*sin(a)
        G.ico((x,y,1.42),(.24,.23,.25),random.choice(['leaf','leafLight','leafDark']))
        if i%2==0:
            G.beam((x,y,1.4),(x,y,1.65),.018,'leaf',False)
            for k in range(5):
                aa=k*2*pi/5
                G.ico((x+.055*cos(aa),y+.055*sin(aa),1.65),(.065,.065,.04),random.choice(['flowerWhite','flowerBlue','flowerYellow']))
    # Rim gardens and small plants in the cliff cracks.
    for i in range(390):
        a=random.uniform(0,2*pi);r=random.uniform(10.55,12.0);x=r*cos(a);y=.88*r*sin(a);z=height(x,y)+.05
        if -10<y<-8.3 and -2<x<3:continue
        if 10.7<x and -1.6<y<.5:continue
        if -9.7<x<-7.4 and y<-7.4:continue
        s=random.uniform(.10,.30)
        if i%3==0:
            for k in range(5):
                aa=k*2.4;G.add([(x,y,z),(x+.15*cos(aa),y+.15*sin(aa),z+.06),(x+.28*cos(aa),y+.28*sin(aa),z+.34)],[(0,1,2)],'grassLight' if k%2 else 'leaf')
        else:
            G.ico((x,y,z+.12),(s*1.5,s*1.4,s),random.choice(['leaf','leafLight','moss']))
            if i%5==0:G.ico((x,y,z+.30),(.075,.075,.06),random.choice(['flowerYellow','flowerWhite','flowerBlue','flowerPink']))
    for x,y in [(-4.1,-1.7),(4.5,-.5),(-4,-4.1),(5.5,3.5),(-8.2,6.6),(3.1,5.6),(7,-7.8),(-5.2,-6.8)]:
        for j in range(14):
            xx=x+random.uniform(-.5,.5);yy=y+random.uniform(-.4,.4);z=height(xx,yy)
            G.ico((xx,yy,z+.2),(.31,.30,.25),random.choice(['leaf','leafLight']))
            G.ico((xx,yy,z+.43),(.08,.08,.07),random.choice(['flowerYellow','flowerWhite','flowerPink']))
    # Moss on exposed stone, slightly inside the cliff rim.
    for i in range(130):
        a=random.random()*2*pi;x=12*cos(a);y=10.55*sin(a);z=random.uniform(-1.6,.6)
        G.ico((x,y,z),(.33,.27,.14),'moss')
    T.finish();P.finish();G.finish()

vegetation()

def details():
    B=Build('Lanterns • village lighting','09 Village props')
    positions=[(-2.7,-2.8),(2.8,-2.8),(-2.8,2.6),(2.9,2.5),(-8.2,-2.4),(-8,-6.5),(-4.2,-8.5),(2.3,-9.0),(4.6,-8.1),(9.6,-3.4),(9.7,1.9),(-5,4.9),(2.1,4.9),(8.7,5),(-9,5.3)]
    positions += [(-1.25,-5.2),(1.25,-5.2),(-1.25,-9.35),(1.25,-9.35)]
    for x,y in positions:
        z=height(x,y)+.1
        B.cyl((x,y,z+.10),.19,.20,'stone',8)
        B.cyl((x,y,z+.78),.055,1.45,'iron',8)
        B.cyl((x,y,z+1.51),.13,.10,'iron',8)
        B.box((x,y,z+1.76),(.22,.22,.39),'glow')
        for xx in [-.13,.13]:
            for yy in [-.13,.13]:B.box((x+xx,y+yy,z+1.76),(.035,.035,.45),'iron')
        B.cyl((x,y,z+2.04),.23,.22,'iron',4,r2=.03)
        B.ico((x,y,z+2.18),(.06,.06,.10),'gold')
    B.finish(.012)
    Q=Build('Props • barrels, crates, benches and signs','09 Village props')
    for x,y in [(-6.3,.9),(-3.5,.8),(3.0,2.4),(5.7,1.4),(-7.7,2.0),(6.3,-.8),(8.3,-.9),(-4.6,-4.5),(-7.8,-4.2),(-4.4,6.3),(1.6,6.2)]:
        z=height(x,y)
        Q.cyl((x,y,z+.35),.27,.64,'woodLight',12,r2=.24)
        ring(Q,(x,y),.265,.285,z+.15,.065,'iron',12);ring(Q,(x,y),.26,.28,z+.57,.065,'iron',12)
        Q.cyl((x,y,z+.69),.24,.04,'plank',12)
        for k in range(12):
            a=k*2*pi/12;Q.beam((x+.273*cos(a),y+.273*sin(a),z+.06),(x+.25*cos(a),y+.25*sin(a),z+.66),.018,'wood')
    for x,y in [(-5.8,-.8),(3.7,.7),(-9,-.3),(5.4,2.3),(-4.3,5.7),(8.9,-6.4)]:
        z=height(x,y)
        Q.box((x,y,z+.28),(.64,.56,.53),'woodLight')
        for zz in [z+.08,z+.45]:Q.box((x,y-.30,zz),(.68,.06,.09),'plank')
        Q.beam((x-.27,y-.34,z+.05),(x+.27,y-.34,z+.51),.06,'wood')
    for x,y,a in [(-3.5,-2.5,-.6),(3.5,-2.5,.6),(2.8,3.2,0)]:
        R=Matrix.Rotation(a,3,'Z');z=1.25
        for k in range(3):Q.box(Vector((x,y,z+.43))+R@Vector((0,(k-1)*.12,0)),(1.15,.10,.08),'plank',R)
        for xx in [-.43,.43]:Q.box(Vector((x,y,z+.21))+R@Vector((xx,0,0)),(.09,.35,.43),'wood',R)
        for k in range(2):Q.box(Vector((x,y,z+.74+k*.14))+R@Vector((0,.22,0)),(1.15,.07,.10),'plank',R)
    # Wooden entrance marker, kept small so the scene stays the focal point.
    for x in [2.2,3.65]:Q.box((x,-9.1,1.95),(.12,.12,1.65),'wood')
    Q.box((2.93,-9.1,2.47),(1.65,.16,.50),'woodLight')
    Q.finish(.018)
    font=bpy.data.curves.new('Village entrance lettering','FONT');font.body='CRYSTALBROOK';font.align_x='CENTER';font.size=.135;font.extrude=.002
    ob=bpy.data.objects.new('Sign • Crystalbrook',font);cols['09 Village props'].objects.link(ob);ob.location=(2.93,-9.195,2.43);ob.rotation_euler=(pi/2,0,0);font.materials.append(M['cream'])
    # Short hanging shop signs.
    S=Build('Shop signs and hanging brackets','09 Village props')
    for x,y,z in [(-7.9,1.8,3.4),(6.7,-.8,3.2),(-.3,5.2,4.9)]:
        S.beam((x,y,z+.4),(x,y-.65,z+.4),.07,'iron')
        S.box((x,y-.58,z),(.55,.10,.42),'woodLight')
        S.ico((x,y-.65,z),(.16,.025,.16),'gold')
    S.finish(.012)

details()
print('River, waterfalls, bridges, fences, trees, gardens and village props completed')
