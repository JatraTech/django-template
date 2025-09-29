from django.db.models import TextChoices


class UserRoleChoices(TextChoices):
    SUPER_ADMIN = "super_admin", "Super Admin"
    ADMIN = "admin", "Admin"
    WORKER = "worker", "Worker"
    CLEANER = "cleaner", "Cleaner"

    HOST = "host", "Host"
    PROPERTY_MANAGER = "property_manager", "Property Manager"
    COMMUNITY_MEMBER = "community_member", "Community Member"


class AccessHaltReasonChoices(TextChoices):
    APPLICATION_PENDING = "application_pending", "Application Pending"
    SUBSCRIPTION_EXPIRED = "subscription_expired", "Subscription Expired"
    BANNED = "banned", "Banned"
