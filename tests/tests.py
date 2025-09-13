import pytest
from httpx import AsyncClient
from app.main import app
import asyncio

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient):
    employee_data = {
        "employee_id": "E001",
        "name": "John Doe",
        "department": "Engineering",
        "salary": 75000,
        "joining_date": "2023-01-15",
        "skills": ["Python", "MongoDB", "APIs"]
    }
    
    response = await client.post("/employees/", json=employee_data)
    assert response.status_code == 201
    assert "Employee created successfully" in response.json()["message"]

@pytest.mark.asyncio
async def test_get_employee(client: AsyncClient):
    response = await client.get("/employees/E001")
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "E001"
    assert data["name"] == "John Doe"
