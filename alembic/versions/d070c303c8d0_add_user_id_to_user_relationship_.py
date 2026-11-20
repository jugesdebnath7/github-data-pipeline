"""add user_id to user relationship staging tables

Revision ID: d070c303c8d0
Revises: c805bfa3ade7
Create Date: 2026-11-19 20:16:42.880808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd070c303c8d0'
down_revision: Union[str, Sequence[str], None] = (
    'c00c3f42e807',
    'c805bfa3ade7',
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = (
    "follower",
    "following",
    "received_event",
    "starred",
    "repository",
)


def upgrade() -> None:
    """
    Existing relationship records cannot reliably be assigned to their parent users.
    So clearing them before adding NOT NULL.

    """
    op.execute("""
        TRUNCATE TABLE
            staging_user.follower,
            staging_user.following,
            staging_user.received_event,
            staging_user.starred,
            staging_user.repository     
    """)

    for table in TABLES:
        op.add_column(
            table, 
            sa.Column(
                "user_id",
                sa.BigInteger(),
                nullable=False,
            ),
            schema="staging_user",
        )


def downgrade() -> None:
    """Downgrade schema."""

    for table in reversed(TABLES):
        op.drop_column(
            table,
            "user_id",
            schema="staging_user",
        )
