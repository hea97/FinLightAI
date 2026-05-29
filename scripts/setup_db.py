from __future__ import annotations

from pathlib import Path


def main() -> None:
    schema = Path("database/schema.sql")
    print(f"Database schema is ready at {schema.resolve()}")
    print("Apply it to PostgreSQL with psql or a migration tool after DATABASE_URL is configured.")


if __name__ == "__main__":
    main()
