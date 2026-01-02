"""
Main window for Browser Session Manager desktop application.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolBar, QStatusBar, QMenuBar, QMessageBox, QLabel, QTabWidget
)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, QSettings, QTimer

from widgets.session_list import SessionListWidget
from widgets.search_bar import SearchBar
from widgets.status_bar import BrowserStatusBar
from widgets.workflows_widget import WorkflowsWidget
from dialogs.new_session import NewSessionDialog
from dialogs.confirm_delete import ConfirmDeleteDialog
from dialogs.about_dialog import AboutDialog
from utils.session_manager_wrapper import SessionManagerWrapper


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.session_manager = SessionManagerWrapper()

        self.init_ui()
        self.restore_geometry_from_settings()
        self.refresh_sessions()

        # Start browser status polling
        self.start_browser_status_polling()

        # Start auto-refresh timer for live sync with browser tabs
        self.start_session_refresh_timer()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Browser Automation Manager")
        self.setMinimumSize(1200, 700)

        # Create central widget with modern styling
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        self.setCentralWidget(central_widget)

        # Create main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #d0d0d0;
                background: #f5f5f5;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #e8e8e8;
                color: #333333;
                padding: 12px 24px;
                margin: 2px;
                margin-bottom: -2px;
                border: 2px solid #d0d0d0;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background: #f5f5f5;
                color: #000000;
                font-weight: bold;
                border-bottom: 2px solid #f5f5f5;
            }
            QTabBar::tab:hover:!selected {
                background: #d8d8d8;
            }
        """)
        layout.addWidget(self.tab_widget)

        # Create Sessions tab
        sessions_tab = QWidget()
        sessions_layout = QVBoxLayout(sessions_tab)
        sessions_layout.setContentsMargins(0, 0, 0, 0)
        sessions_layout.setSpacing(0)

        # Create search bar for sessions tab
        self.search_bar = SearchBar()
        self.search_bar.search_changed.connect(self.on_search_changed)
        self.search_bar.sort_changed.connect(self.on_sort_changed)
        sessions_layout.addWidget(self.search_bar)

        # Create session list widget
        self.session_list = SessionListWidget(self.session_manager)
        self.session_list.session_loaded.connect(self.on_session_loaded)
        self.session_list.session_deleted.connect(self.on_session_deleted)
        sessions_layout.addWidget(self.session_list)

        # Add sessions tab
        self.tab_widget.addTab(sessions_tab, "Sessions")

        # Create Workflows tab
        self.workflows_widget = WorkflowsWidget()
        self.tab_widget.addTab(self.workflows_widget, "Workflows")

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Create custom status bar
        self.browser_status_bar = BrowserStatusBar(self.session_manager)
        self.setStatusBar(self.browser_status_bar)

    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Session", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.new_session)
        file_menu.addAction(new_action)

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence("Ctrl+R"))
        refresh_action.triggered.connect(self.refresh_sessions)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        search_action = QAction("&Search", self)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(self.focus_search)
        edit_menu.addAction(search_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        sort_name_action = QAction("Sort by &Name", self)
        sort_name_action.triggered.connect(lambda: self.search_bar.set_sort_mode("name"))
        view_menu.addAction(sort_name_action)

        sort_date_action = QAction("Sort by &Date", self)
        sort_date_action.triggered.connect(lambda: self.search_bar.set_sort_mode("date"))
        view_menu.addAction(sort_date_action)

        sort_tabs_action = QAction("Sort by &Tab Count", self)
        sort_tabs_action.triggered.connect(lambda: self.search_bar.set_sort_mode("tabs"))
        view_menu.addAction(sort_tabs_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New session action
        new_action = QAction("New Session", self)
        new_action.triggered.connect(self.new_session)
        toolbar.addAction(new_action)

        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_sessions)
        toolbar.addAction(refresh_action)

    def new_session(self):
        """Show dialog to create a new session."""
        dialog = NewSessionDialog(self)
        if dialog.exec():
            session_name = dialog.get_session_name()
            auto_save = dialog.get_auto_save_enabled()
            interval = dialog.get_auto_save_interval()
            browser_type = dialog.get_browser_type()
            incognito_mode = dialog.get_incognito_mode()
            profile_name = dialog.get_profile_name()

            print(f"[MainWindow] Session name: {session_name}")
            print(f"[MainWindow] Browser: {browser_type}, Incognito: {incognito_mode}")
            print(f"[MainWindow] Profile: {profile_name if profile_name else 'None'}")
            print(f"[MainWindow] Auto-save: {auto_save}, Interval: {interval}")

            # Create new session via session manager
            success = self.session_manager.create_new_session(
                session_name, auto_save, interval, browser_type, incognito_mode, profile_name
            )

            print(f"[MainWindow] Create result: {success}")

            if success:
                self.statusBar().showMessage(f"Created new session: {session_name}", 3000)
                self.refresh_sessions()
            else:
                QMessageBox.warning(
                    self, "Error",
                    f"Failed to create session '{session_name}'"
                )

    def refresh_sessions(self):
        """Reload and display all sessions."""
        sessions = self.session_manager.get_sessions()
        self.session_list.load_sessions(sessions)
        self.apply_current_filter()

    def focus_search(self):
        """Focus the search bar."""
        self.search_bar.focus_search()

    def on_search_changed(self, search_text):
        """Handle search text changes."""
        self.apply_current_filter()

    def on_sort_changed(self, sort_mode):
        """Handle sort mode changes."""
        self.apply_current_filter()

    def apply_current_filter(self):
        """Apply current search and sort settings."""
        search_text = self.search_bar.get_search_text()
        sort_mode = self.search_bar.get_sort_mode()
        self.session_list.filter_and_sort(search_text, sort_mode)

    def on_session_loaded(self, session_name):
        """Handle session loaded event."""
        self.statusBar().showMessage(f"Loaded session: {session_name}", 3000)

    def on_session_deleted(self, session_name):
        """Handle session deleted event."""
        self.statusBar().showMessage(f"Deleted session: {session_name}", 3000)
        self.refresh_sessions()

    def start_browser_status_polling(self):
        """Start polling browser status."""
        self.browser_status_bar.start_polling()

    def start_session_refresh_timer(self):
        """Start timer to auto-refresh sessions for live sync with browser."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh_sessions)
        # Refresh every 5 seconds to show new tabs
        self.refresh_timer.start(5000)  # 5000 ms = 5 seconds

    def auto_refresh_sessions(self):
        """Auto-refresh sessions if browser is running (for live sync)."""
        # Only refresh if browser is running (to avoid unnecessary file reads)
        if self.session_manager.check_browser_status():
            self.refresh_sessions()

    def show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """Handle window close event."""
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        # Stop browser status polling
        self.browser_status_bar.stop_polling()

        # Stop session refresh timer
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()

        # Accept the close event
        event.accept()

    def restore_geometry_from_settings(self):
        """Restore window geometry from settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)
