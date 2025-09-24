from __future__ import annotations

import os

from PySide6.QtCore import Qt, QThread, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.function_worker import FunctionWorker
from core.project_utils import find_all_res_dirs


class ProjectSettingsWidget(QWidget):
    def __init__(self, on_res_selected_callback):
        super().__init__()
        self.project_path = ""
        self.on_res_selected_callback = on_res_selected_callback
        self._scan_thread = None
        self._scan_worker = None
        self._preferred_res_path = None
        self._show_warning_on_empty_scan = False

        self.path_label = QLineEdit()
        self.path_label.setReadOnly(True)

        self.choose_button = QPushButton("Select project")
        self.choose_button.clicked.connect(self.select_project)

        self.res_list = QListWidget()
        self.res_list.currentItemChanged.connect(self.on_res_selected)

        self.scan_status_label = QLabel("")
        self.scan_status_label.setStyleSheet("color: #666;")

        self.selected_res_label = QLabel("Current save path:")
        self.selected_res_path = QLineEdit()
        self.selected_res_path.setReadOnly(True)

        # Top row: [path | button]
        path_row = QHBoxLayout()
        path_row.addWidget(self.path_label)
        path_row.addWidget(self.choose_button)

        # Left column
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("Android project path:"))
        left_col.addLayout(path_row)
        left_col.addWidget(self.scan_status_label)
        left_col.addWidget(self.selected_res_label)
        left_col.addWidget(self.selected_res_path)

        # Right column
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Detected res directories:"))
        right_col.addWidget(self.res_list, 0)

        left_col.setSpacing(4)
        left_col.setContentsMargins(0, 0, 0, 0)

        right_col.setSpacing(4)
        right_col.setContentsMargins(0, 0, 0, 0)

        # Final layout
        layout = QHBoxLayout()
        layout.addLayout(left_col, 1)
        layout.addLayout(right_col, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setMaximumHeight(130)
        self.setLayout(layout)

    def select_project(self):
        path = QFileDialog.getExistingDirectory(self, "Select project folder")
        if not path:
            return
        self.set_project_path(path, show_warning_if_empty=True)

    def update_res_list(self, res_dirs):
        self.res_list.clear()
        for path in res_dirs:
            item = QListWidgetItem(path)
            self.res_list.addItem(item)

    def on_res_selected(self, current, _previous):
        if current:
            self.selected_res_path.setText(current.text())
        else:
            self.selected_res_path.clear()
        self.on_res_selected_callback(current)

    def get_selected_res_path(self):
        current = self.res_list.currentItem()
        return current.text() if current else ""

    def get_project_path(self):
        return self.project_path

    def is_scanning(self) -> bool:
        return bool(self._scan_thread and self._scan_thread.isRunning())

    def stop_scan(self, wait_ms: int = 2000):
        if self.is_scanning():
            self._scan_thread.quit()
            self._scan_thread.wait(wait_ms)

    def set_project_path(
        self,
        path: str,
        preferred_res_path: str | None = None,
        show_warning_if_empty: bool = False,
    ):
        if not path or not os.path.isdir(path):
            return

        if self.is_scanning():
            QMessageBox.information(self, "Scanning", "Please wait until the current scan is finished.")
            return

        self.project_path = path
        self.path_label.setText(path)
        self._preferred_res_path = preferred_res_path or self.selected_res_path.text() or None
        self._show_warning_on_empty_scan = show_warning_if_empty
        self._start_scan(path)

    def set_selected_res_path(self, path: str):
        self.selected_res_path.setText(path)
        items = self.res_list.findItems(path, Qt.MatchExactly)
        if items:
            self.res_list.setCurrentItem(items[0])

    def _start_scan(self, project_path: str):
        self._set_scan_running_ui()

        self._scan_thread = QThread()
        self._scan_worker = FunctionWorker(find_all_res_dirs, project_path)
        self._scan_worker.moveToThread(self._scan_thread)

        self._scan_thread.started.connect(self._scan_worker.run)
        self._scan_worker.result.connect(self._on_scan_result, Qt.QueuedConnection)
        self._scan_worker.error.connect(self._on_scan_error, Qt.QueuedConnection)
        self._scan_worker.finished.connect(self._scan_thread.quit)

        self._scan_thread.finished.connect(self._scan_worker.deleteLater)
        self._scan_thread.finished.connect(self._scan_thread.deleteLater)
        self._scan_thread.finished.connect(self._clear_scan_refs)

        self._scan_thread.start()

    @Slot(object)
    def _on_scan_result(self, result):
        res_dirs = list(result) if isinstance(result, list) else []
        self.update_res_list(res_dirs)

        if not res_dirs:
            self.selected_res_path.clear()
            self.scan_status_label.setText("No res/ directories found")
            if self._show_warning_on_empty_scan:
                QMessageBox.warning(self, "Error", "No res/ directories found in project subfolders.")
            return

        preferred = self._preferred_res_path
        if preferred and preferred in res_dirs:
            self.set_selected_res_path(preferred)
        else:
            self.res_list.setCurrentRow(0)

        self.scan_status_label.setText(f"Found res/ directories: {len(res_dirs)}")

    @Slot(str)
    def _on_scan_error(self, message: str):
        self.update_res_list([])
        self.selected_res_path.clear()
        self.scan_status_label.setText("Scan failed")
        QMessageBox.critical(self, "Error", f"Failed to scan project:\n{message}")

    def _set_scan_running_ui(self):
        self.choose_button.setEnabled(False)
        self.res_list.setEnabled(False)
        self.scan_status_label.setText("Scanning project...")

    def _clear_scan_refs(self):
        self.choose_button.setEnabled(True)
        self.res_list.setEnabled(True)
        self._scan_thread = None
        self._scan_worker = None

    def closeEvent(self, event: QCloseEvent):  # noqa: N802
        self.stop_scan()
        super().closeEvent(event)
