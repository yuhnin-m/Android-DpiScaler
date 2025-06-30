import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QGroupBox, QGridLayout, QCheckBox, QHBoxLayout, QPushButton, QProgressBar
)

from core.validated_line_edit import ValidatedLineEdit


class ExportSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Имя файла
        self.export_name_label = QLabel("Имя файла:")
        self.export_name_input = QLineEdit()
        self.export_name_input.setPlaceholderText("по умолчанию — из имени файла")

        # Пресеты DPI
        self.dpi_widgets = {}
        dpi_group = QGroupBox("Настройки плотностей DPI")
        dpi_layout = QGridLayout()

        # кнопка сбросить
        self.reset_button = QPushButton("Пресеты по умолчанию")
        self.reset_button.clicked.connect(self.reset_defaults)

        # кнопка конвертировать
        self.convert_button = QPushButton("Сконвертировать")
        self.convert_button.setStyleSheet("font-weight: bold; font-size: 16px; padding: 10px;")
        self.convert_button.setFixedHeight(40)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        self.status_label = QLabel()
        self.status_label.setVisible(False)

        default_scales = {
            "mdpi": "0.25",
            "hdpi": "0.375",
            "xhdpi": "0.5",
            "xxhdpi": "0.75",
            "xxxhdpi": "1.0"
        }

        for i, (dpi, default_value) in enumerate(default_scales.items()):
            checkbox = QCheckBox(dpi)
            checkbox.setChecked(True)

            input_field = ValidatedLineEdit()
            input_field.setText(default_value)
            input_field.setFixedWidth(60)
            input_field.setToolTip("Масштаб относительно xxxhdpi")

            row_layout = QHBoxLayout()
            row_layout.addWidget(checkbox)
            row_layout.addWidget(QLabel("×"))
            row_layout.addWidget(input_field)

            dpi_layout.addLayout(row_layout, i, 0)
            self.dpi_widgets[dpi] = (checkbox, input_field)

        dpi_group.setLayout(dpi_layout)

        # Конвертация в WebP
        self.webp_checkbox = QCheckBox(f"Конвертировать в WebP")

        # Финальный layout
        layout = QVBoxLayout()
        layout.addWidget(self.export_name_label)
        layout.addWidget(self.export_name_input)
        layout.addWidget(dpi_group)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.webp_checkbox)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        self.setLayout(layout)

    def set_suggested_name(self, filename: str):
        name, _ = os.path.splitext(filename)
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        self.export_name_input.setText(name)

    def get_export_config(self):
        dpi_config = {}
        has_errors = False

        for dpi, (checkbox, input_field) in self.dpi_widgets.items():
            if checkbox.isChecked():
                text = input_field.text().strip()
                try:
                    scale = float(text)
                    if not (0.1 <= scale <= 10.0):
                        raise ValueError("Масштаб вне допустимого диапазона")

                    dpi_config[dpi] = scale
                    input_field.setStyleSheet("")  # сброс красной рамки

                except Exception:
                    input_field.setStyleSheet("border: 1px solid red;")
                    has_errors = True

        if has_errors:
            return None  # или кинуть исключение, или вернуть статус
        else:
            return {
                "filename": self.export_name_input.text().strip(),
                "dpi": dpi_config,
                "to_webp": self.webp_checkbox.isChecked()
            }

    def set_suggested_name(self, filename: str):
        # Убираем расширение
        name, _ = os.path.splitext(filename)
        # Заменяем всё, что Android не любит
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        self.export_name_input.setText(name)

    def reset_defaults(self):
        default_scales = {
            "mdpi": "0.25",
            "hdpi": "0.375",
            "xhdpi": "0.5",
            "xxhdpi": "0.75",
            "xxxhdpi": "1.0"
        }

        for dpi, (checkbox, input_field) in self.dpi_widgets.items():
            checkbox.setChecked(True)
            input_field.setText(default_scales.get(dpi, "1.0"))
            input_field.setStyleSheet("")  # убираем красную рамку, если была

