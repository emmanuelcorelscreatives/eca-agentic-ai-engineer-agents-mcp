"""Run the shared suite and every project's actual tests directory.

Framework integration cases may explicitly skip when optional SDKs are absent.
Their installed-environment run is separate evidence and must report zero relevant
skips before a lesson claims that framework path was exercised.
"""
from pathlib import Path
import os,subprocess,sys
root=Path(__file__).resolve().parents[1]
folders=[root/'tests']
project_test_dirs={path.parent for path in (root/'projects').rglob('test_*.py') if not any(part in path.parts for part in ('.venv','node_modules','__pycache__','dist'))}
folders.extend(sorted(project_test_dirs))
failed=[]
for folder in folders:
 print(f'Running {folder.relative_to(root)}',flush=True)
 # Project examples intentionally support their documented project-local
 # imports. Every discovery process gets its own path and module namespace.
 # Keep the repository root too, for shared examples and fixture imports.
 paths=[str(root)]
 if folder.is_relative_to(root/'projects'):
  paths.append(str(root/'projects'/folder.relative_to(root/'projects').parts[0]))
 if os.environ.get('PYTHONPATH'):paths.append(os.environ['PYTHONPATH'])
 environment={**os.environ,'PYTHONPATH':os.pathsep.join(paths)}
 result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(folder),'-v'],cwd=root,env=environment)
 if result.returncode:failed.append(str(folder.relative_to(root)))
if failed:
 print('Failed test directories: '+', '.join(failed),file=sys.stderr)
 sys.exit(1)
print(f'PASS: {len(folders)} independently discovered test directories')
