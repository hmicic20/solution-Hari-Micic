from typing import Any

from tickethub.schemas import TicketPriority, TicketStatus


def calculate_priority(ticket_id: int) -> str:
    # Jednostavno pravilo za određivanje prioriteta prema ID-u
    remainder = ticket_id % 3

    if remainder == 0:
        return TicketPriority.high.value

    if remainder == 1:
        return TicketPriority.low.value

    return TicketPriority.medium.value


def map_status(completed: bool) -> str:
    # DummyJSON completed pretvaramo u naš status
    if completed:
        return TicketStatus.closed.value

    return TicketStatus.open.value


def build_users_by_id(users: list[dict[str, Any]]) -> dict[int, str]:
    # Pretvara listu korisnika u mapu user_id -> username
    return {
        user["id"]: user["username"]
        for user in users
    }


def map_todo_to_ticket_data(
    todo: dict[str, Any],
    users_by_id: dict[int, str],
) -> dict[str, Any]:
    # Pretvara jedan DummyJSON todo u podatke za naš Ticket model
    todo_text = todo["todo"]
    user_id = todo.get("userId")

    return {
        "id": todo["id"],
        "title": todo_text,
        "description": todo_text,
        "status": map_status(todo["completed"]),
        "priority": calculate_priority(todo["id"]),
        "assignee": users_by_id.get(user_id),
        "source_payload": todo,
    }