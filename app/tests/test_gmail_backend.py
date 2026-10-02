from unittest.mock import MagicMock, patch

from django.core.mail import EmailMessage
from django.test import SimpleTestCase

from app.utils.backends.email.gmail import GmailBackend


class GmailEmailBackendTests(SimpleTestCase):
    @patch("app.utils.backends.email.gmail.queue_email_tasks", return_value=False)
    @patch("app.utils.backends.email.gmail.BatchHttpRequest")
    @patch.object(GmailBackend, "get_gmail_service")
    def test_fail_silently_skips_failed_batch(
        self,
        mock_get_service,
        mock_batch_cls,
        _mock_queue,
    ):
        mock_batch = mock_batch_cls.return_value
        mock_batch.execute.side_effect = RuntimeError("boom")

        backend = GmailBackend(fail_silently=True)
        message = EmailMessage(
            subject="Alert",
            body="Body",
            from_email="noreply@example.com",
            to=["ops@example.com"],
        )
        sent = backend.send_messages([message])

        self.assertEqual(sent, 0)
        mock_batch.execute.assert_called_once()

    @patch("app.utils.backends.email.gmail.queue_email_tasks", return_value=False)
    @patch("app.utils.backends.email.gmail.BatchHttpRequest")
    @patch.object(GmailBackend, "get_gmail_service")
    def test_raises_when_not_fail_silently(
        self,
        mock_get_service,
        mock_batch_cls,
        _mock_queue,
    ):
        mock_batch = mock_batch_cls.return_value
        mock_batch.execute.side_effect = RuntimeError("boom")

        backend = GmailBackend(fail_silently=False)
        message = EmailMessage(
            subject="Alert",
            body="Body",
            from_email="noreply@example.com",
            to=["ops@example.com"],
        )

        with self.assertRaises(RuntimeError):
            backend.send_messages([message])

    @patch("app.utils.backends.email.gmail.queue_email_tasks", return_value=False)
    @patch("app.utils.backends.email.gmail.BatchHttpRequest")
    @patch.object(GmailBackend, "get_gmail_service")
    def test_send_success_returns_count(
        self,
        mock_get_service,
        mock_batch_cls,
        _mock_queue,
    ):
        mock_batch = mock_batch_cls.return_value
        mock_get_service.return_value = MagicMock()

        backend = GmailBackend()
        message = EmailMessage(
            subject="Alert",
            body="Body",
            from_email="noreply@example.com",
            to=["ops@example.com"],
        )
        sent = backend.send_messages([message])

        self.assertEqual(sent, 1)
