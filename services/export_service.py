from __future__ import annotations

from collections.abc import Callable

from PIL import Image

from core.image_utils import get_scaled_dimensions
from domain.export_models import ExportRequest
from infrastructure.atomic_file import atomic_save_image
from services.export_planner import build_export_targets


def execute_export(
    request: ExportRequest,
    progress_callback: Callable[[int], None] | None = None,
) -> None:
    targets = build_export_targets(request)

    with Image.open(request.image_path) as source_image:
        image = source_image.copy()

    for index, target in enumerate(targets, start=1):
        width, height = get_scaled_dimensions(image.size, target.scale)
        resized = image.resize((width, height), Image.LANCZOS)
        atomic_save_image(resized, target.output_path, request.save_format)

        if progress_callback:
            progress_callback(index)
