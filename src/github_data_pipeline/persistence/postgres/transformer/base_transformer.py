
# src/gitrec/persistence/postgres/transformer/base_transformer.py

from __future__ import annotations

from typing import Any

from sqlalchemy import Table

from src.github_data_pipeline.persistence.postgres.schema.production_builder import (
    ProductionSchemaBuilder,
)
from src.github_data_pipeline.persistence.postgres.schema.production_constraints import (
    COLUMN_RENAMES,
)


Record = dict[str, Any]
Records = dict[str, list[Record]]


class BaseTransformer:

    def __init__(
        self,
        schema_builder: ProductionSchemaBuilder,
        staging_schema: str,
        production_schema: str,
    ) -> None:

        self.schema_builder = schema_builder
        self.staging_schema = staging_schema
        self.production_schema = production_schema

    def _transform_table(
        self,
        table_name: str,
        records: list[Record],
    ) -> list[Record]:
        """Map staging records into a production table structure."""

        source_table = self.schema_builder.get_staging_table(
            table_name,
            self.staging_schema,
        )

        target_table = self.schema_builder.get_production_table(
            table_name,
            self.production_schema,
        )

        target_key = f"{self.production_schema}.{table_name}"

        renames = COLUMN_RENAMES.get(target_key, {})

        transformed_records = []

        for record in records:

            production_record = {}

            for source_column in source_table.columns:

                source_name = source_column.name

                target_name = renames.get(
                    source_name,
                    source_name,
                )

                if target_name not in target_table.columns:
                    continue

                if source_name in record:
                    production_record[target_name] = record[source_name]

            transformed_records.append(production_record)

        return transformed_records
