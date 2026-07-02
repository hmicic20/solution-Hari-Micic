import pytest
from pydantic import ValidationError

from tickethub.schemas import TicketCreate, TicketPriority, TicketStatus


def test_ticket_create_accepts_valid_data() -> None:
    ticket = TicketCreate(
        title="Problem s printerom",
        description="Printer ne radi.",
        status=TicketStatus.open,
        priority=TicketPriority.high,
        assignee="ivan",
    )

    assert ticket.title == "Problem s printerom"
    assert ticket.status == TicketStatus.open
    assert ticket.priority == TicketPriority.high


def test_ticket_create_rejects_empty_title() -> None:
    with pytest.raises(ValidationError):
        TicketCreate(title="")


def test_ticket_create_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        TicketCreate(title="Test ticket", status="invalid")


def test_ticket_create_rejects_invalid_priority() -> None:
    with pytest.raises(ValidationError):
        TicketCreate(title="Test ticket", priority="urgent")