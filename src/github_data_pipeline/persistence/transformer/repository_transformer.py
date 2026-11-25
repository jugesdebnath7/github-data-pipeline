
# src/github_data_pipeline/persistence/transformer/repository_transformer.py

from __future__ import annotations

from typing import Any

from src.github_data_pipeline.persistence.transformer.base_transformer import (
    BaseTransformer,
    Records,
)

from src.github_data_pipeline.persistence.schema.production_builder import (
    ProductionSchemaBuilder,
)


class RepositoryTransformer(BaseTransformer):
    """Transform staging repository resources into production records."""

    RESOURCES = (
        "repository",
        "branch",
        "commit",
        "contributor",
        "fork",
        "issue",
        "language",
        "pull_request",
        "readme",
        "release",
        "tag",
        "topic",
    )

    def __init__(
        self,
        schema_builder: ProductionSchemaBuilder,
    ) -> None:

        super().__init__(
            schema_builder=schema_builder,
            staging_schema="staging_repository",
            production_schema="production_repository",
        )

    def transform(
        self,
        records: Records,
    ) -> Records:
        """Transform all repository resources."""

        return {
            resource: self._transform_table(
                resource,
                records.get(resource, []),
            )
            for resource in self.RESOURCES
        }
