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

    async def get_project_environments(self, appcode: str) -> Dict[str, str]:
        """
        Get deployment environments for an appcode
        Returns: {"dev": "true/false", "uat": "true/false", "prod": "true/false"}
        """
        if not self.client:
            raise FirestoreError("Firestore client is not initialized")
            
        try:
            logger.info("Fetching project environments", appcode=appcode)
            projects_ref = self.client.collection("cloudresource_project")
            query = projects_ref.where("app_code", "==", appcode).stream()
            
            environments = {"dev": "false", "uat": "false", "prod": "false"}
            
            async for doc in query:
                data = doc.to_dict()
                env = data.get("environment", "").lower()
                if env in environments:
                    environments[env] = "true"
            
            return environments
        except Exception as e:
            logger.error("Failed to fetch project environments", error=str(e), appcode=appcode)
            raise FirestoreError(f"Failed to fetch project environments: {str(e)}")

# Global instance
firestore_service = FirestoreService()
