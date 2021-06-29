import json
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional

from coppertone import TweetMonitor


class CoppertoneServer:
    def __init__(self, monitor: TweetMonitor):
        self.monitor = monitor

        self.server = HTTPServer(("", 8080), _CoppertoneServerRequestHandler)
        self.server.coppertone = self

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)

    def run(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()


class _CoppertoneServerRequestHandler(BaseHTTPRequestHandler):

    @property
    def _monitor(self) -> TweetMonitor:
        return self.server.coppertone.monitor

    def do_GET(self):
        if self.path == '/' or self.path == '/tweets':
            self.render_tweets()
        elif self.path == '/status':
            self.render_status()

    def _render_dict_as_json(self, obj: Dict[str, Any]) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(bytes(json.dumps(obj, default=str), "UTF-8"))

    def render_tweets(self):
        self._render_dict_as_json({
            "bogus": "test"
        })

    def render_status(self):
        self._render_dict_as_json({
            "server_started": self._monitor.start_dt,
            "twitter_handle": self._monitor.twitter_username,
        })
