import os

from PIL import Image

from core.image_utils import get_resized_image_preview_info
from core.resource_name import validate_resource_name
from domain.export_models import ExportRequest, ExportTarget, PreviewEntry


def build_export_targets(request: ExportRequest) -> list[ExportTarget]:
    validate_resource_name(request.filename)

    targets: list[ExportTarget] = []
    for dpi, scale in request.dpi_scales.items():
        output_dir = os.path.join(request.base_res_path, f"drawable-{dpi}")
        output_path = os.path.join(output_dir, f"{request.filename}.{request.extension}")
        targets.append(
            ExportTarget(
                dpi=dpi,
                scale=scale,
                output_dir=output_dir,
                output_path=output_path,
            )
        )
    return targets


def build_preview_entries(request: ExportRequest) -> list[PreviewEntry]:
    targets = build_export_targets(request)
    entries: list[PreviewEntry] = []

    with Image.open(request.image_path) as source_image:
        image = source_image.copy()

    for target in targets:
        output_path, (width, height), size_kb = get_resized_image_preview_info(
            image=image,
            scale=target.scale,
            format=request.save_format,
            path=target.output_path,
        )
        entries.append(
            PreviewEntry(
                output_path=output_path,
                width=width,
                height=height,
                size_kb=size_kb,
            )
        )

    return entries
