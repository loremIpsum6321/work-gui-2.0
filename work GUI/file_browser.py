from PyQt5.QtWidgets import QFileDialog

class FileBrowser:
    """Manages the file browser dialog."""

    def __init__(self, parent=None):
        """Initializes the FileBrowser."""
        self.parent = parent

    def get_file_path(self):
        """Opens the file browser dialog and returns the selected file path."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Open HTML File", "", "HTML Files (*.html *.htm)"
        )
        return file_path
