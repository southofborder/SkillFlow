import zipfile

import pytest

from skillflow.common.inputs.skill_package import SkillPackageError
from skillflow.common.inputs.skill_package import load_skill_package


def test_directory_loader_preserves_text_and_classifies_binary(tmp_path) -> None:
    root = tmp_path / "sample"
    root.mkdir()
    (root / "SKILL.md").write_bytes(b"# Title\nstep one\n")
    (root / "run.py").write_bytes(b"print('hello')\n")
    (root / "config.json").write_bytes(b'{"enabled": true}\n')
    (root / "image.bin").write_bytes(b"\x00\x01\x02")

    package = load_skill_package(root)

    assert package.root_name == "sample"
    assert [item.path for item in package.files] == [
        "SKILL.md",
        "config.json",
        "image.bin",
        "run.py",
    ]
    assert package.files[0].kind == "markdown"
    assert package.files[0].content == "# Title\nstep one\n"
    assert package.files[1].kind == "text"
    assert package.files[2].kind == "binary"
    assert package.files[2].content is None
    assert package.files[2].size == 3


def test_zip_loader_strips_single_wrapper_directory(tmp_path) -> None:
    archive_path = tmp_path / "sample.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("wrapped/SKILL.md", "# Wrapped\n")
        archive.writestr("wrapped/scripts/run.sh", "echo ok\n")

    package = load_skill_package(archive_path)

    assert package.root_name == "wrapped"
    assert [item.path for item in package.files] == ["SKILL.md", "scripts/run.sh"]
    assert package.files[1].kind == "code"


def test_zip_loader_rejects_path_traversal(tmp_path) -> None:
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../outside.txt", "not safe")

    with pytest.raises(SkillPackageError, match="unsafe package path"):
        load_skill_package(archive_path)
