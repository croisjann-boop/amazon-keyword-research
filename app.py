#!/usr/bin/env python3
"""Local Amazon autocomplete research UI. Python standard library only."""
import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

MARKETS = {
    'us': ('美国', 'amazon.com', 'ATVPDKIKX0DER'),
    'uk': ('英国', 'amazon.co.uk', 'A1F83G8C2ARO7P'),
    'de': ('德国', 'amazon.de', 'A1PA6795UKMFR9'),
    'fr': ('法国', 'amazon.fr', 'A13V1IB3VIYZZH'),
    'it': ('意大利', 'amazon.it', 'APJ6JRA9NG5V4'),
    'es': ('西班牙', 'amazon.es', 'A1RKKUPIHCS9HS'),
    'jp': ('日本', 'amazon.co.jp', 'A1VC38T7YXB528'),
    'ca': ('加拿大', 'amazon.ca', 'A2EUQ1WTGCTBG2'),
    'au': ('澳洲', 'amazon.com.au', 'A39IBJ37TRP1C6'),
    'in': ('印度', 'amazon.in', 'A21TJRUUN4KGV'),
    'mx': ('墨西哥', 'amazon.com.mx', 'A1AM78C64UM0Y8'),
    'br': ('巴西', 'amazon.com.br', 'A2Q3Y263D00KWC'),
}
ROOT = Path(__file__).parent
LOCK = threading.Lock()
JOBS = {}


def suggestions(term, market):
    _, domain, mid = MARKETS[market]
    url = 'https://completion.' + domain + '/api/2017/suggestions?' + urlencode({'mid': mid, 'alias': 'aps', 'prefix': term})
    req = Request(url, headers={'User-Agent': 'AmazonKeywordResearch/1.0', 'Accept': 'application/json'})
    with urlopen(req, timeout=8) as response:
        payload = response.read(1024 * 1024)
    data = json.loads(payload)
    if not isinstance(data, dict) or not isinstance(data.get('suggestions'), list):
        raise ValueError('接口返回了无法识别的数据')
    return [s['value'].strip() for s in data['suggestions'] if isinstance(s, dict) and isinstance(s.get('value'), str) and s['value'].strip()]


def collect(job, fetch=suggestions, pause=time.sleep):
    seed, market = job['seed'], job['market']
    terms = [seed] + [p + seed for p in ('best ', 'cheap ', 'top ')]
    if job['expanded']:
        terms += [seed + ' ' + c for c in 'abcdefghijklmnopqrstuvwxyz']
    found = {}
    try:
        for i, term in enumerate(terms):
            try:
                values = fetch(term, market)
                with LOCK:
                    for value in values:
                        key = value.casefold()
                        if key not in found:
                            found[key] = {'keyword': value, 'queries': [term]}
                        elif term not in found[key]['queries']:
                            found[key]['queries'].append(term)
                    job['successful'] += 1
            except Exception as exc:
                with LOCK:
                    job['errors'].append({'query': term, 'message': str(exc)[:240]})
            with LOCK:
                job.update(done=i + 1, rows=list(found.values()))
            if i + 1 < len(terms):
                pause(0.4)
    finally:
        with LOCK:
            job['status'] = 'complete'


class Handler(BaseHTTPRequestHandler):
    def reply(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def allowed(self):
        # Bind to loopback and reject foreign Host / Origin to prevent browser drive-by requests.
        host = self.headers.get('Host', '')
        valid = {'127.0.0.1:' + str(self.server.server_port), 'localhost:' + str(self.server.server_port)}
        origin = self.headers.get('Origin')
        return host in valid and (not origin or origin in {'http://' + h for h in valid})

    def do_GET(self):
        if not self.allowed():
            return self.reply({'error': '仅允许本机访问'}, 403)
        path = urlsplit(self.path).path
        if path == '/':
            body = (ROOT / 'web/index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            return self.wfile.write(body)
        if path == '/api/markets':
            return self.reply({k: v[0] for k, v in MARKETS.items()})
        if path.startswith('/api/jobs/'):
            with LOCK:
                job = JOBS.get(path.rsplit('/', 1)[-1])
                return self.reply(job if job else {'error': '任务不存在，请重新采集'}, 200 if job else 404)
        self.reply({'error': '页面不存在'}, 404)

    def do_POST(self):
        if not self.allowed():
            return self.reply({'error': '仅允许本机访问'}, 403)
        if self.path != '/api/jobs':
            return self.reply({'error': '接口不存在'}, 404)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 4096:
                raise ValueError('请求大小无效')
            data = json.loads(self.rfile.read(size))
            seed = data.get('seed', '').strip()
            market = data.get('market', '')
            if not seed or len(seed) > 120 or any(ord(c) < 32 for c in seed):
                raise ValueError('请输入 1–120 个字符的产品核心词')
            if market not in MARKETS:
                raise ValueError('请选择支持的站点')
        except (ValueError, TypeError, AttributeError):
            return self.reply({'error': '请输入有效核心词与站点（核心词最多 120 字）'}, 400)
        with LOCK:
            if any(j['status'] == 'running' for j in JOBS.values()):
                return self.reply({'error': '已有采集任务运行中，请等待完成'}, 409)
            # Bounded in-memory history; restarting the app clears it.
            while len(JOBS) >= 20:
                JOBS.pop(next(iter(JOBS)))
            ident = uuid.uuid4().hex
            expanded = data.get('expanded') is True
            job = dict(id=ident, seed=seed, market=market, expanded=expanded, status='running', done=0,
                       total=30 if expanded else 4, successful=0, errors=[], rows=[],
                       collected_at=datetime.now(timezone.utc).isoformat())
            JOBS[ident] = job
        threading.Thread(target=collect, args=(job,), daemon=True).start()
        self.reply({'id': ident}, 202)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8765'))
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'关键词工作台已启动：http://127.0.0.1:{port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
