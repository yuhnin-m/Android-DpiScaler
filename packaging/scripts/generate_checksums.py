from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SHA256SUMS for artifact files.")
    parser.add_argument(
        "artifacts_dir",
        nargs="?",
        default="artifacts",
        help="Directory that contains build artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        [
            path
            for path in artifacts_dir.iterdir()
            if path.is_file() and path.name != "SHA256SUMS"
        ]
    )

    lines = [f"{sha256sum(path)}  {path.name}" for path in files]
    output_path = artifacts_dir / "SHA256SUMS"
    output_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    print(f"Checksums written to {output_path}")


if __name__ == "__main__":
    main()
