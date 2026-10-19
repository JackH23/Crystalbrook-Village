"""Fresh rebuild of the village including all approved reference corrections."""
import os
from pathlib import Path
source=Path(__file__).resolve().parent
os.environ['VILLAGE_PROJECT_DIR']=str(source.parent)
build_namespace={'__name__':'__main__'}
pipeline=['refine_village_v2.py','refine_village_v2_assets.py','setup_village.py','refine_village_v2_gardens.py','finalize_village_v2.py','add_marked_area_v3.py','fix_pool_terrace_v4.py','fix_reference_stairs_v5.py','fix_garden_entrance_v6.py','finish_garden_entrance_v6.py','widen_garden_terrace_v7.py']
for filename in pipeline:
    build_namespace['__file__']=str(source/filename)
    exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='fix_stairside_flowerbed_v8.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='fix_stair_landing_v9.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='fix_inner_stair_rail_v10.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='fix_mill_courtyard_v11.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='fix_mill_sign_and_bench_v12.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='remove_marked_lamps_v13.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='align_riverside_fence_v14.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
filename='simplify_roadside_seating_v15.py'
build_namespace['__file__']=str(source/filename)
exec(compile((source/filename).read_text(encoding='utf-8'),str(source/filename),'exec'),build_namespace)
print('Current V15 village rebuilt and saved.')
