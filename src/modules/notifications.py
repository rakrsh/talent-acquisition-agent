"""Notification module - sends email/SMS alerts for new jobs."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from typing import Optional

from config import logger
from settings import get_settings


@dataclass
class NotificationConfig:
    """Email/SMS configuration."""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipient_email: str = ""
    twilio_sid: str = ""
    twilio_token: str = ""
    twilio_phone: str = ""
    recipient_phone: str = ""


class NotificationService:
    """Sends notifications for new job listings."""
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        settings = get_settings()
        self.config = config or NotificationConfig(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            sender_email=settings.sender_email,
            sender_password=settings.sender_password,
            recipient_email=settings.recipient_email,
            twilio_sid=settings.twilio_sid,
            twilio_token=settings.twilio_token,
            twilio_phone=settings.twilio_phone,
            recipient_phone=settings.recipient_phone,
        )
    
    def _load_config(self) -> NotificationConfig:
        """Load notification config from environment."""
        return NotificationConfig(
            smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            sender_email=os.getenv("SENDER_EMAIL", ""),
            sender_password=os.getenv("SENDER_PASSWORD", ""),
            recipient_email=os.getenv("RECIPIENT_EMAIL", ""),
            twilio_sid=os.getenv("TWILIO_SID", ""),
            twilio_token=os.getenv("TWILIO_TOKEN", ""),
            twilio_phone=os.getenv("TWILIO_PHONE", ""),
            recipient_phone=os.getenv("RECIPIENT_PHONE", ""),
        )
    
    def send_email(self, subject: str, body: str) -> bool:
        """Send email notification."""
        if not self.config.sender_email or not self.config.recipient_email:
            print("Email not configured - skipping")
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.config.sender_email
            msg["To"] = self.config.recipient_email
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "html"))
            
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.sender_email, self.config.sender_password)
                server.send_message(msg)
            
            print(f"Email sent: {subject}")
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
    
    def send_sms(self, message: str) -> bool:
        """Send SMS notification via Twilio."""
        if not self.config.twilio_sid or not self.config.recipient_phone:
            print("SMS not configured - skipping")
            return False
        
        try:
            from twilio.rest import Client
            client = Client(self.config.twilio_sid, self.config.twilio_token)
            client.messages.create(
                body=message,
                from_=self.config.twilio_phone,
                to=self.config.recipient_phone
            )
            print(f"SMS sent: {message[:50]}...")
            return True
        except Exception as e:
            print(f"SMS send error: {e}")
            return False
    
    def notify_new_jobs(self, jobs: list) -> None:
        """Notify about new job listings."""
        if not jobs:
            return
        
        # Email with job list
        job_list_html = "<ul>"
        for job in jobs[:10]:  # Limit to 10 jobs per notification
            job_list_html += f'<li><a href="{job.url}">{job.title}</a> @ {job.company} ({job.location})</li>'
        job_list_html += "</ul>"
        
        subject = f"🔔 New Job Alerts - {len(jobs)} jobs found"
        body = f"""
        <h2>New Job Opportunities Found</h2>
        <p>Found {len(jobs)} new jobs matching your criteria:</p>
        {job_list_html}
        <p>Log in to view all or auto-apply.</p>
        """
        
        self.send_email(subject, body)
        
        # SMS summary for urgent jobs
        if len(jobs) > 0:
            sms_msg = f"New {len(jobs)} jobs found! Top: {jobs[0].title} at {jobs[0].company}"
            self.send_sms(sms_msg)


if __name__ == "__main__":
    # Test
    notifier = NotificationService()
    print("Notification service ready")