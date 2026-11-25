# src/github_data_pipeline/persistence/postgres/schema/production_builder.py

from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKeyConstraint,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    UniqueConstraint,
    inspect,
    text,
)
from sqlalchemy.engine import Connection
from .production_constraints import (
    PRIMARY_KEYS,
    UNIQUE_CONSTRAINTS,
    FOREIGN_KEYS,
    CHECK_CONSTRAINTS,
    ADDITIONAL_COLUMNS,
    PRODUCTION_COLUMNS,
    COLUMN_RENAMES,
)


# =================================================
# SCHEMA CONFIGURATION
# =================================================

SCHEMA_MAPPING = {
    "staging_repository": "production_repository",
    "staging_user": "production_user",
}


class ProductionSchemaBuilder:
    """
    Build production PostgreSQL tables from reflected staging tables.

    Uses SQLAlchemy Core. No ORM models are required.
    """

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

        # Metadata for production tables.
        self.metadata = MetaData()

        # Metadata for reflected staging tables.
        self.source_metadata = MetaData()

        self.tables: dict[str, Table] = {}

    # =================================================
    # 1. REFLECT STAGING TABLES
    # =================================================

    def _reflect_table(
        self,
        schema: str,
        table_name: str,
    ) -> Table:

        return Table(
            table_name,
            self.source_metadata,
            schema=schema,
            autoload_with=self.connection,
        )

    # =================================================
    # 2. BUILD PRODUCTION COLUMNS
    # =================================================

    def _build_columns(
        self,
        source_table: Table,
        target_key: str,
    ) -> list[Column]:

        columns: list[Column] = []

        existing_columns: set[str] = set()

        allowed_columns = PRODUCTION_COLUMNS.get(target_key, None)

        renames = COLUMN_RENAMES.get(target_key, {})

        primary_key_columns = PRIMARY_KEYS.get(target_key, [])

        for source_column in source_table.columns:

            # Apply production column renaming.
            target_column_name = renames.get(
                source_column.name,
                source_column.name,
            )

            # Apply production column allowlist.
            if (
                allowed_columns is not None
                and target_column_name not in allowed_columns
            ):
                continue

            if target_column_name in existing_columns:
                raise ValueError(
                    f"Duplicate production column "
                    f"{target_key}.{target_column_name}"
                )

            column = Column(
                target_column_name,
                source_column.type,
                nullable=source_column.nullable,
                server_default=source_column.server_default,
                comment=source_column.comment,
            )

            # Production primary-key columns must be non-null.
            if target_column_name in primary_key_columns:
                column.nullable = False

            columns.append(column)

            existing_columns.add(target_column_name)

        # Add production-specific columns.
        for column_name, column_type in (
            ADDITIONAL_COLUMNS.get(target_key, {}).items()
        ):

            if column_name in existing_columns:
                continue

            columns.append(
                Column(
                    column_name,
                    column_type,
                    nullable=False,
                )
            )

            existing_columns.add(column_name)

        # Validate primary-key columns.
        missing_pk_columns = (
            set(primary_key_columns) - existing_columns
        )

        if missing_pk_columns:
            raise ValueError(
                f"Missing primary-key columns in {target_key}: "
                f"{sorted(missing_pk_columns)}"
            )

        # Validate production allowlist.
        if allowed_columns is not None:
            missing_columns = set(allowed_columns) - existing_columns

            if missing_columns:
                raise ValueError(
                    f"Missing production columns in {target_key}: "
                    f"{sorted(missing_columns)}"
                )

        return columns

    # =================================================
    # 3. APPLY PRIMARY KEYS
    # =================================================

    def _apply_primary_key(
        self,
        table: Table,
        target_key: str,
    ) -> None:

        columns = PRIMARY_KEYS.get(target_key, [])

        if columns:
            table.append_constraint(
                PrimaryKeyConstraint(
                    *columns,
                    name=f"pk_{table.name}",
                )
            )

    # =================================================
    # 4. APPLY UNIQUE CONSTRAINTS
    # =================================================

    def _apply_unique_constraints(
        self,
        table: Table,
        target_key: str,
    ) -> None:

        constraints = UNIQUE_CONSTRAINTS.get(target_key, [])

        for index, columns in enumerate(constraints):

            table.append_constraint(
                UniqueConstraint(
                    *columns,
                    name=f"uq_{table.name}_{index}",
                )
            )

    # =================================================
    # 5. APPLY FOREIGN KEYS
    # =================================================

    def _apply_foreign_keys(
        self,
        table: Table,
        target_key: str,
    ) -> None:

        constraints = FOREIGN_KEYS.get(target_key, [])

        for index, (
            local_columns,
            target_schema,
            target_table,
            target_columns,
        ) in enumerate(constraints):

            remote_columns = [
                (
                    f"{target_schema}."
                    f"{target_table}."
                    f"{column}"
                )
                for column in target_columns
            ]

            table.append_constraint(
                ForeignKeyConstraint(
                    local_columns,
                    remote_columns,
                    name=f"fk_{table.name}_{index}",
                )
            )

    # =================================================
    # 6. APPLY CHECK CONSTRAINTS
    # =================================================

    def _apply_check_constraints(
        self,
        table: Table,
        target_key: str,
    ) -> None:

        constraints = CHECK_CONSTRAINTS.get(target_key, {})

        for column_name, expression in constraints.items():

            if column_name not in table.columns:
                raise ValueError(
                    f"Check constraint references missing column: "
                    f"{target_key}.{column_name}"
                )

            table.append_constraint(
                CheckConstraint(
                    expression,
                    name=f"ck_{table.name}_{column_name}",
                )
            )

    # =================================================
    # 7. BUILD PRODUCTION TABLE
    # =================================================

    def _build_table(
        self,
        source_table: Table,
        target_schema: str,
        target_name: str,
    ) -> Table:

        target_key = f"{target_schema}.{target_name}"

        columns = self._build_columns(
            source_table,
            target_key,
        )

        target_table = Table(
            target_name,
            self.metadata,
            *columns,
            schema=target_schema,
        )

        self._apply_primary_key(
            target_table,
            target_key,
        )

        self._apply_unique_constraints(
            target_table,
            target_key,
        )

        self._apply_foreign_keys(
            target_table,
            target_key,
        )

        self._apply_check_constraints(
            target_table,
            target_key,
        )

        self.tables[target_key] = target_table

        return target_table

    # =================================================
    # 8. REFLECT AND BUILD ALL TABLES
    # =================================================

    def build(self) -> MetaData:
        """
        Reflect staging tables and construct production metadata.

        Does not create database tables.
        """

        inspector = inspect(self.connection)

        for source_schema, target_schema in SCHEMA_MAPPING.items():

            if not inspector.has_schema(source_schema):
                raise RuntimeError(
                    f"Staging schema does not exist: {source_schema}"
                )

            source_tables = inspector.get_table_names(
                schema=source_schema,
            )

            if not source_tables:
                raise RuntimeError(
                    f"No staging tables found in {source_schema}"
                )

            for source_name in source_tables:

                source_table = self._reflect_table(
                    source_schema,
                    source_name,
                )

                # The target table retains its name.
                target_name = source_name

                self._build_table(
                    source_table,
                    target_schema,
                    target_name,
                )

        self.validate()

        return self.metadata

    # =================================================
    # 9. VALIDATE PRODUCTION METADATA
    # =================================================

    def validate(self) -> None:
        """Validate constructed tables and relationships."""

        for target_key, table in self.tables.items():

            if not table.primary_key.columns:
                raise ValueError(
                    f"Production table has no primary key: "
                    f"{target_key}"
                )

            for constraint in table.foreign_key_constraints:

                remote_table = (
                    f"{constraint.elements[0].column.table.schema}."
                    f"{constraint.elements[0].column.table.name}"
                )

                if remote_table not in self.tables:
                    raise ValueError(
                        f"Foreign-key target is missing: "
                        f"{target_key} -> {remote_table}"
                    )

    # =================================================
    # 10. CREATE PRODUCTION SCHEMAS
    # =================================================

    def create_schemas(self) -> None:
        """Create production PostgreSQL schemas if necessary."""

        preparer = self.connection.dialect.identifier_preparer

        for schema in SCHEMA_MAPPING.values():

            quoted_schema = preparer.quote(schema)

            self.connection.execute(
                text(
                    f"CREATE SCHEMA IF NOT EXISTS {quoted_schema}"
                )
            )

    # =================================================
    # 11. CREATE PRODUCTION TABLES
    # =================================================

    def create(self) -> None:
        """
        Create production schemas and tables.

        Existing tables are not altered.
        """

        self.create_schemas()

        metadata = self.build()

        metadata.create_all(
            bind=self.connection,
            checkfirst=True,
        )

    # =================================================
    # 12. INSPECT GENERATED METADATA
    # =================================================

    def summary(self) -> dict[str, dict]:
        """Return a summary of generated production tables."""

        result = {}

        for target_key, table in self.tables.items():

            result[target_key] = {
                "columns": list(table.columns.keys()),
                "primary_key": [
                    column.name
                    for column in table.primary_key.columns
                ],
                "unique_constraints": [
                    [
                        column.name
                        for column in constraint.columns
                    ]
                    for constraint in table.constraints
                    if isinstance(constraint, UniqueConstraint)
                ],
                "foreign_keys": [
                    {
                        "columns": [
                            element.parent.name
                            for element in constraint.elements
                        ],
                        "references": [
                            str(element.target_fullname)
                            for element in constraint.elements
                        ],
                    }
                    for constraint in table.foreign_key_constraints
                ],
                "check_constraints": [
                    str(constraint.sqltext)
                    for constraint in table.constraints
                    if isinstance(constraint, CheckConstraint)
                ],
            }

        return result

    def get_staging_table(
        self,
        table_name: str,
        schema: str,
    ) -> Table:
        """Get reflected staging table."""

        key = f"{schema}.{table_name}"

        try:
            return self.source_metadata.tables[key]

        except KeyError:
            raise KeyError(
                f"Staging table not found: {key}. "
                f"Available staging tables: "
                f"{list(self.source_metadata.tables.keys())}"
            )
        
    def get_production_table(
        self,
        table_name: str,
        schema: str,
    ) -> Table:
        """Get constructed production table."""

        key = f"{schema}.{table_name}"

        try:
            return self.metadata.tables[key]

        except KeyError:
            raise KeyError(
                f"Production table not found: {key}. "
                f"Available production tables: "
                f"{list(self.metadata.tables.keys())}"
            )
