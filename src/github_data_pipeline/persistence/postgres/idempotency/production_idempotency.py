# src/github_data_pipeline/persistence/postgres/idempotency/production_idempotency.py

from __future__ import annotations

from typing import Any

from sqlalchemy import MetaData, Table, select, tuple_
from sqlalchemy.engine import Connection

from src.github_data_pipeline.persistence.postgres.schema.production_constraints import (
    PRIMARY_KEYS,
)


Record = dict[str, Any]

Records = dict[str, list[Record]]

ClassifiedTable = dict[str, list[Record]]

ClassifiedRecords = dict[str, ClassifiedTable]


class ProductionIdempotency:
    """
    Classify incoming records against actual production data.

    Classification:
        new:
            Unique incoming records whose primary keys do not
            exist in the production table.

        existing:
            Unique incoming records whose primary keys already
            exist in the production table.

        duplicate_incoming:
            Subsequent occurrences of duplicate primary keys
            within the incoming batch.

    Duplicate policy:
        First occurrence wins.

    This module performs database reads only.
    """

    def __init__(
        self,
        connection: Connection,
        batch_size: int = 500,
    ) -> None:

        if batch_size < 1:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self.connection = connection
        self.batch_size = batch_size

        self.metadata = MetaData()
        self.tables: dict[str, Table] = {}

    # =================================================
    # 1. REFLECT PRODUCTION TABLE
    # =================================================

    def _get_table(
        self,
        schema: str,
        table_name: str,
    ) -> Table:

        key = f"{schema}.{table_name}"

        if key not in self.tables:

            self.tables[key] = Table(
                table_name,
                self.metadata,
                schema=schema,
                autoload_with=self.connection,
            )

        return self.tables[key]

    # =================================================
    # 2. VALIDATE INCOMING RECORDS
    # =================================================

    def _validate_records(
        self,
        records: list[Record],
        columns: list[str],
        table_key: str,
    ) -> None:

        for index, record in enumerate(records):

            if not isinstance(record, dict):
                raise ValueError(
                    f"{table_key}: Record {index} "
                    "must be a dictionary."
                )

            missing = [
                column
                for column in columns
                if column not in record
            ]

            if missing:
                raise ValueError(
                    f"{table_key}: Record {index} "
                    f"is missing primary-key columns: {missing}"
                )

            null_columns = [
                column
                for column in columns
                if record[column] is None
            ]

            if null_columns:
                raise ValueError(
                    f"{table_key}: Record {index} "
                    f"has NULL primary-key values: {null_columns}"
                )

    # =================================================
    # 3. DEDUPLICATE INCOMING BATCH
    # =================================================

    def _deduplicate_incoming(
        self,
        records: list[Record],
        columns: list[str],
    ) -> tuple[list[Record], list[Record]]:

        seen: set[tuple[Any, ...]] = set()

        unique_records: list[Record] = []

        duplicate_records: list[Record] = []

        for record in records:

            key = tuple(
                record[column]
                for column in columns
            )

            try:
                already_seen = key in seen
                seen.add(key)

            except TypeError as exc:
                raise ValueError(
                    f"Unhashable primary-key values: {key}"
                ) from exc

            if already_seen:
                duplicate_records.append(record)

            else:
                unique_records.append(record)

        return unique_records, duplicate_records

    # =================================================
    # 4. EXTRACT PRIMARY KEYS
    # =================================================

    @staticmethod
    def _extract_keys(
        records: list[Record],
        columns: list[str],
    ) -> list[tuple[Any, ...]]:

        return [
            tuple(record[column] for column in columns)
            for record in records
        ]

    # =================================================
    # 5. FIND EXISTING PRODUCTION KEYS
    # =================================================

    def _find_existing_keys(
        self,
        table: Table,
        columns: list[str],
        keys: list[tuple[Any, ...]],
    ) -> set[tuple[Any, ...]]:

        if not keys:
            return set()

        existing_keys: set[tuple[Any, ...]] = set()

        key_columns = [
            table.c[column]
            for column in columns
        ]

        for start in range(
            0,
            len(keys),
            self.batch_size,
        ):

            chunk = keys[
                start:start + self.batch_size
            ]

            if len(columns) == 1:

                statement = select(
                    key_columns[0]
                ).where(
                    key_columns[0].in_(
                        [key[0] for key in chunk]
                    )
                )

            else:

                statement = select(
                    *key_columns
                ).where(
                    tuple_(*key_columns).in_(chunk)
                )

            rows = self.connection.execute(
                statement
            ).all()

            existing_keys.update(
                tuple(row)
                for row in rows
            )

        return existing_keys

    # =================================================
    # 6. CLASSIFY ONE TABLE
    # =================================================

    def classify_table(
        self,
        records: list[Record],
        schema: str,
        table_name: str,
    ) -> ClassifiedTable:

        table_key = f"{schema}.{table_name}"

        primary_keys = PRIMARY_KEYS.get(table_key)

        if not primary_keys:
            raise ValueError(
                f"Missing primary-key configuration: {table_key}"
            )

        if not records:
            return {
                "new": [],
                "existing": [],
                "duplicate_incoming": [],
            }

        # Validate incoming records before classification.
        self._validate_records(
            records=records,
            columns=primary_keys,
            table_key=table_key,
        )

        # Stage 1: Remove duplicates within incoming batch.
        unique_records, duplicate_records = (
            self._deduplicate_incoming(
                records=records,
                columns=primary_keys,
            )
        )

        # Stage 2: Compare unique records against production.
        table = self._get_table(
            schema=schema,
            table_name=table_name,
        )

        missing_columns = (
            set(primary_keys) - set(table.columns.keys())
        )

        if missing_columns:
            raise ValueError(
                f"{table_key}: Production table is missing "
                f"primary-key columns: {sorted(missing_columns)}"
            )

        keys = self._extract_keys(
            records=unique_records,
            columns=primary_keys,
        )

        existing_keys = self._find_existing_keys(
            table=table,
            columns=primary_keys,
            keys=keys,
        )

        new_records: list[Record] = []
        existing_records: list[Record] = []

        for record, key in zip(unique_records, keys):

            if key in existing_keys:
                existing_records.append(record)

            else:
                new_records.append(record)

        return {
            "new": new_records,
            "existing": existing_records,
            "duplicate_incoming": duplicate_records,
        }

    # =================================================
    # 7. CLASSIFY ONE SCHEMA
    # =================================================

    def classify(
        self,
        records: Records,
        schema: str,
    ) -> ClassifiedRecords:

        result: ClassifiedRecords = {}

        for table_name, table_records in records.items():

            result[table_name] = self.classify_table(
                records=table_records,
                schema=schema,
                table_name=table_name,
            )

        return result

    # =================================================
    # 8. CLASSIFY ALL PRODUCTION SCHEMAS
    # =================================================

    def classify_all(
        self,
        repository_records: Records,
        user_records: Records,
    ) -> dict[str, ClassifiedRecords]:

        return {
            "production_repository": self.classify(
                records=repository_records,
                schema="production_repository",
            ),
            "production_user": self.classify(
                records=user_records,
                schema="production_user",
            ),
        }
