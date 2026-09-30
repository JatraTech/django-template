# celery tasks


from celery import shared_task
from django.core.mail import EmailMessage


@shared_task(serializer="pickle")
def send_gmail_emails(email_messages: list[EmailMessage]):
    from app.utils.backends.email.gmail import GmailBackend

    GmailBackend.send_batch_emails(email_messages)
