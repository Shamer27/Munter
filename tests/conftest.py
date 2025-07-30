import os
import sqlite3
import tempfile
import pytest

# Import your app module
import main


@pytest.fixture(scope="session")
def temp_db_path(tmp_path_factory):
    """Create a temporary SQLite DB path for the whole test session."""
    db_dir = tmp_path_factory.mktemp("db")
    db_path = os.path.join(db_dir, "test_flavors.db")
    return db_path


def _init_master_tables(db_path):
    """Create the master 'flavours' table and seed data."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # This is the master list table your code expects.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flavours (
            flavour TEXT PRIMARY KEY,
            caffeine INTEGER NOT NULL,
            size INTEGER NOT NULL
        );
    """)

    # Seed: use names that exist in your app list/colors/etc.
    seed = [
        ("Ultra Rosa", 150, 500),
        ("Ultra Red",  150, 500),
        ("Mango Loco", 152, 500),
        ("Absolutely Zero", 140, 500),
    ]
    cur.executemany("INSERT OR REPLACE INTO flavours (flavour, caffeine, size) VALUES (?, ?, ?)", seed)
    conn.commit()
    conn.close()


@pytest.fixture(autouse=True)
def patch_db_and_schema(monkeypatch, temp_db_path):
    """
    - Point main.DB_PATH to our temp DB
    - Ensure schema for flavours_device
    - Ensure master flavours exists and is seeded
    """
    monkeypatch.setattr(main, "DB_PATH", temp_db_path, raising=False)
    _init_master_tables(temp_db_path)

    # Ensure the per-device table exists
    main.ensure_schema()

    yield  # tests run here


@pytest.fixture()
def client():
    """Flask test client."""
    # Flask app object is "app" in main.py
    main.app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    with main.app.test_client() as client:
        yield client
