# src/github_data_pipeline/persistence/user_writer.py

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.github_data_pipeline.persistence.staging.staging_base import StagingBaseWriter


Record = dict[str, Any]
Records = dict[str, list[Record]]


class UserWriter(StagingBaseWriter):
    """Persist user-related records to PostgreSQL."""

    def __init__(self, connection: Connection) -> None:
        super().__init__(
            connection=connection,
            schema="staging_user",
        )

    def write(self, records: Records) -> None:
        """Persist all user resources."""

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
        self._insert("user", records)

    def _write_profile(self, records: list[Record]) -> None:
        self._insert("profile", records)

    def _write_event(self, records: list[Record]) -> None:
        self._insert("event", records)

    def _write_follower(self, records: list[Record]) -> None:
        self._insert("follower", records)

    def _write_following(self, records: list[Record]) -> None:
        self._insert("following", records)

    def _write_gist(self, records: list[Record]) -> None:
        self._insert("gist", records)

    def _write_organization(self, records: list[Record]) -> None:
        self._insert("organization", records)

    def _write_received_event(self, records: list[Record]) -> None:
        self._insert("received_event", records)

    def _write_starred(self, records: list[Record]) -> None:
        self._insert("starred", records)

    def _write_repository(self, records: list[Record]) -> None:
        self._insert("repository", records)
