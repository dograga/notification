import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import structlog
from typing import List
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

class SmtpError(Exception):
    """Base exception for SMTP errors"""
    pass

class SmtpService:
    def send_email(self, to_emails: List[str], subject: str, content: str):
        """
        Send email using SMTP
        """
        if not settings.smtp_host:
            logger.warning("SMTP host not configured, skipping email send")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = settings.sender_email
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject

            msg.attach(MIMEText(content, 'html'))

            # Synchronous SMTP call - in production might want to offload to background task
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_username and settings.smtp_password:
                    server.starttls()
                    server.login(settings.smtp_username, settings.smtp_password)
                
                server.send_message(msg)
            
            logger.info("Email sent successfully", recipients_count=len(to_emails))
            
        except Exception as e:
            logger.error("Failed to send email", error=str(e))
            raise SmtpError(f"Failed to send email: {str(e)}")

# Global instance
smtp_service = SmtpService()
