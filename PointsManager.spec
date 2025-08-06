# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os

# Список дополнительных данных (например, city.txt, settings.txt, requirements.txt)
datas = [
    ('settings.txt', '.'),
    ('requirements.txt', '.'),
    ('data/city.txt', 'data'),
    ('e:/Programming/Projects/Python/Points/.venv/lib/site-packages/pyproj/proj_dir', 'share/proj'),
    ('src/countries.geojson', 'src'),
]

hiddenimports = [
    'customtkinter',
    'loguru',
    'pandas',
    'openpyxl',
    'jinja2',
    'fiona',
    'pyogrio',
]

# Если нужны дополнительные скрытые импорты, добавьте их в hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PointsManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI приложение
    icon=None  # Можно указать путь к .ico
)
