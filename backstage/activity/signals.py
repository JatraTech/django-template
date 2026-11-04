from __future__ import annotations

from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver

from backstage.client_ip import client_ip
from backstage.middleware import get_current_request
from backstage.models import AdminLogEntryMeta


@receiver(post_save, sender=LogEntry)
def attach_admin_log_entry_meta(sender, instance: LogEntry, created: bool, **kwargs) -> None:
    if not created:
        return
    request = get_current_request()
    AdminLogEntryMeta.objects.get_or_create(
        log_entry=instance,
        defaults={"ip_address": client_ip(request)},
    )
