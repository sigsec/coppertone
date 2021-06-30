import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any

from coppertone import TweetMonitor


class CoppertoneServer:
    def __init__(self, port: int, monitor: TweetMonitor):
        self.monitor = monitor

        self.server = HTTPServer(("", port), _CoppertoneServerRequestHandler)
        self.server.coppertone = self
        self.requests_handled = 0

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.setDaemon(True)

    def run(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()


class _CoppertoneServerRequestHandler(BaseHTTPRequestHandler):

    @property
    def _server(self) -> CoppertoneServer:
        # noinspection PyUnresolvedReferences
        return self.server.coppertone

    @property
    def _monitor(self) -> TweetMonitor:
        return self._server.monitor

    def log_message(self, format: str, *args: Any) -> None:
        # Silence log output.
        pass

    def do_GET(self):
        if self.path == '/' or self.path == '/tweets':
            self.render_tweets()
        elif self.path == '/status':
            self.render_status()
        else:
            return

        self._server.requests_handled += 1

    def _render_obj_as_json(self, obj: Any) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        self.wfile.write(bytes(json.dumps(obj, default=str), "UTF-8"))

    def render_tweets(self):
        self._render_obj_as_json(self._monitor.tweets)

    def render_status(self):
        self._render_obj_as_json({
            "coppertone": {
                "server_started": self._monitor.start_dt,
                "requests_handled": self._server.requests_handled,
            },
            "monitor": {
                "twitter_handle": self._monitor.twitter_handle,
                "user_id": self._monitor.user_id,
                "poll_rate": self._monitor.poll_rate,
                "num_tweets_cached": len(self._monitor.tweets),
            },
        })
