"""
New session dialog - prompts user to create a new browser session.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QSpinBox, QPushButton, QMessageBox, QComboBox,
    QListWidget, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from pathlib import Path


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
        self.disable_web_security = False
        self.profile_name = ""
        self.extensions = []

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        # Set dialog palette for reliable colors
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#e8e8e8"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#000000"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Session name input
        name_label = QLabel("Session Name:")
        name_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 11pt;")
        layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., my-work-session")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #bdbdbd;
                padding: 8px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        layout.addWidget(self.name_input)

        # Validation hint
        hint_label = QLabel("Only letters, numbers, dashes, and underscores allowed")
        hint_label.setStyleSheet("color: #616161; font-size: 9pt; font-style: italic;")
        layout.addWidget(hint_label)

        # Browser selection
        browser_layout = QHBoxLayout()
        browser_label = QLabel("Browser:")
        browser_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 11pt;")
        browser_layout.addWidget(browser_label)

        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Chrome", "Brave", "Firefox", "Chromium"])
        self.browser_combo.setCurrentText("Chrome")
        self.browser_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #bdbdbd;
                padding: 6px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QComboBox:hover {
                border: 2px solid #1976D2;
            }
        """)
        browser_layout.addWidget(self.browser_combo)
        browser_layout.addStretch()

        layout.addLayout(browser_layout)

        # Incognito mode checkbox
        self.incognito_checkbox = QCheckBox("Launch in Incognito/Private mode")
        self.incognito_checkbox.setChecked(False)
        self.incognito_checkbox.setStyleSheet("color: #000000; font-size: 10pt; font-weight: bold;")
        layout.addWidget(self.incognito_checkbox)

        # Disable web security checkbox (for automation/data gathering)
        self.web_security_checkbox = QCheckBox("Disable Web Security (for automation)")
        self.web_security_checkbox.setChecked(False)
        self.web_security_checkbox.setStyleSheet("color: #000000; font-size: 10pt; font-weight: bold;")
        layout.addWidget(self.web_security_checkbox)

        # Explanation for web security option
        web_security_hint = QLabel(
            "Enable when gathering data across sites. Allows cross-origin requests.\n"
            "Leave OFF for normal browsing (some sites won't load with this enabled)."
        )
        web_security_hint.setStyleSheet("color: #616161; font-size: 9pt; font-style: italic;")
        layout.addWidget(web_security_hint)

        # Profile name input
        profile_layout = QVBoxLayout()

        profile_label = QLabel("Profile Name (optional):")
        profile_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 11pt;")
        profile_layout.addWidget(profile_label)

        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("e.g., work, personal, dev (leave blank for no profile)")
        self.profile_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #bdbdbd;
                padding: 8px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #1976D2;
            }
        """)
        profile_layout.addWidget(self.profile_input)

        # Hint about profiles
        profile_hint = QLabel("Profile stores cookies, history, and settings. Leave blank for ephemeral session.")
        profile_hint.setStyleSheet("color: #616161; font-size: 9pt; font-style: italic;")
        profile_layout.addWidget(profile_hint)

        layout.addLayout(profile_layout)

        # Extensions section
        ext_layout = QVBoxLayout()

        ext_label = QLabel("Extensions (Chromium only):")
        ext_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 11pt;")
        ext_layout.addWidget(ext_label)

        self.extension_list = QListWidget()
        self.extension_list.setMaximumHeight(80)
        self.extension_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #bdbdbd;
                border-radius: 4px;
                font-size: 9pt;
            }
            QListWidget::item {
                color: #000000;
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #1976D2;
                color: #ffffff;
            }
        """)
        ext_layout.addWidget(self.extension_list)

        ext_buttons_layout = QHBoxLayout()

        add_ext_button = QPushButton("Add Extension...")
        add_ext_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: #ffffff;
                border: 2px solid #1565C0;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
        """)
        add_ext_button.clicked.connect(self.on_add_extension)
        ext_buttons_layout.addWidget(add_ext_button)

        remove_ext_button = QPushButton("Remove Selected")
        remove_ext_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: #ffffff;
                border: 2px solid #616161;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #9E9E9E;
            }
        """)
        remove_ext_button.clicked.connect(self.on_remove_extension)
        ext_buttons_layout.addWidget(remove_ext_button)

        ext_buttons_layout.addStretch()
        ext_layout.addLayout(ext_buttons_layout)

        # Extension hint
        ext_hint = QLabel("Select unpacked extension directories containing manifest.json")
        ext_hint.setStyleSheet("color: #616161; font-size: 9pt; font-style: italic;")
        ext_layout.addWidget(ext_hint)

        layout.addLayout(ext_layout)

        # Auto-save checkbox
        self.auto_save_checkbox = QCheckBox("Enable auto-save")
        self.auto_save_checkbox.setChecked(True)
        self.auto_save_checkbox.setStyleSheet("color: #000000; font-size: 10pt; font-weight: bold;")
        self.auto_save_checkbox.stateChanged.connect(self.on_auto_save_toggled)
        layout.addWidget(self.auto_save_checkbox)

        # Auto-save interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Auto-save interval (seconds):")
        interval_label.setStyleSheet("color: #000000; font-size: 10pt;")
        interval_layout.addWidget(interval_label)

        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(60)
        self.interval_spin.setValue(3)
        self.interval_spin.setStyleSheet("""
            QSpinBox {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #bdbdbd;
                padding: 6px;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()

        layout.addLayout(interval_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: #ffffff;
                border: 2px solid #424242;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #9E9E9E;
                border: 2px solid #616161;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        create_button = QPushButton("Create")
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: #ffffff;
                border: 2px solid #1B5E20;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #388E3C;
                border: 2px solid #2E7D32;
            }
        """)
        create_button.setDefault(True)
        create_button.clicked.connect(self.on_create)
        button_layout.addWidget(create_button)

        layout.addLayout(button_layout)

    def on_auto_save_toggled(self, state):
        """Handle auto-save checkbox toggle."""
        enabled = (state == Qt.CheckState.Checked.value)
        self.interval_spin.setEnabled(enabled)

    def on_add_extension(self):
        """Handle add extension button click."""
        ext_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Extension Directory",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if ext_dir:
            ext_path = Path(ext_dir)

            # Check for manifest.json
            manifest_file = ext_path / 'manifest.json'
            if not manifest_file.exists():
                QMessageBox.warning(
                    self,
                    "Invalid Extension",
                    f"No manifest.json found in:\n{ext_dir}\n\nPlease select an unpacked extension directory."
                )
                return

            # Check if already added
            if ext_dir in self.extensions:
                QMessageBox.information(
                    self,
                    "Already Added",
                    "This extension has already been added."
                )
                return

            self.extensions.append(ext_dir)
            self.extension_list.addItem(ext_path.name)

    def on_remove_extension(self):
        """Handle remove extension button click."""
        current_row = self.extension_list.currentRow()
        if current_row >= 0:
            self.extension_list.takeItem(current_row)
            del self.extensions[current_row]

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
        self.disable_web_security = self.web_security_checkbox.isChecked()

        # Validate profile name if provided
        self.profile_name = self.profile_input.text().strip()
        if self.profile_name:
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', self.profile_name):
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Profile name can only contain letters, numbers, dashes, and underscores"
                )
                return

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

    def get_disable_web_security(self):
        """Get disable web security status."""
        return self.disable_web_security

    def get_profile_name(self):
        """Get the entered profile name."""
        return self.profile_name

    def get_extensions(self):
        """Get the list of extension paths."""
        return self.extensions if self.extensions else None
