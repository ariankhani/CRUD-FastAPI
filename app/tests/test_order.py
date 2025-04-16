import pytest

from app.tests.conftest import TestClient
from fastapi import status

@pytest.fixture
def created_order(test_client: TestClient, auth_token, created_item):
    headers = {"Authorization": f"Bearer {auth_token}"}
    order_data = {
        "user_id": 1,
        "items": [{"product_id": created_item, "quantity": 2}]
    }
    
    response = test_client.post("/orders/create/", json=order_data, headers=headers)
    
    # This assertion is correct - keep it as-is
    assert response.status_code == status.HTTP_200_OK



def test_get_order_details(test_client, auth_token, created_order):
    headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}
    response = test_client.get(f"/orders/{created_order}", headers=headers)
    assert response.status_code == 200, f"Unexpected status: {response.status_code}"
    # data = response.json()
    # assert data["id"] == created_order
