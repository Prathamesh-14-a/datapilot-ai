# services/email.py
import os
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "no-reply@example.com")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

print("HOST:", SMTP_HOST)
print("PORT:", SMTP_PORT)
print("USER:", SMTP_USER)
print("FROM:", SMTP_FROM)
print("BASE URL:", APP_BASE_URL)

def send_email(to_email: str, subject: str, html_body: str, text_body: str) -> None:
    if not SMTP_HOST:
        raise RuntimeError("SMTP is not configured. Set SMTP_HOST in your environment to send reset emails.")

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    if SMTP_USE_TLS:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls(context=ctx)
            if SMTP_USER:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    else:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
            if SMTP_USER:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)


def send_password_reset_email(to_email: str, raw_token: str) -> str:
    reset_url = f"{APP_BASE_URL.rstrip('/')}/ResetPassword?token={quote(raw_token, safe='')}"
    print(reset_url)

    if not SMTP_HOST:
        return reset_url

    subject = "Reset your password"
    text_body = (
        f"We received a request to reset your password.\n\n"
        f"Open this link to choose a new password (valid 30 minutes):\n{reset_url}\n\n"
        f"If you didn't request this, you can ignore this email."
    )
    html_body = f"""
      <p>We received a request to reset your password.</p>
      <p><a href="{reset_url}">Click here to reset your password</a> (valid 30 minutes).</p>
      <p>If you didn't request this, you can ignore this email.</p>
    """
    send_email(to_email, subject, html_body, text_body)
    return reset_url
