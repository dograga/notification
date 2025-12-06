import pytest
from unittest.mock import MagicMock, patch
from firestore_service import FirestoreService, FirestoreError
from datetime import datetime

@pytest.fixture
def mock_firestore_client():
    with patch('google.cloud.firestore.Client') as mock_client:
        yield mock_client

def test_add_email_group_success(mock_firestore_client):
    # Setup
    service = FirestoreService()
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_snapshot = MagicMock()
    
    service.client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value = mock_doc_snapshot
    mock_doc_snapshot.exists = False
    
    # Execute
    result = pytest.mark.asyncio(service.add_email_group(
        appcode="TESTAPP",
        alert_type="CRITICAL",
        members=["test@example.com"],
        alert_type="CRITICAL",
        members=["test@example.com"],
        addedby="user@example.com",
        task_id="TASK-123"
    ))
    
    # Verify
    service.client.collection.assert_called_with("email_groups")
    mock_collection.document.assert_called_with("TESTAPP-CRITICAL")
    mock_doc_ref.set.assert_called()
    
    # Check set arguments
    call_args = mock_doc_ref.set.call_args[0][0]
    assert call_args["appcode"] == "TESTAPP"
    assert call_args["alert_type"] == "CRITICAL"
    assert call_args["members"] == ["test@example.com"]
    assert call_args["members"] == ["test@example.com"]
    assert call_args["addedby"] == "user@example.com"
    assert call_args["task_id"] == "TASK-123"
    assert "timestamp" in call_args

def test_add_email_group_already_exists(mock_firestore_client):
    # Setup
    service = FirestoreService()
    mock_collection = MagicMock()
    mock_doc_ref = MagicMock()
    mock_doc_snapshot = MagicMock()
    
    service.client.collection.return_value = mock_collection
    mock_collection.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value = mock_doc_snapshot
    mock_doc_snapshot.exists = True
    
    # Execute & Verify
    import asyncio
    
    async def run_test():
        with pytest.raises(ValueError) as excinfo:
            await service.add_email_group(
                appcode="TESTAPP",
                alert_type="CRITICAL",
                members=["test@example.com"],
                addedby="user@example.com"
            )
        assert "already exists" in str(excinfo.value)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_test())
    loop.close()

def test_add_email_group_firestore_error(mock_firestore_client):
    # Setup
    service = FirestoreService()
    mock_collection = MagicMock()
    
    service.client.collection.side_effect = Exception("Connection failed")
    
    # Execute & Verify
    import asyncio
    
    async def run_test():
        with pytest.raises(FirestoreError) as excinfo:
            await service.add_email_group(
                appcode="TESTAPP",
                alert_type="CRITICAL",
                members=["test@example.com"],
                addedby="user@example.com"
            )
        assert "Failed to add email group" in str(excinfo.value)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_test())
    loop.close()

if __name__ == "__main__":
    # Manual run if pytest not available or for quick check
    print("Running manual tests...")
    
    # Mocking for manual run
    with patch('google.cloud.firestore.Client') as mock_client:
        service = FirestoreService()
        
        # Test 1: Success
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_snapshot = MagicMock()
        
        service.client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        mock_doc_ref.get.return_value = mock_doc_snapshot
        mock_doc_snapshot.exists = False
        
        import asyncio
        loop = asyncio.new_event_loop()
        
        print("Test 1: Success case")
        result = loop.run_until_complete(service.add_email_group(
            appcode="TESTAPP",
            alert_type="CRITICAL",
            members=["test@example.com"],
            members=["test@example.com"],
            addedby="user@example.com",
            task_id="TASK-123"
        ))
        print("Result:", result)
        
        # Test 2: Exists
        print("\nTest 2: Exists case")
        mock_doc_snapshot.exists = True
        try:
            loop.run_until_complete(service.add_email_group(
                appcode="TESTAPP",
                alert_type="CRITICAL",
                members=["test@example.com"],
                members=["test@example.com"],
                addedby="user@example.com",
                task_id="TASK-123"
            ))
        except ValueError as e:
            print("Caught expected error:", e)
            
        loop.close()
