"""
Session card widget - displays a single session as a visual card.
"""

from datetime import datetime
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QFont


class SessionCard(QFrame):
    """Visual card widget for displaying a session."""

    # Signals
    double_clicked = pyqtSignal(str)  # session_name
    load_requested = pyqtSignal(str)  # session_name
    details_requested = pyqtSignal(str)  # session_name
    scrape_requested = pyqtSignal(str)  # session_name
    delete_requested = pyqtSignal(str)  # session_name

    def __init__(self, session_data, parent=None):
        super().__init__(parent)
        self.session_data = session_data
        self.session_name = session_data['name']

        self.init_ui()
        self.setup_style()

    def init_ui(self):
        """Initialize the UI components."""
        self.setFrameShape(QFrame.Shape.Box)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setLineWidth(1)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMaximumWidth(280)
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Session name (title)
        name_label = QLabel(self.session_name)
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)
        name_label.setObjectName("sessionName")
        name_label.setStyleSheet("color: #000000; font-weight: 700;")
        layout.addWidget(name_label)

        # Created date
        created_at = self.session_data.get('created_at', 'Unknown')
        try:
            # Parse and format the date
            dt = datetime.fromisoformat(created_at)
            date_str = dt.strftime('%b %d, %Y')
        except:
            date_str = created_at

        date_label = QLabel(date_str)
        date_label.setObjectName("dateLabel")
        date_label.setStyleSheet("color: #444444; font-size: 9pt; font-weight: 600;")
        layout.addWidget(date_label)

        layout.addStretch()

        # Tab and group count
        info_layout = QHBoxLayout()
        info_layout.setSpacing(12)

        tab_count = self.session_data.get('tab_count', 0)
        tab_label = QLabel(f"📑 {tab_count} tabs")
        tab_label.setObjectName("tabLabel")
        tab_label.setStyleSheet("color: #2c3e50; font-size: 9pt; font-weight: 600;")
        info_layout.addWidget(tab_label)

        group_count = self.session_data.get('group_count', 0)
        if group_count > 0:
            group_label = QLabel(f"📁 {group_count} groups")
            group_label.setObjectName("groupLabel")
            group_label.setStyleSheet("color: #2c3e50; font-size: 9pt; font-weight: 600;")
            info_layout.addWidget(group_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)

    def setup_style(self):
        """Setup the widget styling with high contrast."""
        self.setStyleSheet("""
            SessionCard {
                background-color: #ffffff;
                border: 2px solid #d0d7de;
                border-radius: 10px;
            }
            SessionCard:hover {
                background-color: #e6f2ff;
                border: 3px solid #0969da;
                border-radius: 10px;
            }
            SessionCard QLabel#sessionName {
                color: #000000;
            }
            SessionCard:hover QLabel#sessionName {
                color: #0550ae;
            }
            SessionCard QLabel#dateLabel {
                color: #444444;
            }
            SessionCard:hover QLabel#dateLabel {
                color: #0969da;
            }
            SessionCard QLabel#tabLabel, SessionCard QLabel#groupLabel {
                color: #1f2937;
            }
            SessionCard:hover QLabel#tabLabel, SessionCard:hover QLabel#groupLabel {
                color: #0550ae;
            }
        """)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.session_name)
            self.load_requested.emit(self.session_name)

    def contextMenuEvent(self, event):
        """Handle right-click context menu with high contrast styling."""
        menu = QMenu(self)

        # Apply high contrast stylesheet to context menu
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 2px solid #0969da;
                border-radius: 8px;
                padding: 6px;
                font-size: 10pt;
                font-weight: 600;
            }
            QMenu::item {
                background-color: transparent;
                color: #000000;
                padding: 8px 24px;
                margin: 2px 4px;
                border-radius: 6px;
                font-weight: 600;
            }
            QMenu::item:selected {
                background-color: #0969da;
                color: #ffffff;
            }
            QMenu::item:hover {
                background-color: #0969da;
                color: #ffffff;
            }
            QMenu::separator {
                height: 2px;
                background-color: #d0d7de;
                margin: 6px 8px;
            }
        """)

        load_action = menu.addAction("🚀 Load Session")
        load_action.triggered.connect(lambda: self.load_requested.emit(self.session_name))

        details_action = menu.addAction("🔍 View Details")
        details_action.triggered.connect(lambda: self.details_requested.emit(self.session_name))

        scrape_action = menu.addAction("📊 Scrape All Tabs")
        scrape_action.triggered.connect(lambda: self.scrape_requested.emit(self.session_name))

        menu.addSeparator()

        delete_action = menu.addAction("🗑️ Delete Session")
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.session_name))

        menu.exec(event.globalPos())
