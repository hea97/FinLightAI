from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dashboard.database import SessionLocal  # noqa: E402
from src.dashboard.services.data_pipeline import refresh_pipeline_data  # noqa: E402


def main() -> None:
    with SessionLocal() as db:
        print(refresh_pipeline_data(db))


if __name__ == "__main__":
    main()
