import pytest
from httpx import AsyncClient, ASGITransport

from main import app

@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(transport=ASGITransport(app)) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Прогноз продаж на следующие 20 дней" in response.text

@pytest.mark.asyncio
async def test_add_sale():
    sale_data = {
        "sale_date": "2025-01-22T00:00:00",
        "quantity": 5,
        "item_id": 1
    }
    async with AsyncClient(transport=ASGITransport(app)) as ac:
        response = await ac.post("/sales", json=sale_data)
    assert response.status_code == 200
    assert response.json()["sale"]["quantity"] == 5
    assert response.json()["sale"]["item_id"] == 1