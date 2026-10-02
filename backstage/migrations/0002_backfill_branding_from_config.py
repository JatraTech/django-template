from django.conf import settings as django_settings
from django.db import migrations


def _backstage_config() -> dict:
    backstage = getattr(django_settings, "BACKSTAGE", None)
    if isinstance(backstage, dict):
        return backstage
    return {}


def _nonempty_str(value: object) -> str | None:
    if value is None or value == "" or isinstance(value, dict):
        return None
    return str(value)


def backfill_branding_from_config(apps, schema_editor):
    BackstageSettings = apps.get_model("backstage", "BackstageSettings")
    try:
        obj = BackstageSettings.objects.get(pk=1)
    except BackstageSettings.DoesNotExist:
        return

    if obj.site_title or obj.site_header or obj.site_subheader:
        return

    cfg = _backstage_config()
    updates: dict[str, str] = {}
    for db_field, cfg_key in (
        ("site_title", "SITE_TITLE"),
        ("site_header", "SITE_HEADER"),
        ("site_subheader", "SITE_SUBHEADER"),
    ):
        value = _nonempty_str(cfg.get(cfg_key))
        if value is not None:
            updates[db_field] = value

    if updates:
        for field, value in updates.items():
            setattr(obj, field, value)
        obj.save(update_fields=list(updates.keys()))


class Migration(migrations.Migration):

    dependencies = [
        ("backstage", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(backfill_branding_from_config, migrations.RunPython.noop),
    ]
