# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = []
hiddenimports += collect_submodules("pye3d")
hiddenimports += collect_submodules("mediapipe")
# there is a problem with Tk not finding some dynamically loaded modules,
# which is why we need to manually add them.
# https://stackoverflow.com/questions/52675162/pyinstaller-doesnt-play-well-with-imagetk-and-tkinter
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

splash = Splash(
    "assets/splash_screen.png",
    binaries=a.binaries,
    datas=a.datas,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    a.binaries,
    a.zipfiles,
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
