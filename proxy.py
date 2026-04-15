#!/usr/bin/env python3
"""
本地代理服务器 - 转发请求到 Anthropic API（解决浏览器 CORS 限制）
使用方法：python proxy.py
然后打开 index.html 使用 Claude API 功能
"""
import http.server
import urllib.request
import urllib.error
import json
import sys

PORT = 8787

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[代理] {format % args}")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        api_key = self.headers.get('x-api-key', '')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=body,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            },
            method='POST'
        )
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, x-api-key, anthropic-version')

if __name__ == '__main__':
    server = http.server.HTTPServer(('localhost', PORT), ProxyHandler)
    print(f"代理服务器已启动：http://localhost:{PORT}")
    print("保持此窗口开启，然后使用网页中的 Claude API 功能")
    print("按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        sys.exit(0)
