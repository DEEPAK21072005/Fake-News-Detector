"""
Notebook 02: Linguistic Preprocessing & Stylometric Feature Extraction
Tests extraction of sensationalism, clickbait, uppercase density, emotional polarity, and claim assertions.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.ml.preprocessing import extract_linguistic_signals, extract_claims

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 02: Linguistic & Stylometry Preprocessing")
    print("=" * 60)

    sample_fake = (
        "BOMBSHELL REVELATION! Top secret laboratory experiments have 100% PROVEN that "
        "drinking coffee cures every cancer instantly! The mainstream media and deep state won't tell you!"
    )

    sample_real = (
        "BAGHDAD (Reuters) - Kurdish authorities offered on Tuesday a joint border deployment "
        "with Iraqi federal forces at the Fish-Khabur crossing point with Turkey."
    )

    print("\n--- Fake Sample Linguistic Signals ---")
    fake_signals = extract_linguistic_signals(sample_fake, "SHOCKING SECRET CURE")
    for k, v in fake_signals.items():
        print(f"  {k}: {v}")

    print("\n--- Real Sample Linguistic Signals ---")
    real_signals = extract_linguistic_signals(sample_real, "Kurds offer joint border deployment")
    for k, v in real_signals.items():
        print(f"  {k}: {v}")

    print("\n--- Extracted Claims from Fake Sample ---")
    claims = extract_claims(sample_fake, "SHOCKING SECRET CURE")
    for c in claims:
        print(f"  Claim [{c['claim_id']}] ({c['type']}): {c['text']}")

if __name__ == "__main__":
    main()
