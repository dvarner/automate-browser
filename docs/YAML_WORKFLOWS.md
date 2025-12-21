# Running YAML Workflow Automations

This guide explains how to run and create YAML-based browser automation workflows.

## Quick Start

```bash
# Navigate to the workflow-engine directory
cd workflow-engine

# Run a workflow
python workflow_runner.py workflows/test-simple.yaml

# Run in headless mode (no browser window)
python workflow_runner.py workflows/my-workflow.yaml --headless

# Use a specific browser
python workflow_runner.py workflows/my-workflow.yaml --browser chrome
```

## Installation

If you haven't set up the workflow engine yet:

```bash
pip install playwright pyyaml
playwright install
```

## Command-Line Options

- `--headless` - Run without visible browser window
- `--browser chrome|firefox|chromium|webkit` - Choose browser (default: chromium)

## Available Workflows

Current workflows in the `workflow-engine/workflows/` directory:

- `test-all-downloads.yaml` - Test all download functionality
- `test-download-direct.yaml` - Test direct downloads
- `test-downloads.yaml` - Download testing suite
- `test-simple-download.yaml` - Simple download example
- `example-google-search.yaml` - Search Google and extract results
- `example-login-flow.yaml` - Login flow with human interaction
- `example-form-submission.yaml` - Form filling with CAPTCHA handling

## Example Usage

```bash
cd workflow-engine

# Run a simple download test
python workflow_runner.py workflows/test-simple-download.yaml

# Run with Chrome in headless mode
python workflow_runner.py workflows/test-downloads.yaml --browser chrome --headless
```

## Output Location

All workflow results are saved to `workflow-engine/results/`:
- Screenshots (`.png`)
- Downloaded files (PDFs, images, videos)
- Exported data (`.csv`)

## Creating New Workflows

### Basic Workflow Structure

Create a YAML file in the `workflows/` folder:

```yaml
name: "My Workflow"
browser: "chrome"  # chrome, firefox, chromium, webkit
timeout: 30

steps:
  - action: navigate
    url: "https://example.com"

  - action: click
    selector: "#button"

  - action: screenshot
    file: "result.png"
```

### Available Actions

**Navigation:**
- `navigate` - Go to URL
- `wait` - Wait for element or time

**Interaction:**
- `click` - Click element
- `fill` - Fill form field

**Data Extraction:**
- `extract` - Extract single value
- `extract_table` - Extract table/list data

**Human Interaction:**
- `wait_for_human` - Pause for manual action (login, CAPTCHA)

**Downloads:**
- `download` - Click and download file
- `download_link` - Download from link
- `download_media` - Download image/video

**Utility:**
- `screenshot` - Take screenshot
- `save_csv` - Export extracted data
- `conditional` - Conditional logic

### Example Workflow

```yaml
name: "Extract Product Data"
browser: "chrome"
timeout: 30

steps:
  - action: navigate
    url: "https://example-store.com/products"

  - action: wait
    selector: ".product-list"

  - action: extract_table
    selector: ".product-item"
    fields:
      - name: "title"
        selector: ".product-title"
      - name: "price"
        selector: ".product-price"
    save_to: "products"

  - action: save_csv
    data: "products"
    file: "products.csv"

  - action: screenshot
    file: "products-page.png"
```

## Recording Workflows with Playwright Codegen

You can record browser actions and convert them to YAML:

```bash
# Record browser actions
playwright codegen -o recorded.py https://example.com

# Convert to YAML
python codegen_converter.py recorded.py -o workflows/my-workflow.yaml

# Run the converted workflow
python workflow_runner.py workflows/my-workflow.yaml
```

## Advanced Features

### Human-in-the-Loop

For workflows requiring manual interaction (CAPTCHAs, logins):

```yaml
steps:
  - action: navigate
    url: "https://site-with-captcha.com/login"

  - action: fill
    selector: "#username"
    value: "myuser"

  - action: fill
    selector: "#password"
    value: "mypass"

  - action: wait_for_human
    message: "Please solve the CAPTCHA and click login"
    timeout: 300

  - action: wait
    selector: ".dashboard"
```

### Error Handling

Continue execution even if a step fails:

```yaml
steps:
  - action: click
    selector: "#optional-button"
    continue_on_error: true

  - action: navigate
    url: "https://next-page.com"
```

### Conditional Logic

Execute steps based on conditions:

```yaml
steps:
  - action: conditional
    condition: "element_exists"
    selector: "#cookie-banner"
    then:
      - action: click
        selector: "#accept-cookies"
```

## Supported Browsers

- **Chrome** - Google Chrome
- **Firefox** - Mozilla Firefox
- **Chromium** - Open-source Chromium (default)
- **WebKit** - Safari engine

## Troubleshooting

### Workflow fails to start
- Ensure Playwright is installed: `pip install playwright`
- Install browsers: `playwright install`

### Element not found
- Increase timeout in workflow config
- Verify selector using browser DevTools
- Add `wait` step before interaction

### Downloads not working
- Check `results/` folder permissions
- Ensure download URL is accessible
- Verify file type is supported

## Documentation References

For more detailed information:

- **workflow-engine/README.md** - Complete reference with all actions and options
- **workflow-engine/QUICKSTART.md** - Quick examples and common patterns
- **workflow-engine/CODEGEN_GUIDE.md** - Recording workflows guide

## Example: Complete Workflow

Here's a complete example that demonstrates multiple features:

```yaml
name: "Research Paper Downloader"
browser: "chrome"
timeout: 60

steps:
  - action: navigate
    url: "https://arxiv.org"

  - action: fill
    selector: 'input[name="query"]'
    value: "machine learning"

  - action: click
    selector: 'button[type="submit"]'

  - action: wait
    selector: ".arxiv-result"

  - action: extract_table
    selector: ".arxiv-result"
    fields:
      - name: "title"
        selector: ".title"
      - name: "authors"
        selector: ".authors"
      - name: "pdf_link"
        selector: '.pdf a'
        attribute: "href"
    save_to: "papers"

  - action: save_csv
    data: "papers"
    file: "arxiv-results.csv"

  - action: screenshot
    file: "search-results.png"

  - action: download_link
    url: "{{ papers[0].pdf_link }}"
    filename: "first-paper.pdf"
```

Run this workflow with:
```bash
python workflow_runner.py workflows/research-downloader.yaml
```

Results will be saved to `workflow-engine/results/`:
- `arxiv-results.csv` - Extracted paper data
- `search-results.png` - Screenshot of results page
- `first-paper.pdf` - Downloaded paper
