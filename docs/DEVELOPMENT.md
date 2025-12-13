# Development Guide

This guide covers how to set up, develop, and build the Browser Automation project.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running in Development](#running-in-development)
- [Building for Production](#building-for-production)
- [Testing](#testing)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.8+** (Recommended: Python 3.10 or 3.11)
- **pip** (Python package manager)
- **Git** (for version control)
- **Chrome/Chromium Browser** (for Playwright automation)

### Optional

- **Node.js & npm** (for Chrome extension development)
- **Virtual environment tool** (venv, virtualenv, or conda)

---

## Project Structure

```
Browser/
├── docs/                           # Documentation files
│   └── DEVELOPMENT.md             # This file
├── tab-session-manager/           # Browser tab session manager
│   ├── desktop_gui/               # PyQt6 desktop application
│   │   ├── main.py               # GUI entry point
│   │   ├── dialogs/              # Dialog windows
│   │   ├── widgets/              # Custom widgets
│   │   └── utils/                # Utility functions
│   ├── sessions/                  # Saved session data (JSON)
│   ├── tab_session_manager.py    # Core session manager
│   └── requirements.txt          # Python dependencies
├── chrome-extension/              # Chrome extension for tab management
│   ├── manifest.json             # Extension manifest
│   ├── popup.html/css/js         # Extension UI
│   └── icons/                    # Extension icons
├── ai-tasks/                      # Project management system
│   ├── pm.db                     # SQLite database
│   ├── pm.md                     # PM documentation
│   └── run-pm.py                 # PM launcher script
├── CLAUDE.md                      # Project instructions
├── BROWSER_AUTOMATION.md          # Browser automation guide
└── .gitignore                     # Git ignore rules
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Browser
```

### 2. Set Up Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

**For Tab Session Manager:**

```bash
cd tab-session-manager
pip install -r requirements.txt
```

**For Desktop GUI:**

```bash
cd tab-session-manager/desktop_gui
pip install -r requirements.txt
```

**Install Playwright browsers:**

```bash
playwright install chromium
# Or for all browsers:
playwright install
```

### 4. Verify Installation

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify Playwright installation
playwright --version
```

---

## Running in Development

### Desktop GUI Application

**Quick Start:**

```bash
cd tab-session-manager/desktop_gui
python main.py
```

**With Virtual Environment:**

```bash
# Windows
venv\Scripts\activate
cd tab-session-manager\desktop_gui
python main.py

# macOS/Linux
source venv/bin/activate
cd tab-session-manager/desktop_gui
python main.py
```

### Tab Session Manager (CLI)

**Run the session manager:**

```bash
cd tab-session-manager
python tab_session_manager.py
```

**Common CLI commands:**

```bash
# Save current browser session
python tab_session_manager.py save my-session

# Load a session
python tab_session_manager.py load my-session

# List all sessions
python tab_session_manager.py list
```

### Chrome Extension

**Load Unpacked Extension:**

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `chrome-extension/` folder
5. The extension icon should appear in your toolbar

**Test the extension:**

1. Click the extension icon
2. Test saving/loading tab sessions
3. Check console for errors (F12 → Console)

### Project Management GUI

**Run the PM system:**

```bash
cd ai-tasks
python run-pm.py
```

**Access the web interface:**

Open browser to: `http://localhost:8000`

**Note:** Requires the AI PM GUI to be installed at `D:\Claude\ai-pm-gui`

---

## Building for Production

### Desktop GUI Application

**Option 1: PyInstaller (Recommended)**

```bash
# Install PyInstaller
pip install pyinstaller

# Navigate to GUI directory
cd tab-session-manager/desktop_gui

# Create executable
pyinstaller --name="BrowserSessionManager" \
            --windowed \
            --onefile \
            --icon=resources/icon.ico \
            main.py

# Output will be in dist/ folder
```

**Option 2: cx_Freeze**

```bash
# Install cx_Freeze
pip install cx_Freeze

# Create setup.py (see example below)
python setup.py build

# Output will be in build/ folder
```

**Example setup.py for cx_Freeze:**

```python
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["PyQt6", "playwright"],
    "include_files": ["resources/"]
}

setup(
    name="Browser Session Manager",
    version="1.0.0",
    description="Desktop GUI for managing browser tab sessions",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base="Win32GUI")]
)
```

### Chrome Extension

**Package for Chrome Web Store:**

1. **Prepare manifest:**
   - Ensure `manifest.json` has correct version
   - Add icons (16x16, 48x48, 128x128)
   - Update description and permissions

2. **Create ZIP package:**

```bash
cd chrome-extension
zip -r browser-tab-manager.zip . -x "*.git*" -x "*node_modules*"
```

3. **Upload to Chrome Web Store:**
   - Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - Upload ZIP file
   - Fill in store listing details
   - Submit for review

**For local distribution:**

- Share the `chrome-extension/` folder
- Users load it as unpacked extension

---

## Testing

### Manual Testing

**Desktop GUI:**

```bash
cd tab-session-manager/desktop_gui
python main.py
```

Test checklist:
- [ ] Search functionality works
- [ ] Session cards display correctly
- [ ] Right-click context menu works
- [ ] Session details dialog shows all tabs/groups
- [ ] All text is readable (black on light backgrounds)
- [ ] Create/delete sessions work
- [ ] Load session opens browser correctly

**Tab Session Manager:**

```bash
cd tab-session-manager
python test_browser.py
```

### Automated Tests (Future)

```bash
# Run unit tests (when implemented)
pytest tests/

# Run with coverage
pytest --cov=tab-session-manager tests/
```

---

## Common Tasks

### Update Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade pyqt6

# Generate updated requirements
pip freeze > requirements.txt
```

### Database Management

**Backup PM database:**

```bash
cp ai-tasks/pm.db ai-tasks/pm.db.backup
```

**Query database:**

```bash
cd ai-tasks
sqlite3 pm.db "SELECT * FROM tickets;"
```

### Clean Build Artifacts

```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove build directories
rm -rf build/ dist/ *.spec

# Remove virtual environment
rm -rf venv/
```

### Code Formatting (Optional)

```bash
# Install black formatter
pip install black

# Format Python files
black tab-session-manager/
black tab-session-manager/desktop_gui/
```

---

## Troubleshooting

### Playwright Issues

**Error: "Playwright browser not found"**

```bash
# Reinstall browsers
playwright install chromium --force
```

**Error: "Browser closed unexpectedly"**

- Check if Chrome is already running
- Try using headless mode: `headless=True` in code
- Update Playwright: `pip install --upgrade playwright`

### PyQt6 Issues

**Error: "No module named 'PyQt6'"**

```bash
# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

**GUI not displaying correctly:**

- Check display scaling settings
- Try running with `QT_AUTO_SCREEN_SCALE_FACTOR=1`
- Update graphics drivers

### Session Manager Issues

**Sessions not loading:**

- Check `sessions/` folder exists
- Verify JSON files are valid
- Check file permissions

**Browser not opening:**

- Ensure Playwright browsers are installed
- Check if Chrome/Chromium is in PATH
- Try running with `python -v` for verbose output

### General Python Issues

**Import errors:**

```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Version conflicts:**

```bash
# Create fresh virtual environment
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## Development Workflow

### Making Changes

1. **Create feature branch** (recommended):
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes** to code

3. **Test changes** thoroughly

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: Add my new feature"
   ```

5. **Merge to master**:
   ```bash
   git checkout master
   git merge feature/my-new-feature
   ```

### Commit Message Format

Follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Example:
```
feat: Add dark mode to desktop GUI

- Added dark mode toggle in settings
- Updated all widget stylesheets
- Persisted theme preference to settings
```

---

## Environment Variables

Create a `.env` file for configuration (optional):

```bash
# Browser settings
BROWSER_TYPE=chromium
HEADLESS=false

# Session settings
SESSION_DIR=./sessions
AUTO_SAVE_INTERVAL=3

# Development
DEBUG=true
LOG_LEVEL=INFO
```

---

## Resources

- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Playwright Python Docs](https://playwright.dev/python/docs/intro)
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## License

[Add your license information here]

---

## Support

For issues and questions:
- Check this documentation first
- Search existing issues in the issue tracker
- Create a new issue with detailed information

---

**Last Updated:** 2025-12-13
**Version:** 1.0.0
