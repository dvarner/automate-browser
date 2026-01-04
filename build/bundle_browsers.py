"""
Bundle Playwright Browser Binaries Post-Build Script

This script copies Playwright browser binaries from the system cache
into the dist folder after PyInstaller builds the executable.

Usage:
    python bundle_browsers.py

Run this after: pyinstaller browser_automation.spec
"""

import sys
import shutil
import os
from pathlib import Path


def get_playwright_browsers_path():
    """Find the Playwright browsers directory"""

    try:
        import playwright
    except ImportError:
        print("[!] Error: playwright module not found")
        print("    Install with: pip install playwright")
        return None

    try:
        # Playwright browsers are stored in user's local AppData
        # Typical path: C:\Users\<user>\AppData\Local\ms-playwright
        home = Path.home()

        # Try common locations
        possible_paths = [
            home / 'AppData' / 'Local' / 'ms-playwright',  # Windows
            home / 'Library' / 'Caches' / 'ms-playwright',  # macOS
            home / '.cache' / 'ms-playwright',  # Linux
        ]

        for browsers_path in possible_paths:
            if browsers_path.exists():
                print(f"[*] Found browsers at: {browsers_path}")
                return browsers_path

        print(f"[!] Browsers not found in standard locations")
        print(f"    Searched: {[str(p) for p in possible_paths]}")
        return None

    except Exception as e:
        print(f"[!] Error finding Playwright browsers: {e}")
        return None


def get_dist_path():
    """Get the dist/BrowserAutomation folder path"""

    # Check current directory
    dist_path = Path('dist/BrowserAutomation')

    if not dist_path.exists():
        print(f"[!] Dist folder not found: {dist_path}")
        print("    Make sure you run this from the build/ directory")
        print("    And run PyInstaller first: pyinstaller browser_automation.spec")
        return None

    return dist_path


def copy_browsers(src, dest):
    """Copy browser binaries to dist folder"""

    print(f"\n[*] Copying browsers from:")
    print(f"    {src}")
    print(f"[*] To:")
    print(f"    {dest}")

    # Create destination directory
    dest.mkdir(parents=True, exist_ok=True)

    # Get list of browsers
    browsers = [d for d in src.iterdir() if d.is_dir()]
    print(f"\n[*] Found {len(browsers)} browser(s):")

    total_size = 0

    for browser_dir in browsers:
        browser_name = browser_dir.name
        print(f"    - {browser_name}", end=" ... ")

        dest_browser = dest / browser_name

        try:
            # Copy browser directory
            if dest_browser.exists():
                shutil.rmtree(dest_browser)

            shutil.copytree(browser_dir, dest_browser)

            # Calculate size
            size = sum(f.stat().st_size for f in dest_browser.rglob('*') if f.is_file())
            size_mb = size / (1024 * 1024)
            total_size += size_mb

            print(f"+ ({size_mb:.1f} MB)")

        except Exception as e:
            print(f"! Error: {e}")
            return False

    print(f"\n[+] Total browsers size: {total_size:.1f} MB")
    return True


def verify_bundled_browsers(dist_path):
    """Verify that browsers were bundled correctly"""

    playwright_browsers = dist_path / 'playwright' / 'browsers'

    if not playwright_browsers.exists():
        print("\n[!] Warning: playwright/browsers folder not found in dist")
        return False

    browsers = list(playwright_browsers.iterdir())
    if not browsers:
        print("\n[!] Warning: No browsers found in dist/playwright/browsers")
        return False

    print(f"\n[+] Verification: {len(browsers)} browser(s) bundled successfully")
    for browser in browsers:
        if browser.is_dir():
            print(f"    + {browser.name}")

    return True


def main():
    """Main bundling process"""

    print("=" * 60)
    print("  Playwright Browser Bundling Script")
    print("=" * 60)

    # Step 1: Find Playwright browsers
    print("\n[1/4] Locating Playwright browsers...")
    browsers_path = get_playwright_browsers_path()

    if not browsers_path:
        print("\n[!] ERROR: Could not find Playwright browsers")
        print("\n[*] To install browsers, run:")
        print("    python -m playwright install")
        sys.exit(1)

    # Step 2: Find dist folder
    print("\n[2/4] Locating dist folder...")
    dist_path = get_dist_path()

    if not dist_path:
        print("\n[!] ERROR: Dist folder not found")
        sys.exit(1)

    print(f"[+] Found: {dist_path}")

    # Step 3: Copy browsers
    print("\n[3/4] Bundling browsers...")
    dest_path = dist_path / 'playwright' / 'browsers'

    success = copy_browsers(browsers_path, dest_path)

    if not success:
        print("\n[!] ERROR: Failed to copy browsers")
        sys.exit(1)

    # Step 4: Verify
    print("\n[4/4] Verifying bundled browsers...")
    if verify_bundled_browsers(dist_path):
        print("\n" + "=" * 60)
        print("  + Browser bundling complete!")
        print("=" * 60)
        print(f"\n[*] Browsers location: {dest_path}")
        print("[*] Executable is now self-contained and works offline")
    else:
        print("\n[!] ERROR: Verification failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
