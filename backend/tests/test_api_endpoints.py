import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_and_system_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "online"

        res_sys = await ac.get("/api/system/status")
        assert res_sys.status_code == 200
        sys_data = res_sys.json()
        assert sys_data["backend"] == "online"
        assert "hardware" in sys_data


@pytest.mark.asyncio
async def test_models_list_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/models")
        assert res.status_code == 200
        models = res.json()
        assert len(models) >= 4
        names = [m["name"] for m in models]
        assert "VeritasFusion" in names
        assert "TFIDF_LogisticRegression" in names


@pytest.mark.asyncio
async def test_analyze_text_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "text": "BOMBSHELL REVELATION! SECRET MIRACLE CURE THEY DONT WANT YOU TO KNOW! Drink coffee to destroy all cancers!",
            "title": "SECRET CANCER CURE",
            "category": "Health",
            "inference_mode": "BALANCED"
        }
        res = await ac.post("/api/analyze/text", json=payload)
        assert res.status_code == 200
        result = res.json()
        assert result["verdict"] in ("LIKELY_FAKE", "LIKELY_REAL", "UNCERTAIN", "INSUFFICIENT_EVIDENCE")
        assert 0.0 <= result["confidence"] <= 1.0
        assert "modality_breakdown" in result
        assert "claims" in result
        assert "linguistic_signals" in result
