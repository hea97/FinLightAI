from __future__ import annotations

from config.settings import get_settings
from src.dashboard.database import create_tables


def main() -> None:
    settings = get_settings()
    create_tables()
    scheme = settings.database_url.split(":", 1)[0]
    print(f"FinLightAI database tables are ready using the {scheme} connection.")


if __name__ == "__main__":
    main()
