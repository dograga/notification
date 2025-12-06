# Notification Service

A FastAPI-based webhook service that receives notification payloads and forwards them to Microsoft Teams channels and Email via SMTP.

## Features

- 🚀 Fast and lightweight FastAPI application
- 📢 Forward notifications to Microsoft Teams channels
- 📧 Send email notifications via SMTP
- 🎨 Support for different severity levels (info, warning, error, success)
- 📊 Rich message cards with custom fields
- 🔗 Clickable URLs in notifications
- 📝 Comprehensive logging with structlog
- 🐛 Debug mode with interactive API documentation
- 🎯 Multiple recipients support (To, CC, BCC)

## Prerequisites

- Python 3.8 or higher
- Microsoft Teams incoming webhook URL (for Teams notifications)
- SMTP server credentials (for email notifications)
- pip or uv for package management

## Quick Start

### 1. Clone or Download

```bash
cd C:\Users\gaura\Downloads\repo\notification
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

### 3. Configure Notification Channels

**For Teams Notifications:**
1. Open Microsoft Teams
2. Navigate to the channel where you want to receive notifications
3. Click on the three dots (...) next to the channel name
4. Select **Connectors** or **Workflows**
5. Search for **Incoming Webhook**
6. Configure the webhook and copy the webhook URL

**For Email Notifications:**
1. Obtain SMTP server credentials (Gmail, Outlook, or custom SMTP)
2. For Gmail: Generate an App Password (see [EMAIL_SETUP.md](EMAIL_SETUP.md))

### 4. Set Environment Variables

Copy the example environment file:

```bash
copy .env.example .env.local
```

Edit `.env.local` and configure your notification channels:

```bash
# Teams Configuration
TEAMS_WEBHOOK_URL=https://your-org.webhook.office.com/webhookb2/your-webhook-url

# Email/SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Notification Service
```

### 5. Run the Service

```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Or specify environment
$env:ENVIRONMENT="local"
uvicorn main:app --reload --port 8000
```

The service will be available at: `http://localhost:8000`

## API Documentation

Once the service is running in debug mode, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### POST `/notify` - Teams Notification

Send a notification to Microsoft Teams channel.

**Request Body:**

```json
{
  "url": "https://example.com/details",
  "message": "Your notification message",
  "title": "Optional Title",
  "severity": "info",
  "additional_facts": {
    "Key1": "Value1",
    "Key2": "Value2"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | URL to include in the notification |
| `message` | string | Yes | The notification message |
| `title` | string | No | Title for the notification |
| `severity` | string | No | Severity: `info`, `warning`, `error`, `success` (default: `info`) |
| `additional_facts` | object | No | Additional key-value pairs to display |

**Severity Colors:**
- `info`: Blue (#0078D4)
- `warning`: Orange (#FFA500)
- `error`: Red (#D13438)
- `success`: Green (#28A745)

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Notification sent to Teams channel",
  "details": {
    "success": true,
    "status_code": 200,
    "message": "Notification sent successfully",
    "timestamp": "2024-01-15T10:30:00.000000"
  },
  "payload": {
    "url": "https://example.com/details",
    "message": "Your notification message",
    "title": "Optional Title",
    "severity": "info"
  },
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

**Error Response (502):**

```json
{
  "detail": "Failed to send Teams notification: HTTP error sending Teams notification: 400"
}
```

### POST `/notify/email` - Email Notification

Send an email notification via SMTP.

**Request Body:**

```json
{
  "to_emails": ["user@example.com"],
  "subject": "Deployment Notification",
  "message": "Deployment completed successfully",
  "cc_emails": ["manager@example.com"],
  "url": "https://example.com/deployment/123",
  "additional_info": {
    "Environment": "Production",
    "Version": "1.2.3"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to_emails` | array | Yes | List of recipient email addresses |
| `subject` | string | Yes | Email subject |
| `message` | string | Yes | Email message content |
| `cc_emails` | array | No | Optional CC recipients |
| `bcc_emails` | array | No | Optional BCC recipients |
| `html_message` | string | No | Custom HTML version |
| `url` | string | No | URL to include in email |
| `additional_info` | object | No | Additional information |

For detailed email setup instructions, see [EMAIL_SETUP.md](EMAIL_SETUP.md).

### GET `/`

Root endpoint with service information.

### GET `/health`

Health check endpoint.

## Usage Examples

### Teams Notifications

#### Example 1: Simple Teams Notification

```bash
curl -X POST "http://localhost:8000/notify" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://example.com/deployment/123\", \"message\": \"Deployment completed successfully\"}"
```

#### Example 2: Success Notification with Details

```bash
curl -X POST "http://localhost:8000/notify" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://dashboard.example.com/deployments/456\", \"message\": \"Application version 2.5.0 deployed to production\", \"title\": \"Deployment Success\", \"severity\": \"success\", \"additional_facts\": {\"Environment\": \"Production\", \"Version\": \"2.5.0\"}}"
```

### Email Notifications

#### Example 1: Simple Email

```bash
curl -X POST "http://localhost:8000/notify/email" \
  -H "Content-Type: application/json" \
  -d "{\"to_emails\": [\"user@example.com\"], \"subject\": \"Test Notification\", \"message\": \"This is a test email\"}"
```

#### Example 2: Email with CC and Additional Info

```bash
curl -X POST "http://localhost:8000/notify/email" \
  -H "Content-Type: application/json" \
  -d "{\"to_emails\": [\"user@example.com\"], \"cc_emails\": [\"manager@example.com\"], \"subject\": \"Deployment Success\", \"message\": \"Application deployed to production\", \"url\": \"https://example.com/deployment/123\", \"additional_info\": {\"Environment\": \"Production\", \"Version\": \"1.2.3\"}}"
```

### Python Examples

#### Teams Notification

```python
import httpx
import asyncio

async def send_notification():
    url = "http://localhost:8000/notify"
    payload = {
        "url": "https://example.com/task/123",
        "message": "Task execution completed",
        "title": "Task Notification",
        "severity": "success",
        "additional_facts": {
            "Task ID": "task-123",
            "Status": "Completed",
            "Duration": "2 minutes"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        print(response.json())

asyncio.run(send_notification())
```

#### Email Notification

```python
import httpx
import asyncio

async def send_email():
    url = "http://localhost:8000/notify/email"
    payload = {
        "to_emails": ["user@example.com"],
        "subject": "Pipeline Completed",
        "message": "Data pipeline execution completed successfully",
        "url": "https://example.com/pipeline/run/42",
        "additional_info": {
            "Pipeline": "daily-etl-pipeline",
            "Records": "1,234,567",
            "Duration": "45 minutes"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        print(response.json())

asyncio.run(send_email())
```

### PowerShell Examples

#### Teams Notification

```powershell
$body = @{
    url = "https://example.com/details"
    message = "Deployment completed"
    title = "Deployment Notification"
    severity = "success"
    additional_facts = @{
        Environment = "Production"
        Version = "1.0.0"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/notify" -Method Post -Body $body -ContentType "application/json"
```

#### Email Notification

```powershell
$body = @{
    to_emails = @("user@example.com")
    subject = "Deployment Notification"
    message = "Deployment completed successfully"
    url = "https://example.com/deployment/123"
    additional_info = @{
        Environment = "Production"
        Version = "1.0.0"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/notify/email" -Method Post -Body $body -ContentType "application/json"
```

## Integration with Pub/Sub

### Google Cloud Pub/Sub Example

```python
from google.cloud import pubsub_v1
import httpx
import json

def callback(message):
    """Process Pub/Sub message and forward to Teams"""
    data = json.loads(message.data.decode('utf-8'))
    
    # Forward to Teams notification service
    payload = {
        "url": data.get("url", ""),
        "message": data.get("message", ""),
        "title": data.get("title", "Pub/Sub Notification"),
        "severity": data.get("severity", "info")
    }
    
    response = httpx.post(
        "http://localhost:8000/notify",
        json=payload
    )
    
    if response.status_code == 200:
        message.ack()
    else:
        message.nack()

# Subscribe to topic
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('project-id', 'subscription-name')
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

print(f"Listening for messages on {subscription_path}...")
streaming_pull_future.result()
```

## Project Structure

```
notification/
├── main.py                 # FastAPI application
├── teams_service.py        # Teams notification service
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.local            # Local environment config
├── .env.example          # Example environment config
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name (local, production) | `local` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `RELOAD` | Auto-reload on code changes | `false` |
| `TEAMS_WEBHOOK_URL` | Microsoft Teams webhook URL | `None` |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

## Troubleshooting

### Common Issues

**1. "Teams webhook URL is not configured"**
- Ensure `TEAMS_WEBHOOK_URL` is set in `.env.local`
- Restart the service after updating environment variables

**2. HTTP 400 Bad Request from Teams**
- Verify the webhook URL is correct
- Check if the webhook is still active in Teams
- Ensure the message card format is valid

**3. Connection Errors**
- Check your internet connectivity
- Verify firewall settings
- Ensure the Teams webhook URL is accessible

**4. Module Import Errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## Development

### Running in Development Mode

```bash
# Set environment
$env:ENVIRONMENT="local"

# Run with auto-reload
uvicorn main:app --reload --port 8000
```

### Testing the Service

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test notification endpoint
curl -X POST "http://localhost:8000/notify" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://example.com\", \"message\": \"Test message\"}"
```

### Using a Test Webhook

For testing without a real Teams webhook, use services like:
- [webhook.site](https://webhook.site)
- [requestbin.com](https://requestbin.com)

Set the test URL in your `.env.local`:
```bash
TEAMS_WEBHOOK_URL=https://webhook.site/your-unique-id
```

## Production Deployment

### 1. Create Production Environment File

```bash
copy .env.example .env.prod
```

Edit `.env.prod`:
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
TEAMS_WEBHOOK_URL=your-production-webhook-url
```

### 2. Run in Production Mode

```bash
$env:ENVIRONMENT="production"
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t teams-notification-service .
docker run -p 8000:8000 --env-file .env.prod teams-notification-service
```

## Security Considerations

1. **Webhook URL Protection**
   - Never commit webhook URLs to version control
   - Use environment variables for sensitive data
   - Rotate webhook URLs periodically

2. **Network Security**
   - Use HTTPS in production
   - Implement rate limiting if exposed publicly
   - Consider adding authentication for the API endpoint

3. **Message Content**
   - Avoid sending sensitive data in notifications
   - Use URLs to link to detailed information

## Architecture

```
┌─────────────────────┐
│  External System    │
│  (Pub/Sub, Webhook, │
│   Application)      │
└──────────┬──────────┘
           │
           │ POST /notify
           │ {url, message, ...}
           ▼
┌─────────────────────────────┐
│  FastAPI Service            │
│  ┌─────────────────────┐    │
│  │ /notify Endpoint    │    │
│  └──────────┬──────────┘    │
│             │                │
│             ▼                │
│  ┌─────────────────────┐    │
│  │ Teams Service       │    │
│  │ (teams_service.py)  │    │
│  └──────────┬──────────┘    │
└─────────────┼───────────────┘
              │
              │ HTTPS POST
              │ (Message Card JSON)
              ▼
┌─────────────────────────────┐
│  Microsoft Teams            │
│  Incoming Webhook           │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Teams Channel              │
│  (Notification Displayed)   │
└─────────────────────────────┘
```

## License

This project is provided as-is for internal use.

## Support

For issues or questions, please refer to the Microsoft Teams webhook documentation:
- [Microsoft Teams Incoming Webhooks](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [Message Card Reference](https://docs.microsoft.com/en-us/outlook/actionable-messages/message-card-reference)
