"""
Browser status bar widget - shows browser running status.
"""

from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import QTimer


class BrowserStatusBar(QStatusBar):
    """Custom status bar showing browser status."""

    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.polling_timer = None

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        # Browser status indicator
        self.status_label = QLabel("Browser: Not Running")
        self.status_label.setStyleSheet("color: #d9534f;")  # Red for not running
        self.addPermanentWidget(self.status_label)

        # Initial status check
        self.update_browser_status()

    def start_polling(self):
        """Start polling browser status."""
        if self.polling_timer is None:
            self.polling_timer = QTimer()
            self.polling_timer.timeout.connect(self.update_browser_status)
            self.polling_timer.start(2000)  # Poll every 2 seconds

    def stop_polling(self):
        """Stop polling browser status."""
        if self.polling_timer:
            self.polling_timer.stop()
            self.polling_timer = None

    def update_browser_status(self):
        """Update the browser status display."""
        is_running = self.session_manager.check_browser_status()

        if is_running:
            self.status_label.setText("Browser: Running")
            self.status_label.setStyleSheet("color: #5cb85c;")  # Green for running
        else:
            self.status_label.setText("Browser: Not Running")
            self.status_label.setStyleSheet("color: #d9534f;")  # Red for not running
