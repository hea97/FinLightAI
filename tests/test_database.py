from src.dashboard.database import normalize_database_url


def test_render_postgres_url_uses_psycopg_v3_driver() -> None:
    assert normalize_database_url("postgresql://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )
    assert normalize_database_url("postgres://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )


def test_explicit_driver_and_sqlite_urls_are_unchanged() -> None:
    assert normalize_database_url("postgresql+psycopg://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )
    assert normalize_database_url("sqlite:///./data/test.db") == "sqlite:///./data/test.db"
