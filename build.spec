# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build specification.

Build with:
    pyinstaller build.spec --noconfirm

Produces:
    Windows -> dist/BusinessDocGenerator/BusinessDocGenerator.exe
    macOS   -> dist/BusinessDocGenerator.app

Notes
-----
* ``templates/`` is bundled so the app works out of the box. A ``templates/``
  folder placed next to the executable overrides the bundled one, so the
  business teams can adjust the document structures without a rebuild
  (see core/config.templates_dir).
* ``.env`` is deliberately NOT bundled -- the API key must never be baked into
  a distributed binary. Deployment drops a ``.env`` next to the executable.
* One-folder (not one-file) output is used: it starts faster and makes the
  adjacent ``.env`` / ``templates/`` story obvious to whoever deploys it.
"""

import sys

APP_NAME = "BusinessDocGenerator"

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    # (source, destination-inside-bundle)
    datas=[("templates", "templates")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Trim large unused PyQt6 modules to keep the build small.
    excludes=[
        "tkinter",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtMultimedia",
        "PyQt6.QtQuick",
        "PyQt6.Qt3DCore",
        "matplotlib",
        "numpy",
        "pytest",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # GUI app: no console window
    disable_windowed_traceback=False,
    argv_emulation=False,   # set True only if macOS file-drop support is wanted
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/app.ico",   # add an icon file here if the company has one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)

# macOS: wrap the collected folder into a proper .app bundle.
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=None,           # "assets/app.icns"
        bundle_identifier="jp.co.twave.businessdocgenerator",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": "1.0.0",
        },
    )
