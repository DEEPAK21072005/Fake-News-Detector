import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings, BASE_DIR
from backend.app.core.logging_config import logger
from backend.app.core.error_handlers import (
    VeritasException,
    veritas_exception_handler,
    generic_exception_handler
)
from backend.app.database.database import init_database
from backend.app.api.api_router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    await init_database()
    logger.info(f"Server listening on http://{settings.HOST}:{settings.PORT}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title="VeritasAI API",
    description="Multimodal Fake News Detection & Evidence Verification Platform REST API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(VeritasException, veritas_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include All Routers
app.include_router(api_router)

# Health endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "service": settings.APP_NAME,
        "mode": settings.DEFAULT_INFERENCE_MODE,
        "version": "1.0.0"
    }

# Mount Uploads directory for image inspection
if settings.UPLOADS_PATH.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_PATH)), name="uploads")

# Mount frontend/dist if available to serve the complete Single Page Application
frontend_dist = BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_dist / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json") or full_path.startswith("uploads"):
            raise VeritasException(message=f"Endpoint '{full_path}' not found", status_code=404)
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    async def root_endpoint():
        return {
            "message": "Welcome to VeritasAI Multimodal Fake News Detection & Verification API",
            "docs_url": "/docs",
            "health_check": "/api/health"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
