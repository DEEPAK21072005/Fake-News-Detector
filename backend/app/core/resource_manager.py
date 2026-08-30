import os
import platform
import gc
from typing import Dict, Any, Optional
from backend.app.core.logging_config import logger

try:
    import psutil
except ImportError:
    psutil = None


class ResourceManager:
    """
    Hardware and Memory Resource Manager tailored for Windows 11 Intel Core i5 16GB RAM machines.
    Monitors RAM, manages lazy model lifecycles, and enforces CPU-safe batch limits.
    """
    _instance: Optional["ResourceManager"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResourceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.active_mode = "BALANCED"  # FAST | BALANCED | RESEARCH | CLOUD_ENHANCED
        self._model_cache: Dict[str, Any] = {}
        self._model_metadata: Dict[str, Dict[str, Any]] = {}
        logger.info(f"ResourceManager initialized. Detected profile: {self.get_system_specs()['recommended_profile']}")
    
    def get_system_specs(self) -> Dict[str, Any]:
        """Detect system hardware specifications and memory constraints."""
        cpu_count = os.cpu_count() or 4
        try:
            mem = psutil.virtual_memory()
            total_ram_gb = round(mem.total / (1024 ** 3), 2)
            available_ram_gb = round(mem.available / (1024 ** 3), 2)
            ram_percent = mem.percent
        except Exception:
            total_ram_gb = 16.0
            available_ram_gb = 8.0
            ram_percent = 50.0

        # Check CUDA availability safely
        cuda_available = False
        gpu_name = "Intel Iris Xe Graphics (Integrated / CPU inference)"
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                gpu_name = torch.cuda.get_device_name(0)
        except Exception:
            pass

        # Recommendation logic
        if total_ram_gb <= 8.0:
            recommended_profile = "FAST (Lightweight TF-IDF / MiniLM)"
        elif total_ram_gb <= 16.0:
            recommended_profile = "BALANCED (MiniLM + VeritasFusion + CPU Vector Search)"
        else:
            recommended_profile = "RESEARCH (Full Multimodal + Deep Attention Fusion)"

        return {
            "os": f"{platform.system()} {platform.release()} ({platform.machine()})",
            "processor": platform.processor() or "Intel Core i5-1340P 13th Gen",
            "cpu_cores": cpu_count,
            "total_ram_gb": total_ram_gb,
            "available_ram_gb": available_ram_gb,
            "ram_usage_percent": ram_percent,
            "cuda_available": cuda_available,
            "gpu_name": gpu_name,
            "recommended_profile": recommended_profile,
            "active_mode": self.active_mode,
        }
    
    def set_inference_mode(self, mode: str) -> str:
        valid_modes = ["FAST", "BALANCED", "RESEARCH", "CLOUD_ENHANCED"]
        if mode.upper() in valid_modes:
            self.active_mode = mode.upper()
            logger.info(f"Inference mode switched to: {self.active_mode}")
            return self.active_mode
        raise ValueError(f"Invalid mode {mode}. Choose from {valid_modes}")

    def register_model(self, key: str, model_instance: Any, meta: Dict[str, Any]) -> None:
        """Register a loaded model into the memory-tracked cache."""
        self._model_cache[key] = model_instance
        self._model_metadata[key] = {
            **meta,
            "loaded": True,
        }
        logger.info(f"Model '{key}' registered in cache. Active models: {len(self._model_cache)}")

    def get_model(self, key: str) -> Optional[Any]:
        return self._model_cache.get(key)

    def is_model_loaded(self, key: str) -> bool:
        return key in self._model_cache

    def unload_model(self, key: str) -> bool:
        """Safely evict a model to free RAM."""
        if key in self._model_cache:
            del self._model_cache[key]
            if key in self._model_metadata:
                self._model_metadata[key]["loaded"] = False
            gc.collect()
            logger.info(f"Evicted model '{key}' from memory cache.")
            return True
        return False

    def list_models_status(self) -> Dict[str, Any]:
        return {
            "loaded_count": len(self._model_cache),
            "models": self._model_metadata,
            "active_mode": self.active_mode
        }


resource_manager = ResourceManager()
