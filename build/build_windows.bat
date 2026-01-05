@echo off
REM ====================================================================
REM Browser Automation Suite - Windows 11 Build Script
REM ====================================================================
REM
REM This script builds a standalone executable for Windows 11
REM Includes: Tab Session Manager, Workflow Engine, Chrome Extension
REM
REM Prerequisites:
REM   - Python 3.8+ installed
REM   - pip install -r requirements-build.txt
REM   - python -m playwright install
REM
REM Usage:
REM   build_windows.bat
REM
REM ====================================================================

echo.
echo ====================================================================
echo   Browser Automation Suite - Windows 11 Build
echo ====================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] ERROR: Python not found
    echo     Please install Python 3.8+ and add to PATH
    exit /b 1
)

echo [*] Python detected:
python --version
echo.

REM ====================================================================
REM Step 1: Clean previous builds
REM ====================================================================
echo [1/7] Cleaning previous builds...

if exist dist (
    echo       Removing dist/
    rmdir /s /q dist
)

if exist build (
    echo       Removing build/
    rmdir /s /q build
)

if exist __pycache__ (
    rmdir /s /q __pycache__
)

echo       [+] Cleanup complete
echo.

REM ====================================================================
REM Step 2: Verify dependencies
REM ====================================================================
echo [2/7] Verifying dependencies...

python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo       [!] ERROR: playwright not installed
    echo           Run: pip install -r requirements-build.txt
    exit /b 1
)
echo       [+] playwright

python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo       [!] ERROR: PyQt6 not installed
    echo           Run: pip install -r requirements-build.txt
    exit /b 1
)
echo       [+] PyQt6

python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo       [!] ERROR: PyYAML not installed
    echo           Run: pip install -r requirements-build.txt
    exit /b 1
)
echo       [+] PyYAML

python -c "import pyinstaller" >nul 2>&1
if errorlevel 1 (
    echo       [!] ERROR: pyinstaller not installed
    echo           Run: pip install -r requirements-build.txt
    exit /b 1
)
echo       [+] pyinstaller

echo       [+] All dependencies verified
echo.

REM ====================================================================
REM Step 3: Check Playwright browsers
REM ====================================================================
echo [3/7] Checking Playwright browsers...

python -c "from playwright.driver import compute_driver_executable; from pathlib import Path; browsers = Path(compute_driver_executable()).parent.parent / 'browsers'; exit(0 if browsers.exists() else 1)" >nul 2>&1

if errorlevel 1 (
    echo       [!] WARNING: Playwright browsers not found
    echo           Downloading browsers (this may take a few minutes)...
    python -m playwright install
    if errorlevel 1 (
        echo       [!] ERROR: Failed to download browsers
        exit /b 1
    )
)

echo       [+] Playwright browsers available
echo.

REM ====================================================================
REM Step 4: Build with PyInstaller
REM ====================================================================
echo [4/7] Building executable with PyInstaller...
echo       (This may take 5-10 minutes)
echo.

pyinstaller browser_automation.spec

if errorlevel 1 (
    echo.
    echo       [!] ERROR: PyInstaller build failed
    echo           Check the output above for errors
    exit /b 1
)

echo.
echo       [+] PyInstaller build complete
echo.

REM ====================================================================
REM Step 5: Bundle Playwright browsers
REM ====================================================================
echo [5/7] Bundling Playwright browsers...
echo       (This may take 3-5 minutes)
echo.

python bundle_browsers.py

if errorlevel 1 (
    echo.
    echo       [!] ERROR: Browser bundling failed
    exit /b 1
)

echo.

REM ====================================================================
REM Step 6: Create runtime folders
REM ====================================================================
echo [6/7] Creating runtime folders...

if not exist "dist\BrowserAutomation\sessions" (
    mkdir "dist\BrowserAutomation\sessions"
    echo       [+] Created sessions/
)

if not exist "dist\BrowserAutomation\profiles" (
    mkdir "dist\BrowserAutomation\profiles"
    echo       [+] Created profiles/
)

echo       [+] Runtime folders ready
echo.

REM ====================================================================
REM Step 7: Copy documentation
REM ====================================================================
echo [7/7] Copying documentation and assets...

if exist "..\README.md" (
    copy /y "..\README.md" "dist\BrowserAutomation\" >nul
    echo       [+] README.md
)

if exist "..\chrome-extension\README.md" (
    copy /y "..\chrome-extension\README.md" "dist\BrowserAutomation\EXTENSION-README.md" >nul
    echo       [+] EXTENSION-README.md
)

if exist "..\LICENSE" (
    copy /y "..\LICENSE" "dist\BrowserAutomation\" >nul
    echo       [+] LICENSE
)

echo       [+] Documentation copied
echo.

REM ====================================================================
REM Build Summary
REM ====================================================================
echo ====================================================================
echo   BUILD COMPLETE!
echo ====================================================================
echo.
echo Output Location:
echo   dist\BrowserAutomation\
echo.
echo Executable:
echo   dist\BrowserAutomation\BrowserAutomation_*.exe (timestamped)
echo.
echo Folder Structure:
echo   BrowserAutomation_*.exe       - Main executable (timestamped)
echo   chrome-extension/             - Chrome extension files
echo   workflows/                    - Example YAML workflows
echo   sessions/                     - Session storage (empty)
echo   profiles/                     - Browser profiles (empty)
echo   playwright/browsers/          - Bundled browser binaries
echo.

REM Get folder size
for /f "tokens=3" %%a in ('dir /s /-c "dist\BrowserAutomation" 2^>nul ^| findstr /C:"bytes"') do set size=%%a
if defined size (
    set /a size_mb=size / 1048576
    echo Estimated Size: ~!size_mb! MB
    echo.
)

echo TESTING:
echo   1. GUI Mode:      Double-click BrowserAutomation_*.exe
echo   2. CLI Mode:      BrowserAutomation_*.exe list
echo   3. Workflow Mode: BrowserAutomation_*.exe workflow test.yaml
echo.
echo DISTRIBUTION:
echo   Zip the entire BrowserAutomation/ folder for distribution
echo.
echo ====================================================================
echo.

pause
