import pytest
from unittest.mock import MagicMock, patch
from firestore_service import FirestoreService
from smtp_service import SmtpService

def test_group_email_flow():
    # Mocks
    mock_firestore = MagicMock()
    mock_smtp = MagicMock()
    
    # Setup Firestore Service
    with patch('google.cloud.firestore.Client') as mock_client:
        fs_service = FirestoreService()
        fs_service.client = mock_firestore
        
        # Mock get_email_group
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"members": ["test@example.com"]}
        mock_firestore.collection.return_value.document.return_value.get.return_value = mock_doc
        
        # Setup SMTP Service
        smtp_service = SmtpService()
        with patch('smtplib.SMTP') as mock_smtp_conn:
            
            # Execute Logic (Simulating Main Endpoint Logic)
            import asyncio
            loop = asyncio.new_event_loop()
            
            async def run_flow():
                # 1. Get Group
                group = await fs_service.get_email_group("APP", "ALERT")
                assert group["members"] == ["test@example.com"]
                
                # 2. Log Notification
                await fs_service.log_notification("APP", "ALERT", "user", "content", ["test@example.com"])
                mock_firestore.collection.assert_called_with("notification_logs")
                mock_firestore.collection.return_value.add.assert_called()
                
                # 3. Send Email
                # Need to patch settings to ensure host is present
                with patch('config.settings.smtp_host', 'smtp.test'):
                    smtp_service.send_email(["test@example.com"], "Subject", "Content")
                    mock_smtp_conn.assert_called()
            
            loop.run_until_complete(run_flow())
            loop.close()

if __name__ == "__main__":
    print("Running manual test...")
    test_group_email_flow()
    print("Test passed!")
