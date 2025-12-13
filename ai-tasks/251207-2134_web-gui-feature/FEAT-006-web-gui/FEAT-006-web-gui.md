# [FEAT-006] Desktop GUI for Browser Session Manager

## Priority
- **P0 (Critical)** - This will make the browser session manager accessible to non-technical users with a native desktop experience

## Estimated Time
- 6-8 hours

## Dependencies
- Existing `tab_session_manager.py` (FEAT-001 through FEAT-005 completed)
- PyQt6 or CustomTkinter for desktop GUI
- Sessions stored in `tab-session-manager/sessions/*.json`
- Python 3.8+

## Description
Create a modern, native desktop application GUI for the browser tab session manager. The desktop app will allow users to:
- View all saved sessions in a visual dashboard
- Restore sessions with one click
- Create new browser sessions interactively
- Organize and manage tab groups within sessions
- See session details (creation date, tab count, groups, etc.)
- Search and filter sessions
- Delete unwanted sessions
- System tray integration (optional)
- Launch on startup (optional)

This will provide a native desktop experience, eliminating the need for CLI commands and making the tool accessible to anyone.

## Technical Approach

### Technology Choice
**Option A: PyQt6 (Recommended)**
- Professional, modern look
- Cross-platform (Windows, macOS, Linux)
- Rich widget library
- Good documentation
- Native performance

**Option B: CustomTkinter**
- Simpler than PyQt
- Modern, clean aesthetic
- Built on standard Tkinter
- Lightweight
- Easier learning curve

**Decision: Use PyQt6** for professional appearance and rich features

### Application Architecture

1. **Main Application Structure**
   ```
   tab-session-manager/
   ├── desktop_gui/
   │   ├── main.py              (Entry point, QApplication setup)
   │   ├── main_window.py       (Main window class)
   │   ├── widgets/
   │   │   ├── session_card.py  (Session card widget)
   │   │   ├── session_list.py  (Session list widget)
   │   │   ├── detail_dialog.py (Session detail dialog)
   │   │   ├── status_bar.py    (Browser status widget)
   │   │   └── search_bar.py    (Search/filter widget)
   │   ├── dialogs/
   │   │   ├── new_session.py   (New session dialog)
   │   │   ├── confirm_delete.py (Delete confirmation)
   │   │   └── about_dialog.py  (About dialog)
   │   ├── resources/
   │   │   ├── icons/           (App icons, button icons)
   │   │   └── styles.qss       (Qt stylesheet for styling)
   │   ├── utils/
   │   │   └── session_manager_wrapper.py (Wrapper for TabSessionManager)
   │   └── requirements.txt
   ```

2. **Core Components**
   - **MainWindow**: Application main window with menu bar, toolbar, status bar
   - **SessionListWidget**: Scrollable list/grid of session cards
   - **SessionCard**: Custom widget displaying session info (name, date, tab count)
   - **DetailDialog**: Modal dialog showing all tabs and groups
   - **StatusBar**: Shows browser running status, current session, auto-save status
   - **SearchBar**: Filter sessions by name, with sort options

3. **Integration with Existing Code**
   - Import `TabSessionManager` from parent directory
   - Wrap in thread-safe wrapper for GUI operations
   - Use Qt signals/slots for async operations
   - Keep existing JSON file format unchanged

## Acceptance Criteria

- [ ] Desktop app launches without errors
- [ ] Main window displays all saved sessions as visual cards
- [ ] Each session card shows: name, creation date, tab count, group count, icon
- [ ] Double-click or "Load" button restores session in browser
- [ ] Right-click context menu on session cards (Load, Details, Delete)
- [ ] "Details" opens dialog showing all tabs and groups
- [ ] "New Session" button creates new browser instance
- [ ] "Delete" prompts for confirmation before removing session
- [ ] Status bar shows browser state (Running/Stopped) with colored indicator
- [ ] Search bar filters sessions in real-time as user types
- [ ] Sort options available (name, date, tab count)
- [ ] Menu bar with File, Edit, View, Help menus
- [ ] System tray icon with quick actions (optional)
- [ ] App remembers window size and position on restart
- [ ] Keyboard shortcuts work (Ctrl+N for new, Ctrl+F for search, etc.)
- [ ] No UI freezing during browser operations (use threading)
- [ ] Empty state message when no sessions exist
- [ ] Can load specific groups from detail dialog
- [ ] Refresh button to reload session list
- [ ] Settings dialog for auto-save interval, theme, etc. (optional)

## Implementation Steps

### Step 1: Environment Setup (30 min)
1. Create `desktop_gui/` folder in `tab-session-manager/`
2. Create folder structure as outlined above
3. Create `requirements.txt`:
   ```
   PyQt6>=6.6.0
   playwright>=1.40.0
   ```
4. Install dependencies: `pip install -r desktop_gui/requirements.txt`
5. Test PyQt6 installation with simple "Hello World" window

### Step 2: Main Window and Application Setup (1 hour)
1. Create `main.py` with `QApplication` setup:
   - Application instance
   - System tray icon (optional)
   - Application exit handling
2. Create `main_window.py` with `QMainWindow`:
   - Set window title, size (800x600 default)
   - Create menu bar (File, Edit, View, Help)
   - Create toolbar with main actions
   - Create status bar
   - Create central widget (will hold session list)
3. Add application icon and window icon
4. Test window launches and displays correctly

### Step 3: Session Manager Integration (1 hour)
1. Create `utils/session_manager_wrapper.py`:
   - Import `TabSessionManager` from parent directory
   - Create wrapper class with Qt signals for events
   - Implement methods: `get_sessions()`, `load_session()`, `delete_session()`, etc.
   - Handle threading for browser operations (use QThread)
2. Create Qt signals:
   - `session_loaded(name: str)`
   - `session_saved(name: str)`
   - `session_deleted(name: str)`
   - `browser_status_changed(is_running: bool)`
3. Test wrapper can read existing sessions

### Step 4: Session List and Cards (2 hours)
1. Create `widgets/session_card.py`:
   - Custom `QWidget` or `QFrame` for each session
   - Display session name (large, bold text)
   - Display creation date (smaller text)
   - Display tab count and group count (with icons)
   - Display session icon/thumbnail
   - Hover effects (highlight on mouse over)
   - Click handlers (double-click to load)
   - Context menu (right-click) with Load/Details/Delete
2. Create `widgets/session_list.py`:
   - Scrollable area with grid or list layout
   - Dynamically create session cards from session data
   - Empty state widget (shown when no sessions)
   - Refresh method to reload sessions
3. Add session cards to main window central widget
4. Test session list displays existing sessions correctly

### Step 5: Dialogs and User Actions (1-2 hours)
1. Create `dialogs/new_session.py`:
   - Input for session name
   - Checkbox for auto-save enabled
   - Spinner for auto-save interval
   - OK/Cancel buttons
   - Validation for session name
2. Create `dialogs/detail_dialog.py`:
   - Display session name and metadata
   - Tree view or list showing groups and tabs
   - Each tab shows title and URL
   - Buttons to load entire session or specific groups
   - Close button
3. Create `dialogs/confirm_delete.py`:
   - Warning message with session name
   - Yes/No buttons
   - Optional "Don't ask again" checkbox
4. Connect dialogs to main window actions
5. Test all dialogs open and function correctly

### Step 6: Search, Filter, and Status Bar (1 hour)
1. Create `widgets/search_bar.py`:
   - Search input field with placeholder text
   - Clear button (X icon)
   - Sort dropdown (Name, Date, Tab Count)
   - Filter sessions in real-time as user types
2. Create `widgets/status_bar.py`:
   - Browser status indicator (green/red circle with text)
   - Current session name (if auto-saving)
   - Auto-save status (enabled/disabled)
   - Background thread to poll browser status every 2 seconds
3. Add search bar to main window toolbar
4. Add status bar to main window bottom
5. Test search filters sessions correctly
6. Test status bar updates when browser state changes

### Step 7: Menu Bar, Keyboard Shortcuts, and Polish (1-2 hours)
1. Implement menu bar actions:
   - **File**: New Session, Refresh, Exit
   - **Edit**: Search (focus search bar)
   - **View**: Sort by Name/Date/Tabs, Toggle Toolbar
   - **Help**: About, Documentation
2. Add keyboard shortcuts:
   - `Ctrl+N`: New Session
   - `Ctrl+F`: Focus search bar
   - `Ctrl+R`: Refresh session list
   - `Ctrl+Q`: Quit application
   - `Delete`: Delete selected session
   - `Enter`: Load selected session
3. Create `dialogs/about_dialog.py`:
   - App name, version, description
   - Link to documentation
   - Credits
4. Save/restore window geometry (size, position)
5. Add application stylesheet (`resources/styles.qss`) for modern look:
   - Color scheme (light or dark theme)
   - Button styles, hover effects
   - Card shadows and borders
6. Add icons to buttons and menu items
7. Test all keyboard shortcuts work
8. Test app remembers window size/position

### Step 8: Testing and Bug Fixes (1 hour)
1. Test complete workflow:
   - Launch app
   - View sessions
   - Search sessions
   - Load a session (verify browser opens)
   - Create new session
   - Save session (via TabSessionManager)
   - Delete session
   - View session details
2. Test edge cases:
   - No sessions exist (empty state)
   - Browser crashes during load
   - Invalid session file
   - Very long session names
   - Sessions with 100+ tabs
3. Test on different screen resolutions
4. Fix any bugs found
5. Optimize performance (lazy loading if many sessions)

## Testing Steps

### Manual Testing Checklist

**Basic Functionality:**
1. Launch app: `python desktop_gui/main.py`
2. Verify main window appears with session list
3. Verify existing sessions displayed as cards
4. Double-click a session - verify browser launches and tabs restore
5. Click "New Session" - verify dialog appears, create session, verify browser launches
6. Use search bar - verify sessions filter in real-time
7. Right-click session card - verify context menu appears
8. Select "Details" - verify all tabs/groups shown in dialog
9. Select "Delete" - verify confirmation dialog, confirm, verify session removed
10. Check status bar - verify browser status indicator accurate
11. Try keyboard shortcuts (Ctrl+N, Ctrl+F, etc.)
12. Close and reopen app - verify window size/position remembered

**Edge Cases:**
1. Launch with no saved sessions - verify empty state message
2. Create session with invalid name (spaces, special chars) - verify validation
3. Load session while browser already running - handle gracefully
4. Delete session that doesn't exist - handle error
5. Test with 50+ sessions - verify performance acceptable
6. Minimize to system tray (if implemented) - verify works
7. Resize window to very small size - verify UI still usable

**UI/UX:**
1. Verify all icons load correctly
2. Verify hover effects on cards and buttons
3. Verify status bar updates in real-time
4. Verify no UI freezing during browser operations
5. Verify error messages are clear and helpful
6. Verify dialogs are modal (can't interact with main window while open)

### Automated Testing (Optional)
- Unit tests for session manager wrapper (pytest)
- UI tests for widgets (pytest-qt)

## Security Considerations

- [x] **Input Validation**
  - Validate session names (alphanumeric, dash, underscore only)
  - Prevent path traversal in session file names
  - Validate user inputs in all dialogs

- [x] **File System Security**
  - Only allow access to `sessions/` directory
  - Validate file extensions (.json only)
  - Check file permissions before read/write

- [x] **Process Security**
  - Validate browser process is legitimate
  - Don't execute arbitrary commands from session files
  - Sanitize URLs before opening in browser

- [x] **Desktop Security**
  - Don't store sensitive data in app settings
  - Use OS keychain if storing credentials (future)
  - Respect OS security permissions

- [x] **UI Security**
  - Escape special characters in displayed text
  - Don't render untrusted HTML
  - Validate all user inputs before processing

## Rollback Plan

If issues arise:
1. Delete `desktop_gui/` folder to remove GUI
2. Use CLI commands from `tab_session_manager.py` as fallback
3. If GUI corrupts session files:
   - Restore from backup (create backup before first use)
   - Session files are human-readable JSON, can manually edit
4. No changes to core `tab_session_manager.py`, so CLI functionality unaffected
5. Uninstall PyQt6 if causing system issues: `pip uninstall PyQt6`

## Notes

### Future Enhancements
- **Dark mode** support with theme switcher
- **System tray integration** with quick actions menu
- **Drag-and-drop** to reorder sessions
- **Session templates** (create reusable tab group templates)
- **Export/import** sessions (share with others)
- **Scheduled sessions** (auto-load work tabs at 9am)
- **Cloud sync** (sync sessions across devices)
- **Session tagging** (tag sessions for organization)
- **Recent sessions** (quick access to recently loaded)
- **Session thumbnails** (screenshot preview of first tab)
- **Multi-browser support** (Chrome, Firefox, Edge simultaneously)
- **Browser extension integration** (better group support)
- **Session comparison** (diff view between two sessions)
- **Tab deduplication** (remove duplicate URLs)
- **Installer/executable** (PyInstaller or cx_Freeze for distribution)

### Known Limitations
- Desktop app is local-only (no web access)
- Tab groups may not perfectly restore browser native groups (Playwright limitation)
- Large sessions (100+ tabs) may take time to load
- No mobile version (desktop only)
- System tray may not work on all Linux desktop environments

### Technology Choices
- **PyQt6** chosen for professional look and rich features
- **Alternative: CustomTkinter** if PyQt too complex
- **Threading** required to prevent UI freezing during browser ops
- **Qt Signals/Slots** for event handling
- **QSettings** for persisting app preferences
- **JSON** for session storage (unchanged from CLI version)

### PyQt6 vs CustomTkinter Comparison

| Feature | PyQt6 | CustomTkinter |
|---------|-------|---------------|
| Look & Feel | Professional, native | Modern, flat design |
| Complexity | Medium-High | Low-Medium |
| Features | Very rich | Basic-Medium |
| Performance | Excellent | Good |
| Learning Curve | Steeper | Gentle |
| Documentation | Excellent | Good |
| License | GPL/Commercial | MIT |

### Development Tips
- Use Qt Designer for rapid UI prototyping (optional)
- Use Qt Resource System for embedding icons
- Use QThread for long-running operations (never block UI)
- Test on Windows, macOS, Linux if possible
- Use virtual environment to avoid dependency conflicts

### Success Metrics
- User can perform all CLI operations via GUI
- App startup time < 3 seconds
- Session load time < 5 seconds for typical session (< 20 tabs)
- Zero crashes during normal use
- UI responsive at all times (no freezing)
- Positive user feedback on ease of use
- Users prefer GUI over CLI

---

**Created:** 2025-12-07
**Updated:** 2025-12-07 (Changed from web-based to desktop app)
**Status:** Todo
**Assigned to:** Claude Code
**Tags:** gui, desktop, pyqt, native-app, dashboard, browser-automation
