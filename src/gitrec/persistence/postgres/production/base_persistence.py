# src/gitrec/persistence/postgres/writer/production/production_base.py

from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import MetaData, Table
from sqlalchemy.engine import Connection
from sqlalchemy.dialects.postgresql import insert


Record = dict[str, Any]


class ProductionBasePersistence:
    """Provide common PostgreSQL persistence operations."""

    def __init__(
        self,
        connection: Connection,
        schema: str,
    ) -> None:
        self._connection = connection
        self._schema = schema
        self._metadata = MetaData()
        self._tables: dict[str, Table] = {}

    def _get_table(self, table_name: str) -> Table:
        """Reflect and cache a PostgreSQL production table."""

        if table_name not in self._tables:
            self._tables[table_name] = Table(
                table_name,
                self._metadata,
                schema=self._schema,
                autoload_with=self._connection,
            )

        return self._tables[table_name]

    def _validate_columns(
        self,
        table: Table,
        records: list[Record],
    ) -> None:
        """Validate record columns against the database table."""

        valid_columns = set(table.columns.keys())

        for index, record in enumerate(records):
            unknown_columns = set(record) - valid_columns

            if unknown_columns:
                raise ValueError(
                    f"Record at index {index} contains "
                    f"unknown columns: {unknown_columns}"
                )

    def _insert(
        self,
        table_name: str,
        records: list[Record],
    ) -> None:
        """Bulk insert records into a production table."""

        if not records:
            return

        table = self._get_table(table_name)

        self._validate_columns(table, records)

        statement = insert(table).values(records)

        self._connection.execute(statement)

    def _upsert(
        self,
        table_name: str,
        records: list[Record],
        conflict_columns: Sequence[str],
        update_columns: Sequence[str] | None = None,
    ) -> None:
        """Insert or update records using PostgreSQL conflict handling."""

        if not records:
            return

        table = self._get_table(table_name)

        self._validate_columns(table, records)

        valid_columns = set(table.columns.keys())

        if not set(conflict_columns).issubset(valid_columns):
            raise ValueError("Invalid conflict columns.")

        if update_columns is not None:
            if not set(update_columns).issubset(valid_columns):
                raise ValueError("Invalid update columns.")

        statement = insert(table).values(records)

        if update_columns:
            statement = statement.on_conflict_do_update(
                index_elements=list(conflict_columns),
                set_={
                    column: getattr(statement.excluded, column)
                    for column in update_columns
                },
            )
        else:
            statement = statement.on_conflict_do_nothing(
                index_elements=list(conflict_columns),
            )

        self._connection.execute(statement)
