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
            if settings.firestore_project_id:
                self.client = firestore.Client(project=settings.firestore_project_id)
            else:
                # Attempt to use default credentials/project
                self.client = firestore.Client()
            
            logger.info("Firestore client initialized", project=self.client.project)
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
        collection_name = "email_groups"
        
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

# Global instance
firestore_service = FirestoreService()
