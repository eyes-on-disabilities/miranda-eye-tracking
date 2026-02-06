# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = []
hiddenimports += collect_submodules("pye3d")
hiddenimports += collect_submodules("mediapipe")
hiddenimports += ["PIL._tkinter_finder"]

datas = []
datas += collect_data_files("pye3d", includes=["refraction_models/*.msgpack"])
datas += collect_data_files("assets", includes=["*.png", "*.ico"])
datas += collect_data_files(
    "mediapipe",
    includes=[
        "**/*.binarypb",
        "**/*.tflite",
        "**/*.pbtxt",
        "**/*.txt",
    ],
)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Miranda",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/icon.ico",
    onefile=True,
)
