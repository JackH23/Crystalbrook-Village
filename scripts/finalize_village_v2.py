import bmesh

# Correct the mesh normals on the closed kit pieces and keep water sheets facing up.
for ob in scene.objects:
    if ob.type!='MESH':continue
    if ob.name.startswith(('Trees • layered individual','Trees • branch whorls','Gardens • leafy')):continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if ob.name.startswith('River • recessed'):
        for face in bm.faces:
            if face.normal.z<0:face.normal_flip()
    bm.to_mesh(ob.data);bm.free();ob.data.update()

# Ripples provide reflective breakup while the river remains a static modeled asset.
water=M['water'];nodes=water.node_tree.nodes;links=water.node_tree.links
p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
p.inputs['Roughness'].default_value=.17;p.inputs['Metallic'].default_value=.18
p.inputs['Transmission Weight'].default_value=.10
coord=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise');bump=nodes.new('ShaderNodeBump')
noise.inputs['Scale'].default_value=4.0;noise.inputs['Detail'].default_value=2.0
bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.035
links.new(coord.outputs['Object'],noise.inputs['Vector']);links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])

scene.camera=hero;scene.render.resolution_x=1600;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.cycles.samples=80;scene.cycles.use_denoising=True
scene.render.filepath=os.path.join(OUT,'renders','v2','03_village_hero.png')
scene.render.image_settings.file_format='PNG'
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            sp=a.spaces.active;sp.region_3d.view_perspective='CAMERA';sp.shading.type='MATERIAL';sp.overlay.show_overlays=False;sp.clip_end=300

report={
 'project':'Crystalbrook Village','revision':2,'active_scene':scene.name,
 'file':'Crystalbrook_Village.blend','previous_version':'versions/Crystalbrook_Village_v1.blend',
 'objects':len(scene.objects),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),
 'faces':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),
 'houses':6,'market_stalls':4,'saved_cameras':7,'engine':scene.render.engine,'hero_resolution':[1600,1400],
 'changes_from_v1':[
  'Three terrain levels with modeled retaining walls and recessed river channel',
  'Houses reduced by 20 percent in manor height and 17 percent in cottage height',
  'Right-side upper pool cascading into a lower river pool',
  'Broader diagonal stone bridge with shallower deck and visible open arch',
  'Broken cliff shelves, varied stone sizes and moss in crevices',
  'Individual lobed leaves, visible tree branches and varied canopy heights',
  'Paved routes and stairs linking doorways, stalls, bridge landings and terraces',
  'Porches, shutters, dormers, gutter beams, chimney joints and mill annex',
  'Fountain rim detail, water jets, transmissive crystal facets and local cyan light',
  'Woven baskets, pottery, sacks, crates, handcart, benches and shop signs',
  'Warmer sunlight, brighter terracotta, quieter varied windows and reflective water ripples'],
 'external_texture_dependencies':[]
}
with open(os.path.join(OUT,'project_manifest.json'),'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
readme='''CRYSTALBROOK VILLAGE - REFINED VERSION 2

Open Crystalbrook_Village.blend. The active scene is Crystalbrook Village - Refined.
The original version is preserved in versions/Crystalbrook_Village_v1.blend.

This pass follows the comparison plan: terrain and river geometry, house proportions,
bridge composition, cliff variety, fine foliage, connected routes, architectural
detail, fountain effects, market props, and warmer lighting.

CONTENTS
Crystalbrook_Village.blend   Editable refined scene with materials and seven cameras.
renders/v2/                 Structure checkpoint, colored preview and final views.
versions/                   Original Blender file and original hero render.
references/                 Supplied reference image.
scripts/                    Original asset kit and full V2 rebuild sources.
project_manifest.json       Geometry counts and the implemented change list.

REBUILD
Open scripts/rebuild_project.py in Blender's Scripting workspace and Run Script.
This creates a new scene and saves the result in this project folder.
For saved camera renders, run scripts/render_refined_views.py after rebuilding.

RENDER
Cycles, 1600 x 1400, 80 samples and denoising. Press F12 for the main camera.
Water, foliage and fountain jets are static modeled geometry.
Materials are self-contained; no external textures or downloaded assets are needed.

EDITING
Ten numbered collections group the scene by purpose. Each house has a main mesh
and separate architectural detail meshes. Vegetation, stonework and props are
grouped by category. Use Edit Mode to select and adjust individual pieces.
The river is below the surrounding land, with shaped banks and a modeled bed.
'''
with open(os.path.join(OUT,'PROJECT_README.txt'),'w',encoding='utf-8') as f:f.write(readme)
txt=bpy.data.texts.get('PROJECT • Refined V2 read me') or bpy.data.texts.new('PROJECT • Refined V2 read me');txt.clear();txt.write(readme)
with open(os.path.join(OUT,'V2_CHANGELOG.txt'),'w',encoding='utf-8') as f:
    f.write('IMPLEMENTED REFERENCE REFINEMENTS\n\n'+'\n'.join(str(i+1)+'. '+x for i,x in enumerate(report['changes_from_v1'])))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
print('V2 saved:',os.path.join(OUT,'Crystalbrook_Village.blend'));print(report)
