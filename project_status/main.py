"""
FastAPI Project Status Service

This service manages application deployment environments in Firestore.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from firestore_service import firestore_service, FirestoreError
from config import get_settings

# --- Configuration ---
settings = get_settings()

# --- Logging Configuration ---
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = structlog.get_logger()

# --- FastAPI App Configuration ---
app = FastAPI(
    title="Project Status Service",
    description="Service for managing application deployment environments",
    version="1.0.0",
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Custom Exception Handler ---
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unexpected Error",
        error=str(exc),
        traceback=traceback.format_exc(),
        path=request.url.path,
        method=request.method
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "status_code": 500,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    logger.info(
        "Application startup",
        app_name="Project Status Service",
        version="1.0.0",
        environment=settings.environment
    )

# --- Shutdown Event ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

# --- Root Endpoint ---
@app.get("/", tags=["General"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Project Status Service",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "docs_url": "/docs" if settings.debug else "disabled",
        "timestamp": datetime.utcnow().isoformat()
    }

# --- Health Check Endpoint ---
@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment
    }

@app.get("/projects/environments", tags=["Projects"])
async def get_project_environments(appcode: str):
    """
    Get deployment environments for an application
    """
    try:
        environments = await firestore_service.get_project_environments(appcode)
        return environments
    except FirestoreError as e:
        logger.error("Failed to fetch project environments", error=str(e), appcode=appcode)
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error fetching project environments", error=str(e), appcode=appcode)
        raise HTTPException(status_code=500, detail=str(e))

# --- Application Info ---
logger.info(
    "FastAPI application configured",
    title=app.title,
    version=app.version,
    debug=app.debug,
    docs_enabled=app.docs_url is not None
)
