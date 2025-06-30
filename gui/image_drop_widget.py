from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QSizePolicy
)
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QImageReader
from PySide6.QtCore import Qt, Signal

import os

ACCEPTED_FORMATS = (".png", ".jpg", ".jpeg", ".webp")

class ImageDropWidget(QWidget):
    # отправляем имя файла
    image_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.image_path = None

        self.drop_label = QLabel("Перетащите сюда изображение\nили нажмите кнопку ниже")
        self.drop_label.setAlignment(Qt.AlignCenter)

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(240)
        self.preview.setStyleSheet("border: 2px dashed #888; border-radius: 10px; background-color: #f0f0f0;")
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.meta_label = QLabel("Информация о файле:\n")
        self.meta_label.setAlignment(Qt.AlignTop)
        self.meta_label.setWordWrap(True)
        self.meta_label.setStyleSheet("color: #333;")


        self.button = QPushButton("Выбрать файл")
        self.button.clicked.connect(self.open_file_dialog)
        self.button.setStyleSheet("")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.addWidget(self.drop_label)
        layout.addWidget(self.preview)
        layout.addWidget(self.meta_label)
        layout.addWidget(self.button)
        layout.addStretch(1)

        self.setLayout(layout)

        self.setStyleSheet("""
            ImageDropWidget {
                border: 2px dashed #666;
                border-radius: 10px;
                padding: 20px;
                background-color: #fefefe;
            }
        """)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Изображения (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.set_image(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(ACCEPTED_FORMATS):
                self.set_image(path)
                break

    def set_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.preview.width(), self.preview.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.preview.setPixmap(scaled)
            info = self.get_image_info(path)
            self.meta_label.setText(info)
            self.image_path = path
            filename = os.path.basename(path)
            self.image_loaded.emit(filename)
        else:
            self.meta_label.setText("Ошибка загрузки изображения.")

    def get_image_info(self, path):
        try:
            size_kb = os.path.getsize(path) / 1024
            reader = QImageReader(path)
            size_px = reader.size()
            fmt = reader.format().data().decode('utf-8').upper()
            name = os.path.basename(path)
            return (
                f"<b>Путь:</b>\n{path}\n\n"
                f"<b>Имя файла:</b> {name}\n"
                f"<b>Размер:</b> {size_px.width()}x{size_px.height()} px\n"
                f"<b>Формат:</b> {fmt}\n"
                f"<b>Объём:</b> {size_kb:.1f} KB"
            )
        except Exception as e:
            return f"Ошибка чтения файла: {e}"
