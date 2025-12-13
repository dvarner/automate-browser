"""
Session detail dialog - shows all tabs and groups in a session.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt


class SessionDetailDialog(QDialog):
    """Dialog for displaying session details."""

    def __init__(self, session_name, details, session_manager, parent=None):
        super().__init__(parent)
        self.session_name = session_name
        self.details = details
        self.session_manager = session_manager

        self.setWindowTitle(f"Session Details - {session_name}")
        self.setModal(True)
        self.setMinimumSize(700, 500)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Session info header
        info_text = f"Session: {self.session_name}\n"
        info_text += f"Created: {self.details.get('created_at', 'Unknown')}"

        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: black;")
        layout.addWidget(info_label)

        # Tree widget for groups and tabs
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Title", "URL"])
        self.tree.setColumnWidth(0, 300)
        self.tree.setStyleSheet("QTreeWidget { color: black; } QTreeWidget::item { color: black; }")
        layout.addWidget(self.tree)

        # Populate tree
        self.populate_tree()

        # Buttons
        button_layout = QHBoxLayout()

        load_all_button = QPushButton("Load Entire Session")
        load_all_button.setStyleSheet("QPushButton { color: black; }")
        load_all_button.clicked.connect(self.on_load_all)
        button_layout.addWidget(load_all_button)

        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.setStyleSheet("QPushButton { color: black; }")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def populate_tree(self):
        """Populate the tree widget with groups and tabs."""
        # Add grouped tabs
        for group in self.details.get('groups', []):
            group_name = group.get('name', 'Unnamed')
            group_item = QTreeWidgetItem(self.tree, [f"📁 {group_name}", ""])
            group_item.setExpanded(True)

            # Add tabs in this group
            for tab in group.get('tabs', []):
                title = tab.get('title', 'Untitled')
                url = tab.get('url', '')
                tab_item = QTreeWidgetItem(group_item, [f"  📄 {title}", url])

        # Add ungrouped tabs
        ungrouped = self.details.get('ungrouped_tabs', [])
        if ungrouped:
            ungrouped_item = QTreeWidgetItem(self.tree, ["📑 Ungrouped Tabs", ""])
            ungrouped_item.setExpanded(True)

            for tab in ungrouped:
                title = tab.get('title', 'Untitled')
                url = tab.get('url', '')
                tab_item = QTreeWidgetItem(ungrouped_item, [f"  📄 {title}", url])

    def on_load_all(self):
        """Handle load entire session."""
        reply = QMessageBox.question(
            self,
            "Load Session",
            f"Load session '{self.session_name}'?\n\nThis will open a browser with all tabs from this session.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.session_manager.load_session(self.session_name)
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Session '{self.session_name}' loaded successfully!"
                )
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to load session '{self.session_name}'"
                )
