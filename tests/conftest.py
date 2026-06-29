from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.dashboard.app import app
from src.dashboard.database import Base, get_db


@pytest.fixture(autouse=True)
def isolated_dashboard_database(tmp_path) -> Generator[None, None, None]:
    """Keep every FastAPI test request out of the development database."""
    database_path = tmp_path / "finlightai-test.db"
    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    test_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()
