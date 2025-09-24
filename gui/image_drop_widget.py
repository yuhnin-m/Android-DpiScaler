import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QImageReader, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

ACCEPTED_FORMATS = (".png", ".jpg", ".jpeg", ".webp")


class ImageDropWidget(QWidget):
    image_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.image_path = None

        # === preview + drag area ===
        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("""
            QFrame {
                border: 2px dashed #888;
                border-radius: 10px;
                background-color: transparent;
            }
        """)

        preview_layout = QStackedLayout(self.preview_container)
        self.drop_label = QLabel("Drop an image here\nor click the button above")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("color: gray;")

        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        preview_layout.addWidget(self.drop_label)
        preview_layout.addWidget(self.preview)
        preview_layout.setCurrentWidget(self.drop_label)

        # === image metadata ===
        self.meta_label = QLabel("File info will appear here:\n")
        self.meta_label.setAlignment(Qt.AlignTop)
        self.meta_label.setWordWrap(True)

        self.meta_container = QFrame()
        self.meta_container.setObjectName("meta_container")
        self.meta_container.setFrameShape(QFrame.StyledPanel)
        self.meta_container.setStyleSheet("""
            #meta_container {
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 2px;
            }
        """)

        meta_layout = QVBoxLayout()
        # meta_layout.setContentsMargins(4, 4, 4, 4)
        meta_layout.addWidget(self.meta_label)
        self.meta_container.setLayout(meta_layout)

        # === open file button ===
        self.button = QPushButton("Select file")
        self.button.clicked.connect(self.open_file_dialog)

        # === final layout ===
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.setSpacing(8)
        layout.addWidget(self.button)
        layout.addWidget(self.preview_container, 1)  # expandable
        layout.addWidget(self.meta_container, 0)     # at the bottom

        self.setLayout(layout)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select image", "", "Images (*.png *.jpg *.jpeg *.webp)"
        )
        if path:
            self.set_image(path)

    def dragEnterEvent(self, event: QDragEnterEvent):  # noqa: N802
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):  # noqa: N802
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(ACCEPTED_FORMATS):
                self.set_image(path)
                break

    def set_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.preview_container.width(), self.preview_container.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.preview.setPixmap(scaled)
            self.preview_container.layout().setCurrentWidget(self.preview)

            info = self.get_image_info(path)
            self.meta_label.setText(info)
            self.image_path = path
            self.image_loaded.emit(path)
        else:
            self.meta_label.setText("Failed to load image.")

    def get_image_info(self, path):
        try:
            size_kb = os.path.getsize(path) / 1024
            reader = QImageReader(path)
            size_px = reader.size()
            fmt = reader.format().data().decode('utf-8').upper()
            name = os.path.basename(path)
            return (
                f"<b>Path:</b>\n{path}<br>"
                f"<b>File name:</b> {name}<br>"
                f"<b>Size:</b> {size_px.width()}x{size_px.height()} px<br>"
                f"<b>Format:</b> {fmt}<br>"
                f"<b>File size:</b> {size_kb:.1f} KB"
            )
        except Exception as e:
            return f"Failed to read file: {e}"
