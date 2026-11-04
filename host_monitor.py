"""Windows CPU exporter and local Alertmanager webhook receiver."""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import psutil

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "webhook_events.jsonl"


class Metrics(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_error(404)
            return
        cpu = psutil.cpu_percent(interval=0.2)
        data = (f"# TYPE windows_cpu_usage_percent gauge\n"
                f"windows_cpu_usage_percent {cpu}\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class Webhook(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in ("/primary", "/computer"):
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1048576:
            self.send_error(413)
            return
        payload = json.loads(self.rfile.read(length))
        event = {"received_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                 "contact_point": self.path[1:], "status": payload.get("status"),
                 "alerts": [{"name": a.get("labels", {}).get("alertname"),
                             "status": a.get("status")}
                            for a in payload.get("alerts", [])]}
        with EVENTS.open("a", encoding="utf-8") as out:
            out.write(json.dumps(event, ensure_ascii=False) + "\n")
        print(event, flush=True)
        self.send_response(200)
        self.end_headers()


if __name__ == "__main__":
    Thread(target=ThreadingHTTPServer(("0.0.0.0", 9183), Metrics).serve_forever,
           daemon=True).start()
    print("Metrics :9183/metrics; webhook :9184/primary and /computer", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 9184), Webhook).serve_forever()
