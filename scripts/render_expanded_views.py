import bpy,os,shutil
from mathutils import Vector
scene=bpy.context.scene
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder=os.path.join(root,'renders','v3');os.makedirs(folder,exist_ok=True)
def find_camera(prefix):return next(o for o in scene.objects if o.type=='CAMERA' and o.name.startswith(prefix))
for prefix in ['Camera • front','Camera • back','Camera • left','Camera • right','Camera • underside']:
    cam=find_camera(prefix);cam.data.ortho_scale=35.5
    direction=cam.rotation_euler.to_quaternion()@Vector((0,0,1))
    target=Vector((1,-1.3,0));cam.location=target+direction*48
queue=[('02_top_layout','Camera • top layout'),('05_right_expansion','Camera • right'),('06_underside','Camera • underside'),('04_isometric','Camera • hero isometric'),('03_expanded_village','Camera • marked expansion overview')]
def next_view():
    name,prefix=queue.pop(0);scene.camera=find_camera(prefix)
    final=name=='03_expanded_village';iso=name=='04_isometric'
    scene.render.resolution_x=1700 if final else (1200 if iso else 800)
    scene.render.resolution_y=1450 if final else (1050 if iso else 800)
    scene.render.resolution_percentage=100;scene.cycles.samples=64 if final else (32 if iso else 16)
    scene.render.filepath=os.path.join(folder,name+'.png')
    bpy.app.driver_namespace['village_render_status']='V3 rendering '+name
    bpy.ops.render.render(write_still=True)
    if queue:return .3
    shutil.copy2(scene.render.filepath,os.path.join(root,'renders','03_village_hero.png'))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'Crystalbrook_Village.blend'))
    bpy.app.driver_namespace['village_render_status']='V3 expansion renders complete and project saved'
    return None
bpy.app.timers.register(next_view,first_interval=.3)
print('Expanded map verification and final render scheduled')
