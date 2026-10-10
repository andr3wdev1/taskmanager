import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_session
from app.models import Base, Task

import os
from dotenv import load_dotenv

client = TestClient(app)

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not set")

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=test_engine)


def override_get_session():
    with TestingSessionLocal() as session:
        yield session



# Чтобы пайтест автоматически обновлял
# тестовую бд перед тестами

@pytest.fixture(autouse=True)
def reset_tasks():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestingSessionLocal() as session:
        session.add_all([
            Task(title="Teach Sql"),
            Task(title="Teach python"),
            Task(title="Do task manager"),
        ])
        session.commit()

# Фикстура для подмены сессии
@pytest.fixture
def override_session():
    app.dependency_overrides[get_session] = override_get_session
    yield # - момент когда выполняется тест
    app.dependency_overrides.pop(get_session, None)
# в конце удаление подмены


# Сами тесты, pytest видит функцию
# которая начинается с test
# и автоматически тестирует

def test_update_task(override_session, reset_tasks):
    response = client.patch(
        "/tasks/1",
        json={"title": "Updated title"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    print("STATUS:", response.status_code)
    print("BODY:", response.text)
    assert data["id"] == 1
    assert data["title"] == "Updated title"

def test_update_task_empty_body(override_session, reset_tasks):
    before = client.get("/tasks/1").json()
    response = client.patch(
        "/tasks/1",
        json={}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == before

def test_get_tasks(override_session, reset_tasks):
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for task in data:
        assert "id" in task
        assert "title" in task
        assert isinstance(task["id"], int)
        assert isinstance(task["title"], str)


def test_create_task(override_session, reset_tasks):
    response = client.post(
        "/tasks",
        json={"title": "Test_title"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data
    assert "title" in data
    assert isinstance(data["id"], int)
    assert isinstance(data["title"], str)
    assert data["title"] == "Test_title"
    tasks = client.get("/tasks").json()
    assert data in tasks


def test_create_task_without_title(override_session, reset_tasks):
    response = client.post(
        "/tasks",
        json={}
    )
    assert response.status_code == 422


def test_get_task(override_session, reset_tasks):
    response = client.get("/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data
    assert "title" in data
    assert data["id"] == 1


def test_get_task_not_found(override_session, reset_tasks):
    tasks = client.get("/tasks").json()
    nonexistent_id = 999_999_999
    response = client.get(f"/tasks/{nonexistent_id}")
    assert response.status_code == 404



def test_update_task_not_found(override_session, reset_tasks):
    nonexistent_id = 999_999_999
    response = client.patch(
        f"/tasks/{nonexistent_id}",
        json={"title": "Update Task"}
    )
    assert response.status_code == 404


def test_update_task_invalid_data(override_session, reset_tasks):
    response = client.patch(
        "/tasks/1",
        json={"title": []}
    )
    assert response.status_code == 422


def test_delete_task(override_session, reset_tasks):
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    response = client.get("/tasks/1")
    assert response.status_code == 404


def test_delete_task_not_found(override_session, reset_tasks):
    nonexistent_id = 999_999_999
    response = client.delete(f"/tasks/{nonexistent_id}")
    assert response.status_code == 404
