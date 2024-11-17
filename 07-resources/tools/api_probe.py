"""Tiny HTTP health probe with no external dependencies.

Example:
    python tools/api_probe.py http://127.0.0.1:8000/health
"""

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def probe(url: str, timeout: float = 3.0) -> tuple[int, object]:
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise ValueError('Expected an http:// or https:// URL with a hostname')
    if timeout <= 0:
        raise ValueError('Timeout must be > 0')
    req = Request(url, headers={'Accept': 'application/json'}, method='GET')
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read(64_000)
            status = response.status
    except HTTPError as exc:
        status = exc.code
        raw = exc.read(64_000)
    try:
        body = json.loads(raw) if raw else None
    except (UnicodeError, ValueError):
        body = raw.decode('utf-8', errors='replace')
    return status, body


def main() -> int:
    parser = argparse.ArgumentParser(description='Send a GET request to an API health URL')
    parser.add_argument('url', nargs='?', default='http://127.0.0.1:8000/health')
    parser.add_argument('--timeout', type=float, default=3.0)
    args = parser.parse_args()
    try:
        code, body = probe(args.url, args.timeout)
    except (ValueError, URLError, TimeoutError, OSError) as exc:
        print('Probe failed:', exc)
        return 2
    print('HTTP status:', code)
    print('Response:', json.dumps(body, indent=2, ensure_ascii=False))
    return 0 if 200 <= code < 300 else 1


if __name__ == '__main__':
    raise SystemExit(main())
