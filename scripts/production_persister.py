# scripts/production_ingest.py

from __future__ import annotations

import logging

from src.gitrec.config.settings import get_settings
from src.gitrec.persistence.postgres.connection import PostgresConnection
from src.gitrec.persistence.postgres.production.production_persistence import (
    ProductionPersistence,
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Execute production persistence of staging data."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings = get_settings()

    logger.info("Starting production persistence")

    with PostgresConnection(settings=settings) as postgres_connection:

        production_persistence = ProductionPersistence(
            connection=postgres_connection,
        )

        production_persistence.persist()


if __name__ == "__main__":
    main()