"""Run tests project by project, so their individual `app.py` imports cannot clash."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
projects = sorted(p.parent for p in root.glob('*/**/app.py'))
assert len(projects) == 9, f'Expected 9 apps; found {len(projects)}'
failures = []
for project in projects:
    print(f'\n=== {project.relative_to(root)} ===', flush=True)
    result = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests'], cwd=project, check=False)
    if result.returncode:
        failures.append(str(project.relative_to(root)))
print(f'\nPassed projects: {len(projects)-len(failures)}/{len(projects)}')
if failures:
    print('Failed:', ', '.join(failures))
    sys.exit(1)
