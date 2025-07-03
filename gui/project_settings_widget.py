import os
import json
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QListWidgetItem, QSizePolicy
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
        # self.res_list.setMaximumHeight(50)
        self.res_list.currentItemChanged.connect(self.on_res_selected)

        self.selected_res_label = QLabel("Выбран текущий путь для сохранения:")
        self.selected_res_path = QLineEdit()
        self.selected_res_path.setReadOnly(True)

        # Верхняя строка: [ путь | кнопка ]
        path_row = QHBoxLayout()
        path_row.addWidget(self.path_label)
        path_row.addWidget(self.choose_button)

        # Левая колонка
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("Путь к Android-проекту:"))
        left_col.addLayout(path_row)
        left_col.addWidget(self.selected_res_label)
        left_col.addWidget(self.selected_res_path)

        # Правая колонка
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Найденные res директории:"))
        right_col.addWidget(self.res_list, 0)

        left_col.setSpacing(4)
        left_col.setContentsMargins(0, 0, 0, 0)

        right_col.setSpacing(4)
        right_col.setContentsMargins(0, 0, 0, 0)

        # Итоговая компоновка
        layout = QHBoxLayout()
        layout.addLayout(left_col, 1)
        layout.addLayout(right_col, 1)
        # layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setMaximumHeight(100)
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
