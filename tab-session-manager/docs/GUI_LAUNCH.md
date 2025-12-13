# Desktop GUI Launch Guide

**Browser Tab Session Manager - Desktop GUI**

This guide explains how to launch and use the Desktop GUI for managing browser tab sessions.

---

## Quick Start

### Option 1: Run from root directory
```bash
python tab-session-manager/desktop_gui/main.py
```

### Option 2: Run from desktop_gui directory
```bash
cd tab-session-manager/desktop_gui
python main.py
```

---

## Prerequisites

The GUI requires **PyQt6** which is not included in the base requirements. Install it first:

```bash
pip install PyQt6
```

If you don't have Playwright installed yet:
```bash
pip install -r tab-session-manager/requirements.txt
python -m playwright install chromium
```

---

## Complete Setup & Launch

Follow these steps for a fresh installation:

```bash
# 1. Install dependencies
pip install PyQt6 playwright

# 2. Install Chromium browser
python -m playwright install chromium

# 3. Launch GUI
python tab-session-manager/desktop_gui/main.py
```

---

## GUI Features

Based on **FEAT-006** (Desktop GUI for Browser Session Manager), the application provides:

### Core Features
- 📋 **View saved sessions** - Browse all your saved browser tab sessions
- 🚀 **One-click restore** - Restore sessions with a single click
- 🗂️ **Session organization** - Organize and manage your sessions visually
- 📊 **Session details** - See detailed information about each session
  - Number of tabs
  - Tab groups
  - Creation timestamps
  - Tab URLs and titles
- 🖥️ **Native desktop experience** - Built with PyQt6 for a modern, responsive interface

### User Interface Components
- **Session cards** - Visual representation of each saved session
- **Search functionality** - Quickly find sessions
- **Status bar** - Display application status and messages
- **Detail dialogs** - View comprehensive session information
- **Confirmation dialogs** - Safe deletion with user confirmation

---

## Session Storage

Sessions are stored as JSON files in:
```
tab-session-manager/sessions/
```

Each session file contains:
- Session name
- Creation timestamp
- Tab information (URLs, titles, order)
- Optional tab groups for organization

---

## Creating Sessions

You can create sessions using the CLI tool before managing them with the GUI:

```bash
cd tab-session-manager

# Start a new browser session
python tab_session_manager.py new

# Open tabs as needed, they will auto-save to sessions/auto-save.json

# Or save with a custom name from another terminal
python tab_session_manager.py save my-session-name
```

Then use the GUI to browse, restore, and manage these sessions!

---

## Session File Formats

### Simple Format (Flat Tabs)
```json
{
  "session_name": "my-session",
  "created_at": "2025-12-06T15:30:00",
  "tabs": [
    {
      "order": 1,
      "url": "https://github.com",
      "title": "GitHub"
    },
    {
      "order": 2,
      "url": "https://stackoverflow.com",
      "title": "Stack Overflow"
    }
  ]
}
```

### Grouped Format (With Tab Groups)
```json
{
  "session_name": "work-grouped",
  "created_at": "2025-12-06T17:00:00",
  "groups": [
    {
      "name": "Communication",
      "tabs": [
        {"order": 1, "url": "https://gmail.com", "title": "Gmail"},
        {"order": 2, "url": "https://calendar.google.com", "title": "Calendar"}
      ]
    },
    {
      "name": "Development",
      "tabs": [
        {"order": 1, "url": "https://github.com", "title": "GitHub"},
        {"order": 2, "url": "https://stackoverflow.com", "title": "Stack Overflow"}
      ]
    }
  ]
}
```

---

## Troubleshooting

### PyQt6 Import Error
```
ModuleNotFoundError: No module named 'PyQt6'
```
**Solution:** Install PyQt6
```bash
pip install PyQt6
```

### Browser doesn't open when restoring
- Make sure Playwright is installed: `python -m playwright install chromium`
- Check that Python 3.8+ is installed
- Verify the session file exists in `sessions/` folder

### GUI window doesn't appear
- Check if Python is 64-bit (PyQt6 requires 64-bit Python)
- Verify PyQt6 installation: `python -c "from PyQt6.QtWidgets import QApplication"`
- Check terminal for error messages

### Session file not found
- Run `python tab_session_manager.py list` to see available sessions
- Check that JSON files exist in `tab-session-manager/sessions/` folder
- Verify file permissions

---

## Technical Details

### Technology Stack
- **Language:** Python 3.8+
- **GUI Framework:** PyQt6
- **Browser Automation:** Playwright
- **Browser:** Chromium (headed mode)
- **Storage:** JSON files
- **Architecture:** Desktop native application

### Application Structure
```
tab-session-manager/
├── desktop_gui/
│   ├── main.py              # Entry point
│   ├── main_window.py       # Main window class
│   ├── widgets/             # UI components
│   │   ├── session_card.py
│   │   ├── session_list.py
│   │   ├── search_bar.py
│   │   └── status_bar.py
│   ├── dialogs/             # Dialog windows
│   │   ├── new_session.py
│   │   ├── detail_dialog.py
│   │   ├── confirm_delete.py
│   │   └── about_dialog.py
│   └── utils/               # Helper modules
│       └── session_manager_wrapper.py
├── sessions/                # Session storage
└── tab_session_manager.py   # CLI tool
```

---

## Related Documentation

- **README.md** - CLI usage and basic features
- **BROWSER_AUTOMATION.md** - Browser automation guides
- **ai-tasks/pm.md** - Project management system

---

## Version Information

- **Application Version:** 1.0.0
- **Feature Ticket:** FEAT-006
- **Status:** Completed ✅
- **Last Updated:** 2025-12-08

---

## Support & Feedback

For issues or feature requests, refer to the project's issue tracking system in `ai-tasks/pm.db`.

---

**Ready to get started?** Run `python tab-session-manager/desktop_gui/main.py` and start managing your browser sessions visually!
