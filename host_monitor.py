"""Метрика загрузки процессора Windows и прием уведомлений от Alertmanager."""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock, Thread

import psutil

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "webhook_events.jsonl"
EVENTS_LOCK = Lock()
CONTACT_POINTS = ("/application", "/computer", "/reserve")


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

    def log_message(self, *args):
        pass


class Webhook(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path not in CONTACT_POINTS:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1048576:
            self.send_error(413)
            return
        payload = json.loads(self.rfile.read(length))
        received = time.strftime("%Y-%m-%d %H:%M:%S")
        alerts = [{"name": a.get("labels", {}).get("alertname"),
                   "group": a.get("labels", {}).get("group"),
                   "status": a.get("status"),
                   "description": a.get("annotations", {}).get("description")}
                  for a in payload.get("alerts", [])]
        event = {"received_at": received, "contact_point": self.path[1:],
                 "status": payload.get("status"), "alerts": alerts}
        # уведомления приходят в разные потоки одновременно
        with EVENTS_LOCK, EVENTS.open("a", encoding="utf-8") as out:
            out.write(json.dumps(event, ensure_ascii=False) + "\n")
        for a in alerts:
            print(f"{received}  {self.path[1:]:<12} {a['status'].upper():<9} "
                  f"{a['name']:<20} {a['description']}", flush=True)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    Thread(target=ThreadingHTTPServer(("0.0.0.0", 9183), Metrics).serve_forever,
           daemon=True).start()
    Thread(target=ThreadingHTTPServer(("0.0.0.0", 9185), Webhook).serve_forever,
           daemon=True).start()
    print("Метрика:  http://localhost:9183/metrics", flush=True)
    print("Webhook:  :9184/application, :9184/computer, :9185/reserve", flush=True)
    print("Жду уведомления от Alertmanager...", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 9184), Webhook).serve_forever()
