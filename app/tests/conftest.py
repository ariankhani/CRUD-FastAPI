import base64
import io

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from app.core.security import create_access_token
from app.crud.user import create_user, get_user_by_username, update_user_jti
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


@pytest.fixture
def auth_token() -> str:
    # Ensure the test user exists and has a JTI stored in the database so the
    # generated token will match the DB and be accepted by auth deps.
    db = TestingSessionLocal()
    try:
        user = get_user_by_username(db, "testuser")
        if not user:
            # create a lightweight test user directly in DB
            create_user(db, "testuser", "testpass")

        jti = update_user_jti(db, "testuser")
    finally:
        db.close()

    token = create_access_token(data={"sub": "testuser"}, jti=jti)
    return token

# Monkey-patch the image validation functions to always return True
@pytest.fixture(autouse=True)
def override_image_validations(monkeypatch: pytest.MonkeyPatch):
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
    # Minimal valid 1x1 pixel black GIF (43 bytes)
    gif_base64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    gif_data = base64.b64decode(gif_base64)
    dummy_file = io.BytesIO(gif_data)
    dummy_file.name = "dummy.gif"
    
    files = {"image": (dummy_file.name, dummy_file, "image/gif")}

    response = test_client.post(
        "/products/create",
        data=data,
        files=files,
        headers=headers
    )
    
    assert response.status_code == 201, (
        f"Failed to create item. Response: {response.json()}"
    )
    return response.json()["id"]