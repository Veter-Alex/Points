"""
Модуль графического интерфейса для PointsManager на базе CustomTkinter.

Содержит классы и функции для создания окон, диалогов и управления основным GUI приложения.
Все классы и методы снабжены подробными комментариями и докстрингами согласно лучшим практикам.
"""


import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk  # type: ignore

from src.core import find_and_parse_files

APP_VERSION = "v1.1.0"


class TXTFileDialog(ctk.CTkToplevel):
    """
    Кастомный диалог для выбора TXT файла или директории.

    Args:
        parent: Родительское окно.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("Выбор файла данных о городах")
        self.geometry("380x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.center_window(parent)
        self.create_widgets()

    def center_window(self, parent):
        """
        Центрирует окно относительно родительского.

        Args:
            parent: Родительское окно.
        """
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 190
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """
        Создает виджеты диалога выбора TXT файла или директории.
        """
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Выберите TXT файл или директорию для создания city.txt",
            justify="center",
            wraplength=350,
        )
        desc_label.pack(pady=(15, 25), padx=10)
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15), padx=10)
        # Кнопка выбора файла
        ctk.CTkButton(
            button_frame, text="📄 Файл", width=110, height=40, command=self.choose_file
        ).pack(side="left", padx=(0, 5))
        # Кнопка выбора директории
        ctk.CTkButton(
            button_frame,
            text="📁 Папка",
            width=110,
            height=40,
            command=self.choose_directory,
        ).pack(side="left", padx=(5, 5))
        # Кнопка отмены
        ctk.CTkButton(
            button_frame,
            text="Отмена",
            width=110,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self.cancel,
        ).pack(side="left", padx=(5, 0))

    def choose_file(self):
        """
        Обработчик выбора файла.
        """
        self.result = "file"
        self.destroy()

    def choose_directory(self):
        """
        Обработчик выбора директории.
        """
        self.result = "directory"
        self.destroy()

    def cancel(self):
        """
        Обработчик отмены выбора.
        """
        self.result = None
        self.destroy()

    def get_choice(self):
        """
        Возвращает выбор пользователя (file/directory/None).
        """
        self.wait_window()
        return self.result


class CSVFileDialog(ctk.CTkToplevel):
    """
    Кастомный диалог для выбора между файлом и директорией.

    Args:
        parent: Родительское окно.
    """

    def __init__(self, parent):
        """
        Инициализация диалога выбора CSV файла или директории.

        Args:
            parent: Родительское окно.
        """
        super().__init__(parent)
        self.result = None

        # Настройка окна
        self.title("Выбор файла базы данных")
        self.geometry("380x200")
        self.resizable(False, False)

        # Делаем окно модальным
        self.transient(parent)
        self.grab_set()

        # Центрируем окно относительно родительского
        self.center_window(parent)

        self.create_widgets()

    def center_window(self, parent):
        """
        Центрирует окно относительно родительского.

        Args:
            parent: Родительское окно.
        """
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 190
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """
        Создает виджеты диалога выбора CSV файла или директории.
        """
        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Описание
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Вы можете выбрать существующий CSV файл\nили указать директорию для создания нового файла AllPoint.csv",
            justify="center",
            wraplength=350,
        )
        desc_label.pack(pady=(15, 25), padx=10)

        # Все кнопки в одну линию
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15), padx=10)

        # Кнопка выбора файла
        file_button = ctk.CTkButton(
            button_frame,
            text="📄 Выбрать файл",
            width=110,
            height=40,
            command=self.choose_file,
        )
        file_button.pack(side="left", padx=(0, 5))

        # Кнопка выбора директории
        dir_button = ctk.CTkButton(
            button_frame,
            text="📁 Выбрать папку",
            width=110,
            height=40,
            command=self.choose_directory,
        )
        dir_button.pack(side="left", padx=(5, 5))

        # Кнопка отмены
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Отмена",
            width=110,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self.cancel,
        )
        cancel_button.pack(side="left", padx=(5, 0))

    def choose_file(self):
        """
        Обработчик выбора файла.
        """
        self.result = "file"
        self.destroy()

    def choose_directory(self):
        """
        Обработчик выбора директории.
        """
        self.result = "directory"
        self.destroy()

    def cancel(self):
        """
        Обработчик отмены выбора.
        """
        self.result = None
        self.destroy()

    def get_choice(self):
        """
        Возвращает выбор пользователя (file/directory/None).
        """
        self.wait_window()  # Ждем закрытия окна
        return self.result


class PointsGUI(ctk.CTk):
    """
    Основной класс графического интерфейса приложения PointsManager.

    Отвечает за создание главного окна, настройку элементов управления,
    обработку событий и взаимодействие с данными точек и городов.

    Args:
        settings: Объект с настройками приложения.
        logger: Объект логгера для ведения журнала событий.
    """

    def __init__(self, settings, logger):
        """
        Инициализация главного окна приложения, создание всех элементов интерфейса.

        Args:
            settings: Объект с настройками приложения.
            logger: Объект логгера.
        """
        super().__init__()
        self.title(f"PointsManager {APP_VERSION} - Географические точки")
        self.geometry("1000x700")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.settings = settings
        self.logger = logger

        # Инициализируем объекты данных как None
        self.points_data = None
        self.city_data = None

        # Создаем меню
        self.create_menu()

        # Верхняя панель с настройками
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, fill="x", padx=20)

        # rootFolder
        self.lbl_root = ctk.CTkLabel(
            self.settings_frame, text="Директория для поиска файлов:"
        )
        self.lbl_root.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_root = ctk.CTkEntry(self.settings_frame, width=400)
        # Отображаем путь с корректными разделителями
        self.entry_root.insert(0, os.path.normpath(self.settings.rootFolder))
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
        self.entry_csv.insert(0, os.path.normpath(self.settings.mainDataCSV))
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
        self.entry_city.insert(0, os.path.normpath(self.settings.cityDataFile))
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
            command=self.on_log_level_changed,
        )
        self.combo_log.set(self.settings.log_level)
        self.combo_log.grid(row=3, column=1, padx=5, sticky="w")

        # ===== Область для логов =====
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.pack(pady=10, fill="both", expand=True, padx=20)

        # Заголовок и кнопка очистки логов
        self.log_header_frame = ctk.CTkFrame(self.log_frame)
        self.log_header_frame.pack(fill="x", padx=5, pady=5)

        self.log_label = ctk.CTkLabel(
            self.log_header_frame, text="Журнал событий:", font=("Arial", 12, "bold")
        )
        self.log_label.pack(side="left", padx=5)

        self.clear_log_button = ctk.CTkButton(
            self.log_header_frame,
            text="Очистить логи",
            width=100,
            height=25,
            command=self.clear_logs,
        )
        self.clear_log_button.pack(side="right", padx=5)

        self.log_text = ctk.CTkTextbox(self.log_frame, width=950, height=250)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # ===== Кнопка начать обработку =====
        self.button_process = ctk.CTkButton(
            self, text="Обработать файлы", command=self.start_processing
        )
        self.button_process.pack(pady=10)

        # ===== Прогресс-бар =====
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=5, padx=20, fill="x")
        self.progress_bar.set(0)  # Изначально пустой

        # ===== Статус =====
        self.status_label = ctk.CTkLabel(self, text="Готов к работе", anchor="w")
        self.status_label.pack(pady=5, padx=20, anchor="w", side="left")

        # ===== Инициализация и вывод логов =====
        self.after(100, self.init_and_log)

    def create_menu(self):
        """Создание верхнего меню."""
        # Создаем главное меню
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выход", command=self.exit_application)

        # Меню "Команды"
        commands_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Команды", menu=commands_menu)
        commands_menu.add_command(
            label="Очистить входную директорию", command=self.clean_input_directory
        )

        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Вызвать справку", command=self.show_help)

    def exit_application(self):
        """Выход из приложения."""
        self.log_message("Завершение работы приложения...", color="blue")
        self.quit()

    def clean_input_directory(self):
        """Очистка входной директории с подтверждением."""
        # Показываем предупреждение
        result = messagebox.askyesno(
            "Подтверждение очистки",
            "ВНИМАНИЕ!!!\n\n"
            f"Из входной директории:\n{self.settings.rootFolder}\n\n"
            "будут удалены все файлы кроме xml, json и spr\n\n"
            "Продолжить очистку?",
            icon="warning",
        )

        if result:
            try:
                # Импортируем функции очистки
                from src.cleanup_input_folder import (
                    clean_input_folder,
                    process_bad_folders,
                )

                self.log_message(
                    "Начинается очистка входной директории...", color="blue"
                )

                # Отключаем кнопку обработки и активируем прогресс-бар
                self.button_process.configure(state="disabled")
                self.progress_bar.set(0)

                # Выполняем очистку в отдельном потоке
                def cleanup_thread():
                    try:
                        # Создаем callback для обновления прогресса
                        def progress_callback(message):
                            self.after(
                                0, lambda: self.log_message(message, color="blue")
                            )
                            self.after(
                                0, lambda: self.status_label.configure(text=message)
                            )

                        # Запускаем анимацию прогресс-бара
                        self.after(0, self._animate_cleanup_progress)

                        # Выполняем очистку файлов
                        self.after(
                            0,
                            lambda: self.status_label.configure(
                                text="Очистка файлов..."
                            ),
                        )
                        clean_input_folder(self.settings.rootFolder, progress_callback)

                        # Выполняем обработку папок bad
                        self.after(
                            0,
                            lambda: self.status_label.configure(
                                text="Обработка папок 'bad'..."
                            ),
                        )
                        process_bad_folders(self.settings.rootFolder, progress_callback)

                        # Завершение
                        self.after(0, self._cleanup_completed)

                    except Exception as e:
                        # Используем after для безопасного обновления GUI
                        self.after(0, lambda: self._cleanup_error(str(e)))

                # Запускаем очистку в отдельном потоке
                self.cleanup_thread = threading.Thread(
                    target=cleanup_thread, daemon=True
                )
                self.cleanup_thread.start()

            except ImportError as e:
                self.log_message(
                    f"Ошибка импорта модуля очистки: {e}",
                    color="red",
                    logger_level="error",
                )
                messagebox.showerror(
                    "Ошибка", f"Не удалось загрузить модуль очистки:\n{e}"
                )
        else:
            self.log_message(
                "Очистка входной директории отменена пользователем", color="orange"
            )

    def _animate_cleanup_progress(self):
        """Анимация прогресс-бара во время очистки."""
        if hasattr(self, "cleanup_thread") and self.cleanup_thread.is_alive():
            # Обновляем прогресс-бар (неопределенный прогресс)
            current = self.progress_bar.get()
            if current >= 0.9:
                self.progress_bar.set(0.1)
            else:
                self.progress_bar.set(current + 0.1)

            # Продолжаем анимацию через 200ms
            self.after(200, self._animate_cleanup_progress)

    def _cleanup_completed(self):
        """Завершение очистки - вызывается в основном потоке."""
        self.log_message("Очистка входной директории завершена успешно", color="blue")
        self.button_process.configure(state="normal")
        self.progress_bar.set(1.0)  # Полный прогресс
        self.status_label.configure(text="Очистка завершена")
        messagebox.showinfo("Очистка завершена", "Входная директория успешно очищена")

    def _cleanup_error(self, error_message):
        """Обработка ошибки очистки - вызывается в основном потоке."""
        self.log_message(
            f"Ошибка при очистке: {error_message}", color="red", logger_level="error"
        )
        self.button_process.configure(state="normal")
        self.progress_bar.set(0)  # Сброс прогресса
        self.status_label.configure(text="Ошибка очистки")
        messagebox.showerror(
            "Ошибка очистки", f"Произошла ошибка при очистке:\n{error_message}"
        )


    def show_help(self):
        """Показать справку: сначала DOCX/DOC, иначе MD."""
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            docx_file = os.path.join(base_dir, "help.docx")
            doc_file = os.path.join(base_dir, "help.doc")
            md_file = os.path.join(base_dir, "help.md")

            help_file = None
            if os.path.exists(docx_file):
                help_file = docx_file
            elif os.path.exists(doc_file):
                help_file = doc_file
            elif os.path.exists(md_file):
                help_file = md_file

            if help_file:
                # Открываем файл справки в системном редакторе
                if os.name == "nt":  # Windows
                    os.startfile(help_file)
                else:  # Linux/Mac
                    os.system(f"xdg-open '{help_file}'")
                self.log_message(f"Открыт файл справки: {help_file}", color="blue")
            else:
                messagebox.showwarning(
                    "Справка недоступна", "Файл справки не найден: help.docx/help.doc/help.md"
                )
                self.log_message("Файл справки не найден: help.docx/help.doc/help.md", color="orange")
        except Exception as e:
            self.log_message(
                f"Ошибка при открытии справки: {e}", color="red", logger_level="error"
            )
            messagebox.showerror("Ошибка", f"Не удалось открыть справку:\n{e}")

    def log_message(self, message, color=None, logger_level="info"):
        """Логировать сообщение в текстовом поле и в логгер.
        Args:
            message (str): Сообщение для логирования
            color (str, optional): Цвет текста ('blue', 'red', 'yellow')
            logger_level (str): Уровень логирования (info, warning, error)
        """
        # Гарантируем, что logger_level всегда строка
        logger_level = logger_level or "info"
        current_level = (getattr(self.settings, "log_level", None) or "INFO").upper()
        message_level = logger_level.upper()
        # Иерархия уровней логирования
        level_hierarchy = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4,
        }
        # Показываем сообщение в GUI только если его уровень >= текущего уровня
        if level_hierarchy.get(message_level, 1) >= level_hierarchy.get(
            current_level, 1
        ):
            tag = None
            if color:
                tag = color
                if tag not in self.log_text.tag_names():
                    self.log_text.tag_config(tag, foreground=color)
            # Добавляем сообщение в конец лога
            self.log_text.insert("end", message + "\n", tag if color else None)
            # Ограничиваем количество строк в логе (максимум 1000 строк)
            lines = self.log_text.get("1.0", "end").count("\n")
            if lines > 1000:
                # Удаляем первые 100 строк при превышении лимита
                self.log_text.delete("1.0", "101.0")
            # Автоскроллинг: прокручиваем до конца
            self.log_text.see("end")
            # Обновляем GUI для немедленного отображения
            self.update_idletasks()
        # Логируем в файл (независимо от уровня отображения в GUI)
        if hasattr(self.logger, logger_level):
            getattr(self.logger, logger_level)(message)
        else:
            self.logger.info(message)

    def clear_logs(self):
        """Очистить окно логов."""
        self.log_text.delete("1.0", "end")
        self.log_message("Логи очищены", color="blue")

    def reload_points_data(self):
        """Перезагрузка данных точек при изменении файла базы данных."""
        try:
            from models.points import PointsData

            # Обнуляем старые данные
            self.points_data = None

            # Загружаем новые данные
            self.points_data = PointsData(self.settings.mainDataCSV, self.log_message)
            self.log_message("Данные точек успешно перезагружены", color="blue")

        except Exception as e:
            self.log_message(
                f"Ошибка при перезагрузке данных точек: {e}",
                color="red",
                logger_level="error",
            )
            self.points_data = None

    def reload_city_data(self):
        """Перезагрузка данных городов при изменении файла данных о городах."""
        try:
            from models.city import CityData

            # Обнуляем старые данные
            self.city_data = None

            # Загружаем новые данные
            self.city_data = CityData(self.settings.cityDataFile, self.log_message)
            self.log_message("Данные городов успешно перезагружены", color="blue")

        except Exception as e:
            self.log_message(
                f"Ошибка при перезагрузке данных городов: {e}",
                color="red",
                logger_level="error",
            )
            self.city_data = None

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
            norm_path = os.path.normpath(path)
            self.entry_root.insert(0, norm_path)
            self.settings.rootFolder = norm_path
            self.log_message(
                f"Выбрана директория для поиска файлов: {path}", color="blue"
            )

    def on_log_level_changed(self, new_level):
        """Обработчик изменения уровня логирования."""
        self.settings.log_level = new_level
        self.log_message(f"Уровень логирования изменен на: {new_level}", color="blue")

    def choose_csv(self):
        # Открываем кастомный диалог
        dialog = CSVFileDialog(self)
        choice = dialog.get_choice()

        if choice == "file":
            file = filedialog.askopenfilename(
                title="Выберите CSV файл", filetypes=[("CSV", "*.csv")]
            )
            if file:
                self.entry_csv.delete(0, "end")
                norm_file = os.path.normpath(file)
                self.entry_csv.insert(0, norm_file)
                self.settings.mainDataCSV = norm_file
                self.log_message(
                    f"Выбран файл базы данных точек (CSV): {file}", color="blue"
                )
                # Перезагружаем данные точек
                self.reload_points_data()

        elif choice == "directory":
            directory = filedialog.askdirectory(
                title="Выберите директорию для создания AllPoint.csv"
            )
            if directory:
                allpoint_path = os.path.join(directory, "AllPoint.csv")

                if os.path.exists(allpoint_path):
                    # Файл уже существует
                    self.entry_csv.delete(0, "end")
                    norm_allpoint = os.path.normpath(allpoint_path)
                    self.entry_csv.insert(0, norm_allpoint)
                    self.settings.mainDataCSV = norm_allpoint
                    self.log_message(
                        f"Выбран существующий файл базы данных: {allpoint_path}",
                        color="blue",
                    )
                    # Перезагружаем данные точек
                    self.reload_points_data()
                else:
                    # Файл не существует, создаем автоматически
                    try:
                        from models.points import PointsData

                        # Создаем файл через PointsData
                        temp_points_data = PointsData(allpoint_path, self.log_message)

                        self.entry_csv.delete(0, "end")
                        norm_allpoint = os.path.normpath(allpoint_path)
                        self.entry_csv.insert(0, norm_allpoint)
                        self.settings.mainDataCSV = norm_allpoint
                        self.log_message(
                            f"Создан и выбран новый файл базы данных: {allpoint_path}",
                            color="blue",
                        )
                        # Перезагружаем данные точек (используем созданный объект)
                        self.points_data = temp_points_data
                        self.log_message(
                            "Данные точек инициализированы для работы", color="blue"
                        )
                    except Exception as e:
                        self.log_message(
                            f"Ошибка при создании файла: {e}",
                            color="red",
                            logger_level="error",
                        )
                        messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{e}")
                        self.points_data = None

    def choose_city(self):
        # Открываем кастомный диалог
        dialog = TXTFileDialog(self)
        choice = dialog.get_choice()

        if choice == "file":
            file = filedialog.askopenfilename(
                title="Выберите файл данных о городах", filetypes=[("TXT", "*.txt")]
            )
            if file:
                self.entry_city.delete(0, "end")
                norm_file = os.path.normpath(file)
                self.entry_city.insert(0, norm_file)
                self.settings.cityDataFile = norm_file
                self.log_message(
                    f"Выбран файл данных о городах (txt): {file}", color="blue"
                )
                # Перезагружаем данные городов
                self.reload_city_data()

        elif choice == "directory":
            directory = filedialog.askdirectory(
                title="Выберите директорию для создания city.txt"
            )
            if directory:
                city_path = os.path.join(directory, "city.txt")

                if os.path.exists(city_path):
                    # Файл уже существует
                    self.entry_city.delete(0, "end")
                    norm_city = os.path.normpath(city_path)
                    self.entry_city.insert(0, norm_city)
                    self.settings.cityDataFile = norm_city
                    self.log_message(
                        f"Выбран существующий файл данных о городах: {city_path}",
                        color="blue",
                    )
                    # Перезагружаем данные городов
                    self.reload_city_data()
                else:
                    # Файл не существует, создаем автоматически
                    try:
                        from models.city import CityData

                        # Создаем файл через CityData
                        temp_city_data = CityData(city_path, self.log_message)

                        self.entry_city.delete(0, "end")
                        norm_city = os.path.normpath(city_path)
                        self.entry_city.insert(0, norm_city)
                        self.settings.cityDataFile = norm_city
                        self.log_message(
                            f"Создан и выбран новый файл данных о городах: {city_path}",
                            color="blue",
                        )
                        # Перезагружаем данные городов (используем созданный объект)
                        self.city_data = temp_city_data
                        self.log_message(
                            "Данные городов инициализированы для работы", color="blue"
                        )
                    except Exception as e:
                        self.log_message(
                            f"Ошибка при создании файла: {e}",
                            color="red",
                            logger_level="error",
                        )
                        messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{e}")
                        self.city_data = None

    def start_processing(self):
        """Запуск обработки файлов в отдельном потоке."""
        if hasattr(self, "processing_thread") and self.processing_thread.is_alive():
            self.log_message("Обработка уже запущена!", color="orange")
            return

        self.log_message("Запуск обработки файлов...", color="blue")

        # Отключаем кнопку обработки и показываем прогресс
        self.button_process.configure(state="disabled", text="Обработка...")
        self.progress_bar.set(0)
        self.status_label.configure(text="Обработка файлов...")

        # Запускаем обработку в отдельном потоке
        self.processing_thread = threading.Thread(
            target=self._process_files_thread, daemon=True
        )
        self.processing_thread.start()

        # Запускаем анимацию прогресс-бара
        self._animate_progress()

    def _animate_progress(self):
        """Анимация прогресс-бара во время обработки."""
        if hasattr(self, "processing_thread") and self.processing_thread.is_alive():
            # Обновляем прогресс-бар (неопределенный прогресс)
            current = self.progress_bar.get()
            if current >= 0.9:
                self.progress_bar.set(0.1)
            else:
                self.progress_bar.set(current + 0.1)

            # Продолжаем анимацию через 200ms
            self.after(200, self._animate_progress)

    def _process_files_thread(self):
        """Обработка файлов в отдельном потоке."""
        try:
            from models.city import CityData
            from models.points import PointsData

            self.log_message(
                f"Начинаю обработку файлов в папке: {self.settings.rootFolder}"
            )

            # Загружаем данные о городах, если еще не загружены
            if self.city_data is None:
                self.city_data = CityData(self.settings.cityDataFile, self.log_message)

            # Загружаем данные о точках, если еще не загружены
            if self.points_data is None:
                self.points_data = PointsData(
                    self.settings.mainDataCSV, self.log_message
                )

            # Создаем callback для обновления статуса
            def update_status(message):
                self.after(0, lambda: self.status_label.configure(text=message))

            find_and_parse_files(
                self.settings.rootFolder,
                self.city_data,
                self.points_data,
                self.settings,
                self.log_message,
                status_callback=update_status,
            )

            # Используем after для безопасного обновления GUI из потока
            self.after(0, self._processing_completed)

        except Exception as e:
            # Используем after для безопасного обновления GUI из потока
            self.after(0, lambda e=e: self._processing_error(str(e)))

    def _processing_completed(self):
        """Завершение обработки - вызывается в основном потоке."""
        self.log_message("Обработка завершена.", color="blue")
        self.button_process.configure(state="normal", text="Обработать файлы")
        self.progress_bar.set(1.0)  # Полный прогресс
        self.status_label.configure(text="Обработка завершена")

    def _processing_error(self, error_message):
        """Обработка ошибки - вызывается в основном потоке."""
        self.log_message(f"Ошибка при обработке: {error_message}", color="red")
        self.button_process.configure(state="normal", text="Обработать файлы")
        self.progress_bar.set(0)  # Сброс прогресса
        self.status_label.configure(text="Ошибка обработки")

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
