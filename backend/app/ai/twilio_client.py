"""
Twilio SMS wrapper for the Emergency Alert module.
Reuses the same account-based Twilio pattern already proven in the
Outreach project — just a different message payload here.
"""
from twilio.rest import Client

from app.core.config import settings


class TwilioNotConfiguredError(Exception):
    pass


def send_emergency_sms(to_phone: str, message: str) -> str:
    """Returns the Twilio message SID on success."""
    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER):
        raise TwilioNotConfiguredError(
            "Twilio credentials are not set in the backend .env file "
            "(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER)."
        )
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    msg = client.messages.create(body=message, from_=settings.TWILIO_FROM_NUMBER, to=to_phone)
    return msg.sid
