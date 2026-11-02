from pathlib import Path


def test_database_foundation_files_exist() -> None:
    backend = Path(__file__).parents[1]

    assert (backend / "app/db/base.py").exists()
    assert (backend / "app/db/session.py").exists()
    assert (backend / "alembic.ini").exists()
    assert (backend / "migrations/env.py").exists()
