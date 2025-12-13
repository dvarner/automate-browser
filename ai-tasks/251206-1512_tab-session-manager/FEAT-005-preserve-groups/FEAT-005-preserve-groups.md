# [FEAT-005] Preserve Groups When Saving

## Priority
- P0 - Critical

## Estimated Time
- 1-2 hours

## Dependencies
- FEAT-004 (Tab Grouping)

## Description
When saving a session that already has groups defined, preserve the group structure instead of overwriting with flat format. This ensures manually created groups aren't lost when auto-save or manual save runs.

**Current Problem:**
- User creates grouped session manually
- Auto-save overwrites it with flat format
- All group organization is lost

**Solution:**
- Check if existing session file has groups
- Map current tabs into existing groups (by URL matching)
- Preserve group structure
- Add new tabs to ungrouped section

## Technical Approach

### Algorithm
1. Check if session file exists
2. Load existing session data
3. If it has `groups`, preserve structure:
   - Match current tabs to existing groups by URL
   - Keep tabs in their original groups
   - Add new tabs to `ungrouped_tabs`
4. If no groups, save as flat format (current behavior)

### URL Matching
- Match tabs by URL to determine which group they belong to
- If URL matches a tab in a group, keep it in that group
- If URL is new, add to ungrouped

## Acceptance Criteria
- [ ] Loading grouped session and saving preserves groups
- [ ] Auto-save preserves groups
- [ ] New tabs added to ungrouped section
- [ ] Removed tabs are removed from groups
- [ ] Flat format sessions still save as flat format
- [ ] Group order preserved
- [ ] Tab order within groups preserved

## Implementation Steps

1. **Add _load_existing_session_structure() method**
   - Load existing JSON file
   - Return groups if present, None otherwise

2. **Add _map_tabs_to_groups() method**
   - Takes current tabs and existing groups
   - Maps tabs to groups by URL matching
   - Returns updated groups + ungrouped tabs

3. **Update save_session() method**
   - Load existing structure before saving
   - If groups exist, use _map_tabs_to_groups()
   - Save with groups or flat format accordingly

4. **Handle edge cases**
   - Session file doesn't exist (new session)
   - Session exists but is flat format
   - Session exists with groups
   - All tabs removed
   - All new tabs

5. **Test all scenarios**
   - Save grouped session → groups preserved
   - Auto-save grouped session → groups preserved
   - Add new tabs → go to ungrouped
   - Remove tabs → removed from groups
   - Flat session → stays flat

## Testing Steps

1. **Test group preservation:**
   - Create grouped session manually
   - Load it
   - Add 2 tabs manually in browser
   - Auto-save triggers
   - Check JSON → groups still there, new tabs in ungrouped

2. **Test flat format:**
   - Load demo-session (flat format)
   - Add tabs
   - Save
   - Check JSON → still flat format

3. **Test new session:**
   - Start new session
   - Add tabs
   - Save as new name
   - Check JSON → flat format (no existing structure)

## Security Considerations
- [ ] File reading/writing is safe
- [ ] No code injection via JSON
- [ ] Validation still applies

## Rollback Plan
- Revert save_session() changes
- Groups still work for loading
- Just won't be preserved when saving

## Notes

### Matching Strategy
Use URL as primary key for matching:
- If `current_tab.url` exists in `group.tabs[].url`, keep in group
- If new URL, add to ungrouped
- If URL missing from current tabs, remove from group

### Example Flow
**Before save:**
```json
{
  "groups": [
    {"name": "Work", "tabs": [
      {"url": "https://github.com", "title": "GitHub"},
      {"url": "https://gmail.com", "title": "Gmail"}
    ]}
  ]
}
```

**User adds stackoverflow.com**

**After save:**
```json
{
  "groups": [
    {"name": "Work", "tabs": [
      {"url": "https://github.com", "title": "GitHub"},
      {"url": "https://gmail.com", "title": "Gmail"}
    ]}
  ],
  "ungrouped_tabs": [
    {"url": "https://stackoverflow.com", "title": "Stack Overflow"}
  ]
}
```

---

**Created:** 2025-12-06
**Status:** Todo
**Assignee:** Claude Code
