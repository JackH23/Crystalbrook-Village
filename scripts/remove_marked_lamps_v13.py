"""Remove the eleven lampposts crossed out in the user's village overview."""
import bpy,bmesh,ast,os,json,shutil,math
from mathutils import Vector
OUT=os.environ.get('VILLAGE_PROJECT_DIR',r'D:\codex+blender\village')
source=os.path.dirname(os.path.abspath(__file__));scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
backup=os.path.join(OUT,'versions','Crystalbrook_Village_v12.blend')
if not os.path.isfile(backup):bpy.ops.wm.save_as_mainfile(filepath=backup,copy=True)
for node in ast.parse(open(os.path.join(source,'widen_garden_terrace_v7.py'),encoding='utf-8').read()).body:
    if isinstance(node,ast.FunctionDef) and node.name=='parts':exec(compile(ast.Module(body=[node],type_ignores=[]),'parts_helper','exec'))
targets={
 'Lanterns • paths, bridges and terrace landings':[(2.0,5.0),(3.0,-2.5),(-3.0,-2.5),(-1.463,-4.288),(-5.407,-7.829),(-3.537,-9.912),(1.0,-9.5)],
 'Pool terrace • warm reference lanterns':[(11.104,.089),(10.946,-1.437),(10.25,-2.48)],
 'Expansion • promenade lanterns and overlook benches':[(-1.052,-13.237)]
}
removed={}
for prefix,points in targets.items():
    ob=next(o for o in scene.objects if o.type=='MESH' and o.name.startswith(prefix))
    before=len(ob.data.vertices)
    parts(ob,lambda p:any(math.hypot(p.x-x,p.y-y)<.26 for x,y in points))
    removed[prefix]=before-len(ob.data.vertices)
    # Inspect every remaining vertex to ensure no pole, shade or base remains.
    remnants=[v for v in ob.data.vertices if any(math.hypot((ob.matrix_world@v.co).x-x,(ob.matrix_world@v.co).y-y)<.20 for x,y in points)]
    if remnants:raise RuntimeError('Lamp geometry remains at a marked position: '+prefix)
    print(prefix,'removed vertices:',removed[prefix])
scene['Revision']='V13 • eleven unwanted lampposts removed at the marked plaza, bridge, terrace and lower path positions'
scene['Marked lampposts removed']=11
p=os.path.join(OUT,'project_manifest.json');report=json.load(open(p,encoding='utf-8'))
report.update({'revision':13,'previous_version':'versions/Crystalbrook_Village_v12.blend','removed_lampposts':targets,'marked_lamp_count':11,'removed_lamp_vertices':removed})
with open(p,'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
dest=os.path.join(OUT,'scripts',os.path.basename(__file__))
if os.path.normcase(os.path.abspath(__file__))!=os.path.normcase(os.path.abspath(dest)):shutil.copy2(__file__,dest)
ref=r'C:\Users\User\OneDrive\Pictures\Screenshots 1\Screenshot 2026-10-19 163404.png'
if os.path.isfile(ref):shutil.copy2(ref,os.path.join(OUT,'references','marked_unwanted_lampposts.png'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('Eleven marked lampposts removed; no geometry remains at their positions.')
