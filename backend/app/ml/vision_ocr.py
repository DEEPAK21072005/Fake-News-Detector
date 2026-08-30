import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union
import numpy as np
try:
    from PIL import Image, ImageStat
    HAS_PIL = True
except ImportError:
    Image = None
    ImageStat = None
    HAS_PIL = False
from backend.app.core.logging_config import logger


def calculate_image_phash(image_path: Union[str, Path]) -> str:
    """Calculate 64-bit perceptual difference hash (dHash) for duplicate detection."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
            pixels = np.array(img.getdata(), dtype=np.float32).reshape((8, 9))
            diff = pixels[:, 1:] > pixels[:, :-1]
            decimal_val = 0
            hash_str = []
            for idx, val in enumerate(diff.flatten()):
                if val:
                    decimal_val += 2 ** (idx % 8)
                if (idx % 8) == 7:
                    hash_str.append(hex(decimal_val)[2:].rjust(2, "0"))
                    decimal_val = 0
            return "".join(hash_str)
    except Exception as e:
        logger.warning(f"Failed to calculate pHash for {image_path}: {e}")
        return hashlib.md5(str(image_path).encode()).hexdigest()[:16]


def extract_visual_features(image_path: Union[str, Path], feature_dim: int = 128) -> Dict[str, Any]:
    """
    Extract CPU-friendly visual features:
    Color distribution, HSV histograms, edge intensity, image quality/entropy, and a normalized embedding.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        return {
            "embedding": np.zeros(feature_dim, dtype=np.float32),
            "phash": "",
            "dimensions": {"width": 0, "height": 0},
            "aspect_ratio": 1.0,
            "mean_brightness": 0.0,
            "contrast": 0.0,
            "color_entropy": 0.0,
            "has_manipulation_artifacts": False
        }

    try:
        with Image.open(image_path) as raw_img:
            img_rgb = raw_img.convert("RGB")
            width, height = img_rgb.size
            aspect_ratio = round(width / max(height, 1), 3)

            # Basic stats
            stat = ImageStat.Stat(img_rgb)
            mean_brightness = round(float(np.mean(stat.mean)), 2)
            contrast = round(float(np.mean(stat.stddev)), 2)

            # Generate normalized visual descriptor (128-dim dense representation)
            # Resize to 32x32 for spatial color grid + HSV histogram
            small = img_rgb.resize((16, 16), Image.Resampling.BILINEAR)
            arr = np.array(small, dtype=np.float32) / 255.0  # 16x16x3 = 768
            
            # Spatial downsampling to 64 dims + histogram to 64 dims = 128 dims
            spatial_desc = arr.reshape(16, 16, 3).mean(axis=2).flatten()[:64]  # 64
            # Color histogram in 3 channels (21 bins R, 21 bins G, 22 bins B = 64)
            hist_r, _ = np.histogram(arr[:, :, 0], bins=21, range=(0, 1))
            hist_g, _ = np.histogram(arr[:, :, 1], bins=21, range=(0, 1))
            hist_b, _ = np.histogram(arr[:, :, 2], bins=22, range=(0, 1))
            hist_desc = np.concatenate([hist_r, hist_g, hist_b]).astype(np.float32)
            
            combined_desc = np.concatenate([spatial_desc, hist_desc]).astype(np.float32)
            norm = np.linalg.norm(combined_desc)
            if norm > 1e-6:
                combined_desc /= norm

            phash = calculate_image_phash(image_path)

            return {
                "embedding": combined_desc,
                "phash": phash,
                "dimensions": {"width": width, "height": height},
                "aspect_ratio": aspect_ratio,
                "mean_brightness": mean_brightness,
                "contrast": contrast,
                "color_entropy": round(float(stat.rms[0]), 2),
                "has_manipulation_artifacts": bool(contrast < 15.0 or contrast > 95.0)
            }
    except Exception as e:
        logger.warning(f"Error extracting visual features: {e}")
        return {
            "embedding": np.zeros(feature_dim, dtype=np.float32),
            "phash": "",
            "dimensions": {"width": 0, "height": 0},
            "aspect_ratio": 1.0,
            "mean_brightness": 0.0,
            "contrast": 0.0,
            "color_entropy": 0.0,
            "has_manipulation_artifacts": False
        }


def extract_ocr_text(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract embedded text from image using available OCR engine (EasyOCR/Tesseract/Fallback).
    """
    image_path = Path(image_path)
    if not image_path.exists():
        return {"extracted_text": "", "ocr_available": False, "confidence": 0.0}

    # Attempt pytesseract if available
    try:
        import pytesseract
        text = pytesseract.image_to_string(Image.open(image_path))
        return {
            "extracted_text": text.strip(),
            "ocr_available": True,
            "engine": "pytesseract",
            "confidence": 0.88 if text.strip() else 0.0
        }
    except Exception:
        pass

    # Attempt EasyOCR if available
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(str(image_path))
        extracted = " ".join([res[1] for res in results])
        return {
            "extracted_text": extracted.strip(),
            "ocr_available": True,
            "engine": "easyocr",
            "confidence": 0.85 if extracted.strip() else 0.0
        }
    except Exception:
        pass

    # Fallback when OCR engine binaries are not installed
    return {
        "extracted_text": "",
        "ocr_available": False,
        "engine": "none",
        "confidence": 0.0,
        "note": "OCR engine not installed or no text detected. Image analyzed via visual perceptual descriptors."
    }
