"""
Модуль для работы с файлами и папками.
Содержит функции поиска папок и файлов по различным критериям.
"""

import os
from typing import List


def find_folders_missing_data_csv(rootFolder: str) -> List[str]:
    """
    Находит все папки, в которых отсутствует файл data.xlsx.

    Args:
        rootFolder (str): Корневая папка для поиска

    Returns:
        List[str]: Список путей к папкам без data.xlsx
    """
    result: List[str] = []
    for dirpath, dirnames, filenames in os.walk(rootFolder):
        if os.path.basename(dirpath).lower() == "bad":
            continue
        has_xml_or_json = any(f.lower().endswith((".xml", ".json")) for f in filenames)
        has_data_csv = any(f.lower() == "data.xlsx" for f in filenames)
        if has_xml_or_json and not has_data_csv:
            result.append(dirpath)
    return result
