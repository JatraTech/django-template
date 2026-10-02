# celery tasks


from celery import shared_task
from django.core.mail import EmailMessage


@shared_task(serializer="pickle")
def send_gmail_emails(email_messages: list[EmailMessage], fail_silently: bool = False):
    from app.utils.backends.email.gmail import GmailBackend

    return GmailBackend.send_batch_emails(
        email_messages,
        fail_silently=fail_silently,
    )


@shared_task(serializer="pickle")
def send_graph_emails(email_messages: list[EmailMessage], fail_silently: bool = False):
    from app.utils.backends.email.graph import GraphEmailBackend

    return GraphEmailBackend.send_batch_emails(
        email_messages,
        fail_silently=fail_silently,
    )
