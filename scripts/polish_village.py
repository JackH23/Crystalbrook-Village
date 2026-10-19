# Smaller rock columns break up the large island silhouette.
R=Build('Cliffs • weathered vertical columns','01 Island & cliffs')
for i in range(110):
    a=i*2*pi/110;r=12.18+.12*sin(i*2.1);x=r*cos(a);y=.88*r*sin(a)
    w=random.uniform(.25,.48);dep=random.uniform(.38,.66);top=random.uniform(2.35,2.55) if y>4.2 else random.uniform(.55,.92);base=random.uniform(-2.65,-1.75)
    n=7;v=[]
    for k,z in enumerate([base,(base+top)*.5,top]):
        for j in range(n):
            t=j*2*pi/n;rr=random.uniform(.85,1.15)
            v.append((x+rr*w*cos(t),y+rr*dep*sin(t),z+random.uniform(-.13,.13)))
    R.add(v,[tuple(range(n-1,-1,-1)),tuple(range(2*n,3*n))]+[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for k in range(2) for j in range(n)],random.choice(['rockLight','rockLight','rock','stone']))
R.finish(.018)

# Finish the backs and left sides as well as the camera-facing facades.
for name,x,y,z,w,d,h,angle,manor in [
    ('Manor',-1.3,7.05,2.60,4.7,3.35,3.65,0,True),
    ('Merchant',-7.15,3.3,1.15,3.1,2.75,3.05,-.13,False),
    ('Hill cottage',6.3,5.9,2.60,2.65,2.6,2.45,.16,False),
    ('Baker',7.35,.75,1.15,2.9,2.65,2.75,-.25,False),
    ('Garden cottage',-6.15,-4.7,1.15,2.85,2.6,2.6,-.20,False),
    ('Mill',8.2,-6.65,1.15,1.8,1.75,1.6,.12,False)]:
    H=Build('Rear details • '+name,'03 Houses',(x,y,z),angle)
    for xx in [-w*.28,w*.28]:
        H.box((xx,d/2+.06,h/2+.15),(.12,.13,h),'wood')
        for zz in [.3+h*.24,.3+h*.74]:
            ww=min(.56,w*.22);hh=min(.7,h*.26)
            H.box((xx,d/2+.12,zz),(ww+.18,.10,hh+.18),'wood')
            H.box((xx,d/2+.18,zz),(ww,.04,hh),'glow')
            H.box((xx,d/2+.22,zz),(.05,.045,hh),'wood')
            H.box((xx,d/2+.22,zz),(ww,.045,.05),'wood')
            H.box((xx,d/2+.20,zz-hh/2-.09),(ww+.25,.26,.09),'plank')
    for yy in [-d*.24,d*.24]:
        H.box((-w/2-.04,yy,h/2+.15),(.12,.12,h),'wood')
        for zz in [.3+h*.24,.3+h*.74]:
            ww=min(.54,d*.25);hh=min(.68,h*.26)
            H.box((-w/2-.12,yy,zz),(.10,ww+.18,hh+.18),'wood')
            H.box((-w/2-.18,yy,zz),(.04,ww,hh),'glow')
            H.box((-w/2-.22,yy,zz),(.045,.05,hh),'wood')
            H.box((-w/2-.22,yy,zz),(.045,ww,.05),'wood')
    H.finish(.018)

# Extra arch blocks emphasize the open underside from the hero camera.
A=Build('Bridge • arch keystones and masonry joints','07 Bridges & fences')
for side in [-1,1]:
    for i in range(19):
        t=(i+.5)/19;y=-5.20-4.15*t;z=1.30+1.45*sin(pi*t)-.43
        slope=math.atan2(1.45*pi*cos(pi*t),-4.15)
        # Short radial seams make the construction legible at miniature scale.
        A.box((side*1.215,y,z),(.055,.14,.29),'paverDark',Matrix.Rotation(-.28*cos(pi*t),3,'X'))
A.finish(.01)

# Individual leaves add a finer silhouette over the clustered tree canopies.
L=Build('Canopies • individual pointed leaves','08 Trees & gardens')
tree=next(o for o in cols['08 Trees & gardens'].objects if o.name.startswith('Trees • branching'))
leafmats={i for i,m in enumerate(tree.data.materials) if m.name.startswith(('leaf','leafLight','leafDark'))}
for poly in tree.data.polygons:
    if poly.material_index not in leafmats or poly.normal.z<.2 or random.random()>.11:continue
    p=poly.center
    # Polygon centers require a mesh update after generation; calculate explicitly.
    p=sum((tree.data.vertices[i].co for i in poly.vertices),Vector())/len(poly.vertices)
    a=random.random()*2*pi;d=Vector((cos(a),sin(a),random.uniform(.1,.5)))*.24;side=Vector((-sin(a),cos(a),0))*.10
    L.add([p-d,p+side+Vector((0,0,.035)),p+d,p-side],[(0,1,2),(0,2,3)],random.choice(['leaf','leafLight']))
L.finish()

# Moss-covered stones and low flower beds in the village gardens.
G=Build('Garden accents • flowers, ferns and stone borders','08 Trees & gardens')
for x,y,z in [(-4.45,3.2,1.2),(3.65,3.45,1.2),(-8.9,-4.7,1.2),(6,-1.8,1.2),(3.6,6.9,2.65),(-4,8.5,2.65),(-5,-6.8,1.2),(6.3,-7.7,1.2)]:
    for k in range(24):
        a=k*2.4;rr=random.uniform(.1,.65);xx=x+rr*cos(a);yy=y+rr*sin(a)
        G.beam((xx,yy,z),(xx,yy,z+.22),.015,'leaf',False)
        for j in range(5):
            aa=j*2*pi/5
            G.ico((xx+.045*cos(aa),yy+.045*sin(aa),z+.24),(.055,.055,.032),'flowerWhite' if k%3 else 'flowerYellow')
    for k in range(8):
        a=k*2*pi/8;G.ico((x+.77*cos(a),y+.65*sin(a),z+.04),(.18,.15,.12),'stone')
G.finish()

# A lighter stone palette makes the hanging island visible against the studio.
for key,color in [('rock',(.39,.43,.45)),('rockLight',(.53,.55,.53)),('rockDark',(.28,.33,.36))]:
    m=M[key];p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);m.diffuse_color=(*color,1)
scene['Project']='Crystalbrook • Floating Village'
scene['Reference priority']='Upper-left isometric composition; detail panels guide individual assets.'
scene['Build stage']='First complete editable village scene'
scene['Art direction']='Warm timber and terracotta, cool water and crystal, layered green gardens.'
print('Cliff detail, foliage, flower gardens and bridge masonry refined')
