#!/usr/bin/env python3
"""
Browser Tab Session Manager - Desktop GUI
Main entry point for the desktop application.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPalette, QColor
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

    # Force light theme palette for entire application
    light_palette = QPalette()
    light_palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    light_palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    light_palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    light_palette.setColor(QPalette.ColorRole.Highlight, QColor(25, 118, 210))
    light_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(light_palette)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
