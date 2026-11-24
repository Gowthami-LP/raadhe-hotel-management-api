from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_invalid_menu_price():
    response = client.post(
        "/menu/",
        json={
            "name": "Chicken Biryani",
            "category": "Biryani",
            "description": "Chicken Biryani",
            "price": -100,
            "is_available": True,
        },
    )

    assert response.status_code == 422
