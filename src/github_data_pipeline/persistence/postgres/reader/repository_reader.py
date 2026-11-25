# src/gitrec/persistence/postgres/reader/repository.py

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.github_data_pipeline.persistence.postgres.reader.base_reader import BaseReader


class RepositoryReader(BaseReader):
    """Fetch repository-related records from staging tables."""

    def __init__(
        self,
        connection: Connection,
    ) -> None:
        super().__init__(
        connection=connection,
        schema="staging_repository",
        )

    def read(self) -> dict[str, list[dict[str, Any]]]:
        """Read all repository-related staging records."""

        return {
            "repository": self._read_repository(),
            "branch": self._read_branch(),
            "commit": self._read_commit(),
            "contributor": self._read_contributor(),
            "fork": self._read_fork(),
            "issue": self._read_issue(),
            "language": self._read_language(),
            "pull_request": self._read_pull_request(),
            "readme": self._read_readme(),
            "release": self._read_release(),
            "tag": self._read_tag(),
            "topic": self._read_topic(),
        }

    def _read_repository(self) -> list[dict[str, Any]]:
        return self._read("repository")

    def _read_branch(self) -> list[dict[str, Any]]:
        return self._read("branch")

    def _read_commit(self) -> list[dict[str, Any]]:
        return self._read("commit")

    def _read_contributor(self) -> list[dict[str, Any]]:
        return self._read("contributor")

    def _read_fork(self) -> list[dict[str, Any]]:
        return self._read("fork")

    def _read_issue(self) -> list[dict[str, Any]]:
        return self._read("issue")

    def _read_language(self) -> list[dict[str, Any]]:
        return self._read("language")

    def _read_pull_request(self) -> list[dict[str, Any]]:
        return self._read("pull_request")

    def _read_readme(self) -> list[dict[str, Any]]:
        return self._read("readme")

    def _read_release(self) -> list[dict[str, Any]]:
        return self._read("release")

    def _read_tag(self) -> list[dict[str, Any]]:
        return self._read("tag")

    def _read_topic(self) -> list[dict[str, Any]]:
        return self._read("topic")
