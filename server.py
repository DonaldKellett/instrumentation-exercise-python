#!/usr/bin/python

import logging
import random
import threading
import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from prometheus_client import MetricsHandler, Counter, Gauge
from urllib.parse import urlparse
from datetime import datetime

print(time.mktime(datetime.now().timetuple()))

batch_jobs = Counter('batch_jobs', 'Total number of batch jobs executed')
batch_jobs_failed = Counter('batch_jobs_failed', 'Total number of batch jobs failed')
batch_jobs_last_success = Gauge('batch_jobs_last_success', 'UNIX timestamp of last successful batch job')

def handler_404(self):
    self.send_response(404)

def handler_foo(self):
    logging.info("Handling foo...")
    time.sleep(.075 + random.random() * .05)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Handled foo")

def handler_bar(self):
    logging.info("Handling bar...")
    time.sleep(.15 + random.random() * .1)

    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Handled bar")

ROUTES = {
    "/api/foo": handler_foo,
    "/api/bar": handler_bar
}

class Handler(MetricsHandler):
    def do_GET(self):
        endpoint = urlparse(self.path).path
        if endpoint == '/metrics':
            return super(Handler, self).do_GET()
        return ROUTES.get(endpoint, handler_404)(self)

class MultiThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Server(threading.Thread):
    def run(self):
        httpd = MultiThreadedHTTPServer(('', 12345), Handler)
        httpd.serve_forever()

def background_task():
    logging.info("Starting background task loop...")
    while True:
        logging.info("Performing background task...")
        # Simulate a random duration that the background task needs to be completed.
        time.sleep(1 + random.random() * 0.5)

        # Simulate the background task either succeeding or failing (with a 30% probability).
        if random.random() > 0.3:
            logging.info("Background task completed successfully.")
            batch_jobs_last_success.set(time.mktime(datetime.now().timetuple()))
        else:
            logging.warning("Background task failed.")
            batch_jobs_failed.inc()
        batch_jobs.inc()

        time.sleep(5)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    s = Server()
    s.daemon = True
    s.start()
    background_task()
