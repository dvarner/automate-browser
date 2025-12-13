# Browser Automation with Python

Below are several browser automation tasks you can accomplish using Python:

## 1. Getting List of Open Browser Tabs

To get a list of tabs from browsers that are already running, you can use:

### **Option A: Selenium WebDriver** (Chrome/Edge/Firefox)

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Connect to existing Chrome instance (requires Chrome started with debugging port)
# Start Chrome with: chrome.exe --remote-debugging-port=9222
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

driver = webdriver.Chrome(options=options)

# Get all window handles
windows = driver.window_handles

tabs_info = []
for window in windows:
    driver.switch_to.window(window)
    tabs_info.append({
        'title': driver.title,
        'url': driver.current_url
    })

for i, tab in enumerate(tabs_info, 1):
    print(f"{i}. {tab['title']}")
    print(f"   URL: {tab['url']}\n")

# Don't close the driver if you want to keep the browser open
# driver.quit()
```

### **Option B: PyAutoGUI + Clipboard** (Less reliable)

```python
import pyautogui
import time
import pyperclip

# This approach uses keyboard shortcuts to copy URLs
# Works but is less reliable than Selenium

def get_chrome_tabs():
    # Focus on Chrome window
    # Press Ctrl+L to focus address bar
    # Press Ctrl+C to copy URL
    # Press Ctrl+Tab to move to next tab
    # Repeat
    pass  # Implementation depends on specific needs
```

### **Option C: Browser Extension + Local Server**

Create a browser extension that communicates with your Python script via a local web server or native messaging.

## 2. Opening Browser with Multiple Tabs and Tab Groups

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Configure Chrome options
options = Options()
# options.add_argument('--start-maximized')

driver = webdriver.Chrome(options=options)

# List of URLs to open
urls = [
    'https://www.google.com',
    'https://www.github.com',
    'https://www.stackoverflow.com',
    'https://www.reddit.com'
]

# Open first URL in current tab
driver.get(urls[0])

# Open remaining URLs in new tabs
for url in urls[1:]:
    driver.execute_script(f"window.open('{url}', '_blank');")
    time.sleep(0.5)  # Small delay to prevent overwhelming the browser

# Switch between tabs
all_tabs = driver.window_handles
driver.switch_to.window(all_tabs[1])  # Switch to second tab

# Note: Tab groups require Chrome extension or manual setup
# Selenium doesn't have native support for tab groups yet
# You can use Chrome DevTools Protocol (CDP) for more advanced features

# Using CDP to create tab groups (Chrome 88+)
driver.execute_cdp_cmd('Target.createTarget', {
    'url': 'https://www.example.com',
    'newWindow': False
})
```

## 3. Getting Content from a Webpage

### **Option A: BeautifulSoup (Static Content)**

```python
import requests
from bs4 import BeautifulSoup

url = 'https://example.com/article'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Get article title
title = soup.find('h1').get_text()

# Get article content (adjust selectors based on site structure)
article = soup.find('article')
paragraphs = article.find_all('p')
content = '\n\n'.join([p.get_text() for p in paragraphs])

print(f"Title: {title}\n")
print(f"Content:\n{content}")
```

### **Option B: Selenium (Dynamic Content)**

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get('https://example.com/article')

# Wait for content to load (for dynamic sites)
wait = WebDriverWait(driver, 10)
article = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'article')))

# Get title
title = driver.find_element(By.TAG_NAME, 'h1').text

# Get all paragraphs
paragraphs = driver.find_elements(By.CSS_SELECTOR, 'article p')
content = '\n\n'.join([p.text for p in paragraphs])

print(f"Title: {title}\n")
print(f"Content:\n{content}")

driver.quit()
```

### **Option C: Playwright (Modern Alternative)**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://example.com/article')

    # Get title
    title = page.locator('h1').text_content()

    # Get article content
    paragraphs = page.locator('article p').all()
    content = '\n\n'.join([p.text_content() for p in paragraphs])

    print(f"Title: {title}\n")
    print(f"Content:\n{content}")

    browser.close()
```

### **Option D: Newspaper3k (Specifically for Articles)**

```python
from newspaper import Article

url = 'https://example.com/article'
article = Article(url)
article.download()
article.parse()

print(f"Title: {article.title}")
print(f"Authors: {article.authors}")
print(f"Publish Date: {article.publish_date}")
print(f"\nContent:\n{article.text}")

# Optional: NLP features
article.nlp()
print(f"\nKeywords: {article.keywords}")
print(f"Summary: {article.summary}")
```

## Installation Requirements

```bash
# Selenium
pip install selenium webdriver-manager

# BeautifulSoup
pip install beautifulsoup4 requests

# Playwright
pip install playwright
playwright install

# Newspaper3k
pip install newspaper3k lxml_html_clean

# PyAutoGUI (if needed)
pip install pyautogui pyperclip
```

## Tips for Browser Automation

1. **For connecting to existing Chrome instance**: Start Chrome with debugging port:
   ```bash
   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/chrome-dev-session"
   ```

2. **Headless mode**: Add `options.add_argument('--headless')` to run without GUI

3. **User agent**: Customize user agent to avoid detection:
   ```python
   options.add_argument('user-agent=Mozilla/5.0 ...')
   ```

4. **Handling dynamic content**: Use explicit waits instead of `time.sleep()`

5. **Error handling**: Always use try-except blocks and proper cleanup

## Example: Complete Workflow

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
from datetime import datetime

def automate_browser_tasks():
    options = Options()
    driver = webdriver.Chrome(options=options)

    try:
        # Task 1: Open multiple tabs
        urls = [
            'https://news.ycombinator.com',
            'https://github.com/trending',
            'https://stackoverflow.com/questions'
        ]

        for i, url in enumerate(urls):
            if i == 0:
                driver.get(url)
            else:
                driver.execute_script(f"window.open('{url}', '_blank');")

        # Task 2: Get list of all tabs
        tabs_info = []
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            tabs_info.append({
                'title': driver.title,
                'url': driver.current_url
            })

        # Task 3: Extract content from first tab
        driver.switch_to.window(driver.window_handles[0])
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'tabs': tabs_info,
            'page_title': driver.title
        }

        with open('browser_automation_log.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Opened {len(tabs_info)} tabs")
        for i, tab in enumerate(tabs_info, 1):
            print(f"{i}. {tab['title']}")

    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == '__main__':
    automate_browser_tasks()
```

## Next Steps

1. Choose the appropriate library based on your needs (Selenium for full control, BeautifulSoup for simple scraping, Playwright for modern features)
2. Install required dependencies
3. Test with simple examples first
4. Build more complex automation workflows
5. Consider error handling, rate limiting, and ethical scraping practices
