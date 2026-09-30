import base64
import logging
import os
from collections.abc import Iterable

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest

from app.celery import is_celery_running
from app.tasks import send_gmail_emails


class GmailBackend(BaseEmailBackend):
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]
    TOKEN_PATH = ".secrets/google_token.json"
    CREDENTIALS_PATH = ".secrets/google_service_account.json"

    @classmethod
    def authenticate(cls):
        creds = service_account.Credentials.from_service_account_file(cls.CREDENTIALS_PATH, scopes=cls.SCOPES)
        subject = f"noreply@{settings.APP_DOMAIN}"
        if subject:
            creds = creds.with_subject(subject)
        return creds

    @classmethod
    def get_gmail_service(cls):
        try:
            creds = cls.authenticate()
            return build("gmail", "v1", credentials=creds)
        except Exception as e:
            logging.error(f"Failed to get Gmail service: {e}")

    @classmethod
    def _apply_recipient_override(cls, email_message: EmailMessage) -> None:
        override = [addr.strip() for addr in settings.EMAIL_RECIPIENTS_OVERRIDE if addr.strip()]
        if not override:
            return
        email_message.to = override
        email_message.cc = []
        email_message.bcc = []

    @classmethod
    def send_batch_emails(cls, email_messages: list[EmailMessage]):
        batch = BatchHttpRequest(batch_uri="https://www.googleapis.com/batch/gmail/v1")

        for email_message in email_messages:
            cls._apply_recipient_override(email_message)
            raw_bytes = email_message.message().as_bytes()
            raw_base64 = base64.urlsafe_b64encode(raw_bytes).decode()
            message = {"raw": raw_base64}
            batch.add(cls.get_gmail_service().users().messages().send(userId="me", body=message))
        batch.execute()

    def send_messages(self, email_messages: Iterable[EmailMessage]):
        if is_celery_running():
            send_gmail_emails.s(email_messages).apply_async()
        else:
            send_gmail_emails(email_messages)

    def open(self) -> bool | None:
        if not self.service:
            self.service = self.get_gmail_service()
