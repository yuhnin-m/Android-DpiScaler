from PIL import Image

from core.image_utils import get_resized_image_preview_info


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
