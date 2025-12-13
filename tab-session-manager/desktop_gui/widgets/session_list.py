"""
Session list widget - displays all sessions as a scrollable grid of cards.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGridLayout,
    QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from widgets.session_card import SessionCard
from dialogs.confirm_delete import ConfirmDeleteDialog
from dialogs.detail_dialog import SessionDetailDialog


class SessionListWidget(QWidget):
    """Widget for displaying a scrollable list/grid of session cards."""

    # Signals
    session_loaded = pyqtSignal(str)  # session_name
    session_deleted = pyqtSignal(str)  # session_name

    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.sessions = []
        self.session_cards = []

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create container for cards
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setContentsMargins(12, 12, 12, 12)

        # Empty state label (shown when no sessions)
        self.empty_label = QLabel("No sessions found\n\nClick 'New Session' to create one")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #1f2937;
                font-size: 15pt;
                font-weight: 600;
                padding: 50px;
                background-color: rgba(255, 255, 255, 0.7);
                border: 2px dashed #d0d7de;
                border-radius: 12px;
            }
        """)
        self.empty_label.setVisible(False)
        self.cards_layout.addWidget(self.empty_label, 0, 0)

        # Style the scroll area
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #e6f2ff;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #0969da;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #0550ae;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        scroll_area.setWidget(self.cards_container)
        layout.addWidget(scroll_area)

    def load_sessions(self, sessions):
        """Load and display sessions.

        Args:
            sessions: List of session dicts
        """
        self.sessions = sessions
        self.render_cards()

    def render_cards(self):
        """Render session cards in the grid."""
        # Clear existing cards
        for card in self.session_cards:
            card.deleteLater()
        self.session_cards.clear()

        # Show empty state if no sessions
        if not self.sessions:
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)

        # Create cards
        columns = 4  # Number of columns in grid
        for i, session in enumerate(self.sessions):
            card = SessionCard(session)

            # Connect signals
            card.load_requested.connect(self.on_load_session)
            card.details_requested.connect(self.on_show_details)
            card.delete_requested.connect(self.on_delete_session)

            # Add to grid
            row = i // columns
            col = i % columns
            self.cards_layout.addWidget(card, row, col)

            self.session_cards.append(card)

    def on_load_session(self, session_name):
        """Handle load session request."""
        reply = QMessageBox.question(
            self,
            "Load Session",
            f"Load session '{session_name}'?\n\nThis will open a browser with all tabs from this session.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.session_manager.load_session(session_name)
            if success:
                self.session_loaded.emit(session_name)
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to load session '{session_name}'"
                )

    def on_show_details(self, session_name):
        """Handle show details request."""
        details = self.session_manager.get_session_details(session_name)

        if details:
            dialog = SessionDetailDialog(session_name, details, self.session_manager, self)
            dialog.exec()
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not load details for session '{session_name}'"
            )

    def on_delete_session(self, session_name):
        """Handle delete session request."""
        dialog = ConfirmDeleteDialog(session_name, self)

        if dialog.exec():
            success = self.session_manager.delete_session(session_name)
            if success:
                self.session_deleted.emit(session_name)
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete session '{session_name}'"
                )

    def filter_and_sort(self, search_text, sort_mode):
        """Filter and sort sessions.

        Args:
            search_text: Text to search for in session names
            sort_mode: Sort mode ('name', 'date', 'tabs')
        """
        # Filter sessions
        if search_text:
            filtered = [
                s for s in self.sessions
                if search_text.lower() in s['name'].lower()
            ]
        else:
            filtered = self.sessions.copy()

        # Sort sessions
        if sort_mode == 'name':
            filtered.sort(key=lambda s: s['name'].lower())
        elif sort_mode == 'date':
            filtered.sort(key=lambda s: s.get('created_at', ''), reverse=True)
        elif sort_mode == 'tabs':
            filtered.sort(key=lambda s: s.get('tab_count', 0), reverse=True)

        # Clear and render filtered sessions
        for card in self.session_cards:
            card.deleteLater()
        self.session_cards.clear()

        # Show empty state if no results
        if not filtered:
            self.empty_label.setText("No sessions match your search")
            self.empty_label.setVisible(True)
            return

        self.empty_label.setVisible(False)

        # Create cards for filtered sessions
        columns = 4
        for i, session in enumerate(filtered):
            card = SessionCard(session)

            # Connect signals
            card.load_requested.connect(self.on_load_session)
            card.details_requested.connect(self.on_show_details)
            card.delete_requested.connect(self.on_delete_session)

            # Add to grid
            row = i // columns
            col = i % columns
            self.cards_layout.addWidget(card, row, col)

            self.session_cards.append(card)
