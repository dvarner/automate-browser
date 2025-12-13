"""
About dialog - shows application information.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class AboutDialog(QDialog):
    """Dialog showing application information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # App name
        title = QLabel("Browser Session Manager")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: black;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Version
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("color: black;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        # Description
        description = QLabel(
            "A desktop application for managing browser tab sessions.\n\n"
            "Save, organize, and restore your browser tabs with ease.\n\n"
            "Built with PyQt6 and Playwright"
        )
        description.setStyleSheet("color: black;")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
