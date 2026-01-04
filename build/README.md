# Browser Automation Suite - Build Instructions

This directory contains the build system for creating standalone executables of the Browser Automation Suite for Windows 11 and macOS.

## Quick Start (Windows 11)

```batch
# 1. Install build dependencies
pip install -r requirements-build.txt

# 2. Download Playwright browsers
python -m playwright install

# 3. Build executable
build_windows.bat
```

The executable will be created in `dist/BrowserAutomation/`.

---

## Build Files Overview

| File | Purpose |
|------|---------|
| `launcher.py` | Unified entry point that routes to CLI/GUI/Workflow modes |
| `browser_automation.spec` | PyInstaller configuration file |
| `bundle_browsers.py` | Post-build script to bundle Playwright browsers |
| `build_windows.bat` | Automated Windows build script |
| `build_macos.sh` | Automated macOS build script (future) |
| `requirements-build.txt` | Build dependencies |

---

## Prerequisites

### Windows 11

- **Python 3.8 or higher**
- **pip** (comes with Python)
- **Microsoft Visual C++ Redistributable** (usually pre-installed)

### macOS

- **Python 3.8 or higher**
- **Xcode Command Line Tools** (`xcode-select --install`)
- **(Optional) Apple Developer ID** for code signing

---

## Detailed Build Process

### Step 1: Install Dependencies

```bash
pip install -r requirements-build.txt
```

This installs:
- `pyinstaller` - Packaging tool
- `playwright` - Browser automation
- `PyQt6` - Desktop GUI framework
- `PyYAML` - YAML parser
- `requests` - HTTP library

### Step 2: Download Playwright Browsers

```bash
python -m playwright install
```

Downloads Chromium, Firefox, and WebKit binaries (~250-300MB).

### Step 3: Build Executable

#### Windows:
```batch
build_windows.bat
```

#### macOS (future):
```bash
chmod +x build_macos.sh
./build_macos.sh
```

#### Manual Build:
```bash
# From build/ directory
pyinstaller browser_automation.spec
python bundle_browsers.py
```

### Step 4: Test the Executable

```bash
cd dist/BrowserAutomation

# Test GUI mode
BrowserAutomation.exe

# Test CLI mode
BrowserAutomation.exe list

# Test workflow mode
BrowserAutomation.exe workflow ../workflow-engine/workflows/example-google-search.yaml
```

---

## Build Output

The `dist/BrowserAutomation/` folder contains:

```
BrowserAutomation/
├── BrowserAutomation.exe           # Main executable (~50MB)
├── chrome-extension/                # Chrome extension files
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   └── icons/
├── workflows/                       # Example YAML workflows
│   ├── example-google-search.yaml
│   └── ...
├── sessions/                        # Session storage (empty)
├── profiles/                        # Browser profiles (empty)
├── playwright/                      # Playwright files
│   └── browsers/                    # Browser binaries (~300MB)
│       ├── chromium-*/
│       ├── firefox-*/
│       └── webkit-*/
├── _internal/                       # Python runtime and dependencies
└── README.md                        # User documentation
```

**Total Size:** ~400-500MB (with bundled browsers)

---

## Distribution

### Windows

Create a ZIP archive:
```batch
cd dist
tar -acf BrowserAutomation-v2.0-Windows.zip BrowserAutomation
```

Or use 7-Zip/WinRAR to create a compressed archive.

### macOS (future)

Create a DMG installer:
```bash
hdiutil create -volname "Browser Automation" \
    -srcfolder dist/BrowserAutomation.app \
    -ov -format UDZO \
    BrowserAutomation-v2.0-macOS.dmg
```

---

## Troubleshooting

### Build Errors

**Error: "playwright module not found"**
```bash
pip install playwright>=1.40.0
```

**Error: "PyQt6 module not found"**
```bash
pip install PyQt6>=6.6.0
```

**Error: "Browser binaries not found"**
```bash
python -m playwright install
```

**Error: "PyInstaller build failed"**
- Check Python version (must be 3.8+)
- Reinstall PyInstaller: `pip install --upgrade pyinstaller`
- Run manually: `pyinstaller browser_automation.spec --clean`

### Runtime Errors

**Error: "Failed to launch browser"**
- Verify browsers are bundled: Check `dist/BrowserAutomation/playwright/browsers/`
- Re-run `python bundle_browsers.py`

**Error: "PyQt6 platform plugin not found"**
- PyQt6 plugins missing from build
- Add to `browser_automation.spec` hidden imports

**Error: "Chrome extension not found"**
- Verify `dist/BrowserAutomation/chrome-extension/` exists
- Check spec file includes chrome-extension in `datas`

---

## Advanced Configuration

### Reducing Executable Size

Edit `browser_automation.spec`:

1. **Exclude unused browsers:**
   ```python
   # In bundle_browsers.py, only copy chromium:
   browsers = [d for d in src.iterdir() if d.name.startswith('chromium')]
   ```

2. **Disable UPX compression:**
   ```python
   upx=False,  # Faster build, larger size
   ```

3. **Use one-file mode:**
   ```python
   exe = EXE(
       ...
       exclude_binaries=False,  # Single EXE
   )
   ```

### Adding Custom Icons

Replace `chrome-extension/icons/icon128.png` with your custom icon (128x128 PNG).

For Windows, convert to `.ico`:
```bash
pip install pillow
python -c "from PIL import Image; Image.open('icon.png').save('icon.ico')"
```

Update spec file:
```python
icon='path/to/icon.ico'
```

---

## Build System Architecture

```
launcher.py
   ├─> CLI Mode (tab_session_manager.py)
   ├─> GUI Mode (desktop_gui/main.py)
   └─> Workflow Mode (workflow_runner.py)

PyInstaller Spec File
   ├─> Collects Python modules
   ├─> Bundles PyQt6, Playwright, PyYAML
   ├─> Includes chrome-extension/
   └─> Includes workflow templates

bundle_browsers.py
   └─> Copies Playwright browsers to dist/
```

---

## macOS Build (Future)

### Differences from Windows

1. **No .bat script** - Use `.sh` shell script
2. **Code signing required** for distribution
3. **Create .app bundle** and .dmg installer
4. **Gatekeeper compatibility** testing needed

### Build Steps

```bash
# Install dependencies
pip3 install -r requirements-build.txt
python3 -m playwright install

# Build
./build_macos.sh

# Sign (optional, for distribution)
codesign --force --deep --sign "Developer ID" \
    dist/BrowserAutomation.app

# Create DMG
hdiutil create -volname "Browser Automation" \
    -srcfolder dist/BrowserAutomation.app \
    -ov -format UDZO \
    BrowserAutomation.dmg
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd build
          pip install -r requirements-build.txt
          python -m playwright install
          build_windows.bat
      - uses: actions/upload-artifact@v3
        with:
          name: BrowserAutomation-Windows
          path: build/dist/BrowserAutomation/
```

---

## Support

For issues with the build process:

1. Check this README
2. Review build output for error messages
3. Verify all prerequisites are installed
4. Try manual build steps one by one
5. Open an issue on GitHub with build logs

---

**Last Updated:** 2026-01-04
**Build System Version:** 1.0
**Target Platforms:** Windows 11, macOS 11+ (Big Sur and newer)
