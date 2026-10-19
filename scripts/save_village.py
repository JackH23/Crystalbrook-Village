import sys
scene.camera=hero
scene.render.resolution_x=1600;scene.render.resolution_y=1600;scene.render.resolution_percentage=100
scene.cycles.samples=96;scene.cycles.use_denoising=True
scene.render.filepath=os.path.join(OUT,'renders','03_village_hero.png')
scene.render.image_settings.file_format='PNG'
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1.0
scene.render.fps=24
# Open the saved project on the isometric composition in material preview.
for screen in bpy.data.screens:
    for area_ui in screen.areas:
        if area_ui.type=='VIEW_3D':
            sp=area_ui.spaces.active;sp.region_3d.view_perspective='CAMERA'
            sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            sp.clip_end=300
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'Crystalbrook_Village.blend'))
report={
    'project':'Crystalbrook Village',
    'blend_file':'Crystalbrook_Village.blend',
    'blender_version':bpy.app.version_string,
    'objects':len(scene.objects),
    'mesh_vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),
    'mesh_faces':sum(len(o.data.polygons) for o in scene.objects if o.type=='MESH'),
    'houses':6,'market_stalls':4,'cameras':7,
    'render_engine':scene.render.engine,
    'render_resolution':[1600,1600],
    'features':['Irregular floating island and modeled underside','Rear terrace, central plaza and stairs','Six timber houses with individual roof tiles','Four striped market stalls with produce','Faceted crystal fountain','Winding river and four waterfalls','Arched stone bridge and timber footbridge','Perimeter fencing, lanterns, gardens and village props'],
    'asset_sources':'Procedurally modeled in Blender; no third-party assets or external textures required.'
}
with open(os.path.join(OUT,'project_manifest.json'),'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
readme='''CRYSTALBROOK VILLAGE - BLENDER PROJECT

Open Crystalbrook_Village.blend. The active scene is Crystalbrook Village.
This is the first complete stylized village version based on the supplied reference.

PROJECT CONTENTS
Crystalbrook_Village.blend   Editable geometry, materials, lights and seven cameras.
renders/                    Gray checkpoint, colored preview and final camera renders.
references/                 Original village reference image.
scripts/                    Procedural modeling sources and rebuild_project.py.
project_manifest.json       Scene contents and technical details.

SCENE ORGANIZATION
Ten numbered collections group terrain, paths, houses, market, fountain, water,
bridges, vegetation, props, lighting and cameras. Geometry is grouped into meshes
by asset or category; use Edit Mode to adjust individual pieces. Roof tiles,
timber framing, foliage, paving and cliff details are modeled geometry.

CAMERAS
Hero isometric, top layout, front, back, left, right and underside.
The saved project opens on the hero camera. Use the Outliner to select another
camera and set it as the active camera when desired.

RENDERING
Cycles, denoising, 1600 x 1600, 96 samples. Press F12 to render the active camera.
Water is a static stylized surface; there is no animation or fluid simulation.
All materials are self-contained. No external texture downloads are needed.

REBUILD
In Blender's Scripting workspace, open scripts/rebuild_project.py and Run Script.
The script creates a new scene and saves the project in this project folder.
It does not need an internet connection or paid asset-generation services.

REFERENCE PRIORITY
The upper-left isometric panel controls the composition; detail panels guide
the architectural, water, vegetation and underside design.
'''
with open(os.path.join(OUT,'PROJECT_README.txt'),'w',encoding='utf-8') as f:f.write(readme)
txt=bpy.data.texts.get('PROJECT • Read me') or bpy.data.texts.new('PROJECT • Read me');txt.clear();txt.write(readme)
print('Saved',os.path.join(OUT,'Crystalbrook_Village.blend'));print(report)
