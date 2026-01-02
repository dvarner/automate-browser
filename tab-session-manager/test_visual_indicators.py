#!/usr/bin/env python3
"""
Test script to verify visual indicators appear correctly
"""

from playwright.sync_api import sync_playwright
import time

def test_visual_indicators():
    """Test that visual indicators appear correctly"""
    print("=" * 70)
    print("Visual Indicators Test")
    print("=" * 70)

    results = []

    # Test configurations
    test_configs = [
        {'browser': 'chrome', 'incognito': False, 'profile': None, 'name': 'Chrome Normal'},
        {'browser': 'chrome', 'incognito': True, 'profile': None, 'name': 'Chrome Incognito'},
    ]

    for config in test_configs:
        print(f"\n[*] Testing: {config['name']}")
        print("-" * 70)

        try:
            playwright = sync_playwright().start()

            # Launch browser with incognito flag
            launch_args = ['--remote-debugging-port=9222', '--disable-blink-features=AutomationControlled']
            if config['incognito']:
                launch_args.append('--incognito')

            browser = playwright.chromium.launch(
                headless=False,
                args=launch_args,
                channel='chrome' if config['browser'] == 'chrome' else None
            )

            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                no_viewport=True
            )

            # Build indicator script
            browser_name = config['browser'].upper()
            mode_text = "INCOGNITO" if config['incognito'] else "NORMAL"
            bg_color = "#424242" if config['incognito'] else "#4285F4"

            indicator_script = f"""
            (() => {{
                const banner = document.createElement('div');
                banner.id = 'session-indicator-banner';
                banner.innerHTML = `
                    <div style="
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        background: {bg_color};
                        color: white;
                        padding: 8px 16px;
                        font-family: Arial, sans-serif;
                        font-size: 13px;
                        font-weight: 600;
                        z-index: 2147483647;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    ">
                        🌐 {browser_name} | {mode_text}
                    </div>
                `;

                if (document.body) {{
                    document.body.appendChild(banner);
                }} else {{
                    document.addEventListener('DOMContentLoaded', () => {{
                        document.body.appendChild(banner);
                    }});
                }}
            }})();
            """

            # Inject indicator script on all pages
            context.add_init_script(indicator_script)

            # Create start page
            page = context.new_page()

            mode_icon = "🔒" if config['incognito'] else "📂"
            mode_badge_color = "#424242" if config['incognito'] else "#2E7D32"

            start_page_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Session Info - {browser_name}</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                    }}
                    .container {{
                        background: white;
                        border-radius: 20px;
                        padding: 50px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        max-width: 600px;
                        text-align: center;
                    }}
                    h1 {{ font-size: 36px; color: {bg_color}; margin: 20px 0; }}
                    .mode-badge {{
                        background: {mode_badge_color};
                        color: white;
                        padding: 12px 24px;
                        border-radius: 25px;
                        font-weight: bold;
                        display: inline-block;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div style="font-size: 80px;">🌐</div>
                    <h1>{browser_name}</h1>
                    <div class="mode-badge">{mode_icon} {mode_text} MODE</div>
                    <p style="margin-top: 20px; color: #666;">
                        Visual indicators are working!
                    </p>
                </div>
            </body>
            </html>
            """

            page.set_content(start_page_html)

            print(f"[+] Browser launched: {config['name']}")
            print(f"   - Start page: Custom session info page")
            print(f"   - Banner color: {'Dark Gray' if config['incognito'] else 'Blue'}")
            print(f"   - Mode: {mode_text}")

            # Wait a bit to see the page
            time.sleep(3)

            # Test banner on a real website
            print(f"   - Testing banner on google.com...")
            page2 = context.new_page()
            page2.goto('https://www.google.com', timeout=10000)

            # Check if banner exists
            banner_exists = page2.evaluate("!!document.getElementById('session-indicator-banner')")

            if banner_exists:
                print(f"   [+] Banner injected successfully on google.com")
                results.append(('PASS', config['name'], 'Banner appears on websites'))
            else:
                print(f"   [-] Banner NOT found on google.com")
                results.append(('FAIL', config['name'], 'Banner not injected'))

            time.sleep(2)

            # Cleanup
            browser.close()
            playwright.stop()

            results.append(('PASS', config['name'], 'Visual indicators working'))

        except Exception as e:
            print(f"   [-] Error: {e}")
            results.append(('FAIL', config['name'], str(e)))

    # Print summary
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)

    for status, test_name, detail in results:
        icon = "[+]" if status == "PASS" else "[-]"
        print(f"{icon} {test_name}: {detail}")

    passed = sum(1 for r in results if r[0] == 'PASS')
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    return passed == total


if __name__ == '__main__':
    success = test_visual_indicators()
    exit(0 if success else 1)
