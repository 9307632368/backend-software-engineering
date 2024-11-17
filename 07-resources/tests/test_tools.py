import tempfile
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from tools.scaffold_project import TEMPLATE, create_project
from tools.repo_audit import EXPECTED, inspect
from tools.api_probe import probe


class ScaffoldTests(unittest.TestCase):
    def test_template_exists(self):
        self.assertTrue((TEMPLATE / 'requirements.txt').is_file())

    def test_create_project_copies_source(self):
        with tempfile.TemporaryDirectory() as folder:
            dst = Path(folder) / 'my-api'
            created = create_project(dst)
            self.assertEqual(created, dst.resolve())
            self.assertTrue((dst / 'app' / 'main.py').exists())
            self.assertTrue((dst / '.github' / 'workflows' / 'test.yml').exists())

    def test_does_not_overwrite_existing_project(self):
        with tempfile.TemporaryDirectory() as folder:
            dst = Path(folder) / 'existing'
            dst.mkdir()
            (dst / 'keep.txt').write_text('do not delete', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                create_project(dst)
            self.assertEqual((dst / 'keep.txt').read_text(encoding='utf-8'), 'do not delete')

    def test_missing_template_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                create_project(Path(folder) / 'new', Path(folder) / 'not-here')


class AuditTests(unittest.TestCase):
    def test_missing_sections(self):
        with tempfile.TemporaryDirectory() as folder:
            result = inspect(Path(folder))
            self.assertEqual(len(result['missing']), len(EXPECTED))

    def test_all_present(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in EXPECTED:
                (root / name).mkdir()
            result = inspect(root)
            self.assertFalse(result['missing'])
            self.assertTrue(all(item['present'] for item in result['sections']))

    def test_detect_readme(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / EXPECTED[0]).mkdir()
            (root / EXPECTED[0] / 'README.md').write_text('# hi', encoding='utf-8')
            result = inspect(root)
            self.assertTrue(result['sections'][0]['readme'])
            self.assertFalse(result['sections'][1]['readme'])


class APIProbeTests(unittest.TestCase):
    def test_reject_non_http_url(self):
        with self.assertRaises(ValueError):
            probe('file:///etc/passwd')

    def test_reject_missing_host(self):
        with self.assertRaises(ValueError):
            probe('http:///health')

    def test_reject_bad_timeout(self):
        with self.assertRaises(ValueError):
            probe('http://localhost:1/health', 0)

    def test_json_response(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = b'{"status":"ok"}'
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            status, result = probe(f'http://127.0.0.1:{server.server_port}/health')
            self.assertEqual(status, 200)
            self.assertEqual(result, {'status': 'ok'})
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == '__main__':
    unittest.main()
