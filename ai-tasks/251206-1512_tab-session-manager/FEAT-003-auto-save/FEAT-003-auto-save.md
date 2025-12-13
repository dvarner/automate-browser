# [FEAT-003] Auto-Save on Tab Changes

## Priority
- P1 - High

## Estimated Time
- 2-3 hours

## Dependencies
- FEAT-001 (completed)
- FEAT-002 (interactive save command)

## Description
Automatically save the browser session whenever tabs change (new tab opened, tab closed, URL changed). This ensures users never lose their session state, even if the browser crashes or the program is interrupted.

**Core functionality:**
- Watch for tab events (new, closed, URL changes)
- Automatically save to a default session file
- Configurable auto-save interval (debounced to avoid too frequent saves)
- Optional: Manual disable/enable of auto-save

## Technical Approach

### Event Listeners
- Use Playwright's event system to watch:
  - `context.on('page')` - new tabs
  - `page.on('close')` - tabs closed
  - `page.on('framenavigated')` - URL changes

### Auto-Save Strategy
- Debounce saves (wait 2-3 seconds after last change)
- Save to special file: `sessions/auto-save.json`
- Include timestamp in session data
- Keep last N auto-saves (optional versioning)

### Architecture
```python
class AutoSaveManager:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.save_timer = None
        self.enabled = True

    def on_tab_event(self):
        # Cancel pending save
        if self.save_timer:
            self.save_timer.cancel()
        # Schedule new save (debounced)
        self.save_timer = Timer(3.0, self._do_auto_save)
        self.save_timer.start()

    def _do_auto_save(self):
        self.session_manager.save_session('auto-save')
```

## Acceptance Criteria
- [ ] Auto-save triggers when new tab opened
- [ ] Auto-save triggers when tab closed
- [ ] Auto-save triggers when URL changes
- [ ] Saves are debounced (3 second delay after last change)
- [ ] Saves to `sessions/auto-save.json`
- [ ] Timestamp included in session file
- [ ] Can disable auto-save with flag: `--no-auto-save`
- [ ] Can configure auto-save interval: `--auto-save-interval 5`

## Implementation Steps

1. **Create AutoSaveManager class**
   - Initialize with session manager reference
   - Add enabled flag
   - Add debounce timer logic

2. **Add event listeners**
   - Listen to `context.on('page')` for new tabs
   - Listen to `page.on('close')` for tab closes
   - Listen to `page.on('framenavigated')` for URL changes

3. **Implement debounced save**
   - Use threading.Timer for debounce
   - Cancel previous timer on new event
   - Start new timer (default 3 seconds)

4. **Add CLI arguments**
   - `--no-auto-save` - disable auto-save
   - `--auto-save-interval N` - set interval in seconds

5. **Integrate with TabSessionManager**
   - Create AutoSaveManager instance
   - Pass to browser launch
   - Wire up event listeners

6. **Add configuration**
   - Auto-save enabled by default
   - Configurable interval
   - Configurable auto-save file name

7. **Test all scenarios**
   - Open tab → auto-saves after 3 seconds
   - Close tab → auto-saves after 3 seconds
   - Change URL → auto-saves after 3 seconds
   - Rapid changes → only saves once after last change

## Testing Steps

1. **Test new tab event:**
   - Run: `python tab_session_manager.py new`
   - Open a new tab
   - Wait 3 seconds
   - Verify `sessions/auto-save.json` updated

2. **Test close tab event:**
   - Close a tab
   - Wait 3 seconds
   - Verify auto-save reflects closure

3. **Test URL change:**
   - Navigate to new URL in existing tab
   - Wait 3 seconds
   - Verify auto-save has new URL

4. **Test debouncing:**
   - Open 5 tabs rapidly (within 2 seconds)
   - Verify only 1 save happens (3 seconds after last tab)

5. **Test disable flag:**
   - Run: `python tab_session_manager.py new --no-auto-save`
   - Open tabs
   - Wait 5 seconds
   - Verify NO auto-save file created

6. **Test custom interval:**
   - Run: `python tab_session_manager.py new --auto-save-interval 10`
   - Open tab
   - Verify save happens after 10 seconds (not 3)

## Security Considerations
- [ ] Auto-save respects session name validation
- [ ] File writes are atomic (use temp file + rename)
- [ ] No sensitive data logged
- [ ] Timer properly cleaned up on exit

## Rollback Plan
- Auto-save is optional (can be disabled with flag)
- Existing functionality not affected
- Can delete auto-save feature if problematic

## Notes

### Performance Considerations
- Debouncing prevents excessive disk writes
- JSON writing is fast (<10ms for typical sessions)
- Event listeners have minimal overhead

### User Experience
- Auto-save is silent (no notifications)
- Can check timestamp in JSON to verify
- Auto-save file can be loaded like any other session

### Recovery Workflow
If browser crashes:
```bash
# Load the last auto-saved session
python tab_session_manager.py load auto-save
```

### Future Improvements
- Keep last N auto-saves (versioning)
- Show notification on auto-save (optional)
- Compress old auto-saves
- Smart save (only if changed)

---

**Created:** 2025-12-06
**Status:** Todo
**Assignee:** Claude Code
