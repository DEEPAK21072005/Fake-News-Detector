import sys
import os
from pathlib import Path

# Add root directory to sys.path so backend imports work seamlessly on Vercel
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import FastAPI app from backend.app.main
from backend.app.main import app  # noqa: E402
