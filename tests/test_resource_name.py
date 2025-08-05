import pytest

from core.resource_name import sanitize_resource_name, validate_resource_name


def test_sanitize_resource_name_uses_basename_and_lowercase() -> None:
    assert sanitize_resource_name("/tmp/My Icon@2x.png") == "my_icon_2x"


def test_sanitize_resource_name_prefixes_digit_start() -> None:
    assert sanitize_resource_name("123logo.png") == "img_123logo"


def test_validate_resource_name_accepts_valid_name() -> None:
    validate_resource_name("ic_launcher_foreground")


@pytest.mark.parametrize("invalid_name", ["", "/tmp/evil", "../evil", "Some-Name", "123icon"])
def test_validate_resource_name_rejects_invalid_names(invalid_name: str) -> None:
    with pytest.raises(ValueError):
        validate_resource_name(invalid_name)
