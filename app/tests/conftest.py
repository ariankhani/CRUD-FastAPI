import io

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import Engine, StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.database.db import Base, get_db
from app.main import app

# Import models so that they register with Base.metadata
# from app.models import orders, product, users

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine: Engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Set up and tear down the database for the test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Override the database dependency
def override_get_db():
    db: Session = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def test_user(test_client: TestClient) -> dict[str, str]:
    user_data = {"username": "testuser", "password": "testpass"}
    response = test_client.post("/accounts/new-user", json=user_data)
    assert response.status_code == 201, f"Unexpected status: {response.status_code}"
    return user_data


@pytest.fixture(scope="module")
def auth_token(test_client, test_user):
    response = test_client.post(
        "/accounts/login",
        json={"username": test_user["username"], "password": test_user["password"]},
    )
    token = response.json().get("access_token")
    assert token is not None, (
        f"Expected 'access_token' in response, got: {response.json()}"
    )
    return token


# Monkey-patch the image validation functions to always return True
@pytest.fixture(autouse=True)
def override_image_validations(monkeypatch):
    async def always_true(*args, **kwargs):
        return True

    monkeypatch.setattr("app.routes.product.verify_file_type", always_true)
    monkeypatch.setattr("app.routes.product.verify_file_size", always_true)
    monkeypatch.setattr("app.routes.product.verify_file_extension", always_true)


# Fixture to create a product and return its id.
@pytest.fixture
def created_item(test_client, auth_token):
    headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}
    # Form fields for product creation
    data: dict[str, str] = {"name": "test_item", "price": "10.0"}
    # Supply a dummy (empty) file since image is required by the route.
    dummy_file = io.BytesIO(b"")
    dummy_file.name = "dummy.jpg"
    files = {"image": ("dummy.jpg", dummy_file, "image/jpeg")}
    # Ensure correct URL prefix (assuming your router is mounted with /products)
    response = test_client.post(
        "/products/create", data=data, files=files, headers=headers
    )
    assert response.status_code == 201, (
        f"Unexpected status code: {response.status_code}"
    )
    item_id = response.json().get("id")
    assert item_id is not None, "Created item should have an id"
    return item_id
