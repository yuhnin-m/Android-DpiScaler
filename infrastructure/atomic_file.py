import os
import tempfile

from PIL import Image


def atomic_save_image(image: Image.Image, output_path: str, save_format: str) -> None:
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=".png2drawable_",
            suffix=f".{save_format.lower()}",
            dir=output_dir,
            delete=False,
        ) as tmp_file:
            tmp_path = tmp_file.name

        image.save(tmp_path, format=save_format)
        os.replace(tmp_path, output_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
