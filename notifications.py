import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import config

def send_notification_email(subject, body):
    """Sends an email notification if enabled in the config."""
    if not config.EMAIL_NOTIFICATIONS_ENABLED:
        logging.info("Email notifications are disabled. Skipping email.")
        return

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = config.EMAIL_SENDER
    msg['To'] = config.EMAIL_RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = None
    try:
        logging.info(f"Connecting to SMTP server at {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
        
        server.send_message(msg)
        logging.info(f"Successfully sent notification email to {config.EMAIL_RECIPIENT}.")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")
    finally:
        if server:
            server.quit()