"""
Health check endpoint for monitoring the application.
This module provides a simple HTTP server that exposes health check endpoints.
"""
import http.server
import json
import logging
import socket
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import psycopg2
import redis
from http import HTTPStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for health check endpoints."""
    
    def __init__(self, *args, **kwargs):
        self.db_config = self.get_db_config()
        self.redis_config = self.get_redis_config()
        super().__init__(*args, **kwargs)
    
    @staticmethod
    def get_db_config() -> Dict[str, str]:
        """Get database configuration from environment variables."""
        return {
            'dbname': 'socialmedia',
            'user': 'socialmedia',
            'password': '',
            'host': 'localhost',
            'port': '5432'
        }
    
    @staticmethod
    def get_redis_config() -> Dict[str, Any]:
        """Get Redis configuration from environment variables."""
        return {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None
        }
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connection and basic functionality."""
        start_time = time.time()
        status = 'ok'
        error = None
        
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
                if cur.fetchone()[0] != 1:
                    raise ValueError('Unexpected database response')
            conn.close()
        except Exception as e:
            status = 'error'
            error = str(e)
            logger.error(f"Database check failed: {error}")
        
        return {
            'status': status,
            'duration_seconds': round(time.time() - start_time, 4),
            'error': error
        }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connection and basic functionality."""
        start_time = time.time()
        status = 'ok'
        error = None
        
        try:
            r = redis.Redis(**self.redis_config)
            if not r.ping():
                raise RuntimeError('Redis ping failed')
        except Exception as e:
            status = 'error'
            error = str(e)
            logger.error(f"Redis check failed: {error}")
        
        return {
            'status': status,
            'duration_seconds': round(time.time() - start_time, 4),
            'error': error
        }
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.handle_health_check()
        elif self.path == '/ready':
            self.handle_readiness_check()
        elif self.path == '/live':
            self.handle_liveness_check()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
    
    def handle_health_check(self):
        """Handle health check request."""
        start_time = time.time()
        checks = {
            'database': self.check_database(),
            'redis': self.check_redis(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Determine overall status
        status = 'ok'
        for check in checks.values():
            if isinstance(check, dict) and check.get('status') == 'error':
                status = 'error'
                break
        
        response = {
            'status': status,
            'checks': checks,
            'uptime_seconds': round(time.time() - self.server.start_time, 2)
        }
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def handle_readiness_check(self):
        """Handle readiness check request."""
        checks = {
            'database': self.check_database(),
            'redis': self.check_redis()
        }
        
        # Determine if application is ready
        is_ready = all(
            check.get('status') == 'ok'
            for check in checks.values()
            if isinstance(check, dict)
        )
        
        status_code = HTTPStatus.OK if is_ready else HTTPStatus.SERVICE_UNAVAILABLE
        
        response = {
            'status': 'ready' if is_ready else 'not_ready',
            'checks': checks,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def handle_liveness_check(self):
        """Handle liveness check request."""
        response = {
            'status': 'alive',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))


class HealthCheckServer:
    """Simple HTTP server for health checks."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the health check server in a separate thread."""
        def run():
            self.server = http.server.HTTPServer((self.host, self.port), HealthCheckHandler)
            self.server.start_time = time.time()
            logger.info(f"Health check server started on http://{self.host}:{self.port}")
            self.server.serve_forever()
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the health check server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Health check server stopped")


def start_health_check_server(host: str = '0.0.0.0', port: int = 8000) -> HealthCheckServer:
    """Start the health check server and return the server instance."""
    server = HealthCheckServer(host, port)
    server.start()
    return server


from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the health check server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()
    
    server = start_health_check_server(args.host, args.port)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
