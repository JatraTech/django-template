from django.core.management.base import BaseCommand

from backstage.favicon import regenerate_favicon_light
from backstage.models import BackstageSettings
from backstage.services import clear_backstage_settings_cache


class Command(BaseCommand):
    help = "Regenerate the admin tab favicon from Admin appearance → light logo."

    def handle(self, *args, **options):
        try:
            settings_obj = BackstageSettings.objects.get(pk=1)
        except BackstageSettings.DoesNotExist:
            self.stdout.write("No Admin appearance record (pk=1). Nothing to do.")
            return

        if not settings_obj.logo_light:
            self.stdout.write("No light logo uploaded. Nothing to do.")
            return

        changed = regenerate_favicon_light(settings_obj)
        if changed:
            settings_obj.save(update_fields=["favicon_light"])
            clear_backstage_settings_cache()
            self.stdout.write(self.style.SUCCESS("Admin favicon regenerated."))
        else:
            self.stdout.write("Admin favicon already up to date.")
