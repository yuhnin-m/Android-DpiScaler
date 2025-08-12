import os

from PySide6.QtCore import QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.config_manager import load_config, save_config
from core.frame_utils import wrap_with_frame
from core.image_exporter import ExportWorker
from domain.export_models import ExportRequest
from gui.export_settings_widget import ExportSettingsWidget
from gui.image_drop_widget import ImageDropWidget
from gui.project_settings_widget import ProjectSettingsWidget
from services.export_planner import build_preview_entries


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PNG2Drawable – Android DPI Exporter")
        self.setMinimumSize(1000, 500)
        self.thread = None
        self.worker = None

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

    def on_res_selected(self, _item):
        # Пока просто логика-заглушка, на будущее
        pass

    def on_convert_clicked(self):
        if not self.image_drop.image_path:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите изображение.")
            return

        base_res_path = self.project_settings.get_selected_res_path()
        if not base_res_path:
            QMessageBox.warning(self, "Ошибка", "Не выбран путь res/ для сохранения.")
            return

        config = self.export_settings.get_export_config()
        if config is None:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Проверьте имя файла, значения масштабов DPI и выберите хотя бы один DPI.",
            )
            return

        request = ExportRequest(
            image_path=self.image_drop.image_path,
            base_res_path=base_res_path,
            filename=config["filename"],
            dpi_scales=config["dpi"],
            to_webp=config["to_webp"],
        )

        try:
            preview_entries = build_preview_entries(request)
        except Exception as error:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подготовить превью экспорта:\n{error}")
            return

        preview_lines = [
            f"{entry.output_path} — {entry.width}x{entry.height} — ~{entry.size_kb:.1f} KB"
            for entry in preview_entries
        ]

        msg = QMessageBox(self)
        msg.setWindowTitle("Подтвердите сохранение")
        msg.setText("Будут созданы следующие файлы:\n\n" + "\n".join(preview_lines))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msg.exec()

        if result != QMessageBox.Ok:
            return

        if self.thread and self.thread.isRunning():
            QMessageBox.warning(self, "Подождите", "Экспорт уже выполняется.")
            return

        # Шаг 2 — блокируем кнопку и показываем прогресс
        self._set_export_running_ui(len(preview_entries))

        # Стартуем воркер в отдельном потоке
        self.thread = QThread()
        self.worker = ExportWorker(request)
        self.worker.moveToThread(self.thread)

        self.worker.progress.connect(self.export_settings.progress_bar.setValue)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_conversion_error)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self._clear_worker_refs)

        self.thread.start()

    def on_conversion_finished(self):
        self._reset_export_ui()

        # Сохраняем конфиг
        self.config["project_path"] = self.project_settings.get_project_path()
        self.config["res_path"] = self.project_settings.get_selected_res_path()
        self.config["dpi_presets"] = self.export_settings.get_dpi_presets()
        self.config["dpi_enabled"] = self.export_settings.get_dpi_enabled()
        self.config["webp"] = self.export_settings.is_webp_enabled()
        save_config(self.config)

        QMessageBox.information(self, "Успех", "Все изображения успешно сохранены.")

    def on_conversion_error(self, message):
        self._reset_export_ui()
        QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении:\n{message}")

    def _set_export_running_ui(self, total_steps: int):
        self.export_settings.convert_button.setEnabled(False)
        self.export_settings.progress_bar.setVisible(True)
        self.export_settings.status_label.setVisible(True)
        self.export_settings.progress_bar.setMaximum(total_steps)
        self.export_settings.progress_bar.setValue(0)
        self.export_settings.status_label.setText("Конвертация...")

    def _reset_export_ui(self):
        self.export_settings.convert_button.setEnabled(True)
        self.export_settings.progress_bar.setVisible(False)
        self.export_settings.status_label.setVisible(False)

    def _clear_worker_refs(self):
        self.thread = None
        self.worker = None

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

    def closeEvent(self, event: QCloseEvent):  # noqa: N802
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(2000)
        super().closeEvent(event)
