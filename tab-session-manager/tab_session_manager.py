#!/usr/bin/env python3
"""
Browser Tab Session Manager (MVP)
Track browser tabs, save sessions to JSON, and restore them later.
"""

import argparse
import json
import sys
import os
import threading
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


class AutoSaveManager:
    """Manages automatic saving of browser sessions when tabs change."""

    def __init__(self, session_manager, interval=3.0, enabled=True):
        self.session_manager = session_manager
        self.interval = interval  # Debounce interval in seconds
        self.enabled = enabled
        self.save_timer = None
        self.lock = threading.Lock()
        self.cached_tabs = []  # Cache tab data to avoid thread issues

    def trigger_save(self, tabs_data=None):
        """Trigger a debounced auto-save.

        Args:
            tabs_data: Optional list of tab dicts to cache (avoids Playwright access in thread)
        """
        if not self.enabled:
            return

        # Cache the tab data if provided (called from main thread)
        if tabs_data is not None:
            self.cached_tabs = tabs_data

        with self.lock:
            # Cancel any pending save
            if self.save_timer and self.save_timer.is_alive():
                self.save_timer.cancel()

            # Schedule new save after interval
            self.save_timer = threading.Timer(self.interval, self._do_auto_save)
            self.save_timer.start()

    def _do_auto_save(self):
        """Perform the actual auto-save using cached data (thread-safe)."""
        try:
            print("\n[Auto-save] Saving session...")
            # Use cached tabs instead of accessing Playwright (thread-safe)
            success = self.session_manager.save_session('auto-save', quiet=True, cached_tabs=self.cached_tabs)
            if success:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[Auto-save] Session saved at {timestamp}")
        except Exception as e:
            print(f"[Auto-save] Error: {e}")

    def cancel(self):
        """Cancel any pending auto-save."""
        with self.lock:
            if self.save_timer and self.save_timer.is_alive():
                self.save_timer.cancel()


class TabSessionManager:
    """Manages browser tab sessions with save/load functionality."""

    def __init__(self, auto_save_enabled=True, auto_save_interval=3.0):
        self.sessions_dir = Path(__file__).parent / 'sessions'
        self.sessions_dir.mkdir(exist_ok=True)
        self.tabs = []
        self.browser = None
        self.context = None
        self.playwright = None
        self.auto_save_manager = AutoSaveManager(self, interval=auto_save_interval, enabled=auto_save_enabled)
        self.current_browser_type = None  # Track current browser type
        self.current_profile_name = None  # Track current profile name
        self.current_incognito_mode = False  # Track incognito status

    def launch_browser(self, browser_type='chrome', incognito_mode=False, profile_name=None):
        """Launch browser in headed mode and return browser instance.

        Args:
            browser_type: Browser to use ('chrome', 'brave', 'firefox', 'chromium')
            incognito_mode: Launch in incognito/private mode (overrides profile)
            profile_name: Optional profile name for persistent storage (e.g., 'work', 'personal')
                         If None or empty, uses ephemeral session (current behavior)
                         Ignored if incognito_mode=True
        """
        print(f"Launching {browser_type} browser" + (" in incognito mode..." if incognito_mode else "..."))
        self.playwright = sync_playwright().start()

        # Determine if using persistent profile
        use_persistent_profile = profile_name and not incognito_mode
        profile_path = None

        if use_persistent_profile:
            # Create profiles directory if it doesn't exist
            from pathlib import Path
            import re
            profiles_dir = Path(__file__).parent / 'profiles'
            profiles_dir.mkdir(exist_ok=True)

            # Validate profile name (alphanumeric, dash, underscore only)
            if not re.match(r'^[a-zA-Z0-9_-]+$', profile_name):
                print(f"[WARNING] Invalid profile name '{profile_name}', using ephemeral session")
                use_persistent_profile = False
            else:
                profile_path = profiles_dir / profile_name
                profile_path.mkdir(exist_ok=True)
                print(f"Using persistent profile: {profile_path}")

        # Store profile info for session metadata
        browser_type_lower = browser_type.lower()
        self.current_browser_type = browser_type_lower
        self.current_profile_name = profile_name if use_persistent_profile else None
        self.current_incognito_mode = incognito_mode

        # Browser launch with profile support
        if browser_type_lower == 'firefox':
            # Firefox implementation
            firefox_args = []
            if incognito_mode:
                firefox_args.append('--private-window')

            if use_persistent_profile:
                # Launch with persistent profile
                self.context = self.playwright.firefox.launch_persistent_context(
                    str(profile_path),
                    headless=False,
                    args=firefox_args,
                    no_viewport=True
                )
                self.browser = self.context.browser
            else:
                # Launch without profile (current behavior)
                self.browser = self.playwright.firefox.launch(
                    headless=False,
                    args=firefox_args
                )
                self.context = self.browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    no_viewport=True
                )

        elif browser_type_lower in ['chrome', 'chromium', 'brave']:
            # Chromium-based browsers
            launch_args = [
                '--remote-debugging-port=9222',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
            ]

            if incognito_mode:
                launch_args.append('--incognito')

            launch_kwargs = {
                'headless': False,
                'args': launch_args
            }

            # Set channel or executable path
            if browser_type_lower == 'chrome':
                launch_kwargs['channel'] = 'chrome'
            elif browser_type_lower == 'brave':
                # Brave: try common installation paths
                import platform
                brave_paths = []
                if platform.system() == 'Windows':
                    brave_paths = [
                        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                    ]
                elif platform.system() == 'Darwin':
                    brave_paths = ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
                elif platform.system() == 'Linux':
                    brave_paths = ["/usr/bin/brave-browser", "/usr/bin/brave"]

                brave_exe = None
                for path in brave_paths:
                    if os.path.exists(path):
                        brave_exe = path
                        break

                if brave_exe:
                    launch_kwargs['executable_path'] = brave_exe
                else:
                    print("[WARNING] Brave browser not found, falling back to Chromium")

            if use_persistent_profile:
                # Launch with persistent profile
                self.context = self.playwright.chromium.launch_persistent_context(
                    str(profile_path),
                    **launch_kwargs,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    no_viewport=True
                )
                self.browser = self.context.browser
            else:
                # Launch without profile (current behavior)
                self.browser = self.playwright.chromium.launch(**launch_kwargs)
                self.context = self.browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    no_viewport=True
                )
        else:
            # Default to chromium
            launch_args = [
                '--remote-debugging-port=9222',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
            ]
            if incognito_mode:
                launch_args.append('--incognito')

            if use_persistent_profile:
                self.context = self.playwright.chromium.launch_persistent_context(
                    str(profile_path),
                    headless=False,
                    args=launch_args,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    no_viewport=True
                )
                self.browser = self.context.browser
            else:
                self.browser = self.playwright.chromium.launch(headless=False, args=launch_args)
                self.context = self.browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    no_viewport=True
                )

        # Open initial blank page
        page = self.context.new_page()

        # Track the initial page
        self._add_tab(page)

        # Listen for new pages/tabs
        self.context.on('page', self._on_new_page)

        print("Browser launched successfully!")
        print("Open tabs manually. When done, use save command to save session.")
        return self.browser

    def connect_to_browser(self):
        """Connect to an existing browser instance via remote debugging port."""
        try:
            print("Connecting to running browser...")
            self.playwright = sync_playwright().start()
            # Connect to browser on debugging port 9222
            self.browser = self.playwright.chromium.connect_over_cdp('http://localhost:9222')
            # Get the default context
            contexts = self.browser.contexts
            if contexts:
                self.context = contexts[0]
                print(f"Connected successfully! Found {len(self.context.pages)} open tabs.")
                return True
            else:
                print("Error: No browser context found")
                return False
        except Exception as e:
            print(f"Error connecting to browser: {e}")
            print("\nMake sure browser is running with:")
            print("  python tab_session_manager.py new")
            print("  or")
            print("  python tab_session_manager.py load <session-name>")
            return False

    def _on_new_page(self, page: Page):
        """Handle new page/tab opened event."""
        # Wait for the page to load to get the URL
        try:
            page.wait_for_load_state('domcontentloaded', timeout=5000)
        except Exception:
            pass  # Timeout is okay, we'll get URL anyway

        self._add_tab(page)

        # Set up event listeners for this page
        page.on('close', lambda: self._on_tab_close(page))
        page.on('framenavigated', lambda frame: self._on_url_change(page, frame))

        # Get current tabs and trigger auto-save for new tab (thread-safe)
        tabs_data = self._get_current_tabs()
        self.auto_save_manager.trigger_save(tabs_data)

    def _add_tab(self, page: Page):
        """Add a tab to the tracking list."""
        try:
            url = page.url
            title = page.title() if url != 'about:blank' else 'New Tab'

            tab_data = {
                'order': len(self.tabs) + 1,
                'url': url,
                'title': title
            }
            self.tabs.append(tab_data)
            print(f"  Tab {tab_data['order']}: {title} - {url}")
        except Exception as e:
            print(f"  Warning: Could not track tab - {e}")

    def _on_tab_close(self, page: Page):
        """Handle tab close event."""
        print(f"  Tab closed: {page.url}")
        # Get current tabs and trigger auto-save (thread-safe)
        tabs_data = self._get_current_tabs()
        self.auto_save_manager.trigger_save(tabs_data)

    def _on_url_change(self, page: Page, frame):
        """Handle URL change in tab."""
        # Only trigger for main frame changes
        if frame == page.main_frame:
            print(f"  URL changed: {page.url}")
            # Get current tabs and trigger auto-save (thread-safe)
            tabs_data = self._get_current_tabs()
            self.auto_save_manager.trigger_save(tabs_data)

    def _get_current_tabs(self):
        """Get current tabs from browser (must be called from main thread)."""
        current_tabs = []
        if self.context:
            for idx, page in enumerate(self.context.pages, 1):
                try:
                    url = page.url
                    title = page.title()
                    current_tabs.append({
                        'order': idx,
                        'url': url,
                        'title': title
                    })
                except Exception as e:
                    print(f"  Warning: Could not read tab {idx} - {e}")
        return current_tabs

    def _load_existing_session_structure(self, session_name):
        """Load existing session structure to preserve groups.

        Returns:
            Existing session data dict if file exists, None otherwise
        """
        session_file = self.sessions_dir / f'{session_name}.json'
        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def _map_tabs_to_groups(self, current_tabs, existing_groups):
        """Map current tabs into existing group structure.

        Args:
            current_tabs: List of current tab dicts
            existing_groups: List of existing group dicts from session

        Returns:
            Tuple of (updated_groups, ungrouped_tabs)
        """
        # Create URL lookup for current tabs
        current_tabs_by_url = {tab['url']: tab for tab in current_tabs}

        # Update existing groups
        updated_groups = []
        used_urls = set()

        for group in existing_groups:
            group_name = group.get('name', 'Unnamed')
            old_tabs = group.get('tabs', [])
            new_tabs = []

            # Keep tabs that still exist
            for old_tab in old_tabs:
                old_url = old_tab.get('url')
                if old_url in current_tabs_by_url:
                    # Tab still exists, update it
                    new_tabs.append(current_tabs_by_url[old_url])
                    used_urls.add(old_url)

            # Only include group if it has tabs
            if new_tabs:
                updated_groups.append({
                    'name': group_name,
                    'tabs': new_tabs
                })

        # Collect ungrouped tabs (new tabs not in any group)
        ungrouped_tabs = [
            tab for tab in current_tabs
            if tab['url'] not in used_urls
        ]

        return updated_groups, ungrouped_tabs

    def save_session(self, session_name: str, quiet=False, cached_tabs=None):
        """Save current browser session to JSON file.

        Args:
            session_name: Name for the session
            quiet: Suppress output if True
            cached_tabs: Use these tabs instead of reading from browser (for thread safety)
        """
        # Validate session name
        if not self._validate_session_name(session_name):
            if not quiet:
                print(f"Error: Invalid session name '{session_name}'")
                print("Session names should contain only letters, numbers, dashes, and underscores")
            return False

        # Get tabs - use cached if provided, otherwise read from browser
        if cached_tabs is not None:
            current_tabs = cached_tabs
        else:
            current_tabs = self._get_current_tabs()

        if not current_tabs:
            current_tabs = self.tabs  # Fallback to tracked tabs

        # Check if existing session has groups (preserve structure)
        existing_data = self._load_existing_session_structure(session_name)

        if existing_data and 'groups' in existing_data:
            # Preserve group structure
            existing_groups = existing_data.get('groups', [])
            updated_groups, ungrouped_tabs = self._map_tabs_to_groups(current_tabs, existing_groups)

            session_data = {
                'session_name': session_name,
                'created_at': datetime.now().isoformat(),
                'browser_type': self.current_browser_type,
                'profile_name': self.current_profile_name,
                'incognito_mode': self.current_incognito_mode,
                'groups': updated_groups
            }

            # Add ungrouped tabs if any
            if ungrouped_tabs:
                session_data['ungrouped_tabs'] = ungrouped_tabs

            if not quiet:
                total_grouped = sum(len(g['tabs']) for g in updated_groups)
                print(f"  Preserved {len(updated_groups)} groups ({total_grouped} tabs)")
                if ungrouped_tabs:
                    print(f"  Added {len(ungrouped_tabs)} new tabs to ungrouped")
        else:
            # No existing groups, save as flat format
            session_data = {
                'session_name': session_name,
                'created_at': datetime.now().isoformat(),
                'browser_type': self.current_browser_type,
                'profile_name': self.current_profile_name,
                'incognito_mode': self.current_incognito_mode,
                'tabs': current_tabs
            }
            self.tabs = current_tabs  # Update tracked tabs

        # Save to file
        session_file = self.sessions_dir / f'{session_name}.json'
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            if not quiet:
                # Calculate total tabs (works for both formats)
                if 'groups' in session_data:
                    total_tabs = sum(len(g['tabs']) for g in session_data['groups'])
                    total_tabs += len(session_data.get('ungrouped_tabs', []))
                else:
                    total_tabs = len(session_data.get('tabs', []))

                print(f"\nSession saved successfully!")
                print(f"  File: {session_file}")
                print(f"  Tabs: {total_tabs}")
            return True
        except Exception as e:
            if not quiet:
                print(f"Error saving session: {e}")
            return False

    def _parse_session_tabs(self, session_data, group_filter=None):
        """Parse tabs from session data, handling both old and new format.

        Args:
            session_data: The loaded JSON session data
            group_filter: Optional list of group names to filter

        Returns:
            List of tab dicts with order, url, title, and optionally group_name
        """
        tabs = []

        # Check if new format (with groups)
        if 'groups' in session_data:
            groups = session_data.get('groups', [])

            for group in groups:
                group_name = group.get('name', 'Unnamed')

                # Skip if group filter is set and this group not in filter
                if group_filter and group_name not in group_filter:
                    continue

                # Add tabs from this group
                group_tabs = group.get('tabs', [])
                for tab in group_tabs:
                    tab_copy = tab.copy()
                    tab_copy['group_name'] = group_name
                    tabs.append(tab_copy)

            # Also include ungrouped tabs (if no filter or if requested)
            ungrouped = session_data.get('ungrouped_tabs', [])
            if ungrouped and (not group_filter or 'ungrouped' in group_filter):
                for tab in ungrouped:
                    tab_copy = tab.copy()
                    tab_copy['group_name'] = 'Ungrouped'
                    tabs.append(tab_copy)

        # Old format (flat tabs array)
        elif 'tabs' in session_data:
            tabs = session_data.get('tabs', [])
            # Add group_name as 'Ungrouped' for backward compat
            for tab in tabs:
                tab['group_name'] = 'Ungrouped'

        return tabs

    def load_session(self, session_name: str, group_filter=None):
        """Load session from JSON file and open tabs in browser.

        Args:
            session_name: Name of the session to load
            group_filter: Optional list of group names to load (None = load all)
        """
        # Validate session name
        if not self._validate_session_name(session_name):
            print(f"Error: Invalid session name '{session_name}'")
            return False

        session_file = self.sessions_dir / f'{session_name}.json'

        # Check if session exists
        if not session_file.exists():
            print(f"Error: Session '{session_name}' not found")
            print(f"  Looking for: {session_file}")
            self._list_available_sessions()
            return False

        # Load session data
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in session file - {e}")
            return False
        except Exception as e:
            print(f"Error loading session: {e}")
            return False

        # Extract browser metadata (backward compatible)
        browser_type = session_data.get('browser_type', 'chrome')
        profile_name = session_data.get('profile_name')  # May be None
        incognito_mode = session_data.get('incognito_mode', False)

        # Parse tabs (handle both old and new format)
        tabs = self._parse_session_tabs(session_data, group_filter)

        if not tabs:
            print("Warning: Session contains no tabs" + (f" in selected groups" if group_filter else ""))
            return False

        print(f"\nLoading session: {session_name}")
        print(f"  Created: {session_data.get('created_at', 'Unknown')}")

        # Show profile info if available
        if profile_name:
            print(f"  Browser: {browser_type} (profile: {profile_name})")
        elif incognito_mode:
            print(f"  Browser: {browser_type} (incognito mode)")
        else:
            print(f"  Browser: {browser_type}")

        if group_filter:
            print(f"  Groups: {', '.join(group_filter)}")
        print(f"  Tabs: {len(tabs)}")

        # Launch browser if not already running
        if not self.browser:
            self.launch_browser(browser_type=browser_type, incognito_mode=incognito_mode, profile_name=profile_name)

        # Close the initial blank page if it exists
        if self.context.pages:
            try:
                if self.context.pages[0].url == 'about:blank':
                    self.context.pages[0].close()
            except Exception:
                pass

        # Open tabs in order, grouped by group_name
        print("\nOpening tabs...")
        current_group = None

        for tab in sorted(tabs, key=lambda x: (x.get('group_name', ''), x.get('order', 0))):
            url = tab.get('url', '')
            title = tab.get('title', 'Unknown')
            group_name = tab.get('group_name')

            # Print group header if changed
            if group_name and group_name != current_group:
                print(f"\n  Group: {group_name}")
                current_group = group_name

            if url and url != 'about:blank':
                try:
                    page = self.context.new_page()
                    page.goto(url, timeout=30000)
                    print(f"    {tab.get('order', '?')}. {title} - {url}")
                except Exception as e:
                    print(f"    Warning: Could not open {url} - {e}")

        print("\nSession loaded successfully!")
        return True

    def _validate_session_name(self, name: str) -> bool:
        """Validate session name for safety."""
        if not name:
            return False
        # Allow alphanumeric, dash, and underscore only
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        return all(c in allowed_chars for c in name)

    def _list_available_sessions(self):
        """List available saved sessions."""
        session_files = list(self.sessions_dir.glob('*.json'))
        if session_files:
            print("\nAvailable sessions:")
            for session_file in sorted(session_files):
                print(f"  - {session_file.stem}")
        else:
            print("\nNo saved sessions found")

    def list_groups(self, session_name: str):
        """List all groups in a session."""
        session_file = self.sessions_dir / f'{session_name}.json'

        if not session_file.exists():
            print(f"Error: Session '{session_name}' not found")
            return False

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return False

        print(f"\nGroups in session '{session_name}':")

        # Check for new format (groups)
        if 'groups' in session_data:
            groups = session_data.get('groups', [])
            for group in groups:
                group_name = group.get('name', 'Unnamed')
                tab_count = len(group.get('tabs', []))
                print(f"  - {group_name} ({tab_count} tabs)")

            # Also show ungrouped tabs if any
            ungrouped = session_data.get('ungrouped_tabs', [])
            if ungrouped:
                print(f"  - Ungrouped ({len(ungrouped)} tabs)")
        # Old format (flat tabs)
        elif 'tabs' in session_data:
            tabs = session_data.get('tabs', [])
            print(f"  - All tabs ({len(tabs)} tabs)")
            print("\n  Note: This session uses the old flat format (no groups)")

        return True

    def run_interactive(self):
        """Run browser and wait for user input to save."""
        # Only launch browser if not already running
        if not self.browser:
            self.launch_browser()

        print("\n" + "="*60)
        print("Browser is running. Open tabs as needed.")
        print("="*60)
        print("\nCommands:")
        print("  - Press Ctrl+C to exit without saving")
        print("  - Or close this terminal to keep browser open")
        print("="*60)

        try:
            # Keep the script running
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nExiting...")
            self.cleanup()

    def cleanup(self):
        """Clean up browser resources."""
        # Cancel any pending auto-save
        if self.auto_save_manager:
            self.auto_save_manager.cancel()

        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Browser Tab Session Manager - Track, save, and restore browser sessions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tab_session_manager.py new
  python tab_session_manager.py save my-research
  python tab_session_manager.py load my-research
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # New session command
    new_parser = subparsers.add_parser('new', help='Start a new browser session')
    new_parser.add_argument('--no-auto-save', action='store_true', help='Disable auto-save')
    new_parser.add_argument('--auto-save-interval', type=float, default=3.0, help='Auto-save interval in seconds (default: 3.0)')

    # Save session command
    save_parser = subparsers.add_parser('save', help='Save current session')
    save_parser.add_argument('name', help='Session name')

    # Load session command
    load_parser = subparsers.add_parser('load', help='Load saved session')
    load_parser.add_argument('name', help='Session name')
    load_parser.add_argument('--group', type=str, help='Load specific group only')
    load_parser.add_argument('--groups', type=str, help='Load multiple groups (comma-separated)')
    load_parser.add_argument('--no-auto-save', action='store_true', help='Disable auto-save')
    load_parser.add_argument('--auto-save-interval', type=float, default=3.0, help='Auto-save interval in seconds (default: 3.0)')

    # List sessions command
    subparsers.add_parser('list', help='List available sessions')

    # Groups command
    groups_parser = subparsers.add_parser('groups', help='List groups in a session')
    groups_parser.add_argument('name', help='Session name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Determine auto-save settings
    auto_save_enabled = True
    auto_save_interval = 3.0

    if hasattr(args, 'no_auto_save') and args.no_auto_save:
        auto_save_enabled = False

    if hasattr(args, 'auto_save_interval'):
        auto_save_interval = args.auto_save_interval

    manager = TabSessionManager(
        auto_save_enabled=auto_save_enabled,
        auto_save_interval=auto_save_interval
    )

    try:
        if args.command == 'new':
            if auto_save_enabled:
                print(f"Auto-save enabled (interval: {auto_save_interval}s)")
            else:
                print("Auto-save disabled")
            manager.run_interactive()

        elif args.command == 'save':
            # Connect to running browser and save session
            if manager.connect_to_browser():
                manager.save_session(args.name)
                manager.cleanup()
            else:
                print("\nFailed to connect to browser.")
                sys.exit(1)

        elif args.command == 'load':
            # Parse group filter
            group_filter = None
            if hasattr(args, 'group') and args.group:
                group_filter = [args.group]
            elif hasattr(args, 'groups') and args.groups:
                group_filter = [g.strip() for g in args.groups.split(',')]

            manager.load_session(args.name, group_filter=group_filter)
            manager.run_interactive()

        elif args.command == 'list':
            manager._list_available_sessions()

        elif args.command == 'groups':
            manager.list_groups(args.name)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.cleanup()


if __name__ == '__main__':
    main()
