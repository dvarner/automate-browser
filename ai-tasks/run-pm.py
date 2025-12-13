r"""
AI Project Manager Launcher Template

Copy this file to your project's ai-tasks/ folder as run-pm.py

Usage:
    cd D:\Claude\YourProject\ai-tasks
    python run-pm.py

Options:
    python run-pm.py --port 8080
    python run-pm.py --import ROADMAP.md
    python run-pm.py --no-browser

Auto-Update:
    This launcher automatically checks for updates from run-pm-template.py
    and updates itself if needed. This ensures all projects use the latest
    launcher version without manual intervention.
"""

import sys
import os
import hashlib
import shutil
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

# Find ai-pm-gui (go up to D:\Claude\ai-pm-gui)
project_root = Path(__file__).parent.parent  # D:\Claude\YourProject
ai_pm_gui = project_root.parent / 'ai-pm-gui'  # D:\Claude\ai-pm-gui

# Verify ai-pm-gui exists
if not ai_pm_gui.exists():
    print(f"Error: ai-pm-gui not found at {ai_pm_gui}")
    print("Please ensure D:\\Claude\\ai-pm-gui is installed")
    sys.exit(1)

# Add to Python path
sys.path.insert(0, str(ai_pm_gui))

# Set environment variables
os.environ['PM_DB_PATH'] = str(Path(__file__).parent / 'pm.db')
os.environ['PM_PROJECT_NAME'] = project_root.name

# ============================================================================
# Auto-Update Mechanism
# ============================================================================

def get_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    try:
        return hashlib.md5(filepath.read_bytes()).hexdigest()
    except Exception:
        return None


def check_and_update_launcher():
    """Check if launcher needs updating and auto-update if needed."""
    # Skip update check if we're in the middle of an update (prevent loop)
    if os.environ.get('PM_LAUNCHER_UPDATING'):
        return

    template_path = ai_pm_gui / 'run-pm-template.py'
    current_path = Path(__file__)

    # Skip if this IS the template (not a project launcher)
    if current_path.resolve() == template_path.resolve():
        return

    # Skip if template doesn't exist
    if not template_path.exists():
        return

    # Compare file hashes
    template_hash = get_file_hash(template_path)
    current_hash = get_file_hash(current_path)

    if not template_hash or not current_hash:
        return  # Couldn't read files, skip update

    if template_hash == current_hash:
        return  # Already up to date

    # Update needed
    print("[*] Launcher update available")
    print(f"    Template: {template_hash[:8]}...")
    print(f"    Current:  {current_hash[:8]}...")

    try:
        # Backup current launcher
        backup_path = current_path.with_suffix('.py.bak')
        shutil.copy2(current_path, backup_path)

        # Copy template to current location
        shutil.copy2(template_path, current_path)
        print("[+] Launcher updated successfully")
        print("[*] Restarting with new version...")

        # Set flag to prevent update loop
        os.environ['PM_LAUNCHER_UPDATING'] = '1'

        # Restart the process
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except PermissionError:
        print("[!] Warning: Permission denied updating launcher")
        print("    Continuing with current version...")
        print(f"    To update manually: copy {template_path} to {current_path}")

    except Exception as e:
        print(f"[!] Warning: Failed to update launcher: {e}")
        print("    Continuing with current version...")
        # Restore from backup if update failed
        if backup_path.exists():
            try:
                shutil.copy2(backup_path, current_path)
            except Exception:
                pass


# ============================================================================
# Run
# ============================================================================

if __name__ == '__main__':
    # Check for updates before running
    check_and_update_launcher()

    # Run the main application
    from run import main
    main()
