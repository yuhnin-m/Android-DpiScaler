from PySide6.QtCore import QObject, Signal
from PIL import Image
import os

class ExportWorker(QObject):
    progress = Signal(int)
    finished = Signal()
    error = Signal(str)

    def __init__(self, image_path, config, base_res_path):
        super().__init__()
        self.image_path = image_path
        self.config = config
        self.base_res_path = base_res_path

    def run(self):
        try:
            image = Image.open(self.image_path)
            width, height = image.size
            ext = "webp" if self.config["to_webp"] else "png"
            dpi_data = self.config["dpi"]
            filename = self.config["filename"]

            for i, (dpi, scale) in enumerate(dpi_data.items()):
                out_w = int(width * scale)
                out_h = int(height * scale)
                resized = image.resize((out_w, out_h), Image.LANCZOS)

                folder = os.path.join(self.base_res_path, f"drawable-{dpi}")
                os.makedirs(folder, exist_ok=True)
                out_path = os.path.join(folder, f"{filename}.{ext}")

                if os.path.exists(out_path):
                    os.remove(out_path)

                resized.save(out_path, format="WEBP" if self.config["to_webp"] else "PNG")
                self.progress.emit(i + 1)

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
