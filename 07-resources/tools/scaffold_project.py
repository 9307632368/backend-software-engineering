"""Copy the included 2024-era FastAPI starter into a NEW directory.

Example:
    python tools/scaffold_project.py --dest ./my-task-api
"""

import argparse
from pathlib import Path
import shutil


TEMPLATE = Path(__file__).resolve().parents[1] / 'templates' / 'fastapi-starter'


def create_project(destination: Path, template: Path = TEMPLATE) -> Path:
    """Copy template with no overwrite. The target may not already exist."""
    if not template.is_dir():
        raise FileNotFoundError(f'Template not found: {template}')
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f'Destination already exists: {destination}')
    # copytree normally refuses existing directories; preserve that behavior.
    shutil.copytree(template, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description='Create a new FastAPI starter project')
    parser.add_argument('--dest', required=True, type=Path, help='New project directory')
    args = parser.parse_args()
    try:
        created = create_project(args.dest)
    except (OSError, FileNotFoundError) as exc:
        parser.exit(2, f'Could not create project: {exc}\n')
    print(f'Created: {created}')
    print('Next: cd into the folder, install requirements-dev.txt, then run python -m pytest -q')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
