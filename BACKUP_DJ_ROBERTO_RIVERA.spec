from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

project_root = Path(SPECPATH).resolve()
datas = []
# Required model is bundled inside the executable. The build fails if absent.
model_dir = project_root / 'models'
for filename in ('discogs-effnet-bsdynamic-1.onnx', 'discogs-effnet-bsdynamic-1.json'):
    model_file = model_dir / filename
    if not model_file.is_file():
        raise FileNotFoundError(f'Required pretrained AI model missing: {model_file}')
    datas.append((str(model_file), 'models'))
binaries = []
hiddenimports = collect_submodules("app")

# Collect Qt plugins/resources and runtime dependencies used by the application.
for package in ["PySide6", "mutagen", "soundfile", "librosa", "onnxruntime", "certifi", "truststore"]:
    try:
        package_datas, package_binaries, package_hidden = collect_all(package)
        datas += package_datas
        binaries += package_binaries
        hiddenimports += package_hidden
    except Exception as exc:
        print(f"Optional collection skipped for {package}: {exc}")

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MI_BACK_UP",
    icon=str(project_root / "assets" / "icons" / "mi_backup.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)
