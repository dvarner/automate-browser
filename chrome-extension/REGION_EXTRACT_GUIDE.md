# Region Text Extraction - User Guide

## Overview

The **Region Extract** feature allows you to visually select any region on a webpage and extract all text content within that area. This works across complex DOM structures, spanning multiple HTML elements.

## How to Use

### 1. Open the Extension
- Click the extension icon in Chrome toolbar
- Navigate to the **"📍 Region Extract"** tab

### 2. Start Selection Mode
- Click **"Start Selection"** button
- The page will show:
  - Orange indicator: "📍 Region Selection Mode"
  - Crosshair cursor

### 3. Select Your Region
- Click and drag to create a selection rectangle
- You'll see:
  - Blue rectangle showing the selected area
  - Dimension tooltip (width × height in pixels)
- Release mouse to complete selection

### 4. View Results
- Extension popup will show:
  - Number of text elements extracted
  - Preview of extracted text
- Status badge changes to **"Complete"** (green)

### 5. Export Your Data

Choose from multiple export formats:

#### Copy to Clipboard
- Click **"📋 Copy to Clipboard"**
- Paste anywhere (Ctrl+V / Cmd+V)

#### Download as TXT
- Click **"💾 Download TXT"**
- Plain text file with all extracted text
- Filename: `region-text-YYYYMMDD.txt`

#### Download as JSON
- Click **"📄 Download JSON"**
- Structured data with metadata:
  ```json
  {
    "region": { "x": 100, "y": 200, "width": 500, "height": 300 },
    "extracted_at": "2026-01-01T12:00:00.000Z",
    "count": 15,
    "elements": [
      {
        "text": "Sample text",
        "tagName": "P",
        "selector": "div.content > p:nth-child(1)",
        "x": 120,
        "y": 220
      }
    ]
  }
  ```
- Filename: `region-text-YYYYMMDD.json`

#### Download as CSV
- Click **"📊 Download CSV"**
- Spreadsheet-compatible format
- Columns: Text, Tag, X, Y
- Filename: `region-text-YYYYMMDD.csv`

## Features

### ✅ What It Does
- Extracts visible text from any selected region
- Works across multiple HTML elements (divs, spans, paragraphs, etc.)
- Handles complex nested DOM structures
- Filters out hidden/invisible elements
- Preserves element metadata (tag name, position, CSS selector)
- Real-time dimension display while selecting

### 🎯 Use Cases
- Extract data from tables or lists
- Copy text from specific sections
- Scrape content from web pages
- Extract information from poorly structured HTML
- Capture text that spans multiple elements
- Document web content for research

### 🔒 Privacy & Safety
- All processing happens locally in your browser
- No data sent to external servers
- Works on any webpage (except browser internal pages)
- Respects page security settings

## Tips & Tricks

### Getting Better Results
1. **Zoom In**: For precise selection, zoom in the webpage first
2. **Scroll to Target**: Position the content you want in the viewport
3. **Select Generously**: Include a bit of extra space around text
4. **Multiple Extractions**: You can run multiple extractions - use "Clear" between them

### Troubleshooting

**Problem**: "Start Selection" button doesn't work
- **Solution**: Make sure you're on a valid webpage (not chrome://, edge://, or about: pages)

**Problem**: No text extracted or partial extraction
- **Solution**:
  - Try selecting a larger region
  - Ensure text elements are visible on screen
  - Check that elements aren't hidden (display:none, visibility:hidden)

**Problem**: Extension popup closes during selection
- **Solution**: Keep the extension popup open. Click on it again if it closes, then restart selection.

## Technical Details

### Text Extraction Algorithm
1. Uses `TreeWalker` API to traverse all text nodes in DOM
2. Filters visible nodes (checks `display`, `visibility`, `opacity`)
3. Gets bounding rectangles for each text element
4. Checks rectangle intersection with selected region
5. Collects text, tag name, position, and CSS selector
6. Returns structured data to popup

### File Locations (For Developers)
- Content Script: `content-script.js` (lines 624-960)
- Background Script: `background.js` (lines 108-141, 278-305)
- Popup UI: `popup.html` (lines 288-348)
- Popup Logic: `popup.js` (lines 960-1184)

## Version History

### Current Version
- ✅ Visual drag-to-select interface
- ✅ Text extraction across complex DOM
- ✅ Multiple export formats (Copy, TXT, JSON, CSV)
- ✅ Real-time dimension display
- ✅ Status indicators

---

**Need Help?** Check the main extension README or open an issue on GitHub.
