"""
FastAPI Notification Service

This service manages email groups in Firestore.
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
from smtp_service import smtp_service, SmtpError
from config import get_settings
from dataclass import EmailGroupPayload, MemberUpdatePayload, GroupEmailPayload

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
    title="Notification Service",
    description="Service for managing email groups",
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
        app_name="Notification Service",
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
        "service": "Notification Service",
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

# --- Email Group Endpoint ---
@app.post("/email-groups", tags=["Configuration"])
async def add_email_group(payload: EmailGroupPayload):
    """
    Add a new email group
    This endpoint adds a new email group configuration to Firestore.
    The group is uniquely identified by the combination of `appcode` and `alert_type`.
    """
    logger.info(
        "Received add email group request",
        appcode=payload.appcode,
        alert_type=payload.alert_type,
        members_count=len(payload.members)
    )
    
    try:
        result = await firestore_service.add_email_group(
            appcode=payload.appcode,
            alert_type=payload.alert_type,
            members=payload.members,
            addedby=payload.addedby,
            task_id=payload.task_id
        )
        
        return {
            "status": "success",
            "message": "Email group added successfully",
            "data": result
        }
        
    except ValueError as e:
        logger.warning(
            "Email group already exists",
            error=str(e)
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
    except FirestoreError as e:
        logger.error(
            "Failed to add email group",
            error=str(e)
        )
        raise HTTPException(
            status_code=502,
            detail=f"Failed to add email group: {str(e)}"
        )
    
    except Exception as e:
        logger.error(
            "Unexpected error adding email group",
            error=str(e),
            traceback=traceback.format_exc()
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/email-groups/members/add", tags=["Configuration"])
async def add_members(payload: MemberUpdatePayload):
    """
    Add members to an email group
    """
    try:
        result = await firestore_service.add_members(
            appcode=payload.appcode,
            alert_type=payload.alert_type,
            members=payload.members
        )
        return {"status": "success", "message": "Members added successfully", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email-groups/members/remove", tags=["Configuration"])
async def remove_members(payload: MemberUpdatePayload):
    """
    Remove members from an email group
    """
    try:
        result = await firestore_service.remove_members(
            appcode=payload.appcode,
            alert_type=payload.alert_type,
            members=payload.members
        )
        return {"status": "success", "message": "Members removed successfully", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notify/group", tags=["Notifications"])
async def send_group_email(payload: GroupEmailPayload):
    """
    Trigger an email to a group
    """
    try:
        # 1. Check if group exists and get members
        group = await firestore_service.get_email_group(payload.appcode, payload.alert_type)
        if not group:
            raise HTTPException(status_code=404, detail=f"Email group {payload.appcode}-{payload.alert_type} not found")
            
        members = group.get("members", [])
        if not members:
             raise HTTPException(status_code=400, detail="Group has no members")

        # 2. Log notification
        await firestore_service.log_notification(
            appcode=payload.appcode,
            alert_type=payload.alert_type,
            requestedby=payload.requestedby,
            email_content=payload.email_content,
            recipients=members
        )
        
        # 3. Send email
        smtp_service.send_email(
            to_emails=members,
            subject=f"Alert: {payload.appcode} - {payload.alert_type}",
            content=payload.email_content
        )
        
        return {
            "status": "success", 
            "message": "Email sent successfully", 
            "recipients_count": len(members)
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error("Failed to process group email", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# --- Application Info ---
logger.info(
    "FastAPI application configured",
    title=app.title,
    version=app.version,
    debug=app.debug,
    docs_enabled=app.docs_url is not None
)
