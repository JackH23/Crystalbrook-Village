"""Portable entry point to reproduce the refined village."""
import os
from pathlib import Path
root=Path(__file__).resolve().parent
os.environ['VILLAGE_PROJECT_DIR']=str(root.parent)
namespace={'__name__':'__main__'}
for filename in ['refine_village_v2.py','refine_village_v2_assets.py','setup_village.py','refine_village_v2_gardens.py','finalize_village_v2.py']:
    namespace['__file__']=str(root/filename)
    exec(compile((root/filename).read_text(encoding='utf-8'),str(root/filename),'exec'),namespace)
print('Refined village rebuilt and saved.')
