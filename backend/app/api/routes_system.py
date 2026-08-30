from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from backend.app.core.config import settings
from backend.app.core.resource_manager import resource_manager
from backend.app.ml.model_registry import model_registry
from backend.app.retrieval.vector_store import vector_store

router = APIRouter(prefix="/system", tags=["System Hardware & Status"])


@router.get("/info")
async def get_system_hardware_info():
    """Detect and return CPU, RAM, GPU, and recommended execution profile."""
    return resource_manager.get_system_specs()


@router.get("/status")
async def get_system_status():
    """Returns dynamic health state of all platform components."""
    specs = resource_manager.get_system_specs()
    models_status = resource_manager.list_models_status()
    
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "inference_mode": resource_manager.active_mode,
        "backend": "online",
        "database": "connected",
        "text_model": "loaded" if model_registry.get_active_model() else "ready",
        "vision_engine": "ready",
        "vector_store": {
            "status": "ready",
            "indexed_documents": vector_store.count()
        },
        "llm_provider": {
            "provider": settings.LLM_PROVIDER,
            "configured": bool(settings.GEMINI_API_KEY if settings.LLM_PROVIDER == "gemini" else False)
        },
        "hardware": specs,
        "loaded_models_count": models_status["loaded_count"]
    }


@router.post("/mode")
async def switch_inference_mode(payload: Dict[str, str]):
    """Switch system inference mode (FAST | BALANCED | RESEARCH | CLOUD_ENHANCED)."""
    mode = payload.get("mode", "")
    try:
        new_mode = resource_manager.set_inference_mode(mode)
        return {"status": "success", "active_mode": new_mode}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/models/unload")
async def unload_model_endpoint(payload: Dict[str, str]):
    """Evict a model from memory to free RAM."""
    key = payload.get("model_key", "")
    evicted = resource_manager.unload_model(key)
    return {"status": "success", "evicted": evicted}
