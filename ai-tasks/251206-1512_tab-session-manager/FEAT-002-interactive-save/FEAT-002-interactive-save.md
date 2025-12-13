# [FEAT-002] Interactive Save Command

## Priority
- P1 - High

## Estimated Time
- 1-2 hours

## Dependencies
- FEAT-001 (completed)

## Description
Add interactive save functionality that captures the current browser state and saves it to a JSON file. This is the biggest missing piece from the MVP - users can load sessions but need a way to save their current browser tabs without manually creating JSON files.

**Core functionality:**
- Save command works while browser is running
- Captures all open tabs from current browser session
- Saves to named JSON file in sessions directory
- Can be called from a separate terminal window

## Technical Approach

### Implementation Options

**Option A: Keyboard shortcut in running browser**
- Listen for keyboard event (e.g., Ctrl+S)
- Prompt for session name
- Save immediately

**Option B: Signal-based (file watcher)**
- Watch for a trigger file (e.g., `.save-session`)
- When file appears, read session name from it
- Save and delete trigger file

**Option C: Separate command that connects to running browser** (CHOSEN)
- Use Playwright's ability to connect to existing browser
- Run: `python tab_session_manager.py save my-session` in new terminal
- Connects to running browser and captures state

**Decision: Option C** - Most flexible, works with existing CLI pattern

### Architecture
- Modify `save_session()` to work with or without running browser
- Add browser connection logic (connect to existing browser via debugging port)
- Launch browser with remote debugging enabled
- Save command connects via CDP (Chrome DevTools Protocol)

## Acceptance Criteria
- [ ] Can save current browser state while browser is running
- [ ] Command: `python tab_session_manager.py save <name>` works in separate terminal
- [ ] All open tabs are captured (URL, title, order)
- [ ] Session saved to JSON file correctly
- [ ] Works with both `new` and `load` commands
- [ ] Error handling for browser not running
- [ ] Error handling for invalid session names

## Implementation Steps

1. **Modify browser launch to enable remote debugging**
   - Add `--remote-debugging-port=9222` to browser launch
   - Store debugging port info for connection

2. **Create browser connection method**
   - Add `connect_to_browser()` method
   - Use Playwright's `connect_over_cdp()` or browser endpoint
   - Handle connection errors gracefully

3. **Update save command logic**
   - Check if browser is running (try to connect)
   - If connected, capture current tabs
   - Save to JSON file
   - Display success message

4. **Update save_session() method**
   - Make it work independently (not just from running instance)
   - Get tabs from connected browser
   - Create session data structure
   - Write to file

5. **Add error handling**
   - Browser not running error
   - Connection timeout
   - Invalid session name
   - File write errors

6. **Update CLI argument parsing**
   - Remove note about save being unimplemented
   - Update help text with new workflow

7. **Test workflow**
   - Start browser: `python tab_session_manager.py new`
   - Open several tabs
   - In new terminal: `python tab_session_manager.py save test-session`
   - Verify JSON file created with correct tabs

## Testing Steps

1. **Test save with new command:**
   - Run: `python tab_session_manager.py new`
   - Open 5 tabs
   - In new terminal: `python tab_session_manager.py save work-session`
   - Verify `sessions/work-session.json` exists
   - Verify all 5 tabs are in JSON file

2. **Test save with load command:**
   - Run: `python tab_session_manager.py load demo-session`
   - Add 2 more tabs manually
   - In new terminal: `python tab_session_manager.py save expanded-session`
   - Verify JSON has 5 tabs (3 original + 2 new)

3. **Test error cases:**
   - Try save when no browser running → helpful error message
   - Try save with invalid name → validation error
   - Try save when connection fails → timeout error

## Security Considerations
- [ ] Remote debugging port (9222) only listens on localhost
- [ ] Session name validation (prevent path traversal)
- [ ] No sensitive data in session files (URLs only)
- [ ] Connection timeout to prevent hanging

## Rollback Plan
- Changes are additive (new methods)
- Existing functionality not affected
- Can revert to manual JSON creation if needed

## Notes

### Browser Connection Methods
- Playwright supports `connect_over_cdp()` for Chrome DevTools Protocol
- Need to launch browser with debugging port enabled
- Port 9222 is standard for Chrome debugging

### User Workflow After This Feature
```bash
# Terminal 1: Start browser
python tab_session_manager.py new

# (Open tabs as needed)

# Terminal 2: Save session
python tab_session_manager.py save my-work-session

# Later: Load session
python tab_session_manager.py load my-work-session
```

### Future Improvements
- Auto-detect debugging port
- Support multiple browser instances
- Save without requiring separate terminal (background thread)

---

**Created:** 2025-12-06
**Status:** Todo
**Assignee:** Claude Code
