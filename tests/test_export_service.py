from pathlib import Path

import pytest
from PIL import Image

from domain.export_models import ExportRequest
from services import export_service
from services.export_service import execute_export


def test_execute_export_creates_density_files_with_expected_sizes(tmp_path: Path) -> None:
    image_path = tmp_path / "source.png"
    base_res_path = tmp_path / "res"
    Image.new("RGBA", (20, 10), (0, 120, 255, 255)).save(image_path)

    request = ExportRequest(
        image_path=str(image_path),
        base_res_path=str(base_res_path),
        filename="sample_image",
        dpi_scales={"mdpi": 0.25, "xxhdpi": 0.75},
        to_webp=False,
    )

    execute_export(request)

    mdpi_path = base_res_path / "drawable-mdpi" / "sample_image.png"
    xxhdpi_path = base_res_path / "drawable-xxhdpi" / "sample_image.png"
    assert mdpi_path.exists()
    assert xxhdpi_path.exists()

    with Image.open(mdpi_path) as mdpi_image:
        assert mdpi_image.size == (5, 2)

    with Image.open(xxhdpi_path) as xxhdpi_image:
        assert xxhdpi_image.size == (15, 7)


def test_execute_export_calls_progress_callback_for_each_target(tmp_path: Path) -> None:
    image_path = tmp_path / "source.png"
    base_res_path = tmp_path / "res"
    Image.new("RGBA", (20, 10), (255, 255, 255, 255)).save(image_path)

    request = ExportRequest(
        image_path=str(image_path),
        base_res_path=str(base_res_path),
        filename="sample_image",
        dpi_scales={"mdpi": 0.25, "hdpi": 0.375, "xhdpi": 0.5},
        to_webp=False,
    )

    events = []
    execute_export(request, progress_callback=events.append)
    assert events == [1, 2, 3]


def test_execute_export_overwrites_existing_target_file(tmp_path: Path) -> None:
    image_path = tmp_path / "source.png"
    base_res_path = tmp_path / "res"
    output_path = base_res_path / "drawable-mdpi" / "sample_image.png"
    output_path.parent.mkdir(parents=True)
    Image.new("RGBA", (2, 2), (0, 0, 0, 255)).save(output_path)
    Image.new("RGBA", (20, 10), (0, 120, 255, 255)).save(image_path)

    request = ExportRequest(
        image_path=str(image_path),
        base_res_path=str(base_res_path),
        filename="sample_image",
        dpi_scales={"mdpi": 0.25},
        to_webp=False,
    )

    execute_export(request)

    with Image.open(output_path) as image:
        assert image.size == (5, 2)


def test_execute_export_keeps_existing_file_when_write_fails(tmp_path: Path, monkeypatch) -> None:
    image_path = tmp_path / "source.png"
    base_res_path = tmp_path / "res"
    output_path = base_res_path / "drawable-mdpi" / "sample_image.png"
    output_path.parent.mkdir(parents=True)
    Image.new("RGBA", (3, 3), (0, 0, 0, 255)).save(output_path)
    Image.new("RGBA", (20, 10), (0, 120, 255, 255)).save(image_path)

    request = ExportRequest(
        image_path=str(image_path),
        base_res_path=str(base_res_path),
        filename="sample_image",
        dpi_scales={"mdpi": 0.25},
        to_webp=False,
    )

    def fail_save(*_args, **_kwargs):
        raise PermissionError("write denied")

    monkeypatch.setattr(export_service, "atomic_save_image", fail_save)

    with pytest.raises(PermissionError):
        execute_export(request)

    with Image.open(output_path) as existing:
        assert existing.size == (3, 3)
