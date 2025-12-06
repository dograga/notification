from pydantic import BaseModel, Field
from typing import List

class EmailGroupPayload(BaseModel):
    """Payload model for adding an email group"""
    appcode: str = Field(..., description="Application code")
    alert_type: str = Field(..., description="Type of alert")
    members: List[str] = Field(..., description="List of email addresses")
    addedby: str = Field(..., description="User who added the group")
    task_id: str = Field(..., description="Task ID associated with the approval")
