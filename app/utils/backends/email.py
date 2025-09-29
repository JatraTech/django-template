import base64
import logging
import os
from collections.abc import Iterable

from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest
from utils.tasks import send_gmail_emails


class GmailBackend(BaseEmailBackend):
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    TOKEN_PATH = ".secrets/google_token.json"
    CREDENTIALS_PATH = ".secrets/google_credentials.json"

    @classmethod
    def authenticate(cls):
        """Authenticate with Google and refresh token automatically if expired."""
        creds = None
        try:
            # Load existing credentials if available
            if os.path.exists(cls.TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(
                    cls.TOKEN_PATH, cls.SCOPES
                )

            # If credentials are invalid or expired, refresh or reauthenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())  # Auto-refresh using refresh token
                    logging.info("Token refreshed successfully.")
                else:
                    # First-time authentication (Manual login required once)
                    flow = InstalledAppFlow.from_client_secrets_file(
                        cls.CREDENTIALS_PATH, cls.SCOPES
                    )
                    creds = flow.run_local_server(port=0)  # Opens login prompt

                # Save updated credentials
                with open(cls.TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())

            logging.info("Authenticated successfully.")
            return creds

        except HttpError as e:
            logging.error(f"Authentication failed: {e}")
            return None

    @classmethod
    def get_gmail_service(cls):
        try:
            creds = cls.authenticate()
            return build("gmail", "v1", credentials=creds)
        except Exception as e:
            logging.error(f"Failed to get Gmail service: {e}")

    @classmethod
    def send_batch_emails(cls, email_messages: list[EmailMessage]):
        batch = BatchHttpRequest(batch_uri="https://www.googleapis.com/batch/gmail/v1")

        for email_message in email_messages:
            raw_bytes = email_message.message().as_bytes()
            raw_base64 = base64.urlsafe_b64encode(raw_bytes).decode()
            message = {"raw": raw_base64}
            batch.add(
                cls.get_gmail_service()
                .users()
                .messages()
                .send(userId="me", body=message)
            )
        batch.execute()

    def send_messages(self, email_messages: Iterable[EmailMessage]):
        send_gmail_emails.s(email_messages).apply_async()

    def open(self) -> bool | None:
        if not self.service:
            self.service = self.get_gmail_service()
