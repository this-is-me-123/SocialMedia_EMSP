import smtplib
import logging
from email.mime.text import MIMEText
import os

# --- Logging setup ---
logger = logging.getLogger("automation_stack.email_utils")

"""
Required environment variables:
- SMTP_SERVER
- SMTP_PORT (default: 587)
- SMTP_USER
- SMTP_PASSWORD
- NOTIFY_FROM_EMAIL (optional, defaults to SMTP_USER)
- NOTIFY_TO_EMAIL (optional, can be passed to function)
"""

def send_failure_notification(subject, message, to_email=None, html=False):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('NOTIFY_FROM_EMAIL', smtp_user)
    to_email = to_email or os.getenv('NOTIFY_TO_EMAIL')

    if not (smtp_server and smtp_user and smtp_password and to_email):
        logger.error('Email notification not sent: SMTP config missing.')
        return False

    subtype = 'html' if html else 'plain'
    msg = MIMEText(message, subtype)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info(f'Notification sent to {to_email}')
        return True
    except Exception as e:
        logger.error(f'Failed to send notification: {e}')
        return False
