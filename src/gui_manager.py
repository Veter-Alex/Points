"""
Модуль графического интерфейса для PointsManager на базе CustomTkinter.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.core import find_and_parse_files


class PointsGUI(ctk.CTk):

    def __init__(self, settings, logger):
        super().__init__()
        self.title("PointsManager - Географические точки")
        self.geometry("1000x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.settings = settings
        self.logger = logger

        # ===== Верхняя панель с настройками =====
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, fill="x", padx=20)

        # rootFolder
        self.lbl_root = ctk.CTkLabel(
            self.settings_frame, text="Директория для поиска файлов:"
        )
        self.lbl_root.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_root = ctk.CTkEntry(self.settings_frame, width=400)
        self.entry_root.insert(0, self.settings.rootFolder)
        self.entry_root.grid(row=0, column=1, padx=5)
        self.btn_root = ctk.CTkButton(
            self.settings_frame, text="...", width=30, command=self.choose_root
        )
        self.btn_root.grid(row=0, column=2, padx=5)

        # mainDataCSV
        self.lbl_csv = ctk.CTkLabel(
            self.settings_frame, text="Файл базы данных точек (CSV):"
        )
        self.lbl_csv.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_csv = ctk.CTkEntry(self.settings_frame, width=400)
        self.entry_csv.insert(0, self.settings.mainDataCSV)
        self.entry_csv.grid(row=1, column=1, padx=5)
        self.btn_csv = ctk.CTkButton(
            self.settings_frame, text="...", width=30, command=self.choose_csv
        )
        self.btn_csv.grid(row=1, column=2, padx=5)

        # cityDataFile
        self.lbl_city = ctk.CTkLabel(
            self.settings_frame, text="Файл данных о городах (txt):"
        )
        self.lbl_city.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_city = ctk.CTkEntry(self.settings_frame, width=400)
        self.entry_city.insert(0, self.settings.cityDataFile)
        self.entry_city.grid(row=2, column=1, padx=5)
        self.btn_city = ctk.CTkButton(
            self.settings_frame, text="...", width=30, command=self.choose_city
        )
        self.btn_city.grid(row=2, column=2, padx=5)

        # log_level
        self.lbl_log = ctk.CTkLabel(self.settings_frame, text="Уровень логирования:")
        self.lbl_log.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.combo_log = ctk.CTkComboBox(
            self.settings_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        self.combo_log.set(self.settings.log_level)
        self.combo_log.grid(row=3, column=1, padx=5)

        # ===== Область для логов =====
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.pack(pady=10, fill="both", expand=True, padx=20)
        self.log_text = ctk.CTkTextbox(self.log_frame, width=950, height=250)
        self.log_text.pack(fill="both", expand=True)

        # ===== Кнопка начать обработку =====
        self.btn_start = ctk.CTkButton(
            self, text="Начать обработку", command=self.start_processing
        )
        self.btn_start.pack(pady=20)

        # ===== Инициализация и вывод логов =====
        self.after(100, self.init_and_log)

    def log_message(self, message, color=None, logger_level="info"):
        """Логировать сообщение в текстовом поле и в логгер.
        Args:
            message (str): Сообщение для логирования
            color (str, optional): Цвет текста ('blue', 'red', 'yellow')
            logger_level (str): Уровень логирования (info, warning, error)
        """
        tag = None
        if color:
            tag = color
            if tag not in self.log_text.tag_names():
                self.log_text.tag_config(tag, foreground=color)
        self.log_text.insert("end", message + "\n", tag if color else None)
        if hasattr(self.logger, logger_level):
            getattr(self.logger, logger_level)(message)
        else:
            self.logger.info(message)

    def init_and_log(self):
        self.log_message("Старт программы ...", color="blue")
        # Первичная инициализация настроек и их проверка
        self.log_message("Загрузка настроек приложения...", color="blue")
        if self.settings:
            self.log_message(f"Настройки загружены:", color="blue")
            self.log_message(
                f"- Директория для поиска файлов xml/json: {self.settings.rootFolder}"
            )
            self.log_message(
                f"- Файл базы данных точек (CSV): {self.settings.mainDataCSV}"
            )
            self.log_message(
                f"- Файл данных о городах (txt): {self.settings.cityDataFile}"
            )
            self.log_message(f"- Уровень логирования: {self.settings.log_level}")
            # Проверка существования директорий и файлов
            self.log_message("Проверка настроек...", color="blue")
            errors = self.settings.validate()
            if errors:
                for key, msg in errors.items():
                    self.log_message(
                        f"Ошибка в настройке '{key}': {msg}",
                        color="red",
                        logger_level="error",
                    )
            else:
                self.log_message("Все настройки корректны.", color="blue")

    def choose_root(self):
        path = filedialog.askdirectory(title="Выберите директорию для поиска файлов")
        if path:
            self.entry_root.delete(0, "end")
            self.entry_root.insert(0, path)
            self.settings.rootFolder = path
            self.log_message(
                f"Выбрана директория для поиска файлов: {path}", color="blue"
            )

    def choose_csv(self):
        file = filedialog.askopenfilename(
            title="Выберите CSV файл", filetypes=[("CSV", "*.csv")]
        )
        if file:
            self.entry_csv.delete(0, "end")
            self.entry_csv.insert(0, file)
            self.settings.mainDataCSV = file
            self.log_message(
                f"Выбран файл базы данных точек (CSV): {file}", color="blue"
            )

    def choose_city(self):
        file = filedialog.askopenfilename(
            title="Выберите файл данных о городах", filetypes=[("TXT", "*.txt")]
        )
        if file:
            self.entry_city.delete(0, "end")
            self.entry_city.insert(0, file)
            self.settings.cityDataFile = file
            self.log_message(
                f"Выбран файл данных о городах (txt): {file}", color="blue"
            )

    def start_processing(self):
        from models.city import CityData
        from models.points import PointsData

        self.log_message("Запуск обработки файлов...", color="blue")
        self.log_message(
            f"Начинаю обработку файлов в папке: {self.settings.rootFolder}"
        )

        # Загружаем данные о городах и точках
        city_data = CityData(self.settings.cityDataFile, self.log_message)
        points_data = PointsData(self.settings.mainDataCSV, self.log_message)

        find_and_parse_files(
            self.settings.rootFolder,
            city_data,
            points_data,
            self.settings,
            self.log_message,
        )
        self.log_message("Обработка завершена.", color="blue")

    def load_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите файлы для обработки",
            filetypes=[("XML/JSON", "*.xml *.json")],
        )
        if files:
            self.listbox.delete("1.0", "end")
            self.listbox.insert("end", f"Загружено файлов: {len(files)}\n")
            for f in files:
                self.listbox.insert("end", f"{f}\n")
            self.status.configure(text="Файлы загружены")
        else:
            self.status.configure(text="Файлы не выбраны")

    def open_settings(self):
        messagebox.showinfo("Настройки", "Окно настроек будет реализовано позже.")

    def export_data(self):
        messagebox.showinfo("Экспорт", "Экспорт данных будет реализован позже.")
