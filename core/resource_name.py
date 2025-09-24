import os
import re

RESOURCE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def sanitize_resource_name(raw_name: str) -> str:
    candidate = os.path.basename(raw_name.strip())
    candidate = os.path.splitext(candidate)[0]
    candidate = candidate.lower()
    candidate = re.sub(r"[^a-z0-9_]", "_", candidate)
    candidate = re.sub(r"_+", "_", candidate).strip("_")

    if not candidate:
        return ""

    if candidate[0].isdigit():
        candidate = f"img_{candidate}"

    return candidate


def validate_resource_name(name: str) -> None:
    if not name:
        raise ValueError("File name cannot be empty.")

    separators = [sep for sep in (os.sep, os.altsep) if sep]
    if os.path.isabs(name) or ".." in name or any(sep in name for sep in separators):
        raise ValueError("File name must not contain paths or '..'.")

    if not RESOURCE_NAME_PATTERN.fullmatch(name):
        raise ValueError("Only lowercase letters, digits, and '_' are allowed (must start with a letter).")
