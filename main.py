import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QLabel, QWidget
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, QPropertyAnimation, QEasingCurve, QTimer, QEvent, QMargins
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView

from core.webview_manager import WebviewManager
from core.server_manager import ServerManager, get_local_ip
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
        
        #padding for the window
        self.padding = QMargins(0, 0, 0, 50) #arguments are (left, top, right, bottom) 50 px to be ontop of the start bar

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
        self.resize_widget.installEventFilter(self)
        self.resize_widget.enterEvent = self.resize_enter_event
        self.resize_widget.mousePressEvent = self.resize_mouse_press_event

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
                padding-left: 10px; /* Add padding to the left */
                padding-right: 10px; /* Add padding to the right */
            }
            QLabel:hover {
                color: rgba(255, 255, 255, 255);
                background-color: rgba(24, 28, 39, 100);
            }
        """)
        self.close_button.setAlignment(Qt.AlignCenter)
        self.close_button.setFixedSize(40, 20) #increased the width from 20 to 40
        self.close_button.mousePressEvent = self.close_app
        self.close_button.hide()
       
        self.close_animation = QPropertyAnimation(self, b"windowOpacity")
        self.close_animation.setDuration(500)
        self.close_animation.setEndValue(0)
        self.close_animation.finished.connect(self.close)

        self.close_button_animation = QPropertyAnimation(self.close_button, b"windowOpacity")
        self.close_button_animation.setDuration(200)
        self.close_button_animation.setEasingCurve(QEasingCurve.OutQuad)

    def close_app(self, event):
        """Closes the application."""
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

    def resizeEvent(self, event):
        """Override resizeEvent to keep the window pinned to the left."""
        screen = QDesktopWidget().screenGeometry()        
        self.webview_manager.setContentsMargins(self.padding)
        self.setGeometry(0, 0, self.width(), screen.height())
        if self.close_button:
            self.close_button.move(self.width() - 40, 0) #changed from 20 to 40
        self.resize_widget.setGeometry(self.width() - 10, 0, 10, self.height())
        super().resizeEvent(event)

    def enterEvent(self, event):
        """Shows the close button when the mouse enters the window."""
        if self.close_button:
            self.close_button.show()
            self.close_button.raise_()
            self.close_button_animation.setStartValue(0)
            self.close_button_animation.setEndValue(1)
            self.close_button_animation.start()

    def leaveEvent(self, event):
        """Hides the close button when the mouse leaves the window."""
        if self.close_button:
            self.close_button_animation.setEndValue(0)
            self.close_button_animation.start()
    
    def resize_enter_event(self, event):
        self.setCursor(Qt.SizeHorCursor)

    def resize_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def show(self):
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
