"""
Wrapper around TabSessionManager for GUI integration.
Provides Qt signals for events and thread-safe operations.
"""

import sys
import json
import threading
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# Add parent directory to path to import tab_session_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tab_session_manager import TabSessionManager


class SessionManagerWrapper(QObject):
    """Thread-safe wrapper for TabSessionManager with Qt signals."""

    # Qt signals
    session_loaded = pyqtSignal(str)  # session_name
    session_saved = pyqtSignal(str)   # session_name
    session_deleted = pyqtSignal(str) # session_name
    browser_status_changed = pyqtSignal(bool)  # is_running

    def __init__(self):
        super().__init__()
        self.sessions_dir = Path(__file__).parent.parent.parent / 'sessions'
        self.sessions_dir.mkdir(exist_ok=True)
        self._browser_running = False
        self.active_manager = None  # Keep reference to prevent garbage collection

    def get_sessions(self):
        """Get all saved sessions.

        Returns:
            List of dicts with session info: name, created_at, tab_count, group_count
        """
        sessions = []
        session_files = list(self.sessions_dir.glob('*.json'))

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                session_name = session_file.stem
                created_at = data.get('created_at', 'Unknown')

                # Calculate tab count (handle both old and new format)
                if 'groups' in data:
                    tab_count = sum(len(g.get('tabs', [])) for g in data.get('groups', []))
                    tab_count += len(data.get('ungrouped_tabs', []))
                    group_count = len(data.get('groups', []))
                else:
                    tab_count = len(data.get('tabs', []))
                    group_count = 0

                sessions.append({
                    'name': session_name,
                    'created_at': created_at,
                    'tab_count': tab_count,
                    'group_count': group_count,
                    'file_path': str(session_file)
                })
            except Exception as e:
                print(f"Error loading session {session_file}: {e}")

        return sessions

    def get_session_details(self, session_name):
        """Get detailed session information including all tabs and groups.

        Args:
            session_name: Name of the session

        Returns:
            Dict with session details or None if not found
        """
        session_file = self.sessions_dir / f'{session_name}.json'

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Parse into consistent format
            details = {
                'name': session_name,
                'created_at': data.get('created_at', 'Unknown'),
                'groups': [],
                'ungrouped_tabs': []
            }

            # Handle new format (with groups)
            if 'groups' in data:
                details['groups'] = data.get('groups', [])
                details['ungrouped_tabs'] = data.get('ungrouped_tabs', [])
            # Handle old format (flat tabs)
            elif 'tabs' in data:
                details['ungrouped_tabs'] = data.get('tabs', [])

            return details
        except Exception as e:
            print(f"Error loading session details: {e}")
            return None

    def load_session(self, session_name, group_filter=None):
        """Load a session (opens browser with tabs).

        Args:
            session_name: Name of the session to load
            group_filter: Optional list of group names to load

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Close existing browser if running
            if self.active_manager:
                try:
                    print("[DEBUG] Closing existing browser before loading session...")
                    self.active_manager.cleanup()
                    import time
                    time.sleep(2)  # Give port time to release
                except Exception as cleanup_error:
                    print(f"[WARNING] Error closing existing browser: {cleanup_error}")

            # Create TabSessionManager instance
            self.active_manager = TabSessionManager(auto_save_enabled=True, auto_save_interval=3.0)

            # Load the session in a separate thread to avoid asyncio loop conflict
            load_success = [False]
            load_error = [None]

            def load_thread():
                try:
                    # Set asyncio policy to avoid conflicts
                    import asyncio
                    try:
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                    except:
                        pass

                    result = self.active_manager.load_session(session_name, group_filter=group_filter)
                    load_success[0] = result
                except Exception as e:
                    load_error[0] = e
                    import traceback
                    print(f"[ERROR] Load thread exception: {e}")
                    traceback.print_exc()

            thread = threading.Thread(target=load_thread, daemon=False)
            thread.start()
            thread.join(timeout=30)

            if load_error[0]:
                print(f"[ERROR] Load failed with error: {load_error[0]}")
                raise load_error[0]

            if not thread.is_alive():
                if load_success[0]:
                    self.session_loaded.emit(session_name)
                    self._browser_running = True
                    self.browser_status_changed.emit(True)
                    return True
                else:
                    print("[ERROR] Load thread completed but returned False")
                    return False
            else:
                print("[ERROR] Load thread timed out after 30 seconds")
                return False

        except Exception as e:
            import traceback
            print(f"[ERROR] Error loading session: {e}")
            traceback.print_exc()
            return False

    def create_new_session(self, session_name, auto_save=True, auto_save_interval=3.0, browser_type='chrome', incognito_mode=False, profile_name=None):
        """Create a new browser session.

        Args:
            session_name: Name for the session
            auto_save: Enable auto-save
            auto_save_interval: Auto-save interval in seconds
            browser_type: Browser to use ('chrome', 'brave', 'firefox', 'chromium')
            incognito_mode: Launch in incognito/private mode
            profile_name: Optional profile name for persistent storage

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"[DEBUG] Creating session: {session_name}")
            print(f"[DEBUG] Browser: {browser_type}, Incognito: {incognito_mode}")
            print(f"[DEBUG] Profile: {profile_name if profile_name else 'None (ephemeral)'}")

            # Validate session name
            if not self._validate_session_name(session_name):
                print(f"[ERROR] Session name validation failed: {session_name}")
                return False

            print("[DEBUG] Session name validated")

            # Create TabSessionManager instance
            self.active_manager = TabSessionManager(
                auto_save_enabled=auto_save,
                auto_save_interval=auto_save_interval
            )
            print("[DEBUG] TabSessionManager created")

            # Launch browser in a separate thread to avoid asyncio loop conflict
            print(f"[DEBUG] Launching browser: {browser_type}")

            launch_success = [False]  # Use list to allow modification in thread
            launch_error = [None]

            def launch_thread():
                try:
                    # Set environment variable to avoid asyncio conflicts
                    import os
                    os.environ['PLAYWRIGHT_PYTHON_SYNC_LAUNCH'] = '1'

                    self.active_manager.launch_browser(browser_type=browser_type, incognito_mode=incognito_mode, profile_name=profile_name)
                    launch_success[0] = True
                except Exception as e:
                    # Check if it's just the asyncio warning but browser actually launched
                    error_msg = str(e)
                    if "asyncio loop" in error_msg and self.active_manager.browser:
                        print("[WARNING] Asyncio warning but browser launched successfully")
                        launch_success[0] = True  # Browser is running despite warning
                    else:
                        launch_error[0] = e

            thread = threading.Thread(target=launch_thread, daemon=False)
            thread.start()
            thread.join(timeout=10)  # Wait up to 10 seconds for browser to start

            if launch_error[0]:
                raise launch_error[0]

            if not launch_success[0]:
                raise Exception("Browser launch timed out")

            print("[DEBUG] Browser launched successfully")

            # Save initial session file so it appears in the session list
            # Note: This may fail if browser just launched, but that's okay
            try:
                print(f"[DEBUG] Saving initial session file: {session_name}")
                self.active_manager.save_session(session_name, quiet=True)
                print("[DEBUG] Initial session file saved")
            except Exception as save_error:
                print(f"[WARNING] Could not save initial session (this is normal): {save_error}")
                # This is okay - user can save later manually

            self._browser_running = True
            self.browser_status_changed.emit(True)

            return True
        except Exception as e:
            import traceback
            print(f"[ERROR] Error creating new session: {e}")
            print(f"[ERROR] Traceback:")
            traceback.print_exc()
            return False

    def delete_session(self, session_name):
        """Delete a saved session.

        Args:
            session_name: Name of the session to delete

        Returns:
            bool: True if successful, False otherwise
        """
        session_file = self.sessions_dir / f'{session_name}.json'

        if not session_file.exists():
            return False

        try:
            session_file.unlink()
            self.session_deleted.emit(session_name)
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def check_browser_status(self):
        """Check if browser is currently running.

        Returns:
            bool: True if browser is running, False otherwise
        """
        # For now, we'll check if we can connect to the debugging port
        # This is a simplified check - in production you might want to actually
        # try connecting via CDP
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('localhost', 9222))
            sock.close()

            is_running = (result == 0)

            # Emit signal if status changed
            if is_running != self._browser_running:
                self._browser_running = is_running
                self.browser_status_changed.emit(is_running)

            return is_running
        except Exception:
            return False

    def _validate_session_name(self, name):
        """Validate session name for safety.

        Args:
            name: Session name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not name:
            return False
        # Allow alphanumeric, dash, and underscore only
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        return all(c in allowed_chars for c in name)
