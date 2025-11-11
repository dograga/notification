"""
Microsoft Teams Notification Service

This module provides functionality to send notifications to Microsoft Teams channels
via incoming webhooks.
"""

import httpx
import structlog
from typing import Optional, Dict, Any
from datetime import datetime
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class TeamsNotificationError(Exception):
    """Custom exception for Teams notification errors"""
    pass


class TeamsNotificationService:
    """Service for sending notifications to Microsoft Teams channels"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Teams notification service
        
        Args:
            webhook_url: Microsoft Teams incoming webhook URL
                        If not provided, will use TEAMS_WEBHOOK_URL from settings
        """
        self.webhook_url = webhook_url or getattr(settings, 'teams_webhook_url', None)
        
        if not self.webhook_url:
            logger.warning("Teams webhook URL not configured")
    
    async def send_notification(
        self, 
        message: str, 
        url: Optional[str] = None,
        title: Optional[str] = None,
        color: str = "0078D4",
        additional_facts: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send a notification to Microsoft Teams channel
        
        Args:
            message: The main message content
            url: Optional URL to include in the notification
            title: Optional title for the notification (defaults to "Notification")
            color: Hex color code for the message card (default: Microsoft Blue)
            additional_facts: Optional dictionary of additional facts to display
            
        Returns:
            Dict containing the response status and details
            
        Raises:
            TeamsNotificationError: If the notification fails to send
        """
        if not self.webhook_url:
            error_msg = "Teams webhook URL is not configured"
            logger.error(error_msg)
            raise TeamsNotificationError(error_msg)
        
        # Build the message card payload
        card = self._build_message_card(
            message=message,
            url=url,
            title=title or "Notification",
            color=color,
            additional_facts=additional_facts
        )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=card,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                
                logger.info(
                    "Teams notification sent successfully",
                    status_code=response.status_code,
                    title=title,
                    message_preview=message[:100]
                )
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "message": "Notification sent successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error sending Teams notification: {e.response.status_code}"
            logger.error(
                error_msg,
                status_code=e.response.status_code,
                response_text=e.response.text
            )
            raise TeamsNotificationError(error_msg) from e
            
        except httpx.RequestError as e:
            error_msg = f"Request error sending Teams notification: {str(e)}"
            logger.error(error_msg, error=str(e))
            raise TeamsNotificationError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error sending Teams notification: {str(e)}"
            logger.error(error_msg, error=str(e))
            raise TeamsNotificationError(error_msg) from e
    
    def _build_message_card(
        self,
        message: str,
        url: Optional[str],
        title: str,
        color: str,
        additional_facts: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Build a Microsoft Teams message card payload
        
        Args:
            message: The main message content
            url: Optional URL to include
            title: Title for the card
            color: Hex color code
            additional_facts: Additional facts to display
            
        Returns:
            Dict containing the message card structure
        """
        # Base card structure
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": color,
            "title": title,
            "text": message,
            "sections": []
        }
        
        # Add facts section if we have URL or additional facts
        facts = []
        
        if url:
            facts.append({
                "name": "URL",
                "value": url
            })
        
        if additional_facts:
            for key, value in additional_facts.items():
                facts.append({
                    "name": key,
                    "value": str(value)
                })
        
        if facts:
            card["sections"].append({
                "facts": facts
            })
        
        # Add timestamp
        card["sections"].append({
            "facts": [{
                "name": "Timestamp",
                "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }]
        })
        
        # Add potential actions if URL is provided
        if url:
            card["potentialAction"] = [{
                "@type": "OpenUri",
                "name": "View Details",
                "targets": [{
                    "os": "default",
                    "uri": url
                }]
            }]
        
        return card


# Singleton instance
teams_notification_service = TeamsNotificationService()
