# src/gitrec/persistence/postgres/production/production_persistence.py

from __future__ import annotations

from src.gitrec.persistence.postgres.connection import PostgresConnection

from src.gitrec.persistence.postgres.reader.repository_reader import RepositoryReader
from src.gitrec.persistence.postgres.reader.user_reader import UserReader

from src.gitrec.persistence.postgres.schema.production_builder import (
    ProductionSchemaBuilder,
)
from src.gitrec.persistence.postgres.transformer.repository_transformer import (
    RepositoryTransformer,
)
from src.gitrec.persistence.postgres.transformer.user_transformer import (
    UserTransformer,
)
from src.gitrec.persistence.postgres.validation.production_validator import (
    ProductionValidator,
)
from src.gitrec.persistence.postgres.production.repository_persistence import (
    ProductionRepositoryPersistence,
)
from src.gitrec.persistence.postgres.production.user_persistence import (
    ProductionUserPersistence,
)


class ProductionPersistence:
    """Coordinate staging-to-production persistence."""

    def __init__(self, connection: PostgresConnection) -> None:
        self._connection = connection

    
    def persist(self) -> None:
        """Extract, transform and validate production records."""

        with self._connection.engine.begin() as connection:

            # 1. Extract
            repository_records = RepositoryReader(connection).read()
            user_records = UserReader(connection).read()

            # 2. Build production metadata
            builder = ProductionSchemaBuilder(connection)
            builder.build()

            # 3. Transform
            repository_transformer = RepositoryTransformer(builder)

            repository_transformed = repository_transformer.transform(
                repository_records
            )

            user_transformer = UserTransformer(builder)

            user_transformed = user_transformer.transform(
                user_records
            )

            # 4. Validate
            validator = ProductionValidator()

            validator.validate_all(
                repository_records=repository_transformed,
                user_records=user_transformed,
            )

            # 5. Production writes intentionally disabled.
