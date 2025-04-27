import pytest
from datetime import datetime, timedelta


@pytest.fixture
def test_task(authorized_client, test_user):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": 1
    }
    response = authorized_client.post("/api/tasks", json=task_data)
    return response.json()

def test_create_task(authorized_client, test_user):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": 1
    }
    response = authorized_client.post("/api/tasks", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert data["priority"] == task_data["priority"]
    assert data["owner_id"] == test_user.id
    assert "created_at" in data
    assert "id" in data


def test_create_task_unauthorized(client):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending",
        "priority": 1
    }
    response = client.post("/api/tasks", json=task_data)
    assert response.status_code == 403


def test_get_task_by_id(authorized_client, test_task):
    response = authorized_client.get(f"/api/tasks/{test_task['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_task["id"]
    assert data["title"] == test_task["title"]
    assert data["description"] == test_task["description"]


def test_get_task_not_found(authorized_client):
    response = authorized_client.get("/api/tasks/9999")
    assert response.status_code == 404
    assert "Задача не найдена" in response.json()["detail"]


def test_get_tasks_empty(authorized_client):
    response = authorized_client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_tasks(authorized_client, test_user):
    tasks_data = [
        {"title": "Task 1", "status": "pending", "priority": 1},
        {"title": "Task 2", "status": "done", "priority": 2},
        {"title": "Task 3", "status": "pending", "priority": 3}
    ]
    
    created_tasks = []
    for task in tasks_data:
        response = authorized_client.post("/api/tasks", json=task)
        created_tasks.append(response.json())
    
    response = authorized_client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    task_ids = [task["id"] for task in data]
    for task in created_tasks:
        assert task["id"] in task_ids


def test_filter_tasks_by_status(authorized_client):
    tasks_data = [
        {"title": "Pending Task 1", "status": "pending", "priority": 1},
        {"title": "Done Task", "status": "done", "priority": 2},
        {"title": "Pending Task 2", "status": "pending", "priority": 3}
    ]
    
    for task in tasks_data:
        authorized_client.post("/api/tasks", json=task)
    
    response = authorized_client.get("/api/tasks?status=pending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["status"] == "pending" for task in data)
    
    response = authorized_client.get("/api/tasks?status=done")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert all(task["status"] == "done" for task in data)


def test_filter_tasks_by_priority(authorized_client):
    tasks_data = [
        {"title": "Low Priority", "priority": 1},
        {"title": "Medium Priority", "priority": 2},
        {"title": "High Priority", "priority": 3}
    ]
    
    for task in tasks_data:
        authorized_client.post("/api/tasks", json=task)
    
    response = authorized_client.get("/api/tasks?priority=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == 2


def test_filter_tasks_by_created_after(authorized_client):
    response = authorized_client.get("/api/tasks")
    initial_tasks = response.json()
    
    task_data = {"title": "Future Task", "priority": 1}
    create_response = authorized_client.post("/api/tasks", json=task_data)
    task = create_response.json()

    created_at = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
    filter_date = (created_at - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S")
    
    response = authorized_client.get(f"/api/tasks?created_after={filter_date}")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 1
    assert any(t["id"] == task["id"] for t in data)

def test_search_tasks(authorized_client):
    tasks_data = [
        {"title": "Find this task", "description": "Normal description"},
        {"title": "Normal title", "description": "Find in description"},
        {"title": "Another task", "description": "Another description"}
    ]
    
    for task in tasks_data:
        authorized_client.post("/api/tasks", json=task)

    response = authorized_client.get("/api/tasks/search?q=Find")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    titles_and_descriptions = [(task["title"], task["description"]) for task in data["results"]]
    assert ("Find this task", "Normal description") in titles_and_descriptions
    assert ("Normal title", "Find in description") in titles_and_descriptions


def test_update_task(authorized_client, test_task):
    update_data = {
        "title": "Updated Title",
        "status": "done"
    }
    response = authorized_client.put(f"/api/tasks/{test_task['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["status"] == update_data["status"]
    assert data["description"] == test_task["description"]
    assert data["priority"] == test_task["priority"]


def test_update_task_not_found(authorized_client):
    update_data = {"title": "Updated Title"}
    response = authorized_client.put("/api/tasks/9999", json=update_data)
    assert response.status_code == 404


def test_delete_task(authorized_client, test_task):
    response = authorized_client.delete(f"/api/tasks/{test_task['id']}")
    assert response.status_code == 204
    
    response = authorized_client.get(f"/api/tasks/{test_task['id']}")
    assert response.status_code == 404


def test_delete_task_not_found(authorized_client):
    response = authorized_client.delete("/api/tasks/9999")
    assert response.status_code == 404