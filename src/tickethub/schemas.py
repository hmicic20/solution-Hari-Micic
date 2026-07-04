from datetime import datetime
from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class TicketStatus(str, Enum):
    open = "open"
    closed = "closed"


class TicketPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


NonEmptyTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]

OptionalDescription = (
    Annotated[
        str,
        StringConstraints(strip_whitespace=True, max_length=2000),
    ]
    | None
)

OptionalAssignee = (
    Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
    ]
    | None
)

NonEmptyString = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class TicketBase(BaseModel):
    title: NonEmptyTitle
    description: OptionalDescription = None
    status: TicketStatus = TicketStatus.open
    priority: TicketPriority = TicketPriority.medium
    assignee: OptionalAssignee = None


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: NonEmptyTitle | None = None
    description: OptionalDescription = None
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assignee: OptionalAssignee = None


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


class AuthLoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    expires_in_mins: int | None = Field(default=30, ge=1, le=1440)


class AuthTokenResponse(BaseModel):
    id: int
    username: str
    email: str
    firstName: str
    lastName: str
    gender: str
    image: str
    accessToken: str
    refreshToken: str


class AuthUserResponse(BaseModel):
    id: int
    username: str
    email: str
    firstName: str
    lastName: str
    gender: str
    image: str
