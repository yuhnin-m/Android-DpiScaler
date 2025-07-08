import os
import json
import logging

from PySide6.QtCore import Qt
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

    def get_project_path(self):
        return self.project_path

    from PySide6.QtWidgets import QMessageBox
    from core.project_utils import find_all_res_dirs

    def set_project_path(self, path: str):
        self.project_path = path
        self.path_label.setText(path)

        res_dirs = find_all_res_dirs(path)
        self.res_list.clear()

        if not res_dirs:
            self.selected_res_path.setText("")
            QMessageBox.warning(self, "res/ директории не найдены",
                                "В выбранном проекте не обнаружено ни одной директории res/")
            return

        for d in res_dirs:
            self.res_list.addItem(d)

        # Если было выбрано что-то ранее, пробуем восстановить его
        selected = self.selected_res_path.text()
        if selected and selected in res_dirs:
            self.set_selected_res_path(selected)
        else:
            # По умолчанию выбираем первый
            self.set_selected_res_path(res_dirs[0])

    def set_selected_res_path(self, path: str):
        self.selected_res_path.setText(path)
        items = self.res_list.findItems(path, Qt.MatchExactly)
        if items:
            self.res_list.setCurrentItem(items[0])
