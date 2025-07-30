from pathlib import Path

from core.project_utils import find_all_res_dirs


def test_find_all_res_dirs_excludes_build_generated(tmp_path: Path) -> None:
    app_res = tmp_path / "app" / "src" / "main" / "res"
    generated_res = tmp_path / "feature" / "build" / "generated" / "res"
    plain_res = tmp_path / "lib" / "res"

    app_res.mkdir(parents=True)
    generated_res.mkdir(parents=True)
    plain_res.mkdir(parents=True)

    found = find_all_res_dirs(str(tmp_path))

    assert str(app_res) in found
    assert str(plain_res) in found
    assert str(generated_res) not in found
