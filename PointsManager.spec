# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import glob

# Функция для сбора DLL из geo-пакетов
def collect_geo_dlls():
    binaries = []
    venv_path = r'D:\Projects\Points\.venv'

    # Пути к .libs директориям geo-пакетов
    libs_paths = [
        (f"{venv_path}\\Lib\\site-packages\\pyproj.libs", "pyproj.libs"),
        (f"{venv_path}\\Lib\\site-packages\\Shapely.libs", "Shapely.libs"),
        (f"{venv_path}\\Lib\\site-packages\\Fiona.libs", "Fiona.libs"),
        (f"{venv_path}\\Lib\\site-packages\\pyogrio.libs", "pyogrio.libs")
    ]

    for libs_path, dest_dir in libs_paths:
        if os.path.exists(libs_path):
            for dll in glob.glob(f"{libs_path}\\*.dll"):
                binaries.append((dll, dest_dir))
            # Также добавляем служебные файлы (.load-order-*)
            for load_order_file in glob.glob(f"{libs_path}\\.load-order-*"):
                binaries.append((load_order_file, dest_dir))

    return binaries

# Функция для сбора PROJ данных
def collect_proj_data():
    try:
        import pyproj
        proj_dir = pyproj.datadir.get_data_dir()
        if proj_dir and os.path.exists(proj_dir):
            return [(proj_dir, 'share/proj')]
    except:
        # Fallback для случая если pyproj.datadir недоступен
        venv_proj = r'D:\Projects\Points\.venv\Lib\site-packages\pyproj\proj_dir'
        if os.path.exists(venv_proj):
            return [(venv_proj, 'share/proj')]
    return []

# Список дополнительных данных
datas = [
    ('settings.txt', '.'),
    ('requirements.txt', '.'),
    ('data/city.txt', 'data'),
    ('src/countries.geojson', 'src'),
] + collect_proj_data()

# Добавляем целые .libs директории
venv_path = r'D:\Projects\Points\.venv'
libs_dirs = [
    (f"{venv_path}\\Lib\\site-packages\\pyproj.libs", "pyproj.libs"),
    (f"{venv_path}\\Lib\\site-packages\\Shapely.libs", "Shapely.libs"),
    (f"{venv_path}\\Lib\\site-packages\\Fiona.libs", "Fiona.libs"),
    (f"{venv_path}\\Lib\\site-packages\\pyogrio.libs", "pyogrio.libs")
]

for src_path, dest_path in libs_dirs:
    if os.path.exists(src_path):
        datas.append((src_path, dest_path))

# Добавляем fiona data если есть
try:
    import fiona
    fiona_path = os.path.dirname(fiona.__file__)
    gdal_data = os.path.join(fiona_path, 'gdal_data')
    proj_data = os.path.join(fiona_path, 'proj_data')
    if os.path.exists(gdal_data):
        datas.append((gdal_data, 'gdal_data'))
    if os.path.exists(proj_data):
        datas.append((proj_data, 'proj_data'))
except:
    pass

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
    binaries=collect_geo_dlls(),  # Добавляем собранные DLL
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
    upx=False,  # Отключено для совместимости с Windows 7
    console=False,  # GUI приложение
    icon=None  # Можно указать путь к .ico
)
