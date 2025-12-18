# Playwright Codegen to YAML Converter Guide

Record browser actions using Playwright's codegen, then convert to YAML workflows automatically!

## Quick Workflow

### 1. Record Actions with Playwright Codegen

```bash
# Record browser interactions
playwright codegen https://example.com

# Record and save to file
playwright codegen --target python -o recorded.py https://example.com

# Record with specific browser
playwright codegen --browser chromium https://example.com
playwright codegen --browser firefox https://example.com
```

**What happens:**
- Browser window opens
- Your actions are recorded (clicks, form fills, navigation)
- Python code is generated
- Code is saved to `recorded.py`

### 2. Convert to YAML

```bash
# Convert the recorded file
python codegen_converter.py recorded.py

# Specify output file
python codegen_converter.py recorded.py -o workflows/my-workflow.yaml

# Set workflow name
python codegen_converter.py recorded.py --name "My Workflow" --browser chrome
```

### 3. Run Your Workflow

```bash
# Run the converted workflow
python workflow_runner.py workflows/my-workflow.yaml
```

## Complete Example

### Step 1: Record

```bash
playwright codegen --target python -o google-search.py https://www.google.com
```

**Do these actions in the browser:**
1. Type "playwright automation" in search box
2. Click "Google Search" button
3. Wait for results

**Close the browser** when done.

### Step 2: Check Generated Code

`google-search.py` will contain:
```python
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.google.com/")
    page.fill("textarea[name='q']", "playwright automation")
    page.click("input[value='Google Search']")
    page.wait_for_selector("#search")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
```

### Step 3: Convert to YAML

```bash
python codegen_converter.py google-search.py -o workflows/google-search.yaml
```

**Output: `workflows/google-search.yaml`**
```yaml
# Auto-generated from Playwright codegen
# Review and edit as needed:
#   - Update workflow name
#   - Add wait_for_human steps for logins/CAPTCHAs
#   - Add extract/extract_table for data scraping
#   - Convert role/text selectors to CSS selectors

name: Generated Workflow
browser: chromium
timeout: 30
steps:
- action: navigate
  url: https://www.google.com/
- action: fill
  selector: textarea[name='q']
  value: playwright automation
- action: click
  selector: input[value='Google Search']
- action: wait
  selector: '#search'
```

### Step 4: Edit YAML (Add Enhancements)

Edit `workflows/google-search.yaml`:
```yaml
name: Google Search Workflow
browser: chrome
timeout: 30

steps:
  - action: navigate
    url: https://www.google.com/

  - action: fill
    selector: textarea[name='q']
    value: playwright automation

  - action: click
    selector: input[value='Google Search']

  - action: wait
    selector: '#search'

  # ADD: Extract search results
  - action: extract_table
    name: results
    rows: '#search .g'
    columns:
      title: h3
      snippet: .VwiC3b

  # ADD: Save to CSV
  - action: save_csv
    data: results
    file: search-results.csv

  # ADD: Take screenshot
  - action: screenshot
    file: google-results.png
```

### Step 5: Run Workflow

```bash
python workflow_runner.py workflows/google-search.yaml
```

## Supported Playwright Actions

| Playwright Code | YAML Action |
|----------------|-------------|
| `page.goto("url")` | `navigate` |
| `page.click("selector")` | `click` |
| `page.fill("selector", "value")` | `fill` |
| `page.press("selector", "Enter")` | `fill` with `press_enter: true` |
| `page.wait_for_selector("selector")` | `wait` |
| `page.screenshot(path="file.png")` | `screenshot` |
| `page.locator("selector").click()` | `click` |
| `page.get_by_placeholder("text").fill("val")` | `fill` |

## Advanced: Direct Pipe from Codegen

```bash
# Record and convert in one command
playwright codegen https://example.com 2>&1 | python codegen_converter.py --stdin -o workflows/example.yaml
```

## Tips

### 1. Record Clean Actions
- Don't make mistakes while recording (or delete bad lines)
- Be deliberate with clicks and form fills
- Wait for pages to load before interacting

### 2. Edit After Conversion
The converter creates a basic workflow. You should add:
- **Workflow name**: Change "Generated Workflow" to something descriptive
- **Human interaction**: Add `wait_for_human` for logins, CAPTCHAs
- **Data extraction**: Add `extract` or `extract_table` steps
- **Error handling**: Add `continue_on_error` for optional steps
- **Waits**: Add explicit `wait` steps if needed

### 3. Selector Compatibility
Playwright codegen may generate role-based or text-based selectors:
- `page.get_by_role("button", name="Submit")` → Convert to CSS selector
- `page.get_by_text("Login")` → Convert to CSS selector

The converter adds comments when manual editing is needed.

### 4. Handle Complex Flows
For login flows or multi-page workflows:
```yaml
# After conversion, add human interaction
- action: wait_for_human
  reason: "Please log in if needed"
  continue_selector: "#dashboard"
  timeout: 120
```

## Example: Login Flow Recording

### 1. Record
```bash
playwright codegen --target python -o login-flow.py https://example.com/login
```

**Actions in browser:**
1. Navigate to login page
2. Click username field
3. Type username
4. Click password field
5. Type password
6. Click submit button

### 2. Convert
```bash
python codegen_converter.py login-flow.py -o workflows/login-flow.yaml --name "Login Flow"
```

### 3. Edit (Add Human Interaction)
```yaml
name: Login Flow
browser: chrome
timeout: 30

steps:
  - action: navigate
    url: https://example.com/login

  # ADD: Wait for CAPTCHA
  - action: wait_for_human
    reason: "Please solve CAPTCHA if present"
    continue_selector: "#username"

  - action: fill
    selector: "#username"
    value: "your-username"

  - action: fill
    selector: "#password"
    value: "your-password"
    sensitive: true  # ADD: Hide in logs

  - action: click
    selector: "button[type='submit']"

  # ADD: Wait for successful login
  - action: wait
    selector: ".dashboard"

  # ADD: Screenshot confirmation
  - action: screenshot
    file: "logged-in.png"
```

## Troubleshooting

### Converter doesn't recognize action
- Check if the Playwright code uses supported methods
- Some advanced Playwright features may not convert automatically
- Manually add the step to YAML

### Selectors don't work
- Playwright codegen may generate fragile selectors
- Test and update selectors manually
- Use browser DevTools to find better selectors

### Missing actions in conversion
- Ensure input file has valid Playwright code
- Check for syntax errors in recorded file
- Some boilerplate code (imports, browser setup) is ignored

## Next Steps

After converting:
1. ✅ Review generated YAML
2. ✅ Add workflow name and description
3. ✅ Insert `wait_for_human` for auth/CAPTCHAs
4. ✅ Add `extract` or `extract_table` for data
5. ✅ Add `save_csv` to export data
6. ✅ Test workflow with `workflow_runner.py`
7. ✅ Refine selectors and waits as needed

## Reference

- **Playwright Codegen Docs**: https://playwright.dev/docs/codegen
- **YAML Workflow Actions**: See `README.md`
- **Workflow Examples**: See `workflows/` folder
