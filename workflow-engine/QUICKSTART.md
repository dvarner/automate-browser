# Quick Start Guide

## Installation

```bash
# Install dependencies (if not already installed)
pip install playwright pyyaml
playwright install
```

## Run Your First Workflow

```bash
# From workflow-engine directory
python workflow_runner.py workflows/test-simple.yaml

# Run in headless mode (no browser window)
python workflow_runner.py workflows/test-simple.yaml --headless

# Use Chrome instead of Chromium
python workflow_runner.py workflows/test-simple.yaml --browser chrome
```

## Create Your Own Workflow

1. Create a new YAML file in `workflows/` folder:

```yaml
# workflows/my-automation.yaml
name: "My Automation"
browser: "chrome"
timeout: 30

steps:
  - action: navigate
    url: "https://example.com"

  - action: screenshot
    file: "my-screenshot.png"
```

2. Run it:

```bash
python workflow_runner.py workflows/my-automation.yaml
```

## Common Actions

### Navigate to URL
```yaml
- action: navigate
  url: "https://example.com"
```

### Click a button
```yaml
- action: click
  selector: "#submit-button"
```

### Fill a form
```yaml
- action: fill
  selector: "#email"
  value: "user@example.com"
```

### Wait for human (login, CAPTCHA)
```yaml
- action: wait_for_human
  reason: "Please log in"
  continue_selector: "#dashboard"
```

### Extract data
```yaml
- action: extract_table
  name: "products"
  rows: ".product-item"
  columns:
    title: "h2"
    price: ".price"
```

### Save to CSV
```yaml
- action: save_csv
  data: "products"
  file: "products.csv"
```

## See Examples

Check `workflows/` folder for complete examples:
- `example-google-search.yaml` - Search and extract data
- `example-login-flow.yaml` - Login with human interaction
- `example-form-submission.yaml` - Form filling with CAPTCHA

## Full Documentation

See `README.md` for complete action reference and advanced features.
