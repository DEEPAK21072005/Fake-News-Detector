import pytest
from backend.app.ml.preprocessing import extract_linguistic_signals, extract_claims, clean_text_basic


def test_clean_text_basic():
    dirty = "<p>Visit https://example.com for shocking news!!!   </p>"
    cleaned = clean_text_basic(dirty)
    assert "https://" not in cleaned
    assert "<p>" not in cleaned
    assert "shocking news" in cleaned


def test_linguistic_signals_sensational():
    fake_text = "SHOCKING BOMBSHELL: Deep state conspiracy exposed! They don't want you to know the secret miracle truth!"
    signals = extract_linguistic_signals(fake_text, "SECRET MIRACLE CURE")
    assert signals["sensationalism_score"] > 0.3
    assert signals["clickbait_score"] > 0.2
    assert signals["uppercase_ratio"] > 0.1
    assert len(signals["sensational_keywords_found"]) >= 2


def test_linguistic_signals_neutral():
    real_text = "The Ministry of Transport announced regular maintenance operations on regional railway lines scheduled for next month."
    signals = extract_linguistic_signals(real_text, "Transport Ministry Update")
    assert signals["sensationalism_score"] < 0.1
    assert signals["clickbait_score"] < 0.1
    assert signals["uppercase_ratio"] < 0.1


def test_claim_extraction():
    text = "Scientists have discovered that regular exercise reduces cardiac event probability. Health organizations confirmed the report."
    claims = extract_claims(text, "Cardiology Study")
    assert len(claims) >= 1
    assert claims[0]["is_title_claim"] is True or len(claims[0]["text"]) > 10
