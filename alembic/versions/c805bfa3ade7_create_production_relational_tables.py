"""create production relational tables

Revision ID: c805bfa3ade7
Revises: c00c3f42e807
Create Date: 2026-11-09 22:39:51.612780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as text

from src.gitrec.persistence.postgres.schema.production_builder import (
    ProductionSchemaBuilder,
)

# revision identifiers, used by Alembic.
revision: str = 'c805bfa3ade7'
down_revision: Union[str, Sequence[str], None] = 'c00c3f42e807'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create production relational tables."""
    connection = op.get_bind()

    builder = ProductionSchemaBuilder(
        connection=connection,
    )
    builder.create()


def downgrade() -> None:
    """Remove production schemas."""
    connection = op.get_bind()

    connection.execute(
        text.text(
            "DROP SCHEMA IF EXISTS production_repository CASCADE"
        )
    )
    connection.execute(
        text.text(
            "DROP SCHEMA IF EXISTS production_user CASCADE"
        )
    )