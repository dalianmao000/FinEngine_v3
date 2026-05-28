import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_full_pipeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/health")
        assert health.status_code == 200

        chat_response = await client.post(
            "/api/v1/chat",
            json={"prompt": "What is my balance?", "business_line": "customer_service"},
        )
        assert chat_response.status_code == 200
        data = chat_response.json()
        assert "response" in data
        assert "model" in data

@pytest.mark.asyncio
async def test_guardrail_blocks_pii():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/chat",
            json={"prompt": "My card is 1234-5678-9012-3456", "business_line": "customer_service"},
        )
        assert response.status_code == 400
        assert "blocked" in response.json()["detail"].lower()