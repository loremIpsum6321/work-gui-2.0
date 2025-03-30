import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QShortcut, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from file_browser import FileBrowser
from utils import is_valid_url, get_local_ip
import os

class WebviewManager(QWidget):
    """Manages the webview and its behavior."""

    def __init__(self, server_manager):
        """Initializes the WebviewManager."""
        super().__init__()
        self.server_manager = server_manager
        self.setWindowTitle("Local Webview")
        self.setWindowFlag(Qt.FramelessWindowHint)  # Remove window frame
        self.showFullScreen()  # Start in fullscreen

        self.init_ui()

    def init_ui(self):
        """Initializes the user interface."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        self.webview = QWebEngineView(self)
        self.layout.addWidget(self.webview)

        self.url_bar = QLineEdit(self)
        self.url_bar.hide()  # Initially hidden
        self.layout.addWidget(self.url_bar)
        self.url_bar.returnPressed.connect(self.load_url)

        # Hotkey to show/hide URL bar (Ctrl+L)
        self.url_shortcut = QShortcut("Ctrl+L", self)
        self.url_shortcut.activated.connect(self.toggle_url_bar)

        # Hotkey to open file browser (Ctrl+O)
        self.file_shortcut = QShortcut("Ctrl+O", self)
        self.file_shortcut.activated.connect(self.open_file_browser)

        # Load the initial URL (local server index)
        self.load_initial_url()

    def load_initial_url(self):
        """Loads the initial URL (local server index)."""
        local_ip = get_local_ip()
        if local_ip:
            initial_url = f"http://{local_ip}:{self.server_manager.port}"
        else:
            initial_url = f"http://localhost:{self.server_manager.port}"
        self.webview.setUrl(QUrl(initial_url))

    def toggle_url_bar(self):
        """Toggles the visibility of the URL bar."""
        self.url_bar.setVisible(not self.url_bar.isVisible())
        if self.url_bar.isVisible():
            self.url_bar.setFocus()
            self.url_bar.setText(self.webview.url().toString())

    def load_url(self):
        """Loads the URL entered in the URL bar."""
        url = self.url_bar.text()
        if is_valid_url(url):
            self.webview.setUrl(QUrl(url))
        else:
            self.webview.setUrl(QUrl(f"http://{url}"))

    def open_file_browser(self):
        """Opens the file browser dialog."""
        file_browser = FileBrowser(self)
        file_path = file_browser.get_file_path()
        if file_path:
            self.webview.setUrl(QUrl.fromLocalFile(file_path))
