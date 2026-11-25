# src/github_data_pipeline/persistence/validation/production_validator.py

from __future__ import annotations

from typing import Any

from src.github_data_pipeline.persistence.validation.required_key_validator import (
    RequiredKeyValidator,
)


Records = dict[str, list[dict[str, Any]]]


class ProductionValidationError(ValueError):
    """Raised when production records fail structural validation."""

    def __init__(
        self,
        errors: list[str],
    ) -> None:

        self.errors = errors

        super().__init__(
            "Production records failed validation:\n"
            + "\n".join(
                f"- {error}"
                for error in errors
            )
        )


class ProductionValidator:
    """
    Coordinate structural validation of production records.

    Validates incoming records before idempotency checks
    and database persistence.
    """

    def __init__(self) -> None:

        self.required_key_validator = RequiredKeyValidator()

    def _collect_errors(
        self,
        records: Records,
        schema: str,
    ) -> list[str]:

        return self.required_key_validator.validate(
            records=records,
            schema=schema,
        )

    def validate(
        self,
        records: Records,
        schema: str,
    ) -> None:
        """Validate records belonging to one production schema."""

        errors = self._collect_errors(
            records=records,
            schema=schema,
        )

        if errors:
            raise ProductionValidationError(errors)

    def validate_all(
        self,
        repository_records: Records,
        user_records: Records,
    ) -> None:
        """Validate all incoming production records."""

        errors: list[str] = []

        schemas = [
            (
                "production_repository",
                repository_records,
            ),
            (
                "production_user",
                user_records,
            ),
        ]

        for schema, records in schemas:

            errors.extend(
                self._collect_errors(
                    records=records,
                    schema=schema,
                )
            )

        if errors:
            raise ProductionValidationError(errors)
