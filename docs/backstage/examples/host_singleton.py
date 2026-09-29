"""Copy into your host app (e.g. cms/models/base.py). Not imported by Backstage."""

from django.db import models


class SingletonModel(models.Model):
    """Forces pk=1. Backstage detects this base by class name in the MRO."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
