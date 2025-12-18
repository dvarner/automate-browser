# YAML Workflow Engine for Browser Automation

A simple, powerful workflow automation system using YAML configuration files. No coding required for basic automation tasks!

## Features

- ✅ **YAML-based workflows** - Write automation in simple, readable YAML files
- 🌐 **Multi-browser support** - Chrome, Firefox, Chromium, WebKit
- 👤 **Human-in-the-loop** - Pause for logins, CAPTCHAs, and manual tasks
- 📊 **Data extraction** - Scrape tables and data from pages
- 💾 **CSV export** - Save extracted data to CSV files
- 📸 **Screenshots** - Capture page states
- ⚡ **Fast and simple** - No complex GUI, just edit YAML files

## Installation

### Prerequisites

```bash
# Install Python dependencies
pip install playwright pyyaml

# Install Playwright browsers
playwright install
```

## Quick Start

### 1. Create a Workflow File

Create a YAML file in `workflows/` folder:

```yaml
# workflows/my-workflow.yaml
name: "My First Workflow"
browser: "chrome"
timeout: 30

steps:
  - action: navigate
    url: "https://example.com"

  - action: fill
    selector: "#search"
    value: "search query"

  - action: click
    selector: "#submit-btn"

  - action: wait
    selector: ".results"

  - action: screenshot
    file: "results.png"
```

### 2. Run the Workflow

```bash
# From workflow-engine directory
python workflow_runner.py workflows/my-workflow.yaml

# Run in headless mode
python workflow_runner.py workflows/my-workflow.yaml --headless

# Use different browser
python workflow_runner.py workflows/my-workflow.yaml --browser firefox
```

## Available Actions

### Navigation

#### `navigate`
Navigate to a URL

```yaml
- action: navigate
  url: "https://example.com"
```

#### `wait`
Wait for element or time

```yaml
# Wait for element
- action: wait
  selector: ".loading"
  timeout: 30

# Wait for time
- action: wait
  seconds: 5
```

### Interaction

#### `click`
Click an element

```yaml
- action: click
  selector: "button#submit"
  wait: true           # Wait for element first (default: true)
  wait_after: 2        # Wait seconds after click (optional)
```

#### `fill`
Fill a form field

```yaml
- action: fill
  selector: "#email"
  value: "user@example.com"
  clear: true          # Clear field first (default: true)
  press_enter: false   # Press Enter after fill (default: false)
  sensitive: false     # Hide value in logs (default: false)
```

### Data Extraction

#### `extract`
Extract single value

```yaml
- action: extract
  name: "price"          # Name to store in data_store
  selector: ".price"
  attribute: "text"      # text, href, src, etc. (default: text)
```

#### `extract_table`
Extract table/list data

```yaml
- action: extract_table
  name: "products"
  rows: ".product-item"  # Selector for each row
  columns:
    title: "h2"          # Column name: selector
    price: ".price"
    rating: ".stars"
```

### Human Interaction

#### `wait_for_human`
Pause workflow for human interaction

```yaml
# Wait for manual ENTER
- action: wait_for_human
  reason: "Please complete CAPTCHA"
  timeout: 300

# Auto-continue when element appears
- action: wait_for_human
  reason: "Please log in"
  continue_selector: "#dashboard"
  timeout: 120

# Auto-continue when URL changes
- action: wait_for_human
  reason: "Complete login"
  continue_url: "/dashboard"
  timeout: 120
```

### Utility

#### `screenshot`
Take a screenshot

```yaml
- action: screenshot
  file: "my-screenshot.png"
  full_page: false  # Capture full page (default: false)
```

#### `save_csv`
Save extracted data to CSV

```yaml
- action: save_csv
  data: "products"     # Name from extract/extract_table
  file: "products.csv"
```

#### `conditional`
Conditional logic (basic)

```yaml
- action: conditional
  element_exists: ".error-message"

# Or check if data exists
- action: conditional
  data_exists: "products"
```

## Workflow Configuration

### Basic Structure

```yaml
name: "Workflow Name"           # Required: Workflow description
browser: "chrome"                # Optional: chrome, firefox, chromium (default: chromium)
timeout: 30                      # Optional: Default timeout in seconds (default: 30)

steps:                           # Required: List of actions
  - action: navigate
    url: "https://example.com"
```

### Browser Options

- `chrome` - Google Chrome
- `brave` - Brave Browser
- `firefox` - Firefox
- `chromium` - Chromium
- `webkit` - WebKit (Safari)

### Error Handling

Add `continue_on_error: true` to any step to continue even if it fails:

```yaml
- action: click
  selector: ".optional-button"
  continue_on_error: true
```

## Example Workflows

### Example 1: Google Search

```yaml
name: "Google Search"
browser: "chrome"

steps:
  - action: navigate
    url: "https://www.google.com"

  - action: fill
    selector: "textarea[name='q']"
    value: "Playwright automation"
    press_enter: true

  - action: wait
    selector: "#search"

  - action: extract_table
    name: "results"
    rows: "#search .g"
    columns:
      title: "h3"
      snippet: ".VwiC3b"

  - action: save_csv
    data: "results"
    file: "search-results.csv"
```

### Example 2: Login with CAPTCHA

```yaml
name: "Login Flow"
browser: "chrome"

steps:
  - action: navigate
    url: "https://example.com/login"

  - action: wait_for_human
    reason: "Please solve CAPTCHA if present"
    continue_selector: "#username"

  - action: fill
    selector: "#username"
    value: "user@example.com"

  - action: fill
    selector: "#password"
    value: "password123"
    sensitive: true

  - action: click
    selector: "button[type='submit']"

  - action: wait
    selector: ".dashboard"
```

### Example 3: Data Scraping

```yaml
name: "Product Scraper"
browser: "chrome"

steps:
  - action: navigate
    url: "https://example.com/products"

  - action: wait
    selector: ".product-grid"

  - action: extract_table
    name: "products"
    rows: ".product-card"
    columns:
      name: ".product-title"
      price: ".product-price"
      rating: ".rating-value"
      url: "a"

  - action: save_csv
    data: "products"
    file: "products.csv"

  - action: screenshot
    file: "products-page.png"
```

## Data Flow

Extracted data is stored in a `data_store` dictionary that persists across steps:

```yaml
# Step 1: Extract data
- action: extract
  name: "username"
  selector: ".profile-name"

# Step 2: Extract table
- action: extract_table
  name: "orders"
  rows: ".order-row"
  columns:
    id: ".order-id"
    total: ".order-total"

# Step 3: Save to CSV
- action: save_csv
  data: "orders"
  file: "my-orders.csv"
```

## Output

- **Screenshots**: Saved to `workflow-engine/results/`
- **CSV files**: Saved to `workflow-engine/results/`
- **Logs**: Printed to console in real-time

## Tips & Best Practices

1. **Start simple** - Test with basic navigation first, then add complexity
2. **Use descriptive names** - Name your workflows and data clearly
3. **Add wait steps** - Pages need time to load; don't rush
4. **Human-in-loop for auth** - Use `wait_for_human` for logins and CAPTCHAs
5. **Test selectors** - Use browser DevTools to verify CSS selectors
6. **Error handling** - Use `continue_on_error` for optional steps
7. **Screenshots for debugging** - Add screenshots to see what went wrong

## Troubleshooting

### "Element not found" errors
- Check CSS selector in browser DevTools
- Add `wait` step before interacting with element
- Increase timeout value

### Workflow hangs
- Check if `wait_for_human` is waiting for input
- Verify selectors are correct
- Check browser console for JavaScript errors

### Data not extracted
- Verify row and column selectors
- Check if page has loaded completely
- Use screenshot to see page state

## Next Steps

- ✅ **YAML workflows** - Done!
- 🔄 **Playwright codegen converter** - Coming next
- 📹 **Chrome extension recorder** - Coming soon

## Examples

See `workflows/` folder for complete examples:
- `example-google-search.yaml` - Simple search and data extraction
- `example-login-flow.yaml` - Login with human interaction
- `example-form-submission.yaml` - Form filling with CAPTCHA handling
