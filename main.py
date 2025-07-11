import os
import sys

import customtkinter as ctk  # type: ignore

from src.city_manager import CityManager
from src.settings_manager import SettingsManager

# Настройка внешнего вида
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class PointsApp:
    def __init__(self):

        self.settings_manager = SettingsManager()
        # Получаем путь к city.txt из настроек, иначе по умолчанию
        city_file = self.settings_manager.get("cityDataFile", "data/city.txt")
        self.city_manager = CityManager(city_file)

        app_name = "Points Data Manager"
        width = 800
        height = 600
        self.root = ctk.CTk()
        self.root.title(app_name)
        self.root.geometry(f"{width}x{height}")

        # Настройка сетки
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # Боковая панель
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Заголовок боковой панели
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Points Manager",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Кнопки в боковой панели
        self.load_data_button = ctk.CTkButton(
            self.sidebar_frame, text="Загрузить данные", command=self.load_data
        )
        self.load_data_button.grid(row=1, column=0, padx=20, pady=10)

        self.process_button = ctk.CTkButton(
            self.sidebar_frame, text="Обработать", command=self.process_data
        )
        self.process_button.grid(row=2, column=0, padx=20, pady=10)

        self.save_button = ctk.CTkButton(
            self.sidebar_frame, text="Сохранить", command=self.save_data
        )
        self.save_button.grid(row=3, column=0, padx=20, pady=10)

        self.settings_button = ctk.CTkButton(
            self.sidebar_frame, text="Настройки", command=self.open_settings_window
        )
        self.settings_button.grid(row=4, column=0, padx=20, pady=10)

    def open_settings_window(self):
        # Окно для настроек с вкладками
        win = ctk.CTkToplevel(self.root)
        win.title("Настройки приложения")
        win.geometry("700x400")
        win.grab_set()

        tabview = ctk.CTkTabview(win, width=650, height=340)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # === Вкладка 1: Основные настройки ===
        tab_main = tabview.add("Основные")
        settings_fields = [
            ("rootFolder", "Папка для поиска файлов для парсинга (xml, json и т.д.)"),
            (
                "mainDataCSV",
                "Файл (база данных) для хранения всех ранее отмеченных точек (CSV, UTF-8)",
            ),
            ("cityDataFile", "Файл для хранения данных о городах (txt, UTF-8)"),
        ]
        settings_frame = ctk.CTkFrame(tab_main)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.settings_entries = {}
        row = 0
        for key, desc in settings_fields:
            value = self.settings_manager.get(key, "")
            label = ctk.CTkLabel(settings_frame, text=desc, anchor="w")
            label.grid(row=row, column=0, columnspan=3, sticky="w", padx=2, pady=(5, 0))
            row += 1
            entry = ctk.CTkEntry(settings_frame, width=420)
            entry.insert(0, str(value))
            entry.grid(row=row, column=0, columnspan=2, sticky="w", padx=2, pady=(0, 8))
            self.settings_entries[key] = entry
            if key in ("rootFolder", "mainDataCSV", "cityDataFile"):

                def make_callback(entry_ref=entry, is_dir=(key == "rootFolder")):
                    import tkinter.filedialog as fd

                    def callback():
                        if is_dir:
                            path = fd.askdirectory()
                        else:
                            path = fd.askopenfilename()
                        if path:
                            entry_ref.delete(0, "end")
                            entry_ref.insert(0, path)

                    return callback

                btn = ctk.CTkButton(
                    settings_frame, text="...", width=30, command=make_callback()
                )
                btn.grid(row=row, column=2, padx=2, pady=(0, 8), sticky="w")
            row += 1

        btn_frame = ctk.CTkFrame(tab_main)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        load_btn = ctk.CTkButton(
            btn_frame, text="Загрузить из файла", command=self.reload_settings_from_file
        )
        load_btn.pack(side="left", padx=5)
        save_btn = ctk.CTkButton(
            btn_frame, text="Сохранить", command=self.save_settings_from_window
        )
        save_btn.pack(side="left", padx=5)
        close_btn = ctk.CTkButton(btn_frame, text="Закрыть", command=win.destroy)
        close_btn.pack(side="right", padx=5)

        # === Вкладка 2: Города ===
        tab_cities = tabview.add("Города")
        city_frame = ctk.CTkFrame(tab_cities)
        city_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Метка поиска
        print("Создаю search_label")
        search_label = ctk.CTkLabel(
            city_frame, text="Поиск города (ориг. назв.):", anchor="w"
        )
        search_label.grid(row=0, column=0, sticky="w", padx=2, pady=(5, 0))

        # Поле поиска
        print("Создаю city_search_entry")
        self.city_search_entry = ctk.CTkEntry(city_frame, width=300)
        self.city_search_entry.grid(row=1, column=0, sticky="w", padx=2, pady=0)

        # Разрешить вставку из буфера обмена (Ctrl+V для обеих раскладок)
        def paste_event(event=None):
            try:
                clipboard = self.root.clipboard_get()
                self.city_search_entry.delete(0, "end")
                self.city_search_entry.insert(0, clipboard)
            except Exception:
                pass
            return "break"

        # Стандартные бинды для вставки: Ctrl+V, Shift+Insert (работают в любой раскладке)
        self.city_search_entry.bind("<Control-v>", paste_event)
        self.city_search_entry.bind("<Control-V>", paste_event)
        self.city_search_entry.bind("<Shift-Insert>", paste_event)

        # Кнопка поиска
        print("Создаю search_btn")
        search_btn = ctk.CTkButton(
            city_frame, text="Найти", width=80, command=self.city_search_action
        )
        search_btn.grid(row=1, column=1, sticky="w", padx=2, pady=0)

        # Поля для вывода/редактирования информации о городе
        city_labels = [
            ("Оригинальное название:", "orig_name"),
            ("Русское название:", "type_and_rus"),
            ("Широта:", "latitude"),
            ("Долгота:", "longitude"),
            ("Страна:", "country"),
            ("Описание:", "description"),
            ("Регион:", "region"),
        ]
        self.city_result_entries = {}
        for i, (label_text, key) in enumerate(city_labels):
            print(f"Создаю label и entry для {key}")
            label = ctk.CTkLabel(city_frame, text=label_text, anchor="w")
            label.grid(row=2 + i, column=0, sticky="w", padx=2, pady=(2, 0))
            entry = ctk.CTkEntry(city_frame, width=400)
            entry.grid(row=2 + i, column=1, sticky="w", padx=2, pady=(2, 0))
            self.city_result_entries[key] = entry

        # Кнопка для обновления информации о городе
        print("Создаю update_btn")
        update_btn = ctk.CTkButton(
            city_frame, text="Обновить", width=120, command=self.city_update_action
        )
        update_btn.grid(row=2 + len(city_labels), column=0, columnspan=2, pady=(10, 0))

        city_frame.grid_rowconfigure(2 + len(city_labels) + 1, weight=1)
        city_frame.grid_columnconfigure(0, weight=1)

        win.lift()
        win.update()
        self.settings_window = win

    def city_search_action(self):
        query = self.city_search_entry.get().strip()
        # Очистить все поля
        for entry in self.city_result_entries.values():
            entry.delete(0, "end")
        if not query:
            self.city_result_entries["orig_name"].insert(
                0, "Введите название города для поиска."
            )
            return
        rec = self.city_manager.search(query)
        if rec:
            values = {
                "orig_name": rec.orig_name,
                "type_and_rus": rec.type_and_rus,
                "latitude": str(rec.latitude),
                "longitude": str(rec.longitude),
                "country": rec.country,
                "description": rec.description,
                "region": rec.region,
            }
            for key, entry in self.city_result_entries.items():
                entry.delete(0, "end")
                entry.insert(0, values.get(key, ""))
        else:
            self.city_result_entries["orig_name"].insert(0, "Город не найден.")

    def city_update_action(self):
        # Получить значения из полей
        values = {k: e.get().strip() for k, e in self.city_result_entries.items()}
        orig_name = values["orig_name"]
        if not orig_name or orig_name in (
            "Город не найден.",
            "Введите название города для поиска.",
        ):
            return
        # Найти город в city_manager
        rec = self.city_manager.find_by_eng(orig_name)
        if not rec:
            # Добавление нового города не реализовано (только обновление)
            return
        # Обновить поля объекта
        rec.type_and_rus = values["type_and_rus"]
        try:
            rec.latitude = float(values["latitude"].replace(",", "."))
        except Exception:
            pass
        try:
            rec.longitude = float(values["longitude"].replace(",", "."))
        except Exception:
            pass
        rec.country = values["country"]
        rec.description = values["description"]
        rec.region = values["region"]
        # Сохранить изменения в файл
        self._save_city_manager_to_file()

    def _save_city_manager_to_file(self):
        # Перезаписать city.txt с обновлёнными данными, сохраняя структуру и комментарии
        path = self.settings_manager.get("cityDataFile", "data/city.txt")
        # Читаем все строки
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        # Собираем новые строки
        new_lines = []
        for line in lines:
            l = line.strip()
            if not l or l.startswith("'") or l.startswith("=") or "=" not in l:
                new_lines.append(line)
                continue
            orig_name, rest = l.split("=", 1)
            rec = self.city_manager.find_by_eng(orig_name)
            if rec:
                # Формируем новую строку
                parts = [
                    rec.type_and_rus,
                    str(rec.latitude).replace(".", ","),
                    str(rec.longitude).replace(".", ","),
                    rec.country,
                    rec.description,
                    rec.region,
                ]
                # Удаляем пустые поля в конце
                while parts and parts[-1] == "":
                    parts.pop()
                new_line = f"{orig_name}={'_'.join(parts)}\n"
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        # Записываем обратно
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def reload_settings_from_file(self):
        self.settings_manager.load()
        if hasattr(self, "settings_window") and self.settings_window.winfo_exists():
            for key, entry in self.settings_entries.items():
                entry.delete(0, "end")
                entry.insert(0, str(self.settings_manager.settings.get(key, "")))

    def save_settings_from_window(self):
        # Сохраняет значения из окна настроек в файл
        for key, entry in self.settings_entries.items():
            val = entry.get()
            if key in (
                "window_width",
                "window_height",
                "font_size",
                "update_interval",
                "max_history_days",
                "cache_duration",
            ):
                try:
                    val = int(val)
                except Exception:
                    pass
            elif key in ("auto_update", "cache_enabled"):
                val = val in ("True", "true", "1")
            self.settings_manager.set(key, val)
        self.settings_manager.save()
        if hasattr(self, "settings_window") and self.settings_window.winfo_exists():
            self.settings_window.destroy()
        self.status_label.configure(
            text="Настройки сохранены. Перезапустите приложение для применения размеров окна и заголовка."
        )

        # Настройки внешнего вида
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, text="Тема:", anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        # Основная область
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(
            row=0, column=1, sticky="nsew", padx=(20, 20), pady=(20, 20)
        )
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Заголовок основной области
        self.main_title = ctk.CTkLabel(
            self.main_frame,
            text="Добро пожаловать в Points Manager",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.main_title.grid(row=0, column=0, padx=20, pady=20)

        # Текстовое поле для вывода информации
        self.textbox = ctk.CTkTextbox(self.main_frame, width=400)
        self.textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Добавляем приветственное сообщение
        welcome_text = """Приложение для работы с данными Points готово к использованию!

Возможности:
• Загрузка данных из CSV и JSON файлов
• Обработка и анализ данных
• Сохранение результатов

Используйте кнопки в боковой панели для начала работы.
        """
        self.textbox.insert("0.0", welcome_text)

        # Статус бар
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20)
        )

        self.status_label = ctk.CTkLabel(self.status_frame, text="Готов к работе")
        self.status_label.pack(pady=5)

    def load_data(self):
        """Загрузка данных"""
        self.textbox.delete("0.0", "end")
        self.textbox.insert(
            "0.0", "Функция загрузки данных будет реализована здесь...\n"
        )
        self.status_label.configure(text="Загрузка данных...")

    def process_data(self):
        """Обработка данных"""
        self.textbox.delete("0.0", "end")
        self.textbox.insert(
            "0.0", "Функция обработки данных будет реализована здесь...\n"
        )
        self.status_label.configure(text="Обработка данных...")

    def save_data(self):
        """Сохранение данных"""
        self.textbox.delete("0.0", "end")
        self.textbox.insert(
            "0.0", "Функция сохранения данных будет реализована здесь...\n"
        )
        self.status_label.configure(text="Сохранение данных...")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Изменение темы приложения"""
        ctk.set_appearance_mode(new_appearance_mode)

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


if __name__ == "__main__":
    app = PointsApp()
    app.run()
