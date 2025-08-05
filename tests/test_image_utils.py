from PIL import Image

from core.image_utils import get_resized_image_preview_info, get_scaled_dimensions


def test_get_resized_image_preview_info_returns_expected_dimensions() -> None:
    image = Image.new("RGBA", (100, 50), (255, 0, 0, 255))

    path, (width, height), size_kb = get_resized_image_preview_info(
        image=image,
        scale=0.5,
        format="PNG",
        path="/tmp/example.png",
    )

    assert path == "/tmp/example.png"
    assert width == 50
    assert height == 25
    assert size_kb > 0


def test_get_scaled_dimensions_clamps_to_minimum_1px() -> None:
    width, height = get_scaled_dimensions((1, 1), 0.1)
    assert width == 1
    assert height == 1
