# Chrome Extension Workflow Recorder - User Guide

Record browser workflows directly in Chrome and export to YAML format!

## Features

✅ **Two Modes in One Extension:**
1. 📥 **Export Tabs** - Export browser tabs with groups to JSON (original feature)
2. 🔴 **Record Workflow** - Record browser actions and export to YAML (NEW!)

## Installation

### Load Extension in Chrome

1. Open `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select folder: `D:\Claude\Automate\Browser\chrome-extension`
5. Extension will appear in toolbar (click puzzle icon 🧩 to pin it)

## Using the Workflow Recorder

### Quick Start

1. **Click extension icon** in Chrome toolbar
2. **Switch to "Record Workflow" tab**
3. **Click "Start Recording"**
4. **Perform actions** in the page:
   - Click buttons and links
   - Fill out forms
   - Navigate to new pages
5. **Click "Stop Recording"** when done
6. **Review captured actions** (edit/delete as needed)
7. **Export to YAML**
8. **Save to** `workflow-engine/workflows/`
9. **Run with** `python workflow_runner.py workflows/your-workflow.yaml`

### Detailed Walkthrough

#### Step 1: Start Recording

- Click "Start Recording" button
- A red 🔴 indicator appears on the page showing recording is active
- Extension popup shows status: "🔴 Recording..."

#### Step 2: Perform Actions

The recorder captures:

- **Navigation** - Moving to new URLs
- **Clicks** - Button clicks, link clicks, any element clicks
- **Form Fills** - Input fields, textareas, select dropdowns
- **Checkboxes/Radios** - Selection changes

**Tips:**
- Be deliberate - only perform actions you want recorded
- Passwords are automatically marked as sensitive (hidden with `********`)
- Actions appear in real-time in the actions list

#### Step 3: Stop Recording

- Click "Stop Recording" button
- Red indicator disappears from page
- All captured actions are saved

#### Step 4: Review Actions

The actions list shows:
- Action number
- Action type (NAVIGATE, CLICK, FILL)
- Element selector
- Additional details (URL, text, value)

**You can:**
- Delete individual actions (click ✕ button)
- Clear all actions (click "Clear All")
- Actions are automatically deduplicated

#### Step 5: Export to YAML

1. Enter a workflow name (e.g., `login-flow`)
2. Click "Preview YAML" to see the output
3. Click "Export YAML" to download
4. Save to `workflow-engine/workflows/`

#### Step 6: Run Workflow

```bash
cd workflow-engine
python workflow_runner.py workflows/login-flow.yaml
```

## Example Workflows

### Example 1: Simple Form Fill

**Actions:**
1. Navigate to form page
2. Fill email field
3. Fill message field
4. Click submit button

**Generated YAML:**
```yaml
name: "Contact Form"
browser: "chrome"
timeout: 30

steps:
  - action: navigate
    url: "https://example.com/contact"

  - action: fill
    selector: "#email"
    value: "user@example.com"

  - action: fill
    selector: "#message"
    value: "Hello from recorder!"

  - action: click
    selector: "button[type='submit']"
```

### Example 2: Login Flow

**Actions:**
1. Navigate to login page
2. Fill username
3. Fill password
4. Click login button
5. Navigate to dashboard (after login)

**Generated YAML:**
```yaml
name: "Login Workflow"
browser: "chrome"
timeout: 30

steps:
  - action: navigate
    url: "https://example.com/login"

  - action: fill
    selector: "#username"
    value: "myusername"

  - action: fill
    selector: "#password"
    value: "********"
    sensitive: true

  - action: click
    selector: "button#login"

  - action: navigate
    url: "https://example.com/dashboard"
```

## Editing Exported Workflows

After exporting, you can enhance the YAML file:

### Add Human Interaction Pauses

```yaml
- action: wait_for_human
  reason: "Please complete CAPTCHA"
  continue_selector: "#main-content"
  timeout: 120
```

### Add Data Extraction

```yaml
- action: extract_table
  name: "products"
  rows: ".product-item"
  columns:
    title: "h2"
    price: ".price"

- action: save_csv
  data: "products"
  file: "products.csv"
```

### Add Explicit Waits

```yaml
- action: wait
  selector: ".results"
  timeout: 10
```

## Tips & Best Practices

### Recording Tips

1. **Start fresh** - Navigate to starting URL before recording
2. **Be deliberate** - Only perform actions you need
3. **Wait for pages** - Let pages load before clicking
4. **One workflow at a time** - Don't switch tabs during recording
5. **Test selectors** - Some generated selectors may need manual editing

### Selector Quality

The recorder generates selectors in this priority:
1. Element ID (`#element-id`) - Most reliable
2. Name attribute (`input[name="email"]`)
3. Data attributes (`[data-testid="button"]`)
4. Classes (`.class-name`)
5. Tag + nth-child (fallback)

**If a selector doesn't work:**
- Open browser DevTools (F12)
- Find the element
- Copy a better selector
- Edit the YAML file manually

### Password & Sensitive Data

- Password fields are automatically detected
- Values shown as `********`
- Marked with `sensitive: true` in YAML
- You can manually edit values later

### Action Cleanup

The recorder automatically:
- Removes duplicate consecutive actions
- Keeps only the final value for repeated form fills
- Tracks navigation changes

## Troubleshooting

### Extension doesn't load
- Check Developer mode is enabled
- Reload the extension in `chrome://extensions/`
- Check browser console for errors

### Recording doesn't start
- Make sure you're on a web page (not chrome:// page)
- Check that activeTab permission is granted
- Try refreshing the page and starting again

### Actions not captured
- Some elements may not trigger events properly
- Dynamic content (SPAs) may need manual selectors
- Try clicking more deliberately (slower)

### Selectors don't work when running workflow
- Generated selectors may be fragile
- Use DevTools to find better selectors
- Edit YAML file with more stable selectors
- Prefer IDs or data-test attributes

### Exported file not downloading
- Check Chrome download settings
- Check downloads permission is granted
- Try a different filename

## Integration with Workflow Engine

Recorded workflows are fully compatible with the workflow engine and support all features:

- ✅ Navigate to URLs
- ✅ Click elements
- ✅ Fill forms
- ✅ Manual additions: waits, data extraction, human pauses
- ✅ All 9 workflow actions available

After recording, you can add:
- `wait_for_human` for logins/CAPTCHAs
- `extract` / `extract_table` for data scraping
- `save_csv` for exporting data
- `screenshot` for debugging
- `wait` for page loads

## Comparison with Other Methods

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Chrome Recorder** | Quick, simple workflows | Fast, visual, in-browser | Limited editing |
| **Playwright Codegen** | Complex, multi-page flows | Powerful, accurate | Requires conversion |
| **Manual YAML** | Precise control | Full flexibility | More time-consuming |

**Recommended approach:**
1. Use Chrome Recorder for initial capture
2. Export to YAML
3. Edit YAML to add enhancements
4. Run with workflow engine

## Version History

**v2.0.0** (2025-12-14)
- Added workflow recording capability
- Tab-based UI (Export vs Record)
- Real-time action capture
- YAML export
- Action editing (delete individual actions)
- Automatic deduplication

**v1.0.0** (2025-12-12)
- Tab session export functionality
- Group preservation
- JSON format export

## Support

For issues:
- **Extension**: Check this guide
- **Workflow Engine**: See `workflow-engine/README.md`
- **YAML Format**: See `workflow-engine/QUICKSTART.md`
