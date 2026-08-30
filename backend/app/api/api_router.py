from fastapi import APIRouter
from backend.app.api.routes_analyze import router as analyze_router
from backend.app.api.routes_datasets import router as datasets_router
from backend.app.api.routes_models import router as models_router
from backend.app.api.routes_evaluation import router as evaluation_router
from backend.app.api.routes_evidence import router as evidence_router
from backend.app.api.routes_experiments import router as experiments_router
from backend.app.api.routes_system import router as system_router

api_router = APIRouter(prefix="/api")

api_router.include_router(analyze_router)
api_router.include_router(datasets_router)
api_router.include_router(models_router)
api_router.include_router(evaluation_router)
api_router.include_router(evidence_router)
api_router.include_router(experiments_router)
api_router.include_router(system_router)
