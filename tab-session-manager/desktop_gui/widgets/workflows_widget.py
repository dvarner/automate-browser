"""
Workflows Widget - Browse and run YAML workflow automations
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QTextEdit,
    QComboBox, QCheckBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QProcess
from PyQt6.QtGui import QFont, QTextCursor
from pathlib import Path
import yaml
import sys


class WorkflowCard(QWidget):
    """Individual workflow card widget"""

    run_clicked = pyqtSignal(str)  # Emits workflow file path

    def __init__(self, workflow_path, parent=None):
        super().__init__(parent)
        self.workflow_path = workflow_path
        self.workflow_data = None
        self.init_ui()
        self.load_workflow_info()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Workflow name
        self.name_label = QLabel("Loading...")
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        layout.addWidget(self.name_label)

        # Workflow file path
        self.path_label = QLabel(str(self.workflow_path))
        self.path_label.setStyleSheet("color: #424242; font-size: 9pt;")
        layout.addWidget(self.path_label)

        # Steps count
        self.steps_label = QLabel("Steps: 0")
        self.steps_label.setStyleSheet("color: #212121; font-size: 10pt;")
        layout.addWidget(self.steps_label)

        # Browser type
        self.browser_label = QLabel("Browser: chromium")
        self.browser_label.setStyleSheet("color: #212121; font-size: 10pt;")
        layout.addWidget(self.browser_label)

        # Run button
        self.run_button = QPushButton("Run Workflow")
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: #ffffff;
                border: 2px solid #1B5E20;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #388E3C;
                border: 2px solid #2E7D32;
            }
            QPushButton:disabled {
                background-color: #9E9E9E;
                border: 2px solid #757575;
                color: #E0E0E0;
            }
        """)
        self.run_button.clicked.connect(self.on_run_clicked)
        layout.addWidget(self.run_button)

        # Card styling
        self.setStyleSheet("""
            WorkflowCard {
                background-color: #ffffff;
                border: 2px solid #bdbdbd;
                border-radius: 8px;
            }
            WorkflowCard:hover {
                border: 2px solid #2E7D32;
                background-color: #f5f5f5;
            }
        """)

        self.setMaximumHeight(180)

    def load_workflow_info(self):
        """Load workflow YAML and extract metadata"""
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                self.workflow_data = yaml.safe_load(f)

            # Update UI with workflow info
            name = self.workflow_data.get('name', self.workflow_path.stem)
            self.name_label.setText(name)

            steps = self.workflow_data.get('steps', [])
            self.steps_label.setText(f"Steps: {len(steps)}")

            browser = self.workflow_data.get('browser', 'chromium')
            self.browser_label.setText(f"Browser: {browser}")

        except Exception as e:
            self.name_label.setText(f"Error loading: {self.workflow_path.name}")
            self.steps_label.setText(f"Error: {str(e)}")

    def on_run_clicked(self):
        """Emit signal when run button is clicked"""
        self.run_clicked.emit(str(self.workflow_path))


class WorkflowsWidget(QWidget):
    """Main workflows widget for browsing and running YAML workflows"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.workflows_dir = Path(__file__).parent.parent.parent.parent / "workflow-engine" / "workflows"
        self.workflow_runner = Path(__file__).parent.parent.parent.parent / "workflow-engine" / "workflow_runner.py"
        self.process = None  # QProcess for running workflows
        self.is_running = False
        self.init_ui()
        self.load_workflows()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Set widget background
        self.setStyleSheet("""
            WorkflowsWidget {
                background-color: #f5f5f5;
            }
        """)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("YAML Workflow Automations")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #000000; background: transparent;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Button style for header buttons
        button_style = """
            QPushButton {
                background-color: #1976D2;
                color: #ffffff;
                border: 2px solid #0D47A1;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #1E88E5;
                border: 2px solid #1565C0;
            }
        """

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(button_style)
        refresh_btn.clicked.connect(self.load_workflows)
        header_layout.addWidget(refresh_btn)

        # Stop workflow button
        self.stop_btn = QPushButton("Stop Workflow")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: #ffffff;
                border: 2px solid #B71C1C;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 10pt;
            }
            QPushButton:hover:enabled {
                background-color: #E53935;
                border: 2px solid #C62828;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                border: 2px solid #9E9E9E;
                color: #757575;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_workflow)
        header_layout.addWidget(self.stop_btn)

        # Open folder button
        open_folder_btn = QPushButton("Open Workflows Folder")
        open_folder_btn.setStyleSheet(button_style)
        open_folder_btn.clicked.connect(self.open_workflows_folder)
        header_layout.addWidget(open_folder_btn)

        # View results button
        results_btn = QPushButton("View Results")
        results_btn.setStyleSheet(button_style)
        results_btn.clicked.connect(self.open_results_folder)
        header_layout.addWidget(results_btn)

        layout.addLayout(header_layout)

        # Options bar
        options_layout = QHBoxLayout()

        # Browser selection
        browser_label = QLabel("Browser:")
        browser_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 11pt;")
        options_layout.addWidget(browser_label)

        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["chrome", "firefox", "chromium", "webkit"])
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
            QComboBox::drop-down {
                border: none;
            }
        """)
        options_layout.addWidget(self.browser_combo)

        # Headless mode
        self.headless_check = QCheckBox("Headless Mode")
        self.headless_check.setStyleSheet("""
            QCheckBox {
                color: #000000;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        options_layout.addWidget(self.headless_check)

        options_layout.addStretch()

        layout.addLayout(options_layout)

        # Workflow list (scrollable)
        self.workflow_list = QListWidget()
        self.workflow_list.setSpacing(10)
        self.workflow_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #bdbdbd;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.workflow_list)

        # Status/output area
        status_label = QLabel("Output:")
        status_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 11pt;")
        layout.addWidget(status_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(200)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
                border: 3px solid #424242;
                border-radius: 6px;
                padding: 10px;
                font-size: 10pt;
            }
        """)
        layout.addWidget(self.output_text)

    def load_workflows(self):
        """Load all YAML workflows from the workflows directory"""
        self.workflow_list.clear()

        if not self.workflows_dir.exists():
            self.output_text.append(f"Workflows directory not found: {self.workflows_dir}")
            return

        # Find all .yaml files
        yaml_files = list(self.workflows_dir.glob("*.yaml"))

        if not yaml_files:
            self.output_text.append("No workflow files found in workflows directory")
            return

        # Create a card for each workflow
        for yaml_file in sorted(yaml_files):
            card = WorkflowCard(yaml_file)
            card.run_clicked.connect(self.run_workflow)

            # Add to list widget
            item = QListWidgetItem(self.workflow_list)
            item.setSizeHint(card.sizeHint())
            self.workflow_list.addItem(item)
            self.workflow_list.setItemWidget(item, card)

        self.output_text.append(f"Loaded {len(yaml_files)} workflows")

    def run_workflow(self, workflow_path):
        """Run a workflow file using QProcess"""
        # Check if a workflow is already running
        if self.is_running:
            QMessageBox.warning(self, "Workflow Running",
                              "A workflow is already running. Please wait for it to complete.")
            return

        # Check if workflow runner exists
        if not self.workflow_runner.exists():
            QMessageBox.critical(self, "Error",
                               f"Workflow runner not found:\n{self.workflow_runner}")
            return

        # Clear output and show starting message
        self.output_text.clear()
        self.output_text.append(f"=== Starting Workflow: {Path(workflow_path).name} ===")
        self.output_text.append(f"Browser: {self.browser_combo.currentText()}")
        self.output_text.append(f"Headless: {self.headless_check.isChecked()}")
        self.output_text.append("=" * 60)
        self.output_text.append("")

        # Create QProcess
        self.process = QProcess(self)

        # Connect signals
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.process_error)

        # Build command arguments
        args = [str(self.workflow_runner), str(workflow_path)]

        if self.headless_check.isChecked():
            args.append("--headless")

        args.extend(["--browser", self.browser_combo.currentText()])

        # Show command being executed
        cmd_display = f"python {' '.join(args)}"
        self.output_text.append(f"Command: {cmd_display}")
        self.output_text.append("")

        # Set working directory to workflow-engine
        working_dir = str(self.workflow_runner.parent)

        # Start the process
        self.process.setWorkingDirectory(working_dir)
        self.process.start(sys.executable, args)

        # Update state
        self.is_running = True
        self.disable_all_run_buttons(True)

    def handle_stdout(self):
        """Handle standard output from the process"""
        if self.process:
            data = self.process.readAllStandardOutput()
            text = bytes(data).decode('utf-8', errors='replace')
            self.append_output(text)

    def handle_stderr(self):
        """Handle standard error from the process"""
        if self.process:
            data = self.process.readAllStandardError()
            text = bytes(data).decode('utf-8', errors='replace')
            # Display stderr in a different color (red)
            self.append_output(text, is_error=True)

    def append_output(self, text, is_error=False):
        """Append text to output area"""
        if not text:
            return

        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

        if is_error:
            # Red color for errors
            self.output_text.setTextColor(Qt.GlobalColor.red)
        else:
            # Green color for normal output
            self.output_text.setTextColor(Qt.GlobalColor.green)

        self.output_text.insertPlainText(text)

        # Reset color
        self.output_text.setTextColor(Qt.GlobalColor.green)

        # Scroll to bottom
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

    def process_finished(self, exit_code, exit_status):
        """Handle process completion"""
        self.output_text.append("")
        self.output_text.append("=" * 60)

        if exit_code == 0:
            self.output_text.append(f"=== Workflow Completed Successfully ===")
        else:
            self.output_text.append(f"=== Workflow Failed (Exit Code: {exit_code}) ===")

        self.output_text.append("=" * 60)

        # Update state
        self.is_running = False
        self.disable_all_run_buttons(False)
        self.process = None

    def process_error(self, error):
        """Handle process errors"""
        error_messages = {
            QProcess.ProcessError.FailedToStart: "Failed to start workflow runner",
            QProcess.ProcessError.Crashed: "Workflow runner crashed",
            QProcess.ProcessError.Timedout: "Workflow execution timed out",
            QProcess.ProcessError.WriteError: "Write error occurred",
            QProcess.ProcessError.ReadError: "Read error occurred",
            QProcess.ProcessError.UnknownError: "Unknown error occurred"
        }

        error_msg = error_messages.get(error, f"Error: {error}")
        self.output_text.append("")
        self.output_text.append(f"ERROR: {error_msg}")

        # Update state
        self.is_running = False
        self.disable_all_run_buttons(False)

    def disable_all_run_buttons(self, disable):
        """Enable or disable all run buttons"""
        for i in range(self.workflow_list.count()):
            item = self.workflow_list.item(i)
            widget = self.workflow_list.itemWidget(item)
            if isinstance(widget, WorkflowCard):
                widget.run_button.setEnabled(not disable)
                if disable:
                    widget.run_button.setText("Running...")
                else:
                    widget.run_button.setText("Run Workflow")

        # Enable/disable stop button
        self.stop_btn.setEnabled(disable)

    def stop_workflow(self):
        """Stop the currently running workflow"""
        if self.process and self.is_running:
            reply = QMessageBox.question(
                self,
                "Stop Workflow",
                "Are you sure you want to stop the running workflow?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.output_text.append("")
                self.output_text.append(">>> User requested to stop workflow...")
                self.process.kill()
                self.process.waitForFinished(3000)
                self.output_text.append(">>> Workflow stopped by user")

                # Update state
                self.is_running = False
                self.disable_all_run_buttons(False)

    def open_workflows_folder(self):
        """Open the workflows folder in file explorer"""
        import subprocess
        import platform

        if not self.workflows_dir.exists():
            QMessageBox.warning(self, "Folder Not Found",
                              f"Workflows directory does not exist:\n{self.workflows_dir}")
            return

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(self.workflows_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(self.workflows_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(self.workflows_dir)])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{str(e)}")

    def open_results_folder(self):
        """Open the results folder in file explorer"""
        import subprocess
        import platform

        results_dir = self.workflow_runner.parent / "results"

        # Create results folder if it doesn't exist
        if not results_dir.exists():
            try:
                results_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.warning(self, "Error",
                                  f"Could not create results folder:\n{str(e)}")
                return

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(results_dir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(results_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(results_dir)])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{str(e)}")
