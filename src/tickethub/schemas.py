from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TicketStatus(str, Enum):
    open = "open"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TicketBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority = TicketPriority.medium
    assignee: str | None = Field(default=None, max_length=100)


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assignee: str | None = Field(default=None, max_length=100)


class TicketListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TicketStatus
    priority: TicketPriority
    description: str | None = None


class TicketDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    status: TicketStatus
    priority: TicketPriority
    assignee: str | None = None

    # Puni JSON iz vanjskog izvora
    source_payload: dict[str, Any] | None = None

    created_at: datetime
    updated_at: datetime


class TicketListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TicketListItem]


class TicketStatsResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
