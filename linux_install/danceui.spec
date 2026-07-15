import os
from PyInstaller.utils.hooks import collect_data_files, collect_all

block_cipher = None

# Collect all Streamlit static assets and metadata
streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all("streamlit")
plotly_datas, plotly_binaries, plotly_hiddenimports = collect_all("plotly")

datas = (
    streamlit_datas
    + plotly_datas
    + [("danceui.py", ".")]
)

binaries = streamlit_binaries + plotly_binaries

hiddenimports = (
    streamlit_hiddenimports
    + plotly_hiddenimports
    + [
        "streamlit.runtime.scriptrunner.magic_funcs",
        "pandas",
        "numpy",
        "openpyxl",
        "altair",
    ]
)

a = Analysis(
    ["run_app.py"],
    pathex=[os.path.abspath(".")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DanceUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DanceUI",
)
