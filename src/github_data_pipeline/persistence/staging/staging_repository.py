# src/github_data_pipeline/persistence/repository_writer.py

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.github_data_pipeline.persistence.staging.staging_base import StagingBaseWriter


Record = dict[str, Any]
Records = dict[str, list[Record]]


class RepositoryWriter(StagingBaseWriter):
    """Persist repository-related records to PostgreSQL."""

    def __init__(self, connection: Connection) -> None:
        super().__init__(
            connection=connection,
            schema="staging_repository",
        )

    def write(self, records: Records) -> None:
        """Persist all repository resources."""

        self._write_repository(records["repository"])
        self._write_branch(records["branch"])
        self._write_commit(records["commit"])
        self._write_contributor(records["contributor"])
        self._write_fork(records["fork"])
        self._write_issue(records["issue"])
        self._write_language(records["language"])
        self._write_pull_request(records["pull_request"])
        self._write_readme(records["readme"])
        self._write_release(records["release"])
        self._write_tag(records["tag"])
        self._write_topic(records["topic"])

    def _write_repository(self, records: list[Record]) -> None:
        self._insert("repository", records)

    def _write_branch(self, records: list[Record]) -> None:
        self._insert("branch", records)

    def _write_commit(self, records: list[Record]) -> None:
        self._insert("commit", records)

    def _write_contributor(self, records: list[Record]) -> None:
        self._insert("contributor", records)

    def _write_fork(self, records: list[Record]) -> None:
        self._insert("fork", records)

    def _write_issue(self, records: list[Record]) -> None:
        self._insert("issue", records)

    def _write_language(self, records: list[Record]) -> None:
        self._insert("language", records)

    def _write_pull_request(self, records: list[Record]) -> None:
        self._insert("pull_request", records)

    def _write_readme(self, records: list[Record]) -> None:
        self._insert("readme", records)

    def _write_release(self, records: list[Record]) -> None:
        self._insert("release", records)

    def _write_tag(self, records: list[Record]) -> None:
        self._insert("tag", records)

    def _write_topic(self, records: list[Record]) -> None:
        self._insert("topic", records)
