from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from backstage.accent_palettes import (
    ACCENT_PALETTE_CHOICES,
    DEFAULT_ACCENT_PALETTE,
    get_accent_palette,
)
from backstage.models import BackstageSettings
from backstage.registry.base import SingletonAdmin
from backstage.services import clear_backstage_settings_cache
from backstage.theme_presets import THEME_PRESETS
from backstage.widgets import AccentPaletteRadioWidget


class BackstageSettingsForm(forms.ModelForm):
    accent_palette = forms.ChoiceField(
        choices=ACCENT_PALETTE_CHOICES,
        widget=AccentPaletteRadioWidget,
        required=True,
        help_text="Choose a Tailwind-style accent palette for buttons, links, and active states.",
    )

    class Meta:
        model = BackstageSettings
        fields = (
            "site_title",
            "site_header",
            "site_subheader",
            "logo_light",
            "logo_dark",
            "accent_palette",
            "theme_preset",
            "font_family",
            "sidebar_density",
            "custom_css",
            "frontend_url",
        )
        widgets = {
            "custom_css": forms.Textarea(
                attrs={
                    "rows": 8,
                    "class": "font-mono text-sm w-full",
                    "placeholder": "/* Optional custom admin CSS */",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial.setdefault("accent_palette", DEFAULT_ACCENT_PALETTE)
        self.fields["theme_preset"].help_text = (
            "Applies border radius and sidebar density when changed. Accent palette is preserved."
        )
        self.fields[
            "font_family"
        ].help_text = "Admin panel font stack. Inter is bundled; other options use system fonts."
        self.fields["custom_css"].help_text = "Advanced overrides appended to the dynamic theme stylesheet. Admin-only."

    def clean(self):
        cleaned_data = super().clean()
        preset = cleaned_data.get("theme_preset")
        if preset and preset in THEME_PRESETS:
            if self.instance.pk is None or self.instance.theme_preset != preset:
                preset_values = THEME_PRESETS[preset]
                cleaned_data["sidebar_density"] = preset_values["sidebar_density"]
        return cleaned_data


@admin.register(BackstageSettings)
class BackstageSettingsAdmin(SingletonAdmin):
    form = BackstageSettingsForm

    readonly_fields = ("admin_scope_notice", "appearance_preview")

    fieldsets = (
        (
            "Branding",
            {
                "classes": ["tab"],
                "fields": (
                    "admin_scope_notice",
                    "site_title",
                    "site_header",
                    "site_subheader",
                    "logo_light",
                    "logo_dark",
                ),
            },
        ),
        (
            "Appearance",
            {
                "classes": ["tab"],
                "fields": (
                    "appearance_preview",
                    "accent_palette",
                    "theme_preset",
                ),
            },
        ),
        (
            "Layout",
            {
                "classes": ["tab"],
                "fields": ("font_family", "sidebar_density"),
            },
        ),
        (
            "Advanced",
            {
                "classes": ["tab"],
                "fields": ("custom_css",),
            },
        ),
        (
            "Preview",
            {
                "classes": ["tab"],
                "fields": ("frontend_url",),
            },
        ),
    )

    @admin.display(description="")
    def admin_scope_notice(self, obj: BackstageSettings) -> str:
        frontend_url = obj.frontend_url or "http://localhost:5173"
        return mark_safe(
            format_html(
                """
                <div class="rounded-lg border border-border bg-muted px-4 py-3 text-sm text-foreground">
                    <p class="font-medium">Admin panel only</p>
                    <p class="mt-1 text-muted-foreground">
                        These settings style the <strong>Backstage admin panel</strong>
                        (<code>/admin/</code>) only. The public website uses separate
                        brand colors configured in the frontend codebase.
                    </p>
                    <p class="mt-2">
                        <a href="{frontend_url}" target="_blank" rel="noopener noreferrer"
                           class="text-primary-600 hover:underline">
                            View public site &rarr;
                        </a>
                    </p>
                </div>
                """,
                frontend_url=frontend_url,
            )
        )

    @admin.display(description="Live preview")
    def appearance_preview(self, obj: BackstageSettings) -> str:
        palette = get_accent_palette(obj.accent_palette)
        accent = palette["preview_hex"]
        dark_rgb = palette["dark_primary_600"]
        r, g, b = (int(part) for part in dark_rgb.split())
        accent_dark = f"rgb({r}, {g}, {b})"
        preset_values = THEME_PRESETS.get(obj.theme_preset, THEME_PRESETS["default"])
        return mark_safe(
            format_html(
                """
                <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:12px 0;">
                    <span style="display:inline-flex;align-items:center;justify-content:center;
                        padding:8px 16px;border-radius:{radius};background:{accent};
                        color:#fff;font-weight:600;">Primary button</span>
                    <span style="display:inline-flex;align-items:center;justify-content:center;
                        padding:8px 16px;border-radius:{radius};background:{accent_dark};
                        color:#fff;font-weight:600;">Hover state</span>
                    <span style="display:inline-flex;align-items:center;justify-content:center;
                        padding:6px 12px;border-radius:{radius};border:1px solid {accent};
                        color:{accent};font-weight:500;">Accent chip</span>
                </div>
                """,
                radius=preset_values["border_radius"],
                accent=accent,
                accent_dark=accent_dark,
            )
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_backstage_settings_cache()
