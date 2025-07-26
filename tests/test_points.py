import os
import tempfile
import shutil
import csv
import pytest
from models.points import PointsData, PointRecord

def make_csv(filepath, rows):
    fieldnames = [
        'Data', 'Time', 'Lat_WGS84', 'Lon_WGS84',
        'X_SK-42_Gauss_Kruger', 'Y_SK-42_Gauss_Kruger',
        'Country_Value', 'City_Value',
        'Description of the area', 'Description of the region',
        'Original text'
    ]
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def test_load_and_find(tmp_path):
    csv_path = tmp_path / 'AllPoint.csv'
    make_csv(csv_path, [
        {
            'Data': '01.01.2025', 'Time': '12:00',
            'Lat_WGS84': '50,123', 'Lon_WGS84': '36,456',
            'X_SK-42_Gauss_Kruger': '1234567', 'Y_SK-42_Gauss_Kruger': '7654321',
            'Country_Value': 'Россия', 'City_Value': 'Белгород',
            'Description of the area': 'desc', 'Description of the region': 'reg',
            'Original text': '<point>...</point>'
        }
    ])
    pd = PointsData(str(csv_path))
    assert len(pd.points) == 1
    rec = pd.find_by_lat_lon(50.123, 36.456)
    assert rec is not None
    assert rec.city == 'Белгород'

def test_add_point_and_save(tmp_path):
    csv_path = tmp_path / 'AllPoint.csv'
    make_csv(csv_path, [])
    pd = PointsData(str(csv_path))
    new_point = PointRecord(
        date='02.02.2025', time='13:00', latitude=51.0, longitude=37.0,
        x_sk42=111, y_sk42=222, country='Россия', city='Москва',
        area_desc='area', region_desc='region', original_text='<point/>'
    )
    pd.add_point(new_point)
    pd.save()
    # Проверяем, что точка сохранилась
    pd2 = PointsData(str(csv_path))
    found = pd2.find_by_lat_lon(51.0, 37.0)
    assert found is not None
    assert found.city == 'Москва'

def test_backup_created_and_limited(tmp_path):
    csv_path = tmp_path / 'AllPoint.csv'
    make_csv(csv_path, [])
    pd = PointsData(str(csv_path))
    for i in range(12):
        pd.save()
    backup_dir = os.path.join(tmp_path, 'backup')
    backups = [f for f in os.listdir(backup_dir) if f.startswith('AllPoint.csv') and f.endswith('.bak')]
    assert len(backups) <= 10
