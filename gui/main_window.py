from __future__ import annotations

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
from core.function_worker import FunctionWorker
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
        self.preview_thread = None
        self.preview_worker = None
        self.export_thread = None
        self.export_worker = None

        self.config = load_config()
        self.init_widgets()
        self.init_layout()
        self.apply_config()

    def init_widgets(self):
        self.project_settings = ProjectSettingsWidget(self.on_res_selected)
        self.image_drop = ImageDropWidget()
        self.export_settings = ExportSettingsWidget()

        self.export_settings.convert_button.clicked.connect(self.on_convert_clicked)
        self.image_drop.image_loaded.connect(self.export_settings.set_suggested_name)

    def init_layout(self):
        step1_title = QLabel("<b>ШАГ 1. Настройка проекта</b>")
        step2_title = QLabel("<b>ШАГ 2. Исходное изображение</b>")
        step3_title = QLabel("<b>ШАГ 3. Настройки экспорта изображения</b>")

        step1_layout = QVBoxLayout()
        step1_layout.addWidget(step1_title)
        step1_layout.addWidget(self.project_settings)

        step1_widget = QWidget()
        step1_widget.setLayout(step1_layout)
        step1_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        step2_layout = QVBoxLayout()
        step2_layout.addWidget(step2_title)
        step2_layout.addWidget(self.image_drop)
        step2_layout.setStretch(1, 1)

        step3_layout = QVBoxLayout()
        step3_layout.addWidget(step3_title)
        step3_layout.addWidget(self.export_settings)
        step3_layout.setStretch(1, 0)

        step1_frame = wrap_with_frame(self.project_settings, "step1_frame", "ШАГ 1. Настройка проекта")
        step2_frame = wrap_with_frame(self.image_drop, "step2_frame", "ШАГ 2. Исходное изображение")
        step3_frame = wrap_with_frame(self.export_settings, "step3_frame", "ШАГ 3. Настройки экспорта изображения")

        step_2_3_layout = QHBoxLayout()
        step_2_3_layout.setContentsMargins(0, 0, 0, 0)
        step_2_3_layout.addWidget(step2_frame, 2)
        step_2_3_layout.addWidget(step3_frame, 1)

        step_2_3_widget = QWidget()
        step_2_3_widget.setLayout(step_2_3_layout)
        step_2_3_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(step1_frame, 0)
        main_layout.addWidget(step_2_3_widget, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def on_res_selected(self, _item):
        pass

    def on_convert_clicked(self):
        if self.project_settings.is_scanning():
            QMessageBox.information(self, "Сканирование", "Дождитесь завершения сканирования проекта.")
            return

        if self._is_busy():
            QMessageBox.warning(self, "Подождите", "Операция уже выполняется.")
            return

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
        self._start_preview_job(request)

    def _start_preview_job(self, request: ExportRequest):
        self._set_preview_running_ui()

        self.preview_thread = QThread()
        self.preview_worker = FunctionWorker(build_preview_entries, request)
        self.preview_worker.moveToThread(self.preview_thread)

        self.preview_thread.started.connect(self.preview_worker.run)
        self.preview_worker.result.connect(
            lambda entries, current_request=request: self._on_preview_ready(current_request, entries)
        )
        self.preview_worker.error.connect(self._on_preview_error)
        self.preview_worker.finished.connect(self.preview_thread.quit)

        self.preview_thread.finished.connect(self.preview_worker.deleteLater)
        self.preview_thread.finished.connect(self.preview_thread.deleteLater)
        self.preview_thread.finished.connect(self._clear_preview_refs)

        self.preview_thread.start()

    def _on_preview_ready(self, request: ExportRequest, result):
        preview_entries = list(result) if isinstance(result, list) else []
        if not preview_entries:
            self._reset_export_ui()
            QMessageBox.warning(self, "Ошибка", "Не удалось подготовить данные для предпросмотра.")
            return

        preview_lines = [
            f"{entry.output_path} — {entry.width}x{entry.height} — ~{entry.size_kb:.1f} KB"
            for entry in preview_entries
        ]

        msg = QMessageBox(self)
        msg.setWindowTitle("Подтвердите сохранение")
        msg.setText("Будут созданы следующие файлы:\n\n" + "\n".join(preview_lines))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result_code = msg.exec()

        if result_code != QMessageBox.Ok:
            self._reset_export_ui()
            return

        self._start_export_job(request, len(preview_entries))

    def _on_preview_error(self, message: str):
        self._reset_export_ui()
        QMessageBox.critical(self, "Ошибка", f"Не удалось подготовить превью экспорта:\n{message}")

    def _start_export_job(self, request: ExportRequest, total_steps: int):
        if self._is_export_running():
            QMessageBox.warning(self, "Подождите", "Экспорт уже выполняется.")
            self._reset_export_ui()
            return

        self._set_export_running_ui(total_steps)

        self.export_thread = QThread()
        self.export_worker = ExportWorker(request)
        self.export_worker.moveToThread(self.export_thread)

        self.export_worker.progress.connect(self.export_settings.progress_bar.setValue)
        self.export_worker.finished.connect(self.on_conversion_finished)
        self.export_worker.error.connect(self.on_conversion_error)

        self.export_thread.started.connect(self.export_worker.run)
        self.export_worker.finished.connect(self.export_thread.quit)
        self.export_worker.error.connect(self.export_thread.quit)

        self.export_thread.finished.connect(self.export_worker.deleteLater)
        self.export_thread.finished.connect(self.export_thread.deleteLater)
        self.export_thread.finished.connect(self._clear_export_refs)

        self.export_thread.start()

    def on_conversion_finished(self):
        self._reset_export_ui()
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

    def _set_preview_running_ui(self):
        self.export_settings.convert_button.setEnabled(False)
        self.export_settings.progress_bar.setVisible(True)
        self.export_settings.status_label.setVisible(True)
        self.export_settings.progress_bar.setRange(0, 0)
        self.export_settings.status_label.setText("Подготовка превью...")

    def _set_export_running_ui(self, total_steps: int):
        self.export_settings.convert_button.setEnabled(False)
        self.export_settings.progress_bar.setVisible(True)
        self.export_settings.status_label.setVisible(True)
        self.export_settings.progress_bar.setRange(0, max(total_steps, 1))
        self.export_settings.progress_bar.setValue(0)
        self.export_settings.status_label.setText("Конвертация...")

    def _reset_export_ui(self):
        self.export_settings.convert_button.setEnabled(True)
        self.export_settings.progress_bar.setVisible(False)
        self.export_settings.status_label.setVisible(False)
        self.export_settings.progress_bar.setRange(0, 1)

    def _clear_preview_refs(self):
        self.preview_thread = None
        self.preview_worker = None

    def _clear_export_refs(self):
        self.export_thread = None
        self.export_worker = None

    def _is_preview_running(self) -> bool:
        return bool(self.preview_thread and self.preview_thread.isRunning())

    def _is_export_running(self) -> bool:
        return bool(self.export_thread and self.export_thread.isRunning())

    def _is_busy(self) -> bool:
        return self._is_preview_running() or self._is_export_running()

    def apply_config(self):
        project_path = self.config.get("project_path", "")
        res_path = self.config.get("res_path", "")
        preferred_res_path = res_path if os.path.exists(res_path) else None

        if os.path.exists(project_path):
            self.project_settings.set_project_path(
                project_path,
                preferred_res_path=preferred_res_path,
                show_warning_if_empty=False,
            )

        dpi_values = self.config.get("dpi_presets", {})
        dpi_enabled = self.config.get("dpi_enabled", {})
        self.export_settings.set_presets(dpi_values, dpi_enabled)
        self.export_settings.set_webp_enabled(self.config.get("webp", False))

    def closeEvent(self, event: QCloseEvent):  # noqa: N802
        self.project_settings.stop_scan()
        for thread in (self.preview_thread, self.export_thread):
            if thread and thread.isRunning():
                thread.quit()
                thread.wait(2000)
        super().closeEvent(event)
