# src/github_data_pipeline/persistence/postgres/reader/base_reader.py

from __future__ import annotations

from sqlalchemy import MetaData, Table, select
from sqlalchemy.engine import Connection
from typing import Any


class BaseReader: 
    """Base class for reading records from PostgreSQL tables."""
    def __init__(
        self, 
        connection: Connection,
        schema: str,
    ) -> None: 
        self._connection = connection
        self._schema = schema
        self._meta_data = MetaData()
        self._tables: dict[str, Table] = {}

    def _get_table(self, table_name: str) -> Table: 
        """Reflect and cache a PostgreSQL table."""  

        if table_name not in self._tables:
            self._tables[table_name] = Table(
                table_name,
                self._meta_data,
                schema=self._schema,
                autoload_with=self._connection,
            )

        return self._tables[table_name] 

    def _read(
        self,
        table_name: str,
    ) -> list[dict[str, Any]]:
        """Read all records from a PostgreSQL table."""

        table = self._get_table(table_name)
        statement = select(table)
        result = self._connection.execute(statement)
        records = [
            dict(row) for row in result.mappings().all()
        ]

        return records