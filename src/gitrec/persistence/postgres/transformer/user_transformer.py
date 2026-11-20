# src/gitrec/persistence/postgres/transformer/user_transformer.py

from __future__ import annotations

from typing import Any

from src.gitrec.persistence.postgres.transformer.base_transformer import (
    BaseTransformer,
    Records,
)
from src.gitrec.persistence.postgres.schema.production_builder import (
    ProductionSchemaBuilder,
)


class UserTransformer(BaseTransformer):
    """Transforming staging user schema data into production sechema data"""

    RESOURCES = (
        "event",
        "follower",
        "following",
        "gist",
        "organization",
        "profile",
        "received_event",
        "starred",
        "user",
        "repository",
    )

    def __init__(
        self,
        schema_builder: ProductionSchemaBuilder,
    ) -> None:

        super().__init__(
            schema_builder=schema_builder,
            staging_schema="staging_user",
            production_schema="production_user",
        )

    def transform(
        self,
        staging_records: Records,
    ) -> Records:
        """Transform all user resources."""

        return {
            resource: self._transform_table(
                resource,
                staging_records.get(resource, []),
            )
            for resource in self.RESOURCES
        }