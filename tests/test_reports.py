import sqlite3

from fastapi.testclient import TestClient

from app.routers import reports


def test_sales_report(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "total"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "category": "Laptop",
        "items": [
            {
                "id": 1,
                "name": "Zenbook 14 OLED",
                "category": "Laptop",
                "price": 42900.0,
            }
        ],
        "total": 42900.0,
    }


def test_sales_report_does_not_interpolate_category(client: TestClient) -> None:
    category = "Laptop' OR 1=1 --"

    response = client.get("/reports/sales", params={"category": category})

    assert response.status_code == 200
    assert response.json() == {"category": category, "items": [], "total": 0}


def test_sales_report_rejects_python_formula(client: TestClient) -> None:
    response = client.get(
        "/reports/sales",
        params={"category": "Laptop", "formula": "__import__('os').system('id')"},
    )

    assert response.status_code == 422


def test_sales_report_does_not_disclose_database_error(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(reports, "create_database", lambda: sqlite3.connect(":memory:"))

    response = client.get("/reports/sales", params={"category": "Laptop"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Unable to generate sales report"}
