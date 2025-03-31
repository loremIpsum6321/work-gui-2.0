# Local Web view Application

This is a custom web view application built with Python and PyQt5. It's designed to display web content, primarily local HTML files, in a clean, full screen environment without the usual browser chrome.

## Features

*   **Fullscreen Web view:** The application runs in full screen mode, providing an immersive experience without any window borders or title bars.
*   **Hidden URL Bar:** The URL bar is hidden by default. You can toggle its visibility using the `Ctrl+L` hotkey.
*   **Local HTTP Server:** On startup, the application automatically starts a local HTTP server using `python -m http.server` in the background. This allows you to easily view local HTML files.
*   **Local File Browser:** You can browse and open local HTML files using the `Ctrl+O` hotkey. A file dialog will appear, allowing you to select the desired file.
*   **URL Input:** When the URL bar is visible, you can type in a URL and press Enter to navigate to that page. It supports both local server addresses and external URLs.
*   **Clean Interface:** The application is designed to be as clean and uncluttered as possible, focusing on the web content.
*   **OOP Design:** The code is structured using object-oriented programming principles, making it modular and maintainable.
*   **Well-Documented:** The code is thoroughly documented with docstrings and comments to explain its functionality.

## File Structure

