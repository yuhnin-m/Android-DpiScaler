from PIL import Image
from io import BytesIO

def get_resized_image_preview_info(image: Image.Image, scale: float, format: str, path: str) -> tuple[str, tuple[int, int], float]:
    """
    Возвращает информацию о ресайзнутом изображении:
    - путь
    - размер (width, height)
    - примерный вес в килобайтах
    """
    width, height = image.size
    new_w = int(width * scale)
    new_h = int(height * scale)

    resized = image.resize((new_w, new_h), Image.LANCZOS)
    buffer = BytesIO()
    resized.save(buffer, format=format)
    size_kb = len(buffer.getvalue()) / 1024

    return path, (new_w, new_h), size_kb
