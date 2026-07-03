"""add ticket constraints

Revision ID: 54c27220a5ce
Revises: 1b59f51b76d5
Create Date: 2026-07-03 18:14:11.346120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54c27220a5ce'
down_revision: Union[str, Sequence[str], None] = '1b59f51b76d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.create_check_constraint(
            "ck_tickets_status",
            "status IN ('open', 'closed')",
        )
        batch_op.create_check_constraint(
            "ck_tickets_priority",
            "priority IN ('low', 'medium', 'high')",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_constraint(
            "ck_tickets_priority",
            type_="check",
        )
        batch_op.drop_constraint(
            "ck_tickets_status",
            type_="check",
        )
