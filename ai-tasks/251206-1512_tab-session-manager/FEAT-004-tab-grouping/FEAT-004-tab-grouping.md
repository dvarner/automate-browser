# [FEAT-004] Tab Grouping and Organization

## Priority
- P2 - Medium

## Estimated Time
- 2-3 hours

## Dependencies
- FEAT-001 (completed)
- FEAT-002 (interactive save)
- FEAT-003 (auto-save)

## Description
Add the ability to organize tabs into named groups within sessions. This allows better organization for large sessions with many tabs (e.g., separate "Work", "Research", "Entertainment" groups).

**Core functionality:**
- Define groups in session JSON
- Assign tabs to groups
- Load specific groups (not entire session)
- Visual separation when loading grouped tabs
- Group management commands

## Technical Approach

### Enhanced JSON Structure
```json
{
  "session_name": "my-work",
  "created_at": "2025-12-06T16:00:00",
  "groups": [
    {
      "name": "Email & Calendar",
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
  ],
  "ungrouped_tabs": [
    {"order": 1, "url": "https://news.ycombinator.com", "title": "Hacker News"}
  ]
}
```

### Backward Compatibility
- Old format (flat `tabs` array) still supported
- Automatically converts to ungrouped tabs
- Can upgrade old sessions to grouped format

### Group Commands
```bash
# Load entire session (all groups)
python tab_session_manager.py load my-work

# Load specific group only
python tab_session_manager.py load my-work --group "Development"

# Load multiple groups
python tab_session_manager.py load my-work --groups "Email & Calendar,Development"

# List groups in a session
python tab_session_manager.py groups my-work

# Add group to session (edit mode)
python tab_session_manager.py add-group my-work "New Group"
```

## Acceptance Criteria
- [ ] Sessions can define groups in JSON
- [ ] Old format (flat tabs) still loads correctly
- [ ] Can load entire session (all groups)
- [ ] Can load specific group: `--group "Group Name"`
- [ ] Can load multiple groups: `--groups "Group1,Group2"`
- [ ] Groups listed with: `python tab_session_manager.py groups <session>`
- [ ] Tabs within groups maintain order
- [ ] Ungrouped tabs supported (backward compat)
- [ ] Auto-save preserves groups (if they exist)

## Implementation Steps

1. **Update data model**
   - Create Group dataclass/dict structure
   - Update session loading to handle both formats
   - Add backward compatibility layer

2. **Implement group loading**
   - Parse groups from JSON
   - Filter by group name if `--group` specified
   - Load tabs from selected groups only

3. **Add CLI arguments**
   - `--group "GroupName"` - load single group
   - `--groups "Group1,Group2"` - load multiple groups
   - Add `groups` command to list groups

4. **Update save functionality**
   - Save preserves group structure if exists
   - Auto-save preserves groups
   - Option to auto-group by domain (future)

5. **Add group management commands**
   - `groups <session>` - list all groups
   - `add-group <session> <name>` - add new group
   - `move-tab <session> <tab-index> <group>` - move tab to group

6. **Update documentation**
   - Add examples of grouped sessions
   - Update README with group commands

7. **Test all scenarios**
   - Load old format sessions (backward compat)
   - Load new format with groups
   - Load specific groups
   - Save and preserve groups

## Testing Steps

1. **Test backward compatibility:**
   - Load old `demo-session.json` (flat tabs)
   - Verify tabs load correctly
   - Save should convert to new format (optional)

2. **Test grouped session loading:**
   - Create session with 2 groups, 3 tabs each
   - Load entire session
   - Verify all 6 tabs open

3. **Test single group loading:**
   - Run: `python tab_session_manager.py load my-work --group "Development"`
   - Verify only Development group tabs open

4. **Test multiple group loading:**
   - Run: `python tab_session_manager.py load my-work --groups "Email,Development"`
   - Verify both groups load (others ignored)

5. **Test group listing:**
   - Run: `python tab_session_manager.py groups my-work`
   - Verify all groups listed with tab counts

6. **Test auto-save with groups:**
   - Load grouped session
   - Open new tabs
   - Auto-save
   - Verify groups preserved in auto-save.json

## Security Considerations
- [ ] Group names validated (alphanumeric, spaces, dashes)
- [ ] No injection attacks via group names
- [ ] File paths still validated
- [ ] Group data doesn't exceed reasonable size

## Rollback Plan
- Backward compatible (old sessions still work)
- Can ignore group features if not needed
- Flat tab format still supported

## Notes

### User Workflow with Groups

**Creating a grouped session manually:**
```json
{
  "session_name": "daily-work",
  "groups": [
    {
      "name": "Communication",
      "tabs": [
        {"order": 1, "url": "https://gmail.com", "title": "Gmail"},
        {"order": 2, "url": "https://slack.com", "title": "Slack"}
      ]
    },
    {
      "name": "Code",
      "tabs": [
        {"order": 1, "url": "https://github.com", "title": "GitHub"},
        {"order": 2, "url": "https://localhost:3000", "title": "Local Dev"}
      ]
    }
  ]
}
```

**Loading workflows:**
```bash
# Morning: Load email and calendar only
python tab_session_manager.py load daily-work --group "Communication"

# Later: Add development tabs
python tab_session_manager.py load daily-work --group "Code"

# End of day: Load everything
python tab_session_manager.py load daily-work
```

### Auto-Grouping Ideas (Future)
- Group by domain (all github.com tabs together)
- Group by time opened (morning vs afternoon)
- Smart grouping based on tab relationships
- User-defined rules for auto-grouping

### Visual Organization
- Print group headers when loading:
  ```
  Loading group: Development
    1. GitHub - https://github.com
    2. Stack Overflow - https://stackoverflow.com

  Loading group: Email & Calendar
    1. Gmail - https://gmail.com
    2. Calendar - https://calendar.google.com
  ```

### Integration with Other Features
- Auto-save preserves group structure
- Interactive save can prompt for group assignment
- Groups can have metadata (color, icon in future GUI)

---

**Created:** 2025-12-06
**Status:** Todo
**Assignee:** Claude Code
