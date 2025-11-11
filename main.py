"""
FastAPI Notification Service

This service receives webhook payloads and forwards notifications to Microsoft Teams channels and Email.
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

from teams_service import teams_notification_service, TeamsNotificationError
from email_service import email_notification_service, EmailNotificationError
from config import get_settings

# --- Request Models ---
class NotificationPayload(BaseModel):
    """Payload model for Teams notification webhook"""
    url: str = Field(..., description="URL to include in the notification")
    message: str = Field(..., description="The notification message content")
    title: Optional[str] = Field(None, description="Optional title for the notification")
    severity: Optional[str] = Field("info", description="Severity level: info, warning, error, success")
    additional_facts: Optional[Dict[str, str]] = Field(None, description="Additional key-value pairs to display")

class EmailPayload(BaseModel):
    """Payload model for Email notification"""
    to_emails: List[str] = Field(..., description="List of recipient email addresses")
    subject: str = Field(..., description="Email subject")
    message: str = Field(..., description="Email message content")
    cc_emails: Optional[List[str]] = Field(None, description="Optional CC recipients")
    bcc_emails: Optional[List[str]] = Field(None, description="Optional BCC recipients")
    html_message: Optional[str] = Field(None, description="Optional HTML version of the message")
    url: Optional[str] = Field(None, description="Optional URL to include in the email")
    additional_info: Optional[Dict[str, str]] = Field(None, description="Additional information to include")

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
    description="Webhook service for forwarding notifications to Microsoft Teams channels and Email",
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
        app_name="Teams Notification Service",
        version="1.0.0",
        environment=settings.environment,
        teams_webhook_configured=bool(settings.teams_webhook_url)
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
        "service": "Teams Notification Service",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "teams_webhook_configured": bool(settings.teams_webhook_url),
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
        "environment": settings.environment,
        "teams_webhook_configured": bool(settings.teams_webhook_url)
    }

# --- Teams Notification Endpoint ---
@app.post("/notify", tags=["Notifications"])
async def send_teams_notification(payload: NotificationPayload):
    """
    Send a notification to Microsoft Teams channel
    
    This endpoint receives a webhook payload and forwards the message to a configured Teams channel.
    
    **Payload Structure:**
    - `url`: URL to include in the notification (required)
    - `message`: The message content to send (required)
    - `title`: Optional title for the notification
    - `severity`: Optional severity level (info, warning, error, success) - defaults to "info"
    - `additional_facts`: Optional dictionary of additional key-value pairs to display
    
    **Example Payload:**
    ```json
    {
        "url": "https://example.com/details",
        "message": "Deployment completed successfully",
        "title": "Deployment Notification",
        "severity": "success",
        "additional_facts": {
            "Environment": "Production",
            "Version": "1.2.3"
        }
    }
    ```
    """
    logger.info(
        "Received Teams notification request",
        message_preview=payload.message[:100],
        url=payload.url,
        severity=payload.severity
    )
    
    try:
        # Send notification to Teams
        result = await teams_notification_service.send_notification(
            message=payload.message,
            url=payload.url,
            title=payload.title,
            color=_get_severity_color(payload.severity),
            additional_facts=payload.additional_facts
        )
        
        logger.info(
            "Teams notification sent successfully",
            result=result
        )
        
        return {
            "status": "success",
            "message": "Notification sent to Teams channel",
            "details": result,
            "payload": {
                "url": payload.url,
                "message": payload.message,
                "title": payload.title,
                "severity": payload.severity
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except TeamsNotificationError as e:
        logger.error(
            "Failed to send Teams notification",
            error=str(e)
        )
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send Teams notification: {str(e)}"
        )
    
    except Exception as e:
        logger.error(
            "Unexpected error sending Teams notification",
            error=str(e),
            traceback=traceback.format_exc()
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def _get_severity_color(severity: Optional[str]) -> str:
    """Get hex color code based on severity level"""
    color_map = {
        "info": "0078D4",      # Blue
        "warning": "FFA500",   # Orange
        "error": "D13438",     # Red
        "success": "28A745"    # Green
    }
    return color_map.get(severity.lower() if severity else "info", "0078D4")

# --- Email Notification Endpoint ---
@app.post("/notify/email", tags=["Notifications"])
async def send_email_notification(payload: EmailPayload):
    """
    Send an email notification via SMTP
    
    This endpoint receives an email payload and forwards it to the configured SMTP server.
    
    **Payload Structure:**
    - `to_emails`: List of recipient email addresses (required)
    - `subject`: Email subject (required)
    - `message`: Email message content (required)
    - `cc_emails`: Optional list of CC recipients
    - `bcc_emails`: Optional list of BCC recipients
    - `html_message`: Optional HTML version of the message
    - `url`: Optional URL to include in the email
    - `additional_info`: Optional dictionary of additional information
    
    **Example Payload:**
    ```json
    {
        "to_emails": ["user@example.com"],
        "subject": "Deployment Notification",
        "message": "Deployment completed successfully",
        "url": "https://example.com/deployment/123",
        "additional_info": {
            "Environment": "Production",
            "Version": "1.2.3"
        }
    }
    ```
    """
    logger.info(
        "Received email notification request",
        to=payload.to_emails,
        subject=payload.subject,
        cc=payload.cc_emails,
        bcc_count=len(payload.bcc_emails) if payload.bcc_emails else 0
    )
    
    try:
        # Send email
        result = await email_notification_service.send_email(
            to_emails=payload.to_emails,
            subject=payload.subject,
            message=payload.message,
            cc_emails=payload.cc_emails,
            bcc_emails=payload.bcc_emails,
            html_message=payload.html_message,
            url=payload.url,
            additional_info=payload.additional_info
        )
        
        logger.info(
            "Email notification sent successfully",
            result=result
        )
        
        return {
            "status": "success",
            "message": "Email sent successfully",
            "details": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except EmailNotificationError as e:
        logger.error(
            "Failed to send email notification",
            error=str(e)
        )
        raise HTTPException(
            status_code=502,
            detail=f"Failed to send email notification: {str(e)}"
        )
    
    except Exception as e:
        logger.error(
            "Unexpected error sending email notification",
            error=str(e),
            traceback=traceback.format_exc()
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# --- Application Info ---
logger.info(
    "FastAPI application configured",
    title=app.title,
    version=app.version,
    debug=app.debug,
    docs_enabled=app.docs_url is not None
)
