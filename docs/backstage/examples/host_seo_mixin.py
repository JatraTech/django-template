"""Copy into your host app. Field names must match Backstage SEO conventions (or override SEO_FIELD_NAMES)."""

from django.db import models


class SEOMixin(models.Model):
    seo_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Search result title",
        help_text="Recommended max 60 characters. Leave blank to use the page title.",
    )
    seo_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Search result description",
        help_text="Recommended max 160 characters for Google.",
    )
    canonical_url = models.URLField(
        blank=True,
        verbose_name="Canonical URL",
        help_text="Advanced. Only set if this page has a duplicate URL elsewhere.",
    )
    og_title = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Social share title",
        help_text="When shared on social media. Leave blank to use the search title.",
    )
    og_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Social share description",
        help_text="Short blurb when the page is shared on social media.",
    )
    og_image = models.ImageField(
        upload_to="seo/",
        blank=True,
        verbose_name="Social share image",
        help_text="Image used in link previews.",
    )

    class Meta:
        abstract = True
