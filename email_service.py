"""
Email Notification Service

This module provides functionality to send email notifications via SMTP server.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import structlog
from typing import Optional, List, Dict, Any
from datetime import datetime
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()


class EmailNotificationError(Exception):
    """Custom exception for email notification errors"""
    pass


class EmailNotificationService:
    """Service for sending email notifications via SMTP"""
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        smtp_use_tls: Optional[bool] = None,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None
    ):
        """
        Initialize Email notification service
        
        Args:
            smtp_server: SMTP server hostname
            smtp_port: SMTP server port
            smtp_username: SMTP username for authentication
            smtp_password: SMTP password for authentication
            smtp_use_tls: Whether to use TLS encryption
            sender_email: Email address to send from
            sender_name: Display name for sender
        """
        self.smtp_server = smtp_server or getattr(settings, 'smtp_server', None)
        self.smtp_port = smtp_port or getattr(settings, 'smtp_port', 587)
        self.smtp_username = smtp_username or getattr(settings, 'smtp_username', None)
        self.smtp_password = smtp_password or getattr(settings, 'smtp_password', None)
        self.smtp_use_tls = smtp_use_tls if smtp_use_tls is not None else getattr(settings, 'smtp_use_tls', True)
        self.sender_email = sender_email or getattr(settings, 'sender_email', None)
        self.sender_name = sender_name or getattr(settings, 'sender_name', 'Notification Service')
        
        if not self.smtp_server:
            logger.warning("SMTP server not configured")
        if not self.sender_email:
            logger.warning("Sender email not configured")
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        message: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        html_message: Optional[str] = None,
        url: Optional[str] = None,
        additional_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send an email notification
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            message: Plain text message content
            cc_emails: Optional list of CC recipients
            bcc_emails: Optional list of BCC recipients
            html_message: Optional HTML version of the message
            url: Optional URL to include in the email
            additional_info: Optional dictionary of additional information
            
        Returns:
            Dict containing the response status and details
            
        Raises:
            EmailNotificationError: If the email fails to send
        """
        if not self.smtp_server:
            error_msg = "SMTP server is not configured"
            logger.error(error_msg)
            raise EmailNotificationError(error_msg)
        
        if not self.sender_email:
            error_msg = "Sender email is not configured"
            logger.error(error_msg)
            raise EmailNotificationError(error_msg)
        
        if not to_emails:
            error_msg = "No recipient email addresses provided"
            logger.error(error_msg)
            raise EmailNotificationError(error_msg)
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = ', '.join(to_emails)
            
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)
            
            # Build email body
            text_body = self._build_text_body(message, url, additional_info)
            html_body = html_message or self._build_html_body(subject, message, url, additional_info)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Combine all recipients
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            # Send email
            if self.smtp_use_tls:
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls(context=context)
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.sender_email, all_recipients, msg.as_string())
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.smtp_username and self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.sendmail(self.sender_email, all_recipients, msg.as_string())
            
            logger.info(
                "Email sent successfully",
                to=to_emails,
                subject=subject,
                cc=cc_emails,
                bcc_count=len(bcc_emails) if bcc_emails else 0
            )
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "recipients": {
                    "to": to_emails,
                    "cc": cc_emails or [],
                    "bcc_count": len(bcc_emails) if bcc_emails else 0
                },
                "subject": subject,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            logger.error(error_msg)
            raise EmailNotificationError(error_msg) from e
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error sending email: {str(e)}"
            logger.error(error_msg)
            raise EmailNotificationError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(error_msg, error=str(e))
            raise EmailNotificationError(error_msg) from e
    
    def _build_text_body(
        self,
        message: str,
        url: Optional[str],
        additional_info: Optional[Dict[str, str]]
    ) -> str:
        """Build plain text email body"""
        body_parts = [message]
        
        if url:
            body_parts.append(f"\n\nURL: {url}")
        
        if additional_info:
            body_parts.append("\n\nAdditional Information:")
            for key, value in additional_info.items():
                body_parts.append(f"  {key}: {value}")
        
        body_parts.append(f"\n\nTimestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        return '\n'.join(body_parts)
    
    def _build_html_body(
        self,
        subject: str,
        message: str,
        url: Optional[str],
        additional_info: Optional[Dict[str, str]]
    ) -> str:
        """Build HTML email body"""
        html = f"""
        <html>
          <head>
            <style>
              body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
              }}
              .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
              }}
              .header {{
                background-color: #0078D4;
                color: white;
                padding: 20px;
                border-radius: 5px 5px 0 0;
              }}
              .content {{
                background-color: #f9f9f9;
                padding: 20px;
                border: 1px solid #ddd;
              }}
              .message {{
                background-color: white;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
              }}
              .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
              }}
              .info-table td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
              }}
              .info-table td:first-child {{
                font-weight: bold;
                width: 40%;
              }}
              .button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #0078D4;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 15px 0;
              }}
              .footer {{
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
              }}
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <h2>{subject}</h2>
              </div>
              <div class="content">
                <div class="message">
                  <p>{message.replace(chr(10), '<br>')}</p>
                </div>
        """
        
        if url:
            html += f"""
                <div style="text-align: center;">
                  <a href="{url}" class="button">View Details</a>
                </div>
            """
        
        if additional_info:
            html += """
                <table class="info-table">
            """
            for key, value in additional_info.items():
                html += f"""
                  <tr>
                    <td>{key}</td>
                    <td>{value}</td>
                  </tr>
                """
            html += """
                </table>
            """
        
        html += f"""
                <div class="footer">
                  <p>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                  <p>This is an automated notification from the Notification Service</p>
                </div>
              </div>
            </div>
          </body>
        </html>
        """
        
        return html


# Singleton instance
email_notification_service = EmailNotificationService()
