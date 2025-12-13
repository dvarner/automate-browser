# Browser Tab Session Manager (MVP)

A simple Python tool using Playwright to manage browser tab sessions. Track tabs as they're opened, save sessions to named JSON files, and restore them later.

## Features

- Launch browser with Playwright (headed mode)
- Track tabs automatically as they're opened
- **Auto-save on tab changes** (new tabs, closed tabs, URL changes)
- **Tab grouping** - Organize tabs into named groups
- Save current session to named JSON files
- Load and restore sessions (tabs open in original order)
- Load specific groups from sessions
- Simple CLI interface

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

## Usage

### Start a New Session

```bash
python tab_session_manager.py new
```

This will:
- Launch a browser
- Track each tab you open
- **Auto-save session** when tabs change (enabled by default)
- Keep running until you press Ctrl+C

**Auto-Save Options:**
```bash
# Disable auto-save
python tab_session_manager.py new --no-auto-save

# Custom auto-save interval (default: 3 seconds)
python tab_session_manager.py new --auto-save-interval 10
```

Auto-save creates `sessions/auto-save.json` which you can load later.

### Load a Saved Session

```bash
python tab_session_manager.py load <session-name>
```

Example:
```bash
python tab_session_manager.py load work-tabs
```

This will:
- Load the session from `sessions/work-tabs.json`
- Open all tabs in the original order
- Keep browser open for interaction

### List Available Sessions

```bash
python tab_session_manager.py list
```

Shows all saved sessions in the `sessions/` directory.

### Working with Tab Groups

**List groups in a session:**
```bash
python tab_session_manager.py groups work-grouped
```

**Load specific group:**
```bash
python tab_session_manager.py load work-grouped --group "Development"
```

**Load multiple groups:**
```bash
python tab_session_manager.py load work-grouped --groups "Communication,Development"
```

**Load entire session (all groups):**
```bash
python tab_session_manager.py load work-grouped
```

### Save Current Session

While the browser is running, you can save the current state in a separate terminal:

```bash
python tab_session_manager.py save <session-name>
```

Example:
```bash
# Terminal 1: Start browser
python tab_session_manager.py new

# (Open tabs as needed in the browser)

# Terminal 2: Save session
python tab_session_manager.py save my-work-session
```

This will:
- Connect to the running browser
- Capture all currently open tabs
- Save to `sessions/my-work-session.json`

## Session File Formats

### Simple Format (Flat Tabs)

Sessions are stored as JSON files in `sessions/` folder with this structure:

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

For better organization, you can group tabs:

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

**Benefits:**
- Load specific groups only (e.g., just "Development" tabs)
- Better organization for large sessions
- Visual separation when loading

## Examples

### Example 1: Research Session
```bash
# Load your research tabs
python tab_session_manager.py load research

# Browser opens with all your research tabs
```

### Example 2: Work Session
```bash
# Start fresh session
python tab_session_manager.py new

# Open tabs: Gmail, Calendar, Slack, GitHub
# Tabs are automatically tracked and displayed in terminal
```

## Session Files

Sessions are stored as JSON files in the `sessions/` directory:
- Location: `sessions/<session-name>.json`
- Format: Human-readable JSON
- Can be manually edited

## Current Limitations

- **Single browser instance**: Can't manage multiple browser instances simultaneously
- **Manual group creation**: Groups must be created manually in JSON files

## Planned Features

See project tickets for upcoming features:
- GUI interface (future)
- Auto-group tabs by domain (future)
- Session merging/editing tools (future)
- Export to other formats (future)

## Troubleshooting

### Browser doesn't open
- Make sure Playwright is installed: `python -m playwright install chromium`
- Check that Python 3.8+ is installed

### Session not found
- Run `python tab_session_manager.py list` to see available sessions
- Check that the JSON file exists in `sessions/` folder
- Verify session name has no special characters

### Tabs don't load
- Check your internet connection
- Some URLs might be blocked or require authentication
- Check terminal for error messages

## Technical Details

- **Language:** Python 3.8+
- **Library:** Playwright
- **Browser:** Chromium
- **Storage:** JSON files
- **Mode:** Headed (browser visible)

## License

TBD
