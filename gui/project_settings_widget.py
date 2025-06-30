import os
import json
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QListWidgetItem
)

from core.project_utils import find_all_res_dirs

CONFIG_PATH = "config.json"


class ProjectSettingsWidget(QWidget):
    def __init__(self, on_res_selected_callback):
        super().__init__()
        self.project_path = ""
        self.on_res_selected_callback = on_res_selected_callback

        self.path_label = QLineEdit()
        self.path_label.setReadOnly(True)

        self.choose_button = QPushButton("Выбрать проект")
        self.choose_button.clicked.connect(self.select_project)

        self.res_list = QListWidget()
        self.res_list.currentItemChanged.connect(self.on_res_selected)

        self.selected_res_label = QLabel("Выбран текущий путь для сохранения:")
        self.selected_res_path = QLineEdit()
        self.selected_res_path.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<b>Шаг 1. Настройка проекта</b>"))
        layout.addWidget(QLabel("Путь к проекту:"))
        layout.addWidget(self.path_label)
        layout.addWidget(self.choose_button)
        layout.addWidget(QLabel("Найденные res директории:"))
        layout.addWidget(self.res_list)
        layout.addWidget(self.selected_res_label)
        layout.addWidget(self.selected_res_path)
        self.setLayout(layout)

        self.load_last_path()

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

    def update_res_list(self, res_dirs):
        self.res_list.clear()
        for path in res_dirs:
            item = QListWidgetItem(path)
            self.res_list.addItem(item)
        if res_dirs:
            self.res_list.setCurrentRow(0)

    def on_res_selected(self, current, previous):
        if current:
            self.selected_res_path.setText(current.text())
        else:
            self.selected_res_path.clear()
        self.on_res_selected_callback(current)

    def get_selected_res_path(self):
        current = self.res_list.currentItem()
        return current.text() if current else ""

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
