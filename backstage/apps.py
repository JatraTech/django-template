from django.apps import AppConfig


def _ensure_backstage_settings_on_migrate(sender, **kwargs) -> None:
    if sender.name != "backstage":
        return

    from backstage.services import ensure_backstage_settings

    ensure_backstage_settings()


class BackstageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backstage"
    verbose_name = "Backstage"

    def ready(self) -> None:
        from django.contrib import admin
        from django.contrib.admin import sites
        from django.db.models.signals import post_migrate

        from backstage.sites import BackstageAdminSite

        site = BackstageAdminSite()
        admin.site = site
        sites.site = site

        from backstage.registry.autodiscover import register_all_models
        from backstage.registry.settings_admin import BackstageSettingsAdmin  # noqa: F401

        register_all_models()

        post_migrate.connect(
            _ensure_backstage_settings_on_migrate,
            dispatch_uid="backstage.ensure_settings",
        )
