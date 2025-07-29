#!/usr/bin/env python3
"""
Simple HTTP server for the test results dashboard.
This script serves the dashboard files and provides an API for test results.
"""
import os
import json
import http.server
import socketserver
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Configuration
PORT = 8000
DASHBOARD_DIR = Path(__file__).parent.parent / 'dashboard'
DATA_DIR = DASHBOARD_DIR / 'data'
TEST_RESULTS_FILE = DATA_DIR / 'test_results.json'

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler for the dashboard server."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path.lstrip('/')
        
        # API endpoints
        if path == 'api/test-results':
            self.serve_test_results()
            return
        elif path == 'api/health':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'timestamp': self.date_time_string()
            }).encode('utf-8'))
            return
        
        # Serve static files
        try:
            # Default to index.html for the root path
            if path == '':
                path = 'index.html'
            
            # Check if the file exists
            file_path = Path(DASHBOARD_DIR) / path
            if not file_path.exists():
                self.send_error(HTTPStatus.NOT_FOUND, f"File not found: {path}")
                return
            
            # Set content type based on file extension
            if file_path.suffix == '.html':
                self.send_header('Content-Type', 'text/html')
            elif file_path.suffix == '.css':
                self.send_header('Content-Type', 'text/css')
            elif file_path.suffix == '.js':
                self.send_header('Content-Type', 'application/javascript')
            elif file_path.suffix == '.json':
                self.send_header('Content-Type', 'application/json')
            elif file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.ico']:
                self.send_header('Content-Type', f'image/{file_path.suffix[1:]}')
            else:
                self.send_header('Content-Type', 'application/octet-stream')
            
            # Serve the file
            with open(file_path, 'rb') as f:
                self.send_response(HTTPStatus.OK)
                self.end_headers()
                self.wfile.write(f.read())
                
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))
    
    def serve_test_results(self):
        """Serve test results as JSON."""
        try:
            # Check if test results file exists
            if not TEST_RESULTS_FILE.exists():
                self.send_error(
                    HTTPStatus.NOT_FOUND,
                    f"Test results not found: {TEST_RESULTS_FILE}"
                )
                return
            
            # Read and serve the test results
            with open(TEST_RESULTS_FILE, 'r') as f:
                test_results = json.load(f)
            
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(json.dumps(test_results).encode('utf-8'))
            
        except Exception as e:
            self.send_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Error reading test results: {str(e)}"
            )


def run_server(port=PORT):
    """Run the HTTP server."""
    # Ensure the data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create a test results file if it doesn't exist
    if not TEST_RESULTS_FILE.exists():
        with open(TEST_RESULTS_FILE, 'w') as f:
            json.dump({
                'timestamp': '2023-01-01T00:00:00Z',
                'suites': [],
                'stats': {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0,
                    'duration': 0.0
                },
                'coverage': {
                    'coverage_percent': 0,
                    'lines_covered': 0,
                    'lines_total': 0
                },
                'performance': {
                    'response_times': [],
                    'requests_per_second': 0,
                    'failures': 0,
                    'p95': 0
                }
            }, f, indent=2)
    
    # Start the server
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        print(f"Serving dashboard at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the server...")
            httpd.server_close()
            print("Server stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Results Dashboard Server')
    parser.add_argument('-p', '--port', type=int, default=PORT,
                        help=f'Port to run the server on (default: {PORT})')
    
    args = parser.parse_args()
    run_server(port=args.port)
