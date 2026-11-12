from django.test import SimpleTestCase


class CeleryEmailTaskRegistrationTests(SimpleTestCase):
    def test_email_tasks_registered_on_celery_app_load(self):
        from app.celery import celery_app

        self.assertIn("django_jt.backends.email.tasks.send_gmail_emails", celery_app.tasks)
        self.assertIn("django_jt.backends.email.tasks.send_graph_emails", celery_app.tasks)
