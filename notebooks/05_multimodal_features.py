"""
Notebook 05: Multimodal Vision & OCR Representation
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.ml.vision_ocr import extract_visual_features, extract_ocr_text
from backend.app.core.config import settings

def main():
    print("=" * 60)
    print("VeritasAI Research Notebook 05: Multimodal Vision & OCR")
    print("=" * 60)

    # Create synthetic test image
    test_img_path = settings.DATA_PATH / "test_sample_image.png"
    img = Image.new("RGB", (300, 200), color=(73, 109, 137))
    img.save(test_img_path)

    features = extract_visual_features(test_img_path)
    print(f"Image Dimensions: {features['dimensions']}")
    print(f"Perceptual Hash (pHash): {features['phash']}")
    print(f"Visual Vector Dim: {len(features['embedding'])}")
    print(f"Contrast Metric: {features['contrast']}")

    ocr_res = extract_ocr_text(test_img_path)
    print(f"OCR Engine: {ocr_res['engine']} | Confidence: {ocr_res['confidence']}")

    if test_img_path.exists():
        test_img_path.unlink()

if __name__ == "__main__":
    main()
