from pathlib import Path


def test_backend_foundation_declares_project_metadata() -> None:
    project_file = Path(__file__).parents[1] / "pyproject.toml"
    contents = project_file.read_text(encoding="utf-8")

    assert 'name = "codedock-backend"' in contents
    assert 'requires-python = ">=3.12"' in contents
