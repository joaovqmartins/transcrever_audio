# -*- mode: python ; coding: utf-8 -*-
"""Spec do PyInstaller: gera um executável único (sem precisar de Python
instalado) para o Audio Transcriber.

Como gerar o build (com o venv ativado e `pip install -r requirements-dev.txt`):

    pyinstaller build.spec

O executável final fica em dist/AudioTranscriber.exe (Windows) ou
dist/AudioTranscriber (Linux/macOS).
"""

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[("assets", "assets")],
    hiddenimports=[],
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
    name="AudioTranscriber",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icons/app_icon.ico",
)
