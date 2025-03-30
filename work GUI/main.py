import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QLabel, QWidget
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QPropertyAnimation, QEasingCurve, QTimer, QEvent
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from webview_manager import WebviewManager
from server_manager import ServerManager, get_local_ip
import os

class MainWindow(QMainWindow):
    """Main window class to manage the application window."""

    def __init__(self, server_manager):
        """Initializes the MainWindow."""
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)  # Remove window frame
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setMinimumSize(400, 600)

        self.oldPos = None
        self.close_button = None

        # Disable cache and offline storage
        settings = QWebEngineSettings.globalSettings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        #settings.setAttribute(QWebEngineSettings.OfflineStorageDefaultQuota, 0) #removed because it is not supported in the current version of QtWebEngine

        # Create the webview manager and set it as the central widget
        self.webview_manager = WebviewManager(server_manager)
        self.setCentralWidget(self.webview_manager)

        self.init_close_button()
        self.resize_widget = QWidget(self)
        self.resize_widget.setCursor(Qt.SizeHorCursor)
        self.resize_widget.setGeometry(390, 0, 10, self.height())
        self.resize_widget.installEventFilter(self)

    def init_close_button(self):
        """Initializes the close button."""
        self.close_button = QLabel(self)
        self.close_button.setText("X")
        self.close_button.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0);
                font-size: 20px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0);
                border-radius: 10px;
            }
            QLabel:hover {
                color: rgba(255, 255, 255, 255);
                background-color: rgba(255, 0, 0, 100);
            }
        """)
        self.close_button.setAlignment(Qt.AlignCenter)
        self.close_button.setFixedSize(20, 20)
        self.close_button.move(380, 0)
        self.close_button.mousePressEvent = self.close_app
        self.close_button.hide()
       
        self.close_animation = QPropertyAnimation(self, b"windowOpacity")
        self.close_animation.setDuration(500)
        self.close_animation.setEndValue(0)
        self.close_animation.finished.connect(self.close)

    def close_app(self, event):
        """Closes the application."""
       
        self.close_animation.setDuration(500)
        self.close_animation.setEndValue(0)
        self.close_animation.start()

    def eventFilter(self, obj, event):
        if obj == self.resize_widget and event.type() == QEvent.MouseMove:
            self.resize_window(event.globalPos())
        return super().eventFilter(obj, event)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.oldPos:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = None

    def resize_window(self, global_pos):
        """Resizes the window horizontally."""
        if self.oldPos:
            delta = global_pos.x() - self.oldPos.x()
            new_width = self.width() + delta
            if new_width >= self.minimumWidth():
                self.resize(new_width, self.height())
                self.oldPos = global_pos
                self.resize_widget.setGeometry(self.width() - 10, 0, 10, self.height())
                self.close_button.move(self.width() - 20, 0)

    def resizeEvent(self, event):
        """Override resizeEvent to keep the window pinned to the left."""
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, self.width(), screen.height())
        if self.close_button:
            self.close_button.move(380, 0)
        super().resizeEvent(event)

    def enterEvent(self, event):
        """Shows the close button when the mouse enters the window."""
        if self.close_button:
            self.close_button.show()
            self.close_button.raise_()
            self.close_button_animation = QPropertyAnimation(self.close_button, b"windowOpacity")
            self.close_button_animation.setDuration(200)
            self.close_button_animation.setStartValue(0)
            self.close_button_animation.setEndValue(1)
            self.close_button_animation.setEasingCurve(QEasingCurve.OutQuad)
            self.close_button_animation.start()

    def leaveEvent(self, event):
        """Hides the close button when the mouse leaves the window."""
        if self.close_button:
            self.close_button_animation = QPropertyAnimation(self.close_button, b"windowOpacity")
            self.close_button_animation.setDuration(200)
            self.close_button_animation.setEndValue(0)
            self.close_button_animation.start()
           
    def mouseMoveEvent(self, event):
        if self.resize_widget.underMouse():
            self.setCursor(Qt.SizeHorCursor)
        super().mouseMoveEvent(event)
    def show(self):
        self.resizeEvent(None)
        super().show()

def main():
    """Main function to start the application."""
    app = QApplication(sys.argv)

    # Start the local server
    server_manager = ServerManager()
    server_manager.start_server()
    local_ip = get_local_ip()
    if local_ip:
        print(f"Server started on port {server_manager.port}")
        print(f"Access it at http://{local_ip}:{server_manager.port}")
    else:
        print(f"Server started on port {server_manager.port}")
        print(f"Access it at http://localhost:{server_manager.port}")

    # Create and show the main window
    main_window = MainWindow(server_manager)
   
    main_window.show()

    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
