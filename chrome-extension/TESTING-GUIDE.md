# Chrome Extension Testing Guide

## Installation & Loading

### 1. Open Chrome Extensions Page

```
chrome://extensions/
```

Or: Menu (⋮) → Extensions → Manage Extensions

### 2. Enable Developer Mode

Toggle the "Developer mode" switch in the top-right corner

### 3. Load Extension

1. Click "Load unpacked" button
2. Navigate to: `D:\Claude\Automate\Browser\chrome-extension`
3. Click "Select Folder"

### 4. Verify Installation

- Extension appears in list as "Tab Session Exporter & Workflow Recorder v2.0.0"
- Pin it to toolbar: Click puzzle icon (🧩) → Pin

## Test Plan

### Test 1: Verify Extension Loads ✅

**Expected:**
- Extension icon appears in toolbar
- Clicking icon opens popup
- Popup shows two tabs: "📥 Export Tabs" and "🔴 Record Workflow"
- No console errors

**Steps:**
1. Click extension icon
2. Check popup displays correctly
3. Press F12 → Console tab
4. Verify no errors

---

### Test 2: Tab Export (Existing Feature) ✅

**Expected:**
- Export tabs functionality still works
- Groups are preserved

**Steps:**
1. Open several tabs in Chrome (at least 5)
2. Create a tab group (right-click tab → Add to new group)
3. Click extension icon
4. Stay on "Export Tabs" tab
5. Enter session name: `test-session`
6. Click "Export Session"
7. Save file to `tab-session-manager/sessions/`

**Verify:**
- JSON file downloads
- File contains tabs and groups
- No errors

---

### Test 3: Start Recording ✅

**Expected:**
- Recording starts
- Red indicator appears on page
- UI updates to show recording status

**Steps:**
1. Navigate to https://example.com
2. Click extension icon
3. Switch to "🔴 Record Workflow" tab
4. Click "Start Recording" button

**Verify:**
- Button becomes disabled
- "Stop Recording" button becomes enabled
- Status changes to "🔴 Recording..."
- Red recording indicator appears on page (top-right)
- No console errors

---

### Test 4: Capture Actions ✅

**Expected:**
- Clicks, fills, navigation are captured
- Actions appear in real-time

**Steps:**
1. With recording active, perform these actions:
   - Navigate to https://www.google.com
   - Click the search box
   - Type "playwright automation" in search box
   - Click "Google Search" button (or press Enter)
   - Wait for results to load

**Verify:**
- Navigate action captured with correct URL
- Fill action captured with search text
- Click action captured for search button
- Navigate action captured for results page
- Actions list shows all actions in order
- Action count updates (should show 3-4 actions)

---

### Test 5: Stop Recording ✅

**Expected:**
- Recording stops
- Red indicator disappears
- Actions remain visible

**Steps:**
1. Click "Stop Recording" button

**Verify:**
- "Start Recording" button becomes enabled again
- Status changes to "⚪ Ready to Record"
- Red indicator disappears from page
- Actions list still visible
- Action count preserved

---

### Test 6: Review Actions ✅

**Expected:**
- All actions listed correctly
- Can delete individual actions

**Steps:**
1. Review captured actions list
2. Click ✕ on one action to delete it
3. Verify action removed
4. Count remaining actions

**Verify:**
- Each action shows:
  - Action number
  - Action type (NAVIGATE, CLICK, FILL)
  - Details (URL, selector, value)
- Delete button works
- Action count decreases when deleted

---

### Test 7: Preview YAML ✅

**Expected:**
- Valid YAML preview appears

**Steps:**
1. Enter workflow name: `google-search-test`
2. Click "Preview YAML" button

**Verify:**
- YAML preview section appears
- Shows valid YAML format:
  ```yaml
  name: "google-search-test"
  browser: "chrome"
  timeout: 30
  steps:
    - action: navigate
      url: ...
  ```
- All captured actions included
- Comments present
- Proper indentation

---

### Test 8: Export YAML ✅

**Expected:**
- YAML file downloads
- File is valid

**Steps:**
1. Click "Export YAML" button
2. Save file to `workflow-engine/workflows/google-search-test.yaml`

**Verify:**
- File downloads successfully
- Alert shows save location
- File contains valid YAML

---

### Test 9: Run Exported Workflow ✅

**Expected:**
- Workflow runs successfully in workflow engine

**Steps:**
```bash
cd workflow-engine
python workflow_runner.py workflows/google-search-test.yaml
```

**Verify:**
- Workflow executes without errors
- Browser opens and navigates to Google
- Search query is entered
- Search is performed
- Results page loads

---

### Test 10: Clear Actions ✅

**Expected:**
- All actions cleared

**Steps:**
1. Click "Clear All" button
2. Confirm in dialog

**Verify:**
- Actions list becomes empty
- Action count shows 0
- "No actions captured yet" message appears

---

### Test 11: Complex Workflow ✅

**Expected:**
- Can record multi-step workflow with forms

**Steps:**
1. Start new recording
2. Navigate to a site with a form (e.g., contact form)
3. Fill multiple fields:
   - Text input
   - Email input
   - Textarea
   - Select dropdown (if available)
   - Checkbox (if available)
4. Click submit (don't actually submit)
5. Stop recording

**Verify:**
- All form fills captured
- Correct selectors generated
- Values captured correctly
- Email/password fields marked as sensitive if applicable

---

### Test 12: Navigation Between Pages ✅

**Expected:**
- Multi-page navigation captured
- Content script re-injected after navigation

**Steps:**
1. Start recording
2. Navigate to https://example.com
3. Click a link that goes to another page
4. Click another element on new page
5. Stop recording

**Verify:**
- Both navigate actions captured
- Click actions on both pages captured
- No errors during navigation
- Recording continues seamlessly

---

### Test 13: Password Field Handling ✅

**Expected:**
- Password values masked
- Marked as sensitive

**Steps:**
1. Find a login page (e.g., GitHub login, Gmail login)
2. Start recording
3. Fill password field with "test123"
4. Stop recording
5. Check actions list
6. Export YAML

**Verify:**
- Password value shows as `********` in UI
- YAML shows `sensitive: true`
- Value masked in YAML

---

### Test 14: Delete Individual Actions ✅

**Expected:**
- Can remove unwanted actions

**Steps:**
1. Record a workflow with 5+ actions
2. Delete the 2nd action (click ✕ button)
3. Delete the last action
4. Export YAML

**Verify:**
- Deleted actions removed from list
- Remaining actions renumbered correctly
- Action count updated
- Exported YAML doesn't include deleted actions

---

### Test 15: Tab Switching ✅

**Expected:**
- Can switch between Export and Record tabs

**Steps:**
1. Switch to "Export Tabs" tab
2. Verify tab export UI shows
3. Switch to "Record Workflow" tab
4. Verify recorder UI shows
5. Repeat 2-3 times

**Verify:**
- Tab content switches correctly
- Active tab highlighted
- No UI glitches
- State preserved when switching

---

## Troubleshooting Tests

### Test 16: Extension Reload

**Steps:**
1. Go to `chrome://extensions/`
2. Find extension
3. Click reload button (🔄)
4. Test recording again

**Verify:**
- Extension reloads without errors
- Functionality works after reload

### Test 17: Error Handling

**Steps:**
1. Try to start recording on a chrome:// page
2. Check console for errors

**Expected:**
- Graceful error handling
- User-friendly error message

### Test 18: Memory/Performance

**Steps:**
1. Record a workflow with 20+ actions
2. Check Chrome Task Manager (Shift+Esc)

**Expected:**
- Reasonable memory usage
- No memory leaks
- Recording remains responsive

---

## Success Criteria

All tests should pass with:
- ✅ No console errors
- ✅ Actions captured correctly
- ✅ YAML exports successfully
- ✅ Workflows run in engine
- ✅ UI responsive and functional
- ✅ Both tabs work independently

## Common Issues & Solutions

### Extension doesn't load
- Check folder path is correct
- Ensure Developer mode enabled
- Check console for errors

### Recording doesn't start
- Verify you're on a web page (not chrome:// page)
- Check activeTab permission granted
- Reload extension and try again

### Actions not captured
- Ensure recording indicator is visible
- Try clicking more slowly/deliberately
- Check content script injected (inspect page → check for content-script.js)

### YAML export fails
- Check downloads permission
- Try different filename
- Check browser download settings

### Workflow doesn't run
- Verify YAML syntax is valid
- Check selectors are correct
- Run with --headless flag for debugging

---

## Next Steps After Testing

If all tests pass:
1. ✅ Extension is production ready
2. ✅ Create example workflows
3. ✅ Document common patterns
4. ✅ Share with users

If issues found:
1. Document the issue
2. Check console errors
3. Fix bugs
4. Re-test
5. Iterate until all pass
