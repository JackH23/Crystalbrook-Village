import bpy,os,shutil
scene=bpy.context.scene
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder=os.path.join(root,'renders','v2');os.makedirs(folder,exist_ok=True)
cameras={o.name.split('.00')[0]:o for o in scene.objects if o.type=='CAMERA'}
queue=[('04_top_layout','Camera • top layout'),('05_front','Camera • front'),('06_back','Camera • back'),('07_left','Camera • left'),('08_right','Camera • right'),('09_underside','Camera • underside'),('03_village_hero','Camera • hero isometric')]
def next_view():
    name,camera_name=queue.pop(0);scene.camera=cameras[camera_name];hero=name=='03_village_hero'
    scene.render.resolution_x=1600 if hero else 700;scene.render.resolution_y=1400 if hero else 700
    scene.render.resolution_percentage=100;scene.cycles.samples=80 if hero else 16
    scene.render.filepath=os.path.join(folder,name+'.png')
    bpy.app.driver_namespace['village_render_status']='V2 rendering '+name
    bpy.ops.render.render(write_still=True)
    if queue:return .3
    scene.camera=cameras['Camera • hero isometric']
    scene.render.resolution_x=1600;scene.render.resolution_y=1400;scene.cycles.samples=80
    shutil.copy2(os.path.join(folder,'03_village_hero.png'),os.path.join(root,'renders','03_village_hero.png'))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'Crystalbrook_Village.blend'))
    bpy.app.driver_namespace['village_render_status']='V2 all camera renders complete and project saved'
    return None
bpy.app.timers.register(next_view,first_interval=.3)
print('V2 alternate views and final hero render scheduled')
