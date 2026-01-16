from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError

from app.utils.mixins.models import ModelMixin
from user.constants import AccessHaltReasonChoices, UserRoleChoices
from django.contrib.auth.models import UserManager


class User(ModelMixin, AbstractUser):
    image = models.ImageField(upload_to="user/users/", null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True)
    dob = models.DateField(null=True, blank=True)
    user_role = models.CharField(
        max_length=20, choices=UserRoleChoices.choices, default=UserRoleChoices.USER
    )
    email_verified_at = models.DateTimeField(null=True, blank=True)

    access_halt_reason = models.CharField(
        blank=True,
        default="",
        choices=AccessHaltReasonChoices.choices,
    )
    ahr_desc = models.TextField(
        help_text="Description why the access is halted for cases like Banned, etc.",
        blank=True,
        default="",
        verbose_name="Access Halt Reason Description",
    )

    notify_on_user_reg = models.BooleanField(
        default=True,
        help_text="For admins: notify if a user registers",
    )

    objects: UserManager = UserManager()

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def full_name(self) -> str:
        return self.get_full_name()

    @property
    def is_password_set(self) -> bool:
        return self.password != ""

    def save(self, *args, **kwargs):
        if self.is_staff:
            self.user_role = UserRoleChoices.ADMIN
        elif self.is_superuser:
            self.user_role = UserRoleChoices.ADMIN
        super().save(*args, **kwargs)
