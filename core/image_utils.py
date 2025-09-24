from io import BytesIO

from PIL import Image


def get_scaled_dimensions(size: tuple[int, int], scale: float) -> tuple[int, int]:
    width, height = size
    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))
    return new_width, new_height


def get_resized_image_preview_info(
    image: Image.Image,
    scale: float,
    format: str,
    path: str,
) -> tuple[str, tuple[int, int], float]:
    """
    Return preview metadata for a resized image:
    - output path
    - dimensions (width, height)
    - approximate size in kilobytes
    """
    new_w, new_h = get_scaled_dimensions(image.size, scale)

    resized = image.resize((new_w, new_h), Image.LANCZOS)
    buffer = BytesIO()
    resized.save(buffer, format=format)
    size_kb = len(buffer.getvalue()) / 1024

    return path, (new_w, new_h), size_kb
