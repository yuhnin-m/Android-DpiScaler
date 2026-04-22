from pathlib import Path

import pytest
from PIL import Image

from domain.export_models import ExportRequest
from services.export_planner import build_export_targets, build_preview_entries


def test_build_export_targets_and_preview_do_not_create_output_dirs(tmp_path: Path) -> None:
    image_path = tmp_path / "source.png"
    base_res_path = tmp_path / "res"
    Image.new("RGBA", (10, 8), (255, 0, 0, 255)).save(image_path)

    request = ExportRequest(
        image_path=str(image_path),
        base_res_path=str(base_res_path),
        filename="ic_launcher",
        dpi_scales={"mdpi": 0.5, "xhdpi": 1.0},
        to_webp=False,
    )

    targets = build_export_targets(request)
    assert len(targets) == 2
    assert Path(targets[0].output_path).as_posix().endswith("drawable-mdpi/ic_launcher.png")
    assert Path(targets[1].output_path).as_posix().endswith("drawable-xhdpi/ic_launcher.png")

    previews = build_preview_entries(request)
    assert len(previews) == 2
    assert previews[0].width == 5
    assert previews[0].height == 4
    assert previews[1].width == 10
    assert previews[1].height == 8

    assert not (base_res_path / "drawable-mdpi").exists()
    assert not (base_res_path / "drawable-xhdpi").exists()


def test_build_export_targets_rejects_invalid_filename(tmp_path: Path) -> None:
    image_path = tmp_path / "source.png"
    Image.new("RGBA", (10, 8), (255, 0, 0, 255)).save(image_path)

    request = ExportRequest(
        image_path=str(image_path),
        base_res_path=str(tmp_path / "res"),
        filename="../evil",
        dpi_scales={"mdpi": 0.5},
        to_webp=False,
    )

    with pytest.raises(ValueError):
        build_export_targets(request)
