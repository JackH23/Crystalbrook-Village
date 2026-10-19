def leaf(B,p,size,color,angle=0,tilt=0):
    outline_pts=[(0,-1),(.34,-.52),(.65,-.43),(.40,-.05),(.68,.18),(.27,.28),(0,1),(-.27,.28),(-.68,.18),(-.40,-.05),(-.65,-.43),(-.34,-.52)]
    R=Matrix.Rotation(angle,3,'Z')@Matrix.Rotation(tilt,3,'X')
    v=[Vector(p)+R@Vector((0,0,.10*size))]+[Vector(p)+R@Vector((x*size,y*size,.02*size)) for x,y in outline_pts]
    B.add(v,[(0,i+1,(i+1)%12+1) for i in range(12)],color)

def on_route(x,y,extra=0):
    if x*x+y*y<4.8**2:return True
    for pts,w in PATHS:
        if min(segdist(x,y,a,b) for a,b in zip(pts[:-1],pts[1:]))<w/2+extra:return True
    return False
def in_building(x,y,extra=.15):
    for _,xx,yy,z,w,d,h,a,manor in HOUSES:
        q=Matrix.Rotation(-a,3,'Z')@Vector((x-xx,y-yy,0))
        if abs(q.x)<w*.51+extra and abs(q.y)<d*.55+extra:return True
    for xx,yy in [(-4.9,.10),(4.3,1.65),(-5.05,6.1),(-9.1,-.65)]:
        if abs(x-xx)<1.3+extra and abs(y-yy)<1.0+extra:return True
    return False

def refined_trees():
    trunk=Build('Trees • visible branching trunks','08 Trees & gardens')
    leaves=Build('Trees • layered individual lobed leaves','08 Trees & gardens')
    pine=Build('Trees • branch whorls and fine pine foliage','08 Trees & gardens')
    def tree(x,y,s):
        z=landheight(x,y)+.025
        trunk.cyl((x,y,z+.93*s),.125*s,1.86*s,'wood',9,r2=.06*s)
        for k in range(7):
            a=k*2.4+random.uniform(-.3,.3);rr=random.uniform(.48,.82)*s;zz=random.uniform(1.8,2.6)*s
            p=Vector((x+rr*cos(a),y+rr*sin(a),z+zz))
            trunk.beam((x,y,z+1.15*s),p,.045*s,'woodLight',False)
            for j in range(3):
                aa=a+j*2.1;q=p+Vector((.28*s*cos(aa),.28*s*sin(aa),.17*s))
                trunk.beam(p,q,.018*s,'wood',False)
            # Small inner tufts support a fine, leafy canopy silhouette.
            leaves.ico(p,(.44*s,.43*s,.27*s),'leafDark')
            for j in range(58):
                aa=j*2.39996;r=random.uniform(.14,.53)*s
                p2=p+Vector((r*cos(aa),r*sin(aa),random.uniform(-.17,.28)*s))
                leaf(leaves,p2,random.uniform(.13,.24)*s,random.choices(['leaf','leafLight','leafGold','leafDark'],[6,3,.3,2])[0],random.random()*2*pi,random.uniform(-.7,.7))
        for k in range(5):
            a=k*2*pi/5;trunk.beam((x,y,z+.22*s),(x+.30*s*cos(a),y+.30*s*sin(a),z),.04*s,'wood',False)
    def conifer(x,y,s):
        z=landheight(x,y)+.025
        trunk.cyl((x,y,z+1.55*s),.09*s,3.1*s,'wood',8,r2=.025*s)
        for level in range(7):
            h=(.70+level*.37)*s;r=(.83-level*.095)*s
            for j in range(8):
                a=j*2*pi/8+level*.36
                q=Vector((x+r*cos(a),y+r*sin(a),z+h-.18*s))
                trunk.beam((x,y,z+h+.15*s),q,.023*s,'wood',False)
                for k in range(4):
                    aa=a+(k-1.5)*.22;dist=r*(.42+k*.16);p=Vector((x+dist*cos(aa),y+dist*sin(aa),z+h+.11*s-k*.06*s))
                    leaf(pine,p,.28*s,random.choice(['pine','leaf','leafDark']),a+pi/2,-.20)
        for j in range(3):leaf(pine,(x,y,z+3.2*s),.25*s,'leafLight',j*2*pi/3,1.1)
    for x,y,s in [(-10.6,1.6,.95),(-10.1,5.2,1.03),(-7.9,8.0,1.0),(-5.0,9.3,.95),(-1.3,9.65,.8),(2.1,9.1,1.08),(4.5,8.8,.9),(8.5,7.5,1.0),(10.0,4.4,.95),(10.7,2.5,.65),(10.6,-5.4,.65),(-10.4,-2.8,.9),(-9.3,-5.9,.72),(-8.1,-6.4,.75),(4.7,5.5,.70),(-4.6,3.3,.65)]:
        tree(x,y,s)
    for x,y,s in [(-10.6,-.4,.8),(-9.2,6.7,1.05),(-4,9.2,1.10),(3.1,8.75,1.0),(10.1,6.0,1.15),(10.8,-4.1,.7),(-8.7,-4.3,.6)]:conifer(x,y,s)
    trunk.finish();leaves.finish();pine.finish()

def refined_gardens():
    G=Build('Gardens • leafy shrubs, ferns and wildflowers','08 Trees & gardens')
    def flower(x,y,z,color,s=1):
        G.beam((x,y,z),(x,y,z+.20*s),.009*s,'leaf',False)
        for k in range(5):
            a=k*2*pi/5;G.ico((x+.04*s*cos(a),y+.04*s*sin(a),z+.22*s),(.05*s,.05*s,.028*s),color)
        G.ico((x,y,z+.235*s),(.025*s,.025*s,.023*s),'flowerYellow')
    def bush(x,y,z,s):
        for k in range(12):
            a=k*2.4;r=random.random()*.29*s
            p=(x+r*cos(a),y+r*sin(a),z+random.uniform(.10,.33)*s)
            leaf(G,p,random.uniform(.14,.24)*s,random.choice(['leaf','leafLight','leafDark']),random.random()*2*pi,random.uniform(-.6,.6))
    # Plant the perimeter in varied patches, leaving the river outlets exposed.
    for i in range(780):
        a=random.random()*2*pi;r=outline(a)-random.uniform(.20,1.60);x=r*cos(a);y=.88*r*sin(a);z=landheight(x,y)
        if z<.50 or on_route(x,y,.08) or in_building(x,y):continue
        bush(x,y,z,random.uniform(.6,1.2))
        if i%4==0:flower(x,y,z,random.choice(['flowerYellow','flowerWhite','flowerBlue','flowerPink']),random.uniform(.6,1.0))
    # Riverbank ferns and reeds follow the carved channel instead of covering it.
    for i,p in enumerate(RIVER):
        if i%2:continue
        d=RIVER[min(i+1,len(RIVER)-1)]-RIVER[max(0,i-1)];side=Vector((-d.y,d.x,0)).normalized()
        for s in [-1,1]:
            q=p+side*s*random.uniform(1.2,1.55);z=landheight(q.x,q.y)
            if on_route(q.x,q.y,.03) or in_building(q.x,q.y):continue
            bush(q.x,q.y,z,.9)
            for k in range(6):
                aa=k*2.4;end=Vector((q.x+.30*cos(aa),q.y+.30*sin(aa),z+.34))
                G.beam((q.x,q.y,z),end,.008,'leaf',False)
                for j in range(3):
                    t=.3+j*.20;pp=Vector((q.x,q.y,z)).lerp(end,t)
                    leaf(G,pp,.10,'leafLight',aa+pi/2,.3)
            if i%4==0:flower(q.x,q.y,z,'flowerYellow')
    # Low planted beds beside the plaza and cottage gardens.
    beds=[(-4.0,-3.8),(4.1,-2.1),(-4.5,2.8),(3.8,3.4),(-8.4,6.2),(3.3,6.8),(6.3,-7.5),(-5.2,-6.0)]
    for x,y in beds:
        z=landheight(x,y)
        for j in range(38):
            a=j*2.4;r=random.random()*.63;xx=x+r*cos(a);yy=y+r*sin(a)
            if on_route(xx,yy,.02) or in_building(xx,yy,.05):continue
            bush(xx,yy,z,.55)
            if j%2:flower(xx,yy,z,random.choice(['flowerWhite','flowerYellow','flowerBlue','flowerPink']),.9)
        for j in range(12):
            a=j*2*pi/12
            xx=x+.76*cos(a);yy=y+.65*sin(a)
            if not on_route(xx,yy):G.ico((xx,yy,z+.03),(.15,.14,.10),'stone')
    # Small trailing leaves and moss interrupt the stone rim and hanging formations.
    for i in range(230):
        a=random.random()*2*pi;r=outline(a);x=r*cos(a);y=.88*r*sin(a);z=random.uniform(-1.6,landheight(x*.97,y*.97)-.15)
        G.ico((x,y,z),(.18,.17,.08),'moss')
        if i%3==0:
            for j in range(4):leaf(G,(x+.035*sin(j),y-.025*cos(j),z-j*.11),.10,'leaf',j*1.7,.2)
    # Preserve the existing circular fountain bed and add fine colored flowers.
    for j in range(80):
        a=j*2*pi/80;r=random.uniform(1.73,1.93);x=r*cos(a);y=r*sin(a)
        leaf(G,(x,y,1.44),.13,'leafLight',a,.5)
        if j%2:flower(x,y,1.38,'flowerWhite' if j%3 else 'flowerBlue',.7)
    G.finish()

def props_and_lighting():
    B=Build('Market props • baskets, pottery, sacks and stacked crates','09 Village props')
    def basket(x,y,z,r=.22,h=.30):
        B.cyl((x,y,z+h/2),r*.8,h,'woodLight',12,r2=r)
        for j in range(6):ring(B,(x,y),r*(.80+.20*j/5),r*(.80+.20*j/5)+.018,z+h*j/5,.025,'sack',16)
        for j in range(12):
            a=j*2*pi/12;B.beam((x+r*.81*cos(a),y+r*.81*sin(a),z),(x+r*cos(a),y+r*sin(a),z+h),.017,'plank',False)
        for j in range(9):
            a=j*2.4;rr=random.uniform(0,r*.7);B.ico((x+rr*cos(a),y+rr*sin(a),z+h),(.075,.075,.065),random.choice(['apple','orange','leafLight']))
    def pot(x,y,z,r=.18,h=.4):
        profile=[(.65,0),(.94,.12),(1,.45),(.9,.68),(.47,.8),(.48,1),(.34,1),(.33,.82)]
        n=16;v=[(x+r*rr*cos(i*2*pi/n),y+r*rr*sin(i*2*pi/n),z+hh*h) for rr,hh in profile for i in range(n)]
        B.add(v,[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(profile)-1) for i in range(n)],'clay')
        B.cyl((x,y,z+h*.79),r*.32,.015,'wood',16)
    def crate(x,y,z,s=.55):
        for side in [-1,1]:
            for j in range(4):
                B.box((x+side*s/2,y,z+(j+.5)*s/4),(.065,s,.10),'plank')
                B.box((x,y+side*s/2,z+(j+.5)*s/4),(s,.065,.10),'woodLight')
        for xx in [-s/2,s/2]:
            for yy in [-s/2,s/2]:B.box((x+xx,y+yy,z+s/2),(.07,.07,s),'wood')
        B.beam((x-s/2,y-s/2-.04,z+.04),(x+s/2,y-s/2-.04,z+s-.04),.045,'plank')
    for x,y,z in [(-6,.05,1.14),(-5.8,-.7,1.14),(-3.7,.6,1.14),(3.2,1.4,1.14),(5.15,.8,1.14),(-9.9,-1.5,1.14),(-4.1,5.8,2.62),(-6.0,5.5,2.62)]:
        basket(x,y,z);basket(x+.38,y+.1,z,.17,.25);pot(x-.25,y+.32,z)
        crate(x+.15,y+.6,z,.48)
        if random.random()<.5:crate(x+.18,y+.6,z+.48,.42)
    for x,y in [(-7.9,1.9),(7.6,.9),(8.9,-7.3),(-5,-5.8),(-2.9,5.7)]:
        z=landheight(x,y);pot(x,y,z,.22,.43);pot(x+.35,y+.1,z,.15,.33)
        B.ico((x-.25,y,z+.22),(.26,.23,.30),'sack')
        ring(B,(x-.25,y),.035,.07,z+.48,.045,'wood',12)
    # Benches alongside the plaza, facing its central feature.
    for x,y,a in [(-3.5,-2.5,-.6),(3.3,-2.6,.6),(2.5,3.4,0)]:
        R=Matrix.Rotation(a,3,'Z');z=1.27
        for j in range(3):B.box(Vector((x,y,z+.42))+R@Vector((0,(j-1)*.12,0)),(1.1,.105,.075),'plank',R)
        for xx in [-.41,.41]:B.box(Vector((x,y,z+.21))+R@Vector((xx,0,0)),(.08,.32,.42),'iron',R)
        for j in range(2):B.box(Vector((x,y,z+.7+j*.13))+R@Vector((0,.24,0)),(1.1,.065,.09),'plank',R)
    # Handcart with visible spoked wheels.
    x,y,z=2.8,5.05,2.67
    B.box((x,y,z+.42),(1.1,.64,.12),'plank')
    for yy in [-.33,.33]:
        for k in range(3):B.box((x,y+yy,z+.54+k*.12),(1.1,.07,.08),'woodLight')
        B.beam((x-.6,y+yy,z+.25),(x-1.4,y+yy,z+.5),.06,'wood')
    for yy in [-.44,.44]:
        n=20;r=.30;v=[(x+r*cos(i*2*pi/n),y+yy+dy,z+.30+r*sin(i*2*pi/n)) for dy in [-.04,.04] for i in range(n)]
        B.add(v,[tuple(range(n)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'wood')
        for k in range(8):
            a=k*2*pi/8;B.beam((x,y+yy-.05,z+.30),(x+.26*cos(a),y+yy-.05,z+.30+.26*sin(a)),.025,'plank')
    B.finish(.012)
    # Lanterns use a separate glowing material from the quieter window panes.
    M['lamp']=mat('Lantern • warm amber',(1,.50,.09),.22,0,2.3)
    L=Build('Lanterns • paths, bridges and terrace landings','09 Village props')
    locations=[(-3,-2.5,1.25),(3,-2.5,1.25),(-3,2.1,1.25),(3.3,3.1,1.25),(-8.6,-2.4,1.2),(-8.4,-6.3,1.2),(1,-9.5,1.08),(5.4,-8.7,1.15),(10.6,-5.4,1.2),(11.45,-1.4,1.25),(11.55,.65,1.9),(-5.2,5,2.7),(2,5,2.7),(5.8,4.4,2.7)]
    for s in [-2.65,2.65]:
        for w in [-1.40,1.40]:
            p=bp(s,w,1.15);locations.append(tuple(p))
    for x,y,z in locations:
        L.cyl((x,y,z+.08),.14,.16,'stone',8);L.cyl((x,y,z+.70),.043,1.25,'iron',8)
        L.box((x,y,z+1.43),(.18,.18,.30),'lamp')
        for xx in [-.1,.1]:
            for yy in [-.1,.1]:L.box((x+xx,y+yy,z+1.43),(.025,.025,.34),'iron')
        L.cyl((x,y,z+1.66),.17,.17,'iron',4,r2=.015);L.ico((x,y,z+1.76),(.045,.045,.06),'gold')
    L.finish(.008)
    # Small shop signs, including bracket and hanging chains.
    S=Build('Signs • entrance and shop brackets','09 Village props')
    for x,y,z,label in [(-6.4,1.83,2.9,'TRADING POST'),(7.2,1.15,3.0,'BAKERY'),(8.4,-7.5,2.4,'RIVER MILL')]:
        S.beam((x,y,z+.4),(x,y-.5,z+.4),.045,'iron')
        for xx in [-.23,.23]:S.beam((x+xx,y-.48,z+.38),(x+xx,y-.48,z+.18),.012,'iron',False)
        S.box((x,y-.48,z),(.70,.09,.35),'woodLight')
        font=bpy.data.curves.new(label,'FONT');font.body=label;font.align_x='CENTER';font.size=.075;font.extrude=.001
        o=bpy.data.objects.new('Shop sign • '+label,font);cols['09 Village props'].objects.link(o);o.location=(x,y-.536,z-.025);o.rotation_euler=(pi/2,0,0);font.materials.append(M['cream'])
    for x in [-2.0,-.45]:S.box((x,-9.5,1.8),(.12,.12,1.45),'wood')
    S.box((-1.22,-9.5,2.18),(1.8,.15,.40),'woodLight');S.finish(.012)
    f=bpy.data.curves.new('Crystalbrook entrance','FONT');f.body='CRYSTALBROOK';f.align_x='CENTER';f.size=.125;f.extrude=.0015
    o=bpy.data.objects.new('Village entrance sign',f);cols['09 Village props'].objects.link(o);o.location=(-1.22,-9.59,2.13);o.rotation_euler=(pi/2,0,0);f.materials.append(M['cream'])

refined_trees();refined_gardens();props_and_lighting()

# Match the warmer, brighter miniature presentation of the reference.
for o in cols['10 Lighting & cameras'].objects:
    if o.type=='LIGHT':
        if o.name.startswith('Key'):o.data.energy=2900;o.data.size=8;o.data.color=(1,.84,.64)
        elif o.name.startswith('Fill'):o.data.energy=1700;o.data.color=(.64,.80,1)
        elif o.name.startswith('Rim'):o.data.energy=2600
area('Cliff fill • low soft sky',(4,-17,4),500,(.66,.80,1),9,target=(0,0,-1))
hero.location=(25,-38,33);hero.rotation_euler=(Vector((0,0,1.1))-hero.location).to_track_quat('-Z','Y').to_euler();hero.data.ortho_scale=31
scene.camera=hero
scene.view_settings.exposure=0
scene['Project']='Crystalbrook Village • reference refinement V2'
scene['Revision']='V2: carved water, terraces, smaller houses, diagonal bridge, fine foliage and props'
scene['Reference priority']='Upper-left isometric composition with detail-panel architectural guidance'
print('V2: individual leaf canopies, planted banks, richer market, varied windows and warm lighting completed')
