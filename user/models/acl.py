from typing import Literal
from pydantic import BaseModel

ALL = "*"


class AccessPolicyValidator(BaseModel):
    # principal: ALL or list of groups
    principal: Literal["*"] | list  # Example, extend as needed
    action: Literal["*"] | list  # e.g., "read", "write"
    resource: Literal["*"] | list  # e.g., "document", "folder"
    fields: Literal["*"] | list


# models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField


class AccessPolicy(models.Model):
    PRINCIPAL_ALL = "*"
    ACTION_ALL = "*"
    RESOURCE_ALL = "*"
    FIELDS_ALL = "*"

    principal = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text='Use ["*"] for all users or list of groups.',
    )
    action = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        help_text='Actions like ["read", "write", "delete"].',
    )
    resource = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text='Resources like ["document", "order"].',
    )
    fields = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        help_text="Fields allowed to be accessed.",
    )

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Policy[{', '.join(self.action)} on {', '.join(self.resource)} for {', '.join(self.principal)}]"
