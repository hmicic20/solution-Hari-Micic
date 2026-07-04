from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from tickethub.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    source_system: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    external_id: Mapped[int | None] = mapped_column(
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    assignee: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Sprema puni JSON iz DummyJSON-a
    source_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'closed')",
            name="ck_tickets_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tickets_priority",
        ),
        UniqueConstraint(
            "source_system",
            "external_id",
            name="uq_tickets_source_external_id",
        ),
    )
