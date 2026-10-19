"""Clear legacy scenery from the newly paved garden and polish its foliage."""
import bpy,bmesh,math,ast,os,random
from mathutils import Vector,Matrix
from math import sin,cos,pi
scene=bpy.context.scene
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
def parts(ob,action):
    bm=bmesh.new();bm.from_mesh(ob.data);seen=set();delete=[]
    for v in bm.verts:
        if v in seen:continue
        stack=[v];seen.add(v);group=[]
        while stack:
            q=stack.pop();group.append(q)
            for e in q.link_edges:
                r=e.other_vert(q)
                if r not in seen:seen.add(r);stack.append(r)
        p=sum((ob.matrix_world@q.co for q in group),Vector())/len(group)
        decision=action(p)
        if decision is True:delete.extend(group)
        elif isinstance(decision,Vector):
            for q in group:q.co+=decision
    if delete:bmesh.ops.delete(bm,geom=delete,context='VERTS')
    bm.to_mesh(ob.data);bm.free();ob.data.update()
def inside(p,margin=1):return ((p.x-11.65)/1.55)**2+((p.y-3.10)/1.38)**2<margin**2
for ob in list(scene.objects):
    if ob.type!='MESH':continue
    name=ob.name
    if name.startswith(('Gardens • leafy shrubs','Pool terrace • flowers')):
        parts(ob,lambda p:inside(p,1.02) and p.z>1.87)
    if name.startswith(('Railings • garden boundaries','Lanterns • paths')):
        parts(ob,lambda p:10.2<p.x<13.2 and 2.1<p.y<4.6 and p.z>1.86)
    if name.startswith('Lanterns • paths'):
        parts(ob,lambda p:10.0<p.x<13.4 and 1.2<p.y<4.8)
    if name.startswith(('Cliffs • fractured','Pool terrace • planted cliff','Reference stairs • rock buttress')):
        parts(ob,lambda p:(inside(p,1.03) and p.z>1.87) or (12.7<p.x<13.6 and 2.3<p.y<3.8 and p.z>1.65))
    if name.startswith('Terrain • carved'):
        parts(ob,lambda p:Vector((0,0,1.81-p.z)) if inside(p,1.06) and p.z>1.90 else False)
    if name.startswith(('Trees • visible branching','Trees • layered individual')):
        parts(ob,lambda p:Vector((-.30,1.44,.15)) if (p.x-10.7)**2+(p.y-2.5)**2<1.04**2 and p.y<3.52 and p.z>1.80 else False)
    # Small remnants from lanterns crossing the entrance are removed with their bases.
    if name.startswith('Pool terrace • warm reference'):
        parts(ob,lambda p:10.0<p.x<13.4 and 1.2<p.y<4.8)
    if name.startswith('Garden entrance • supported irregular stone ledge'):
        parts(ob,lambda p:p.x>12.65 and p.y<3.95 and p.z>1.25)
# Replace the new tree's coarse leaf tufts with the village's lobed leaf geometry.
ob=next(o for o in scene.objects if o.name.startswith('Garden entrance • branching rear garden tree'))
parts(ob,lambda p:p.z>3.3)
M={m.name.split('.00')[0]:m for o in scene.objects if o.type=='MESH' for m in o.data.materials if m}
cols={'leaves':next(c for c in bpy.data.collections if c.name=='Garden entrance • planting and trees')}
source=os.path.dirname(os.path.abspath(__file__))
for node in ast.parse(open(os.path.join(source,'build_village.py'),encoding='utf-8').read()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cubev','cubef'] for t in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
    if isinstance(node,ast.ClassDef) and node.name=='Build':exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
for node in ast.parse(open(os.path.join(source,'refine_village_v2_gardens.py'),encoding='utf-8').read()).body:
    if isinstance(node,ast.FunctionDef) and node.name=='leaf':exec(compile(ast.Module(body=[node],type_ignores=[]),'helpers','exec'))
G=Build('Garden entrance • fine lobed tree canopy','leaves');random.seed(644)
for j in range(7):
    a=j*2.4;tip=Vector((11.98+.52*cos(a),4.47+.44*sin(a),3.532+.28*(j%3)))
    for k in range(65):
        aa=k*2.4;r=random.uniform(.06,.42);q=tip+Vector((r*cos(aa),r*sin(aa),random.uniform(-.13,.23)))
        leaf(G,q,random.uniform(.12,.19),random.choice(['leaf','leafLight','leafLight','leafDark']),random.random()*2*pi,random.uniform(-.5,.5))
G.finish()
lamp=next(o for o in scene.objects if o.name.startswith('Garden entrance • amber lantern'))
old=next(m for m in lamp.data.materials if m.name.startswith('Lantern • warm amber'))
warm=old.copy();warm.name='Garden lantern • golden glow'
bsdf=next(n for n in warm.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value=(1,.55,.10,1);bsdf.inputs['Emission Color'].default_value=(1,.37,.035,1);bsdf.inputs['Emission Strength'].default_value=5
for i,m in enumerate(lamp.data.materials):
    if m==old:lamp.data.materials[i]=warm
data=bpy.data.lights.new('Garden entrance • gentle amber pool of light','POINT');data.energy=9;data.color=(1,.48,.12);data.shadow_soft_size=.3
light=bpy.data.objects.new(data.name,data);cols['leaves'].objects.link(light);light.location=(11.3,4.04,3.35)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('Legacy garden obstructions cleared and rear canopy refined')
