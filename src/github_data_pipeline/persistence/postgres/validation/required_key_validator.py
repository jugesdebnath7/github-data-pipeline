# src/github_data_pipeline/persistence/postgres/validation/required_key_validator.py

from __future__ import annotations

from typing import Any

from src.github_data_pipeline.persistence.postgres.schema.production_constraints import (
    PRIMARY_KEYS,
)


Records = dict[str, list[dict[str, Any]]]


class RequiredKeyValidator:
    """
    Validates presence and non-null values of production primary keys in records.

    Primary-key definations are obtained from the production constraints module.

    Does not perform: 
        - Duplicate detection
        - Database existence checks
        - Foreign key validation
        - Data type validation
    """

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
                    f"{table_key}: Missing or empty "
                    f"primary-key configuration."
                )
                continue

            for index, record in enumerate(table_records):

                if not isinstance(record, dict):
                    errors.append(
                        f"{table_key}, record {index}: "
                        f"Expected dictionary, received "
                        f"{type(record).__name__}."
                    )
                    continue

                for column in primary_keys:

                    if column not in record:
                        errors.append(
                            f"{table_key}, record {index}: "
                            f"Missing primary-key column '{column}'."
                        )

                    elif record[column] is None:
                        errors.append(
                            f"{table_key}, record {index}: "
                            f"Primary-key column '{column}' "
                            f"cannot be NULL."
                        )

        return errors