import structlog
from datetime import datetime
from typing import List, Optional, Dict, Any
from google.cloud import firestore
from google.api_core import exceptions
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

class FirestoreError(Exception):
    """Base exception for Firestore errors"""
    pass

class FirestoreService:
    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Firestore client"""
        try:
            project_id = settings.firestore_project_id
            db_name = settings.firestore_db_name
            
            if project_id:
                self.client = firestore.Client(project=project_id, database=db_name)
            else:
                # Attempt to use default credentials/project
                self.client = firestore.Client(database=db_name)
            
            logger.info("Firestore client initialized", project=self.client.project, database=db_name)
        except Exception as e:
            logger.error("Failed to initialize Firestore client", error=str(e))
            self.client = None

    async def add_email_group(
        self, 
        appcode: str, 
        alert_type: str, 
        members: List[str], 
        addedby: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Add a new email group to Firestore.
        
        Args:
            appcode: Application code
            alert_type: Type of alert
            members: List of email addresses
            addedby: User who added the group
            task_id: Task ID associated with the approval
            
        Returns:
            Dict containing the created record data
            
        Raises:
            FirestoreError: If operation fails
            ValueError: If group already exists
        """
        if not self.client:
            raise FirestoreError("Firestore client is not initialized")

        # Create unique ID
        doc_id = f"{appcode}-{alert_type}"
        collection_name = settings.firestore_email_groups_collection
        
        try:
            doc_ref = self.client.collection(collection_name).document(doc_id)
            
            # Check if document exists
            doc = doc_ref.get()
            if doc.exists:
                raise ValueError(f"Email group for {appcode} and {alert_type} already exists. Please add members to the existing group.")
            
            # Create new document
            data = {
                "appcode": appcode,
                "alert_type": alert_type,
                "members": members,
                "addedby": addedby,
                "task_id": task_id,
                "timestamp": datetime.utcnow()
            }
            
            doc_ref.set(data)
            
            logger.info(
                "Email group added successfully",
                appcode=appcode,
                alert_type=alert_type,
                doc_id=doc_id
            )
            
            return data
            
        except ValueError as ve:
            logger.warning("Email group already exists", doc_id=doc_id)
            raise ve
        except Exception as e:
            logger.error(
                "Failed to add email group",
                error=str(e),
                appcode=appcode,
                alert_type=alert_type
            )
            raise FirestoreError(f"Failed to add email group: {str(e)}")

    async def add_members(self, appcode: str, alert_type: str, members: List[str]) -> Dict[str, Any]:
        """Add members to an existing email group"""
        if not self.client:
            raise FirestoreError("Firestore client is not initialized")
            
        doc_id = f"{appcode}-{alert_type}"
        collection_name = settings.firestore_email_groups_collection
        
        try:
            doc_ref = self.client.collection(collection_name).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise ValueError(f"Email group for {appcode} and {alert_type} does not exist")
                
            doc_ref.update({
                "members": firestore.ArrayUnion(members)
            })
            
            logger.info("Members added successfully", appcode=appcode, alert_type=alert_type, count=len(members))
            return {"appcode": appcode, "alert_type": alert_type, "added_members": members}
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            logger.error("Failed to add members", error=str(e))
            raise FirestoreError(f"Failed to add members: {str(e)}")

    async def remove_members(self, appcode: str, alert_type: str, members: List[str]) -> Dict[str, Any]:
        """Remove members from an existing email group"""
        if not self.client:
            raise FirestoreError("Firestore client is not initialized")
            
        doc_id = f"{appcode}-{alert_type}"
        collection_name = settings.firestore_email_groups_collection
        
        try:
            doc_ref = self.client.collection(collection_name).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise ValueError(f"Email group for {appcode} and {alert_type} does not exist")
                
            doc_ref.update({
                "members": firestore.ArrayRemove(members)
            })
            
            logger.info("Members removed successfully", appcode=appcode, alert_type=alert_type, count=len(members))
            return {"appcode": appcode, "alert_type": alert_type, "removed_members": members}
            
        except ValueError as ve:
            raise ve
        except Exception as e:
            logger.error("Failed to remove members", error=str(e))
            raise FirestoreError(f"Failed to remove members: {str(e)}")

    async def get_email_group(self, appcode: str, alert_type: str) -> Dict[str, Any]:
        """Get email group details"""
        if not self.client:
            raise FirestoreError("Firestore client is not initialized")
            
        doc_id = f"{appcode}-{alert_type}"
        collection_name = settings.firestore_email_groups_collection
        
        try:
            doc_ref = self.client.collection(collection_name).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
                
            return doc.to_dict()
            
        except Exception as e:
            logger.error("Failed to get email group", error=str(e))
            raise FirestoreError(f"Failed to get email group: {str(e)}")

    async def log_notification(self, appcode: str, alert_type: str, requestedby: str, email_content: str, recipients: List[str]):
        """Log notification details"""
        if not self.client:
            raise FirestoreError("Firestore client is not initialized")
            
        collection_name = settings.firestore_notification_logs_collection
        
        try:
            data = {
                "appcode": appcode,
                "alert_type": alert_type,
                "requestedby": requestedby,
                "email_content": email_content,
                "recipients": recipients,
                "timestamp": datetime.utcnow()
            }
            
            self.client.collection(collection_name).add(data)
            logger.info("Notification logged successfully", appcode=appcode, alert_type=alert_type)
            
        except Exception as e:
            logger.error("Failed to log notification", error=str(e))
            # Don't raise error here to avoid failing the main request if logging fails? 
            # User requirement says "record these details", so maybe we should raise or just log error.
            # I'll log error but allow flow to continue or raise? 
            # Usually logging failure shouldn't stop the email, but requirement implies it's part of the process.
            # I will raise FirestoreError to be safe and ensure data integrity as per "record these details".
            raise FirestoreError(f"Failed to log notification: {str(e)}")

# Global instance
firestore_service = FirestoreService()
