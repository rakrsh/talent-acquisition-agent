import pytest
from unittest.mock import patch, MagicMock
from modules.notifications import NotificationService, NotificationConfig

@pytest.fixture
def mock_config():
    return NotificationConfig(
        sender_email="sender@test.com",
        recipient_email="recipient@test.com",
        sender_password="password",
        twilio_sid="sid",
        twilio_token="token",
        twilio_phone="+123",
        recipient_phone="+456"
    )

def test_send_email_success(mock_config):
    notifier = NotificationService(config=mock_config)
    
    with patch("smtplib.SMTP") as mock_smtp:
        instance = mock_smtp.return_value.__enter__.return_value
        success = notifier.send_email("Subject", "Body")
        
        assert success is True
        assert instance.starttls.called
        assert instance.login.called
        assert instance.send_message.called

def test_send_email_disabled():
    notifier = NotificationService(config=NotificationConfig())
    success = notifier.send_email("Subject", "Body")
    assert success is False

@patch("twilio.rest.Client")
def test_send_sms_success(mock_twilio, mock_config):
    notifier = NotificationService(config=mock_config)
    
    success = notifier.send_sms("Message")
    
    assert success is True
    mock_twilio.assert_called_with("sid", "token")
    mock_twilio.return_value.messages.create.assert_called()

def test_notify_new_jobs(mock_config, sample_job):
    notifier = NotificationService(config=mock_config)
    
    with patch.object(notifier, "send_email") as mock_email, \
         patch.object(notifier, "send_sms") as mock_sms:
        
        notifier.notify_new_jobs([sample_job])
        
        assert mock_email.called
        assert mock_sms.called
        # Check subject
        args, _ = mock_email.call_args
        assert "New Job Alerts" in args[0]
