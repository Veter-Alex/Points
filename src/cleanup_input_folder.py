
"""
Модуль для очистки папки INPUT и обработки папок bad.

Содержит функции для удаления лишних файлов и обработки папок bad.
Все функции снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""

import os
import shutil
from typing import Optional, Callable




def clean_input_folder(input_folder: str, progress_callback: Optional[Callable[[str], None]] = None) -> None:
    """
    Удаляет все файлы в input_folder, кроме xml, json, spr.

    Args:
        input_folder (str): Путь к папке для очистки.
        progress_callback (Optional[Callable[[str], None]]): Функция для отображения прогресса.
    """
    if progress_callback:
        progress_callback("Подсчет файлов для удаления...")
    # Собираем список файлов для удаления (кроме xml, json, spr)
    files_to_delete = [
        os.path.join(root, file)
        for root, _, files in os.walk(input_folder)
        for file in files
        if os.path.splitext(file)[1].lower() not in {".xml", ".json", ".spr"}
    ]
    total_files = len(files_to_delete)
    if progress_callback:
        progress_callback(f"Найдено {total_files} файлов для удаления")
    # Удаляем файлы по одному, с обработкой ошибок
    for i, file_path in enumerate(files_to_delete, 1):
        try:
            os.remove(file_path)
            msg = f"Удален файл ({i}/{total_files}): {os.path.basename(file_path)}"
        except Exception as e:
            msg = f"Ошибка удаления {os.path.basename(file_path)}: {e}"
        if progress_callback:
            progress_callback(msg)
    if progress_callback:
        progress_callback(f"Удаление файлов завершено. Удалено: {total_files} файлов")




def process_bad_folders(input_folder: str, progress_callback: Optional[Callable[[str], None]] = None) -> None:
    """
    Находит все папки bad, переносит их содержимое на уровень выше и удаляет папку bad.

    Args:
        input_folder (str): Путь к папке для поиска bad-папок.
        progress_callback (Optional[Callable[[str], None]]): Функция для отображения прогресса.
    """
    if progress_callback:
        progress_callback("Поиск папок 'bad'...")
    # Находим все папки с именем 'bad'
    bad_folders = [
        os.path.join(root, d)
        for root, dirs, _ in os.walk(input_folder)
        for d in dirs if d == "bad"
    ]
    total_bad_folders = len(bad_folders)
    if progress_callback:
        progress_callback(f"Найдено {total_bad_folders} папок 'bad' для обработки")
    # Обрабатываем каждую bad-папку
    for i, bad_path in enumerate(bad_folders, 1):
        parent_path = os.path.dirname(bad_path)
        if progress_callback:
            progress_callback(f"Обработка папки 'bad' ({i}/{total_bad_folders}): {bad_path}")
        try:
            files_in_bad = os.listdir(bad_path)
        except Exception as e:
            if progress_callback:
                progress_callback(f"Ошибка чтения папки {bad_path}: {e}")
            continue
        # Перемещаем все файлы из bad-папки на уровень выше
        for f in files_in_bad:
            src, dst = os.path.join(bad_path, f), os.path.join(parent_path, f)
            try:
                shutil.move(src, dst)
                msg = f"Перемещен файл: {f}"
            except Exception as e:
                msg = f"Ошибка перемещения {f}: {e}"
            if progress_callback:
                progress_callback(msg)
        # Удаляем пустую bad-папку
        try:
            os.rmdir(bad_path)
            msg = f"Удалена папка: {os.path.basename(bad_path)}"
        except Exception as e:
            msg = f"Ошибка удаления папки {os.path.basename(bad_path)}: {e}"
        if progress_callback:
            progress_callback(msg)
    if progress_callback:
        progress_callback(f"Обработка папок 'bad' завершена. Обработано: {total_bad_folders} папок")



# Запуск очистки и обработки bad-папок при прямом вызове модуля
if __name__ == "__main__":
    INPUT_FOLDER = "INPUT"  # Можно заменить на абсолютный путь
    clean_input_folder(INPUT_FOLDER)
    process_bad_folders(INPUT_FOLDER)
