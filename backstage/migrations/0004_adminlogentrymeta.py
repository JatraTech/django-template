# Generated manually for admin activity log sidecar.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("admin", "0003_logentry_add_action_flag_choices"),
        ("backstage", "0003_backstagesettings_favicon_light"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminLogEntryMeta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "log_entry",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="backstage_meta",
                        to="admin.logentry",
                    ),
                ),
            ],
            options={
                "verbose_name": "Admin log entry metadata",
                "verbose_name_plural": "Admin log entry metadata",
            },
        ),
    ]
