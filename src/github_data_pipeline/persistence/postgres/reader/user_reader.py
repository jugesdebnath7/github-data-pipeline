# src/github_data_pipeline/persistence/postgres/reader/user_reader.py

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.github_data_pipeline.persistence.postgres.reader.base_reader import BaseReader


class UserReader(BaseReader):
    """Fetch all user-related records from staging tables"""
    def __init__(
        self,
        connection: Connection
    ) -> None: 
        super().__init__(
        connection=connection,
        schema="staging_user",
        )

    def read(self) -> dict[str, list[dict[str, Any]]]:
        """Read all user-related staging records."""

        return {
            "user": self._read_user(),
            "profile": self._read_profile(),
            "event": self._read_event(),
            "follower": self._read_follower(),
            "following": self._read_following(),
            "gist": self._read_gist(),
            "organization": self._read_organization(),
            "received_event": self._read_received_event(),
            "starred": self._read_starred(),
            "repository": self._read_repository()
        }   

    def _read_user(self) -> list[dict[str, Any]]:
        return self._read("user")

    def _read_profile(self) -> list[dict[str, Any]]:
        return self._read("profile")

    def _read_event(self) -> list[dict[str, Any]]:
        return self._read("event")

    def _read_follower(self) -> list[dict[str, Any]]:
        return self._read("follower")

    def _read_following(self) -> list[dict[str, Any]]:
        return self._read("following")

    def _read_gist(self) -> list[dict[str, Any]]:
        return self._read("gist")

    def _read_organization(self) -> list[dict[str, Any]]:
        return self._read("organization")

    def _read_received_event(self) -> list[dict[str, Any]]:
        return self._read("received_event")

    def _read_starred(self) -> list[dict[str, Any]]:
        return self._read("starred")

    def _read_repository(self) -> list[dict[str, Any]]:
        return self._read("repository")