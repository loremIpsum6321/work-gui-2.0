import http.server
import socketserver
import threading
import os
from utils import get_local_ip

class ServerManager:
    """Manages the local HTTP server."""

    def __init__(self, port=8000):
        """Initializes the ServerManager."""
        self.port = port
        self.httpd = None
        self.server_thread = None

    def start_server(self):
        """Starts the local HTTP server in a separate thread."""
        handler = http.server.SimpleHTTPRequestHandler
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
