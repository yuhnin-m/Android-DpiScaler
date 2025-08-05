import os
import tempfile

from PIL import Image
from PySide6.QtCore import QObject, Signal

from core.image_utils import get_scaled_dimensions
from core.resource_name import validate_resource_name


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
            with Image.open(self.image_path) as src:
                image = src.copy()

            ext = "webp" if self.config["to_webp"] else "png"
            save_format = "WEBP" if self.config["to_webp"] else "PNG"
            dpi_data = self.config["dpi"]
            filename = self.config["filename"]
            validate_resource_name(filename)

            for i, (dpi, scale) in enumerate(dpi_data.items()):
                out_w, out_h = get_scaled_dimensions(image.size, scale)
                resized = image.resize((out_w, out_h), Image.LANCZOS)

                folder = os.path.join(self.base_res_path, f"drawable-{dpi}")
                os.makedirs(folder, exist_ok=True)
                out_path = os.path.join(folder, f"{filename}.{ext}")
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(
                        prefix=f".{filename}_",
                        suffix=f".{ext}",
                        dir=folder,
                        delete=False,
                    ) as tmp:
                        tmp_path = tmp.name
                    resized.save(tmp_path, format=save_format)
                    os.replace(tmp_path, out_path)
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)

                self.progress.emit(i + 1)

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
