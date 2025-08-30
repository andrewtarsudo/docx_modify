# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = []
binaries += collect_dynamic_libs('.')


a = Analysis(
    ['../__main__.py'],
    pathex=['.'],
    binaries=binaries,
    datas=[('../sources/', './sources/'), ('../MANIFEST.in', '.'), ('../pyproject.toml', '.')],
    hiddenimports=['loguru', 'lxml', 'colorama', 'win32-setctime', 'pyside6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='docx_modify.exe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
