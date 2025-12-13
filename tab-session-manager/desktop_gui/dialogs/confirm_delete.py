"""
Confirm delete dialog - asks for confirmation before deleting a session.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt


class ConfirmDeleteDialog(QDialog):
    """Dialog for confirming session deletion."""

    def __init__(self, session_name, parent=None):
        super().__init__(parent)
        self.session_name = session_name
        self.setWindowTitle("Confirm Delete")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Warning message
        message = QLabel(
            f"Are you sure you want to delete the session '{self.session_name}'?\n\n"
            "This action cannot be undone."
        )
        message.setStyleSheet("color: black;")
        message.setWordWrap(True)
        layout.addWidget(message)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("background-color: #d9534f; color: white;")
        delete_button.clicked.connect(self.accept)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)
