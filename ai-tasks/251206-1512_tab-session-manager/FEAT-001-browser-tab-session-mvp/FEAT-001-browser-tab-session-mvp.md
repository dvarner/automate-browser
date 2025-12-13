# [FEAT-001] Browser Tab Session Manager (MVP)

## Priority
- P1 - High

## Estimated Time
- 3-4 hours

## Dependencies
- Playwright Python library (`pip install playwright`)
- No other tickets or external dependencies

## Description
Create a simple Python program that uses Playwright to manage browser tab sessions. The program should track tabs as they're opened, save sessions to named JSON files, and restore sessions by reopening tabs in the original order.

**Core functionality:**
- Launch browser with Playwright
- Track each tab opened (URL and order)
- Save current session to a named JSON file
- Load and restore sessions from JSON files
- Simple CLI interface for operations

## Technical Approach

### Architecture
- **Language:** Python 3.8+
- **Library:** Playwright for Python
- **Storage:** JSON files in `sessions/` directory
- **Interface:** CLI using argparse

### Data Structure
```json
{
  "session_name": "work-tabs",
  "created_at": "2025-12-06T15:12:00",
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

### File Structure
```
tab-session-manager/
├── tab_session_manager.py    # Main program
├── sessions/                  # Session JSON files
│   ├── work-tabs.json
│   └── research-tabs.json
└── requirements.txt           # Dependencies
```

## Acceptance Criteria
- [ ] Can launch browser with Playwright (headed mode)
- [ ] Tracks each tab as it's opened (URL and order)
- [ ] Can save current browser session to named JSON file
- [ ] Can load and restore session from JSON file
- [ ] Tabs open in original order when restored
- [ ] CLI commands work: `new`, `save <name>`, `load <name>`
- [ ] Sessions directory is created automatically
- [ ] Basic error handling for missing files, invalid names

## Implementation Steps

1. **Setup environment**
   - Create `requirements.txt` with playwright
   - Create project directory structure
   - Install Playwright: `pip install playwright && playwright install`

2. **Create basic script** (`tab_session_manager.py`)
   - Import Playwright and JSON modules
   - Set up argument parser (argparse)
   - Create main() function

3. **Implement browser launch**
   - Function to launch browser (headed mode)
   - Get browser context and initial page
   - Return browser and context objects

4. **Implement tab tracking**
   - Listen to new page/tab events
   - Store tab data (URL, order, title if available)
   - Maintain list of tabs in memory

5. **Implement save session**
   - Function to save current tabs to JSON
   - Create `sessions/` directory if needed
   - Write session data with timestamp
   - Input: session name (string)

6. **Implement load session**
   - Function to read JSON file
   - Launch browser
   - Open tabs in order from session data
   - Input: session name (string)

7. **Create CLI interface**
   - Add argparse commands:
     - `new` - Start new session
     - `save <name>` - Save current session
     - `load <name>` - Load saved session
   - Add help text for each command

8. **Add error handling**
   - Handle missing session files
   - Handle invalid session names
   - Handle browser connection errors
   - Graceful shutdown on Ctrl+C

9. **Test full workflow**
   - Test new → open tabs → save
   - Test load → verify tabs
   - Test error cases

## Testing Steps

### Manual Testing
1. **Test new session:**
   - Run: `python tab_session_manager.py new`
   - Verify browser opens
   - Manually open 3-5 tabs with different URLs
   - Verify program tracks tabs

2. **Test save session:**
   - With tabs open, run save command
   - Verify JSON file created in `sessions/` folder
   - Verify file contains correct URLs and order

3. **Test load session:**
   - Close browser
   - Run: `python tab_session_manager.py load <session_name>`
   - Verify browser opens with all tabs in correct order

4. **Test error handling:**
   - Try loading non-existent session
   - Try invalid session name (special characters)
   - Verify helpful error messages

### Edge Cases
- Empty session (no tabs opened)
- Session with 10+ tabs
- URLs with special characters
- Session name with spaces

## Security Considerations
- [ ] Validate session file paths (prevent directory traversal)
- [ ] Sanitize session names (alphanumeric, dashes, underscores only)
- [ ] JSON parsing with error handling (catch malformed files)
- [ ] No credentials or sensitive data stored (URLs only)
- [ ] Session files stored in local `sessions/` directory only
- [ ] No remote connections except browser navigation

## Rollback Plan
- Simple program with no database or system changes
- Delete session files if needed
- Uninstall Playwright if needed: `pip uninstall playwright`
- No migration or cleanup required

## Notes
- **Keep it simple** - This is MVP, focus on core functionality
- **Headed mode** - Run browser in visible mode (easier for user interaction)
- **Manual tab opening** - User opens tabs manually for MVP (auto-open from list comes later)
- **JSON format** - Easy to read/edit manually, good for debugging

### Future Enhancements (separate tickets)
- GUI interface for easier use
- Auto-save on tab changes
- Tab grouping/organization within sessions
- Browser bookmark import
- Session merging/editing
- Export to other formats (CSV, HTML)
- Integration with existing Python programs
- Auto-restore on crash
- Tab metadata (favicons, timestamps)
- Multiple browser support (Chrome, Firefox, etc.)

---

**Created:** 2025-12-06
**Status:** Todo
**Assignee:** Claude Code
