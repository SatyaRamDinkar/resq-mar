import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Optional, Callable

def send_sms(phone: str, message: str, logger: Optional[Callable] = None) -> bool:
    """Send SMS via Twilio. Fallback to logger if missing keys."""
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    from_num = os.getenv("TWILIO_FROM")

    if not (sid and token and from_num):
        if logger:
            logger("CommsAgent", "dispatch", f"MOCK SMS to {phone}: {message}")
        return True

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = {
        "To": phone,
        "From": from_num,
        "Body": message
    }
    try:
        res = requests.post(url, data=data, auth=(sid, token), timeout=5)
        res.raise_for_status()
        if logger:
            logger("CommsAgent", "dispatch", f"LIVE SMS to {phone} sent successfully.")
        return True
    except Exception as e:
        if logger:
            logger("CommsAgent", "error", f"SMS failed to {phone}: {str(e)}")
        return False

def send_email(to_email: str, subject: str, body: str, logger: Optional[Callable] = None) -> bool:
    """Send Email via SMTP. Fallback to logger if missing keys."""
    server = os.getenv("SMTP_SERVER")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASSWORD")

    if not (server and user and pwd):
        if logger:
            logger("CommsAgent", "dispatch", f"MOCK EMAIL to {to_email} | Subj: {subject} | Body: {body}")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(user, pwd)
            smtp.send_message(msg)
            
        if logger:
            logger("CommsAgent", "dispatch", f"LIVE EMAIL to {to_email} sent successfully.")
        return True
    except Exception as e:
        if logger:
            logger("CommsAgent", "error", f"EMAIL failed to {to_email}: {str(e)}")
        return False
