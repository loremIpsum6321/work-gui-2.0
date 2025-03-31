import http.server
import socketserver
import threading
import os
from .utils import get_local_ip  # Updated import

class FaviconHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            # Serve the favicon.ico file
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            with open('assets/favicon.ico', 'rb') as f:
                self.wfile.write(f.read())
        else:
            # Use the default handler for other requests
            super().do_GET()

class ServerManager:
    """Manages the local HTTP server."""

    def __init__(self, port=8000):
        """Initializes the ServerManager."""
        self.port = port
        self.httpd = None
        self.server_thread = None

    def start_server(self):
        """Starts the local HTTP server in a separate thread."""
        handler = FaviconHandler
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True  # Allow the main thread to exit
        self.server_thread.start()
        print(f"Server started on port {self.port}")
        local_ip = get_local_ip()
        if local_ip:
            print(f"Access it at http://{local_ip}:{self.port}")
        else:
            print(f"Access it at http://localhost:{self.port}")

    def stop_server(self):
        """Stops the local HTTP server."""
        if self.httpd:
            self.httpd.shutdown()
            self.server_thread.join()
            print("Server stopped")
