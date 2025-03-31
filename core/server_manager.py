import http.server
import socketserver
import threading
import os
import functools # Import functools
from .utils import get_local_ip # Keep your relative import

# Define the handler class globally
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    # The 'directory' argument will be passed via functools.partial later
    # The parent __init__ will store it in self.directory

    def do_GET(self):
        # Access the directory the handler was initialized with
        serve_dir = self.directory

        if self.path == '/favicon.ico':
            # Construct the absolute path to the favicon
            favicon_path = os.path.join(serve_dir, 'assets', 'favicon.ico')
            if os.path.isfile(favicon_path): # Check if the file exists
                try:
                    with open(favicon_path, 'rb') as f:
                        self.send_response(200)
                        self.send_header('Content-type', 'image/x-icon')
                        self.end_headers()
                        self.wfile.write(f.read())
                except IOError as e:
                    print(f"Error reading favicon: {e}")
                    self.send_error(500, f"Error reading favicon: {e}")
            else:
                # Favicon not found - send 404 is cleaner than empty response
                self.send_error(404, "Favicon Not Found")
            # Return here to prevent falling through to the default handler
            return

        elif self.path == '/':
            # Point to index.html within the specified directory
            self.path = '/index.html'
            # Let the parent SimpleHTTPRequestHandler handle serving index.html
            # from the correct 'directory' it was initialized with.
            super().do_GET()

        else:
            # Let the parent SimpleHTTPRequestHandler handle serving other files
            # (like CSS, JS in assets) from the correct 'directory'.
            super().do_GET()

class ServerManager:
    """Manages the local HTTP server."""

    def __init__(self, port=8000):
        """Initializes the ServerManager."""
        self.port = port
        self.httpd = None
        self.server_thread = None
        # --- Determine the directory to serve ---
        # Assume this script (server_manager.py) is in 'core'
        # Go up one level to the project root, then down to 'ui/web'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir) # Goes up from core to python dir
        self.serve_directory = os.path.join(project_root, 'ui', 'web')
        print(f"Attempting to serve files from: {self.serve_directory}")
        # --- Basic checks ---
        if not os.path.isdir(self.serve_directory):
            print(f"ERROR: Serve directory does not exist: {self.serve_directory}")
        elif not os.path.isfile(os.path.join(self.serve_directory, "index.html")):
             print(f"WARNING: index.html not found in {self.serve_directory}")


    def start_server(self):
        """Starts the local HTTP server in a separate thread."""
        if not os.path.isdir(self.serve_directory):
             print("Cannot start server: Serve directory is invalid.")
             return # Don't start if the directory is wrong

        # --- Use functools.partial to create a handler factory ---
        # This creates a new handler class on the fly that has the 'directory' argument preset
        HandlerWithDirectory = functools.partial(CustomHandler, directory=self.serve_directory)

        try:
            # Use the factory to create handler instances
            self.httpd = socketserver.TCPServer(("", self.port), HandlerWithDirectory)

            self.server_thread = threading.Thread(target=self.httpd.serve_forever)
            self.server_thread.daemon = True # Allow the main thread to exit
            self.server_thread.start()

            print(f"Server started on port {self.port}")
            print(f"Serving directory: {self.serve_directory}")
            local_ip = get_local_ip()
            if local_ip:
                print(f"Access it at http://{local_ip}:{self.port} or http://localhost:{self.port}")
            else:
                print(f"Access it at http://localhost:{self.port}")

        except OSError as e:
             print(f"ERROR starting server: {e}")
             print("Is the port already in use?")
             self.httpd = None # Ensure httpd is None if setup failed
        except Exception as e:
             print(f"An unexpected error occurred during server startup: {e}")
             self.httpd = None


    def stop_server(self):
        """Stops the local HTTP server."""
        if self.httpd:
            print("Stopping server...")
            self.httpd.shutdown() # Shuts down the server loop
            self.httpd.server_close() # Closes the server socket
            if self.server_thread:
                self.server_thread.join() # Waits for the thread to finish
            print("Server stopped")
        else:
             print("Server not running or failed to start.")