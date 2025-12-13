#!/usr/bin/env python3
"""
Browser Tab Session Manager - Desktop GUI
Main entry point for the desktop application.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Add parent directory to path to import tab_session_manager
sys.path.insert(0, str(Path(__file__).parent.parent))

from main_window import MainWindow


def main():
    """Main entry point for the desktop application."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application instance
    app = QApplication(sys.argv)
    app.setApplicationName("Browser Session Manager")
    app.setOrganizationName("BrowserAutomation")
    app.setApplicationVersion("1.0.0")

    # Set application style (use Fusion for consistent cross-platform look)
    app.setStyle('Fusion')

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
