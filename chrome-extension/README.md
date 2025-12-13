# Tab Session Exporter - Chrome Extension

Export your Chrome browser tabs (with groups) directly to Browser Tab Session Manager format.

## Features

- ✅ **Export all open tabs** from current window or all windows
- 📁 **Preserve tab groups** - Chrome tab groups are exported with names
- 🎯 **Direct format compatibility** - Exports to exact JSON format used by Browser Tab Session Manager
- 👁️ **Preview before export** - See what will be exported
- 📥 **One-click download** - Downloads JSON file ready to use
- 🔒 **Privacy-focused** - All processing happens locally, no data sent anywhere

## Installation

### Step 1: Load Extension in Chrome

1. **Open Chrome Extensions page**
   - Go to `chrome://extensions/`
   - Or: Menu (⋮) → Extensions → Manage Extensions

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the extension**
   - Click "Load unpacked" button
   - Navigate to this folder: `D:\Claude\Automate\Browser\chrome-extension`
   - Click "Select Folder"

4. **Verify installation**
   - You should see "Tab Session Exporter" in your extensions list
   - The extension icon will appear in your Chrome toolbar
   - If you don't see it, click the puzzle piece icon (🧩) and pin it

### Step 2: (Optional) Add Icon

The extension will work without custom icons, but you'll see a placeholder. To add a custom icon:

1. Create or download PNG icons in these sizes:
   - `icon16.png` (16x16 pixels)
   - `icon48.png` (48x48 pixels)
   - `icon128.png` (128x128 pixels)

2. Save them to: `chrome-extension/icons/`

3. Reload the extension in `chrome://extensions/`

**Icon suggestions:**
- Download icon (📥)
- Tabs icon (📑)
- Folder icon (📂)
- Custom design

You can use any icon generator or design tool. Recommended: [IconKitchen](https://icon.kitchen/)

---

## Usage

### Quick Export

1. **Click the extension icon** in Chrome toolbar
2. **Review the info:**
   - Number of open tabs
   - Number of tab groups
   - Current window or all windows
3. **Enter a session name** (or use the auto-generated one)
   - Only letters, numbers, dashes (-), and underscores (_) allowed
   - Example: `work-tabs`, `research-2024`, `dev-session`
4. **Click "Export Session"**
5. **Save the file** to: `D:\Claude\Automate\Browser\tab-session-manager\sessions\`

That's it! The session is now available in your Browser Tab Session Manager.

### Preview Before Export

Click the **"Preview"** button to see:
- All groups and their tabs
- Ungrouped tabs
- Total tab count per group

### Export Options

**Include all windows:**
- Check this box to export tabs from ALL Chrome windows
- Unchecked: Only exports tabs from the current window

---

## Exported Format

The extension exports JSON files compatible with Browser Tab Session Manager:

### With Groups
```json
{
  "session_name": "work-tabs",
  "created_at": "2025-12-12T10:30:00.000Z",
  "groups": [
    {
      "name": "Development",
      "tabs": [
        {"order": 1, "url": "https://github.com", "title": "GitHub"},
        {"order": 2, "url": "https://stackoverflow.com", "title": "Stack Overflow"}
      ]
    },
    {
      "name": "Communication",
      "tabs": [
        {"order": 1, "url": "https://gmail.com", "title": "Gmail"}
      ]
    }
  ],
  "ungrouped_tabs": [
    {"order": 1, "url": "https://google.com", "title": "Google"}
  ]
}
```

### Without Groups
```json
{
  "session_name": "simple-session",
  "created_at": "2025-12-12T10:30:00.000Z",
  "tabs": [
    {"order": 1, "url": "https://github.com", "title": "GitHub"},
    {"order": 2, "url": "https://google.com", "title": "Google"}
  ]
}
```

---

## Workflow

### Complete Workflow: Chrome → Session Manager

1. **Organize your tabs** in Chrome (optional)
   - Right-click on a tab → "Add tab to new group"
   - Name your groups (e.g., "Work", "Research", "Shopping")

2. **Export with extension**
   - Click extension icon
   - Name your session
   - Click "Export Session"
   - Save to `tab-session-manager/sessions/`

3. **Use in Session Manager**
   - Open Desktop GUI: `python tab-session-manager/desktop_gui/main.py`
   - Your session appears in the list
   - Click to restore tabs later

4. **Restore sessions**
   - Launch the GUI or use CLI
   - Select your session
   - All tabs (with groups) will be restored in Playwright browser

---

## Permissions Explained

The extension requests these permissions:

- **`tabs`** - Required to read tab URLs and titles
- **`tabGroups`** - Required to read tab group names and organization
- **`downloads`** - Required to save the JSON file to your computer

**Privacy:** All data stays on your computer. Nothing is sent to any server.

---

## Troubleshooting

### Extension doesn't appear
- Make sure Developer Mode is enabled in `chrome://extensions/`
- Click the puzzle piece icon (🧩) and pin the extension
- Reload the extension

### Export button is disabled
- Check that session name only contains: letters, numbers, `-`, `_`
- No spaces, special characters, or emojis allowed

### Downloaded file goes to wrong location
- Chrome will ask where to save (if "Ask where to save" is enabled)
- Move the file to: `tab-session-manager/sessions/`
- Or configure Chrome default downloads location

### Tab groups not showing
- Make sure you've created tab groups in Chrome first
- Right-click a tab → "Add tab to new group"
- Groups without names will be named "Group [ID]"

### Some tabs missing
- Check "Include all windows" if you have multiple Chrome windows
- Some tabs (like `chrome://` pages) cannot be captured due to security
- Extension pages cannot be exported

---

## Session Name Guidelines

**Valid names:**
- `work-session`
- `research_2024`
- `dev-tabs`
- `project-alpha`

**Invalid names:**
- `work session` (no spaces)
- `work@home` (no special chars)
- `tabs!` (no punctuation)
- Empty string

---

## Tips & Best Practices

1. **Organize before exporting**
   - Group related tabs before exporting
   - Name groups descriptively ("Work Email", "Documentation", etc.)

2. **Use descriptive session names**
   - Include context: `client-presentation-2024`, `react-learning`
   - Use dates for time-sensitive sessions: `quarterly-review-2024-q4`

3. **Regular exports**
   - Export important tab sets before closing them
   - Keep backups of critical research sessions

4. **Combine with Session Manager**
   - Use extension to export current browser state
   - Use Session Manager to restore and manage sessions

---

## Uninstallation

To remove the extension:

1. Go to `chrome://extensions/`
2. Find "Tab Session Exporter"
3. Click "Remove"
4. Confirm removal

Your exported session files will remain in `tab-session-manager/sessions/`

---

## Technical Details

- **Manifest Version:** 3 (latest)
- **Compatible with:** Chrome, Edge, Brave, and other Chromium browsers
- **Minimum Chrome version:** 88+
- **File format:** JSON (UTF-8)
- **Processing:** Client-side only (no external servers)

---

## Support

For issues with:
- **Extension:** Check troubleshooting section above
- **Session Manager:** See `tab-session-manager/README.md`
- **Desktop GUI:** See `tab-session-manager/docs/GUI_LAUNCH.md`

---

## Version History

**v1.0.0** (2025-12-12)
- Initial release
- Export tabs with groups
- Preview functionality
- Single/multi-window support
- Direct Browser Tab Session Manager format compatibility

---

## Future Enhancements

Potential future features:
- Auto-sync to session manager folder
- Scheduled auto-exports
- Cloud backup integration
- Session comparison/diff
- Tag-based organization

---

**Ready to use!** Click the extension icon and export your first session.
