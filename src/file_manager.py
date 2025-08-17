
"""
Модуль для работы с файлами и папками.

Этот модуль содержит функции для поиска папок и файлов по различным критериям.
Все функции снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""


import os
from typing import List


def find_folders_missing_data_csv(root_folder: str) -> List[str]:
    """
    Находит все папки, где присутствуют файлы формата XML или JSON, но отсутствует файл data.xlsx
    и отсутствует файл points_without_city.csv.

    Args:
        root_folder (str): Путь к корневой папке для поиска.

    Returns:
        List[str]: Список путей к найденным папкам.

    Примечание:
        Папки с именем 'bad' игнорируются.
        Папки с уже существующим файлом points_without_city.csv также игнорируются.
    """
    # Проходим по всем папкам и файлам внутри root_folder
    return [
        dirpath
        for dirpath, _, filenames in os.walk(root_folder)
        # Исключаем папки 'bad'
        if os.path.basename(dirpath).lower() != "bad"
        # Проверяем наличие хотя бы одного xml или json файла
        and any(f.lower().endswith((".xml", ".json")) for f in filenames)
        # Проверяем отсутствие файла data.xlsx
        and not any(f.lower() == "data.xlsx" for f in filenames)
        # Проверяем отсутствие файла points_without_city.csv
        and not any(f.lower() == "points_without_city.csv" for f in filenames)
    ]
