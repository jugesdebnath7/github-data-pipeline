# src/github_data_pipeline/persistence/staging/service.py

from __future__ import annotations

from src.github_data_pipeline.domain.entity.repository.repository_item import RepositoryItem
from src.github_data_pipeline.domain.entity.user.user_item import UserItem
from src.github_data_pipeline.persistence.connection import PostgresConnection
from src.github_data_pipeline.persistence.mapper.repository import RepositoryMapper
from src.github_data_pipeline.persistence.mapper.user import UserMapper
from src.github_data_pipeline.persistence.validation.schema_validator import (
    SchemaValidator,
)
from src.github_data_pipeline.persistence.staging.staging_repository import RepositoryWriter
from src.github_data_pipeline.persistence.staging.staging_user import UserWriter


class StagingPersistence:
    """Coordinate mapping, validation, and transactional persistence."""

    def __init__(
        self,
        connection: PostgresConnection,
    ) -> None:
        self._connection = connection

        self._repository_mapper = RepositoryMapper()
        self._user_mapper = UserMapper()
        self._schema_validator = SchemaValidator(
            connection.engine,
            schema_prefix="staging",
        )

    def persist(
        self,
        repositories: list[RepositoryItem],
        users: list[UserItem],
    ) -> None:
        """Validate and persist repository and user aggregates."""

        # Step 1: Map domain entities.
        repository_records = self._repository_mapper.flatten(repositories)
        user_records = self._user_mapper.flatten(users)

        # Step 2: Validate against PostgreSQL staging schemas.
        self._schema_validator.validate_all(
            repository_records=repository_records,
            user_records=user_records,
        )

        # Step 3: Persist both resources in one transaction.
        with self._connection.engine.begin() as connection:
            RepositoryWriter(connection).write(repository_records)
            UserWriter(connection).write(user_records)
