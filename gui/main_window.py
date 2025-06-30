from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QLabel,
    QFileDialog, QVBoxLayout, QLineEdit, QMessageBox, QListWidget, QTextEdit, QHBoxLayout
)

from core.image_exporter import ExportWorker
from core.image_utils import get_resized_image_preview_info
from core.project_utils import find_all_res_dirs
from gui.image_drop_widget import ImageDropWidget
from gui.export_settings_widget import ExportSettingsWidget
from gui.project_settings_widget import ProjectSettingsWidget

import json
import os
import logging

CONFIG_PATH = "config.json"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android Image Processor")
        self.setMinimumSize(1000, 500)
        self.init_widgets()
        self.init_layout()
        self.load_last_path()

    def init_widgets(self):
        # шаг 1
        self.project_settings = ProjectSettingsWidget(self.on_res_selected)

        # шаг 2
        self.image_drop = ImageDropWidget()

        # шаг 3
        self.export_settings = ExportSettingsWidget()

        # логи
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMinimumWidth(300)

    def init_layout(self):

        # Шаг 1 — выбор проекта
        step1_container = QVBoxLayout()
        step1_container.addWidget(QLabel("<b>Шаг 1. Настройка проекта</b>"))
        step1_container.addWidget(self.project_settings)

        # Шаг 2 — Drag & Drop
        step2_layout = QVBoxLayout()
        step2_layout.addWidget(self.image_drop)

        step2_container = QVBoxLayout()
        step2_container.addWidget(QLabel("<b>Шаг 2. Исходное изображение</b>"))
        step2_container.addLayout(step2_layout)

        # Шаг 3 — Пока заглушка
        step3_container = QVBoxLayout()
        step3_container.addWidget(QLabel("<b>Шаг 3. Настройки экспорта изображения</b>"))
        step3_container.addWidget(self.export_settings)

        # Сигналы
        self.image_drop.image_loaded.connect(self.export_settings.set_suggested_name)
        self.export_settings.convert_button.clicked.connect(self.on_convert_clicked)

        # Финальная сборка
        main_layout = QHBoxLayout()
        main_layout.addLayout(step1_container)
        main_layout.addSpacing(20)
        main_layout.addLayout(step2_container)
        main_layout.addSpacing(20)
        main_layout.addLayout(step3_container)
        main_layout.addWidget(self.log_view)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_project(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку проекта")
        if not path:
            return

        res_dirs = find_all_res_dirs(path)
        if not res_dirs:
            QMessageBox.warning(self, "Ошибка", "Не найдены директории res/ в подпапках проекта.")
            return

        self.project_path = path
        self.path_label.setText(path)
        self.save_path()

        self.update_res_list(res_dirs)
        self.update_log_view()

    def load_last_path(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    path = data.get("last_path", "")
                    if os.path.isdir(os.path.join(path, "res")):
                        self.project_path = path
                        self.path_label.setText(path)
            except Exception as e:
                logging.error(f"Ошибка загрузки config: {e}")

    def save_path(self):
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump({"last_path": self.project_path}, f)
        except Exception as e:
            logging.error(f"Ошибка сохранения config: {e}")

    def update_res_list(self, res_dirs):
        self.res_list.clear()
        for path in res_dirs:
            self.res_list.addItem(path)

        if res_dirs:
            self.res_list.setCurrentRow(0)  # авто-выбор первого элемента
            self.selected_res_path.setText(res_dirs[0])  # обновляем поле

    def update_log_view(self):
        try:
            with open("logs.txt", "r") as f:
                self.log_view.setPlainText(f.read())
        except Exception as e:
            self.log_view.setPlainText(f"Ошибка чтения логов: {e}")

    def on_res_selected(self, item):
        # Пока просто логика-заглушка, на будущее
        pass

    def on_convert_clicked(self):
        from PIL import Image
        from PySide6.QtWidgets import QMessageBox

        if not self.image_drop.image_path:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите изображение.")
            return

        base_res_path = self.project_settings.get_selected_res_path()
        if not base_res_path:
            QMessageBox.warning(self, "Ошибка", "Не выбран путь res/ для сохранения.")
            return

        config = self.export_settings.get_export_config()
        if config is None:
            QMessageBox.warning(self, "Ошибка", "Проверьте значения масштабов DPI.")
            return

        try:
            image = Image.open(self.image_drop.image_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {e}")
            return

        original_width, original_height = image.size
        base_filename = config["filename"]
        to_webp = config["to_webp"]
        dpi_scales = config["dpi"]
        ext = "webp" if to_webp else "png"

        preview_lines = []
        output_paths = []
        format_str = "WEBP" if to_webp else "PNG"

        for dpi, scale in dpi_scales.items():
            folder = os.path.join(base_res_path, f"drawable-{dpi}")
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, f"{base_filename}.{ext}")

            path, (w, h), size_kb = get_resized_image_preview_info(image, scale, format_str, file_path)
            preview_lines.append(f"{path} — {w}x{h} — ~{size_kb:.1f} KB")
            output_paths.append((dpi, path, (w, h)))

        msg = QMessageBox(self)
        msg.setWindowTitle("Подтвердите сохранение")
        msg.setText("Будут созданы следующие файлы:\n\n" + "\n".join(preview_lines))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msg.exec()

        if result != QMessageBox.Ok:
            return

        # Шаг 2 — блокируем кнопку и показываем прогресс
        self.export_settings.convert_button.setEnabled(False)
        self.export_settings.progress_bar.setVisible(True)
        self.export_settings.status_label.setVisible(True)
        self.export_settings.progress_bar.setMaximum(len(output_paths))
        self.export_settings.progress_bar.setValue(0)
        self.export_settings.status_label.setText("Конвертация...")

        # Стартуем воркер в отдельном потоке
        self.thread = QThread()
        self.worker = ExportWorker(self.image_drop.image_path, config, base_res_path)
        self.worker.moveToThread(self.thread)

        self.worker.progress.connect(self.export_settings.progress_bar.setValue)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_conversion_error)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_conversion_finished(self):
        self.export_settings.convert_button.setEnabled(True)
        self.export_settings.progress_bar.setVisible(False)
        self.export_settings.status_label.setVisible(False)
        QMessageBox.information(self, "Успех", "Все изображения успешно сохранены.")

    def on_conversion_error(self, message):
        self.export_settings.convert_button.setEnabled(True)
        self.export_settings.progress_bar.setVisible(False)
        self.export_settings.status_label.setVisible(False)
        QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении:\n{message}")

