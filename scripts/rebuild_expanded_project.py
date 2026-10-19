"""Rebuild V2 and apply the approved reference expansion."""
import os
from pathlib import Path
root=Path(__file__).resolve().parent
os.environ['VILLAGE_PROJECT_DIR']=str(root.parent)
ns={'__name__':'__main__'}
for filename in ['refine_village_v2.py','refine_village_v2_assets.py','setup_village.py','refine_village_v2_gardens.py','finalize_village_v2.py','add_marked_area_v3.py']:
    ns['__file__']=str(root/filename)
    exec(compile((root/filename).read_text(encoding='utf-8'),str(root/filename),'exec'),ns)
print('Expanded village rebuilt and saved.')
