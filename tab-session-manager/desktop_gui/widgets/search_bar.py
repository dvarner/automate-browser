"""
Search bar widget - for searching and filtering sessions.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox, QLabel
from PyQt6.QtCore import pyqtSignal


class SearchBar(QWidget):
    """Widget for searching and sorting sessions."""

    # Signals
    search_changed = pyqtSignal(str)  # search_text
    sort_changed = pyqtSignal(str)    # sort_mode

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)

        # Search input
        search_label = QLabel("Search:")
        layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search sessions...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("QLineEdit { color: black; }")
        layout.addWidget(self.search_input, stretch=1)

        # Sort dropdown
        sort_label = QLabel("Sort by:")
        layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Date", "Tab Count"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        layout.addWidget(self.sort_combo)

    def on_search_text_changed(self, text):
        """Handle search text change."""
        self.search_changed.emit(text)

    def on_sort_changed(self, text):
        """Handle sort mode change."""
        # Convert display text to internal sort mode
        mode_map = {
            "Name": "name",
            "Date": "date",
            "Tab Count": "tabs"
        }
        mode = mode_map.get(text, "name")
        self.sort_changed.emit(mode)

    def get_search_text(self):
        """Get current search text."""
        return self.search_input.text()

    def get_sort_mode(self):
        """Get current sort mode."""
        text = self.sort_combo.currentText()
        mode_map = {
            "Name": "name",
            "Date": "date",
            "Tab Count": "tabs"
        }
        return mode_map.get(text, "name")

    def set_sort_mode(self, mode):
        """Set sort mode programmatically."""
        text_map = {
            "name": "Name",
            "date": "Date",
            "tabs": "Tab Count"
        }
        text = text_map.get(mode, "Name")
        self.sort_combo.setCurrentText(text)

    def focus_search(self):
        """Focus the search input."""
        self.search_input.setFocus()
        self.search_input.selectAll()
