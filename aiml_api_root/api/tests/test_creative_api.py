import pytest
from httpx import AsyncClient
from api.main import app  

@pytest.mark.asyncio
async def test_generate_creatives_async():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        customer_id = "acmeinc"
        nct_id = "nct06585670"

        response = await ac.get(f"/creatives/generate/{customer_id}", params={"nct_id": nct_id})
        assert response.status_code == 200  
        async for line in response.aiter_lines():
            assert "error" not in line
            assert len(line) > 0 