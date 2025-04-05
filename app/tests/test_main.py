# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, get_db
from app.main import app

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    Base.metadata.drop_all(bind=engine)

# Create tables and override the database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close() # type: ignore


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def test_user(test_client):
    # Create a test user
    user_data = {"username": "testuser", "password": "testpass"}
    response = test_client.post("/accounts/new-user", json=user_data)
    assert response.status_code == 201
    return user_data


@pytest.fixture(scope="module")
def auth_token(test_client, test_user):
    # Get JWT token
    response = test_client.post(
        "/accounts/login",
        data={"username": test_user["username"], "password": test_user["password"]},
    )
    return response.json()["access_token"]


# # Tests for unauthenticated access (403 Forbidden)
# def test_unauthenticated_access(test_client):
#     # Test all CRUD endpoints without a token
#     endpoints = [
#         ("POST", "/products/", {"name": "item1"}),
#         ("GET", "/products/1", None),
#         ("PUT", "/products/1", {"name": "updated"}),
#         ("DELETE", "/products/1", None),
#     ]

#     for method, url, json in endpoints:
#         if method == "GET" or method == "DELETE":
#             response = test_client.request(method, url)
#         else:
#             response = test_client.request(method, url, json=json)
#         assert response.status_code == 403


# Tests for authenticated CRUD operations
def test_authenticated_crud(test_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create item
    response = test_client.post("/products/create", json={"name": "test_item"}, headers=headers)
    assert response.status_code == 201
    item_id = response.json()["id"]

    # Read item
    response = test_client.get(f"/products/{item_id}", headers=headers)
    assert response.status_code == 200

    # Update item
    response = test_client.put(
        f"/products/update/{item_id}", json={"name": "updated_item"}, headers=headers
    )
    assert response.status_code == 200

    # Delete item
    response = test_client.delete(f"/products/delete/{item_id}", headers=headers)
    assert response.status_code == 200


# Optional: Test invalid/expired tokens
def test_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.get("/products/1", headers=headers)
    assert response.status_code == 401  # Or 403 based on your app's logic
