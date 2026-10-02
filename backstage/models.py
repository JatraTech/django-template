from django.db import models

from backstage.accent_palettes import ACCENT_PALETTE_CHOICES, DEFAULT_ACCENT_PALETTE


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class BackstageSettings(SingletonModel):
    class ThemePreset(models.TextChoices):
        DEFAULT = "default", "Default"
        MINIMAL = "minimal", "Minimal"
        COMPACT = "compact", "Compact"

    class FontFamily(models.TextChoices):
        INTER = "inter", "Inter"
        SYSTEM = "system", "System UI"
        SERIF = "serif", "Serif"
        MONO = "mono", "Monospace"
        ROUNDED = "rounded", "Rounded UI"

    class SidebarDensity(models.TextChoices):
        COMFORTABLE = "comfortable", "Comfortable"
        COMPACT = "compact", "Compact"

    site_title = models.CharField(max_length=120, blank=True, default="")
    site_header = models.CharField(max_length=200, blank=True, default="")
    site_subheader = models.CharField(max_length=200, blank=True, default="")
    theme_preset = models.CharField(
        max_length=16,
        choices=ThemePreset.choices,
        default=ThemePreset.DEFAULT,
    )
    font_family = models.CharField(
        max_length=16,
        choices=FontFamily.choices,
        default=FontFamily.INTER,
    )
    sidebar_density = models.CharField(
        max_length=16,
        choices=SidebarDensity.choices,
        default=SidebarDensity.COMFORTABLE,
    )
    accent_palette = models.CharField(
        max_length=16,
        choices=ACCENT_PALETTE_CHOICES,
        default=DEFAULT_ACCENT_PALETTE,
        help_text="Tailwind-style accent palette for the admin panel.",
    )
    custom_css = models.TextField(
        blank=True,
        help_text="Optional CSS appended to the dynamic admin theme. Admin-only.",
    )
    logo_light = models.ImageField(upload_to="backstage/", blank=True)
    logo_dark = models.ImageField(upload_to="backstage/", blank=True)
    favicon_light = models.ImageField(
        upload_to="backstage/",
        blank=True,
        help_text="Auto-generated from the light logo for browser tabs.",
    )
    frontend_url = models.URLField(
        blank=True,
        default="",
        help_text="Public frontend URL used for preview links and the admin site dropdown.",
    )

    class Meta:
        verbose_name = "Admin appearance"
        verbose_name_plural = "Admin appearance"

    def __str__(self) -> str:
        return self.site_header

    def get_frontend_url(self) -> str:
        return self.frontend_url.rstrip("/")

    def save(self, *args, **kwargs):
        from backstage.favicon import regenerate_favicon_light

        self.pk = 1
        previous_logo_name = ""
        if BackstageSettings.objects.filter(pk=1).exists():
            previous_logo_name = (
                BackstageSettings.objects.values_list("logo_light", flat=True).get(pk=1) or ""
            )

        new_logo_name = self.logo_light.name if self.logo_light else ""
        logo_changed = previous_logo_name != new_logo_name

        super().save(*args, **kwargs)

        if logo_changed and regenerate_favicon_light(self):
            super().save(update_fields=["favicon_light"])
