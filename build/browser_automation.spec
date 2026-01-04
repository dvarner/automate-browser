# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Browser Automation Suite
Bundles Tab Session Manager, Workflow Engine, and Chrome Extension

Build with: pyinstaller browser_automation.spec
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from pathlib import Path

# Determine platform
IS_WINDOWS = sys.platform == 'win32'
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')

# Base paths
# SPECPATH is the directory containing the spec file (build/)
spec_root = os.path.abspath(SPECPATH)
# Project root is parent of build/
project_root = os.path.dirname(spec_root)

print(f"[DEBUG] SPECPATH: {SPECPATH}")
print(f"[DEBUG] spec_root: {spec_root}")
print(f"[DEBUG] project_root: {project_root}")

# Collect data files from packages
print("[*] Collecting Playwright data files...")
playwright_datas = collect_data_files('playwright', include_py_files=True)

print("[*] Collecting PyQt6 data files...")
pyqt6_datas = collect_data_files('PyQt6')

print("[*] Collecting PyYAML data files...")
pyyaml_datas = collect_data_files('yaml')

# Chrome extension files
print("[*] Bundling Chrome extension...")
chrome_ext_src = os.path.join(project_root, 'chrome-extension')
chrome_ext_datas = [
    (chrome_ext_src, 'chrome-extension'),
]

# Workflow templates and examples
print("[*] Bundling workflow templates...")
workflows_src = os.path.join(project_root, 'workflow-engine', 'workflows')
workflow_datas = []
if os.path.exists(workflows_src):
    workflow_datas = [
        (workflows_src, 'workflows'),
    ]

# Tab session manager source files
print("[*] Adding tab-session-manager modules...")
tab_session_src = os.path.join(project_root, 'tab-session-manager')

# Desktop GUI source files
desktop_gui_src = os.path.join(project_root, 'tab-session-manager', 'desktop_gui')

# Workflow engine source files
workflow_src = os.path.join(project_root, 'workflow-engine')

# Collect all submodules
print("[*] Collecting submodules...")
playwright_hiddenimports = collect_submodules('playwright')
pyqt6_hiddenimports = collect_submodules('PyQt6')

# Additional hidden imports
hidden_imports = [
    # Playwright
    'playwright',
    'playwright._impl',
    'playwright.sync_api',
    'playwright._impl._driver',
    'playwright._impl._api_types',
    'playwright._impl._api_structures',

    # PyQt6
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',

    # YAML
    'yaml',

    # Requests
    'requests',
    'urllib3',

    # Standard library
    'argparse',
    'threading',
    'json',
    'csv',
    'sqlite3',
]

# Combine all hidden imports
all_hidden_imports = list(set(hidden_imports + playwright_hiddenimports + pyqt6_hiddenimports))

# Analysis
a = Analysis(
    ['launcher.py'],
    pathex=[
        tab_session_src,
        desktop_gui_src,
        workflow_src,
    ],
    binaries=[],
    datas=playwright_datas + pyqt6_datas + pyyaml_datas + chrome_ext_datas + workflow_datas,
    hiddenimports=all_hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'ai-tasks',
        'ai-pm-gui',
        'test',
        'tests',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    optimize=0,
)

# Filter out unnecessary files
a.datas = [x for x in a.datas if not x[0].startswith('share/')]

# PYZ (Python ZIP archive)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# EXE
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BrowserAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # True = shows console for CLI mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'chrome-extension', 'icons', 'icon128.png') if IS_WINDOWS else None,
)

# COLLECT (gather all files into dist folder)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BrowserAutomation',
)

# macOS: Create .app bundle
if IS_MACOS:
    app = BUNDLE(
        coll,
        name='BrowserAutomation.app',
        icon=None,
        bundle_identifier='com.browserautomation.suite',
        info_plist={
            'CFBundleName': 'Browser Automation',
            'CFBundleDisplayName': 'Browser Automation Suite',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0',
            'NSHighResolutionCapable': 'True',
        },
    )

print("[+] Spec file configuration complete")
print(f"[*] Platform: {'Windows' if IS_WINDOWS else 'macOS' if IS_MACOS else 'Linux'}")
print(f"[*] Console mode: True (allows CLI and GUI)")
print(f"[*] Output name: BrowserAutomation")
