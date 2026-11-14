import importlib.util
import json
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

spec = importlib.util.spec_from_file_location('app', Path(__file__).parents[1] / 'app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class CollectionTests(unittest.TestCase):
    def test_deduplication_provenance_and_partial_failure(self):
        job = dict(seed="women's necklace", market='us', expanded=False, successful=0, errors=[], rows=[], done=0, status='running')
        def fake(term, market):
            if term.startswith('cheap '):
                raise TimeoutError('test timeout')
            return ['Necklace', 'necklace', 'gold necklace']
        app.collect(job, fake, lambda seconds: None)
        self.assertEqual(job['status'], 'complete')
        self.assertEqual(job['done'], 4)
        self.assertEqual(job['successful'], 3)
        self.assertEqual(len(job['rows']), 2)
        self.assertEqual(len(job['rows'][0]['queries']), 3)
        self.assertEqual(len(job['errors']), 1)

    def test_all_failures_are_not_silent(self):
        job = dict(seed='x', market='us', expanded=True, successful=0, errors=[], rows=[], done=0, status='running')
        def fail(*args):
            raise ValueError('invalid response')
        app.collect(job, fail, lambda seconds: None)
        self.assertEqual(len(job['errors']), 30)
        self.assertEqual(job['successful'], 0)
        self.assertEqual(job['rows'], [])

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.url = 'http://127.0.0.1:' + str(cls.server.server_port)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
    def test_page_markets_and_invalid_input(self):
        with urlopen(self.url) as r:
            self.assertIn('关键词工作台', r.read().decode())
        with urlopen(self.url+'/api/markets') as r:
            self.assertEqual(len(json.load(r)), 12)
        with self.assertRaises(HTTPError) as err:
            urlopen(Request(self.url+'/api/jobs',data=b'{}',headers={'Content-Type':'application/json'}))
        self.assertEqual(err.exception.code, 400)
    def test_foreign_origin_rejected(self):
        with self.assertRaises(HTTPError) as err:
            urlopen(Request(self.url+'/api/markets',headers={'Origin':'https://example.com'}))
        self.assertEqual(err.exception.code, 403)

if __name__ == '__main__':
    unittest.main()
