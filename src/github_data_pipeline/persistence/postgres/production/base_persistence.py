# src/gitrec/persistence/postgres/writer/production/base_persistence.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from sqlalchemy import MetaData, Table, insert
from sqlalchemy.engine import Connection


Record = dict[str, Any]

ClassifiedRecords = dict[str, list[Record]]


@dataclass(frozen=True)
class PersistenceResult:
    """Result of inserting classified production records."""

    attempted: int
    inserted: int
    conflict_skipped: int

    @property
    def skipped(self) -> int:
        return self.attempted - self.inserted


class ProductionBasePersistence:
    """
    Provide common PostgreSQL production persistence operations.

    Persistence policy:
        new:
            Eligible for insertion.

        existing:
            Never inserted.

        duplicate_incoming:
            Never inserted.

    Database-level unique conflicts are ignored as a
    final safeguard.

    Transaction ownership belongs to the caller.
    """

    REQUIRED_CATEGORIES = (
        "new",
        "existing",
        "duplicate_incoming",
    )

    def __init__(
        self,
        connection: Connection,
        schema: str,
        batch_size: int = 500,
    ) -> None:

        if not schema:
            raise ValueError("Schema name cannot be empty.")

        if batch_size < 1:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self._connection = connection
        self._schema = schema
        self._batch_size = batch_size

        self._metadata = MetaData()
        self._tables: dict[str, Table] = {}

    # =================================================
    # 1. REFLECT PRODUCTION TABLE
    # =================================================

    def _get_table(self, table_name: str) -> Table:
        """Reflect and cache a production table."""

        if not table_name:
            raise ValueError("Table name cannot be empty.")

        if table_name not in self._tables:

            table = Table(
                table_name,
                self._metadata,
                schema=self._schema,
                autoload_with=self._connection,
            )

            if not table.primary_key.columns:
                raise ValueError(
                    f"Production table has no primary key: "
                    f"{self._schema}.{table_name}"
                )

            self._tables[table_name] = table

        return self._tables[table_name]

    # =================================================
    # 2. VALIDATE RECORD STRUCTURE
    # =================================================

    def _validate_records(
        self,
        table: Table,
        records: list[Record],
    ) -> None:
        """Validate record structures and database columns."""

        valid_columns = set(table.columns.keys())

        primary_key_columns = {
            column.name
            for column in table.primary_key.columns
        }

        for index, record in enumerate(records):

            if not isinstance(record, Mapping):
                raise ValueError(
                    f"Record at index {index} must be a dictionary."
                )

            if not record:
                raise ValueError(
                    f"Record at index {index} is empty."
                )

            if not all(
                isinstance(column, str)
                for column in record
            ):
                raise ValueError(
                    f"Record at index {index} contains "
                    f"non-string column names."
                )

            unknown_columns = set(record) - valid_columns

            if unknown_columns:
                raise ValueError(
                    f"{self._schema}.{table.name}, "
                    f"record {index}: Unknown columns: "
                    f"{sorted(unknown_columns)}"
                )

            missing_pk = primary_key_columns - set(record)

            if missing_pk:
                raise ValueError(
                    f"{self._schema}.{table.name}, "
                    f"record {index}: Missing primary-key "
                    f"columns: {sorted(missing_pk)}"
                )

            null_pk = [
                column
                for column in primary_key_columns
                if record[column] is None
            ]

            if null_pk:
                raise ValueError(
                    f"{self._schema}.{table.name}, "
                    f"record {index}: NULL primary-key "
                    f"values: {sorted(null_pk)}"
                )

    # =================================================
    # 3. VALIDATE INCOMING CLASSIFICATION
    # =================================================

    def _validate_classification(
        self,
        classified_records: ClassifiedRecords,
        table_name: str,
    ) -> None:
        """Validate the idempotency classification contract."""

        if not isinstance(classified_records, Mapping):
            raise ValueError(
                f"{table_name}: Expected classified records."
            )

        missing_categories = (
            set(self.REQUIRED_CATEGORIES)
            - set(classified_records)
        )

        if missing_categories:
            raise ValueError(
                f"{table_name}: Missing classification categories: "
                f"{sorted(missing_categories)}"
            )

        for category in self.REQUIRED_CATEGORIES:

            category_records = classified_records[category]

            if not isinstance(category_records, list):
                raise ValueError(
                    f"{table_name}: Category '{category}' "
                    f"must contain a list."
                )

    # =================================================
    # 4. DETECT DUPLICATE PRIMARY KEYS
    # =================================================

    def _validate_unique_batch_keys(
        self,
        table: Table,
        records: list[Record],
    ) -> None:
        """Reject duplicate primary keys in new records."""

        primary_key_columns = [
            column.name
            for column in table.primary_key.columns
        ]

        seen: set[tuple[Any, ...]] = set()

        for index, record in enumerate(records):

            key = tuple(
                record[column]
                for column in primary_key_columns
            )

            try:
                if key in seen:
                    raise ValueError(
                        f"{self._schema}.{table.name}: "
                        f"Duplicate primary key in new records "
                        f"at index {index}: {key}"
                    )

                seen.add(key)

            except TypeError as exc:
                raise ValueError(
                    f"{self._schema}.{table.name}: "
                    f"Unhashable primary-key values: {key}"
                ) from exc

    # =================================================
    # 5. INSERT NEW RECORDS
    # =================================================

    def _insert_new(
        self,
        table_name: str,
        classified_records: ClassifiedRecords,
    ) -> PersistenceResult:
        """
        Insert only records classified as new.

        Existing and duplicate incoming records are ignored.

        PostgreSQL ON CONFLICT DO NOTHING provides protection
        against concurrent ingestion and unique-key conflicts.
        """

        self._validate_classification(
            classified_records,
            table_name,
        )

        new_records = classified_records["new"]

        if not new_records:
            return PersistenceResult(
                attempted=0,
                inserted=0,
                conflict_skipped=0,
            )

        table = self._get_table(table_name)

        self._validate_records(
            table,
            new_records,
        )

        self._validate_unique_batch_keys(
            table,
            new_records,
        )

        primary_key_columns = list(
            table.primary_key.columns
        )

        inserted_count = 0

        # Group records by their supplied columns.
        # This supports optional columns being omitted
        # from individual records.

        groups: dict[
            frozenset[str],
            list[Record],
        ] = {}

        for record in new_records:

            column_signature = frozenset(record.keys())

            groups.setdefault(
                column_signature,
                [],
            ).append(dict(record))

        # Bulk insert each group in controlled batches.

        for group_records in groups.values():

            for start in range(
                0,
                len(group_records),
                self._batch_size,
            ):

                batch = group_records[
                    start:start + self._batch_size
                ]

                statement = (
                    insert(table)
                    .values(batch)
                    .on_conflict_do_nothing()
                    .returning(*primary_key_columns)
                )

                inserted_rows = self._connection.execute(
                    statement
                ).all()

                inserted_count += len(inserted_rows)

        attempted_count = len(new_records)

        return PersistenceResult(
            attempted=attempted_count,
            inserted=inserted_count,
            conflict_skipped=(
                attempted_count - inserted_count
            ),
        )
