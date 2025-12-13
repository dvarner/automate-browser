# Incognito Mode in Playwright

## Current Behavior

Playwright's `browser.new_context()` already creates isolated contexts (similar to incognito):
- ✅ No shared cookies
- ✅ No shared cache
- ✅ No shared localStorage
- ✅ Fresh session each time

## Enhanced Incognito Mode

For maximum privacy, you can configure additional options:

### Option 1: Basic Incognito (Recommended)

```python
self.context = self.browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    accept_downloads=True,
    ignore_https_errors=False,  # Keep HTTPS validation
    java_script_enabled=True,

    # Privacy enhancements
    locale='en-US',
    timezone_id='America/New_York',
    permissions=[],  # No permissions by default
    geolocation=None,  # No geolocation
    color_scheme='light',
)
```

### Option 2: Maximum Privacy

```python
self.context = self.browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',

    # Block tracking
    ignore_https_errors=False,
    accept_downloads=True,

    # Privacy settings
    locale='en-US',
    timezone_id='America/New_York',
    permissions=[],
    geolocation=None,

    # Extra privacy
    viewport={'width': 1920, 'height': 1080},  # Standard viewport
    screen={'width': 1920, 'height': 1080},
    device_scale_factor=1,
    is_mobile=False,
    has_touch=False,

    # Storage
    storage_state=None,  # No cookies/localStorage loaded

    # Extras
    extra_http_headers={
        'DNT': '1',  # Do Not Track
    }
)
```

### Option 3: True Incognito with Chrome Args

For the closest experience to Chrome's incognito mode:

```python
self.browser = self.playwright.chromium.launch(
    headless=False,
    args=[
        '--remote-debugging-port=9222',
        '--incognito',  # ← Add this
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-web-security',  # Remove this for better privacy

        # Additional privacy args
        '--disable-extensions',
        '--disable-plugins',
        '--disable-plugins-discovery',
        '--disable-background-networking',
        '--disable-sync',
        '--disable-translate',
        '--hide-scrollbars',
        '--metrics-recording-only',
        '--mute-audio',
        '--no-first-run',
        '--safebrowsing-disable-auto-update',
        '--disable-client-side-phishing-detection',
        '--disable-component-update',
        '--disable-default-apps',
        '--disable-domain-reliability',
    ]
)

self.context = self.browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    ignore_https_errors=False,
    accept_downloads=True,
    permissions=[],
    extra_http_headers={'DNT': '1'}
)
```

## Implementation

### Quick Change (Recommended)

Edit `tab_session_manager.py` line 96-98:

**Before:**
```python
self.context = self.browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)
```

**After:**
```python
self.context = self.browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    accept_downloads=True,
    ignore_https_errors=False,
    permissions=[],
    extra_http_headers={'DNT': '1'}  # Do Not Track
)
```

### Add `--incognito` Flag

Edit `tab_session_manager.py` line 88-93:

**Before:**
```python
args=[
    '--remote-debugging-port=9222',
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-web-security',
]
```

**After:**
```python
args=[
    '--remote-debugging-port=9222',
    '--incognito',  # ← Add this line
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    # '--disable-web-security',  # Comment out for better privacy
]
```

## What Each Setting Does

### Browser Launch Args

| Arg | Purpose |
|-----|---------|
| `--incognito` | Launches in incognito mode (closes tabs when browser closes) |
| `--disable-extensions` | No extensions loaded |
| `--disable-sync` | No Chrome sync |
| `--disable-translate` | No Google Translate |
| `--disable-background-networking` | No background connections |

### Context Options

| Option | Purpose |
|--------|---------|
| `permissions=[]` | No permissions granted by default |
| `geolocation=None` | No location access |
| `storage_state=None` | No cookies/localStorage loaded |
| `extra_http_headers={'DNT': '1'}` | Send Do Not Track header |

## Testing

After making changes, test with:

```bash
python tab_session_manager.py new
```

You should see:
- Fresh browser with no history
- No cookies from previous sessions
- No saved passwords/autofill
- Isolated from other browser instances

## Trade-offs

### More Privacy = Some Limitations

**Benefits:**
- ✅ No tracking between sessions
- ✅ No cookies persist
- ✅ No browsing history
- ✅ Fresh start every time

**Limitations:**
- ❌ Can't stay logged in between sessions
- ❌ No saved passwords
- ❌ Some websites may behave differently
- ❌ Need to re-authenticate each time

## Persistent Sessions (If Needed)

If you need to stay logged in across sessions:

```python
# Save state after login
self.context.storage_state(path="auth_state.json")

# Load state in next session
self.context = self.browser.new_context(
    storage_state="auth_state.json"  # ← Load cookies/localStorage
)
```

## Recommendations

### For General Use:
Use **Option 1** (Basic Incognito) - Good balance of privacy and usability

### For Maximum Privacy:
Use **Option 3** (True Incognito) - Most private, but some sites may not work

### For Session Persistence:
Don't use incognito mode - Use `storage_state` to save/load cookies

## Current vs Enhanced

### Current (Already Pretty Private)
```python
✅ Isolated context
✅ No shared cookies
✅ Fresh session
❌ Some tracking possible
❌ Chrome knows it's automated
```

### Enhanced (Maximum Privacy)
```python
✅ Isolated context
✅ No shared cookies
✅ Fresh session
✅ Do Not Track header
✅ No background connections
✅ True incognito flag
✅ Minimal tracking
```

## See Also

- [Playwright Context Documentation](https://playwright.dev/python/docs/browser-contexts)
- [Chrome Command Line Switches](https://peter.sh/experiments/chromium-command-line-switches/)
- [Privacy Settings Guide](https://playwright.dev/python/docs/emulation)
