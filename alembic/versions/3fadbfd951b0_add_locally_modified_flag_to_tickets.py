"""add locally modified flag to tickets

Revision ID: 3fadbfd951b0
Revises: f666d7c46585
Create Date: 2026-07-04 15:32:39.814904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fadbfd951b0'
down_revision: Union[str, Sequence[str], None] = 'f666d7c46585'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.add_column(
            sa.Column(
                "locally_modified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    op.execute(
        """
        UPDATE tickets
        SET source_system = 'local'
        WHERE source_system IS NULL
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_column("locally_modified")
