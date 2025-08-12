from pathlib import Path

from PIL import Image

from domain.export_models import ExportRequest
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
