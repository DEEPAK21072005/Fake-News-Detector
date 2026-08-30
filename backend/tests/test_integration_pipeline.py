import pytest
from backend.app.services.pipeline_service import pipeline_service


@pytest.mark.asyncio
async def test_full_verification_pipeline_text_real():
    real_article = (
        "BAGHDAD (Reuters) - Kurdish authorities offered on Tuesday a joint border deployment "
        "with Iraqi federal forces at the Fish-Khabur crossing point with Turkey, as Baghdad "
        "threatened to resume military operations to seize the strategic territory."
    )
    response = await pipeline_service.execute_verification(
        text=real_article,
        title="Kurds offer joint border deployment",
        category="World",
        inference_mode="BALANCED"
    )
    assert response.verdict in ("LIKELY_REAL", "UNCERTAIN")
    assert response.confidence >= 0.50
    assert len(response.claims) >= 1
    assert response.latency_ms > 0


@pytest.mark.asyncio
async def test_full_verification_pipeline_text_fake():
    fake_article = (
        "SHOCKING BOMBSHELL! Top secret medical insiders have proven that drinking coffee "
        "cures every cancer instantly! The corrupt deep state and mainstream media are banning this secret!"
    )
    response = await pipeline_service.execute_verification(
        text=fake_article,
        title="MIRACLE COFFEE CANCER CURE EXPOSED",
        category="Health",
        inference_mode="BALANCED"
    )
    assert response.verdict == "LIKELY_FAKE"
    assert response.confidence >= 0.55
    assert len(response.key_reasons) >= 1
    assert response.linguistic_signals["sensationalism_score"] > 0.2
