"""
New session dialog - prompts user to create a new browser session.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QSpinBox, QPushButton, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt


class NewSessionDialog(QDialog):
    """Dialog for creating a new browser session."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Session")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.session_name = ""
        self.auto_save_enabled = True
        self.auto_save_interval = 3.0
        self.browser_type = "chrome"
        self.incognito_mode = False

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Session name input
        name_label = QLabel("Session Name:")
        name_label.setStyleSheet("color: black;")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., my-work-session")
        self.name_input.setStyleSheet("QLineEdit { color: black; }")
        layout.addWidget(self.name_input)

        # Validation hint
        hint_label = QLabel("Only letters, numbers, dashes, and underscores allowed")
        hint_label.setStyleSheet("color: #666; font-size: 9pt;")
        layout.addWidget(hint_label)

        # Browser selection
        browser_layout = QHBoxLayout()
        browser_label = QLabel("Browser:")
        browser_label.setStyleSheet("color: black;")
        browser_layout.addWidget(browser_label)

        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Chrome", "Brave", "Firefox", "Chromium"])
        self.browser_combo.setCurrentText("Chrome")
        self.browser_combo.setStyleSheet("QComboBox { color: black; }")
        browser_layout.addWidget(self.browser_combo)
        browser_layout.addStretch()

        layout.addLayout(browser_layout)

        # Incognito mode checkbox
        self.incognito_checkbox = QCheckBox("Launch in Incognito/Private mode")
        self.incognito_checkbox.setChecked(False)
        self.incognito_checkbox.setStyleSheet("color: black;")
        layout.addWidget(self.incognito_checkbox)

        # Auto-save checkbox
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_checkbox.setChecked(True)
        self.auto_save_checkbox.stateChanged.connect(self.on_auto_save_toggled)
        layout.addWidget(self.auto_save_checkbox)

        # Auto-save interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Auto-save interval (seconds):")
        interval_label.setStyleSheet("color: black;")
        interval_layout.addWidget(interval_label)

        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(60)
        self.interval_spin.setValue(3)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()

        layout.addLayout(interval_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("QPushButton { color: black; }")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        create_button = QPushButton("Create")
        create_button.setStyleSheet("QPushButton { color: black; }")
        create_button.setDefault(True)
        create_button.clicked.connect(self.on_create)
        button_layout.addWidget(create_button)

        layout.addLayout(button_layout)

    def on_auto_save_toggled(self, state):
        """Handle auto-save checkbox toggle."""
        enabled = (state == Qt.CheckState.Checked.value)
        self.interval_spin.setEnabled(enabled)

    def on_create(self):
        """Handle create button click."""
        session_name = self.name_input.text().strip()

        # Validate session name
        if not session_name:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a session name"
            )
            return

        # Validate characters
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        if not all(c in allowed_chars for c in session_name):
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Session name can only contain letters, numbers, dashes, and underscores"
            )
            return

        self.session_name = session_name
        self.auto_save_enabled = self.auto_save_checkbox.isChecked()
        self.auto_save_interval = self.interval_spin.value()
        self.browser_type = self.browser_combo.currentText().lower()
        self.incognito_mode = self.incognito_checkbox.isChecked()

        self.accept()

    def get_session_name(self):
        """Get the entered session name."""
        return self.session_name

    def get_auto_save_enabled(self):
        """Get auto-save enabled status."""
        return self.auto_save_enabled

    def get_auto_save_interval(self):
        """Get auto-save interval."""
        return float(self.auto_save_interval)

    def get_browser_type(self):
        """Get selected browser type."""
        return self.browser_type

    def get_incognito_mode(self):
        """Get incognito mode status."""
        return self.incognito_mode
