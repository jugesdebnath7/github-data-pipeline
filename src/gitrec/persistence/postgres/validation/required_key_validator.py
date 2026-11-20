# src/gitrec/persistence/postgres/validation/required_key_validator.py

from __future__ import annotations

from typing import Any

from src.gitrec.persistence.postgres.schema.production_constraints import (
    PRIMARY_KEYS,
)


Records = dict[str, list[dict[str, Any]]]


class RequiredKeyValidator:
    """Validate presence and non-null values of primary-key columns."""

    def validate(
        self,
        records: Records,
        schema: str,
    ) -> list[str]:

        errors: list[str] = []

        for table_name, table_records in records.items():
            table_key = f"{schema}.{table_name}"
            primary_keys = PRIMARY_KEYS.get(table_key)

            if not primary_keys:
                errors.append(
                    f"{table_key}: No primary-key configuration found."
                )
                continue

            for index, record in enumerate(table_records):
                for column in primary_keys:
                    if column not in record:
                        errors.append(
                            f"{table_key}, record {index}: "
                            f"Missing primary-key column '{column}'."
                        )

                    elif record[column] is None:
                        errors.append(
                            f"{table_key}, record {index}: "
                            f"Primary-key column '{column}' cannot be NULL."
                        )
                        
        return errors