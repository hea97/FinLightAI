from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import get_settings


class Base(DeclarativeBase):
    pass


def normalize_database_url(database_url: str) -> str:
    """Use the installed psycopg v3 driver for common hosted Postgres URLs."""
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def _create_engine():
    database_url = normalize_database_url(get_settings().database_url)
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def create_tables() -> None:
    from src.dashboard import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_users_table()


def _migrate_sqlite_users_table() -> None:
    """Apply the small, idempotent SQLite migration required by the MVP user model."""
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    existing = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "provider": "ALTER TABLE users ADD COLUMN provider VARCHAR(40) NOT NULL DEFAULT 'local'",
        "provider_user_id": "ALTER TABLE users ADD COLUMN provider_user_id VARCHAR(255)",
        "profile_image_url": "ALTER TABLE users ADD COLUMN profile_image_url TEXT",
        "updated_at": "ALTER TABLE users ADD COLUMN updated_at DATETIME",
    }

    with engine.begin() as connection:
        for column, statement in additions.items():
            if column not in existing:
                connection.execute(text(statement))
        connection.execute(text("UPDATE users SET provider = 'local' WHERE provider IS NULL OR provider = ''"))
        connection.execute(text("UPDATE users SET provider_user_id = id WHERE provider_user_id IS NULL"))
        connection.execute(text("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_users_provider ON users (provider)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_users_provider_user_id ON users (provider_user_id)"))
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_provider_identity "
                "ON users (provider, provider_user_id)"
            )
        )


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
