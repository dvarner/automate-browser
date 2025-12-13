#!/usr/bin/env python3
"""
Quick browser test to diagnose connection issues
"""

from playwright.sync_api import sync_playwright
import time

print("Testing Playwright browser...")
print("=" * 60)

try:
    with sync_playwright() as p:
        print("\n1. Launching browser...")
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--remote-debugging-port=9222',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
            ]
        )

        print("✓ Browser launched")

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        print("\n2. Creating new page...")
        page = context.new_page()
        print("✓ Page created")

        print("\n3. Testing navigation to google.com...")
        try:
            page.goto('https://www.google.com', timeout=15000)
            print(f"✓ Successfully loaded: {page.title()}")
        except Exception as e:
            print(f"✗ Failed to load google.com: {e}")

        print("\n4. Testing navigation to example.com...")
        try:
            page.goto('https://example.com', timeout=15000)
            print(f"✓ Successfully loaded: {page.title()}")
        except Exception as e:
            print(f"✗ Failed to load example.com: {e}")

        print("\n5. Browser will close in 5 seconds...")
        time.sleep(5)

        browser.close()
        print("✓ Test complete!")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("If pages failed to load, you may have network/proxy issues.")
print("Check your firewall, proxy settings, or antivirus software.")
