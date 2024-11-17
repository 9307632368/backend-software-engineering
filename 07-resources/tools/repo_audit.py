"""Check whether the seven expected sections exist in the parent Git repo.

Example:
    python tools/repo_audit.py --root ..
    python tools/repo_audit.py --root .. --json
    python tools/repo_audit.py --root .. --strict
"""

import argparse
import json
from pathlib import Path

EXPECTED = (
    '01-fundamentals',
    '02-intermediate-concepts',
    '03-advanced-concepts',
    '04-industry-level-projects',
    '05-interview-preparation',
    '06-real-world-case-studies',
    '07-resources',
)


def inspect(root: Path) -> dict:
    root = root.resolve()
    sections = []
    for name in EXPECTED:
        section = root / name
        sections.append({
            'name': name,
            'present': section.is_dir(),
            'readme': (section / 'README.md').is_file(),
        })
    return {'root': str(root), 'sections': sections,
            'missing': [x['name'] for x in sections if not x['present']]}


def main() -> int:
    parser = argparse.ArgumentParser(description='Inspect backend repository section folders')
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--json', action='store_true', dest='json_output')
    parser.add_argument('--strict', action='store_true', help='Fail if a section is missing')
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f'Not a directory: {args.root}')
    result = inspect(args.root)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print('Backend repository section check')
        for item in result['sections']:
            state = 'present' if item['present'] else 'MISSING'
            note = 'README found' if item['readme'] else 'README not at section root'
            print(f"- {item['name']}: {state}; {note}")
        if result['missing']:
            print('Missing sections:', ', '.join(result['missing']))
    return 1 if args.strict and result['missing'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
