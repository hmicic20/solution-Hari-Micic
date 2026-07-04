"""add source fields to tickets

Revision ID: f666d7c46585
Revises: 54c27220a5ce
Create Date: 2026-07-04 13:56:23.090815

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f666d7c46585'
down_revision: Union[str, Sequence[str], None] = '54c27220a5ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.add_column(
            sa.Column("source_system", sa.String(length=50), nullable=True)
        )
        batch_op.add_column(sa.Column("external_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_tickets_source_system", ["source_system"])
        batch_op.create_index("ix_tickets_external_id", ["external_id"])

    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        op.execute(
            """
            UPDATE tickets
            SET source_system = 'dummyjson',
                external_id = (source_payload ->> 'id')::integer
            WHERE source_payload IS NOT NULL
              AND (source_payload ->> 'id') IS NOT NULL
            """
        )
    elif bind.dialect.name == "sqlite":
        op.execute(
            """
            UPDATE tickets
            SET source_system = 'dummyjson',
                external_id = json_extract(source_payload, '$.id')
            WHERE source_payload IS NOT NULL
              AND json_extract(source_payload, '$.id') IS NOT NULL
            """
        )

    with op.batch_alter_table("tickets") as batch_op:
        batch_op.create_unique_constraint(
            "uq_tickets_source_external_id",
            ["source_system", "external_id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_constraint(
            "uq_tickets_source_external_id",
            type_="unique",
        )
        batch_op.drop_index("ix_tickets_external_id")
        batch_op.drop_index("ix_tickets_source_system")
        batch_op.drop_column("external_id")
        batch_op.drop_column("source_system")
