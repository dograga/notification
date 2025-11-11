# Email Notification Setup Guide

This guide explains how to configure and use the email notification feature.

## SMTP Configuration

### Gmail Setup

If you're using Gmail as your SMTP server:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and your device
   - Copy the generated 16-character password

3. **Configure `.env.local`**:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_USE_TLS=true
SENDER_EMAIL=your-email@gmail.com
SENDER_NAME=Notification Service
```

### Microsoft 365 / Outlook Setup

```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
SENDER_EMAIL=your-email@outlook.com
SENDER_NAME=Notification Service
```

### Custom SMTP Server

```bash
SMTP_SERVER=smtp.your-domain.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
SENDER_EMAIL=noreply@your-domain.com
SENDER_NAME=Your Service Name
```

### Common SMTP Ports

- **587**: TLS/STARTTLS (recommended)
- **465**: SSL (legacy)
- **25**: Unencrypted (not recommended)

## API Endpoint

### POST `/notify/email`

Send an email notification via SMTP.

**Request Body:**

```json
{
  "to_emails": ["user@example.com"],
  "subject": "Deployment Notification",
  "message": "Deployment completed successfully",
  "cc_emails": ["manager@example.com"],
  "bcc_emails": ["logs@example.com"],
  "url": "https://example.com/deployment/123",
  "additional_info": {
    "Environment": "Production",
    "Version": "1.2.3",
    "Status": "Success"
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to_emails` | array | Yes | List of recipient email addresses |
| `subject` | string | Yes | Email subject |
| `message` | string | Yes | Email message content (plain text) |
| `cc_emails` | array | No | List of CC recipients |
| `bcc_emails` | array | No | List of BCC recipients |
| `html_message` | string | No | Custom HTML version of the message |
| `url` | string | No | URL to include in the email |
| `additional_info` | object | No | Additional key-value pairs to display |

**Success Response (200):**

```json
{
  "status": "success",
  "message": "Email sent successfully",
  "details": {
    "success": true,
    "message": "Email sent successfully",
    "recipients": {
      "to": ["user@example.com"],
      "cc": ["manager@example.com"],
      "bcc_count": 1
    },
    "subject": "Deployment Notification",
    "timestamp": "2024-01-15T10:30:00.000000"
  },
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Usage Examples

### Example 1: Simple Email

```bash
curl -X POST "http://localhost:8000/notify/email" \
  -H "Content-Type: application/json" \
  -d '{
    "to_emails": ["user@example.com"],
    "subject": "Test Notification",
    "message": "This is a test email notification"
  }'
```

### Example 2: Email with URL and Additional Info

```bash
curl -X POST "http://localhost:8000/notify/email" \
  -H "Content-Type: application/json" \
  -d '{
    "to_emails": ["user@example.com"],
    "subject": "Deployment Success",
    "message": "Application version 2.5.0 has been deployed to production",
    "url": "https://dashboard.example.com/deployments/456",
    "additional_info": {
      "Environment": "Production",
      "Version": "2.5.0",
      "Deployed By": "john.doe@example.com",
      "Duration": "5 minutes"
    }
  }'
```

### Example 3: Email with CC and BCC

```bash
curl -X POST "http://localhost:8000/notify/email" \
  -H "Content-Type: application/json" \
  -d '{
    "to_emails": ["developer@example.com"],
    "cc_emails": ["manager@example.com", "team-lead@example.com"],
    "bcc_emails": ["logs@example.com"],
    "subject": "Critical Error Alert",
    "message": "A critical error has been detected in the payment service",
    "url": "https://logs.example.com/errors/789",
    "additional_info": {
      "Service": "Payment Processing",
      "Error Code": "PAY-500",
      "Severity": "Critical"
    }
  }'
```

### Example 4: Python Client

```python
import httpx
import asyncio

async def send_email_notification():
    url = "http://localhost:8000/notify/email"
    payload = {
        "to_emails": ["user@example.com"],
        "subject": "Pipeline Completed",
        "message": "Data pipeline execution completed successfully",
        "url": "https://example.com/pipeline/run/42",
        "additional_info": {
            "Pipeline": "daily-etl-pipeline",
            "Records Processed": "1,234,567",
            "Duration": "45 minutes",
            "Status": "Success"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        print(response.json())

asyncio.run(send_email_notification())
```

### Example 5: PowerShell

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

Invoke-RestMethod -Uri "http://localhost:8000/notify/email" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## Email Templates

The service automatically generates HTML emails with:
- Professional styling
- Responsive design
- Clickable buttons for URLs
- Formatted tables for additional information
- Timestamp footer

### Custom HTML Template

You can provide your own HTML template:

```json
{
  "to_emails": ["user@example.com"],
  "subject": "Custom Email",
  "message": "Plain text version",
  "html_message": "<html><body><h1>Custom HTML</h1><p>Your custom content here</p></body></html>"
}
```

## Troubleshooting

### Common Issues

**1. SMTP Authentication Failed**
- Verify username and password are correct
- For Gmail: Use App Password, not your regular password
- Check if 2FA is enabled (required for Gmail App Passwords)

**2. Connection Timeout**
- Verify SMTP server address and port
- Check firewall settings
- Ensure your network allows outbound SMTP connections

**3. TLS/SSL Errors**
- Try changing `SMTP_USE_TLS` to `false` for port 465
- Verify the SMTP server supports TLS on the configured port

**4. "Sender Email Not Configured"**
- Ensure `SENDER_EMAIL` is set in your `.env.local`
- Restart the service after updating environment variables

**5. Emails Going to Spam**
- Configure SPF, DKIM, and DMARC records for your domain
- Use a verified sender email address
- Avoid spam trigger words in subject/content

### Testing SMTP Configuration

Test your SMTP settings with Python:

```python
import smtplib
from email.mime.text import MIMEText

# Test connection
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-app-password')
    print("✓ SMTP connection successful")
    server.quit()
except Exception as e:
    print(f"✗ SMTP connection failed: {e}")
```

## Security Best Practices

1. **Never commit credentials**
   - Use environment variables
   - Add `.env.local` to `.gitignore`

2. **Use App Passwords**
   - Don't use your main account password
   - Generate service-specific passwords

3. **Limit Permissions**
   - Use dedicated email accounts for notifications
   - Grant minimal required permissions

4. **Monitor Usage**
   - Track email sending rates
   - Set up alerts for failures
   - Monitor for abuse

5. **Rate Limiting**
   - Implement rate limiting for the API endpoint
   - Respect SMTP provider limits (Gmail: 500/day for free accounts)

## SMTP Provider Limits

| Provider | Daily Limit | Rate Limit |
|----------|-------------|------------|
| Gmail (Free) | 500 emails | 100/hour |
| Gmail (Workspace) | 2,000 emails | 100/hour |
| Outlook/Office 365 | 300 emails | 30/minute |
| SendGrid (Free) | 100 emails | Varies |
| AWS SES | 200/day (sandbox) | 1/second |

## Integration with Pub/Sub

Example of forwarding Pub/Sub messages to email:

```python
from google.cloud import pubsub_v1
import httpx
import json

def callback(message):
    """Process Pub/Sub message and send email"""
    data = json.loads(message.data.decode('utf-8'))
    
    payload = {
        "to_emails": data.get("recipients", []),
        "subject": data.get("subject", "Notification"),
        "message": data.get("message", ""),
        "url": data.get("url"),
        "additional_info": data.get("additional_info")
    }
    
    response = httpx.post(
        "http://localhost:8000/notify/email",
        json=payload
    )
    
    if response.status_code == 200:
        message.ack()
    else:
        message.nack()

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('project-id', 'subscription-name')
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
```

## Additional Resources

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Outlook SMTP Settings](https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
- [Email MIME Types](https://docs.python.org/3/library/email.mime.html)
