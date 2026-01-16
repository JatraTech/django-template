from django.db.models import TextChoices


class UserRoleChoices(TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"


class AccessHaltReasonChoices(TextChoices):
    APPLICATION_PENDING = "application_pending", "Application Pending"
    BANNED = "banned", "Banned"
