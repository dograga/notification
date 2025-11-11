"""
Test script for Teams Notification Service

Run this script to test sending notifications to Teams.
Make sure the service is running on http://localhost:8000
"""

import httpx
import asyncio
from typing import Dict, Any


async def test_simple_notification():
    """Test 1: Simple notification"""
    print("\n" + "="*60)
    print("Test 1: Simple Notification")
    print("="*60)
    
    payload = {
        "url": "https://example.com/deployment/123",
        "message": "Deployment to production completed successfully"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/notify",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Status: {result['status']}")
            print(f"✓ Message: {result['message']}")
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_success_notification():
    """Test 2: Success notification with details"""
    print("\n" + "="*60)
    print("Test 2: Success Notification with Details")
    print("="*60)
    
    payload = {
        "url": "https://dashboard.example.com/deployments/456",
        "message": "Application version 2.5.0 has been deployed to production",
        "title": "Deployment Success",
        "severity": "success",
        "additional_facts": {
            "Environment": "Production",
            "Version": "2.5.0",
            "Deployed By": "john.doe@example.com",
            "Duration": "5 minutes"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/notify",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Status: {result['status']}")
            print(f"✓ Timestamp: {result['timestamp']}")
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_error_alert():
    """Test 3: Error alert"""
    print("\n" + "="*60)
    print("Test 3: Error Alert")
    print("="*60)
    
    payload = {
        "url": "https://logs.example.com/errors/789",
        "message": "Critical error detected in payment processing service",
        "title": "Critical Error Alert",
        "severity": "error",
        "additional_facts": {
            "Service": "Payment Processing",
            "Error Code": "PAY-500",
            "Affected Users": "~150",
            "Time": "2024-01-15 10:30 UTC"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/notify",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Status: {result['status']}")
            print(f"✓ Severity: {result['payload']['severity']}")
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_warning_notification():
    """Test 4: Warning notification"""
    print("\n" + "="*60)
    print("Test 4: Warning Notification")
    print("="*60)
    
    payload = {
        "url": "https://monitoring.example.com/metrics",
        "message": "CPU usage has exceeded 80% threshold",
        "title": "Resource Warning",
        "severity": "warning",
        "additional_facts": {
            "Server": "prod-server-01",
            "CPU Usage": "85%",
            "Memory Usage": "72%",
            "Threshold": "80%"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/notify",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Status: {result['status']}")
            print(f"✓ Title: {result['payload']['title']}")
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_info_notification():
    """Test 5: Info notification"""
    print("\n" + "="*60)
    print("Test 5: Info Notification")
    print("="*60)
    
    payload = {
        "url": "https://example.com/pipeline/run/42",
        "message": "Data pipeline execution completed successfully",
        "title": "Pipeline Notification",
        "severity": "info",
        "additional_facts": {
            "Pipeline": "daily-etl-pipeline",
            "Records Processed": "1,234,567",
            "Duration": "45 minutes",
            "Status": "Success"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/notify",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Status: {result['status']}")
            print(f"✓ Message sent successfully")
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_health_check():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Test: Health Check")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/health",
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Status: {result['status']}")
            print(f"✓ Version: {result['version']}")
            print(f"✓ Teams Webhook Configured: {result['teams_webhook_configured']}")
            return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Teams Notification Service - Test Suite")
    print("="*60)
    print("\nPrerequisites:")
    print("1. Service is running on http://localhost:8000")
    print("2. TEAMS_WEBHOOK_URL is configured in .env.local")
    print("="*60)
    
    # Check if service is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code != 200:
                print("\n✗ Service is not responding correctly")
                print("  Please start the service with: uvicorn main:app --reload")
                return
    except Exception as e:
        print(f"\n✗ Cannot connect to service: {str(e)}")
        print("  Please start the service with: uvicorn main:app --reload")
        return
    
    # Run tests
    results = []
    
    results.append(await test_health_check())
    await asyncio.sleep(1)
    
    results.append(await test_simple_notification())
    await asyncio.sleep(1)
    
    results.append(await test_success_notification())
    await asyncio.sleep(1)
    
    results.append(await test_error_alert())
    await asyncio.sleep(1)
    
    results.append(await test_warning_notification())
    await asyncio.sleep(1)
    
    results.append(await test_info_notification())
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
    else:
        print(f"✗ {total - passed} test(s) failed")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
