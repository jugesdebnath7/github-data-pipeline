# src/gitrec/persistence/postgres/production/production_repository.py

from __future__ import annotations

from typing import Any

from sqlalchemy.engine import Connection

from src.gitrec.persistence.postgres.production.base_persistence import (
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

    @staticmethod
    def _flatten_records(records: ClassifiedRecords) -> list[Record]:
        """Flatten classified records into a single list."""

        return [
            record
            for category_records in records.values()
            for record in category_records
        ]

    def _write_repository(self, records: ClassifiedRecords) -> None:
        self._insert("repository", self._flatten_records(records))

    def _write_branch(self, records: ClassifiedRecords) -> None:
        self._insert("branch", self._flatten_records(records))

    def _write_commit(self, records: ClassifiedRecords) -> None:
        self._insert("commit", self._flatten_records(records))

    def _write_contributor(self, records: ClassifiedRecords) -> None:
        self._insert("contributor", self._flatten_records(records))

    def _write_fork(self, records: ClassifiedRecords) -> None:
        self._insert("fork", self._flatten_records(records))

    def _write_issue(self, records: ClassifiedRecords) -> None:
        self._insert("issue", self._flatten_records(records))

    def _write_language(self, records: ClassifiedRecords) -> None:
        self._insert("language", self._flatten_records(records))

    def _write_pull_request(self, records: ClassifiedRecords) -> None:
        self._insert("pull_request", self._flatten_records(records))

    def _write_readme(self, records: ClassifiedRecords) -> None:
        self._insert("readme", self._flatten_records(records))

    def _write_release(self, records: ClassifiedRecords) -> None:
        self._insert("release", self._flatten_records(records))

    def _write_tag(self, records: ClassifiedRecords) -> None:
        self._insert("tag", self._flatten_records(records))

    def _write_topic(self, records: ClassifiedRecords) -> None:
        self._insert("topic", self._flatten_records(records))


