"""Render the finished scene and return to the hero camera. Run after rebuild."""
import bpy, os
scene=bpy.context.scene
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cameras={o.name:o for o in scene.objects if o.type=='CAMERA'}
queue=[('04_top_layout','Camera • top layout'),('05_front','Camera • front'),('06_back','Camera • back'),('07_left','Camera • left'),('08_right','Camera • right'),('09_underside','Camera • underside'),('03_village_hero','Camera • hero isometric')]
def render_next_village_view():
    name,camname=queue.pop(0);scene.camera=cameras[camname];final=name=='03_village_hero'
    scene.render.resolution_x=1600 if final else 650
    scene.render.resolution_y=scene.render.resolution_x;scene.render.resolution_percentage=100
    scene.cycles.samples=96 if final else 16
    scene.render.filepath=os.path.join(root,'renders',name+'.png')
    bpy.app.driver_namespace['village_render_status']='Rendering '+name
    bpy.ops.render.render(write_still=True)
    if queue:return .3
    scene.camera=cameras['Camera • hero isometric']
    scene.render.resolution_x=1600;scene.render.resolution_y=1600;scene.cycles.samples=96
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'Crystalbrook_Village.blend'))
    bpy.app.driver_namespace['village_render_status']='All renders complete and project saved'
    return None
bpy.app.timers.register(render_next_village_view,first_interval=.3)
print('Final view renders scheduled')
