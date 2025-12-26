"""
Multi-tab scraping dialog for applying templates to all tabs in a session.
"""

import json
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QRadioButton, QButtonGroup, QLineEdit,
    QProgressBar, QTextEdit, QGroupBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor


class ScrapeWorker(QThread):
    """Background thread for scraping tabs."""

    progress = pyqtSignal(int, int, str)  # current, total, url
    finished = pyqtSignal(dict)  # results
    error = pyqtSignal(str)  # error_message

    def __init__(self, session_data, template_path, filter_type, group_pattern):
        super().__init__()
        self.session_data = session_data
        self.template_path = template_path
        self.filter_type = filter_type
        self.group_pattern = group_pattern

    def run(self):
        """Run scraping in background thread."""
        try:
            # Add utils to path
            utils_path = Path(__file__).parent.parent.parent.parent / 'workflow-engine' / 'utils'
            if str(utils_path) not in sys.path:
                sys.path.insert(0, str(utils_path))

            from multi_tab_scraper import MultiTabScraper, TabGroupFilter
            from playwright.sync_api import sync_playwright

            # Create filter
            group_filter = None
            if self.filter_type != 'all':
                group_filter = TabGroupFilter(self.filter_type, self.group_pattern)

            # Create scraper
            scraper = MultiTabScraper(self.template_path, group_filter, continue_on_error=True)

            # Launch browser and load session
            with sync_playwright() as p:
                browser_type = self.session_data.get('browser_type', 'chromium')
                incognito = self.session_data.get('incognito_mode', False)
                profile_name = self.session_data.get('profile_name')

                # Launch browser
                if browser_type == 'firefox':
                    browser_launcher = p.firefox
                elif browser_type == 'webkit':
                    browser_launcher = p.webkit
                else:
                    browser_launcher = p.chromium

                # Use persistent context if profile specified
                if profile_name and not incognito:
                    profiles_dir = Path(__file__).parent.parent.parent / 'profiles'
                    profile_path = profiles_dir / profile_name
                    context = browser_launcher.launch_persistent_context(
                        str(profile_path),
                        headless=False,
                        no_viewport=True
                    )
                else:
                    browser = browser_launcher.launch(headless=False)
                    context = browser.new_context(no_viewport=True)

                # Load tabs from session
                for group in self.session_data.get('groups', []):
                    for tab in group.get('tabs', []):
                        page = context.new_page()
                        try:
                            page.goto(tab['url'], timeout=10000)
                        except:
                            pass

                # Scrape all pages
                results = scraper.scrape_pages(
                    context.pages,
                    progress_callback=lambda c, t, u: self.progress.emit(c, t, u)
                )

                self.finished.emit(results)

                # Close browser
                context.close()
                if not profile_name or incognito:
                    browser.close()

        except Exception as e:
            self.error.emit(str(e))


class ScrapeAllTabsDialog(QDialog):
    """Dialog for configuring and running multi-tab scraping."""

    def __init__(self, session_name, session_details, session_manager, parent=None):
        super().__init__(parent)
        self.session_name = session_name
        self.session_details = session_details
        self.session_manager = session_manager
        self.results = None
        self.worker = None

        self.setWindowTitle(f"Scrape All Tabs - {session_name}")
        self.setModal(True)
        self.setMinimumSize(650, 600)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        # Set dialog palette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Session info
        info_label = QLabel(f"📊 Session: {self.session_name}")
        info_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 13pt;
                color: #000000;
                padding: 8px;
            }
        """)
        layout.addWidget(info_label)

        # Template selection
        template_group = QGroupBox("Template")
        template_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #000000;
                border: 2px solid #d0d7de;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        template_layout = QVBoxLayout()
        self.template_combo = QComboBox()
        self.template_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #d0d7de;
                border-radius: 4px;
                background-color: #ffffff;
                color: #000000;
                font-size: 11pt;
            }
            QComboBox:hover {
                border-color: #0969da;
            }
        """)
        self._load_templates()
        template_layout.addWidget(self.template_combo)
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        # Tab group filter
        filter_group = QGroupBox("Tab Group Filter")
        filter_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #000000;
                border: 2px solid #d0d7de;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        filter_layout = QVBoxLayout()

        self.filter_button_group = QButtonGroup()
        self.filter_all_radio = QRadioButton("All tabs (including grouped)")
        self.filter_all_radio.setChecked(True)
        self.filter_ungrouped_radio = QRadioButton("Only ungrouped tabs")
        self.filter_grouped_radio = QRadioButton("Only grouped tabs")
        self.filter_regex_radio = QRadioButton("Regex match group name:")

        # Style radio buttons
        radio_style = """
            QRadioButton {
                color: #000000;
                font-size: 11pt;
                padding: 4px;
            }
        """
        self.filter_all_radio.setStyleSheet(radio_style)
        self.filter_ungrouped_radio.setStyleSheet(radio_style)
        self.filter_grouped_radio.setStyleSheet(radio_style)
        self.filter_regex_radio.setStyleSheet(radio_style)

        filter_layout.addWidget(self.filter_all_radio)
        filter_layout.addWidget(self.filter_ungrouped_radio)
        filter_layout.addWidget(self.filter_grouped_radio)
        filter_layout.addWidget(self.filter_regex_radio)

        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("e.g., Shop.* or Work|Dev")
        self.regex_input.setEnabled(False)
        self.regex_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 2px solid #d0d7de;
                border-radius: 4px;
                background-color: #ffffff;
                color: #000000;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #0969da;
            }
            QLineEdit:disabled {
                background-color: #f5f5f5;
                color: #999999;
            }
        """)
        filter_layout.addWidget(self.regex_input)

        self.filter_regex_radio.toggled.connect(
            lambda checked: self.regex_input.setEnabled(checked)
        )

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Progress section
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #000000; font-size: 10pt;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #d0d7de;
                border-radius: 4px;
                background-color: #f5f5f5;
                text-align: center;
                color: #000000;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0969da;
                border-radius: 2px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results preview
        results_label = QLabel("Results:")
        results_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 11pt;")
        results_label.setVisible(False)
        self.results_label = results_label
        layout.addWidget(results_label)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #d0d7de;
                border-radius: 4px;
                background-color: #f9f9f9;
                color: #000000;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                padding: 8px;
            }
        """)
        self.results_text.setVisible(False)
        layout.addWidget(self.results_text)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("🚀 Start Scraping")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #0969da;
                color: #ffffff;
                font-weight: bold;
                font-size: 12pt;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0550ae;
            }
            QPushButton:disabled {
                background-color: #d0d7de;
                color: #999999;
            }
        """)
        self.start_button.clicked.connect(self.start_scraping)
        button_layout.addWidget(self.start_button)

        self.export_button = QPushButton("💾 Export Results")
        self.export_button.setEnabled(False)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #2da44e;
                color: #ffffff;
                font-weight: bold;
                font-size: 12pt;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #d0d7de;
                color: #999999;
            }
        """)
        self.export_button.clicked.connect(self.export_results)
        button_layout.addWidget(self.export_button)

        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e8e8e8;
                color: #000000;
                font-weight: bold;
                font-size: 12pt;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _load_templates(self):
        """Load available templates from workflow-engine/templates/"""
        templates_dir = Path(__file__).parent.parent.parent.parent / 'workflow-engine' / 'templates'

        if templates_dir.exists():
            for template_file in templates_dir.glob('*.json'):
                self.template_combo.addItem(template_file.name, str(template_file))

        if self.template_combo.count() == 0:
            self.template_combo.addItem("No templates found", None)
            self.start_button.setEnabled(False)

    def start_scraping(self):
        """Start scraping in background thread."""
        # Get selected template
        template_path = self.template_combo.currentData()
        if not template_path:
            QMessageBox.warning(self, "No Template", "Please select a template first")
            return

        # Get filter settings
        if self.filter_all_radio.isChecked():
            filter_type = 'all'
            group_pattern = None
        elif self.filter_ungrouped_radio.isChecked():
            filter_type = 'ungrouped'
            group_pattern = None
        elif self.filter_grouped_radio.isChecked():
            filter_type = 'grouped'
            group_pattern = None
        else:  # regex
            filter_type = 'regex'
            group_pattern = self.regex_input.text().strip()
            if not group_pattern:
                QMessageBox.warning(self, "Invalid Pattern", "Please enter a regex pattern")
                return

        # Disable controls
        self.start_button.setEnabled(False)
        self.template_combo.setEnabled(False)
        self.filter_all_radio.setEnabled(False)
        self.filter_ungrouped_radio.setEnabled(False)
        self.filter_grouped_radio.setEnabled(False)
        self.filter_regex_radio.setEnabled(False)
        self.regex_input.setEnabled(False)

        # Show progress
        self.progress_label.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create and start worker
        self.worker = ScrapeWorker(
            self.session_details,
            Path(template_path),
            filter_type,
            group_pattern
        )
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, current, total, url):
        """Update progress UI."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Scraping {current}/{total}: {url[:60]}...")

    def on_finished(self, results):
        """Display results and enable export."""
        self.results = results

        # Hide progress
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)

        # Show results
        self.results_label.setVisible(True)
        self.results_text.setVisible(True)

        # Format results summary
        summary = f"Total Tabs: {results['total_tabs']}\n"
        summary += f"Successful: {results['successful']}\n"
        summary += f"Failed: {results['failed']}\n\n"

        total_items = sum(len(r['items']) for r in results['results'] if r['status'] == 'success')
        summary += f"Total Items Extracted: {total_items}\n\n"

        summary += "=" * 60 + "\n\n"

        # Show per-tab details
        for result in results['results']:
            summary += f"[{result['tab_index'] + 1}] {result['tab_title'][:50]}\n"
            summary += f"    URL: {result['tab_url'][:70]}\n"
            summary += f"    Status: {result['status']}\n"

            if result['status'] == 'success':
                summary += f"    Items: {len(result['items'])}\n"
            else:
                summary += f"    Error: {result.get('error_message', 'Unknown')}\n"

            summary += "\n"

        self.results_text.setText(summary)

        # Enable export
        self.export_button.setEnabled(True)

        # Re-enable controls
        self.start_button.setEnabled(True)
        self.template_combo.setEnabled(True)
        self.filter_all_radio.setEnabled(True)
        self.filter_ungrouped_radio.setEnabled(True)
        self.filter_grouped_radio.setEnabled(True)
        self.filter_regex_radio.setEnabled(True)

        QMessageBox.information(
            self,
            "Scraping Complete",
            f"Successfully scraped {results['successful']} tabs\n"
            f"Failed: {results['failed']}\n"
            f"Total items: {total_items}"
        )

    def on_error(self, error_message):
        """Handle scraping error."""
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)

        # Re-enable controls
        self.start_button.setEnabled(True)
        self.template_combo.setEnabled(True)
        self.filter_all_radio.setEnabled(True)
        self.filter_ungrouped_radio.setEnabled(True)
        self.filter_grouped_radio.setEnabled(True)
        self.filter_regex_radio.setEnabled(True)

        QMessageBox.critical(
            self,
            "Scraping Error",
            f"An error occurred during scraping:\n\n{error_message}"
        )

    def export_results(self):
        """Export results to JSON file."""
        if not self.results:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            f"{self.session_name}-scrape-results.json",
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2)

                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Results exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to export results:\n{e}"
                )
