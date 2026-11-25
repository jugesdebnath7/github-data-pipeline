# src/gitrec/persistence/postgres/production/production_persistence.py

from __future__ import annotations

from src.github_data_pipeline.persistence.postgres.connection import PostgresConnection

from src.github_data_pipeline.persistence.postgres.reader.repository_reader import (
    RepositoryReader,
)
from src.github_data_pipeline.persistence.postgres.reader.user_reader import (
    UserReader,
)

from src.github_data_pipeline.persistence.postgres.schema.production_builder import (
    ProductionSchemaBuilder,
)

from src.github_data_pipeline.persistence.postgres.transformer.repository_transformer import (
    RepositoryTransformer,
)
from src.github_data_pipeline.persistence.postgres.transformer.user_transformer import (
    UserTransformer,
)

from src.github_data_pipeline.persistence.postgres.validation.production_validator import (
    ProductionValidator,
)

from src.github_data_pipeline.persistence.postgres.idempotency.production_idempotency import (
    ProductionIdempotency,
)

from src.github_data_pipeline.persistence.postgres.production.repository_persistence import (
    ProductionRepositoryPersistence,
)
from src.github_data_pipeline.persistence.postgres.production.user_persistence import (
    ProductionUserPersistence,
)


class ProductionPersistence:
    """Coordinate staging-to-production persistence."""

    def __init__(
        self,
        connection: PostgresConnection,
    ) -> None:

        self._connection = connection

    def persist(self) -> None:
        """Extract, transform, validate and classify production records."""

        with self._connection.engine.begin() as connection:

            # =========================================
            # 1. EXTRACT
            # =========================================

            repository_records = RepositoryReader(
                connection
            ).read()

            user_records = UserReader(
                connection
            ).read()

            # =========================================
            # 2. BUILD PRODUCTION METADATA
            # =========================================

            builder = ProductionSchemaBuilder(
                connection
            )

            builder.build()

            # =========================================
            # 3. TRANSFORM
            # =========================================

            repository_transformer = RepositoryTransformer(
                builder
            )

            repository_transformed = (
                repository_transformer.transform(
                    repository_records
                )
            )

            user_transformer = UserTransformer(
                builder
            )

            user_transformed = (
                user_transformer.transform(
                    user_records
                )
            )

            # =========================================
            # 4. VALIDATE
            # =========================================

            validator = ProductionValidator()

            validator.validate_all(
                repository_records=repository_transformed,
                user_records=user_transformed,
            )

            # =========================================
            # 5. IDEMPOTENCY CHECK
            # =========================================

            idempotency = ProductionIdempotency(
                connection=connection,
            )

            classified_records = idempotency.classify_all(
                repository_records=repository_transformed,
                user_records=user_transformed,
            )

            repository_classified = (
                classified_records["production_repository"]
            )

            user_classified = (
                classified_records["production_user"]
            )

            # =========================================
            # 6. PRODUCTION PERSISTENCE
            # =========================================

            # Production writes intentionally disabled.

            repository_persistence = ProductionRepositoryPersistence(
                connection=connection,
            )

            user_persistence = ProductionUserPersistence(
                connection=connection,
            )

            repository_persistence.write(repository_classified)
            user_persistence.write(user_classified)

            # =========================================
            # 7. CLASSIFICATION SUMMARY
            # =========================================

            repository_new = sum(
                len(table_records["new"])
                for table_records in repository_classified.values()
            )

            repository_existing = sum(
                len(table_records["existing"])
                for table_records in repository_classified.values()
            )

            user_new = sum(
                len(table_records["new"])
                for table_records in user_classified.values()
            )

            user_existing = sum(
                len(table_records["existing"])
                for table_records in user_classified.values()
            )

            # =========================================
            # 7. CLASSIFICATION SUMMARY
            # =========================================

            def summarize(classified_records) -> None:

                for schema, tables in classified_records.items():

                    new_count = sum(
                        len(data["new"])
                        for data in tables.values()
                    )

                    existing_count = sum(
                        len(data["existing"])
                        for data in tables.values()
                    )

                    duplicate_count = sum(
                        len(data["duplicate_incoming"])
                        for data in tables.values()
                    )

                    total_count = (
                        new_count
                        + existing_count
                        + duplicate_count
                    )

                    print(f"\n{schema}")
                    print("-" * 40)
                    print(f"New: {new_count}")
                    print(f"Existing: {existing_count}")
                    print(f"Duplicate incoming: {duplicate_count}")
                    print(f"Total: {total_count}")

            summarize(classified_records)
