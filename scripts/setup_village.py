import bpy, math, os
from mathutils import Vector

def camera(name,loc,target,scale):
    data=bpy.data.cameras.new(name);data.type='ORTHO';data.ortho_scale=scale
    ob=bpy.data.objects.new(name,data);cols['10 Lighting & cameras'].objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob

def area(name,loc,power,color,size,target=(0,0,1)):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);cols['10 Lighting & cameras'].objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob

hero=camera('Camera • hero isometric',(26,-39,31),(0,0,1.8),32.8)
scene.camera=hero
camera('Camera • top layout',(0,0,45),(0,0,0),29)
camera('Camera • front',(0,-40,17),(0,0,1.7),30)
camera('Camera • back',(0,40,18),(0,0,1.7),30)
camera('Camera • left',(-40,0,19),(0,0,1.7),30)
camera('Camera • right',(40,0,19),(0,0,1.7),30)
camera('Camera • underside',(22,-32,-23),(0,0,-.5),29)
area('Key • warm afternoon',(-10,-14,24),2200,(1,.80,.57),10)
area('Fill • soft sky',(14,-2,18),1500,(.55,.76,1),12)
area('Rim • canopy light',(-4,14,19),2600,(1,.90,.63),9)
world=bpy.data.worlds.new('Midnight blue studio');world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(.075,.115,.16,1);bg.inputs['Strength'].default_value=.45;scene.world=world
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
try:scene.render.engine='CYCLES'
except TypeError:pass
scene.cycles.samples=48;scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    available=[i.identifier for i in prefs.bl_rna.properties['compute_device_type'].enum_items]
    for backend in ['OPTIX','CUDA','HIP','ONEAPI','METAL']:
        if backend in available:
            try:
                prefs.compute_device_type=backend;prefs.get_devices()
                if any(d.type!='CPU' for d in prefs.devices):
                    for d in prefs.devices:d.use=d.type!='CPU'
                    scene.cycles.device='GPU';break
            except Exception:pass
except Exception:pass
scene.render.film_transparent=False
print('Cameras and lighting ready; render device:',scene.cycles.device)
