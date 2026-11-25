# src/github_data_pipeline/persistence/postgres/production/production_repository.py

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.github_data_pipeline.persistence.postgres.production.base_persistence import (
    ProductionBasePersistence,
)


Record = dict[str, Any]
ClassifiedRecords = dict[str, list[Record]]
Records = dict[str, ClassifiedRecords]


class ProductionRepositoryPersistence(ProductionBasePersistence):
    """Persist normalized repository records to PostgreSQL."""

    def __init__(self, connection: Connection) -> None:
        super().__init__(
            connection=connection,
            schema="production_repository",
        )

    def write(self, records: Records) -> None:
        """Persist all transformed repository resources."""

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

    def _write_repository(self, records: list[Records]) -> None:
        self._insert_new("repository",  records)

    def _write_branch(self, records: ClassifiedRecords) -> None:
        self._insert_new("branch",  records)

    def _write_commit(self, records: ClassifiedRecords) -> None:
        self._insert_new("commit",  records)

    def _write_contributor(self, records: ClassifiedRecords) -> None:
        self._insert_new("contributor",  records)

    def _write_fork(self, records: ClassifiedRecords) -> None:
        self._insert_new("fork",  records)

    def _write_issue(self, records: ClassifiedRecords) -> None:
        self._insert_new("issue",  records)

    def _write_language(self, records: ClassifiedRecords) -> None:
        self._insert_new("language",  records)

    def _write_pull_request(self, records: ClassifiedRecords) -> None:
        self._insert_new("pull_request",  records)

    def _write_readme(self, records: ClassifiedRecords) -> None:
        self._insert_new("readme",  records)

    def _write_release(self, records: ClassifiedRecords) -> None:
        self._insert_new("release",  records)

    def _write_tag(self, records: ClassifiedRecords) -> None:
        self._insert_new("tag",  records)

    def _write_topic(self, records: ClassifiedRecords) -> None:
        self._insert_new("topic",  records)


