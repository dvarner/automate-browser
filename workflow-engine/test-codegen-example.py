"""
Example Playwright codegen output
This is what Playwright generates when you record browser actions
"""

from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Navigate to Google
    page.goto("https://www.google.com/")

    # Fill search box
    page.fill("textarea[name='q']", "playwright automation")

    # Click search button
    page.click("input[value='Google Search']")

    # Wait for results
    page.wait_for_selector("#search")

    # Take screenshot
    page.screenshot(path="google-results.png")

    # Close
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
