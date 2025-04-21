# test_products.py

import io
from fastapi import status
from fastapi.testclient import TestClient


def test_create_product(test_client: TestClient, auth_token):
    headers: dict[str, str] = {"Authorization": f"Bearer {auth_token}"}
    data: dict[str, str] = {"name": "Test Product", "price": "19.99"}
    dummy_file = io.BytesIO(b"")
    dummy_file.name = "dummy.jpg"
    files = {"image": ("dummy.jpg", dummy_file, "image/jpeg")}

    response = test_client.post(
        "/products/create", data=data, files=files, headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED

def test_read_item(test_client: TestClient, auth_token, created_item):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = test_client.get(f"/products/{created_item}", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data.get("name") == "test_item", "Item name does not match the created item"


def test_update_item(test_client, auth_token, created_item):
    headers = {"Authorization": f"Bearer {auth_token}"}
    update_data = {"name": "updated_item", "price": "12.0"}
    response = test_client.put(
        f"/products/update/{created_item}", data=update_data, headers=headers
    )
    assert response.status_code == status.HTTP_200_OK

    updated_data = response.json()
    assert updated_data.get("name") == "updated_item", (
        "Item name was not updated correctly"
    )


def test_delete_item(test_client, auth_token, created_item):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = test_client.delete(f"/products/delete/{created_item}", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    read_response = test_client.get(f"/products/{created_item}", headers=headers)
    assert read_response.status_code == status.HTTP_404_NOT_FOUND


def test_invalid_token(test_client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.get("/products/1", headers=headers)
    assert response.status_code in (401, 403)
