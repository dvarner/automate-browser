# Browser Session Manager - Desktop GUI

A modern desktop application for managing browser tab sessions with an intuitive graphical interface.

## Features

- **Visual Session Management** - View all your saved sessions as cards in a clean interface
- **One-Click Loading** - Double-click any session to restore it instantly
- **Session Details** - View all tabs and groups within any session
- **Search & Filter** - Quickly find sessions with real-time search
- **Sort Options** - Sort by name, date, or tab count
- **Browser Status** - Real-time indicator showing if browser is running
- **Keyboard Shortcuts** - Efficient navigation with keyboard
- **Auto-Save Support** - Configure auto-save when creating sessions

## Installation

1. **Install Dependencies:**
   ```bash
   cd desktop_gui
   pip install -r requirements.txt
   ```

2. **Verify Installation:**
   ```bash
   python main.py
   ```

## Usage

### Launching the Application

```bash
cd tab-session-manager/desktop_gui
python main.py
```

### Creating a New Session

1. Click **"New Session"** button in toolbar (or press `Ctrl+N`)
2. Enter a session name (letters, numbers, dashes, underscores only)
3. Configure auto-save settings if desired
4. Click **"Create"**
5. A browser will launch - open your tabs manually
6. Tabs are auto-saved as you work

### Loading a Session

**Method 1: Double-Click**
- Double-click any session card to load it

**Method 2: Right-Click Menu**
- Right-click a session card → Select "Load Session"

**Method 3: Details Dialog**
- Right-click → "View Details" → "Load Entire Session"

### Viewing Session Details

1. Right-click a session card
2. Select **"View Details"**
3. See all tabs organized by groups
4. Can load entire session from detail view

### Deleting a Session

1. Right-click a session card
2. Select **"Delete Session"**
3. Confirm deletion in dialog

### Searching Sessions

1. Type in the search bar at the top (or press `Ctrl+F`)
2. Sessions filter in real-time as you type

### Sorting Sessions

Use the "Sort by" dropdown to sort by:
- **Name** - Alphabetical order
- **Date** - Most recent first
- **Tab Count** - Most tabs first

## Keyboard Shortcuts

- `Ctrl+N` - New Session
- `Ctrl+F` - Focus Search Bar
- `Ctrl+R` - Refresh Session List
- `Ctrl+Q` - Quit Application

## Menu Bar

### File Menu
- **New Session** - Create new browser session
- **Refresh** - Reload session list
- **Exit** - Close application

### Edit Menu
- **Search** - Focus search bar

### View Menu
- **Sort by Name** - Sort sessions alphabetically
- **Sort by Date** - Sort by creation date
- **Sort by Tab Count** - Sort by number of tabs

### Help Menu
- **About** - Show application information

## Browser Status Indicator

The status bar at the bottom shows:
- **Browser: Running** (Green) - Browser is active
- **Browser: Not Running** (Red) - No browser instance

Status updates every 2 seconds automatically.

## Session File Format

Sessions are stored in `../sessions/*.json` in the same format as the CLI version, ensuring full compatibility.

## Tips

1. **Creating Organized Sessions:**
   - Use descriptive names (e.g., `work-project-alpha`, `research-ai-ml`)
   - Enable auto-save to never lose tabs

2. **Managing Many Sessions:**
   - Use search to quickly find sessions
   - Sort by date to see recent sessions first
   - Delete old sessions you no longer need

3. **Browser Integration:**
   - Browser must be running on port 9222 for status detection
   - Sessions launched from GUI automatically configure this

## Troubleshooting

### Application Won't Start

**Error:** `ModuleNotFoundError: No module named 'PyQt6'`
- **Solution:** Install dependencies: `pip install -r requirements.txt`

**Error:** `ModuleNotFoundError: No module named 'playwright'`
- **Solution:** Install Playwright: `pip install playwright && playwright install`

### Can't Create Session

**Error:** "Invalid session name"
- **Solution:** Use only letters, numbers, dashes, and underscores

### Session Won't Load

**Error:** "Failed to load session"
- **Solution:** Check that session JSON file exists in `../sessions/` folder
- **Solution:** Verify Playwright is installed correctly

### Browser Status Always Shows "Not Running"

- Browser may not be running on port 9222
- Create a new session from GUI to launch properly configured browser
- If using CLI, ensure browser started with `--remote-debugging-port=9222`

## Compatibility

- **Python:** 3.8+
- **Operating Systems:** Windows, macOS, Linux
- **Qt:** PyQt6 (uses Fusion style for consistent cross-platform appearance)

## Development

### Project Structure

```
desktop_gui/
├── main.py                    # Application entry point
├── main_window.py             # Main window class
├── widgets/
│   ├── session_card.py        # Session card widget
│   ├── session_list.py        # Session list widget
│   ├── search_bar.py          # Search/filter widget
│   └── status_bar.py          # Browser status widget
├── dialogs/
│   ├── new_session.py         # New session dialog
│   ├── confirm_delete.py      # Delete confirmation
│   ├── detail_dialog.py       # Session detail view
│   └── about_dialog.py        # About dialog
└── utils/
    └── session_manager_wrapper.py  # TabSessionManager wrapper
```

### Adding Features

The application is designed to be extensible:
- Add new dialogs in `dialogs/`
- Add new widgets in `widgets/`
- Extend `SessionManagerWrapper` for new functionality
- Connect new signals to `MainWindow` slots

## License

Same as parent Browser Session Manager project.

## Version

1.0.0 - Initial release
