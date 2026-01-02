# Visual Session Indicators - User Guide

## Problem Solved

Previously, when launching a browser session, there was **no way to tell**:
- ❌ Which browser was running (Chrome vs Brave look identical)
- ❌ If you were in incognito mode
- ❌ Which profile was active
- ❌ Browser window looked "generic" with no indicators

## Solution: Visual Indicators

Now when you launch a browser session, you get **THREE visual indicators**:

### 1. 🎨 Custom Start Page (First Tab)

When you launch a browser, the first tab shows a beautiful session info page:

**Features:**
- Large browser icon and name (Chrome 🌐, Brave 🦁, Firefox 🦊)
- Privacy mode badge (🔒 INCOGNITO or 📂 NORMAL)
- Profile information
- Browser-specific color scheme:
  - **Chrome**: Blue (#4285F4)
  - **Brave**: Orange (#FB542B)
  - **Firefox**: Orange (#FF7139)
  - **Incognito**: Dark Gray (#424242)
- "Start Browsing" and "New Tab" buttons

**Example Display:**
```
🦁
BRAVE

🔒 INCOGNITO MODE

📁 Profile: work

┌──────────────────┬──────────────────┐
│ Browser Type     │ Privacy Mode     │
│ BRAVE            │ Incognito        │
└──────────────────┴──────────────────┘

[Start Browsing] [New Tab]
```

### 2. 📍 Persistent Top Banner (All Pages)

Every page you visit shows a banner at the top with session info:

**Appearance:**
- Fixed at top of page
- Color-coded by browser/mode
- Shows: Browser | Mode | Profile
- Has "Hide" button to remove if desired
- High z-index (stays on top)

**Examples:**

**Chrome Normal Mode:**
```
┌────────────────────────────────────────────────────┐
│ 🌐 CHROME | NORMAL                      [Hide]    │ ← Blue background
└────────────────────────────────────────────────────┘
```

**Brave Incognito with Profile:**
```
┌───────────────────────────────────────────────────────────┐
│ 🌐 BRAVE | INCOGNITO | Profile: work        [Hide]      │ ← Dark gray
└───────────────────────────────────────────────────────────┘
```

**Firefox Normal Mode:**
```
┌────────────────────────────────────────────────────┐
│ 🌐 FIREFOX | NORMAL                     [Hide]    │ ← Orange background
└────────────────────────────────────────────────────┘
```

### 3. 🪟 Window Title Bar (Coming Soon)

Future enhancement will also customize the browser window title.

## Browser-Specific Colors

Each browser has a unique color scheme so you can identify it at a glance:

| Browser | Color | Icon |
|---------|-------|------|
| **Chrome** | Blue (#4285F4) | 🌐 |
| **Brave** | Orange (#FB542B) | 🦁 |
| **Firefox** | Orange (#FF7139) | 🦊 |
| **Chromium** | Gray (#5F6368) | 🌐 |

**Incognito mode** always uses **dark gray (#424242)** regardless of browser.

## How to Use

### Launch with Visual Indicators

**1. Desktop GUI:**
- Click "New Session"
- Select browser (Chrome, Brave, Firefox)
- Check "Incognito" if needed
- Enter profile name (optional)
- Click "Create"

**2. Command Line:**
```bash
# Chrome in normal mode
python tab_session_manager.py new --browser chrome

# Brave in incognito mode
python tab_session_manager.py new --browser brave --incognito

# Firefox with profile
python tab_session_manager.py new --browser firefox --profile work
```

### What You'll See

**On Launch:**
1. Browser opens with custom start page showing session info
2. Banner appears at top of page
3. Clear visual indication of browser type and mode

**When Opening New Tabs:**
1. Banner automatically appears on every new page
2. Can click "Hide" to remove banner temporarily
3. New tabs automatically get the indicator

## Technical Details

### Implementation

**File Modified:** `tab-session-manager/tab_session_manager.py`

**New Functions:**
1. `_show_session_info_page(page)` - Creates beautiful HTML start page
2. `_inject_session_indicator()` - Injects banner on all pages
3. `_get_indicator_injection_script()` - JavaScript for banner injection

**How It Works:**
1. On browser launch, creates custom HTML page with session info
2. Uses `context.add_init_script()` to inject banner on every page load
3. Tracks browser type, incognito mode, and profile name in instance variables
4. Generates browser-specific colors and icons dynamically

### Browser Detection

The system tracks:
- `self.current_browser_type` - 'chrome', 'brave', 'firefox', 'chromium'
- `self.current_incognito_mode` - True/False
- `self.current_profile_name` - Profile name or None

### Security Note

The banner is injected via `add_init_script()` which:
- ✅ Runs before page loads
- ✅ Works on all websites
- ✅ Can be hidden by user
- ✅ Doesn't interfere with page functionality
- ⚠️ May not work on some secure pages (chrome://, about:, etc.)

## Customization

### Change Banner Position

Edit `_get_indicator_injection_script()` line 507-523:

```python
# Change from top to bottom:
position: fixed;
bottom: 0;  # Instead of: top: 0;
```

### Change Banner Style

Modify the inline CSS in `_get_indicator_injection_script()`:

```python
# Make banner smaller:
padding: 4px 8px;  # Instead of: 8px 16px;
font-size: 11px;   # Instead of: 13px;
```

### Disable Banner (Keep Only Start Page)

Comment out line 252 in `tab_session_manager.py`:

```python
# self._inject_session_indicator()
```

### Custom Browser Icons/Colors

Edit `_show_session_info_page()` lines 314-325:

```python
elif browser_type_lower == 'edge':
    browser_icon = "📘"
    browser_color = "#0078D7"
```

## Examples

### Example 1: Chrome Incognito

```bash
python tab_session_manager.py new --browser chrome --incognito
```

**You'll See:**
- Start page with blue "CHROME" heading
- Dark gray "🔒 INCOGNITO MODE" badge
- Banner on all pages: "🌐 CHROME | INCOGNITO" with dark gray background

### Example 2: Brave with Work Profile

```bash
python tab_session_manager.py new --browser brave --profile work
```

**You'll See:**
- Start page with orange "BRAVE" heading and lion icon 🦁
- Green "📂 NORMAL MODE" badge
- "Profile: work" displayed prominently
- Banner on all pages: "🌐 BRAVE | NORMAL | Profile: work" with orange background

### Example 3: Firefox Normal Mode

```bash
python tab_session_manager.py new --browser firefox
```

**You'll See:**
- Start page with "FIREFOX" heading and fox icon 🦊
- Green "📂 NORMAL MODE" badge
- "No Profile (Ephemeral)" message
- Banner on all pages: "🌐 FIREFOX | NORMAL" with orange background

## Benefits

✅ **Instantly Identify Browser** - No more confusion between Chrome and Brave
✅ **Know Your Privacy Mode** - Clear indication of incognito status
✅ **Track Active Profile** - See which profile's cookies/history you're using
✅ **Visual Clarity** - Color-coded banners are hard to miss
✅ **Professional Look** - Beautiful start page with gradient background
✅ **User Control** - Can hide banner with one click

## Troubleshooting

**Problem**: Banner doesn't appear on some pages
**Solution**: Some secure pages (chrome://, about:, file://) block script injection. This is normal browser security.

**Problem**: Start page shows wrong browser name
**Solution**: Check that you're using the correct --browser flag or GUI selection.

**Problem**: Banner appears twice
**Solution**: Shouldn't happen - there's duplicate prevention code. If it does, refresh the page.

**Problem**: Want to permanently hide banner
**Solution**: Comment out line 252 in `tab_session_manager.py` (see Customization section).

## Version History

### v1.1 (Current)
- ✅ Added custom session info start page
- ✅ Added persistent top banner on all pages
- ✅ Browser-specific colors and icons
- ✅ Incognito mode visual indicators
- ✅ Profile name display

### v1.0 (Previous)
- ❌ No visual indicators
- ❌ Generic browser appearance

---

**Need more help?** See the main README or check INCOGNITO_MODE.md for privacy settings.
