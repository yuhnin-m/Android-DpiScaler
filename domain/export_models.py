from dataclasses import dataclass


@dataclass(frozen=True)
class ExportRequest:
    image_path: str
    base_res_path: str
    filename: str
    dpi_scales: dict[str, float]
    to_webp: bool

    @property
    def extension(self) -> str:
        return "webp" if self.to_webp else "png"

    @property
    def save_format(self) -> str:
        return "WEBP" if self.to_webp else "PNG"


@dataclass(frozen=True)
class ExportTarget:
    dpi: str
    scale: float
    output_dir: str
    output_path: str


@dataclass(frozen=True)
class PreviewEntry:
    output_path: str
    width: int
    height: int
    size_kb: float
