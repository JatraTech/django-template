from django.conf import settings
from django.core.mail import EmailMessage


def apply_recipient_override(email_message: EmailMessage) -> None:
    override = [addr.strip() for addr in settings.EMAIL_RECIPIENTS_OVERRIDE if addr.strip()]
    if not override:
        return
    email_message.to = override
    email_message.cc = []
    email_message.bcc = []
