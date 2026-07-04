from tickethub.mappers import (
    build_users_by_id,
    calculate_priority,
    map_status,
    map_todo_to_ticket_data,
)


def test_calculate_priority() -> None:
    assert calculate_priority(1) == "low"
    assert calculate_priority(2) == "medium"
    assert calculate_priority(3) == "high"


def test_map_status() -> None:
    assert map_status(True) == "closed"
    assert map_status(False) == "open"


def test_build_users_by_id() -> None:
    users = [
        {"id": 1, "username": "ivan"},
        {"id": 2, "username": "ana"},
    ]

    result = build_users_by_id(users)

    assert result == {
        1: "ivan",
        2: "ana",
    }


def test_map_todo_to_ticket_data() -> None:
    todo = {
        "id": 1,
        "todo": "Fix printer issue",
        "completed": False,
        "userId": 2,
    }
    users_by_id = {
        2: "ana",
    }

    result = map_todo_to_ticket_data(todo, users_by_id)

    assert "id" not in result
    assert result["source_system"] == "dummyjson"
    assert result["external_id"] == 1
    assert result["title"] == "Fix printer issue"
    assert result["description"] == "Fix printer issue"
    assert result["status"] == "open"
    assert result["priority"] == "low"
    assert result["assignee"] == "ana"
    assert result["source_payload"] == todo
