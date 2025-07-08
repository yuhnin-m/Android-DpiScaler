from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel,
    QFileDialog, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame, QSizePolicy
)
from PySide6.QtCore import QThread

from core.image_exporter import ExportWorker
from core.image_utils import get_resized_image_preview_info
from core.project_utils import find_all_res_dirs
from core.frame_utils import wrap_with_frame
from core.config_manager import load_config, save_config

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

        # загрузка прошлого конфига
        self.config = load_config()
        # инициализация виджетов и лайаутов
        self.init_widgets()
        self.init_layout()
        self.apply_config()

    def init_widgets(self):
        # шаг 1
        self.project_settings = ProjectSettingsWidget(self.on_res_selected)

        # шаг 2
        self.image_drop = ImageDropWidget()

        # шаг 3
        self.export_settings = ExportSettingsWidget()

        # подключение сигналов и слотов
        self.export_settings.convert_button.clicked.connect(self.on_convert_clicked)
        self.image_drop.image_loaded.connect(self.export_settings.set_suggested_name)

    def init_layout(self):
        # Заголовки
        step1_title = QLabel("<b>ШАГ 1. Настройка проекта</b>")
        step2_title = QLabel("<b>ШАГ 2. Исходное изображение</b>")
        step3_title = QLabel("<b>ШАГ 3. Настройки экспорта изображения</b>")

        # Шаг 1 (фиксированная высота)
        step1_layout = QVBoxLayout()
        step1_layout.addWidget(step1_title)
        step1_layout.addWidget(self.project_settings)

        step1_widget = QWidget()
        step1_widget.setLayout(step1_layout)
        step1_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Шаг 2
        step2_layout = QVBoxLayout()
        step2_layout.addWidget(step2_title)
        step2_layout.addWidget(self.image_drop)
        step2_layout.setStretch(1, 1)  # image_drop тянется

        # Шаг 3
        step3_layout = QVBoxLayout()
        step3_layout.addWidget(step3_title)
        step3_layout.addWidget(self.export_settings)
        step3_layout.setStretch(1, 0)  # фикс высота

        step1_frame = wrap_with_frame(self.project_settings, "step1_frame", "ШАГ 1. Настройка проекта")
        step2_frame = wrap_with_frame(self.image_drop, "step2_frame", "ШАГ 2. Исходное изображение")
        step3_frame = wrap_with_frame(self.export_settings, "step3_frame", "ШАГ 3. Настройки экспорта изображения")

        # Объединённый шаг 2 и 3
        step_2_3_layout = QHBoxLayout()
        step_2_3_layout.setContentsMargins(0, 0, 0, 0)
        step_2_3_layout.addWidget(step2_frame, 2)
        step_2_3_layout.addWidget(step3_frame, 1)

        step_2_3_widget = QWidget()
        step_2_3_widget.setLayout(step_2_3_layout)
        step_2_3_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Главный layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addWidget(step1_frame, 0)
        main_layout.addWidget(step_2_3_widget, 1)

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

        self.update_res_list(res_dirs)

    def update_res_list(self, res_dirs):
        self.res_list.clear()
        for path in res_dirs:
            self.res_list.addItem(path)

        if res_dirs:
            self.res_list.setCurrentRow(0)  # авто-выбор первого элемента
            self.selected_res_path.setText(res_dirs[0])  # обновляем поле

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

        # Сохраняем конфиг
        self.config["project_path"] = self.project_settings.get_project_path()
        self.config["res_path"] = self.project_settings.get_selected_res_path()
        self.config["dpi_presets"] = self.export_settings.get_dpi_presets()
        self.config["dpi_enabled"] = self.export_settings.get_dpi_enabled()
        self.config["webp"] = self.export_settings.is_webp_enabled()
        save_config(self.config)

        QMessageBox.information(self, "Успех", "Все изображения успешно сохранены.")

    def on_conversion_error(self, message):
        self.export_settings.convert_button.setEnabled(True)
        self.export_settings.progress_bar.setVisible(False)
        self.export_settings.status_label.setVisible(False)
        QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении:\n{message}")

    def apply_config(self):
        # 1. Android проект
        project_path = self.config.get("project_path", "")
        if os.path.exists(project_path):
            self.project_settings.set_project_path(project_path)

        # 2. Путь до res
        res_path = self.config.get("res_path", "")
        if os.path.exists(res_path):
            self.project_settings.set_selected_res_path(res_path)

        # 3. Пресеты
        dpi_values = self.config.get("dpi_presets", {})
        dpi_enabled = self.config.get("dpi_enabled", {})
        self.export_settings.set_presets(dpi_values, dpi_enabled)

        # 4. WebP
        self.export_settings.set_webp_enabled(self.config.get("webp", False))
