"""
Browser Automation Suite - Unified Launcher
Detects and routes to CLI, GUI, or Workflow modes

Usage:
    launcher.py                    Launch Desktop GUI (no args)
    launcher.py --gui              Launch Desktop GUI (explicit)
    launcher.py new                CLI: Start new browser session
    launcher.py save <name>        CLI: Save current session
    launcher.py load <name>        CLI: Load saved session
    launcher.py list               CLI: List available sessions
    launcher.py groups <name>      CLI: List groups in session
    launcher.py workflow <file>    Run YAML workflow
"""

import sys
import os
from pathlib import Path


def setup_paths():
    """Setup paths for bundled executable or development environment"""

    # Determine if running as bundled executable or development
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        base_path = Path(sys._MEIPASS)
        app_path = Path(sys.executable).parent

        # Set Playwright browsers path to bundled browsers
        playwright_browsers = app_path / 'playwright' / 'browsers'
        if playwright_browsers.exists():
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(playwright_browsers)
    else:
        # Running in development
        base_path = Path(__file__).parent.parent
        app_path = base_path

    # Add module paths
    tab_session_path = base_path / 'tab-session-manager'
    workflow_path = base_path / 'workflow-engine'
    desktop_gui_path = base_path / 'tab-session-manager' / 'desktop_gui'

    # Add to Python path if not already there
    for path in [tab_session_path, workflow_path, desktop_gui_path]:
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)

    # Set working directory for sessions/profiles
    sessions_dir = app_path / 'sessions'
    profiles_dir = app_path / 'profiles'

    # Create directories if they don't exist
    sessions_dir.mkdir(exist_ok=True)
    profiles_dir.mkdir(exist_ok=True)

    # Set environment variables for session paths
    os.environ['BROWSER_SESSIONS_DIR'] = str(sessions_dir)
    os.environ['BROWSER_PROFILES_DIR'] = str(profiles_dir)

    return base_path, app_path


def launch_cli():
    """Launch Tab Session Manager in CLI mode"""
    try:
        import tab_session_manager
        tab_session_manager.main()
    except ImportError as e:
        print(f"Error: Could not import tab_session_manager: {e}")
        print("Make sure tab_session_manager.py is included in the build.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running CLI: {e}")
        sys.exit(1)


def launch_workflow():
    """Launch Workflow Runner"""
    try:
        # Remove 'workflow' from args so workflow_runner gets the file path
        sys.argv.pop(1)

        import workflow_runner
        workflow_runner.main()
    except ImportError as e:
        print(f"Error: Could not import workflow_runner: {e}")
        print("Make sure workflow_runner.py is included in the build.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running workflow: {e}")
        sys.exit(1)


def launch_gui():
    """Launch Desktop GUI"""
    try:
        # Import PyQt6 application
        from main import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error: Could not import desktop GUI: {e}")
        print("Make sure PyQt6 and desktop_gui modules are included.")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def show_help():
    """Display help information"""
    print("""
================================================================
         Browser Automation Suite v2.0
         Tab Session Manager + Workflow Engine
================================================================

USAGE:

  GUI Mode (Desktop Application):
    BrowserAutomation                Launch Desktop GUI
    BrowserAutomation --gui          Launch Desktop GUI (explicit)

  CLI Mode (Tab Session Manager):
    BrowserAutomation new            Start new browser session
    BrowserAutomation save <name>    Save current session
    BrowserAutomation load <name>    Load saved session
    BrowserAutomation list           List available sessions
    BrowserAutomation groups <name>  Show groups in session

  Workflow Mode (YAML Automation):
    BrowserAutomation workflow <file.yaml>    Run workflow

EXAMPLES:

  # Launch GUI
  BrowserAutomation

  # Start new Chrome session with incognito
  BrowserAutomation new --browser chrome --incognito

  # Save current browser session
  BrowserAutomation save my-session

  # Load saved session
  BrowserAutomation load my-session

  # Run automation workflow
  BrowserAutomation workflow scraping.yaml

DOCUMENTATION:

  - README.md in installation folder
  - Chrome Extension: Load from chrome-extension/ folder
  - Workflow examples: See workflows/ folder

For more help, visit: https://github.com/your-repo/browser-automation
    """)


def main():
    """Main entry point - route to appropriate mode"""

    # Setup paths for bundled or development environment
    base_path, app_path = setup_paths()

    # Detect mode based on arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        # CLI commands
        if command in ['new', 'save', 'load', 'list', 'groups']:
            launch_cli()

        # Workflow mode
        elif command == 'workflow':
            if len(sys.argv) < 3:
                print("Error: workflow command requires a YAML file path")
                print("Usage: BrowserAutomation workflow <file.yaml>")
                sys.exit(1)
            launch_workflow()

        # Explicit GUI launch
        elif command == '--gui':
            launch_gui()

        # Help
        elif command in ['-h', '--help', 'help']:
            show_help()

        # Unknown command
        else:
            print(f"Error: Unknown command '{command}'")
            print()
            show_help()
            sys.exit(1)

    else:
        # No arguments = GUI mode (double-click behavior)
        launch_gui()


if __name__ == '__main__':
    main()
