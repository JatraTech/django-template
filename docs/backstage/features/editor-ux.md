# Editor UX

## Host configuration

Everything lives in **`yourapp/backstage_host.py`**: `FIELD_EDITOR_META`, `TAB_DESCRIPTIONS`, `NAV_GROUPS`, `MODEL_ICONS`, `ADMIN_OVERRIDES`, and **`resolve_preview_route`**.

Copy [examples/backstage_host.example.py](examples/backstage_host.example.py) to start.

## Copy policy (model-first)

1. **Models** — default for `verbose_name` and `help_text` (SEO mixin, field limits).
2. **`FIELD_EDITOR_META`** — jargon fields, inlines, rich-text hints on website CMS fields. **Catalog / core models:** put copy on the model; keep meta empty for those keys.
3. **`TAB_DESCRIPTIONS`** — tab intros only.

Use small helpers in `backstage_host.py` for repeated patterns (e.g. `_order()`, `_rich_body(label)`).

Do not duplicate identical label/help on model and meta. Meta wins in admin when both are set. Run `python manage.py check_backstage_integration` — it warns when meta repeats model `verbose_name` / `help_text`.

## TinyMCE

Auto-admin applies `RichTextAdminMixin` / `RichTextInlineMixin` from [`backstage/mixins/rich_text.py`](../mixins/rich_text.py) when field names match `RICH_TEXT_FIELD_NAMES` / suffixes. The mixin loads host static **`admin/tinymce_upload.js`** (wire upload in your project).

Configure `TINYMCE_DEFAULT_CONFIG` in project `settings.py` (slim toolbar). Requires upload URL and `django-tinymce`.

## Singleton safety

`SingletonAdmin` hides Delete on singleton CMS pages.

## QA checklist

1. Singleton — hero labels, tab intros, no Delete
2. Blog-style model — Publishing tab, TinyMCE
3. SEOMixin pages — SEO labels from model
4. Preview when frontend runs

See [integration.md](integration.md).
