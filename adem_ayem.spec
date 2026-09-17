# Build with: pyinstaller --clean --noconfirm adem_ayem.spec
from PyInstaller.utils.hooks import collect_data_files


kivy_data = collect_data_files("kivy")

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=kivy_data + [("assets/generated", "assets/generated")],
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
    name="PemancinganAdemAyemDlopo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/generated/brand-adem-ayem-icon.png",
)
