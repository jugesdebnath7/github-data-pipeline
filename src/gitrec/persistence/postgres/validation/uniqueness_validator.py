# src/gitrec/persistence/postgres/validation/uniqueness_validator.py

from __future__ import annotations

from typing import Any

from src.gitrec.persistence.postgres.schema.production_constraints import (
    PRIMARY_KEYS,
    UNIQUE_CONSTRAINTS,
)

Records = dict[str, list[dict[str, Any]]]


class UniquenessValidator:
    """Detect duplicate primary and unique keys within a batch of records."""

    def validate(
        self, 
        records: Records,
        schema: str,
    ) -> list[str]:

        errors: list[str] = []

        for table_name, table_records in records.items():

            table_key = f"{schema}.{table_name}"
            constraints = []

            primary_key = PRIMARY_KEYS.get(table_key)

            if primary_key:
                constraints.append(
                    ("PRIMARY KEY", primary_key)
                )

            for unique_key in UNIQUE_CONSTRAINTS.get(
                table_key, []
            ):
                constraints.append(
                    ("UNIQUE", unique_key)
                )

            for constraint_type, columns in constraints:
                seen: dict[tuple[Any, ...], int] = {}

                for index, record in enumerate(table_records):
                    # Skip incomplete keys. RequiredKeyValidator
                    # Handles missing or NULL primary-key columns.
                    if any(
                        column not in record
                        or record[column] is None
                        for column in columns
                    ):
                        continue

                    key = tuple(
                        record[column] 
                        for column in columns
                    )

                    try:
                        hash(key)
                    except TypeError:
                        errors.append(
                            f"{table_key}, record {index}: "
                            f"Unhashable key {key} for {constraint_type} "
                            f"on columns {columns}."
                        )
                        continue

                    if key in seen:
                        errors.append(
                            f"{table_key}: Duplicate {constraint_type} "
                            f"{columns} at record "
                            f"{seen[key]} and {index}. "
                            f"Duplicate value: {key}."
                        )

                    else:
                        seen[key] = index

        return errors
    