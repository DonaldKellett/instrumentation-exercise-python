#!/usr/bin/python

import logging
import random
import threading
import time
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from prometheus_client import MetricsHandler, Counter, Gauge, Histogram
from urllib.parse import urlparse

request_latency_seconds = Histogram('request_latency_seconds', 'Request latency in seconds', ['method', 'path', 'status'])
request_latency_seconds.labels(method='GET', path='/api/foo', status=200)
request_latency_seconds.labels(method='GET', path='/api/bar', status=200)
batch_jobs = Counter('batch_jobs', 'Total number of batch jobs executed')
batch_jobs_failed = Counter('batch_jobs_failed', 'Total number of batch jobs failed')
batch_jobs_last_success = Gauge('batch_jobs_last_success', 'UNIX timestamp of last successful batch job')
api_requests = Counter('api_requests', 'Total number of API requests', ['method', 'path', 'status'])
api_requests.labels(method='GET', path='/api/foo', status=200)
api_requests.labels(method='GET', path='/api/bar', status=200)

def handler_404(self):
    start = time.time()
    self.send_response(404)
    end = time.time()
    request_latency_seconds.labels(method=self.command, path=self.path, status=404).observe(end - start)
    api_requests.labels(method=self.command, path=self.path, status=404).inc()

def handler_foo(self):
    start = time.time()
    logging.info("Handling foo...")
    time.sleep(.075 + random.random() * .05)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Handled foo")
    end = time.time()
    request_latency_seconds.labels(method=self.command, path=self.path, status=200).observe(end - start)
    api_requests.labels(method=self.command, path=self.path, status=200).inc()

def handler_bar(self):
    start = time.time()
    logging.info("Handling bar...")
    time.sleep(.15 + random.random() * .1)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Handled bar")
    end = time.time()
    request_latency_seconds.labels(method=self.command, path=self.path, status=200).observe(end - start)
    api_requests.labels(method=self.command, path=self.path, status=200).inc()

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
            batch_jobs_last_success.set_to_current_time()
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
