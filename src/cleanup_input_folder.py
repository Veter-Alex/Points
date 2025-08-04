"""
Модуль для очистки папки INPUT и обработки папок bad.
1. Удаляет все файлы в INPUT, кроме xml, json, spr.
2. Находит все папки bad, переносит их содержимое на уровень выше и удаляет папку bad.
"""

import os
import shutil


def clean_input_folder(input_folder: str) -> None:
    """
    Удаляет все файлы в input_folder, кроме xml, json, spr.
    """
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in [".xml", ".json", ".spr"]:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Удалён файл: {file_path}")
                except Exception as e:
                    print(f"Ошибка удаления {file_path}: {e}")


def process_bad_folders(input_folder: str) -> None:
    """
    Находит все папки bad, переносит их содержимое на уровень выше и удаляет папку bad.
    """
    for root, dirs, files in os.walk(input_folder):
        for d in dirs:
            if d == "bad":
                bad_path = os.path.join(root, d)
                parent_path = root
                # Переносим все файлы из bad на уровень выше
                for f in os.listdir(bad_path):
                    src = os.path.join(bad_path, f)
                    dst = os.path.join(parent_path, f)
                    try:
                        shutil.move(src, dst)
                        print(f"Перемещён файл: {src} -> {dst}")
                    except Exception as e:
                        print(f"Ошибка перемещения {src}: {e}")
                # Удаляем папку bad
                try:
                    os.rmdir(bad_path)
                    print(f"Удалена папка: {bad_path}")
                except Exception as e:
                    print(f"Ошибка удаления папки {bad_path}: {e}")


if __name__ == "__main__":
    INPUT_FOLDER = "INPUT"  # Можно заменить на абсолютный путь
    clean_input_folder(INPUT_FOLDER)
    process_bad_folders(INPUT_FOLDER)
