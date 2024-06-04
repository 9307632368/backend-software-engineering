"""Run each standalone project's tests from its own directory."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PROJECTS = [
    'tutorials/01-circuit-breaker-retry',
    'tutorials/02-optimistic-locking',
    'tutorials/03-transactional-outbox',
    'system-design/04-url-shortener',
    'system-design/05-multi-tenant-reporting',
    'implementations/06-token-bucket-rate-limiter',
    'implementations/07-leased-job-queue',
    'implementations/08-api-observability',
]

if __name__ == '__main__':
    for name in PROJECTS:
        print(f'\n=== {name} ===', flush=True)
        result = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests'], cwd=ROOT / name)
        if result.returncode:
            raise SystemExit(result.returncode)
    print('\nAll advanced-concepts projects passed.')
