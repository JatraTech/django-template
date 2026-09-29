from __future__ import annotations

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from backstage.draft.mixins.models import DraftPublishDuplicateRowMixin
from backstage.models import SingletonModel


class SampleSEOMixin(models.Model):
    seo_title = models.CharField(max_length=60, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    canonical_url = models.URLField(blank=True)
    og_title = models.CharField(max_length=60, blank=True)
    og_description = models.CharField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to="sample/seo/", blank=True)

    class Meta:
        abstract = True


class SampleArticle(DraftPublishDuplicateRowMixin):
    title = models.CharField(max_length=300, verbose_name=_("Title"))
    slug = models.SlugField(max_length=300)
    excerpt = models.TextField(blank=True, help_text="Short teaser on listing pages.")
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    @classmethod
    def draft_copy_field_names(cls) -> tuple[str, ...]:
        return ("title", "slug", "excerpt", "content", "published_at")

    class Meta:
        verbose_name = "Sample article"
        verbose_name_plural = "Sample articles"
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=Q(live_version__isnull=True),
                name="sample_samplearticle_unique_live_slug",
            ),
        ]


class SampleSitePage(SampleSEOMixin, SingletonModel):
    hero_title = models.CharField(max_length=200, blank=True, default="About us")
    intro_body = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sample site page"
        verbose_name_plural = "Sample site page"

    def __str__(self) -> str:
        return "Sample site page"


class SampleInlineFact(models.Model):
    page = models.ForeignKey(SampleSitePage, on_delete=models.CASCADE, related_name="facts")
    order = models.PositiveIntegerField(default=0)
    text = models.CharField(max_length=400)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Sample inline fact"
        verbose_name_plural = "Sample inline facts"

    def __str__(self) -> str:
        return self.text[:60]


class SampleHomePage(SampleSEOMixin, SingletonModel):
    hero_title = models.CharField(max_length=200, blank=True, default="Home")
    slug = models.SlugField(max_length=100, default="home")

    class Meta:
        verbose_name = "Sample home page"
        verbose_name_plural = "Sample home page"

    def __str__(self) -> str:
        return "Sample home page"


class SampleInquiry(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Sample inquiry"
        verbose_name_plural = "Sample inquiries"

    def __str__(self) -> str:
        return self.name
