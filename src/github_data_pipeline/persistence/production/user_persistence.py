# src/github_data_pipeline/persistence/postgres/production/user_persistence.py

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.github_data_pipeline.persistence.production.base_persistence import (
    ProductionBasePersistence,
)


Record = dict[str, Any]
Records = dict[str, list[Record]]


class ProductionUserPersistence(ProductionBasePersistence):
    """Persist normalized user records to PostgreSQL."""

    def __init__(self, connection: Connection) -> None:
        super().__init__(
            connection=connection,
            schema="production_user",
        )

    def write(self, records: Records) -> None:
        """Persist all transformed user resources."""

        self._write_user(records["user"])
        self._write_profile(records["profile"])
        self._write_event(records["event"])
        self._write_follower(records["follower"])
        self._write_following(records["following"])
        self._write_gist(records["gist"])
        self._write_organization(records["organization"])
        self._write_received_event(records["received_event"])
        self._write_starred(records["starred"])
        self._write_repository(records["user_repository"])

    def _write_user(self, records: list[Record]) -> None:
        self._insert_new("user", records)

    def _write_profile(self, records: list[Record]) -> None:
        self._insert_new("profile", records)

    def _write_event(self, records: list[Record]) -> None:
        self._insert_new("event", records)

    def _write_follower(self, records: list[Record]) -> None:
        self._insert_new("follower", records)

    def _write_following(self, records: list[Record]) -> None:
        self._insert_new("following", records)

    def _write_gist(self, records: list[Record]) -> None:
        self._insert_new("gist", records)

    def _write_organization(self, records: list[Record]) -> None:
        self._insert_new("organization", records)

    def _write_received_event(self, records: list[Record]) -> None:
        self._insert_new("received_event", records)

    def _write_starred(self, records: list[Record]) -> None:
        self._insert_new("starred", records)

    def _write_repository(self, records: list[Record]) -> None:
        self._insert_new("repository", records)
