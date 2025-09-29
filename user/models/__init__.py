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
        max_length=20, choices=UserRoleChoices.choices, default=UserRoleChoices.HOST
    )
    address = models.TextField(default="")
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # instead of using org-employee model, we use a foreign key to the same user model. This allows us to create a hierarchy of users within the same organization.
    # The superior field is a foreign key to the User model itself, and the related_name attribute is set to "subordinates" so that we can easily access all subordinates of a given user.
    superior = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subordinates",
    )

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
        help_text="For admins and super-admins: notify if a user registers",
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

    def clean_user_role(self) -> None:
        if self.user_role == UserRoleChoices.PROPERTY_MANAGER and not self.superior:
            raise ValidationError("Sub-host must have a superior")

    def save(self, *args, **kwargs):
        # self.clean_user_role()
        if self.is_staff:
            self.user_role = UserRoleChoices.ADMIN
        elif self.is_superuser:
            self.user_role = UserRoleChoices.SUPER_ADMIN
        super().save(*args, **kwargs)
