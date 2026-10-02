from django.db import migrations, models


def backfill_favicons_from_logos(apps, schema_editor):
    from backstage.favicon import regenerate_favicon_light
    from backstage.models import BackstageSettings

    try:
        settings_obj = BackstageSettings.objects.get(pk=1)
    except BackstageSettings.DoesNotExist:
        return

    if not settings_obj.logo_light:
        return

    if regenerate_favicon_light(settings_obj):
        settings_obj.save(update_fields=["favicon_light"])


class Migration(migrations.Migration):
    dependencies = [
        ("backstage", "0002_backfill_branding_from_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="backstagesettings",
            name="favicon_light",
            field=models.ImageField(
                blank=True,
                help_text="Auto-generated from the light logo for browser tabs.",
                upload_to="backstage/",
            ),
        ),
        migrations.RunPython(backfill_favicons_from_logos, migrations.RunPython.noop),
    ]
