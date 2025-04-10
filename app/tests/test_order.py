import pytest

from app.tests.conftest import TestClient


@pytest.fixture
def created_order(test_client: TestClient, auth_token, created_item):
    headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}
    
    order_data: dict = {
        "user_id": 1,
        "items": [
            {"product_id": created_item, "quantity": 2}
        ]
    }    
    response = test_client.post("/orders/create", json=order_data, headers=headers)
    
    assert response.status_code == 201, (
        f"Unexpected status code: {response.status_code} "
        f"with response: {response.json()}"
    )
    
    order_id = response.json().get("id")
    assert order_id is not None, "Created order should have an id"
    
    return order_id


def test_get_order_details(test_client, auth_token, created_order):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = test_client.get(f"/orders/{created_order}", headers=headers)
    assert response.status_code == 200, f"Unexpected status: {response.status_code}"
    data = response.json()
    assert data["id"] == created_order
