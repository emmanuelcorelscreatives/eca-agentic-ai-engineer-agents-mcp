"""Run the shared suite and every project's actual tests directory.

Framework integration cases may explicitly skip when optional SDKs are absent.
Their installed-environment run is separate evidence and must report zero relevant
skips before a lesson claims that framework path was exercised.
"""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
folders=[root/'tests']
project_test_dirs={path.parent for path in (root/'projects').rglob('test_*.py') if not any(part in path.parts for part in ('.venv','node_modules','__pycache__','dist'))}
folders.extend(sorted(project_test_dirs))
failed=[]
for folder in folders:
 print(f'Running {folder.relative_to(root)}',flush=True)
 result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(folder),'-v'],cwd=root)
 if result.returncode:failed.append(str(folder.relative_to(root)))
if failed:
 print('Failed test directories: '+', '.join(failed),file=sys.stderr)
 sys.exit(1)
print(f'PASS: {len(folders)} independently discovered test directories')
