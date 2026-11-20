# src/gitrec/persistence/postgres/validation/production_validator.py

from __future__ import annotations

from typing import Any

from src.gitrec.persistence.postgres.validation.required_key_validator import (
    RequiredKeyValidator,
)
from src.gitrec.persistence.postgres.validation.uniqueness_validator import (
    UniquenessValidator,
)


Records = dict[str, list[dict[str, Any]]]


class ProductionValidationError(ValueError):
    """Raised when production records fail validation."""

    def __init__(
        self,
        errors: list[str],
    ) -> None:
        super().__init__(
            "Production records failed validation:\n"
            + "\n".join(f"- {error}" for error in errors)
        )
        self.errors = errors

class ProductionValidator:        
    """Cordinate validation of production records before insertion into the database."""

    def __init__(self) -> None:
        self.required_key_validator = RequiredKeyValidator()
        self.uniqueness_validator = UniquenessValidator()

    def validate(
        self,
        records: Records,
        schema: str,
    ) -> None:
        """Validate production records."""

        errors: list[str] = []

        errors.extend(
            self.required_key_validator.validate(
                records=records,
                schema=schema,
            )
        )

        errors.extend(
            self.uniqueness_validator.validate(
                records=records,
                schema=schema,
            )
        )

        if errors:
            raise ProductionValidationError(errors=errors)

    def validate_all(
        self,
        repository_records: Records,
        user_records: Records,
    ) -> None:
        """Validate all transformed production records."""

        self.validate(
            repository_records,
            "production_repository",
        )

        self.validate(
            user_records,
            "production_user",
        )