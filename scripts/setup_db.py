from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from config.settings import get_settings
from src.dashboard.database import normalize_database_url

BASELINE_REVISION = "09c4a8b3721a"


def main() -> None:
    settings = get_settings()
    project_root = settings.project_root
    alembic_config = Config(project_root / "alembic.ini")
    engine = create_engine(normalize_database_url(settings.database_url))
    table_names = set(inspect(engine).get_table_names())
    has_alembic_revision = False
    if "alembic_version" in table_names:
        with engine.connect() as connection:
            has_alembic_revision = (
                connection.execute(text("select count(*) from alembic_version")).scalar_one() > 0
            )
    engine.dispose()
    if "users" in table_names and not has_alembic_revision:
        command.stamp(alembic_config, BASELINE_REVISION)
    command.upgrade(alembic_config, "head")
    scheme = settings.database_url.split(":", 1)[0]
    print(f"FinLightAI database migrations are current using the {scheme} connection.")


if __name__ == "__main__":
    main()
